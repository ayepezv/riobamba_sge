# -*- coding: utf-8 -*-
# Mario Chogllo
# mariofchogllo@gmail.com

import logging
import time
from tools import ustr
from gt_tool import XLSWriter
from openerp.osv import fields, osv
import decimal_precision as dp
from datetime import date, timedelta
DP = dp.get_precision('Budget')
import datetime
class reforma(osv.Model):
    _name = 'reforma'
    _columns = dict(
        name = fields.char('Descripcion',size=256),
        code = fields.integer('Numero'),
        state = fields.selection([('Borrador','Borrador'),('Aprobado','Aprobado')],'Estado'),
    )
reforma()

class budgetReajuste(osv.TransientModel):
    _name = 'budget.reajuste'
    _columns = dict(
        certificate_id = fields.many2one('budget.certificate','Certificado'),
        name = fields.many2one('budget.certificate.line','Partida'),
        date = fields.date('Fecha'),
        monto = fields.float('Monto Extra',help="Ingrese aqui el valor adicional"),
    )

    def agrega_reajuste(self, cr, uid, ids, context):
        item_obj = self.pool.get('budget.item.migrated')
        line_obj = self.pool.get('budget.certificate.line')
        for this in self.browse(cr, uid, ids):
            item_obj.create(cr, uid, {
                'certificate_id':this.certificate_id.id,
                'budget_item_id':this.name.budget_id.id,
                'type_budget':'gasto',
                'code':this.name.budget_id.budget_post_id.code,
                'date':this.date,
                'name':this.name.budget_id.budget_post_id.name,
                'budget_post_id':this.name.budget_id.budget_post_id.id,
                'program_code':this.name.budget_id.program_id.sequence,
                'commited_amount':this.monto,
            })
        return {'type': 'ir.actions.act_window_close'}

    def default_get(self, cr, uid, fields, context):
        if context is None:
            context = {}
        res = {}
        record_id = context and context.get('active_id', False) or False
        cert = self.pool.get('budget.certificate').browse(cr, uid, record_id, context=context)
        res.update({
            'certificate_id':cert.id,
        })
        return res

budgetReajuste()

class fondoProyectoLine(osv.TransientModel):
    _name = 'fondo.proyecto.line'
    _columns = dict(
        p_id = fields.many2one('fondo.proyecto','Proyecto'),
        budget_id = fields.many2one('budget.item','Partida'),
        inicial = fields.float('Inicial'),
        comprometido = fields.float('Comprometido'),
        saldo = fields.float('Saldo por comprometer'),
    )
fondoProyectoLine()
class fondoProyecto(osv.TransientModel):
    _name = 'fondo.proyecto'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        project_id = fields.many2one('project.project','Proyecto'),
        disponible = fields.float('Total Disponible'),
        line_ids = fields.one2many('fondo.proyecto.line','p_id','Detalle'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def exporta_excel_fppy(self, cr, uid, ids, context=None):
        obj = self.pool.get('fondo.proyecto')
        obj.loadSaldoProyecto(cr, uid, ids, context)
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['FONDO PROYECTO'])
            aux_project = this.project_id.code + ' - ' + this.project_id.name
            writer.append(['PROYECTO',aux_project])
            writer.append(['PARTIDA','INICIAL','COMPROMETIDO','SALDO'])
            total_ini = total_c = total_s = aux = 0
            for line in this.line_ids:
                total_ini+=line.inicial
                total_c+=line.comprometido
                total_s += line.saldo
                aux += 1
                aux_budget = line.budget_id.code + ' - ' + line.budget_id.name
                writer.append([aux_budget,line.inicial,line.comprometido,line.saldo])
            writer.append(['TOTAL',total_ini,total_c,total_s])
        writer.save("fondoProyecto.xls")
        out = open("fondoProyecto.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'fondoProyecto.xls'})
        return True

    def printSaldoProyecto(self, cr, uid, ids, context):
        obj = self.pool.get('fondo.proyecto')
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        obj.loadSaldoProyecto(cr, uid, ids, context)
        datas = {'ids': [report.id], 'model': 'report.fondo.proyecto'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fondo.proyecto',
            'model': 'fondo.proyecto',
            'datas': datas,
            'nodestroy': True,
        }

    def loadSaldoProyecto(self, cr, uid, ids, context):
        line_obj = self.pool.get('fondo.proyecto.line')
        item_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            ant_ids = line_obj.search(cr, uid, [('p_id','=',this.id)])
            if ant_ids:
                line_obj.unlink(cr, uid, ant_ids)
            item_ids = item_obj.search(cr, uid, [('project_id','=',this.project_id.id)])
            context = {'by_date':True,'date_start': this.project_id.date_start, 'date_end':this.project_id.date ,'poa_id':this.poa_id.id}
            for line in item_obj.browse(cr,uid,item_ids, context=context):
                aux = line.codif_amount-line.commited_amount,
                line_id = line_obj.create(cr, uid, {
                    'p_id':this.id,
                    'budget_id':line.id,
                    'inicial':line.planned_amount,
                    'comprometido':line.commited_amount,
                    'saldo':line.commited_balance,
                })
        return True

fondoProyecto()

class verificarFondo(osv.TransientModel):
    _name = 'verificar.fondo'

    def onchange_verificar_fondo(self, cr, uid, ids, budget_id, context={}):
        item_obj = self.pool.get('budget.item')
        res = {}
        item = item_obj.browse(cr, uid, budget_id,context=context)
        context = {'by_date':True,'date_start': item.date_start, 'date_end': item.date_end,'poa_id':item.poa_id.id}
        item = item_obj.browse(cr, uid, budget_id,context=context)
        total = item.commited_balance
        return {'value':{'inicial':item.planned_amount,'reformas':item.reform_amount,'codificado':item.codif_amount,'comprometido':item.commited_amount,
                         'devengado':item.devengado_amount,'pagado':item.paid_amount,'disponible':item.commited_balance}}
#        return {'value':{'disponible':total}}

    _columns = dict(
        budget_id = fields.many2one('budget.item','Partida Presupuestaria'),
        inicial = fields.float('Inicial'),
        reformas = fields.float('Reforma'),
        codificado = fields.float('Codificado'),
        comprometido = fields.float('Comprometido'),
        devengado = fields.float('Devengado'),
        pagado = fields.float('Pagado'),
        disponible = fields.float('Monto Disponible'),
    )
verificarFondo()

class massReformLine(osv.Model):
    _name = 'mass.reform.line'
    _order = 'code asc'

    def onchange_monto(self, cr, uid, ids, monto):
        if monto<=0:
            result = {'warning': {'title':'Advertencia', 'message': 'El monto debe ser mayor a cero'},
                      }
            return result

    def _amount_final(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        item_obj = self.pool.get('budget.item')
        for line in self.browse(cr, uid, ids, context=context):
            date_from = line.budget_id.date_start
            if line.mass_id:
                date = line.mass_id.date
            else:
                date = line.mass_id2.date
#            hoy = date
            date_aux = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            ayer = date_aux - timedelta(days=1)
            date_stop = ayer
            context = {'by_date':True,'date_start': date_from, 'date_end': date_stop,'poa_id':line.budget_id.poa_id.id}
            budget = item_obj.browse(cr, uid, line.budget_id.id, context=context)
            if line.mass_id:
                res[line.id] = budget.codif_amount - line.monto #
            else:
                res[line.id] = budget.codif_amount + line.monto #
        return res

    def _amount_reforma(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        item_obj = self.pool.get('budget.item')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'reformas': 0.0,
                'codificado': 0.0,
            }
            date_from = line.budget_id.date_start
            if line.mass_id:
                date = line.mass_id.date
            else:
                date = line.mass_id2.date
#            hoy = date
            date_aux = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            ayer = date_aux - timedelta(days=1)
            date_stop = ayer
            context = {'by_date':True,'date_start': date_from, 'date_end': date_stop,'poa_id':line.budget_id.poa_id.id}
            budget = item_obj.browse(cr, uid, line.budget_id.id, context=context)
            res[line.id]['reformas'] = budget.reform_amount
            res[line.id]['codificado']  = budget.codif_amount
        return res

    _columns = dict(
        mass_id = fields.many2one('mass.reform','Reforma'),
        mass_id2 = fields.many2one('mass.reform','Reforma'),
        program_id =  fields.related('project_id', 'program_id', type="many2one",relation="project.program",
                           string="Programa", store=True),
        project_id =  fields.related('task_id', 'project_id', type="many2one",relation="project.project",
                           string="Proyecto", store=True),
        task_id =  fields.related('budget_id', 'task_id', type="many2one",relation="project.task",
                           string="Actividad", store=True),
        inicial = fields.related('budget_id', 'planned_amount', type="float",
                                 string="Asignacion Inicial", store=True,readonly=True),
#        final = fields.float('Final'),
        reformas = fields.function(_amount_reforma, string='Reformas', multi="rf",store=True),
        codificado = fields.function(_amount_reforma, string='Codificado', multi="rf",store=True),
        final = fields.function(_amount_final,type="float", store=True,string='Presupuesto Final',readonly=True),
        budget_id = fields.many2one(
            'budget.item', required=True,
            string='Partida Origen'),
        traspaso_suma = fields.float('Traspaso Aumento'),
        traspaso_resta = fields.float('Traspaso Disminucion'),
        suma = fields.float('Aumento'),
        resta = fields.float('Disminucion'),
        monto = fields.float('Monto Reforma'),
        traspaso = fields.boolean('Traspaso'),
        code_aux = fields.related('budget_id','code_aux',type="char",size=32,store=True),
        code = fields.related('budget_id','code',type="char",size=32,store=True),
    )

    _sql_constraints = [('unique_budget', 'unique(budget_id,mass_id)', u'No se permite mas de una vez la misma partida.'),
                        ('unique_budget_2', 'unique(budget_id,mass_id2)', u'No se permite mas de una vez la misma partida.')
                    ]

massReformLine()

class massReform(osv.Model):
    _name = 'mass.reform'
    _order = 'date desc'
    READONLY_STATES = {'Borrador': [('readonly', False)]}

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids):
            res.append((record['id'], '%s - %s' % (record.fy_id.name, record.name)))
        return res

    def onchange_project_egreso(self, cr, uid, ids, project_id, context={}):
        project_obj = self.pool.get('project.project')
        project = project_obj.browse(cr, uid, project_id)
        task_id = project.tasks[0].id
        vals = {}
        return {'value':{'task_id':task_id}}

    def _amount_planned(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el budget inicial
        '''
        res = {}
        poa_obj = self.pool.get('budget.poa')
        item_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            total = 0
            res[this.id] = {
                'inicial':0.0,
                'tr_resta':0.0,
                'tr_suma':0.0,
                'aum_suma':0.0,
                'dis_suma':0.0,
                'total_presupuesto':0.0,
            }
            aux_inicial = auxtr_resta = auxtr_suma = auxaum_suma = auxdis_suma = 0
            poa_ids = poa_obj.search(cr, uid, [('date_start','=',this.fy_id.date_start),('date_end','=',this.fy_id.date_stop)])
            if not poa_ids:
                raise osv.except_osv('Error de usuario','No hay presupuesto definido para la fecha o periodo contable seleccionado.')
            item_ids = item_obj.search(cr, uid, [('type_budget','=','ingreso'),('poa_id','=',poa_ids[0])])
            final_aux = datetime.datetime.strptime(this.date, '%Y-%m-%d').date()
            final_aux = final_aux - timedelta(days=1)
            date_final_reporte = final_aux.strftime('%Y-%m-%d')
            context = {'by_date':True,'date_start': this.fy_id.date_start, 'date_end': date_final_reporte,'poa_id':poa_ids[0]}
            aux_inicial = final_budget = 0
            if item_ids:
                for item_id in item_ids:
                    item = item_obj.browse(cr, uid, item_id,context)
                    aux_inicial += item.codif_amount#planned_amount
            final_budget = aux_inicial
            for line in this.line_ids:
                if line.traspaso:
                    auxtr_resta += line.monto
                else:
                    auxdis_suma += line.monto
            res[this.id]['tr_resta']=auxtr_resta
            res[this.id]['dis_suma']=auxdis_suma
            total = total -auxtr_resta - auxdis_suma
            for line in this.line_ids2:
                if line.traspaso:
                    auxtr_suma += line.monto
                else:
                    auxaum_suma += line.monto
            res[this.id]['tr_suma']=auxtr_suma
            res[this.id]['aum_suma']=auxaum_suma
            total = total + auxtr_suma + auxaum_suma
            #aux_inicial = aux_inicial - auxtr_resta - auxdis_suma + auxtr_suma + auxaum_suma
            res[this.id]['inicial']=aux_inicial
            res[this.id]['total_presupuesto'] = total#final_budget
        return res

    _columns = dict(
        num_oficio = fields.char('Num. Oficio',size=32),
        fecha_oficio = fields.date('Fecha Oficio'),
        code = fields.integer('Autorizacion'),
        reforma = fields.integer('Reforma'),
        reforma_id = fields.many2one('reforma','Reforma'),
        inicial = fields.function(_amount_planned,multi="reform",string='Presupuesto Inicial',store=True,method=True),
        tr_resta = fields.function(_amount_planned,multi="reform",string='Total Traspasos Disminucion',store=True,method=True),
        tr_suma = fields.function(_amount_planned,multi="reform",string='Total Traspasos Aumento',store=True,method=True),
        aum_suma = fields.function(_amount_planned,multi="reform",string='Total Aumentos',store=True,method=True),
        dis_suma = fields.function(_amount_planned,multi="reform",string='Total Disminuciones',store=True,method=True),
        total_presupuesto = fields.function(_amount_planned,multi="reform",string='Total Presupuesto',store=True,method=True),
#        reform_ids = fields.one2many('budget.reform',''),
        fy_id = fields.many2one('account.fiscalyear','Periodo',required=True),
        name = fields.char('Descripcion',size=256,required=True),
        date = fields.date('Fecha Aplicacion',required=True),
        line_ids = fields.one2many('mass.reform.line','mass_id','Detalle Disminucion'),
        line_ids2 = fields.one2many('mass.reform.line','mass_id2','Detalle Aumento'),
        project_id = fields.many2one(
            'project.project', 'Proyecto Destino',
            domain=[('state', '=', 'exec')]),
        task_id = fields.many2one(
            'project.task', 'Actividad Destino'),
        budget2_id = fields.many2one(
            'budget.item',
            string='Partida Destino'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
        state = fields.selection([('Borrador','Borrador'),('Aplicada','Aplicada')],'Estado'),
    )

    def exporta_excel_reform(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            cabecera_origen = ['ORIGEN']
            cabecera_all = ['Codigo Partida','Nombre Partida','Inicial','Tipo','Monto','Final']
            writer.append(cabecera_origen)
            writer.append(cabecera_all)
            aux_ini = aux_tipo = aux_monto = 0
            for line_or in this.line_ids:
                aux_ini += line_or.inicial
                aux_tipo += line_or.monto
                aux_monto += line_or.final
                cabecera_cuenta = [line_or.budget_id.code,line_or.budget_id.name,line_or.inicial,line_or.monto,line_or.final]
                writer.append(cabecera_cuenta)
            writer.append(['TOTAL','',aux_ini,aux_tipo,aux_monto])
            cabecera_destino = ['DESTINO']
            writer.append(cabecera_destino)
            writer.append(cabecera_all)
            aux_ini = aux_tipo = aux_monto = 0
            for line_de in this.line_ids2:
                aux_ini += line_de.inicial
                aux_tipo += line_de.monto
                aux_monto += line_de.final
                cabecera_cuenta = [line_de.budget_id.code,line_de.budget_id.name,line_de.inicial,line_de.monto,line_de.final]
                writer.append(cabecera_cuenta)
            writer.append(['TOTAL','',aux_ini,aux_tipo,aux_monto])
        writer.save("reforma.xls")
        out = open("reforma.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'reforma.xls'})
        return True

    def return_reform(self, cr, uid, ids,context=None):
        reform_obj = self.pool.get('budget.reform')
        for this in self.browse(cr, uid, ids):
            reform_ids = reform_obj.search(cr, uid, [('date_done','=',this.date),('justification','=',this.name)])
            if reform_ids:
                reform_obj.write(cr, uid, reform_ids,{
                    'state':'draft',
                })
                reform_obj.unlink(cr, uid, reform_ids)
        self.write(cr, uid, ids[0],{
            'state':'Borrador',
        })
        return True

    def apply_reform(self, cr, uid, ids,context=None):
        reform_obj = self.pool.get('budget.reform')
        mass_reform = self.pool.get('mass.reform')
        mass_reform_i = self.pool.get('mass.reform.ingreso')
        for this in self.browse(cr, uid, ids):
            mass_ids = mass_reform.search(cr, uid, [('name','=',this.name),('id','!=',this.id)])
            massi_ids = mass_reform_i.search(cr, uid, [('name','=',this.name),('id','!=',this.id)])
            if mass_ids or massi_ids:
                raise osv.except_osv('Error de usuario', 'La descipcion de la reforma no puede ser igual a otra.')
            if not (this.date>=this.fy_id.date_start and this.date<=this.fy_id.date_stop):
                raise osv.except_osv('Error de usuario', 'Verifique la fecha corresponda al periodo.')
            monto_total = monto2 = 0
            #validar montos iguales
            for line in this.line_ids:
                #disminuciones
                monto_total += line.monto
            for line in this.line_ids2:
                #disminuciones
                monto2 += line.monto
#            if monto_total != monto2:
 #               raise osv.except_osv('Error de usuario', 'El valor total de aumento con el de disminucion debe ser igual.')
            for line in this.line_ids:
                #disminuciones
                if line.traspaso:
                    tipo_aux = "transferencia"
                else:
                    tipo_aux = "disminucion"
                reform_obj.create(cr, uid, {
                    'project_id':line.budget_id.project_id.id,
                    'task_id':line.budget_id.task_id.id,
                    'budget_id':line.budget_id.id,
                    'type_transaction':tipo_aux,
                    'amount':line.monto,
                    'state':'done',
                    'justification':this.name,
                    'date_done':this.date,
                })
            #aumento
            for line in this.line_ids2:
                #disminuciones
                tipo_aux = "ampliacion"
                reform_obj.create(cr, uid, {
                    'project_id':line.budget_id.project_id.id,
                    'task_id':line.budget_id.task_id.id,
                    'budget_id':line.budget_id.id,
                    'type_transaction':tipo_aux,
                    'amount':line.monto,
                    'state':'done',
                    'justification':this.name,
                    'date_done':this.date,
                })
        self.write(cr, uid, ids[0],{
            'state':'Aplicada',
        })
        return True

    def _checkNoDuplica(self, cr, uid, ids):
        return True
    #     partidas_origen = []
    #     partidas_destino = []
    #     for obj in self.browse(cr, uid, ids):
    #         for line in obj.line_ids:
    #             if not line.budget_id.id in partidas_origen:
    #                 partidas_origen.append(line.budget_id.id)
    #             else:
    #                 mensaje = ustr('La partida %s esta duplicada en origen.' %(line.budget_id.code + ' - ' + line.budget_id.name))
    #                 raise osv.except_osv('Error', mensaje)
    #         for line in obj.line_ids2:
    #             if not line.budget_id.id in partidas_destino:
    #                 partidas_destino.append(line.budget_id.id)
    #             else:
    #                 mensaje = ustr('La partida %s esta duplicada en destino.' %(line.budget_id.code + ' - ' + line.budget_id.name))
    #                 raise osv.except_osv('Error', mensaje)
    #     return True

    # _constraints = [
    #     (_checkNoDuplica,
    #      ustr('No puede duplicar partidas en la reforma, por favor revise.'),[ustr('Partidas'), 'Partida']),
    # ]


    _defaults = dict(
        state = 'Borrador',
        date = time.strftime("%Y-%m-%d"),
    )

massReform()
class massReformLineIngreso(osv.Model):
    _name = 'mass.reform.line.ingreso'
    _order = 'code asc'

    def onchange_monto_ingreso(self, cr, uid, ids, monto):
        if monto<=0:
            result = {'warning': {'title':'Advertencia', 'message': 'El monto debe ser mayor a cero'},
                      }
            return result

    def _amount_final(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.mass_id:
                res[line.id] = line.budget_id.planned_amount - line.monto
            else:
                res[line.id] = line.budget_id.planned_amount + line.monto
        return res

    def _amount_reforma(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        item_obj = self.pool.get('budget.item')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'reformas': 0.0,
                'codificado': 0.0,
            }
            date_from = line.budget_id.date_start
            if line.mass_id:
                date = line.mass_id.date
            else:
                date = line.mass_id2.date
#            hoy = date
            date_aux = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            ayer = date_aux - timedelta(days=1)
            date_stop = ayer
            context = {'by_date':True,'date_start': date_from, 'date_end': date_stop,'poa_id':line.budget_id.poa_id.id}
            budget = item_obj.browse(cr, uid, line.budget_id.id, context=context)
            res[line.id]['reformas'] = budget.reform_amount
            res[line.id]['codificado']  = budget.codif_amount
        return res

    _columns = dict(
        mass_id = fields.many2one('mass.reform.ingreso','Reforma'),
        mass_id2 = fields.many2one('mass.reform.ingreso','Reforma'),
        project_id =  fields.related('task_id', 'project_id', type="many2one",relation="project.project",
                           string="Proyecto", store=True),
        task_id =  fields.related('budget_id', 'task_id', type="many2one",relation="project.task",
                           string="Actividad", store=True),
        inicial = fields.related('budget_id', 'planned_amount', type="float",
                                 string="Asignacion Inicial", store=True,readonly=True),
        reformas = fields.function(_amount_reforma, string='Reformas', multi="rf",store=True),
        codificado = fields.function(_amount_reforma, string='Codificado', multi="rf",store=True),
        final = fields.function(_amount_final,type="float", store=True,string='Presupuesto Final',readonly=True),
#        final = fields.function(_amount_final, multi="bf",type="float", store=True,string='Presupuesto Final',readonly=True),
#        final = fields.float('Final'),
        budget_id = fields.many2one(
            'budget.item', required=True,
            string='Partida Origen'),
        traspaso_suma = fields.float('Traspaso Aumento'),
        traspaso_resta = fields.float('Traspaso Disminucion'),
        suma = fields.float('Aumento'),
        resta = fields.float('Disminucion'),
        monto = fields.float('Monto Reforma'),
        traspaso = fields.boolean('traspaso'),
        code_aux = fields.related('budget_id','code_aux',type="char",size=32,store=True),
        code = fields.related('budget_id','code',type="char",size=32,store=True),
    )

    _sql_constraints = [('unique_budget', 'unique(budget_id,mass_id)', u'No se permite mas de una vez la misma partida.'),
                        ('unique_budget_2', 'unique(budget_id,mass_id2)', u'No se permite mas de una vez la misma partida.')
    ]

massReformLineIngreso()
class massReformIngreso(osv.Model):
    _name = 'mass.reform.ingreso'
    _order = 'date desc'
    READONLY_STATES = {'Borrador': [('readonly', False)]}

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids):
            res.append((record['id'], '%s - %s' % (record.fy_id.name, record.name)))
        return res

    def onchange_project_ingreso(self, cr, uid, ids, project_id, context={}):
        project_obj = self.pool.get('project.project')
        project = project_obj.browse(cr, uid, project_id)
        task_id = project.tasks[0].id
        vals = {}
        return {'value':{'task_id':task_id}}

    def _amount_planned(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el budget inicial
        '''
        res = {}
        poa_obj = self.pool.get('budget.poa')
        item_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            total = 0
            res[this.id] = {
                'inicial':0.0,
                'tr_resta':0.0,
                'tr_suma':0.0,
                'aum_suma':0.0,
                'dis_suma':0.0,
                'total_presupuesto':0.0,
            }
            aux_inicial = auxtr_resta = auxtr_suma = auxaum_suma = auxdis_suma = 0
            poa_ids = poa_obj.search(cr, uid, [('date_start','=',this.fy_id.date_start),('date_end','=',this.fy_id.date_stop)])
            if not poa_ids:
                raise osv.except_osv('Error de usuario','No hay presupuesto definido para la fecha o periodo contable seleccionado.')
            item_ids = item_obj.search(cr, uid, [('type_budget','=','ingreso'),('poa_id','=',poa_ids[0])])
            final_aux = datetime.datetime.strptime(this.date, '%Y-%m-%d').date()
            final_aux = final_aux - timedelta(days=1)
            date_final_reporte = final_aux.strftime('%Y-%m-%d')
            context = {'by_date':True,'date_start': this.fy_id.date_start, 'date_end': date_final_reporte,'poa_id':poa_ids[0]}
            aux_inicial = final_budget = 0
            if item_ids:
                for item_id in item_ids:
                    item = item_obj.browse(cr, uid, item_id,context)
                    aux_inicial += item.codif_amount#planned_amount
            final_budget = aux_inicial
            total = aux_inicial
            for line in this.line_ids:
                if line.traspaso:
                    auxtr_resta += line.monto
                else:
                    auxdis_suma += line.monto
            res[this.id]['tr_resta']=auxtr_resta
            res[this.id]['dis_suma']=auxdis_suma
            total = total -auxtr_resta - auxdis_suma
            for line in this.line_ids2:
                if line.traspaso:
                    auxtr_suma += line.monto
                else:
                    auxaum_suma += line.monto
            res[this.id]['tr_suma']=auxtr_suma
            res[this.id]['aum_suma']=auxaum_suma
            total = total + auxtr_suma + auxaum_suma
            #aux_inicial = aux_inicial - auxtr_resta - auxdis_suma + auxtr_suma + auxaum_suma
            res[this.id]['inicial']=aux_inicial
            res[this.id]['total_presupuesto'] = total#final_budget
        return res

    def _amount_planned2(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el budget inicial
        '''
        res = {}
        poa_obj = self.pool.get('budget.poa')
        for this in self.browse(cr, uid, ids):
            total = 0
            res[this.id] = {
                'inicial':0.0,
                'tr_resta':0.0,
                'tr_suma':0.0,
                'aum_suma':0.0,
                'dis_suma':0.0,
                'total_presupuesto':0.0,
            }
            aux_inicial = auxtr_resta = auxtr_suma = auxaum_suma = auxdis_suma = 0
            poa_ids = poa_obj.search(cr, uid, [('date_start','=',this.fy_id.date_start),('date_end','=',this.fy_id.date_stop)])
            if not poa_ids:
                raise osv.except_osv('Error de usuario','No hay presupuesto definido para la fecha o periodo contable seleccionado.')
            aux_tipo = "'"+'ingreso'+"'"
            sql = """select sum(planned_amount) from budget_item where poa_id=%s and type_budget=%s""" %(str(poa_ids[0]),aux_tipo)
            cr.execute(sql)
            result = cr.fetchall()
            for monto in result:
                res[this.id]['inicial']=monto[0]
                total += monto[0]
            for line in this.line_ids:
                if line.traspaso:
                    auxtr_resta += line.monto
                else:
                    auxdis_suma += line.monto
            res[this.id]['tr_resta']=auxtr_resta
            res[this.id]['dis_suma']=auxdis_suma
            total = total -auxtr_resta - auxdis_suma
            for line in this.line_ids2:
                if line.traspaso:
                    auxtr_suma += line.monto
                else:
                    auxaum_suma += line.monto
            res[this.id]['tr_suma']=auxtr_suma
            res[this.id]['aum_suma']=auxaum_suma
            total = total + auxtr_suma + auxaum_suma
            res[this.id]['total_presupuesto'] = total
        return res

    _columns = dict(
        num_oficio = fields.char('Num. Oficio',size=32),
        fecha_oficio = fields.date('Fecha Oficio'),
        code = fields.integer('Autorizacion'),
        reforma_id = fields.many2one('reforma','Reforma'),
        reforma = fields.integer('Reforma'),
        inicial = fields.function(_amount_planned,multi="reform",string='Presupuesto Inicial',store=True,method=True),
        tr_resta = fields.function(_amount_planned,multi="reform",string='Total Traspasos Disminucion',store=True,method=True),
        tr_suma = fields.function(_amount_planned,multi="reform",string='Total Traspasos Aumento',store=True,method=True),
        aum_suma = fields.function(_amount_planned,multi="reform",string='Total Aumentos',store=True,method=True),
        dis_suma = fields.function(_amount_planned,multi="reform",string='Total Disminuciones',store=True,method=True),
        total_presupuesto = fields.function(_amount_planned,multi="reform",string='Total Presupuesto',store=True,method=True),
        fy_id = fields.many2one('account.fiscalyear','Periodo',required=True),
        name = fields.char('Descripcion',size=256,required=True),
        date = fields.date('Fecha Aplicacion',required=True),
        line_ids = fields.one2many('mass.reform.line.ingreso','mass_id','Detalle Disminucion'),
        line_ids2 = fields.one2many('mass.reform.line.ingreso','mass_id2','Detalle Aumento'),
        project_id = fields.many2one(
            'project.project', 'Proyecto Destino',
            domain=[('state', '=', 'exec')]),
        task_id = fields.many2one(
            'project.task', 'Actividad Destino'),
        budget2_id = fields.many2one(
            'budget.item',
            string='Partida Destino'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
        state = fields.selection([('Borrador','Borrador'),('Aplicada','Aplicada')],'Estado'),
    )

    def exporta_excel_reform_ingreso(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            cabecera_origen = ['ORIGEN']
            cabecera_all = ['Codigo Partida','Nombre Partida','Inicial','Tipo','Monto','Final']
            writer.append(cabecera_origen)
            writer.append(cabecera_all)
            aux_ini = aux_tipo = aux_monto = 0
            for line_or in this.line_ids:
                aux_ini += line_or.inicial
                aux_tipo += line_or.monto
                aux_monto += line_or.final
                cabecera_cuenta = [line_or.budget_id.code,line_or.budget_id.name,line_or.inicial,line_or.monto,line_or.final]
                writer.append(cabecera_cuenta)
            writer.append(['TOTAL','',aux_ini,aux_tipo,aux_monto])
            cabecera_destino = ['DESTINO']
            writer.append(cabecera_destino)
            writer.append(cabecera_all)
            aux_ini = aux_tipo = aux_monto = 0
            for line_de in this.line_ids2:
                aux_ini += line_de.inicial
                aux_tipo += line_de.monto
                aux_monto += line_de.final
                cabecera_cuenta = [line_de.budget_id.code,line_de.budget_id.name,line_de.inicial,line_de.monto,line_de.final]
                writer.append(cabecera_cuenta)
            writer.append(['TOTAL','',aux_ini,aux_tipo,aux_monto])
        writer.save("reforma.xls")
        out = open("reforma.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'reforma.xls'})
        return True

    def return_reform_ingreso(self, cr, uid, ids,context=None):
        reform_obj = self.pool.get('budget.reform')
        for this in self.browse(cr, uid, ids):
            reform_ids = reform_obj.search(cr, uid, [('date_done','=',this.date),('justification','=',this.name)])
            if reform_ids:
                reform_obj.write(cr, uid, reform_ids,{
                    'state':'draft',
                })
                reform_obj.unlink(cr, uid, reform_ids)
        self.write(cr, uid, ids[0],{
            'state':'Borrador',
        })
        return True

    def apply_reform_ingreso(self, cr, uid, ids,context=None):
        reform_obj = self.pool.get('budget.reform')
        mass_reform = self.pool.get('mass.reform')
        mass_reform_i = self.pool.get('mass.reform.ingreso')
        for this in self.browse(cr, uid, ids):
            mass_ids = mass_reform.search(cr, uid, [('name','=',this.name),('id','!=',this.id)])
            massi_ids = mass_reform_i.search(cr, uid, [('name','=',this.name),('id','!=',this.id)])
            if mass_ids or massi_ids:
                raise osv.except_osv('Error de usuario', 'La descipcion de la reforma no puede ser igual a otra.')
            if not (this.date>=this.fy_id.date_start and this.date<=this.fy_id.date_stop):
                raise osv.except_osv('Error de usuario', 'Verifique la fecha corresponda al periodo.')
            for line in this.line_ids:
                #disminuciones
                if line.traspaso:
                    tipo_aux = "transferencia"
                else:
                    tipo_aux = "disminucion"
                reform_obj.create(cr, uid, {
                    'project_id':line.budget_id.project_id.id,
                    'task_id':line.budget_id.task_id.id,
                    'budget_id':line.budget_id.id,
                    'type_transaction': tipo_aux,
                    'amount':line.monto,
                    'state':'done',
                    'justification':this.name,
                    'date_done':this.date,
                })
            #aumento
            for line in this.line_ids2:
                #disminuciones
                if line.traspaso:
                    tipo_aux = "transferencia"
                else:
                    tipo_aux = "ampliacion"
                reform_obj.create(cr, uid, {
                    'project_id':line.budget_id.project_id.id,
                    'task_id':line.budget_id.task_id.id,
                    'budget_id':line.budget_id.id,
                    'type_transaction':tipo_aux,
                    'amount':line.monto,
                    'state':'done',
                    'justification':this.name,
                    'date_done':this.date,
                })
        self.write(cr, uid, ids[0],{
            'state':'Aplicada',
        })
        return True

    def _checkNoDuplica(self, cr, uid, ids):
       return True
    #     partidas_origen = []
    #     partidas_destino = []
    #     for obj in self.browse(cr, uid, ids):
    #         for line in obj.line_ids:
    #             if not line.budget_id.id in partidas_origen:
    #                 partidas_origen.append(line.budget_id.id)
    #             else:
    #                 mensaje = ustr('La partida %s esta duplicada en origen.' %(line.budget_id.code + ' - ' + line.budget_id.name))
    #                 raise osv.except_osv('Error', mensaje)
    #         for line in obj.line_ids2:
    #             if not line.budget_id.id in partidas_destino:
    #                 partidas_destino.append(line.budget_id.id)
    #             else:
    #                 mensaje = ustr('La partida %s esta duplicada en destino.' %(line.budget_id.code + ' - ' + line.budget_id.name))
    #                 raise osv.except_osv('Error', mensaje)
    #     return True

    # _constraints = [
    #     (_checkNoDuplica,
    #      ustr('No puede duplicar partidas en la reforma, por favor revise.'),[ustr('Partidas'), 'Partida']),
    # ]

    # _defaults = dict(
    #     state = 'Borrador',
    # )
    _defaults = dict(
        state = 'Borrador',
        date = time.strftime("%Y-%m-%d"),
        )

massReformIngreso()

class BudgetReformContainer(osv.Model):
    _name = "budget.reform.container"

    _columns = {
        'date': fields.date('Fecha', required=True),
        'name': fields.char('Código', size=128, required=True),
        'line_ids': fields.many2many('budget.reform','container_reform_rel','container_id','reform_id','Detalle de reforma'),
    }
BudgetReformContainer()

class BudgetReform(osv.Model):

    _name = 'budget.reform'
    _description = 'Reformas Presupuestarias'
    _order = "date_done desc"

    READONLY_STATES = {'draft': [('readonly', False)]}
    DP = dp.get_precision('Presupuestos')

    def action_number(self, cr, uid, ids, context=None):
        """
        Metodo que implementa la numeracion del documento
        en base al codigo de secuencia asignada.
        """
        seq_obj = self.pool.get('ir.sequence')
        for obj in self.browse(cr, uid, ids, context):
            number = seq_obj.get('budget.reform')
            self.write(cr, uid, {'name': number})
        return True

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for record in self.read(cr, uid, ids, ['state']):
            if record['state'] != 'draft':
                raise osv.except_osv('Error', 'No se permite eliminar un documento en proceso.')
        return super(BudgetReform, self).unlink(cr, uid, ids, context)

    _columns = {
#        'ri':fields.many2one('','')
        'program_id': fields.related('project_id', 'program_id', type="many2one",relation="project.program",
                           string="Programa", store=True),
        'name': fields.char('Código', size=128, required=True, readonly=True),
        'project_id': fields.many2one(
            'project.project', string='Proyecto',
            required=True, domain=[('state', '=', 'exec')],
            readonly=True, states=READONLY_STATES),
        'task_id': fields.many2one(
            'project.task', 'Actividad',
            required=True, readonly=True,
            states=READONLY_STATES),
        'type_budget': fields.related('budget_id', 'type_budget', type="char",size=10,
                           string="Tipo", store=True),
        'budget_id': fields.many2one(
            'budget.item', required=True,
            string='Partida Origen', readonly=True,
            states=READONLY_STATES),
        'type_transaction': fields.selection([
            ('ampliacion', 'AMPLIACION'),
            ('disminucion', 'DISMINUCION'),
            ('transferencia', 'TRANSFERENCIA')],
            string='Tipo de Reforma', required=True,
            readonly=True, states=READONLY_STATES),
        'amount': fields.float(
            'Valor de Reforma', required=True,
            help='Valor de reforma a la partida presupuestaria, considerar el tipo de reforma.',
            readonly=False,
            states={'done': [('readonly', True)]}, digits_compute=DP),
        'state': fields.selection([
            ('draft', 'Borrador'),
            ('request', 'Solicitud Coordinador'),
            ('review', 'Revisión Presupuestaria'),
            ('done', 'Reforma Aplicada'),
            ('cancel', 'Anulado')],
            string='Estado',
            required=True),
        'justification': fields.text(
            'Justificación Legal', required=True,
            readonly=False,
            states={'done': [('readonly', True)]}),
        # Campos sin uso
        'request_date': fields.date('Fecha de Solicitud', required=True,
                                    readonly=True),
        'date_done': fields.date('Fecha de Aplicación'),
        'project2_id': fields.many2one(
            'project.project', 'Proyecto Destino',
            domain=[('state', '=', 'exec')],
            readonly=True, states=READONLY_STATES),
        'task2_id': fields.many2one(
            'project.task', 'Actividad Destino',
            readonly=True, states=READONLY_STATES),
        'budget2_id': fields.many2one(
            'budget.item',
            string='Partida Destino',
            readonly=True, states=READONLY_STATES),
        'amount_b1': fields.float(string='Disponible (Partida origen)',
                                  digits_compute=DP, readonly=True),
        'amount_b2': fields.float(string='Disponible (Partida destino)',
                                  digits_compute=DP, readonly=True),
        }

    _defaults = dict(
        state='draft',
        request_date=lambda *a: time.strftime('%Y-%m-%d'),
        type_transaction='ampliacion',
        name='/'
        )

    def onchange_amount(self, cr, uid, ids, amount,
                        budget_amount, type_transaction):
        '''
        Verificación de monto disponible en partida presupuestaria
        '''
        res = {}
        if type_transaction in ['ampliacion', 'disminucion']:
            return res
        if amount and budget_amount:
            if amount > budget_amount:
                res = {
                    'warning': {
                        'title': 'Error de Usuario',
                        'message': 'No puede superar el monto disponible'
                        },
                    'value': {
                        'amount': 0
                        }
                    }
        return res

    def onchange_budget(self, cr, uid, ids, budget_id, budget2_id,date_done):
        budget = self.pool.get('budget.item')
        res = {'value': {'amount_b1': 0, 'amount_b2': 0}}
        if date_done:
            context = {'by_date':True,'date_start': '2015-01-01', 'date_end': date_done}
        else:
            context = {}
        if budget_id:
            res['value']['amount_b1'] = budget.browse(cr, uid, budget_id, context=context).avai_amount
        if budget2_id:
            res['value']['amount_b2'] = budget.browse(cr, uid, budget2_id, context=context).avai_amount
        return res

    # Workflow stuff

    def test_availability(self, cr, uid, ids):
        """
        Revisa la disponibilidad de la partida
        si el tipo de transaccion es 'transferencia'
        """
        for obj in self.browse(cr, uid, ids):
            if obj.type_transaction == 'transferencia':
                if obj.amount > obj.budget_id.available_amount:
                    raise osv.except_osv(
                        'Error', 'No dispone del valor solicitado.')
        return True

    def action_request(self, cr, uid, ids, context=None):
        """
        Metodo que implementa la accion de solicitud de reforma
        """
        parameter_obj = self.pool.get('ir.config_parameter')
        validbudget_ids = parameter_obj.search(cr, uid, [('key','=','validbudget')],limit=1)
        valid_budget = 'No'
        if validbudget_ids:
            valid_budget = parameter_obj.browse(cr, uid, validbudget_ids[0]).value
        for obj in self.browse(cr, uid, ids, context):
            amount_b1 = obj.budget_id and obj.budget_id.avai_amount or 0
            amount_b2 = obj.budget2_id and obj.budget2_id.avai_amount or 0
 #                  'amount_b1': amount_b1,
  #                  'amount_b2': amount_b2}
            data = {'state': 'request'}
            for line in obj.line_ids:
                commited = 0
                budget_item = budget_item_obj.browse(cr, uid, line.budget_id.id)
                if valid_budget=='Si' and obj.date>='2017-01-01':
                    if not (budget_item.commited_balance >= line.amount_commited):
                        mensaje = ustr('Desea comprometer %s y tiene disponible %s en la partida %s, por favor ejecute una reforma antes de realizar el compromiso.' %(line.amount_commited,budget_item.commited_balance,budget_item.code + ' - ' +budget_item.name))
                        raise osv.except_osv('Error', mensaje)
            self.write(cr, uid, [obj.id], data)
        return True

    def action_review(self, cr, uid, ids, context=None):
        """
        Metodo que implementa la accion de revision presupuestaria
        """
        self.write(cr, uid, ids, {'state': 'review'})
        return True

    def action_done(self, cr, uid, ids, context=None):
        """
        Metodo que aplica la reforma, este registro se considera
        en el campo de reforma_amount del objeto budget.item
        """
        item_obj = self.pool.get('budget.item')
        for reforma in self.browse(cr, uid, ids):
            monto_anterior = monto = monto_final = 0
            if reforma.type_transaction == 'ampliacion':
                item = item_obj.browse(cr, uid, reforma.budget_id.id)
                monto_anterior = item.reform_amount
                monto = reforma.amount
                monto_final = monto_anterior + monto
#                item_obj.write(cr, uid, reforma.budget_id.id,{
#                        'reform_amount' :monto_final,
#                        })
            elif reforma.type_transaction == 'disminucion':
                item = item_obj.browse(cr, uid, reforma.budget_id.id)
                monto_anterior = item.reform_amount
                monto = reforma.amount
                monto_final = monto_anterior - monto
#                item_obj.write(cr, uid, reforma.budget_id.id,{
#                        'reform_amount' :monto_final,
#                        })
            else:
                item = item_obj.browse(cr, uid, reforma.budget_id.id)
                monto_anterior = item.reform_amount
                monto = reforma.amount
                monto_final = monto_anterior - monto
 #               item_obj.write(cr, uid, reforma.budget_id.id,{
 #                       'reform_amount' :monto_final,
 #                       })
                item_2 = item_obj.browse(cr, uid, reforma.budget2_id.id)
                monto_anterior = item_2.reform_amount
                monto = reforma.amount
                monto_final = monto_anterior + monto
#                item_obj.write(cr, uid, reforma.budget2_id.id,{
#                        'reform_amount' :monto_final,
#                        })

        if not reforma.date_done:
            data = {'date_done': time.strftime('%Y-%m-%d'), 'state': 'done'}
        else:
            data = {'state': 'done'}
        self.write(cr, uid, ids, data)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """
        Metodo que anula el documento.
        set: state='cancel'
        """
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

class budgetPoa(osv.Model):
    _name = 'budget.poa'
    def action_open(self, cr, uid, ids, context=None):
        item_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            for line in this.budget_ids:
                item_obj.write(cr, uid, line.id,{'state':'open'})
        self.write(cr, uid, ids, {'state': 'Abierto'})
        return True
    def action_close(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        for this in self.browse(cr, uid, ids):
            certificate_ids = certificate_obj.search(cr, uid, [('date_commited','>=',this.date_start),('date_commited','<=',this.date_end)])
            if certificate_ids:
                if len(certificate_ids)>1:
                    tuple_ids = tuple(certificate_ids)
                    operador = 'in'
                else:
                    tuple_ids = (certificate_ids[0])
                    operador = '='
                #sql_ids = "update budget_certificate set active=False where id %s %s" %(operador,tuple_ids)
                #cr.execute(sql_ids)
        self.write(cr, uid, ids, {'state': 'Cerrado'})
        return True

    def build_periods(self, cr, uid, obj):
        """
        Metodo que devuelve los periodos del presupuesto
        """
        period_obj = self.pool.get('account.period')
        period_ids = period_obj.search(cr, uid, [('date_start','>=',obj.date_start),('date_stop','<=',obj.date_end)])
        return period_ids
    _columns = dict(
        budget_ids = fields.one2many('budget.item','poa_id','Detalle'),
        name = fields.char('Descripcion',size=64,required=True),
        date_start = fields.date('Fecha Inicio', required=True),
        date_end = fields.date('Fecha Fin', required=True),
        state = fields.selection([('Borrador','Borrador'),('Abierto','Abierto'),('Cerrado','Cerrado')],'Estado'),
        )
    _defaults = dict(
        state = 'Borrador',
        )

budgetPoa()

class BudgetBudget(osv.Model):
    """
    Implementacion de clase de Presupuesto
    """
    _name = 'budget.budget'
    _order = 'code'

    _columns = {
        'poa_id': fields.many2one('budget.poa','POA',required=True),
        'code': fields.char('Código', size=64, required=True),
        'name': fields.char('Presupuesto', size=128, required=True),
        'department_id': fields.many2one('hr.department',
                                         string='Departamento',
                                         required=True),
        'date_start': fields.date('Fecha Inicio', required=True),
        'date_end': fields.date('Fecha Fin', required=True),
        'state': fields.selection(
            [
                ('draft', 'Borrador'),
                ('open', 'Ejecución'),
                ('close', 'Cerrado')
            ],
            string='Estado',
            required=True,
            readonly=True
        ),
        'budget_lines': fields.one2many(
            'budget.item',
            'budget_id',
            'Detalle de Presupuesto'
        )
        }

    _defaults = {
        'state': 'draft'
        }

    def action_ok(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'open'})
        return True


class BudgetUserType(osv.Model):
    _name = 'budget.user.type'
    _columns = {
        'code': fields.char('Código', size=32, required=True),
        'name': fields.char('Aplicación Presupuestaria',
                            size=64, required=True)
    }



class BudgetPost(osv.Model):
    """
    Catalogo de Partidas
    """
    _name = 'budget.post'
    _order = 'code'
    # TODO: parent_id

    def create(self, cr, uid, vals, context=None):
        #validar que no se duplique
        post_obj = self.pool.get('budget.post')
        post_ids = post_obj.search(cr, uid, [('code','=',vals['code'])])
        if len(post_ids)>0:
            raise osv.except_osv('Error de usuario','No se permite duplicar partidas.')
        return super(BudgetPost, self).create(cr, uid, vals, context=None)

    def unlink(self, cr, uid, ids, context=None):
        if uid!=1:
            raise osv.except_osv('Aviso','No se permite borrar partidas del catalogo.')
        else:
            res = super(BudgetPost, self).unlink(cr, uid, ids, context)
            return res

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.read(cr, uid, ids, ['id', 'code', 'name'], context):
            res.append((record['id'], '%s - %s' % (record['code'], record['name'])))
        return res

    def name_search(self, cr, uid, name='', args=None,
                    operator='ilike', context=None, limit=80):
        """
        Redefinición de método para permitir buscar por el código
        """
        ids = []
        ids = self.search(cr, uid, [
            '|', ('code', operator, name),
            ('name', operator, name)] + args,
            context=context,
            limit=limit
            )
        return self.name_get(cr, uid, ids, context)

    def _get_nivel(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for budget in self.browse(cr, uid, ids, context):
            if not budget.parent_id:
                nivel = 1
            else:
                nivel = budget.parent_id.nivel + 1
            res[budget.id] = nivel
        return res

    def _checkCode(self, cr, uid, ids, context=None):
        result = False
        if uid==1:
            return True
        post_obj = self.pool.get('budget.post')
        for this in self.browse(cr, uid, ids):
            ##codigo unico
            post_ids = post_obj.search(cr, uid, [('code','=',this.code),('id','!=',this.id)])
            if len(post_ids)>0:
                MSG = 'El codigo de la partida es unico.'
                raise osv.except_osv('Error', MSG)
            ##
            if this.code=='0':
                return True
            if len(this.code)<=1:
                return True
            if this.parent_id:
                aux_parent = this.parent_id.code.replace('.','')
                aux_hija1 = this.code.replace('.','')
                if aux_parent == aux_hija1:
                    return False
                aux_to = len(aux_parent)
                aux_hija = this.code.replace('.','')[0:aux_to]
                if aux_parent==aux_hija:
                    result=True
        return result

    _columns = {
        'tipo':fields.selection([('i','i'),('e','e')],'Tipo'),
        'venta':fields.boolean('Venta'),
        'parent_id':fields.many2one('budget.post','Partida Mayor/padre'),
        'child_ids': fields.one2many('budget.post', 'parent_id', 'Hijos'),
        'code': fields.char('Código', size=64, required=True),
        'code_aux': fields.char('Código', size=128, required=True),
        'name': fields.char('Partida', size=128, required=True),
        'cxc':fields.many2one('account.account','Cuenta por cobrar'),
        'cingreso':fields.many2one('account.account','Cuenta de ingreso'),
        'aux_recaudacion': fields.boolean('Auxiliar para recaudacion?', invisible=True),
        'nivel': fields.function(_get_nivel, method=True, store=True, string='Nivel', type='integer'),
        'internal_type': fields.selection(
            [('view', 'Vista'),
             ('ingreso', 'Ingreso'),
             ('gasto', 'Gasto'),
             ('normal', 'Normal')],
            string='Tipo',
            required=True
        ),
        'budget_type_id': fields.many2one(
            'budget.user.type',
            string='Tipo de Aplicación',
            required=True
        )
    }

    _sql_constraints = [('unique_code_budget', 'unique(code)', u'El codigo de la partida es unico.')]

    _constraints = [
        (_checkCode, 'Error de configuracion! \nEl codigo de la cuenta a crear o editar debe pernecer a la cuenta padre o de mayor! ', ['code']),
    ]

class budgetItemLog(osv.Model):
    _name = 'budget.item.log'
    _columns=dict(
        budget_log_id = fields.many2one('budget.item','Presupuesto'),
        aplicacion = fields.char('Aplicacion',size=15),
        date = fields.date('Fecha'),
        monto = fields.float('Monto'),
    )
    _defaults = dict(
        date = time.strftime('%Y-%m-%d'),
    )
budgetItemLog()

class BudgetItemMigrated(osv.Model):
    """
    Instancia de una Partida Migrada
    """
    _name = 'budget.item.migrated'
    _description = 'Instancia de Partida presupuestaria migrada'

    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            if context.has_key('elimina') or formulario.elimina:
                return super(BudgetItemMigrated, self).unlink(cr, uid, ids, context=None)
            else:
                raise osv.except_osv('Error', 'No pueden eliminar registros')

    _columns = {
        'elimina':fields.boolean('Permitir Eliminar'),
        'financia_id':fields.many2one('budget.financiamiento','Cta. Financiera'),
        'desc':fields.char('Descripcion',size=128),
        'is_pronto':fields.boolean('Pronto Pago'),
        'certificate_id':fields.many2one('budget.certificate','Certificado'),
        'move_id':fields.many2one('account.move','Comprobante'),
        'move_line_id':fields.many2one('account.move.line','Linea Comprobante'),
        'budget_item_id': fields.many2one('budget.item', "Budget item", readonly=True),
        'type_budget' : fields.char('Tipo', size=10, readonly=True),
        'code': fields.related('budget_post_id', 'code', type="char", size=256,
                               string="Cod. Partida", store=True),#char('Detalle', size=256),
#        'code': fields.char('Código', size=20, readonly=True),
        'date': fields.date('Fecha', readonly=True),
        'name': fields.related('budget_post_id', 'name', type="char", size=256,
                              string="Denominación", store=True),#char('Detalle', size=256),
        'budget_post_id': fields.many2one(
            'budget.post',
            string='Partida',
            required=True,
            readonly=True
        ),
        'program_code': fields.char('codigo programa', size=10, readonly=True),
        'planned_amount': fields.float('Asignación Inicial', digits_compute=DP, readonly=True),
        #campos no funcion
        'reform_amount': fields.float('Reforma',digits_compute=DP, readonly=True),
        'codif_amount': fields.float('Codificado',digits_compute=DP, readonly=True),
        'commited_amount': fields.float('Comprometido',digits_compute=DP, readonly=True),
        'devengado_amount': fields.float('Devengado',digits_compute=DP, readonly=True),
        'paid_amount': fields.float('Devengado',digits_compute=DP, readonly=True),
        'commited_balance': fields.float('Saldo x Comprometer',digits_compute=DP, readonly=True),
        'devengado_balance': fields.float('Saldo x Devengar',digits_compute=DP, readonly=True),
        'avai_amount': fields.float('Saldo Disponible',digits_compute=DP, readonly=True),
        }
BudgetItemMigrated()

class budgetFinanciamiento(osv.Model):
    _name = 'budget.financiamiento'

    def _dec_code_fina(self, cr, uid, ids, fields, context, args):
        res = {}
        for this in self.browse(cr, uid, ids,context):
            aux_res = this.name[0:2]
            res[this.id] = aux_res
        return res

    def _dec_code_sc(self, cr, uid, ids, fields, context, args):
        res = {}
        for this in self.browse(cr, uid, ids,context):
            aux_res = this.desc[0:2]
            res[this.id] = aux_res
        return res

    _columns = dict(
        sc = fields.function(_dec_code_sc,string="Desc Corta",store=True,type='char',size=5),
        code = fields.function(_dec_code_fina,string="Codigo",store=True,type='char',size=5),
        name = fields.char('Codigo',size=12,required=True),
        desc = fields.char('Descripcion',size=128,required=True),
        desc_report = fields.char('Descripcion Aplicacion del Gasto',size=256),
    )

    def name_search(self, cr, uid, name='', args=None,
                    operator='ilike', context=None, limit=80):
        """
        Redefinición de método para permitir buscar por el código
        """
        ids = []
        ids = self.search(cr, uid, [
            '|', ('name', operator, name), ('desc', operator, name)] + args,
            context=context, limit=limit)
        return self.name_get(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for rec in self.browse(cr, uid, ids):
            aux =  ustr(rec.name) + ' - ' + ustr(rec.desc)
            res.append((rec['id'], aux))
        return res

budgetFinanciamiento()

class BudgetItem(osv.Model):
    """
    Instancia de una Partida
    """
    _name = 'budget.item'
    _description = 'Instancia de Partida presupuestaria'
    _order = 'code_aux asc'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for rec in self.browse(cr, uid, ids):#read(cr, uid, ids, ['code', 'name']):
            if rec.budget_post_id:
                aux =  ustr(rec.budget_post_id.name)#ustr(rec['name'])
            else:
                aux =  ustr(rec['name'])
            rec_code = ustr(rec.code)
            anio = rec.year_id
#            disponible = str(rec.avai_amount)
#            txt = '{0} - {1} - {3}'.format(rec_code, aux, disponible)
#            txt = '{0} - {1}'.format(ustr(rec_code),ustr(aux))
            if anio:
                txt = ustr(rec_code) + ' - ' + ustr(aux) + ' - ' + anio.code
            else:
                txt = ustr(rec_code) + ' - ' + ustr(aux)
            res.append((rec['id'], txt))
        return res

    def name_search(self, cr, uid, name='', args=None,
                    operator='ilike', context=None, limit=80):
        """
        Redefinición de método para permitir buscar por el código
        """
        ids = []
        ids = self.search(cr, uid, [
            '|', ('code', operator, name), ('name', operator, name)] + args,
            context=context, limit=limit)
        return self.name_get(cr, uid, ids, context)

    def _compute_budget_all(self, cr, uid, ids, fields, args, context=None):
        """
        Metodo de calculo para los campos:
        reserved_amount
        commited_amount
        En el metodo se considera el context si tiene los limites de periodos
        para consultar datos, la ejecucion presupuestaria puede ser entre meses
        funcionalidad para reportes.
        codificado = inicial + reforma (C = A + B)
        COMPROMISO: D
        DEVENGADO: E
        PAGADO: F
        saldo por comprometer: codificado - comprometido (G = C - D)
        saldo por devengar: codificado - devengado (H = C - E)
        """
        res = {}
        period_ids = context.get('period_ids', [])
        cur_obj = self.pool.get('res.currency')
        req_obj = self.pool.get('budget.certificate.line')
        reforma_obj = self.pool.get('budget.reform')
        migrado_obj = self.pool.get('budget.item.migrated')
        reforma_obj = self.pool.get('budget.reform')
        poa_obj = self.pool.get('budget.poa')
        #mario
        #        it_obj = self.pool.get('budget.item')
        #        item_aux = it_obj.browse(cr, uid, ids[0])
        #        poa_ids = poa_obj.search(cr, uid, [('id','=',item_aux.poa_id.id)])
        by_date = context.get('by_date',False)
        if by_date:
#            poa_ids = poa_obj.search(cr, uid, [('date_start','>=',context['date_start']),('date_end','<=',context['date_end'])])
            poa_ids = poa_obj.search(cr, uid, [('id','=',context['poa_id'])])
        else:
            poa_ids = poa_obj.search(cr, uid, [])
        if context.get('move_ids'):
            move_ids = context['move_ids']
            if len(move_ids) == 1:
                move_ids.append(move_ids[0])
            poa_id = context.get('poa_id')
            if len(ids)>1:
                tuple_ids = tuple(ids)
                operador = 'in'
            else:
                tuple_ids = (ids[0])
                operador = '='
            poa_data = poa_obj.read(cr, uid, poa_id, ['date_start','date_end'])

            sql_ids = "select id,planned_amount,type_budget from budget_item where poa_id=%s and id %s %s" %(poa_id, operador,tuple_ids)
            cr.execute(sql_ids)
            fetch_item_ids = cr.fetchall()
            item_ids = []
            for item_id in fetch_item_ids:
                res[item_id[0]] = {
                    'type_budget': item_id[2],
                    'planned_amount': item_id[1],
                    'codif_amount': 0.00,  # codificado
                    'commited_balance': 0.00, #saldo x comprometer
                    'devengado_balance': 0.00, #saldo x devengar
                    'paid_amount': 0.00, #pagado/recaudado
                    'devengado_amount': 0.00, #devengado
                    'avai_amount': 0.00,  # disponible
                    'request_amount': 0.00,  # solicitado
                    'reserved_amount': 0.00,  # certificado
                    'commited_sobregiro': False,
                    'devengado_sobregiro': False,
                }
            item_ids = res.keys()
            if len(item_ids)>1:
                tuple_items = tuple(item_ids)
                operador = "in"
            elif len(item_ids)==1:
                tuple_items = (item_ids[0])
                operador = "="
            else:
                return res

################
            sql = "SELECT account_move_line.id,coalesce(debit,0),coalesce(credit,0),budget_accrued,budget_paid,budget_post.venta,budget_post.id as budget_post,account_move_line.budget_id,account_move.type  \
FROM account_move_line,budget_item,budget_post,account_move WHERE account_move.id=account_move_line.move_id and budget_item.budget_post_id=budget_post.id and account_move_line.budget_id=budget_item.id and (budget_accrued=true or budget_paid=true) and account_move_line.budget_id %s %s and account_move_line.move_id in %s"%(operador, tuple_items, tuple(move_ids))
            cr.execute(sql)
            data = cr.fetchall()
            devengado_aux = {}
            pagado_aux = {}
            for moveline in data:
                if moveline[5] == True:
                    if moveline[3] == True:
                        if abs(moveline[1])>0:
                            aux_amount = moveline[1]
                        else:
                            aux_amount = moveline[2]
                        devengado_aux[moveline[7]] = devengado_aux.get(moveline[7],0) + aux_amount
                    if moveline[4] == True:
                        if abs(moveline[1])>0:
                            aux_amount = moveline[1]
                        else:
                            aux_amount = moveline[2]
                        pagado_aux[moveline[7]] = pagado_aux.get(moveline[7],0) + aux_amount
                else:
                    if moveline[3] == True:
                        if abs(moveline[1])>0:
                            aux_amount = moveline[1]
                        else:
                            aux_amount = moveline[2]
                        devengado_aux[moveline[7]] = devengado_aux.get(moveline[7],0) + aux_amount
                    if moveline[4] == True:
                        if abs(moveline[1])>0:
                            aux_amount1 = moveline[1]
                        else:
                            aux_amount1 = moveline[2]
                        pagado_aux[moveline[7]] = pagado_aux.get(moveline[7],0) + aux_amount1

                for item_id in item_ids:
                    res[item_id]['devengado_amount'] = devengado_aux.get(item_id,0)
                    res[item_id]['paid_amount'] = pagado_aux.get(item_id,0)
            return res

################

        else:
            for poa_id in poa_ids:
                if len(ids)>1:
                    tuple_ids = tuple(ids)
                    operador = 'in'
                else:
                    tuple_ids = (ids[0])
                    operador = '='
                poa_data = poa_obj.read(cr, uid, poa_id, ['date_start','date_end'])
                sql_ids = "select id,planned_amount,type_budget from budget_item where poa_id=%s and id %s %s" %(poa_id, operador,tuple_ids)
                cr.execute(sql_ids)
                fetch_item_ids = cr.fetchall()
                item_ids = []
                for item_id in fetch_item_ids:
                    res[item_id[0]] = {
                        'type_budget': item_id[2],
                        'planned_amount': item_id[1],
                        'codif_amount': 0.00,  # codificado
                        'commited_balance': 0.00, #saldo x comprometer
                        'devengado_balance': 0.00, #saldo x devengar
                        'paid_amount': 0.00, #pagado/recaudado
                        'devengado_amount': 0.00, #devengado
                        'avai_amount': 0.00,  # disponible
                        'request_amount': 0.00,  # solicitado
                        'reserved_amount': 0.00,  # certificado
                        'commited_sobregiro': False,
                        'devengado_sobregiro': False,
                    }
                item_ids = res.keys()
                if len(item_ids)>1:
                    tuple_items = tuple(item_ids)
                    operador = "in"
                elif len(item_ids)==1:
                    tuple_items = (item_ids[0])
                    operador = "="
                else:
                    return res
                by_date = context.get('by_date',False)
                if by_date == False:
                    date_start = str(poa_data['date_start'])
                    date_end = str(poa_data['date_end'])
                else:
                    date_start = context.get('date_start',False)
                    date_end = context.get('date_end',False)

                tmp = {}  # acumula el valor a restar
                ##DIEGO##
                #sacar los items migrados menores que la fecha indicada
                #1 sacar las reformas
                sql_reforma = """
                select b.budget_item_id,b.date,b.reform_amount
                from (select budget_item_id,max(date) as maxdate
                     from budget_item_migrated where date<='%s' group by budget_item_id) as child inner join budget_item_migrated as b on b.budget_item_id=child.budget_item_id and b.date=child.maxdate and b.budget_item_id %s %s order by b.budget_item_id""" %(date_end, operador,tuple_items)
                cr.execute(sql_reforma)
                data = cr.fetchall()
                reforma_migrated = {}
                for reforma in data:
                    if reforma[0]:
                        reforma_migrated[reforma[0]] = reforma[2]
                sql_more = "select commited_amount,devengado_amount,paid_amount,budget_item_id from budget_item_migrated where date>='%s' and date<='%s' and budget_item_id %s %s" %(date_start,date_end, operador,tuple_items)
                cr.execute(sql_more)
                data = cr.fetchall()
                comprometido_migrated = {}
                pagado_migrated = {}
                devengado_migrated = {}
                for vals in data:
                    if vals[0]:
                        comprometido_migrated[vals[3]] = comprometido_migrated.get(vals[3],0) + vals[0]
                    if vals[1]:
                        devengado_migrated[vals[3]] = devengado_migrated.get(vals[3],0) + vals[1]
                    if vals[2]:
                        pagado_migrated[vals[3]] = pagado_migrated.get(vals[3],0) + vals[2]
                sumar = {}
                restar = {}
                traspaso_aumento = {}
                traspaso_disminucion = {}
                suplemento = {}
                reduccion = {}
                #reformas de ampliacion o disminucion
                if context.get('reforms1',False):
                    reforma_ids = context['reforms1']
                else:
                    reforma_ids = reforma_obj.search(cr, uid, [('budget_id',operador,tuple_items),('date_done','>=',date_start),('date_done','<=',date_end)])
                reforma_browse = reforma_obj.read(cr, uid, reforma_ids, ['budget_id','budget2_id','state','amount','type_transaction'])
                for reforma in reforma_browse:
                    if reforma['state'] == 'done' and reforma['type_transaction'] == 'ampliacion':
                        suplemento[reforma['budget_id'][0]] = suplemento.get(reforma['budget_id'][0],0) + reforma['amount']
                        sumar[reforma['budget_id'][0]] = sumar.get(reforma['budget_id'][0],0) + reforma['amount']
                    elif reforma['state'] == 'done' and reforma['type_transaction'] in ['disminucion', 'transferencia']:
                        reduccion[reforma['budget_id'][0]] = reduccion.get(reforma['budget_id'][0],0) + reforma['amount']
                        restar[reforma['budget_id'][0]] = restar.get(reforma['budget_id'][0],0) + reforma['amount']

                #reformas de transferencia
                if context.get('reforms2',False):
                    reforma2_ids = context['reforms2']
                else:
                    reforma2_ids = reforma_obj.search(cr, uid, [('budget2_id',operador,tuple_items),('date_done','>=',date_start),('date_done','<=',date_end)])
                reforma_browse = reforma_obj.read(cr, uid, reforma2_ids, ['budget2_id','state','type_transaction','amount'])
                for reforma in reforma_browse:
                    if reforma['state'] == 'done' and reforma['type_transaction'] == 'transferencia':
                        sumar[reforma['budget2_id'][0]] = sumar.get(reforma['budget2_id'][0],0) + reforma['amount']
                        if reforma['amount']>=0:
                            traspaso_aumento[reforma['budget2_id'][0]] = traspaso_aumento.get(reforma['budget2_id'][0],0) + reforma['amount']
                        else:
                            traspaso_disminucion[reforma['budget2_id'][0]] = traspaso_disminucion.get(reforma['budget2_id'][0],0) + reforma['amount']

                #DIEGO#
                sql_cert = "SELECT budget_certificate_line.id,budget_certificate_line.amount,budget_certificate_line.amount_certified,budget_certificate_line.amount_commited,budget_id FROM budget_certificate_line,budget_certificate \
                WHERE budget_certificate.state='commited' and budget_certificate_line.certificate_id=budget_certificate.id and budget_id %s %s \
                AND budget_certificate.date_commited is not Null and budget_certificate.date_commited>='%s' and budget_certificate.date_commited<='%s'" % (operador,tuple_items,date_start, date_end)
                cr.execute(sql_cert)
                data_cert = cr.fetchall()
                tmp = {}
                for req in data_cert:
                    if req[2]:
                        res[req[4]]['reserved_amount'] = res.get(req[4],0)['reserved_amount'] + req[2]
                    else:
                        res[req[4]]['reserved_amount'] = res.get(req[4],0)['reserved_amount'] + 0
                    if req[1]:
                        res[req[4]]['request_amount'] += res.get(req[4],0)['request_amount'] + req[1]
                    else:
                        res[req[4]]['request_amount'] += res.get(req[4],0)['request_amount']
                    if req[3]:
                        tmp[req[4]] = tmp.get(req[4],0) + req[3]
                    else:
                        tmp[req[4]] = tmp.get(req[4],0) + 0
    #            for req in req_obj.read(cr, uid, req_ids, ['amount_certified','amount','amount_commited']):
    #                res[obj['id']]['reserved_amount'] += req['amount_certified']
    #                res[obj['id']]['request_amount'] += req['amount']
    #                tmp += req['amount_commited']
    #                elif req.state == 'certified':
    #                    res[obj.id]['reserved_amount'] += req.amount_certified
    #                    res[obj.id]['request_amount'] += req.amount
    #                    tmp += req.amount_certified
    #                elif req.state == 'request':
    #                    res[obj.id]['request_amount'] += req.amount
    #                    tmp += req.amount

                #devengado,pagado amount
                #buscar los account move line donde el budget_id es igual a budget item
                sql = "SELECT account_move_line.id,coalesce(debit,0),coalesce(credit,0),budget_accrued,budget_paid,budget_post.venta,budget_post.id as budget_post,account_move_line.budget_id,account_move.type  \
    FROM account_move_line,budget_item,budget_post,account_move WHERE account_move.id=account_move_line.move_id and account_move.state='posted' and budget_item.budget_post_id=budget_post.id and account_move_line.budget_id=budget_item.id and account_move_line.migrado=False and account_move_line.state='valid' and (budget_accrued=true or budget_paid=true) and account_move_line.budget_id %s %s and account_move_line.date>='%s' and account_move_line.date<='%s'"%(operador,tuple_items, date_start, date_end)
                cr.execute(sql)
                data = cr.fetchall()
                devengado_aux = {}
                pagado_aux = {}
                for moveline in data:
                    if moveline[5] == True:
                        if moveline[3] == True:
                            if abs(moveline[1])>0:
                                aux_amount = moveline[1]
                            else:
                                aux_amount = moveline[2]
                            devengado_aux[moveline[7]] = devengado_aux.get(moveline[7],0) + aux_amount
                        if moveline[4] == True:
                            if abs(moveline[1])>0:
                                aux_amount = moveline[1]
                            else:
                                aux_amount = moveline[2]
                            pagado_aux[moveline[7]] = pagado_aux.get(moveline[7],0) + aux_amount
                    else:
                        if moveline[3] == True:
                            if abs(moveline[1])>0:
                                aux_amount = moveline[1]
                            else:
                                aux_amount = moveline[2]
                            devengado_aux[moveline[7]] = devengado_aux.get(moveline[7],0) + aux_amount
                        if moveline[4] == True:
                            if abs(moveline[1])>0:
                                aux_amount1 = moveline[1]
                            else:
                                aux_amount1 = moveline[2]
                            pagado_aux[moveline[7]] = pagado_aux.get(moveline[7],0) + aux_amount1
                for item_id in item_ids:
                    if reforma_migrated.get(item_id,0):
                        res[item_id]['reform_amount'] = sumar.get(item_id,0) - restar.get(item_id,0) + reforma_migrated.get(item_id,0)
                    else:
                        res[item_id]['reform_amount'] = sumar.get(item_id,0) - restar.get(item_id,0)
                    res[item_id]['suplemento'] = suplemento.get(item_id,0)
                    res[item_id]['reduccion'] = reduccion.get(item_id,0)
                    res[item_id]['traspaso_aumento'] = traspaso_aumento.get(item_id,0)
                    res[item_id]['traspaso_disminucion'] = traspaso_disminucion.get(item_id,0)

                    res[item_id]['codif_amount'] = res[item_id]['planned_amount'] + res[item_id]['reform_amount']
                    if res[item_id]['type_budget'] == 'gasto':
                        res[item_id]['commited_amount'] = tmp.get(item_id,0) + comprometido_migrated.get(item_id,0)
                        res[item_id]['commited_balance'] = res[item_id]['codif_amount'] - res[item_id]['commited_amount']
                    else:
                        res[item_id]['commited_amount'] = 0
                        res[item_id]['commited_balance'] = 0
                    res[item_id]['devengado_amount'] = devengado_aux.get(item_id,0) + devengado_migrated.get(item_id,0)
                    res[item_id]['paid_amount'] = pagado_aux.get(item_id,0) + pagado_migrated.get(item_id,0)
                    res[item_id]['devengado_balance'] = res[item_id]['codif_amount'] - res[item_id]['devengado_amount']
                    res[item_id]['avai_amount'] = res[item_id]['codif_amount'] - res[item_id]['commited_amount']
                    if  res[item_id]['commited_balance'] < 0:
                        res[item_id]['commited_sobregiro'] = True
                    else:
                        res[item_id]['commited_sobregiro'] = False
                    if  res[item_id]['devengado_balance'] < 0:
                        res[item_id]['devengado_sobregiro'] = True
                    else:
                        res[item_id]['devengado_sobregiro'] = False
            return res

    def _get_movelines(self, cr, uid, ids, context):
        result = {}
        for moveline in self.pool.get('account.move.line').browse(
                cr, uid, ids, context=context
                ):
            result[moveline.budget_id.id] = True
        return result.keys()

    def _get_certificates(self, cr, uid, ids, context):
        result = {}
        for budget in self.pool.get('budget.certificate.line').browse(
                cr, uid, ids, context=context
                ):
            result[budget.budget_id.id] = True
        return result.keys()

    def _get_movelines(self, cr, uid, ids, context):
        result = {}
        for moveline in self.pool.get('account.move.line').browse(
                cr, uid, ids, context=context
                ):
            result[moveline.budget_id.id] = True
        return result.keys()

    def _get_reforms(self, cr, uid, ids, context):
        result = {}
        for budget in self.pool.get('budget.reform').browse(
                cr, uid, ids, context
                ):
            result[budget.budget_id.id] = True
            if budget.budget2_id:
                result[budget.budget2_id.id] = True
        return result.keys()


    STORE_VAR = False

    STORE_VAR2 = {
        'budget.item': (
            lambda self, cr, uid, ids, c={}: ids,
            [
                'request_ids',
#                'reserved_amount',
#                'reform_amount',
#                'commited_amount',
                'reforma_ids',
#                'devengado_amount',
#                'paid_amount',
                'reforma_to_ids'
            ],
            10),
        'budget.certificate.line': (
            _get_certificates,
            [
                'amount',
                'amount_certified',
                'amount_compromised',
                'budget_line_id',
                'state'
            ],
            10),
        'budget.reform': (
            _get_reforms,
            ['amount', 'type_transaction', 'state'],
            10),
        'account.move.line': (
            _get_movelines,
            ['debit','credit','date','budget_id','budget_accrued','budget_paid', 'state'],
            10)
        }

    def _dec_code(self, cr, uid, ids, fields, context, args):
        parameter_obj = self.pool.get('ir.config_parameter')
        codificacion_ids = parameter_obj.search(cr, uid, [('key','=','codigoaux')],limit=1)
        band = False
        if codificacion_ids:
            code_budget = parameter_obj.browse(cr, uid, codificacion_ids[0]).value
            if code_budget=='Si':
                band = True
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            if band:
                if obj.program_id.sequence:
                    aux_res =  obj.program_id.sequence + obj.budget_post_id.code
                else:
                    aux_res =  obj.task_id.project_id.program_id.sequence + obj.budget_post_id.code
            else:
                aux_res = obj.code
            res[obj.id] = aux_res
        return res

    def _dec_tipo(self, cr, uid, ids, fields, context, args):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            aux_res = obj.budget_post_id.code[0:1]
            res[obj.id] = aux_res
        return res

    _columns = {
        'aux_tipo':fields.function(_dec_tipo,string="Tipo Aplicacion",store=True,type='char',size=1),
        'financia_id':fields.many2one('budget.financiamiento','Cuenta Financiera'),
        'year_id': fields.related('project_id', 'fy_id', type="many2one",relation="account.fiscalyear",
                           string="Anio Fiscal", store=True),
        'poa_id': fields.related('task_id', 'poa_id', type="many2one",relation="budget.poa",
                           string="POA", store=True),
        'code_report':fields.function(_dec_code,string="Codigo reportes",store=True,type='char',size=32),
        'code_aux':fields.related('budget_post_id', 'code', type="char", size=256,
                              string="Codigo Aux", store=True),
        'code': fields.char('Código', size=64),
        'name': fields.related('budget_post_id', 'name', type="char", size=256,
                              string="Detalle", store=True),#char('Detalle', size=256),
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('cancel', 'Cancelled'),
                ('open', 'Confirmed'),
                ('done', 'Done')
            ],
            string='Estado',
            select=True,
            required=True,
            readonly=True
        ),
        'date_start': fields.related('task_id', 'date_start', type="date",
                              string="Fecha inicio", store=True),
        'date_end':  fields.related('task_id', 'date_end', type="date",
                              string="Fecha Fin", store=True),#fields.date('Fecha Fin'),
        'budget_post_id': fields.many2one(
            'budget.post',
            string='Partida',
            required=True
        ),
        'budget_id': fields.many2one(
            'budget.budget',
            string='Presupuesto',
            select=True
        ),
        'task_id': fields.many2one(
            'project.task',
            string='Actividad',
            ondelete="cascade",
            select=True
        ),
        'type_budget':fields.related('project_id', 'type_budget', type="char",size=10,
                           string="Tipo presupuesto", store=True),
        'project_id': fields.related('task_id', 'project_id', type="many2one",relation="project.project",
                           string="Proyecto", store=True),
        'program_id': fields.related('project_id', 'program_id', type="many2one",relation="project.program",
                           string="Programa", store=True),
        'department_id': fields.many2one(
            'hr.department',
            string='Departamento'
        ),
        'planned_amount': fields.float('Asignación Inicial',
                                       digits_compute=DP),
        #campos funcion no store
        'suplemento': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                          string='Suplemento', digits_compute=DP),
        'reduccion': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                          string='Reduccion', digits_compute=DP),
        'traspaso_aumento': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                          string='Traspaso aumento', digits_compute=DP),
        'traspaso_disminucion': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                          string='Traspaso disminucion', digits_compute=DP),

        'reform_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                          string='Reformado', digits_compute=DP),
        'request_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                          string='Solicitado', digits_compute=DP),
        'codif_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                         string='Codificado', digits_compute=DP),
        'commited_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                           string='Comprometido', digits_compute=DP),
        'reserved_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                           string='Certificado', digits_compute=DP),
        'devengado_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                           string='Devengado', digits_compute=DP),
        'paid_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                        string='Pagado', digits_compute=DP),
        'commited_balance': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                         string='Saldo x Comprometer', digits_compute=DP),
        'commited_sobregiro': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
                                           string='Sobregirada codificado', type='boolean'),
        'devengado_sobregiro': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
                                              string='Sobregirada devengado', type='boolean'),
        'devengado_balance': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                         string='Saldo x Devengar', digits_compute=DP),
        'avai_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR,
                                         string='Disponible', digits_compute=DP),
        #funcion con store
#        'suplemento': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                          string='Suplemento', digits_compute=DP),
#        'reduccion': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                          string='Reduccion', digits_compute=DP),
#        'traspaso_aumento': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                          string='Traspaso aumento', digits_compute=DP),
#        'traspaso_disminucion': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                          string='Traspaso disminucion', digits_compute=DP),
#
#        'reform_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                          string='Reformado', digits_compute=DP),
#        'request_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                          string='Solicitado', digits_compute=DP),
#        'codif_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                         string='Codificado', digits_compute=DP),
#        'commited_amount': fields.function(_compute_budget_all,method=True, multi='budget', store=True,
#                                           string='Comprometido', digits_compute=DP),
#        'reserved_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                           string='Certificado', digits_compute=DP),
#        'devengado_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                           string='Devengado', digits_compute=DP),
#        'paid_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                        string='Pagado', digits_compute=DP),
#        'commited_balance': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                         string='Saldo x Comprometer', digits_compute=DP),
#        'commited_sobregiro': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                           string='Sobregirada codificado', type='boolean'),
#        'devengado_sobregiro': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                              string='Sobregirada devengado', type='boolean'),
#        'devengado_balance': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                         string='Saldo x Devengar', digits_compute=DP),
#        'avai_amount': fields.function(_compute_budget_all, method=True, multi='budget', store=STORE_VAR2,
#                                         string='Disponible', digits_compute=DP),
        ######
        'request_ids': fields.one2many('budget.certificate.line', 'budget_id', 'Documentos'),
        'reforma_ids': fields.one2many('budget.reform', 'budget_id', 'Reformas Aplicadas'),
        'reforma_to_ids': fields.one2many('budget.reform', 'budget2_id', 'Reforma para transferencias'),
        'log_ids':fields.one2many('budget.item.log','budget_log_id','Detalle Aplicacion'),
        }

    def _get_dept(self, cr, uid, context):
        return context.get('default_department_id', False)

    _defaults = {
        'state': 'draft',
        'department_id': _get_dept
        }

    def set_codes(self, cr, uid, ids, context=None):
        parameter_obj = self.pool.get('ir.config_parameter')
        codificacion_ids = parameter_obj.search(cr, uid, [('key','=','codigopartida')],limit=1)
        codificacion_ids2 = parameter_obj.search(cr, uid, [('key','=','muni')],limit=1)
        band = False
        if codificacion_ids:
            code_budget = parameter_obj.browse(cr, uid, codificacion_ids[0]).value
            if code_budget=='Si':
                band = True
        for obj in self.browse(cr, uid, ids, context):
#            code = '{0}.{1}.{2}'.format(
#                obj.task_id.project_id.code,
#                obj.task_id.code,
#                obj.budget_post_id.code)
#            code = '{0}.{1}.{2}'.format(
#                obj.budget_post_id.code,
#                obj.task_id.project_id.code,
#                obj.task_id.project_id.program_id.sequence
#                )
            if band:
                if obj.type_budget=='ingreso':
                    code = '{0}.{1}.{2}'.format(
                        obj.budget_post_id.code,
                        obj.task_id.project_id.code,
                        obj.task_id.project_id.program_id.sequence,
                    )
                else:
                    if codificacion_ids2:
                        code_budget_muni = parameter_obj.browse(cr, uid, codificacion_ids2[0]).value
                        if code_budget_muni=='mil':
                            code = '{0}.{1}.{2}'.format(
                                obj.budget_post_id.code,
                                obj.task_id.project_id.code,
                                obj.task_id.project_id.program_id.sequence,
                            )
                    else:
                        code = '{0}.{1}'.format(
                            obj.task_id.project_id.program_id.sequence,
                            obj.budget_post_id.code
                        )
            else:
                code = '{0}.{1}.{2}'.format(
                    obj.budget_post_id.code,
                    obj.task_id.project_id.code,
                    obj.task_id.project_id.program_id.sequence,
                )
            self.write(cr, uid, obj.id, {'code': code})
        return True
    #quitado cap milagro
    _sql_constraints = [('unique_budget', 'unique(project_id,budget_post_id)', u'No se permite la misma partida mas de una vez.')]

BudgetItem()

class BudgetCertificate(osv.Model):
    """
    Clase de implementacion de Documento presupuestario
    con el detalle realiza al ejecucion prespuestaria
    """

    _name = 'budget.certificate'
    _inherit = ['mail.thread']
    _description = 'Certificados Presupuestarios'
    _order = 'date DESC,name desc'
    __logger = logging.getLogger(_name)
    DP = dp.get_precision('Budget')
    STATES_VALUE = {'draft': [('readonly', False)]}

    def onchange_payment(self, cr, uid, ids, payment_id, context={}):
        payment_obj = self.pool.get('payment.request')
        payment = payment_obj.browse(cr, uid, payment_id)
        vals = {}
        return {'value':{'notes':payment.concepto,'partner_id':payment.partner_id.id}}

    def onchange_project(self, cr, uid, ids, project_id, context={}):
        project_obj = self.pool.get('project.project')
        project = project_obj.browse(cr, uid, project_id)
        task_id = project.tasks[0].id
        vals = {}
        return {'value':{'task_id':task_id}}

    def unlink(self, cr, uid, ids, context):
        MSG = 'Solo se permite eliminar registros en borrador y sin numeracion.'
        for obj in self.browse(cr, uid, ids, context):
            if obj.state=='draft':
                if obj.name!='/':
                    raise osv.except_osv('Error', MSG)
                else:
                    return super(BudgetCertificate, self).unlink(cr, uid, ids, context)
            else:
                raise osv.except_osv('Error', MSG)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            number = r.name + ' - ' + r.notes[0:70]+'...'
            if r.state in ['request', 'certified']:
                number = r.name + ' - ' +r.notes[0:70]+'...'
            elif r.state == 'commited':
                if r.number and r.notes:
                    number = r.number + ' - ' +r.notes[0:70]+'...'
                else:
                    number = r.number
            res.append((r.id, number))
        return res

    def set_sequence(self, cr, uid, ids, sequence='request'):
        """
        Asigna el numero de secuencia para el documento.
        """
        certificate_obj = self.pool.get('budget.certificate')
        year_obj = self.pool.get('account.fiscalyear')
        for this in self.browse(cr, uid, ids):
            if this.date>='2017-01-01':
                year_ids = year_obj.search(cr, uid, [('date_start','<=',this.date),('date_stop','>=',this.date)],limit=1)
                if year_ids:
                    year = year_obj.browse(cr, uid, year_ids[0])
                else:
                    raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha de compromiso.')
                certificate_ids = certificate_obj.search(cr, uid, [('name','!=','/'),('date','>=',year.date_start),('date','<=',year.date_stop),
                                                                   ('tipo_aux','!=','ingreso')],order='name desc')
                if certificate_ids:
                    cert = certificate_obj.browse(cr, uid, certificate_ids[0])
                    number = str(int(cert.name)+1).zfill(5)
                    #number = str(len(certificate_ids)+1).zfill(5)
                else:
                    number = str(1).zfill(5)
                #validar que no se repita
                cert_ids = certificate_obj.search(cr, uid, [('name','=',number),('date','>=',year.date_start),('date','<=',year.date_stop)])
                if cert_ids:
                    raise osv.except_osv('Error de usuario', 'El numero de compromiso es unico.')
            else:
                seq_obj = self.pool.get('ir.sequence')
                number = seq_obj.get(cr, uid, 'budget.certificate')
        self.write(cr, uid, ids, {
            'name': number,
            'number':number,
            'fiscalyear_id':year_ids[0],
        })
        return True

    def _get_user(self, cr, uid, context=None):
        return uid

    def _get_certificate_lines(self, cr, uid, ids, context):
        res = {}
        for obj in self.pool.get('budget.certificate.line').browse(cr, uid, ids, context):
            res[obj.certificate_id.id] = True
        return res.keys()

    def _amount_total(self, cr, uid, ids, fields, args, context):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {
                'amount_total': 0,
                'amount_certified': 0,
                'amount_commited': 0
                }
            for line in obj.line_ids:
                res[obj.id]['amount_total'] += line.amount
                res[obj.id]['amount_certified'] += line.amount_certified
                res[obj.id]['amount_commited'] += line.amount_commited
        return res

    def _compute_budget(self, cr, uid, ids, fields, args, context):
        """
        Metodo de calculo de total devengado para el compromiso
        presupuestario utilizado en las facturas 'invoice_ids'
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {
                'amount_accured': 0,
                'amount_paid': 0
                }
            for inv in obj.invoice_ids:
                res[obj.id]['amount_accured'] += inv.amount_pay
        return res

    STORE_VAR = {
        'budget.certificate': (lambda self, cr, uid, ids, c={}: ids,
                               ['line_ids'],
                               10),
        'budget.certificate.line': (
            _get_certificate_lines,
            [
                'amount',
                'amount_certified',
                'amount_commited',
                'budget_id',
                'state'
            ],
            10)
        }

    _columns = {
        'fiscalyear_id':fields.many2one('account.fiscalyear','Anio Fiscal'),
        'active':fields.boolean('Activo'),
        'log_repetido':fields.char('Log Partidas Repetidas',size=256),
        'revisado':fields.boolean('Revisado??'),
        'item2_ids':fields.one2many('budget.item.migrated','certificate_id','Detalle Reajuste'),
        'tipo_aux':fields.selection([('ingreso','ingreso'),('gasto','gasto')],'Tipo Interno'),
        'migrado':fields.boolean('Migrado'),
#        'budget_ids':fields.many2many('budget.item','c_i_rel','c_id','i_id','Detalle de partidas'),
        'ref_doc': fields.char('Ref. Docmto',size=256),
        'payment_id':fields.many2one('payment.request','Orden de pago'),
        'name': fields.char('Nro. de certificado',
                            size=32, required=True,
                            readonly=True),
        'number': fields.char('Número de Compromiso', readonly=True, size=16),
        'notes': fields.text('Notas',
                             readonly=True, states=STATES_VALUE),
        'user_id': fields.many2one(
            'res.users',
            string='Creado por:',
            required=True,
            readonly=True,
            ),
        'department_id': fields.many2one(
            'hr.department',
            string='Dirección / Coordinación',
            required=True,
            readonly=True,
            states=STATES_VALUE,
            ),
        'solicitant_id':fields.many2one(
            'hr.employee',
            states=STATES_VALUE,
            readonly=True,
            string='Solicitado por:',
            required=True,
            ),
        'state': fields.selection([
            ('draft', 'Borrador'),
            ('request', 'Solicitado'),
            ('certified', 'Certificado'),
            ('commited', 'Comprometido'),
            ('anulado', 'Anulado'),
            ('cancel', 'Rechazado')],
            string='Estado',
            required=True),
        'budget_type': fields.selection(
            [
                ('corriente', 'CORRIENTE'),
                ('inversion', 'INVERSION'),
                ('general', 'GENERAL'),
                ('ogastos', 'OTROS GASTOS (CORRIENTE)'),
                ('opublica', 'OBRAS PUBLICAS (INVERSION)'),
                ('ginversion', 'GASTOS DE INVERSION'),
                ('tranf', 'TRANSF. DE INVERSION'),
                ('bienesld', 'BIENES DE LARGA DURACION (INVERSION)')
            ],
            string='Aplicacion Presupuestaria.'),
        'period_id': fields.many2one(
            'account.period',
            string='Periodo',
            required=True
            ),
        'date': fields.date(
            'Fecha de Emisión',
            required=True,
            #readonly=True,
            states={'commited': [('readonly', True)]}
            ),
        'date_confirmed': fields.date(
            'Fecha de Certificación',
            #readonly=True,
            states={'commited': [('readonly', True)]}
            ),
        'date_commited': fields.date(
            'Fecha de Compromiso',
#            readonly=True,
            states={'commited': [('readonly', True)]}
            ),
        'project_id': fields.many2one(
            'project.project',
            string='Proyecto',
            required=True,
            readonly=True,
            states=STATES_VALUE,
            domain=[('state', '=', 'exec')]
        ),
        'task_id': fields.many2one(
            'project.task',
            string='Tarea',
            readonly=True,
        ),
        'partner_id': fields.many2one(
            'res.partner', 'Proveedor',
            domain=[('supplier', '=', True)],
            readonly=False,
            states={'certified': [('readonly', False)]}),
        'line_ids': fields.one2many(
            'budget.certificate.line',
            'certificate_id',
            'Detalle'
            ),
        'amount_total': fields.function(
            _amount_total,
            string='Total Solicitado',
            method=True,
            digits_compute=DP,
            multi='request',
            store=STORE_VAR
        ),
        'amount_certified': fields.function(
            _amount_total,
            string='Total Certificado',
            method=True,
            digits_compute=DP,
            multi='request',
            store=STORE_VAR
            ),
        'amount_commited': fields.function(
            _amount_total,
            string='Total Comprometido',
            method=True,
            digits_compute=DP,
            multi='request',
            store=STORE_VAR
            ),
        }

    def _get_department(self, cr, uid, context=None):
        data = self.pool.get('res.users').read(
            cr, uid, uid,
            ['context_department_id']
            )
        if not data['context_department_id']:
            raise osv.except_osv('Error', 'El usuario no tiene departamento asignado.')
        return data['context_department_id'][0]

    def _get_period(self, cr, uid, context=None):
        data = self.pool.get('account.period').find(cr, uid)
        return data and data[0]



    def _check_requests(self, cr, uid, ids, context=None):
        """
        Validacion de montos solicitados
        {'partida': monto, 'disponible': monto}
        """
        for obj in self.browse(cr, uid, ids, context):
            if obj.project_id.type_budget == 'ingreso':
                return True
            if not obj.state == 'draft':
                return True
            lista = []
            res = []
            budget = False
            for line in obj.line_ids:
                budget_id = line.budget_line_id.id
                if budget_id != budget:
                    res = [0, line.budget_line_id.available_amount]
                    lista.append(res)
                    budget = budget_id
                res[0] += line.amount
        return True

    def _checkFechasCambia(self, cr, uid, ids):
        band = True
        for obj in self.browse(cr, uid, ids):
            if obj.name!='/':
                if obj.fiscalyear_id:
                    if obj.date_confirmed:
                        if not (obj.date_confirmed>=obj.fiscalyear_id.date_start and obj.date_confirmed<=obj.fiscalyear_id.date_stop):
                            mensaje = ustr('La fecha debe estar dentro del mismo anio fiscal en el cual tomo secuencia %s' %(obj.fiscalyear_id.name))
                            raise osv.except_osv('Error', mensaje)
                    if obj.date_commited:
                        if not (obj.date_commited>=obj.fiscalyear_id.date_start and obj.date_commited<=obj.fiscalyear_id.date_stop):
                            mensaje = ustr('La fecha debe estar dentro del mismo anio fiscal en el cual tomo secuencia %s' %(obj.fiscalyear_id.name))
                            raise osv.except_osv('Error', mensaje)
                    if obj.date:
                        if not (obj.date>=obj.fiscalyear_id.date_start and obj.date<=obj.fiscalyear_id.date_stop):
                            mensaje = ustr('La fecha debe estar dentro del mismo anio fiscal en el cual tomo secuencia %s' %(obj.fiscalyear_id.name))
                            raise osv.except_osv('Error', mensaje)
        return True

    def _checkFechas(self, cr, uid, ids):
        band = True
        for obj in self.browse(cr, uid, ids):
            if obj.date:
                for line in obj.line_ids:
                    if not (obj.date>=line.budget_id.year_id.date_start and obj.date<=line.budget_id.year_id.date_stop):
                        mensaje = ustr('La partida seleccionada %s no corresponde al mismo anio del compromiso' %(line.budget_id.code+' '+line.budget_id.name))
                        raise osv.except_osv('Error', mensaje)
            if obj.date_confirmed:
                for line in obj.line_ids:
                    if not (obj.date_confirmed>=line.budget_id.year_id.date_start and obj.date_confirmed<=line.budget_id.year_id.date_stop):
                        mensaje = ustr('La partida seleccionada %s no corresponde al mismo anio del compromiso' %(line.budget_id.code+' '+line.budget_id.name))
                        raise osv.except_osv('Error', mensaje)
            if obj.date_commited:
                for line in obj.line_ids:
                    if not (obj.date_commited>=line.budget_id.year_id.date_start and obj.date_commited<=line.budget_id.year_id.date_stop):
                        mensaje = ustr('La partida seleccionada %s no corresponde al mismo anio del compromiso' %(line.budget_id.code+' '+line.budget_id.name))
                        raise osv.except_osv('Error', mensaje)
        return band

    def _check_partner(self, cr, uid, ids):
        """
        Verifica que el documento tenga asignado un proveedor
        """
        for obj in self.browse(cr, uid, ids):
            if obj.project_id.type_budget == 'ingreso':
                return True
            if obj.state == 'commited' and not obj.partner_id:
                raise osv.except_osv('Error', 'No ha ingresado un proveedor en el documento.')
            if obj.state == 'commited' and not obj.date_commited:
                raise osv.except_osv('Error', 'No ha ingresado la fecha de compromiso.')
        return True

    def action_request(self, cr, uid, ids, context=None):
        """
        TODO:
        """
        if context is None:
            context = {}
        certificate_obj = self.pool.get('budget.certificate')
        line_obj = self.pool.get('budget.certificate.line')
        parameter_obj = self.pool.get('ir.config_parameter')
        budget_item_obj = self.pool.get('budget.item')
        year_obj = self.pool.get('account.fiscalyear')
        validbudget_ids = parameter_obj.search(cr, uid, [('key','=','validbudget')],limit=1)
        valid_budget = 'No'
        if validbudget_ids:
            valid_budget = parameter_obj.browse(cr, uid, validbudget_ids[0]).value
        for obj in self.browse(cr, uid, ids, context):
            partida = {}
            partida_repetida = {}
            aux_partida = ''
            year_ids = year_obj.search(cr, uid, [('date_start','<=',obj.date),('date_stop','>=',obj.date)],limit=1)
            if year_ids:
                year = year_obj.browse(cr, uid, year_ids[0])
            else:
                raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha de compromiso.')
            for line in obj.line_ids:
                #validar que las partidas seleccionadas correspondan al mismo anio del compromiso
                if line.budget_id.year_id.id!=year_ids[0]:
                    mensaje = ustr('La partida seleccionada %s no corresponde al mismo anio del compromiso' %(line.budget_id.code+' '+line.budget_id.name))
                    raise osv.except_osv('Error', mensaje)
                commited = 0
                if not line.budget_id.id in partida:
                    partida[line.budget_id.id] = line.amount
                else:
                    partida[line.budget_id.id] += line.amount
                    aux_partida = "PARTIDAS REPETIDAS EN EL COMPROBANTE : " + line.budget_id.name + ' - ' + line.budget_id.code
            if valid_budget=='Si' and obj.date>='2017-01-01':
                for partida_det in partida:
                    budget_item = budget_item_obj.browse(cr, uid, partida_det)
                    context = {'by_date':True,'date_start': budget_item.date_start, 'date_end': budget_item.date_end,'poa_id':budget_item.poa_id.id}
                    budget_item2 = budget_item_obj.browse(cr, uid, partida_det,context)
                    aux_diferencia = budget_item2.commited_balance - partida[partida_det]
                    if aux_diferencia<0 and abs(aux_diferencia)>0.001:
#                    if not (budget_item2.commited_balance >= partida[partida_det]):
                        mensaje = ustr('Desea comprometer %s y tiene disponible %s en la partida %s, por favor ejecute una reforma antes de realizar el compromiso.' %(partida[partida_det],budget_item2.commited_balance,budget_item2.code + ' - ' +budget_item2.name))
                        raise osv.except_osv('Error', mensaje)
            if obj.payment_id:
                cert_opago_ids = certificate_obj.search(cr, uid, [('payment_id','=',obj.payment_id.id),('id','!=',obj.id)])
                if cert_opago_ids:
                    raise osv.except_osv('Error de usuario', 'La orden de pago ya esta siendo usada en otro documento presupuestario .')
            lines = [line.id for line in obj.line_ids]
            if not lines:
                raise osv.except_osv('Alerta', 'No ha ingresado el detalle del documento.')
            line_obj.write(cr, uid, lines, {'state': 'request'})
            if obj.name=='/':
                self.set_sequence(cr, uid, ids, sequence='request')
        self.write(cr, uid, ids, {'state': 'request',
                                  'log_repetido':aux_partida,
                                  #'revisado':False,
                               #   'date': time.strftime('%Y-%m-%d %H:%M:%S')
                              })
#        self.__logger.info("Prespuesto referencial emitido")
        return True

    def action_certified(self, cr, uid, ids, context=None):
        """
        Metodo que implementa el CERTIFICAR los valores solicitados
        en las partidas presupuestarias de las actividades seleccionadas
        del proyecto.
        Cambia de estado a certified a self y a line_ids
        TODO: usar los campos actualizados por el usuario
        certified y commited
        """
        budget_item_obj = self.pool.get('budget.item')
        line_obj = self.pool.get('budget.certificate.line')
        parameter_obj = self.pool.get('ir.config_parameter')
        item_ids = []
        validbudget_ids = parameter_obj.search(cr, uid, [('key','=','validbudget')],limit=1)
        valid_budget = 'No'
        if validbudget_ids:
            valid_budget = parameter_obj.browse(cr, uid, validbudget_ids[0]).value
        for obj in self.browse(cr, uid, ids, context):
            if obj.log_repetido:
                if not obj.revisado:
                    raise osv.except_osv('Error de usuario', 'Debe confirmar que reviso el comprobante con partidas duplicados')
            line_ids = []
            for line in obj.line_ids:
                budget_item = budget_item_obj.browse(cr, uid, line.budget_id.id)
#                if valid_budget=='Si' and obj.date>='2017-01-01':
#                    if budget_item.commited_balance >= line.amount:
#                        line_obj.write(cr, uid, line.id, {'state': 'commited', 'amount_paid':line.amount})
#                        item_ids.append(line.budget_id.id)
#                    else:
#                        line_obj.write(cr, uid, line.id, {'state': 'commited', 'amount_paid':line.amount})
#                        item_ids.append(line.budget_id.id)
#                        continue
#                        mensaje = ustr('Desea certificar %s y tiene disponible %s en la partida %s, por favor ejecute una reforma antes de realizar el compromiso.' %(line.amount,budget_item.commited_balance,budget_item.code + ' - ' +budget_item.name))
#                        raise osv.except_osv('Error', mensaje)
                certified_amount = 0
                line_ids.append(line.id)
                certified_amount = line.amount
#                if certified_amount == 0:
#certified_amount = line.amount
                to_update = {
                    'state': 'certified',
                    'amount_certified': certified_amount,
                    'amount_commited':certified_amount,
                    }  # 'plan_id': plan_id[0]}
                line_obj.write(cr, uid, line.id, to_update)
            self.write(cr, uid, obj.id, {
                'state': 'certified',
                #'date_confirmed': time.strftime('%Y-%m-%d')
                })
        return True

    def action_print_report_certificate(self, cr, uid, ids, context=None):
        """
        :action to print report
        """
        if context is None:
            context = {}
        report_name = 'budget.request.cert'
        certificate = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [certificate.id], 'model': 'budget.certificate'}
        if context.get('reprint'):
            datas.update({'watermark': True})
        if context.get('certificado'):
            report_name = 'budget.certificate'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'model': 'budget.certificate',
            'datas': datas,
            'nodestroy': True,
            }

    def action_print_report(self, cr, uid, ids, context=None):
        """
        :action to print report
        """
        if context is None:
            context = {}
        report_name = 'budget.request'
        certificate = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [certificate.id], 'model': 'budget.certificate'}
        if context.get('reprint'):
            datas.update({'watermark': True})
        if context.get('compromiso'):
            report_name = 'budget.compromise'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'model': 'budget.certificate',
            'datas': datas,
            'nodestroy': True,
            }

    def action_commited(self, cr, uid, ids, context=None):
        """
        Metodo que compromete el presupuesto referencial
        valida el monto en sobregiro si esta habilitado en parametros de sistema con la variable validbudget
        """
        parameter_obj = self.pool.get('ir.config_parameter')
        validbudget_ids = parameter_obj.search(cr, uid, [('key','=','validbudget')],limit=1)
        valid_budget = 'No'
        if validbudget_ids:
            valid_budget = parameter_obj.browse(cr, uid, validbudget_ids[0]).value
        line_obj = self.pool.get('budget.certificate.line')
        item_ids = []
        item_aux = {}
        budget_item_obj = self.pool.get('budget.item')
        pay_obj = self.pool.get('payment.request')
        for obj in self.browse(cr, uid, ids, context):
            if not obj.date_commited:
                raise osv.except_osv('Error de usuario', 'Debe ingresar la fecha de compromiso.')
            for line in obj.line_ids:
                if not (obj.date_commited>=line.budget_id.year_id.date_start and obj.date_commited<=line.budget_id.year_id.date_stop):
                    raise osv.except_osv('Error de usuario','La fecha compromiso del documento presupuestario no corresponde con una o varias partidas seleccionadas')
            for line in obj.line_ids:
                commited = 0
                budget_item = budget_item_obj.browse(cr, uid, line.budget_id.id)
                line_obj.write(cr, uid, line.id, {'state': 'commited', 'amount_paid':line.amount_commited})
                item_ids.append(line.budget_id.id)
            # la validacion se dbe agrirap por cada partida y validar una solo no una por una
            if obj.date_commited:
                data = {'state': 'commited',
                        'budget_ids':[(6, 0, item_ids)],
                }
            else:
                data = {'state': 'commited',
                        'date_commited': time.strftime('%Y-%m-%d'),
                        'budget_ids':[(6, 0, item_ids)],
                }
            self.write(cr, uid, obj.id, data)
            if obj.payment_id:
                pay_obj.write(cr, uid, obj.payment_id.id,{
                    'state':'Contabilizado',
                })
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('budget.certificate.line')
        for obj in self.browse(cr, uid, ids, context):
            lines = [line.id for line in obj.line_ids]
            line_obj.write(cr, uid, lines, {'state': 'cancel'})
        self.write(cr, uid, ids, {'state': 'cancel'})
#        self.__logger.info("Presupuesto referencial anulado")
        return True

    def action_draft(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('budget.certificate.line')
        move_obj = self.pool.get('account.move')
        for obj in self.browse(cr, uid, ids, context):
            #validar que primero pase a draft el asiento relacionado
            move_ids = move_obj.search(cr, uid, [('certificate_id','=',obj.id),('state','=','posted')])
            if move_ids:
                move = move_obj.browse(cr, uid, move_ids[0])
                raise osv.except_osv('Error de usuario', 'No puede regresar a borrador por que el comprimiso esta ya devengado en el asiento %s regrese a borrador el asiento relacionado' % (move.name))
            lines = [line.id for line in obj.line_ids]
            line_obj.write(cr, uid, lines, {'state': 'draft'})
        self.write(cr, uid, ids, {'state': 'draft',
                                  'log_repetido':'',})
        return True

    def action_anular(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('budget.certificate.line')
        for obj in self.browse(cr, uid, ids, context):
            lines = [line.id for line in obj.line_ids]
            line_obj.change_state(cr, uid, lines, 'anulado')
        self.write(cr, uid, ids, {'state': 'anulado'})
        return True

    _constraints = [
        (_checkFechas, ustr('La fecha compromiso del documento presupuestario no corresponde con una o varias partidas seleccionadas'),
        ['Documento Presupuestario', 'Detalle Partidas']),
        (_checkFechasCambia, ustr('No puede cambiar las fechas fuera del anio en la que tomo la secuencia'),
        ['Documento Presupuestario', 'Detalle Partidas'])
    ]

    _defaults = {
        'active':True,
        'revisado':True,
        'tipo_aux':'gasto',
        'name': '/',
        'user_id': lambda self, cr, uid, context: uid,
        'state': 'draft',
        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'department_id': _get_department,
        'period_id': _get_period,
        'migrado':False,
        }

BudgetCertificate()

class BudgetCertificateLine(osv.Model):

    _name = 'budget.certificate.line'
    _order = 'date_commited desc,id asc'

    def create(self, cr, uid, vals, context=None):
        #si incluye el iva
        line_obj = self.pool.get('budget.certificate.line')
        if vals.has_key('agrega_iva'):
            if vals['agrega_iva']:
                aux_amount = vals['amount']*0.12
                aux_tipo = 'IvaServicios'
                if vals['tipo_invoice']=='Bien':
                    aux_tipo = 'Iva'
                if vals.has_key('financia_id'):
                    linea_extra_id = line_obj.create(cr, uid, {
                        'project_id':vals['project_id'],
                        'task_id':vals['task_id'],
                        'budget_id':vals['budget_id'],
                        'tipo_invoice':aux_tipo,
                        'amount':aux_amount,
                        'certificate_id':vals['certificate_id'],
                        'financia_id':vals['financia_id']
                    })
                else:
                    linea_extra_id = line_obj.create(cr, uid, {
                        'project_id':vals['project_id'],
                        'task_id':vals['task_id'],
                        'budget_id':vals['budget_id'],
                        'tipo_invoice':aux_tipo,
                        'amount':aux_amount,
                        'certificate_id':vals['certificate_id'],
                    })
        return super(BudgetCertificateLine, self).create(cr, uid, vals, context=None)


    def onchange_project_cert(self, cr, uid, ids, project_id, context={}):
        project_obj = self.pool.get('project.project')
        res = {}
        proyecto = project_obj.browse(cr, uid, project_id)
        task_id = proyecto.tasks[0]
        return {'value':{'task_id':task_id}}

    def onchange_budget_disp(self, cr, uid, ids, budget_id, context={}):
        item_obj = self.pool.get('budget.item')
        res = {}
        item = item_obj.browse(cr, uid, budget_id)
        context = {'by_date':True,'date_start': item.date_start, 'date_end': item.date_end,'poa_id':item.poa_id.id}
        item = item_obj.browse(cr, uid, budget_id,context=context)
        total = item.commited_balance
        return {'value':{'budget_disponible':total}}

    def _amount_totalbl(self, cr, uid, ids, fields, context, args):
        cert_obj = self.pool.get('budget.certificate.line')
        res = {}
        res1 = {}
        if len(ids) == 1:
            tuple_items = (ids[0])
            operador = "="
        else:
            operador = "in"
            tuple_items = tuple(ids)
        #validar mas dev q comp y mas pag q dev
        for id in ids:
            res1[id] = {'budget_accrued': 0.0, 'budget_paid': 0.0}
        #con esto toma todos los comprobantes esten o no contabilizados debe tomar solo contabilizados
#        sql = "SELECT account_move_line.budget_id_cert,account_move_line.id,coalesce(debit,0),coalesce(credit,0),budget_accrued,budget_paid,account_move.type  \
#        FROM account_move_line,account_move,budget_certificate_line WHERE account_move.id=account_move_line.move_id and account_move_line.migrado=False and (budget_accrued=true or budget_paid=true) and account_move_line.budget_id_cert=budget_certificate_line.id and account_move_line.budget_id_cert %s %s"%(operador,tuple_items)
        sql = "SELECT account_move_line.budget_id_cert,account_move_line.id,coalesce(debit,0),coalesce(credit,0),budget_accrued,budget_paid,account_move.type  \
        FROM account_move_line,account_move,budget_certificate_line WHERE account_move.type!='Recaudacion' and account_move.id=account_move_line.move_id and account_move_line.state='valid' and account_move_line.migrado=False and account_move_line.name!='Baja' and account_move_line.budget_certificate_id is not null and (budget_accrued=true or budget_paid=true) and account_move_line.budget_id_cert=budget_certificate_line.id and account_move_line.budget_id_cert %s %s"%(operador,tuple_items)
        cr.execute(sql)
        data = cr.fetchall()
        devengado_aux = {}
        pagado_aux = {}
        for data_line in data:
            if data_line[2] == 0:
                dato = data_line[3]
            else:
                dato = data_line[2]
            if data_line[4]==True:
                res1[data_line[0]].update({'budget_accrued': res1.get(data_line[0])['budget_accrued'] + dato,
                })
            if data_line[5]==True:
                res1[data_line[0]].update({'budget_paid': res1.get(data_line[0])['budget_paid'] + dato,
                })
        #solo si tiene budget_certificate_id en los otros casos solo es artificio
        if res1[ids[0]]['budget_paid']>res1[ids[0]]['budget_accrued']:
            cert = cert_obj.browse(cr, uid, ids[0])
#            raise osv.except_osv('Error de usuario', 'El valor del pagado no puede ser mayor devengado, en la partida %s' % (cert.budget_id.code))
        #####
        for id in ids:
            res[id] = {'budget_accrued': 0.0, 'budget_paid': 0.0}
        sql = "SELECT account_move_line.budget_id_cert,account_move_line.id,coalesce(debit,0),coalesce(credit,0),budget_accrued,budget_paid,account_move.type  \
        FROM account_move_line,account_move,budget_certificate_line WHERE account_move.id=account_move_line.move_id and account_move.state='posted' and account_move_line.migrado=False and account_move_line.state='valid' and (budget_accrued=true or budget_paid=true) and account_move_line.budget_id_cert=budget_certificate_line.id and account_move_line.budget_id_cert %s %s"%(operador,tuple_items)
        cr.execute(sql)
        data = cr.fetchall()
        devengado_aux = {}
        pagado_aux = {}
        for data_line in data:
            if data_line[2] == 0:
                dato = data_line[3]
            else:
                dato = data_line[2]
            if data_line[4]==True:
                res[data_line[0]].update({'budget_accrued': res.get(data_line[0])['budget_accrued'] + dato,
                })
            if data_line[5]==True:
                res[data_line[0]].update({'budget_paid': res.get(data_line[0])['budget_paid'] + dato,
                })
        return res

    def name_search(self, cr, uid, name='', args=None,
                    operator='ilike', context=None, limit=80):
        """
        Redefinición de método para permitir buscar por el código
        """
        ids = []
        ids = self.search(cr, uid, [
            '|', ('code', operator, name),
            ('name', operator, name)] + args,
            context=context,
            limit=limit
            )
        return self.name_get(cr, uid, ids, context)


    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name_aux = record.budget_id.code
            aux_num_partida = record.budget_id.name
            aux_anio = record.budget_id.year_id.name
            aux = name_aux + ' - ' + aux_num_partida
            if record.tipo_invoice:
                aux = name_aux + ' - ' + aux_num_partida + ' - ' + record.tipo_invoice + ' - ' + str(record.amount_commited) + ' - '  + aux_anio
            else:
                aux = name_aux + ' - ' + aux_num_partida + ' - ' + str(record.amount_commited) + ' - '  + aux_anio
            res.append((record.id, aux))
        return res

    def _amount_disponible(self, cr, uid, ids, fields, context, args):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
#            total = obj.budget_id.commited_balance
#            res[obj.id] = total
            res[obj.id] = 0
        return res

    def _budget_aux(self, cr, uid, ids, fields, context, args):
        res = {}
        post_obj = self.pool.get('budget.post')
        for obj in self.browse(cr, uid, ids, context):
            aux_code = obj.budget_id.budget_post_id.code[0:6]
            post_ids = post_obj.search(cr, uid, [('code','=',aux_code)],limit=1)
            if post_ids:
                res[obj.id] = post_ids[0]
            else:
                res[obj.id] = obj.budget_id.budget_post_id.id
        return res

    def _compute_program(self, cr, uid, ids, fields, context, args):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = obj.budget_id.program_id.id
        return res

    _columns = {
        'financia_id':fields.many2one('budget.financiamiento','Cuenta Financiera'),
        'active':fields.boolean('Activo'),
        'agrega_iva':fields.boolean('Agrega Iva',help="Si marca este campo el sistema automaticamente agregara el valor del iva"),
        'tipo_invoice':fields.selection([('Bien','Bien'),('Servicio','Servicio'),('Iva','Iva Bienes'),('IvaServicios','Iva Servicios'),
                                         ('Iess','Iess'),('Terceros','Terceros'),('Viatico','Viatico'),('SRI','SRI')],'Tipo'),
        'budget_id_aux':fields.function(_budget_aux, method=True,type='many2one',relation='budget.post',string='Partida Mayor',
                                        store=True),
        'migrado':fields.boolean('Migrado'),
        'name':fields.related('budget_id', 'name', type='char',
                              size=128, string='Partida',
                              readonly=True,store=True),
        'name_aux':fields.related('certificate_id', 'name', type='char',
                              size=128, string='Documento',
                              readonly=True,store=True),
        'certificate_id': fields.many2one(
            'budget.certificate',
            string='Certificado',
            ondelete='cascade'
        ),
        'program_id': fields.function(
            _compute_program,
            string='Programa',
            type='many2one',relation='project.program', store=True,
        ),
        'project_id': fields.many2one(
            'project.project',
            string='Proyecto',
            required=True
        ),
        'task_id': fields.many2one(
            'project.task',
            string='Actividad',
            required=True
        ),
        'budget_post': fields.related(
            'budget_id','budget_post_id',
            type="many2one",
            relation='budget.post',
            string='Partida Catalogo',
            store=True
        ),
        'code':fields.related('budget_id', 'code', type='char',
                                  size=128, string='Codigo',
                                  readonly=True,store=True),
        'budget_id': fields.many2one(
            'budget.item',
            string='Partida',
            required=True
        ),
        'amount': fields.float('Monto Solicitado',
                               digits_compute=DP),
        'amount_certified': fields.float('Monto Certificado',
                                         digits_compute=DP),
        'amount_commited': fields.float('Monto Comprometido',
                                        digits_compute=DP),
        'amount_paid':fields.float('Monto Pagado',digits_compute=DP),
        'state':fields.related('certificate_id', 'state', type='char',
                              size=128, string='Estado',
                              readonly=True,store=True),
        'period_id':fields.related('certificate_id','period_id',type='many2one',relation='account.period',store=True ,string='Periodo Compromiso'),
        'partner_id':fields.related('certificate_id','partner_id',type='many2one',relation='res.partner',store=True ,string='Proveedor'),
        'date_commited':fields.related('certificate_id','date_commited',type='date',relation='budget.certificate',store=True ,string='Fecha'),
        'budget_disponible': fields.function(
            _amount_disponible, method=True,
            string='Saldo Por Comprometer',
            digits_compute=DP, store=False),
        'budget_accrued': fields.function(
            _amount_totalbl, multi='budgetline', method=True,
            string='Devengado',
            digits_compute=DP, store=False),
        'budget_paid': fields.function(
            _amount_totalbl, multi='budgetline', method=True,
           string='Pagado',
            digits_compute=DP, store=False),
    }

    def _check_rule(self, cr, uid, ids):
        return True

    def _check_amount(self, cr, uid, ids):
        return True

    _defaults = dict(
        active = True,
    )

    _constraints = [
        (_check_amount,'El monto solicitado debe ser mayor a cero',['Monto solicitado']),
        (_check_rule,'El monto pagado no debe ser mayor al devengado, y el devangado no mayor al comprometido',['Monto solicitado'])
        ]

BudgetCertificateLine()

class BudgetRoof(osv.Model):
    _name = 'budget.roof'
    _description = 'Techos Presupuestarios'

    def _amount_total(self, cr, uid, ids, fields, context, args):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            total = 0
            total = sum([line.limit_amount for line in obj.detail_ids])
            res[obj.id] = total
        return res

    STATES_VALUE = {'draft': [('readonly', False)]}

    _columns = {
        'fy_id': fields.many2one(
            'account.fiscalyear',
            string='Ejercicio Fiscal',
            required=True
            ),
        'date': fields.date('Fecha de Aprobación', readonly=True),
        'state': fields.selection([('draft', 'Borrador'),
                                  ('validate', 'Aprobado')],
                                  string="Estado", readonly=True),
        'amount_total': fields.function(
            _amount_total, method=True,
            string='Presupuesto Total',
            digits_compute=DP, store=True),
        'detail_ids': fields.one2many(
            'budget.roof.line', 'roof_id',
            'Detalle de Techo Presupuestario',
            readonly=True, states=STATES_VALUE),
        }

    _defaults = {
        'state': 'draft',
        }

    def action_validate(self, cr, uid, ids, context=None):
        """
        Metodo de validacion de limites presupuestarios
        """
        line_obj = self.pool.get('budget.roof.line')
        for obj in self.browse(cr, uid, ids, context):
            lines = [l.id for l in obj.detail_ids]
            line_obj.write(cr, uid, lines, {'state': 'validate'})
            self.write(cr, uid, [obj.id], {'state': 'validate'})
        return True


class BudgetRoofLine(osv.Model):
    _name = 'budget.roof.line'
    _description = "Limites presupuestarios por departamento"
    DP = dp.get_precision('Account')

    def name_search(self, cr, uid, name, args=None,
                    operator='ilike', context=None, limit=100):
        dept_obj = self.pool.get('hr.department')
        res = dept_obj.search(cr, uid, [('name', operator, name)])
        ids = self.search(cr, uid, [('department_id', 'in', res)])
        return self.name_get(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context):
        res = []
        for obj in self.browse(cr, uid, ids, context):
            text = '%s: %.2f' % (obj.department_id.name, obj.limit_amount)
            res.append((obj.id, text))
        return res

    def _amount_total(self, cr, uid, ids, fields, context, args):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            total = 0
            total = sum([line.amount for line in obj.roof_line])
            res[obj.id] = total
        return res

    _columns = {
        'roof_id': fields.many2one(
            'budget.roof',
            string='Techo Presupuestario'
        ),
        'department_id': fields.many2one(
            'hr.department',
            string='Dirección Coordinación',
            required=True
        ),
        'limit_amount': fields.float('Límite'),
        'fy_id': fields.related(
            'roof_id',
            'fy_id',
            relation='account.fiscalyear',
            store=True,
            string='Ejercicio Fiscal'
            ),
        'state': fields.selection(
            [('draft', 'Borrador'),
             ('validate', 'Aprobado')],
            string="Estado",
            readonly=True
        ),
    }

    def get_limit(self, cr, uid, dept_id, fy_id):
        """
        Consulta el limite entre fechas de un
        departamento.
        """
        ids = self.search(
            cr,
            uid,
            [
                ('department_id', '=', dept_id),
                ('fy_id', '=', fy_id)
            ]
        )
        data = self.read(cr, uid, ids, ['limit_amount'])
        ides, datas = ids and ids[0] or False, data and data[0]['limit_amount'] or False
        return ides, datas


class AccountAccount(osv.Model):
    _inherit = 'account.account'

    _columns = {
        'budget_id': fields.many2one(
            'budget.post',
            string='Partida Debe',
            domain=[('internal_type', '!=', 'view')]
            ),
        'budget_haber_id': fields.many2one(
            'budget.post',
            string='Partida Haber',
            domain=[('internal_type', '!=', 'view')]
            ),
        'account_rec_id': fields.many2one(
            'account.account',
            string='Cuenta de Cobro'
            ),
        'account_pay_id': fields.many2one(
            'account.account',
            string='Cuenta de Pago'
            ),
        'esigef': fields.boolean(string='Exportar a archivo ESIGEF?'),
        'sufijo_esigef': fields.char('Sufijo ESIGEF?',size=2),
        }
