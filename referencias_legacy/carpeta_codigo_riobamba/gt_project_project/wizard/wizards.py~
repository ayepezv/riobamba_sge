# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

__author__ = 'Mario Chogllo'
from gt_tool import XLSWriter
import csv
import base64
import StringIO
import time
import logging
import netsvc
from lxml import etree
import xlrd
from tools import ustr
from osv import osv, fields
from datetime import datetime

class proformaPrespuestariaIngreso(osv.TransientModel):
    _name = 'proforma.presupuestaria.ingreso'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
    )

    def print_report_proforma_ingreso(self, cr, uid, ids, context):
        if context is None:
            context = {}     
        poa_obj = self.pool.get('budget.poa')
        reporte = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [reporte.id], 'model': 'proforma.presupuestaria.ingreso'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'proforma_presupuestaria_ingreso',
            'model': 'proforma.presupuestaria.ingreso',
            'datas': datas,
            'nodestroy': True,                              
            }

proformaPrespuestariaIngreso()


class proformaPrespuestariaIngresoResumen(osv.TransientModel):
    _name = 'proforma.presupuestaria.ingreso.resumen'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
    )

    def print_report_proforma_ingreso_resumen(self, cr, uid, ids, context):
        if context is None:
            context = {}     
        poa_obj = self.pool.get('budget.poa')
        reporte = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [reporte.id], 'model': 'proforma.presupuestaria.ingreso.resumen'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'proforma_presupuestaria_ingreso_resumen',
            'model': 'proforma.presupuestaria.ingreso.resumen',
            'datas': datas,
            'nodestroy': True,                              
            }

proformaPrespuestariaIngresoResumen()

class proformaPrespuestariaGasto(osv.TransientModel):
    _name = 'proforma.presupuestaria.gasto'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
    )

    def print_report_proforma_gasto(self, cr, uid, ids, context):
        if context is None:
            context = {}     
        poa_obj = self.pool.get('budget.poa')
        reporte = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [reporte.id], 'model': 'proforma.presupuestaria.gasto'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'proforma_presupuestaria_gasto',
            'model': 'proforma.presupuestaria.gasto',
            'datas': datas,
            'nodestroy': True,                              
            }

proformaPrespuestariaGasto()

class proformaPrespuestariaGastoResumen(osv.TransientModel):
    _name = 'proforma.presupuestaria.gasto.resumen'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
    )

    def print_report_proforma_gasto_resumen(self, cr, uid, ids, context):
        if context is None:
            context = {}     
        poa_obj = self.pool.get('budget.poa')
        reporte = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [reporte.id], 'model': 'proforma.presupuestaria.gasto.resumen'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'proforma_presupuestaria_gasto_resumen',
            'model': 'proforma.presupuestaria.gasto.resumen',
            'datas': datas,
            'nodestroy': True,                              
            }

proformaPrespuestariaGastoResumen()

class budgetSobregiroLine(osv.TransientModel):
    _name = 'budget.sobregiro.line'
    _order = 'code asc'
    _columns = dict(
        code = fields.char('Codigo',size=64),
        name = fields.char('Descripcion',size=256),
        s_id = fields.many2one('budget.sobregiro','Sobregiro'),
        budget_id = fields.many2one('budget.item','Partida'),
        planned_amount = fields.float('Asignacion Inicial'),
        reform_amount = fields.float('Reforma'),
        codificado_amount = fields.float('Codificado'),
        commited_amount = fields.float('Comprometido'),
        sobregiro_commited = fields.float('Sobregiro Comprometido'),
        devengado_amount = fields.float('Devengado'),
        sobregiro_devengado = fields.float('Sobregiro Devengado'),
    )
budgetSobregiroLine()

class budgetSobregiro(osv.TransientModel):
    _name = 'budget.sobregiro'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        date_to = fields.date('Fecha Hasta'),
        line_ids = fields.one2many('budget.sobregiro.line','s_id','Detalle'),
    )

    def printSobregiro(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        reporte = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [reporte.id], 'model': 'budget.sobregiro'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sobregiro',
            'model': 'budget.sobregiro',
            'datas': datas,
            'nodestroy': True,                        
            }

    def computeSobregiro(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('budget.sobregiro.line')
        item_obj = self.pool.get('budget.item')
        context = {}
        for this in self.browse(cr, uid, ids):
            line_antes = line_obj.search(cr, uid, [('s_id','=',this.id)])
            if line_antes:
                line_obj.unlink(cr, uid, line_antes)
            context = {'by_date':True,'date_start':this.poa_id.date_start, 'date_end': this.date_to,'poa_id':this.poa_id.id}            
            item_ids = item_obj.search(cr, uid, [('poa_id','=',this.poa_id.id),('type_budget','=','gasto')])
            if item_ids:
                for line in item_obj.browse(cr,uid,item_ids, context=context):
                    if (line.commited_amount-line.devengado_amount<-0.01): 
                        line_id = line_obj.create(cr, uid, {
                            's_id':this.id,
                            'code':line.code,
                            'name':line.name,
                            'planned_amount':line.planned_amount,
                            'reform_amount':line.reform_amount,
                            'codificado_amount':line.codif_amount,
                            'commited_amount':line.commited_amount,
                            'devengado_amount':line.devengado_amount,
                            'sobregiro_devengado':line.commited_amount-line.devengado_amount,
                        })
                        if (line.codif_amount-line.commited_amount<-0.01):
                            line_obj.write(cr, uid, line_id,{
                                'sobregiro_commited':line.codif_amount-line.commited_amount,
                            })
                    elif (line.codif_amount-line.commited_amount<-0.01):
                        line_id = line_obj.create(cr, uid, {
                            's_id':this.id,
                            'code':line.code,
                            'name':line.name,
                            'planned_amount':line.planned_amount,
                            'reform_amount':line.reform_amount,
                            'codificado_amount':line.codif_amount,
                            'commited_amount':line.commited_amount,
                            'devengado_amount':line.devengado_amount,
                            'sobregiro_commited':line.codif_amount-line.commited_amount,
                        })
        return True

budgetSobregiro()

class esigefDetalleLine(osv.TransientModel):
    _name = 'esigef.detalle.line'
    _order = 'code asc'
    _columns = dict(
        d_id = fields.many2one('esigef.detalle','Detalle'),
        d_id2 = fields.many2one('esigef.detalle','Detalle'),
        code = fields.char('Codigo',size=8),
        post_id = fields.many2one('budget.post','Partida'),
        inicial = fields.float('Inicial'),
        reforma = fields.float('Reforma'),
        codificado = fields.float('Codificado'),
        comprometido = fields.float('Comprometido'),
        devengado = fields.float('Devengado'),
        ejecutado = fields.float('Ejecutado'),
        r4 = fields.selection([('OK','OK'),('NA','No Aplica'),('Error','Error')],'R4'),
        r6 = fields.selection([('OK','OK'),('NA','No Aplica'),('Error','Error')],'R6'),
        r7 = fields.selection([('OK','OK'),('NA','No Aplica'),('Error','Error')],'R7'),
        r8 = fields.selection([('OK','OK'),('NA','No Aplica'),('Error','Error')],'R8'),
    )
esigefDetalleLine()
class esigefDetalle(osv.TransientModel):
    _name = 'esigef.detalle'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        date_start = fields.date('Fecha Desde'),
        date_stop = fields.date('Fecha Hasta'),
        line_ids = fields.one2many('esigef.detalle.line','d_id','Detalle Ingresos'),
        line_ids2 = fields.one2many('esigef.detalle.line','d_id2','Detalle Gastos'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def printEsigef(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        detallee = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [detallee.id], 'model': 'esigef.detalle'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'esigef_detalle',
            'model': 'esigef.detalle',
            'datas': datas,
            'nodestroy': True,                        
            }        

    def printEsigefIngreso(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        detallee = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [detallee.id], 'model': 'esigef.detalle'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'esigef_detalle_in',
            'model': 'esigef.detalle',
            'datas': datas,
            'nodestroy': True,                        
            }        

    def printEsigefGasto(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        detallee = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [detallee.id], 'model': 'esigef.detalle'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'esigef_detalle_gas',
            'model': 'esigef.detalle',
            'datas': datas,
            'nodestroy': True,                        
            }        

    def computeEsigef(self, cr, uid, ids, context=None):
        post_obj = self.pool.get('budget.post')
        item_obj = self.pool.get('budget.item')
        line_obj = self.pool.get('esigef.detalle.line')
        res_line = {}
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['Esigef Detalle'])
            writer.append(['DESDE',this.date_start,'HASTA',this.date_stop])
            writer.append(['CODIGO','DENOMINACION','INICIAL','REFORMAS','CODIFICADO','COMPROMETIDO','DEVENGADO','EJECUTADO','R4','R6','R7','R8'])
            line_antes_i = line_obj.search(cr, uid, [('d_id','=',this.id)])
            if line_antes_i:
                line_obj.unlink(cr, uid, line_antes_i)
            line_antes_g = line_obj.search(cr, uid, [('d_id','=',this.id)])
            if line_antes_g:
                line_obj.unlink(cr, uid, line_antes_g)
            context = {'by_date':True,'date_start': this.date_start, 'date_end': this.date_stop,'poa_id':this.poa_id.id}            
            #ingresos nivel 5
            item_ids = item_obj.search(cr, uid, [('poa_id','=',this.poa_id.id),('type_budget','=','ingreso')])
            for line in item_obj.browse(cr, uid, item_ids,context=context):
                code = line.budget_post_id.code.replace('.','')[0:6]
                if res_line.has_key(code)==False:
                    res_line[code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': True,#False, 
                        'code':code,
                        'code_aux':code,#line.code
                        'code_report':line.code_report,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'commited_amount':line.commited_amount,
                        'devengado_amount':line.devengado_amount,
                        'paid_amount':line.paid_amount,
                        'devengado_balance':line.devengado_balance,
                        'commited_balance':line.commited_balance,
                        'codif_amount':line.codif_amount,
                        'reform_amount':line.reform_amount,
                        'final': True,#False,
                        'nivel': line.budget_post_id.nivel,
                    }
                else:
                    res_line[code]['planned_amount']+=line.planned_amount
                    res_line[code]['reform_amount']+=line.reform_amount
                    res_line[code]['codif_amount']+=line.codif_amount
                    res_line[code]['commited_amount']+=line.commited_amount
                    res_line[code]['devengado_amount']+=line.devengado_amount
                    res_line[code]['paid_amount']+=line.paid_amount
                    res_line[code]['commited_balance']+=line.commited_balance
                    res_line[code]['devengado_balance']+=line.devengado_balance
            writer.append(['INGRESOS'])
            for line in res_line:
                post_ids = post_obj.search(cr, uid, [('code','=',line)])
                aux_r4 = aux_r6 = aux_r8 = 'OK'
                if (res_line[line]['paid_amount']-res_line[line]['devengado_amount'])>0.01:
                    aux_r4 = 'Error'
                if (res_line[line]['commited_amount']-res_line[line]['codif_amount'])>0.01:
                    aux_r6 = 'Error'
                if (res_line[line]['paid_amount']-res_line[line]['devengado_amount'])>0.01:
                    aux_r8 = 'Error'
                line_obj.create(cr, uid, {
                    'code':line,
                    'd_id':this.id,
                    'post_id':post_ids[0],
                    'inicial':res_line[line]['planned_amount'],
                    'reforma':res_line[line]['reform_amount'],
                    'codificado':res_line[line]['codif_amount'],
                    'comprometido':res_line[line]['commited_amount'],
                    'devengado':res_line[line]['devengado_amount'],
                    'ejecutado':res_line[line]['paid_amount'],
                    'r4':aux_r4,
                    'r6':aux_r6,
                    'r7':'NA',
                    'r8':aux_r8,
                })
            for line in this.line_ids:
                writer.append([line.code,line.post_id.name,line.inicial,line.reforma,line.codificado,line.comprometido,line.devengado,line.ejecutado,line.r4,line.r6,'NA',line.r8])
            #gastos nivel 5
            res_line_g = {}
            item_ids = item_obj.search(cr, uid, [('poa_id','=',this.poa_id.id),('type_budget','=','gasto')])
            for line in item_obj.browse(cr, uid, item_ids,context=context):
                code = line.budget_post_id.code.replace('.','')[0:6]
                if res_line_g.has_key(code)==False:
                    res_line_g[code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': True,#False, 
                        'code':code,
                        'code_aux':code,#line.code
                        'code_report':line.code_report,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'commited_amount':line.commited_amount,
                        'devengado_amount':line.devengado_amount,
                        'paid_amount':line.paid_amount,
                        'devengado_balance':line.devengado_balance,
                        'commited_balance':line.commited_balance,
                        'codif_amount':line.codif_amount,
                        'reform_amount':line.reform_amount,
                        'final': True,#False,
                        'nivel': line.budget_post_id.nivel,
                    }
                else:
                    res_line_g[code]['planned_amount']+=line.planned_amount
                    res_line_g[code]['reform_amount']+=line.reform_amount
                    res_line_g[code]['codif_amount']+=line.codif_amount
                    res_line_g[code]['commited_amount']+=line.commited_amount
                    res_line_g[code]['devengado_amount']+=line.devengado_amount
                    res_line_g[code]['paid_amount']+=line.paid_amount
                    res_line_g[code]['commited_balance']+=line.commited_balance
                    res_line_g[code]['devengado_balance']+=line.devengado_balance
            writer.append(['GASTOS'])
            for line in res_line_g:
                post_ids = post_obj.search(cr, uid, [('code','=',line)])
                aux_r4 = aux_r6 = aux_r7 = aux_r8 = 'OK'
                if (res_line_g[line]['paid_amount']-res_line_g[line]['devengado_amount'])>0.01:
                    aux_r4 = 'OK'#'Error'
                if (res_line_g[line]['commited_amount']-res_line_g[line]['codif_amount'])>0.01:
                    aux_r6 = 'Error'
                if (res_line_g[line]['devengado_amount']-res_line_g[line]['commited_amount'])>0.01:
                    aux_r7 = 'Error'
                if (res_line_g[line]['paid_amount']-res_line_g[line]['devengado_amount'])>0.01:
                    aux_r8 = 'Error'
                line_obj.create(cr, uid, {
                    'code':line,
                    'd_id2':this.id,
                    'post_id':post_ids[0],
                    'inicial':res_line_g[line]['planned_amount'],
                    'reforma':res_line_g[line]['reform_amount'],
                    'codificado':res_line_g[line]['codif_amount'],
                    'comprometido':res_line_g[line]['commited_amount'],
                    'devengado':res_line_g[line]['devengado_amount'],
                    'ejecutado':res_line_g[line]['paid_amount'],
                    'r4':aux_r4,
                    'r6':aux_r6,
                    'r7':aux_r7,
                    'r8':aux_r8,
                })
            for line in this.line_ids2:
                writer.append([line.code,line.post_id.name,line.inicial,line.reforma,line.codificado,line.comprometido,line.devengado,line.ejecutado,line.r4,line.r6,line.r7,line.r8])
        writer.save("EsigefDetalle.xls")
        out = open("EsigefDetalle.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'EsigefDetalle.xls'})
        return True
esigefDetalle()
##recaudacion eefectiva
class efectivaLine(osv.TransientModel):
    _name = 'efectiva.line'
    _columns = dict(
        f_id = fields.many2one('recaudacion.efectiva','Recaudacion'),
        budget_id = fields.many2one('budget.item','Partida'),
        budget_post = fields.many2one('budget.post','Partida Catalogo'),
        anio1 = fields.float('Anio 1'),
        anio2 = fields.float('Anio 2'),
        anio3 = fields.float('Anio 3'),
        promedio = fields.float('Promedio'),
        actual = fields.float('Actual'),
    )
efectivaLine()
class recaudacionEfectiva(osv.TransientModel):
    _name = 'recaudacion.efectiva'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto Actual'),
        poa_ids = fields.many2many('budget.poa','rec_p_id','rec_id','p_id','Presupuesto Anterior'),
        line_ids = fields.one2many('efectiva.line','f_id','Detalle Recaudacion'),
    )

    def generaEfectiva(self, cr, uid, ids, context=None):
        poa_obj = self.pool.get('budget.poa')
        item_obj = self.pool.get('budget.item')
        post_obj = self.pool.get('budget.post')
        line_obj = self.pool.get('efectiva.line')
        aux_poa_ids = []
        result = {}
        for this in self.browse(cr, uid, ids):
            lines_antes = line_obj.search(cr, uid, [('f_id','=',this.id)])
            if lines_antes:
                line_obj.unlink(cr, uid, lines_antes)
            aux_ingreso= "'" + 'ingreso' + "'"
            poa_actual = this.poa_id.id
            poaactual = this.poa_id
            context = {'by_date':True,'date_start': poaactual.date_start, 'date_end': poaactual.date_end,'poa_id':poa_actual}
            aux = '''select budget_post_id from budget_item where poa_id=%s and type_budget=%s group by budget_post_id order by budget_post_id''' % (poa_actual,aux_ingreso)
            cr.execute(aux)
            for row in cr.fetchall():
                item_ids = item_obj.search(cr, uid, [('budget_post_id','=',row[0]),('poa_id','=',poa_actual)])
                if item_ids:
                    item = item_obj.browse(cr, uid, item_ids[0],context)
                    result[item.budget_post_id.code] = [0,0,0,0]
                    recaudado = item.paid_amount
                    result[item.budget_post_id.code][0] = recaudado
                    result[item.budget_post_id.code][1]=0
                    result[item.budget_post_id.code][2]=0
                    result[item.budget_post_id.code][3]=0
            #cada anio a comparar
            aux_pos = 0
            for poa_id in this.poa_ids:
                aux_pos += 1
                context = {'by_date':True,'date_start': poa_id.date_start, 'date_end': poa_id.date_end,'poa_id':poa_id.id}
                aux = '''select budget_post_id from budget_item where poa_id=%s and type_budget=%s group by budget_post_id order by budget_post_id''' % (poa_id.id,aux_ingreso)
                cr.execute(aux)
                for row in cr.fetchall():
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',row[0]),('poa_id','=',poa_id.id)])
                    if item_ids:
                        item = item_obj.browse(cr, uid, item_ids[0],context)
                        recaudado = item.paid_amount
                        if item.budget_post_id.code in result:
                            result[item.budget_post_id.code][aux_pos]=recaudado
                        else:
                            result[item.budget_post_id.code] = [0,0,0,0]
                            result[item.budget_post_id.code][aux_pos]=recaudado
            for line in result:
                post_ids = post_obj.search(cr, uid, [('code','=',line)])
                if post_ids:
                    aux_suma = aux_promedio = aux_divide = 0
                    if result[line][0]>0:
                        aux_suma += result[line][0]
                        aux_divide += 1
                    if result[line][1]>0:
                        aux_suma += result[line][1]
                        aux_divide += 1
                    if result[line][2]>0:
                        aux_suma += result[line][2]
                        aux_divide += 1
                    if result[line][3]>0:
                        aux_suma += result[line][3]
                        aux_divide += 1
                    if aux_divide>0:
                        aux_promedio = aux_suma / aux_divide
                    line_obj.create(cr, uid, {
                        'f_id':this.id,
                        'budget_post':post_ids[0],
                        'anio1':result[line][1],
                        'anio2':result[line][2],
                        'anio3':result[line][3],
                        'actual':result[line][0],
                        'promedio':aux_promedio,
                    })
        return True
    
    def generaEfectiva2(self, cr, uid, ids, context=None):
        poa_obj = self.pool.get('budget.poa')
        item_obj = self.pool.get('budget.item')
        line_obj = self.pool.get('efectiva.line')
        aux_poa_ids = []
        for this in self.browse(cr, uid, ids):
            lines_antes = line_obj.search(cr, uid, [('f_id','=',this.id)])
            if lines_antes:
                line_obj.unlink(cr, uid, lines_antes)
            aux_ingreso= "'" + 'ingreso' + "'"
            poa_1 = this.poa_ids[0].id
#            poa_2 = this.poa_ids[1]
#            poa_3 = this.poa_ids[2]
            poa_actual = this.poa_id.id
            poa1 = poa_obj.browse(cr, uid, poa_1)
#            poa2 = poa_obj.browse(cr, uid, poa_2)
#            poa3 = poa_obj.browse(cr, uid, poa_3)
            poaactual = this.poa_id
            context1 = {'by_date':True,'date_start': poa1.date_start, 'date_end': poa1.date_end,'poa_id':poa_1}
#            context2 = {'by_date':True,'date_start': poa2.date_start, 'date_end': poa2.date_end,'poa_id':poa_2}
#            context3 = {'by_date':True,'date_start': poa3.date_start, 'date_end': poa3.date_end,'poa_id':poa_3}
            context = {'by_date':True,'date_start': poaactual.date_start, 'date_end': poaactual.date_end,'poa_id':poa_actual}
            aux_poa_ids = [this.poa_ids[0].id]
            aux_poa_ids.append(this.poa_id.id)
            aux = '''select budget_post_id from budget_item where poa_id in %s and type_budget=%s group by budget_post_id order by budget_post_id''' % (tuple(aux_poa_ids),aux_ingreso)
            cr.execute(aux)
            for row in cr.fetchall():
                promedio = 0
                item1_ids = item_obj.search(cr, uid, [('budget_post_id','=',row[0]),('poa_id','=',poa_1)])
                recaudado1 = recaudado = 0
                if item1_ids:
                    item1 = item_obj.browse(cr, uid,item1_ids[0],context1)
                    recaudado1 = item1.paid_amount
#                item2 = item_obj.browse(cr, uid, [('budget_post_id','=',row[0]),('poa_id','=',poa_2)],context2)
#                item3 = item_obj.browse(cr, uid, [('budget_post_id','=',row[0]),('poa_id','=',poa_3)],context3)
                item_ids = item_obj.search(cr, uid, [('budget_post_id','=',row[0]),('poa_id','=',poa_actual)])
                if item_ids:
                    item = item_obj.browse(cr, uid, item_ids[0],context)
                    recaudado = item.paid_amount
#                recaudado2 = item2.budget_paid
#                recaudado3 = item3.budget_paid
                promedio = (recaudado1 + recaudado1 + recaudado1)/3.00
                line_obj.create(cr, uid, {
                    'f_id':this.id,
                    'budget_post':row[0],
                    'anio1':recaudado1,
                    'anio2':recaudado1,
                    'anio3':recaudado1,
                    'actual':recaudado,
                    'promedio':promedio,
                })
        return True

    def printEfectiva(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = []
        self.generaEfectiva(cr, uid, ids)
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'efectiva',
            'model': 'recaudacion.efectiva',
            'datas': datas,
            'nodestroy': True,                        
            }            

recaudacionEfectiva()
##distributivo
class distributivoContrato(osv.Model):
    _name = 'distributivo.contrato'
    _columns = dict(
        c_id = fields.many2one('distributivo.departamento','Departamento'),
        contract_id = fields.many2one('hr.contract','Contrato'),
        wage = fields.float('Sueldo'),
    )
distributivoContrato()
class distributivoDepartamento(osv.Model):
    _name = 'distributivo.departamento'
    _columns = dict(
        p_id = fields.many2one('distributivo.programa','Programa'),
        department_id = fields.many2one('hr.department','Departamento'),
        line_ids = fields.one2many('distributivo.contrato','c_id','Contratos'),
        total = fields.float('Total'),
    )
distributivoDepartamento()
class distributivoPrograma(osv.Model):
    _name = 'distributivo.programa'
    _columns = dict(
        d_id = fields.many2one('distributivo.budget.tthh','Distributivo'),
        program_id = fields.many2one('project.program','Programa'),
        total = fields.float('Total'),
        line_ids = fields.one2many('distributivo.departamento','p_id','Detalle Departamento'),
    )
distributivoPrograma()
class distributivoBudgetTthh(osv.Model):
    _name = 'distributivo.budget.tthh'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','POA'),
        name = fields.many2one('project.program','Programa'),
        line_ids = fields.one2many('distributivo.programa','d_id','Detalle Programa'),
    )

    def creaBudgetDistributivo(self, cr, uid, ids, context=None):
        return True
        project_obj = self.pool.get('project.project')
        for this in self.browse(cr, uid, ids):
            for line_programa in this.line_ids:
                project_id = project_obj.create(cr, uid, )
                for line_departamento in line_programa.line_ids:
                    for line_contrato in line_departamento.line_ids:
                        print "CREA PROYECTO"
        return True    

    def generaDistributivo(self, cr, uid, ids, context=None):
        program_obj = self.pool.get('project.program')
        department_obj = self.pool.get('hr.department')
        contract_obj = self.pool.get('hr.contract')
        dprograma_obj = self.pool.get('distributivo.programa')
        ddepartment_obj = self.pool.get('distributivo.departamento')
        dcontract_obj = self.pool.get('distributivo.contrato')
        for this in self.browse(cr, uid, ids):
            program_ids = program_obj.search(cr, uid, [('sequence','in',('1.8','1.1'))])
#            program_ids = program_obj.search(cr, uid, [('sequence','=','1.8')])
#            program_ids = program_obj.search(cr, uid, [])
            if program_ids:
                for program_id in program_ids:
                    total = 0
                    departamentos = {}
                    contract_ids = contract_obj.search(cr, uid, [('activo','=',True),('program_id','=',program_id)])
                    if contract_ids:
                        id_programa = dprograma_obj.create(cr, uid, {
                            'd_id':this.id,
                            'program_id':program_id,
                        })
                        for contract_id in contract_ids:
                            contrato = contract_obj.browse(cr, uid, contract_id)
                            if not contrato.employee_id.department_id.id in departamentos:
                                departamentos[contrato.employee_id.department_id.id]=[]
                                departamentos[contrato.employee_id.department_id.id].append(contract_id)
                            else:
                                departamentos[contrato.employee_id.department_id.id].append(contract_id)
                    for departamento in departamentos:
                        id_departamento = ddepartment_obj.create(cr, uid, {
                            'p_id':id_programa,
                            'department_id':departamento,
                        })
                        for contract_id in departamentos[departamento]:
                            contrato = contract_obj.browse(cr, uid, contract_id)
                            total += contrato.wage
                            dcontract_obj.create(cr, uid, {
                                'contract_id':contract_id,
                                'wage':contrato.wage,
                                'c_id':id_departamento,
                            })
                    dprograma_obj.write(cr, uid, id_programa,{'total':total})
        return True

    def printDistributivo(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = []
#        self.generaDistributivo(cr, uid, ids)
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'distributivo',
            'model': 'distributivo.budget',
            'datas': datas,
            'nodestroy': True,                        
            }            

distributivoBudgetTthh()

##fondo ajenos
class ajenoBudgetLine(osv.Model):
    _name = 'ajeno.budget.line'

    def _amount_budget_ajeno(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'total': 0.0,
                'beneficiario': 0.0,
                'comision':0.0,
                'total_2':0.0,
                }
            aux_total = line.prevista + line.inicial_caja
            res[line.id]['total'] = aux_total
            porcentaje = (100.00 - line.porcentaje)/100.00
            aux_beneficiario = (aux_total)*(porcentaje)
            res[line.id]['beneficiario']  = aux_beneficiario
            res[line.id]['comision']  = aux_total - aux_beneficiario
            res[line.id]['total_2'] = aux_total
            return res

    _columns = dict(
        porcentaje = fields.integer('Porcentaje Comision'),
        name = fields.many2one('account.account','Cuenta'),
        a_id = fields.many2one('ajeno.budget','Fondo Ajeno'),
        prevista = fields.float('Recaudacion Prevista'),
        inicial_caja = fields.float('Saldo Inicial Caja'),
        total = fields.function(_amount_budget_ajeno, string='Total', multi="tl",store=True),#fields.float('Total'),
        beneficiario = fields.function(_amount_budget_ajeno, string='Entrega % Beneficiario', multi="tl",store=True),#fields.float('Entrega % Beneficiario'),
        comision = fields.function(_amount_budget_ajeno, string='Comision % por recaudacion', multi="tl",store=True),#fields.float('Comision % por recaudacion'),
        total_2 = fields.function(_amount_budget_ajeno, string='Total', multi="tl",store=True),#fields.float('Total'),
    )

    _defaults = dict(
        porcentaje = 10,
    )

ajenoBudgetLine()
class ajenoBudget(osv.Model):
    _name = 'ajeno.budget'
    _columns = dict(
        line_ids = fields.one2many('ajeno.budget.line','a_id','Detalle'),
        name = fields.many2one('budget.poa','Presupuesto'),
        porcentaje = fields.integer('Porcentaje Comision'),
    )
    _defaults = dict(
        porcentaje = 10,
    )
ajenoBudget()

##reporte de recurso TTHH
class recursoTTHHLine(osv.TransientModel):
    _name = 'recurso.tthh.line'
    _columns = dict(
        r_id = fields.many2one('recurso.tthh','Recurso TTHH'),
        cargo_id = fields.many2one('hr.job','Cargo'),
        cargo_id2 = fields.char('Cargo',size=64),
        funcionarios = fields.integer('Funcionarios'),
        total = fields.float('Total Anual'),
    )

class recursoTTHH(osv.TransientModel):
    _name = 'recurso.tthh'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        line_ids = fields.one2many('recurso.tthh.line','r_id','Detalle Cargo'),
    )

    def generaRecursoTTHH(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('recurso.tthh.line')
        contract_obj = self.pool.get('hr.contract')
        ocupacional_obj = self.pool.get('grupo.ocupacional')
        lista_empleado = []
        cargo = {}
        for this in self.browse(cr, uid, ids, context=context):
            old_line_ids = line_obj.search(cr, uid, [('r_id','=',this.id)], context=context)
            if old_line_ids:
                line_obj.unlink(cr, uid, old_line_ids, context=context)
            contract_ids = contract_obj.search(cr, uid, [('program_id','=',this.program_id.id),
                                                         ('activo','=',True)])
            if contract_ids:
                for contract_id in contract_ids:
                    contrato = contract_obj.browse(cr, uid, contract_id)
                    if contrato.ocupational_id:
                        if not contrato.employee_id.id in lista_empleado:
                            cargo[contrato.ocupational_id.id]=[]
                            cargo[contrato.ocupational_id.id].append(1)
                            cargo[contrato.ocupational_id.id].append(contrato.wage)
                        else:
                            cargo[contrato.ocupational_id.id][0]+=1
                            cargo[contrato.ocupational_id.id][1]+=contrato.wage
                        lista_empleado.append(contrato.employee_id.id)
            for cargo_id in cargo:
                ocupacional = ocupacional_obj.browse(cr, uid, cargo_id)
                line_obj.create(cr, uid, {
                    'r_id':this.id,
                    'cargo_id2':ocupacional.name,
                    'funcionarios':cargo[cargo_id][0],
                    'total':cargo[cargo_id][1],
                })
        return True

    def printRecursoTTHH(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = []
        self.generaRecursoTTHH(cr, uid, ids)
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'recurso_tthh',
            'model': 'recurso.tthh',
            'datas': datas,
            'nodestroy': True,                        
            }        

recursoTTHH()

##


class ctaFinancieraLine(osv.TransientModel):
    _name = 'cta.financiera.line'
    _columns = dict(
        t_id = fields.many2one('cta.financiera.tipo','Tipo Financiera'),
        financia_id = fields.many2one('budget.financiamiento','Cta. Financiera'),
        inicial = fields.float('Inicial'),
        reformas = fields.float('Reformas'),
        final = fields.float('Final'),
        ingresos = fields.float('Ingresos'),
        compromisos = fields.float('Compromisos'),
        saldos = fields.float('Saldos'),
        desc = fields.char('Partida Gasto',size=128),
    )
ctaFinancieraLine()

class ctaFinancieraTipo(osv.TransientModel):
    _name = 'cta.financiera.tipo'
    _order = 'tipo asc'

    def _amount_financiera(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'inicial': 0.0,
                'reformas': 0.0,
                'final':0.0,
                'ingresos':0.0,
                'compromisos':0.0,
                'pagado':0.0,
                'saldos':0.0,
                'saldo_pagado':0.0,
                }
            aux_inicial = aux_reforma = aux_final = aux_ingresos = aux_compromisos = aux_saldos = 0
            for line_line in line.line_ids:
                aux_inicial += line_line.inicial
                aux_reforma += line_line.reformas
                aux_final += line_line.final
                aux_ingresos += line_line.ingresos
                aux_compromisos += line_line.compromisos
                aux_saldos += line_line.saldos
            res[line.id]['inicial']  = aux_inicial
            res[line.id]['reformas']  = aux_reforma
            res[line.id]['final']  = aux_final
            res[line.id]['ingresos']  = aux_ingresos
            res[line.id]['compromisos']  = aux_compromisos

            res[line.id]['saldos']  = aux_saldos
        return res
    
    _columns = dict(
        c_id = fields.many2one('cta.financiera','Financiera'),
        cg_id = fields.many2one('cta.financiera.gastado','Financiera'),
        tipo = fields.char('Tipo',size=2),
        inicial = fields.function(_amount_financiera, string='Inicial', multi="tl"),#fields.float('Inicial'),
        reformas = fields.function(_amount_financiera, string='Reformas', multi="tl"),#fields.float('Reformas'),
        final = fields.function(_amount_financiera, string='Final', multi="tl"),#fields.float('Final'),
        ingresos = fields.function(_amount_financiera, string='Ingresos', multi="tl"),#fields.float('Ingresos'),
        compromisos = fields.function(_amount_financiera, string='Comprometido', multi="tl"),#fields.float('Compromisos'),
        pagado = fields.function(_amount_financiera, string='Pagado', multi="tl"),#fields.float('Compromisos'),
        saldos = fields.function(_amount_financiera, string='Saldo Comprometido', multi="tl"),#fields.float('Saldos'),
        saldo_pagado = fields.function(_amount_financiera, string='Saldo Pagado', multi="tl"),#fields.float('Saldos'),
        line_ids = fields.one2many('cta.financiera.line','t_id','Detalle Financiamiento'),
    )
ctaFinancieraTipo()

class ctaFinancieraGastado(osv.TransientModel):
    _name = 'cta.financiera.gastado'

    def _amount_financiera(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = {
                'recaudado': 0.0,
                'gastado': 0.0,
                'saldo':0.0,
                'recaudado_sc': 0.0,
                'gastado_sc': 0.0,
                'saldo_sc':0.0,
                'recaudado_t': 0.0,
                'gastado_t': 0.0,
                'saldo_t':0.0,
                }
            aux_rec = aux_gas = aux_sal = aux_recsc = aux_gassc = aux_salsc = aux_rect = aux_gast = aux_salt = 0 
            for line in this.line_ids:
                for line_line in line.line_ids:
                    if line_line.financia_id.tipo=='SC':
                        aux_recsc += line_line.ingresos
                        aux_gassc += line_line.compromisos
                    else:
                        aux_rec += line_line.ingresos
                        aux_gas += line_line.compromisos
                    aux_salsc = aux_recsc - aux_gassc
                    aux_sal = aux_rec - aux_gas
            aux_rect = aux_recsc + aux_rec
            aux_gast = aux_gassc + aux_gas
            aux_salt = aux_rect - aux_gast
            res[this.id]['recaudado']  = aux_rec
            res[this.id]['gastado']  = aux_gas
            res[this.id]['saldo']  = aux_sal
            res[this.id]['recaudado_sc']  = aux_recsc
            res[this.id]['gastado_sc']  = aux_gassc
            res[this.id]['saldo_sc']  = aux_salsc
            res[this.id]['recaudado_t']  = aux_rect
            res[this.id]['gastado_t']  = aux_gast
            res[this.id]['saldo_t']  = aux_salt
        return res

    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        tipo = fields.selection([('Completo','Completo'),('Caja Bancos','SC'),('Partidas Ingreso','NoSC')],'Tipo'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
        line_ids = fields.one2many('cta.financiera.tipo','cg_id','Detalle Tipo Cuenta'),
        recaudado = fields.function(_amount_financiera, string='Recaudado Anio Actual(+)', multi="tl"),
        gastado = fields.function(_amount_financiera, string='Gastado Anio Actual(-)', multi="tl"),
        saldo = fields.function(_amount_financiera, string='Saldo Anio Actual', multi="tl"),
        recaudado_sc = fields.function(_amount_financiera, string='Recaudado Caja Bancos(+)', multi="tl"),
        gastado_sc = fields.function(_amount_financiera, string='Gastado Caja Bancos(-)', multi="tl"),
        saldo_sc = fields.function(_amount_financiera, string='Saldo Caja Bancos', multi="tl"),
        recaudado_t = fields.function(_amount_financiera, string='Total Recaudado(+)', multi="tl"),
        gastado_t = fields.function(_amount_financiera, string='Total Gastado(-)', multi="tl"),
        saldo_t = fields.function(_amount_financiera, string='Total Saldo', multi="tl"),
    )

    def calcular_financieragas(self,cr, uid, ids, context=None):
        res = { }
        context = { }
        result = []
        line_obj = self.pool.get('cta.financiera.line')
        tipo_obj = self.pool.get('cta.financiera.tipo')
        c_b_lines_obj = self.pool.get('budget.item')
        financia_obj = self.pool.get('budget.financiamiento')
        partida_fin_obj = self.pool.get('partida.financia')
        itm_migra_obj = self.pool.get('budget.item.migrated')
        lista_subtotal = []
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            antes_ids = tipo_obj.search(cr, uid, [('cg_id','=',this.id)])
            if antes_ids:
                tipo_obj.unlink(cr, uid, antes_ids)
            if this.tipo=='Caja Bancos':
                financia_ids = financia_obj.search(cr, uid, [('tipo','=','SC')])
            elif this.tipo=='Partidas Ingreso':
                financia_ids = financia_obj.search(cr, uid, [('tipo','=','PI')])
            else:
                financia_ids = financia_obj.search(cr, uid, [])
            if financia_ids:
                for financia_id in financia_ids:
                    financiera = financia_obj.browse(cr, uid, financia_id)
                    if not financiera.name[0:2] in lista_subtotal:
                        lista_subtotal.append(financiera.name[0:2])
            for code in lista_subtotal:
                #itera por cuenta financiera catalogo
                if this.tipo=='Caja Bancos':
                    financia_ids = financia_obj.search(cr, uid, [('code','=',code),('tipo','=','SC')])
                elif this.tipo=='Partidas Ingreso':
                    financia_ids = financia_obj.search(cr, uid, [('tipo','=','PI'),('code','=',code)])
                else:
                    financia_ids = financia_obj.search(cr, uid, [('code','=',code)])
                ids_lines_ingreso = []
                res_line = { }
                if financia_ids:
                    tipo_id = tipo_obj.create(cr, uid, {
                        'cg_id':this.id,
                        'tipo':code,
                    })
                    for financia_id in financia_ids:
                        financiera = financia_obj.browse(cr, uid, financia_id)
                        #busco partidas de ingreso que financia la cuenta
                        if not financiera.name[0:2]==code:
                            continue
                        partida_fin_ids = partida_fin_obj.search(cr, uid, [('financiera_id','=',financia_id),('poa_id','=',poa_id)])
                        #if financiera.name=='5301':
                        #    import pdb
                        #    pdb.set_trace()
                        if partida_fin_ids:
                            #import pdb
                            #pdb.set_trace()
                            res_line[financia_id] = {
                                'code':financiera.name,
                                'name': financiera.desc,
                                'planned_amount':0,
                                'reform':0,
                                'codificado':0,
                                'ingresos':0,
                                'gastos':0,
                                'saldo':0,
                                'descripcion':financiera.desc_report,
                            }
                            ids_lines_ingreso = []
                            aux_sc = 0
                            aux_inicial = 0
                            ref_obj = self.pool.get('financia.reforma')
                            aux_reforma = aux_codif = 0
                            for record in partida_fin_obj.read(cr, uid, partida_fin_ids, ['id','is_reform','reforma_ids','item_id','monto','reforma','recaudado','codificado'], context):
                                #aux_reforma = aux_codif = 0
                                #aqui en la lista hay q pasar ids de budget item no de post
                                res_line[financia_id]['planned_amount'] += record['monto']
                                aux_inicial += record['monto']
                                #aux_sc += record['monto']
                                context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}           
                                partida_reforma = c_b_lines_obj.browse(cr,uid,record['item_id'][0], context=context)
                                if record['is_reform']:
                                    aux_reforma += partida_reforma.reform_amount
                                else:
                                    reforma_ids = ref_obj.search(cr, uid, [('f_id','=',record['id']),('fecha','>=',date_from),('fecha','<=',date_to)])   #campo monto
#                                    reforma_ids = ref_obj.search(cr, uid, [('f_id','in',partida_fin_ids),('fecha','>=',date_from),('fecha','<=',date_to)])   #campo monto
                                    if reforma_ids:
                                        for reforma_id in reforma_ids:
                                            reforma = ref_obj.browse(cr, uid, reforma_id)
                                            aux_reforma += reforma.monto
                                ids_lines_ingreso.append(record['item_id'][0])
                                planed = 0
                                aux_ingreso1 = 0
                                aux_ingreso1 = record['monto']+aux_reforma
                                aux_sc += record['codificado']#aux_ingreso1#record['monto']   ##aqui hay q tomar en cuenta las reformas
#                            print "AUXXXX sc", aux_sc
                            aux_ingreso = 0
                            #preguntar si es SC pone lo mismo del inicial
                            #import pdb
                            #pdb.set_trace()
                            res_line[financia_id]['reform'] += aux_reforma
                            aux_codif = aux_inicial+aux_reforma#record['monto']+aux_reforma
                            res_line[financia_id]['codificado'] = aux_codif
                            #aqui considerar si se repite la fuente financia a otras partidas de ingreso hacer el proporcional
                            fin_ids_repite = partida_fin_obj.search(cr, uid, [('poa_id','=',poa_id),('id','not in',partida_fin_ids),('item_id','in',ids_lines_ingreso)])
                            total_inicial_repetido = aux_inicial
                            inicial_repite = 0
                            if fin_ids_repite:
                                for record in partida_fin_obj.read(cr, uid, fin_ids_repite, ['monto'], context):
                                    inicial_repite += record['monto']
                            else:
                                total_inicial_repetido = 0
                            total_inicial_repetido += inicial_repite 
                            print "TOTAL INICIAL REPETIDPO", total_inicial_repetido
                            if financiera.desc:
                                if financiera.desc[0:2]=='SC':
                                    aux_ingreso = aux_sc
                                    res_line[financia_id]['ingresos']=aux_sc
                                else:
                                    for line in c_b_lines_obj.browse(cr,uid,ids_lines_ingreso, context=context):
                                        aux_pagado = line.paid_amount
                                        if total_inicial_repetido>0:
                                            aux_pagado = line.paid_amount*aux_inicial/total_inicial_repetido
                                        res_line[financia_id]['ingresos']+=aux_pagado#line.paid_amount
                                        aux_ingreso += aux_pagado#line.paid_amount
                            else:
                                for line in c_b_lines_obj.browse(cr,uid,ids_lines_ingreso, context=context):
                                    aux_pagado = line.paid_amount*aux_inicial/total_inicial_repetido
                                    res_line[financia_id]['ingresos']+=aux_pagado#line.paid_amount
                                    aux_ingreso += aux_pagado#line.paid_amount
                            #gastos tomo los certificate_line o los move_line de esa cuenta financiera
                            #select sum(m.debit) from budget_certificate_line c,account_move_line m where c.id=m.budget_id_cert and c.financia_id=202 and m.state='valid' and date>='2020-01-01' and date<='2020-12-31' and budget_paid=True and c.certificate_id=22805
                            sql = """select sum(m.debit),sum(m.credit) from budget_certificate_line c,account_move_line m, account_move mv where m.move_id=mv.id and c.id=m.budget_id_cert and c.financia_id=%s and m.state='valid' and m.date>='%s' and m.date<='%s' and budget_paid=True and mv.state='posted'""" % (financia_id,date_from, date_to)
                            pagado_aux = 0
                            itm_ids = itm_migra_obj.search(cr, uid, [('financia_id','=',financia_id),('date','>=',this.date_from),('date','<=',this.date_to)]) 
                            if itm_ids:
                                for itm_id in itm_ids:
                                    itm = itm_migra_obj.browse(cr, uid, itm_id)
                                    pagado_aux += itm.commited_amount
                            cr.execute(sql)
                            data = cr.fetchall()
                            #import pdb
                            #pdb.set_trace()
                            for moveline in data:
                                if moveline[0]:
                                    pagado_aux += moveline[0]
                                if moveline[1]:
                                    pagado_aux += moveline[1]
                            res_line[financia_id]['gastos'] = pagado_aux
                            res_line[financia_id]['saldo'] = aux_ingreso - pagado_aux
                    for line in res_line:
                        line_obj.create(cr, uid, {
                            't_id':tipo_id,
                            'financia_id':line,
                            'inicial':res_line[line]['planned_amount'],
                            'reformas':res_line[line]['reform'],
                            'final':res_line[line]['codificado'],
                            'ingresos':res_line[line]['ingresos'],
                            'compromisos':res_line[line]['gastos'],
                            'saldos':res_line[line]['saldo'],
                            'desc':res_line[line]['descripcion'],
                        })
#                values=res_line.itervalues()
        return True


    #####

    def _get_financia(self,cr, uid, ids, opc,campo):
        certificate_line_obj = self.pool.get('budget.certificate.line')
        financia_obj = self.pool.get('partida.financia')
        financiera_obj = self.pool.get('budget.financiamiento')
        c_b_lines_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
        if opc=='SC':
            financiera_ids = financiera_obj.search(cr, uid, [('sc','=','SC')])
        else:
            financiera_ids = financiera_obj.search(cr, uid, [('sc','!=','SC')])
        partidas_sc = [] #post
        financia_sc_ids = financia_obj.search(cr, uid, [('financiera_id','in',financiera_ids)])
        if financia_sc_ids:
            for financia_sc_id in financia_sc_ids:
                financia_sc = financia_obj.browse(cr, uid, financia_sc_id)
                if not financia_sc.budget_id.id in partidas_sc:
                    partidas_sc.append(financia_sc.budget_id.id)
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}            
        ids_lines_sc=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('budget_post_id','in',partidas_sc)])
        recaudado_sc = gastado_sc = saldo_sc = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines_sc, context=context):
            recaudado_sc += line.paid_amount
        #Gastado de los compromisos
        certificate_line_ids = certificate_line_obj.search(cr, uid, [('financia_id','in',financiera_ids),
                                                                     ('date_commited','>=',date_from),('date_commited','<=',date_to)])
        if certificate_line_ids:
            for certificate_line_id in certificate_line_ids:
                certificate_line = certificate_line_obj.browse(cr, uid, certificate_line_id)
                gastado_sc += certificate_line.amount_commited
        saldo_sc = recaudado_sc - gastado_sc
        if campo=='recaudado':
            return recaudado_sc
        else:
            return gastado_sc

    def _get_code(self,cr, uid, ids):
        result = []
        financia_obj = self.pool.get('budget.financiamiento')
        lista_subtotal = []
        financia_ids = financia_obj.search(cr, uid, [])
        if financia_ids:
            for financia_id in financia_ids:
                financiera = financia_obj.browse(cr, uid, financia_id)
                if not financiera.name[0:2] in lista_subtotal:
                    lista_subtotal.append(financiera.name[0:2])
        return lista_subtotal
            
    def _get_totales(self,cr, uid, ids, code):
        res = { }
        res_line = { }
        context = { }
        result = []
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
        c_b_lines_obj = self.pool.get('budget.item')
        financia_obj = self.pool.get('budget.financiamiento')
        partida_fin_obj = self.pool.get('partida.financia')
        #itera por cuenta financiera catalogo
        lista_subtotal = []
#        financia_ids = financia_obj.search(self.cr, self.uid, [('code','=',code)])
        financia_ids = financia_obj.search(cr, uid, [])
        ids_lines_ingreso = []
        if financia_ids:
            for financia_id in financia_ids:
                financiera = financia_obj.browse(cr, uid, financia_id)
                #busco partidas de ingreso que financia la cuenta
                if not financiera.name[0:2]==code:
                    continue
                partida_fin_ids = partida_fin_obj.search(cr, uid, [('financiera_id','=',financia_id)])
                res_line[financia_id] = {
                    'code':financiera.name,
                    'name': financiera.desc,
                    'planned_amount':0,
                    'reform':0,
                    'codificado':0,
                    'ingresos':0,
                    'gastos':0,
                    'saldo':0,
                    'descripcion':financiera.desc_report,
                }
                ids_lines_ingreso = []
                aux_sc = 0
                for record in partida_fin_obj.read(cr, uid, partida_fin_ids, ['budget_id','monto','reforma','recaudado'], context):
                    #aqui en la lista hay q pasar ids de budget item no de post
                    res_line[financia_id]['planned_amount'] += record['monto']
                    aux_sc += record['monto']
                    res_line[financia_id]['reform'] += record['reforma']
                    res_line[financia_id]['codificado'] += (record['monto']+record['reforma'])
                    item_ids = c_b_lines_obj.search(cr, uid, [('budget_post_id','=',record['budget_id'][0]),('poa_id','=',poa_id)])
                    if item_ids:
                        ids_lines_ingreso.append(item_ids[0]) #tengo las de ingreso que financian esa cuenta no si va solo la cero o todo
                    context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}           
                    planed = 0
                    aux_ingreso = 0
                #preguntar si es SC pone lo mismo del inicial
                if financiera.desc:
                    if financiera.desc[0:2]=='SC':
                        aux_ingreso = aux_sc
                        res_line[financia_id]['ingresos']=aux_sc
                    else:
                        for line in c_b_lines_obj.browse(cr,uid,ids_lines_ingreso, context=context):
                            res_line[financia_id]['ingresos']+=line.paid_amount
                            aux_ingreso += line.paid_amount
                else:
                    for line in c_b_lines_obj.browse(cr,uid,ids_lines_ingreso, context=context):
                        res_line[financia_id]['ingresos']+=line.paid_amount
                        aux_ingreso += line.paid_amount
                #gastos tomo los certificate_line o los move_line de esa cuenta financiera
                sql = "SELECT budget_certificate_line.id,budget_certificate_line.amount,budget_certificate_line.amount_certified,budget_certificate_line.amount_commited,budget_id FROM budget_certificate_line,budget_certificate \
                WHERE budget_certificate.state='commited' and budget_certificate_line.certificate_id=budget_certificate.id and financia_id = %s \
                AND budget_certificate.date_commited is not Null and budget_certificate.date_commited>='%s' and budget_certificate.date_commited<='%s'" % (financia_id,date_from, date_to)
                cr.execute(sql)
                data = cr.fetchall()
                pagado_aux = 0
                for moveline in data:
                    pagado_aux += moveline[3]
                res_line[financia_id]['gastos'] = pagado_aux
                res_line[financia_id]['saldo'] = aux_ingreso - pagado_aux
        values=res_line.itervalues()
        return res_line

    def exporta_excel_ctag(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['CUENTA FINANCIERA GASTADO',this.tipo])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['CODIGO','CTA. FINANCIERA','INICIAL','REFORMAS','FINAL','INGRESOS','GASTOS','SALDOS','PARTIDA GASTO'])
            p_tt = p_rt = p_ct = p_it = p_gt = p_st = 0
            p_t = p_r = p_c = p_i = p_g = p_s = 0
            for line in this.line_ids:
                p_t = line.inicial
                p_r = line.reformas
                p_c = line.final
                p_i = line.ingresos
                p_g = line.compromisos
                p_s = line.saldos
                if line.line_ids:
                    for line_line in line.line_ids:
                        writer.append([line_line.financia_id.name,line_line.financia_id.desc,line_line.inicial,line_line.reformas,line_line.final,line_line.ingresos,line_line.compromisos,line_line.saldos,line_line.desc])
                    writer.append(['','SUBTOTAL',p_t,p_r,p_c,p_i,p_g,p_s])
                p_tt += p_t
                p_rt += p_r
                p_ct += p_c
                p_it += p_i
                p_gt += p_g
                p_st += p_s
            writer.append(['','TOTAL',p_tt,p_rt,p_ct,p_it,p_gt,p_st])
            writer.append(['','RECAUDADO','GASTADO','TOTAL'])
            writer.append(['','','','','MOVIMIENTO SALDO CAJA BANCOS',this.recaudado_sc,this.gastado_sc,this.saldo_sc])
            writer.append(['','','','','RECAUDACION ANIO ACTUAL',this.recaudado,this.gastado,this.saldo])
            writer.append(['','','','','TOTAL DE RECAUDACION',this.recaudado_t,this.gastado_t,this.saldo_t])
        writer.save("ctaFinancieraGastado.xls")
        out = open("ctaFinancieraGastado.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'ctaFinancieraGastado.xls'})
        return True    

    def exporta_excel_ctag1(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['CUENTA FINANCIERA GASTADO',this.tipo])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['CODIGO','CTA. FINANCIERA','INICIAL','REFORMAS','FINAL','INGRESOS','GASTOS','SALDOS','PARTIDA GASTO'])
            res_code=self._get_code(cr, uid, ids)
            p_tt = p_rt = p_ct = p_it = p_gt = p_st = 0
            for values_code in res_code:
                res=self._get_totales(cr, uid, ids, values_code)
                result_dic=res.values()
                import operator
                dic_ord=sorted(result_dic, key=operator.itemgetter('code'))
                p_t = p_r = p_c = p_i = p_g = p_s = 0
                for values in dic_ord:
                    p_t += values['planned_amount']
                    p_r += values['reform']
                    p_c += values['codificado']
                    p_i += values['ingresos']
                    p_g += values['gastos']
                    p_s += values['saldo']
                    writer.append([values['code'],values['name'],values['planned_amount'],values['reform'],values['codificado'],values['ingresos'],values['gastos'],values['saldo'],values['descripcion']])
                p_tt += p_t
                p_rt += p_r
                p_ct += p_c
                p_it += p_i
                p_gt += p_g
                p_st += p_s
                writer.append(['','SUBTOTAL',p_t,p_r,p_c,p_i,p_g,p_s])
            writer.append(['','TOTAL',p_tt,p_rt,p_ct,p_it,p_gt,p_st])
            sc_r = sc_g = sc_s = ra_r = ra_g = ra_s = tr_r = tr_g = tr_s = 0
            sc_r = self._get_financia(cr, uid, ids, 'SC','recaudado')
            sc_g = self._get_financia(cr, uid, ids,'SC','gastado')
            sc_s = sc_r  - sc_g
            ra_r = self._get_financia(cr, uid, ids,'ALL','recaudado')
            ra_g = self._get_financia(cr, uid, ids,'ALL','gastado')
            ra_s = ra_r - ra_g
            tr_r = sc_r + ra_r
            tr_g = sc_g + ra_g
            tr_s = sc_s + ra_s
            writer.append(['','RECAUDADO','GASTADO','TOTAL'])
            writer.append(['MOVIMIENTO SALDO CAJA BANCOS',sc_r,sc_g,sc_s])
            writer.append(['RECAUDACION ANIO ACTUAL',ra_r,ra_g,ra_s])
            writer.append(['TOTAL DE RECAUDACION',tr_r,tr_g,tr_s])
        writer.save("ctaFinancieraPagado.xls")
        out = open("ctaFinancieraPagado.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'ctaFinancieraPagado.xls'})
        return True    

    def printCtaFinancieraGastado(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        data['poa_id'] = report.poa_id.id
        datas = {'ids': [report.id], 'model': 'cta.financiera.gastado','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cta_financierac_gastado',
            'model': 'cta.financiera.gastado',
            'datas': datas,
            'nodestroy': True,                        
            }
ctaFinancieraGastado()


class ctaFinanciera(osv.TransientModel):
    _name = 'cta.financiera'

    def _amount_financiera(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = {
                'recaudado': 0.0,
                'gastado': 0.0,
                'saldo':0.0,
                'recaudado_sc': 0.0,
                'gastado_sc': 0.0,
                'saldo_sc':0.0,
                'recaudado_t': 0.0,
                'gastado_t': 0.0,
                'saldo_t':0.0,
                }
            aux_rec = aux_gas = aux_sal = aux_recsc = aux_gassc = aux_salsc = aux_rect = aux_gast = aux_salt = 0 
            for line in this.line_ids:
                for line_line in line.line_ids:
                    if line_line.financia_id.tipo=='SC':
                        aux_recsc += line_line.ingresos
                        aux_gassc += line_line.compromisos
                    else:
                        aux_rec += line_line.ingresos
                        aux_gas += line_line.compromisos
                    aux_salsc = aux_recsc - aux_gassc
                    aux_sal = aux_rec - aux_gas
            aux_rect = aux_recsc + aux_rec
            aux_gast = aux_gassc + aux_gas
            aux_salt = aux_rect - aux_gast
            res[this.id]['recaudado']  = aux_rec
            res[this.id]['gastado']  = aux_gas
            res[this.id]['saldo']  = aux_sal
            res[this.id]['recaudado_sc']  = aux_recsc
            res[this.id]['gastado_sc']  = aux_gassc
            res[this.id]['saldo_sc']  = aux_salsc
            res[this.id]['recaudado_t']  = aux_rect
            res[this.id]['gastado_t']  = aux_gast
            res[this.id]['saldo_t']  = aux_salt
        return res

    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        tipo = fields.selection([('Completo','Completo'),('Caja Bancos','SC'),('Partidas Ingreso','NoSC')],'Tipo'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
        line_ids = fields.one2many('cta.financiera.tipo','c_id','Detalle Tipo Cuenta'),
        recaudado = fields.function(_amount_financiera, string='Recaudado Anio Actual(+)', multi="tl"),
        gastado = fields.function(_amount_financiera, string='Gastado Anio Actual(-)', multi="tl"),
        saldo = fields.function(_amount_financiera, string='Saldo Anio Actual', multi="tl"),
        recaudado_sc = fields.function(_amount_financiera, string='Recaudado Caja Bancos(+)', multi="tl"),
        gastado_sc = fields.function(_amount_financiera, string='Gastado Caja Bancos(-)', multi="tl"),
        saldo_sc = fields.function(_amount_financiera, string='Saldo Caja Bancos', multi="tl"),
        recaudado_t = fields.function(_amount_financiera, string='Total Recaudado(+)', multi="tl"),
        gastado_t = fields.function(_amount_financiera, string='Total Gastado(-)', multi="tl"),
        saldo_t = fields.function(_amount_financiera, string='Total Saldo', multi="tl"),
    )

    ##nuevo  metodo
    
    def printCtaFinanciera(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        data['poa_id'] = report.poa_id.id
        datas = {'ids': [report.id], 'model': 'cta.financiera','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cta_financierac',
            'model': 'cta.financiera',
            'datas': datas,
            'nodestroy': True,                        
            }

    def exporta_excel_ctac(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['CUENTA FINANCIERA COMPROMETIDO',this.tipo])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['CODIGO','CTA. FINANCIERA','INICIAL','REFORMAS','FINAL','INGRESOS','GASTOS','SALDOS','PARTIDA GASTO'])
            p_tt = p_rt = p_ct = p_it = p_gt = p_st = 0
            p_t = p_r = p_c = p_i = p_g = p_s = 0
            for line in this.line_ids:
                p_t = line.inicial
                p_r = line.reformas
                p_c = line.final
                p_i = line.ingresos
                p_g = line.compromisos
                p_s = line.saldos
                if line.line_ids:
                    for line_line in line.line_ids:
                        writer.append([line_line.financia_id.name,line_line.financia_id.desc,line_line.inicial,line_line.reformas,line_line.final,line_line.ingresos,line_line.compromisos,line_line.saldos,line_line.desc])
                    writer.append(['','SUBTOTAL',p_t,p_r,p_c,p_i,p_g,p_s])
                p_tt += p_t
                p_rt += p_r
                p_ct += p_c
                p_it += p_i
                p_gt += p_g
                p_st += p_s
            writer.append(['','TOTAL',p_tt,p_rt,p_ct,p_it,p_gt,p_st])
            writer.append(['','RECAUDADO','GASTADO','TOTAL'])
            writer.append(['','','','','MOVIMIENTO SALDO CAJA BANCOS',this.recaudado_sc,this.gastado_sc,this.saldo_sc])
            writer.append(['','','','','RECAUDACION ANIO ACTUAL',this.recaudado,this.gastado,this.saldo])
            writer.append(['','','','','TOTAL DE RECAUDACION',this.recaudado_t,this.gastado_t,this.saldo_t])
        writer.save("ctaFinancieraComprometido.xls")
        out = open("ctaFinancieraComprometido.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'ctaFinancieraComprometido.xls'})
        return True    

    def calcular_financieracomp(self,cr, uid, ids, context=None):
        res = { }
        context = { }
        result = []
        line_obj = self.pool.get('cta.financiera.line')
        tipo_obj = self.pool.get('cta.financiera.tipo')
        c_b_lines_obj = self.pool.get('budget.item')
        financia_obj = self.pool.get('budget.financiamiento')
        partida_fin_obj = self.pool.get('partida.financia')
        cert_line_obj = self.pool.get('budget.certificate.line')
        cert_obj = self.pool.get('budget.certificate')
        itm_migra_obj = self.pool.get('budget.item.migrated')
        lista_subtotal = []
        lista_fin_cert_line = []
        for this in self.browse(cr, uid, ids):
#            cert_ids = cert_obj.search(cr, uid, [('date_commited','>=',this.date_from),('date_commited','<=',this.date_to),('state','=','commited')])
#            lista_origen_cert_line = cert_line_obj.search(cr, uid, [('certificate_id','in',cert_ids)])
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            antes_ids = tipo_obj.search(cr, uid, [('c_id','=',this.id)])
            if antes_ids:
                tipo_obj.unlink(cr, uid, antes_ids)
            if this.tipo=='Caja Bancos':
                financia_ids = financia_obj.search(cr, uid, [('tipo','=','SC')])
            elif this.tipo=='Partidas Ingreso':
                financia_ids = financia_obj.search(cr, uid, [('tipo','=','PI')])
            else:
                financia_ids = financia_obj.search(cr, uid, [])
            if financia_ids:
                for financia_id in financia_ids:
                    financiera = financia_obj.browse(cr, uid, financia_id)
                    if not financiera.name[0:2] in lista_subtotal:
                        lista_subtotal.append(financiera.name[0:2])
            for code in lista_subtotal:
                #itera por cuenta financiera catalogo
                if this.tipo=='Caja Bancos':
                    financia_ids = financia_obj.search(cr, uid, [('code','=',code),('tipo','=','SC')])
                elif this.tipo=='Partidas Ingreso':
                    financia_ids = financia_obj.search(cr, uid, [('tipo','=','PI'),('code','=',code)])
                else:
                    financia_ids = financia_obj.search(cr, uid, [('code','=',code)])
                ids_lines_ingreso = []
                res_line = { }
                if financia_ids:
                    tipo_id = tipo_obj.create(cr, uid, {
                        'c_id':this.id,
                        'tipo':code,
                    })
                    for financia_id in financia_ids:
                        financiera = financia_obj.browse(cr, uid, financia_id)
                        #busco partidas de ingreso que financia la cuenta
                        if not financiera.name[0:2]==code:
                            continue
                        partida_fin_ids = partida_fin_obj.search(cr, uid, [('financiera_id','=',financia_id),('poa_id','=',poa_id)])
                        if partida_fin_ids:
                            #import pdb
                            #pdb.set_trace()
                            res_line[financia_id] = {
                                'code':financiera.name,
                                'name': financiera.desc,
                                'planned_amount':0,
                                'reform':0,
                                'codificado':0,
                                'ingresos':0,
                                'gastos':0,
                                'saldo':0,
                                'descripcion':financiera.desc_report,
                            }
                            ids_lines_ingreso = []
                            aux_sc = 0
                            aux_inicial = 0
                            ref_obj = self.pool.get('financia.reforma')
                            aux_reforma = aux_codif = 0
                            for record in partida_fin_obj.read(cr, uid, partida_fin_ids, ['id','is_reform','reforma_ids','item_id','monto','reforma','recaudado','codificado'], context):
                                #aqui en la lista hay q pasar ids de budget item no de post
                                res_line[financia_id]['planned_amount'] += record['monto']
                                aux_inicial += record['monto']

                                context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}           
                                partida_reforma = c_b_lines_obj.browse(cr,uid,record['item_id'][0], context=context)
                                if record['is_reform']:
                                    aux_reforma += partida_reforma.reform_amount
                                else:
                                    reforma_ids = ref_obj.search(cr, uid, [('f_id','=',record['id']),('fecha','>=',date_from),('fecha','<=',date_to)])   #campo monto
                                    if reforma_ids:
                                        for reforma_id in reforma_ids:
                                            reforma = ref_obj.browse(cr, uid, reforma_id)
                                            aux_reforma += reforma.monto
                                ids_lines_ingreso.append(record['item_id'][0])
                                planed = 0
                                aux_ingreso1 = 0
                                aux_ingreso1 = record['monto']+aux_reforma
                                aux_sc += record['codificado']#aux_ingreso1#record['monto']   ##aqui hay q tomar en cuenta las reformas
                            aux_ingreso = 0
                            #preguntar si es SC pone lo mismo del inicial
                            #import pdb
                            #pdb.set_trace()
                            res_line[financia_id]['reform'] += aux_reforma
                            aux_codif = aux_inicial+aux_reforma#record['monto']+aux_reforma
                            res_line[financia_id]['codificado'] = aux_codif
                            #aqui considerar si se repite la fuente financia a otras partidas de ingreso hacer el proporcional
                            fin_ids_repite = partida_fin_obj.search(cr, uid, [('poa_id','=',poa_id),('id','not in',partida_fin_ids),('item_id','in',ids_lines_ingreso)])
                            total_inicial_repetido = aux_inicial
                            inicial_repite = 0
                            if fin_ids_repite:
                                for record in partida_fin_obj.read(cr, uid, fin_ids_repite, ['monto'], context):
                                    inicial_repite += record['monto']
                            else:
                                total_inicial_repetido = 0
                            total_inicial_repetido += inicial_repite 
                            if financiera.desc:
                                if financiera.desc[0:2]=='SC':
                                    aux_ingreso = aux_sc
                                    res_line[financia_id]['ingresos']=aux_sc
                                else:
                                    for line in c_b_lines_obj.browse(cr,uid,ids_lines_ingreso, context=context):
                                        aux_pagado = line.paid_amount
                                        if total_inicial_repetido>0:
                                            aux_pagado = line.paid_amount*aux_inicial/total_inicial_repetido
                                        res_line[financia_id]['ingresos']+=aux_pagado#line.paid_amount
                                        aux_ingreso += aux_pagado#line.paid_amount
                                        #if total_inicial_repetido>0:
                                        #    aux_pagado = line.paid_amount*aux_inicial/total_inicial_repetido
                                        #else:
                                        #    aux_pagado = line.paid_amount
                                        #res_line[financia_id]['ingresos']+=aux_pagado#line.paid_amount
                                        #aux_ingreso += aux_pagado#line.paid_amount
                            else:
                                for line in c_b_lines_obj.browse(cr,uid,ids_lines_ingreso, context=context):
                                    aux_pagado = line.paid_amount*aux_inicial/total_inicial_repetido
                                    res_line[financia_id]['ingresos']+=aux_pagado#line.paid_amount
                                    aux_ingreso += aux_pagado#line.paid_amount
                                    #if total_inicial_repetido:
                                    #    aux_pagado = line.paid_amount*aux_inicial/total_inicial_repetidow
                                    #else:
                                    #    aux_pagado = line.paid_amount
                                    #res_line[financia_id]['ingresos']+=aux_pagado#line.paid_amount
                                    #aux_ingreso += aux_pagado#line.paid_amount
                            #gastos tomo los certificate_line o los move_line de esa cuenta financiera
                            sql = "SELECT budget_certificate_line.id,budget_certificate_line.amount,budget_certificate_line.amount_certified,budget_certificate_line.amount_commited,budget_id FROM budget_certificate_line,budget_certificate \
                            WHERE budget_certificate.state='commited' and budget_certificate_line.certificate_id=budget_certificate.id and financia_id = %s \
                            AND budget_certificate.date_commited is not Null and budget_certificate.date_commited>='%s' and budget_certificate.date_commited<='%s'" % (financia_id,date_from, date_to)
                            #tomar los gastos de pronto pago y verificar que certificate line no han entrado en el calculo
                            pagado_aux = 0
                            itm_ids = itm_migra_obj.search(cr, uid, [('financia_id','=',financia_id),('date','>=',this.date_from),('date','<=',this.date_to)]) 
                            if itm_ids:
                                for itm_id in itm_ids:
                                    itm = itm_migra_obj.browse(cr, uid, itm_id)
                                    pagado_aux += itm.commited_amount
                            cr.execute(sql)
                            data = cr.fetchall()
                            #pagado_aux = 0
                            for moveline in data:
                                lista_fin_cert_line.append(moveline[0])
                                pagado_aux += moveline[3]
                            res_line[financia_id]['gastos'] = pagado_aux
                            res_line[financia_id]['saldo'] = aux_ingreso - pagado_aux
                        
                    for line in res_line:
                        line_obj.create(cr, uid, {
                            't_id':tipo_id,
                            'financia_id':line,
                            'inicial':res_line[line]['planned_amount'],
                            'reformas':res_line[line]['reform'],
                            'final':res_line[line]['codificado'],
                            'ingresos':res_line[line]['ingresos'],
                            'compromisos':res_line[line]['gastos'],
                            'saldos':res_line[line]['saldo'],
                            'desc':res_line[line]['descripcion'],
                        })
        return True

    ##
    
    def _get_financia(self,cr, uid, ids, opc,campo):
        certificate_line_obj = self.pool.get('budget.certificate.line')
        financia_obj = self.pool.get('partida.financia')
        financiera_obj = self.pool.get('budget.financiamiento')
        c_b_lines_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
        if opc=='SC':
            financiera_ids = financiera_obj.search(cr, uid, [('sc','=','SC')])
        else:
            financiera_ids = financiera_obj.search(cr, uid, [('sc','!=','SC')])
        partidas_sc = [] #post
        financia_sc_ids = financia_obj.search(cr, uid, [('financiera_id','in',financiera_ids)])
        if financia_sc_ids:
            for financia_sc_id in financia_sc_ids:
                financia_sc = financia_obj.browse(cr, uid, financia_sc_id)
                if not financia_sc.budget_id.id in partidas_sc:
                    partidas_sc.append(financia_sc.budget_id.id)
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}            
        ids_lines_sc=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('budget_post_id','in',partidas_sc)])
        recaudado_sc = gastado_sc = saldo_sc = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines_sc, context=context):
            recaudado_sc += line.paid_amount
        #Gastado de los compromisos
        certificate_line_ids = certificate_line_obj.search(cr, uid, [('financia_id','in',financiera_ids),
                                                                     ('date_commited','>=',date_from),('date_commited','<=',date_to)])
        if certificate_line_ids:
            for certificate_line_id in certificate_line_ids:
                certificate_line = certificate_line_obj.browse(cr, uid, certificate_line_id)
                gastado_sc += certificate_line.amount_commited
        saldo_sc = recaudado_sc - gastado_sc
        if campo=='recaudado':
            return recaudado_sc
        else:
            return gastado_sc

    def _get_code(self,cr, uid, ids):
        result = []
        financia_obj = self.pool.get('budget.financiamiento')
        lista_subtotal = []
        financia_ids = financia_obj.search(cr, uid, [])
        if financia_ids:
            for financia_id in financia_ids:
                financiera = financia_obj.browse(cr, uid, financia_id)
                if not financiera.name[0:2] in lista_subtotal:
                    lista_subtotal.append(financiera.name[0:2])
        return lista_subtotal
            
    def _get_totales(self,cr, uid, ids, code):
        res = { }
        res_line = { }
        context = { }
        result = []
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
        c_b_lines_obj = self.pool.get('budget.item')
        financia_obj = self.pool.get('budget.financiamiento')
        partida_fin_obj = self.pool.get('partida.financia')
        #itera por cuenta financiera catalogo
        lista_subtotal = []
#        financia_ids = financia_obj.search(self.cr, self.uid, [('code','=',code)])
        financia_ids = financia_obj.search(cr, uid, [])
        ids_lines_ingreso = []
        if financia_ids:
            for financia_id in financia_ids:
                financiera = financia_obj.browse(cr, uid, financia_id)
                #busco partidas de ingreso que financia la cuenta
                if not financiera.name[0:2]==code:
                    continue
                partida_fin_ids = partida_fin_obj.search(cr, uid, [('financiera_id','=',financia_id)])
                res_line[financia_id] = {
                    'code':financiera.name,
                    'name': financiera.desc,
                    'planned_amount':0,
                    'reform':0,
                    'codificado':0,
                    'ingresos':0,
                    'gastos':0,
                    'saldo':0,
                    'descripcion':financiera.desc_report,
                }
                ids_lines_ingreso = []
                aux_sc = 0
                for record in partida_fin_obj.read(cr, uid, partida_fin_ids, ['budget_id','monto','reforma','recaudado'], context):
                    #aqui en la lista hay q pasar ids de budget item no de post
                    res_line[financia_id]['planned_amount'] += record['monto']
                    aux_sc += record['monto']
                    res_line[financia_id]['reform'] += record['reforma']
                    res_line[financia_id]['codificado'] += (record['monto']+record['reforma'])
                    item_ids = c_b_lines_obj.search(cr, uid, [('budget_post_id','=',record['budget_id'][0]),('poa_id','=',poa_id)])
                    if item_ids:
                        ids_lines_ingreso.append(item_ids[0]) #tengo las de ingreso que financian esa cuenta no si va solo la cero o todo
                    context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}           
                    planed = 0
                    aux_ingreso = 0
                #preguntar si es SC pone lo mismo del inicial
                if financiera.desc:
                    if financiera.desc[0:2]=='SC':
                        aux_ingreso = aux_sc
                        res_line[financia_id]['ingresos']=aux_sc
                    else:
                        for line in c_b_lines_obj.browse(cr,uid,ids_lines_ingreso, context=context):
                            res_line[financia_id]['ingresos']+=line.paid_amount
                            aux_ingreso += line.paid_amount
                else:
                    for line in c_b_lines_obj.browse(cr,uid,ids_lines_ingreso, context=context):
                        res_line[financia_id]['ingresos']+=line.paid_amount
                        aux_ingreso += line.paid_amount
                #gastos tomo los certificate_line o los move_line de esa cuenta financiera
                sql = "SELECT budget_certificate_line.id,budget_certificate_line.amount,budget_certificate_line.amount_certified,budget_certificate_line.amount_commited,budget_id FROM budget_certificate_line,budget_certificate \
                WHERE budget_certificate.state='commited' and budget_certificate_line.certificate_id=budget_certificate.id and financia_id = %s \
                AND budget_certificate.date_commited is not Null and budget_certificate.date_commited>='%s' and budget_certificate.date_commited<='%s'" % (financia_id,date_from, date_to)
                cr.execute(sql)
                data = cr.fetchall()
                pagado_aux = 0
                for moveline in data:
                    pagado_aux += moveline[3]
                res_line[financia_id]['gastos'] = pagado_aux
                res_line[financia_id]['saldo'] = aux_ingreso - pagado_aux
        values=res_line.itervalues()
        return res_line

    def exporta_excel_ctac1(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['CUENTA FINANCIERA COMPROMETIDO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['CODIGO','CTA. FINANCIERA','INICIAL','REFORMAS','FINAL','INGRESOS','GASTOS','SALDOS','PARTIDA GASTO'])
            res_code=self._get_code(cr, uid, ids)
            p_tt = p_rt = p_ct = p_it = p_gt = p_st = 0
            for values_code in res_code:
                res=self._get_totales(cr, uid, ids, values_code)
                result_dic=res.values()
                import operator
                dic_ord=sorted(result_dic, key=operator.itemgetter('code'))
                p_t = p_r = p_c = p_i = p_g = p_s = 0
                for values in dic_ord:
                    p_t += values['planned_amount']
                    p_r += values['reform']
                    p_c += values['codificado']
                    p_i += values['ingresos']
                    p_g += values['gastos']
                    p_s += values['saldo']
                    writer.append([values['code'],values['name'],values['planned_amount'],values['reform'],values['codificado'],values['ingresos'],values['gastos'],values['saldo'],values['descripcion']])
                p_tt += p_t
                p_rt += p_r
                p_ct += p_c
                p_it += p_i
                p_gt += p_g
                p_st += p_s
                writer.append(['','SUBTOTAL',p_t,p_r,p_c,p_i,p_g,p_s])
            writer.append(['','TOTAL',p_tt,p_rt,p_ct,p_it,p_gt,p_st])
            sc_r = sc_g = sc_s = ra_r = ra_g = ra_s = tr_r = tr_g = tr_s = 0
            sc_r = self._get_financia(cr, uid, ids, 'SC','recaudado')
            sc_g = self._get_financia(cr, uid, ids,'SC','gastado')
            sc_s = sc_r  - sc_g
            ra_r = self._get_financia(cr, uid, ids,'ALL','recaudado')
            ra_g = self._get_financia(cr, uid, ids,'ALL','gastado')
            ra_s = ra_r - ra_g
            tr_r = sc_r + ra_r
            tr_g = sc_g + ra_g
            tr_s = sc_s + ra_s
            writer.append(['','RECAUDADO','GASTADO','TOTAL'])
            writer.append(['MOVIMIENTO SALDO CAJA BANCOS',sc_r,sc_g,sc_s])
            writer.append(['RECAUDACION ANIO ACTUAL',ra_r,ra_g,ra_s])
            writer.append(['TOTAL DE RECAUDACION',tr_r,tr_g,tr_s])
        writer.save("ctaFinancieraComprometido.xls")
        out = open("ctaFinancieraComprometido.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'ctaFinancieraComprometido.xls'})
        return True    

    def printCtaFinanciera1(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        data['poa_id'] = report.poa_id.id
        datas = {'ids': [report.id], 'model': 'cta.financiera','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cta_financiera',
            'model': 'cta.financiera',
            'datas': datas,
            'nodestroy': True,                        
            }
ctaFinanciera()


class evaluacionProyecto(osv.TransientModel):
    _name = 'evaluacion.proyecto'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        project_id = fields.many2one('project.project','Proyecto'),
        budget_id = fields.many2one('budget.item','Partida'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        nivel = fields.integer('Nivel'),
        completo = fields.boolean('Completo'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                sal_percent = aux_percent = aux_percent_mes = 0
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['paid_amount_mes'] += data_suma['paid_amount_mes']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['paid_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                    aux_percent_mes = (res[data['post'].parent_id.code]['paid_amount_mes']*100)/res[data['post'].parent_id.code]['codif_amount']
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_rec_mes'] = aux_percent_mes
                res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'paid_amount_mes':data['paid_amount_mes'],
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_rec_mes':data['percent_rec_mes'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        context2 = {}
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            partida_id = this.budget_id.id
            project_id = this.project_id.id
        c_b_lines_obj = self.pool.get('budget.item')
        if partida_id:
            ids_lines.append(partida_id[0])
        else:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('project_id','=',project_id)])        
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}    
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                    
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.paid_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                if line.codif_amount==0:
                    aux_percent_sal = 0
                else:
                    aux_percent_sal = 100 - aux_percent_rec
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'paid_amount':line.paid_amount,     
                    'paid_amount_mes':line2.paid_amount,
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_rec_mes':aux_percent_rec_mes,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel,
                    'final': True,
                }
                if not partida_id:
                    self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.paid_amount
                if line.codif_amount==0:
                    aux_percent_sal = 0
                else:
                    aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.paid_amount - line.codif_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['paid_amount']+=line.paid_amount
                res_line[line.budget_post_id.id]['paid_amount_mes']+=line2.paid_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'paid_amount': 0.00,
            'paid_amount_mes': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'percent_super': 0.00,
            'superavit': 0.00,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['paid_amount_mes']+=line_totales['paid_amount_mes']
                res_line['total']['to_rec']+=line_totales['to_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line

    def _get_totales_egreso(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            partida_id = this.budget_id.id
            project_id = this.project_id.id
        program_obj = self.pool.get('project.program')
        #date_from = resumen.date_start#self.datas['form']['date_from']
        #date_to = self.datas['form']['date_to']
        #program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        #program_code = self.datas['form']['program_id'][1][0:1]
        program_ids = program_obj.search(cr, uid, [])
        pr_ids = []
        if program_ids:
            for program_id in program_ids:
                pr_ids.append(program_id)
                #programa = program_obj.browse(self.cr, self.uid, program_id)
                #if programa.sequence[0:1]==program_code:
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.paid_amount
            comp_corte += line.paid_amount
        saldo = final_funcion - comp_mes
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result        

    def _get_anio(self,cr, uid, ids,code,name):
        post_obj = self.pool.get('budget.post')
        aux = ''
        if len(code)>8:
            post_ids = post_obj.search(cr, uid, [('code','=like',code[:len(code)-4]+"%")])
            if post_ids:
                post = post_obj.browse(cr, uid, post_ids[0])
                aux = post.parent_id.name
        return aux

    def exporta_excel_evpp(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE PROYECTO GASTADO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','INICIAL','REFORMAS','FINAL','PAGADO MES','%','PAGADO CORTE','%','SALDO','%','Financiamiento'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = saldo_acumulado = por_saldo = 0 
            for values in dic_ord:
                if values['code']!=0 and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if values['nivel'] in (5,8,9):
                        aux_1 = aux_2 = aux_saldo =  0
                        aux_values_rec = aux_saldo = 0
                        if abs(values['to_rec'])>0.01:
                            aux_values_rec = values['to_rec']
                        if abs(values['percent_sal'])>0.01:
                            aux_saldo = values['percent_sal']
                        anio = self._get_anio(cr, uid, ids, values['code'],values['general_budget_name'])
                        writer.append([values['code'],values['general_budget_name'],values['planned_amount'],values['reform_amount'],values['codif_amount'],values['paid_amount_mes'],'{:,.2f}'.format(values['percent_rec_mes']),values['paid_amount'],'{:,.2f}'.format(values['percent_rec']),aux_values_rec,'{:,.2f}'.format(aux_saldo),anio])
            por_pagado = (res['total']['paid_amount']*100) / res['total']['codif_amount']
            por_pagado_mes = (res['total']['paid_amount_mes']*100) / res['total']['codif_amount']
            saldo_acumulado = res['total']['codif_amount'] - res['total']['paid_amount']
            por_saldo = 100 - por_pagado
            aux_total_reforma = 0
            if abs(res['total']['reform_amount'])>0.01:
                aux_total_reforma = res['total']['reform_amount']
            writer.append(['','TOTALES',res['total']['planned_amount'],aux_total_reforma,res['total']['codif_amount'],res['total']['paid_amount_mes'],'{:,.2f}'.format(por_pagado_mes),res['total']['paid_amount'],'{:,.2f}'.format(por_pagado),saldo_acumulado,'{:,.2f}'.format(por_saldo)])
            #total egresos
            #res_e=self._get_totales_egreso(cr, uid, ids)
            #writer.append(['','TOTAL EGRESOS',res_e[0],res_e[1],res_e[2],res_e[3],res_e[4],res_e[5],res_e[6],res_e[7],res_e[8]])
        writer.save("evGastoProyectoPagado.xls")
        out = open("evGastoProyectoPagado.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evGastoProyectoPagado.xls'})
        return True

    def printEvaluacionProyecto(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.proyecto','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_proyecto',
            'model': 'evaluacion.proyecto',
            'datas': datas,
            'nodestroy': True,                        
            }
evaluacionProyecto()

class evaluacionProyectoComprometido(osv.TransientModel):
    _name = 'evaluacion.proyecto.comprometido'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        project_id = fields.many2one('project.project','Proyecto'),
        budget_id = fields.many2one('budget.item','Partida'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        nivel = fields.integer('Nivel'),
        completo = fields.boolean('Completo'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                sal_percent = aux_percent = aux_percent_mes = 0
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['commited_amount'] += data_suma['commited_amount']
                res[data['post'].parent_id.code]['commited_amount_mes'] += data_suma['commited_amount_mes']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['commited_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                    aux_percent_mes = (res[data['post'].parent_id.code]['commited_amount_mes']*100)/res[data['post'].parent_id.code]['codif_amount']
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_rec_mes'] = aux_percent_mes
                res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'codif_amount':data['codif_amount'],
                    'commited_amount':data['commited_amount'],
                    'commited_amount_mes':data['commited_amount_mes'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_rec_mes':data['percent_rec_mes'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        context2 = {}
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            partida_id = this.budget_id.id
            project_id = this.project_id.id
        c_b_lines_obj = self.pool.get('budget.item')
        if partida_id:
            ids_lines.append(partida_id[0])
        else:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('project_id','=',project_id)])        
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}    
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                    
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.commited_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.commited_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.commited_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.commited_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                if line.codif_amount==0:
                    aux_percent_sal = 0
                else:
                    aux_percent_sal = 100 - aux_percent_rec
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'commited_amount':line.commited_amount,
                    'commited_amount_mes':line2.commited_amount,
                    'paid_amount':line.paid_amount,     
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_rec_mes':aux_percent_rec_mes,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel,
                    'final': True,
                }
                if not partida_id:
                    self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.commited_amount
                if line.codif_amount==0:
                    aux_percent_sal = 0
                else:
                    aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.commited_amount - line.codif_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.commited_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.commited_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['paid_amount']+=line.paid_amount
                res_line[line.budget_post_id.id]['commited_amount']+=line.commited_amount
                res_line[line.budget_post_id.id]['commited_amount_mes']+=line2.commited_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'commited_amount': 0.00,
            'commited_amount_mes': 0.00,
            'paid_amount': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'percent_super': 0.00,
            'superavit': 0.00,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['commited_amount']+=line_totales['commited_amount']
                res_line['total']['commited_amount_mes']+=line_totales['commited_amount_mes']
                res_line['total']['to_rec']+=line_totales['to_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line

    def _get_totales_egreso(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            partida_id = this.budget_id.id
            project_id = this.project_id.id
        program_obj = self.pool.get('project.program')
        #date_from = resumen.date_start#self.datas['form']['date_from']
        #date_to = self.datas['form']['date_to']
        #program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        #program_code = self.datas['form']['program_id'][1][0:1]
        program_ids = program_obj.search(cr, uid, [])
        pr_ids = []
        if program_ids:
            for program_id in program_ids:
                pr_ids.append(program_id)
                #programa = program_obj.browse(self.cr, self.uid, program_id)
                #if programa.sequence[0:1]==program_code:
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.commited_amount
            comp_corte += line.commited_amount
        saldo = final_funcion - comp_mes
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result        


    def _get_anio(self,cr, uid, ids,code,name):
        post_obj = self.pool.get('budget.post')
        aux = ''
        if len(code)>8:
            post_ids = post_obj.search(cr, uid, [('code','=like',code[:len(code)-4]+"%")])
            if post_ids:
                post = post_obj.browse(cr, uid, post_ids[0])
                aux = post.parent_id.name
        return aux

    def exporta_excel_evpc(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE GASTOS PROYECTO COMPROMETIDO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','INICIAL','REFORMAS','FINAL','COMP. MES','%','COMP. CORTE','%','SALDO','%','Financiamiento'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = saldo_acumulado = por_saldo = 0 
            for values in dic_ord:
                if values['code']!=0 and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if values['nivel'] in (5,8,9):
                        aux_1 = aux_2 = aux_saldo =  0
                        aux_values_rec = aux_saldo = 0
                        if abs(values['to_rec'])>0.01:
                            aux_values_rec = values['to_rec']
                        if abs(values['percent_sal'])>0.01:
                            aux_saldo = values['percent_sal']
                        anio = self._get_anio(cr, uid, ids, values['code'],values['general_budget_name'])
                        writer.append([values['code'],values['general_budget_name'],values['planned_amount'],values['reform_amount'],values['codif_amount'],values['commited_amount_mes'],'{:,.2f}'.format(values['percent_rec_mes']),values['commited_amount'],'{:,.2f}'.format(values['percent_rec']),aux_values_rec,'{:,.2f}'.format(aux_saldo),anio])
            por_pagado = (res['total']['commited_amount']*100) / res['total']['codif_amount']
            por_pagado_mes = (res['total']['commited_amount_mes']*100) / res['total']['codif_amount']
            saldo_acumulado = res['total']['codif_amount'] - res['total']['commited_amount']
            por_saldo = 100 - por_pagado
            aux_total_reforma = 0
            if abs(res['total']['reform_amount'])>0.01:
                aux_total_reforma = res['total']['reform_amount']
            writer.append(['','TOTALES',res['total']['planned_amount'],aux_total_reforma,res['total']['codif_amount'],res['total']['commited_amount_mes'],'{:,.2f}'.format(por_pagado_mes),res['total']['commited_amount'],'{:,.2f}'.format(por_pagado),saldo_acumulado,'{:,.2f}'.format(por_saldo)])
            #total egresos
            #res_e=self._get_totales_egreso(cr, uid, ids)
            #writer.append(['','TOTAL EGRESOS',res_e[0],res_e[1],res_e[2],res_e[3],res_e[4],res_e[5],res_e[6],res_e[7],res_e[8]])
        writer.save("evGastoProyectoComprometido.xls")
        out = open("evGastoProyectoComprometido.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evGastoProyectoComprometido.xls'})
        return True                

    def printEvaluacionProyectoComprometido(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.proyecto.comprometido','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_proyecto_comprometido',
            'model': 'evaluacion.proyecto.comprometido',
            'datas': datas,
            'nodestroy': True,                        
            }
evaluacionProyectoComprometido()

class evaluacionBudget(osv.TransientModel):
    _name = 'evaluacion.budget'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        nivel = fields.integer('Nivel'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                sal_percent = aux_percent = 0
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['paid_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
                res[data['post'].parent_id.code]['superavit'] += 0
                res[data['post'].parent_id.code]['percent_super'] += 0
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_sal':data['percent_sal'],
                    'superavit':0,#data['superavit'],
                    'percent_super':0,#data['percent_super'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)            
            
    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_rec = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.paid_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                aux_percent_sal = 100 - aux_percent_rec
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'paid_amount':line.paid_amount,     
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_sal':aux_percent_sal,
                    'superavit':0,#aux_superavit,
                    'percent_super':0,#aux_percent_super,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.paid_amount - line.codif_amount
                aux_percent_rec = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['paid_amount']+=line.paid_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
#                res_line[line.budget_post_id.id]['percent_rec']+=aux_percent_rec
#                res_line[line.budget_post_id.id]['percent_sal']+=aux_percent_sal
#                res_line[line.budget_post_id.id]['superavit']+=aux_superavit
#                res_line[line.budget_post_id.id]['percent_super']+=aux_percent_super
                res_line[line.budget_post_id.id]['superavit']+=0
                res_line[line.budget_post_id.id]['percent_super']+=0
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'paid_amount': 0.00,
            'to_rec': 0.00,
            'general_budget_name':0,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'percent_super': 0.00,
            'superavit': 0.00,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['to_rec']+=line_totales['to_rec']
  #              res_line['total']['percent_rec']+=line_totales['percent_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
#                res_line['total']['percent_super']+=line_totales['percent_super']
#                res_line['total']['superavit']+=line_totales['superavit']
                res_line['total']['percent_super']+=0
                res_line['total']['superavit']+=0
        return res_line

    def exporta_excel_evbg(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE GASTOS'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','ASIGNACION INICIAL','REFORMAS','FINAL','PAGADO','% PAGADO','SALDO ACUMULADO','% SALDO'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = saldo_acumulado = por_saldo = 0 
            for values in dic_ord:
                if values['code']!='0' and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if (this.nivel > 0 and values['nivel']== this.nivel) or this.nivel==0:
                        #porcentaje = 0
                        #porcentaje = (values['superavit'] * 100) / values['codif_amount']
                        aux_1 = aux_2 = aux_saldo =  0
                        if values['superavit']>0:
                            aux_saldo = values['to_rec'] + values['superavit']
                            aux_saldo = 0
                            aux_1 = aux_saldo
                        else:
                            aux_1 = values['to_rec']
                        if (100-values['percent_rec'])<0:
                            aux_2 = 0
                        else:
                            aux_2 = 100-values['percent_rec']
                        writer.append([values['code'],values['general_budget_name'],values['planned_amount'],values['reform_amount'],values['codif_amount'],values['paid_amount'],values['percent_rec'],values['to_rec'],values['percent_sal']])
            por_pagado = abs((res['total']['paid_amount']*100) / res['total']['codif_amount'])
            saldo_acumulado = abs(res['total']['codif_amount'] - res['total']['paid_amount'])
            por_saldo = 100 - por_pagado
            writer.append(['','TOTALES',res['total']['planned_amount'],res['total']['reform_amount'],res['total']['codif_amount'],res['total']['paid_amount'],por_pagado,saldo_acumulado,por_saldo])
        writer.save("evaluacionPresupuestoGasto.xls")
        out = open("evaluacionPresupuestoGasto.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evaluacionPresupuestoGasto.xls'})
        return True            

    def printEvaluacionE(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
#        data['budget_id'] = context['active_id']
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.budget','form': data}
#        datas = {'ids': [report.id], 'model': 'evaluacion.budget','form': data,'budget_id': context.get('active_id')}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_pgasto',
            'model': 'evaluacion.budget',
            'datas': datas,
            'nodestroy': True,                        
            }

evaluacionBudget()

class evaluacionBudgetI(osv.TransientModel):
    _name = 'evaluacion.budgeti'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        nivel = fields.integer('Nivel'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                sal_percent = aux_percent = 0
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['paid_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
                res[data['post'].parent_id.code]['superavit'] += data_suma['superavit']
                res[data['post'].parent_id.code]['percent_super'] = 0
                superavit = percent = 0
                res[data['post'].parent_id.code]['superavit'] += superavit
                res[data['post'].parent_id.code]['percent_super'] = percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_sal':data['percent_sal'],
                    'superavit':data['superavit'],
                    'percent_super':data['percent_super'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','ingreso')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.paid_amount
                if aux_to_pay < 0:
                    aux_to_pay = 0
                aux_percent_rec = aux_superavit = aux_percent_super = 0
                aux_percent_sal = 100 - aux_percent_rec
                if line.paid_amount > line.codif_amount:
                    aux_superavit = line.paid_amount - line.codif_amount
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'paid_amount':line.paid_amount,     
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_sal':aux_percent_sal,
                    'superavit':aux_superavit,
                    'percent_super':aux_percent_super,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = 0
                if line.paid_amount > line.codif_amount:
                    aux_superavit = line.paid_amount - line.codif_amount
                aux_percent_rec = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['paid_amount']+=line.paid_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
#                res_line[line.budget_post_id.id]['percent_rec']+=aux_percent_rec
#                res_line[line.budget_post_id.id]['percent_sal']+=aux_percent_sal
                res_line[line.budget_post_id.id]['superavit']+=aux_superavit
#                res_line[line.budget_post_id.id]['percent_super']+=aux_percent_super
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'paid_amount': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'percent_super': 0.00,
            'superavit': 0.00,
            'level':0,
            'nivel':0,
            'code':0,
            'code_aux':0,
            'general_budget_name':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['to_rec']+=line_totales['to_rec']
#                res_line['total']['percent_rec']+=line_totales['percent_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
#                res_line['total']['percent_super']+=line_totales['percent_super']
                res_line['total']['superavit']+=line_totales['superavit']
        return res_line

    def exporta_excel_evbi(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE INGRESOS'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','ASIGNACION INICIAL','REFORMAS','FINAL','RECAUDADO','% RECAUDADO','SALDO ACUMULADO','% SALDO ACUMULADO','SUPERAVIT','% SUPERAVIT'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = saldo_acumulado = por_saldo = 0 
            for values in dic_ord:
                if values['code']!='0' and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if (this.nivel > 0 and values['nivel']== this.nivel) or this.nivel==0:
                        porcentaje = 0
                        if values['codif_amount']>0:
                            porcentaje = (values['superavit'] * 100) / values['codif_amount']
                        aux_1 = aux_2 = aux_saldo =  0
                        if values['superavit']>0:
                            aux_saldo = values['to_rec'] + values['superavit']
                            aux_saldo = 0
                            aux_1 = aux_saldo
                        else:
                            aux_1 = values['to_rec']
                        if (100-values['percent_rec'])<0:
                            aux_2 = 0
                        else:
                            aux_2 = 100-values['percent_rec']
                        writer.append([values['code'],values['general_budget_name'],values['planned_amount'],values['reform_amount'],values['codif_amount'],values['paid_amount'],values['percent_rec'],aux_1,aux_2,values['superavit'],porcentaje])
            por_pagado = abs((res['total']['paid_amount']*100) / res['total']['codif_amount'])
            saldo_acumulado = abs(res['total']['codif_amount'] - res['total']['paid_amount'])
            por_saldo = 100 - por_pagado
            writer.append(['','TOTALES',res['total']['planned_amount'],res['total']['reform_amount'],res['total']['codif_amount'],res['total']['paid_amount'],por_pagado,saldo_acumulado,por_saldo,res['total']['superavit'],res['total']['percent_super']])
        writer.save("evaluacionPresupuestoIngreso.xls")
        out = open("evaluacionPresupuestoIngreso.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evaluacionPresupuestoIngreso.xls'})
        return True        

    def printEvaluacionI(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
#        data['budget_id'] = context['active_id']
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.budgeti','form': data}
#        datas = {'ids': [report.id], 'model': 'evaluacion.budgeti','form': data,'budget_id': context.get('active_id')}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_pingreso',
            'model': 'evaluacion.budgeti',
            'datas': datas,
            'nodestroy': True,                        
            }

evaluacionBudgetI()

####evaluacion programa cons

class evalPrograma(osv.TransientModel):
    _name = 'eval.programa'
    _order = 'code asc'
    _columns = dict(
        ec_id = fields.many2one('evaluacion.programa.cons.comprometido','Evaluacion'),
        ep_id = fields.many2one('evaluacion.programa.cons','Evaluacion'),
        code = fields.related('programa_id', 'sequence',type="char",size=10,string='Programa',store=True),
        programa_id = fields.many2one('project.program','Programa'),
        inicial = fields.float('Inicial'),
        reforma = fields.float('Reforma'),
        final = fields.float('Final'),
        com_mes = fields.float('Comp/Pag. Mes'),
        por_mes = fields.float('Porcentaje Mes'),
        com_acum = fields.float('Comp/Pag. Acumulado'),
        por_acum = fields.float('Porcentaje Acum.'),
        saldo = fields.float('Saldo'),
        por_saldo = fields.float('Porcentaje Saldo'),
    )
evalPrograma()

class evaluacionBudgetProgramaCons(osv.TransientModel):
    _name = 'evaluacion.programa.cons'
    _columns = dict(
        is_program = fields.boolean('Seleccionar Programa?'),
        line_ids = fields.one2many('eval.programa','ep_id','Detalle Programa'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        nivel = fields.integer('Nivel'),
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2many('project.program','e_p_id','e_id','p_id','Programa'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )
    
    def printEvaluacionProgramaCons(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
#        data['budget_id'] = context['active_id']
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.programa.cons','form': data}
#        datas = {'ids': [report.id], 'model': 'evaluacion.budgeti','form': data,'budget_id': context.get('active_id')}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_programa_cons',
            'model': 'evaluacion.programa.cons',
            'datas': datas,
            'nodestroy': True,                        
            }    

    def exporta_excel_evprp_cons(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE PROGRAMA CONSOLIDADO PAGADO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PROGRAMA','INICIAL','REFORMAS','FINAL','PAGADO MES','%','PAGADO CORTE','%','SALDO','%'])
            aux_inicial = aux_reforma = aux_codificado = aux_comp_mes = aux_por_mes = aux_comp_acum = aux_por_acum = aux_saldo = aux_por_saldo = 0
            for line in this.line_ids:
                aux_programa = line.programa_id.sequence + ' ' + line.programa_id.name
                aux_inicial += line.inicial
                aux_reforma += line.reforma
                aux_codificado += line.final
                aux_comp_mes += line.com_mes
                aux_comp_acum += line.com_acum
                aux_saldo += line.saldo
                writer.append([aux_programa,line.inicial,line.reforma,line.final,line.com_mes,line.por_mes,line.com_acum,line.por_acum,line.saldo,line.por_saldo])
            aux_por_mes = (aux_comp_mes * 100)/aux_codificado
            aux_por_acum = (aux_comp_acum * 100)/aux_codificado
            aux_por_saldo = (aux_saldo * 100)/aux_codificado
            writer.append(['TOTAL',aux_inicial,aux_reforma,aux_codificado,aux_comp_mes,aux_por_mes,aux_comp_acum,aux_por_acum,aux_saldo,aux_por_saldo])
        writer.save("evGastoProgramaPagado.xls")
        out = open("evGastoProgramaPagado.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evGastoProgramaGastado.xls'})
        return True        

    def generarCons(self, cr, uid, ids, context=None):
        program_obj = self.pool.get('project.program')
        line_obj = self.pool.get('eval.programa')
        item_obj = self.pool.get('budget.item')
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            line_antes = line_obj.search(cr, uid, [('ep_id','=',this.id)])
            if line_antes:
                line_obj.unlink(cr, uid, line_antes)
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}    
            period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
            periodo = period_obj.browse(cr, uid, period_ids[0])
            context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                    
            programa_ids = []
            if this.is_program:
                for programa_id in this.programa_id:
                    programa_ids.append(programa_id.id)
            else:
                programa_ids = program_obj.search(cr, uid, [])
            for programa_id in programa_ids:
                item_ids = item_obj.search(cr, uid, [('program_id','=',programa_id),('poa_id','=',poa_id),('type_budget','=','gasto')])
                if item_ids:
                    aux_inicial = aux_reforma = aux_codificado = aux_comp_mes = aux_por_mes = aux_comp_acum = aux_por_acum = aux_saldo = aux_por_saldo = 0
                    for line in item_obj.browse(cr,uid,item_ids, context=context):
                        line2 = item_obj.browse(cr,uid,line.id, context=context2)
                        aux_inicial += line.planned_amount
                        aux_reforma += line.reform_amount
                        aux_codificado += line.codif_amount
                        aux_comp_mes += line2.paid_amount
                        aux_comp_acum += line.paid_amount
                    aux_por_mes = (aux_comp_mes * 100)/aux_codificado
                    aux_por_acum = (aux_comp_acum * 100)/aux_codificado
                    aux_saldo = aux_codificado - aux_comp_acum
                    aux_por_saldo = (aux_saldo * 100)/aux_codificado
                    line_obj.create(cr, uid, {
                        'ep_id':this.id,
                        'programa_id':programa_id,
                        'inicial':aux_inicial,
                        'reforma':aux_reforma,
                        'final':aux_codificado,
                        'com_mes':aux_comp_mes,
                        'por_mes':aux_por_mes,
                        'com_acum':aux_comp_acum,
                        'por_acum':aux_por_acum,
                        'saldo':aux_saldo,
                        'por_saldo':aux_por_saldo,
                    })
        return True    

evaluacionBudgetProgramaCons()

class evaluacionBudgetProgramaConsComprometido(osv.TransientModel):
    _name = 'evaluacion.programa.cons.comprometido'
    _columns = dict(
        is_program = fields.boolean('Seleccionar Programa?'),
        line_ids = fields.one2many('eval.programa','ec_id','Detalle Programa'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        nivel = fields.integer('Nivel'),
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2many('project.program','e_p_id','e_id','p_id','Programa'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def printEvaluacionProgramaComprometidoCons(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
#        data['budget_id'] = context['active_id']
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.programa.comprometido.cons','form': data}
#        datas = {'ids': [report.id], 'model': 'evaluacion.budgeti','form': data,'budget_id': context.get('active_id')}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_programa_comprometido_cons',
            'model': 'evaluacion.programa.comprometido.cons',
            'datas': datas,
            'nodestroy': True,                        
            }    

    def exporta_excel_evprc_cons(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE PROGRAMA CONSOLIDADO COMPROMETIDO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PROGRAMA','INICIAL','REFORMAS','FINAL','COMPROMETIDO MES','%','COMP. CORTE','%','SALDO','%'])
            aux_inicial = aux_reforma = aux_codificado = aux_comp_mes = aux_por_mes = aux_comp_acum = aux_por_acum = aux_saldo = aux_por_saldo = 0
            for line in this.line_ids:
                aux_programa = line.programa_id.sequence + ' ' + line.programa_id.name
                aux_inicial += line.inicial
                aux_reforma += line.reforma
                aux_codificado += line.final
                aux_comp_mes += line.com_mes
                aux_comp_acum += line.com_acum
                aux_saldo += line.saldo
                writer.append([aux_programa,line.inicial,line.reforma,line.final,line.com_mes,line.por_mes,line.com_acum,line.por_acum,line.saldo,line.por_saldo])
            aux_por_mes = (aux_comp_mes * 100)/aux_codificado
            aux_por_acum = (aux_comp_acum * 100)/aux_codificado
            aux_por_saldo = (aux_saldo * 100)/aux_codificado
            writer.append(['TOTAL',aux_inicial,aux_reforma,aux_codificado,aux_comp_mes,aux_por_mes,aux_comp_acum,aux_por_acum,aux_saldo,aux_por_saldo])
        writer.save("evGastoProgramaComprometido.xls")
        out = open("evGastoProgramaComprometido.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evGastoProgramaComprometido.xls'})
        return True        

    def generarCompCons(self, cr, uid, ids, context=None):
        program_obj = self.pool.get('project.program')
        line_obj = self.pool.get('eval.programa')
        item_obj = self.pool.get('budget.item')
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            line_antes = line_obj.search(cr, uid, [('ec_id','=',this.id)])
            if line_antes:
                line_obj.unlink(cr, uid, line_antes)
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}    
            period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
            periodo = period_obj.browse(cr, uid, period_ids[0])
            context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                    
            programa_ids = []
            if this.is_program:
                for programa_id in this.programa_id:
                    programa_ids.append(programa_id.id)
            else:
                programa_ids = program_obj.search(cr, uid, [])
            for programa_id in programa_ids:
                item_ids = item_obj.search(cr, uid, [('program_id','=',programa_id),('poa_id','=',poa_id),('type_budget','=','gasto')])
                if item_ids:
                    aux_inicial = aux_reforma = aux_codificado = aux_comp_mes = aux_por_mes = aux_comp_acum = aux_por_acum = aux_saldo = aux_por_saldo = 0
                    for line in item_obj.browse(cr,uid,item_ids, context=context):
                        line2 = item_obj.browse(cr,uid,line.id, context=context2)
                        aux_inicial += line.planned_amount
                        aux_reforma += line.reform_amount
                        aux_codificado += line.codif_amount
                        aux_comp_mes += line2.commited_amount
                        aux_comp_acum += line.commited_amount
                    aux_por_mes = (aux_comp_mes * 100)/aux_codificado
                    aux_por_acum = (aux_comp_acum * 100)/aux_codificado
                    aux_saldo = aux_codificado - aux_comp_acum
                    aux_por_saldo = (aux_saldo * 100)/aux_codificado
                    line_obj.create(cr, uid, {
                        'ec_id':this.id,
                        'programa_id':programa_id,
                        'inicial':aux_inicial,
                        'reforma':aux_reforma,
                        'final':aux_codificado,
                        'com_mes':aux_comp_mes,
                        'por_mes':aux_por_mes,
                        'com_acum':aux_comp_acum,
                        'por_acum':aux_por_acum,
                        'saldo':aux_saldo,
                        'por_saldo':aux_por_saldo,
                    })
        return True
    
evaluacionBudgetProgramaConsComprometido()
#####


class evaluacionBudgetPrograma(osv.TransientModel):
    _name = 'evaluacion.programa'

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                aux_percent = aux_percent_mes = 0
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['paid_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                    aux_percent_mes = (res[data['post'].parent_id.code]['paid_amount_mes']*100)/res[data['post'].parent_id.code]['codif_amount']
                    res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
                else:
                    res[data['post'].parent_id.code]['percent_sal'] = 0
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_rec_mes'] = 100 - aux_percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'paid_amount_mes':data['paid_amount_mes'],
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_rec_mes':data['percent_rec_mes'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)        

    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        context2 = {}
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            program_id = this.program_id.id
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','=',program_id),('project_id.state','=','exec')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}    
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                    
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.paid_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                    aux_percent_sal = 100 - aux_percent_rec
                else:
                    aux_percent_sal = 0
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'paid_amount':line.paid_amount,     
                    'paid_amount_mes':line2.paid_amount,     
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_rec_mes':aux_percent_rec_mes,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.paid_amount - line.codif_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['paid_amount']+=line.paid_amount
                res_line[line.budget_post_id.id]['paid_amount_mes']+=line2.paid_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'paid_amount': 0.00,
            'paid_amount_mes': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'percent_super': 0.00,
            'superavit': 0.00,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['paid_amount_mes']+=line_totales['paid_amount_mes']
                res_line['total']['to_rec']+=line_totales['to_rec']
                res_line['total']['percent_rec']+=line_totales['percent_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line

    def _get_totales_funcion(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        program_obj = self.pool.get('project.program')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from#self.datas['form']['date_from']
            date_to = this.date_to
            program_id = this.program_id.id
            resumen = this.poa_id
        c_b_lines_obj = self.pool.get('budget.item')
        program_code = this.program_id.sequence[0:1]
        if this.program_id.sequence[2]!='1':
            return False
        program_ids = program_obj.search(cr, uid, [])
        pr_ids = []
        if program_ids:
            for program_id in program_ids:
                programa = program_obj.browse(cr, uid, program_id)
                if programa.sequence[0:1]==program_code:
                    pr_ids.append(programa.id)
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.paid_amount
            comp_corte += line.paid_amount
        saldo = final_funcion - comp_mes
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result    

    def _get_totales_egreso(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        program_obj = self.pool.get('project.program')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from#self.datas['form']['date_from']
            date_to = this.date_to
            program_id = this.program_id.id
            resumen = this.poa_id
        c_b_lines_obj = self.pool.get('budget.item')
        program_code = this.program_id.sequence[0:1]
        if this.program_id.sequence!='1.1':
            return False
        program_ids = program_obj.search(cr, uid, [])
        pr_ids = []
        if program_ids:
            for program_id in program_ids:
                pr_ids.append(program_id)
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.paid_amount
            comp_corte += line.paid_amount
        saldo = final_funcion - comp_mes
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result    


    def exporta_excel_evprp(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE PROGRAMA GASTADO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','INICIAL','REFORMAS','FINAL','PAGADO MES','%','PAGADO CORTE','%','SALDO','%'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = por_pagado_mes = saldo_acumulado = por_saldo_mes = por_saldo = 0 
            for values in dic_ord:
                if values['code']!=0 and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if values['nivel']<=5:
                        aux1 = len(values['code'])
                        if aux1>6 and aux1<=9:
                            aux = values['code'][0:]
                        elif aux1>9:
                            aux = values['code'][0:]
                        else:
                            aux = values['code']
                        aux_1 = aux_2 = aux_saldo =  0
                        aux_rf = 0
                        if abs(values['reform_amount'])>0.01:
                            aux_rf = values['reform_amount']
                        writer.append([values['code'],values['general_budget_name'],values['planned_amount'],aux_rf,values['codif_amount'],values['paid_amount_mes'],'{:,.2f}'.format(values['percent_rec_mes']),values['paid_amount'],'{:,.2f}'.format(values['percent_rec']),values['to_rec'],'{:,.2f}'.format(values['percent_sal'])])
            por_pagado = (res['total']['paid_amount']*100) / res['total']['codif_amount']
            por_pagado_mes = (res['total']['paid_amount_mes']*100) / res['total']['codif_amount']
            saldo_acumulado = res['total']['codif_amount'] - res['total']['paid_amount']
            por_saldo = 100 - por_pagado
            por_saldo_mes = 100 - por_pagado_mes
            aux_total_reforma = 0
            if abs(res['total']['reform_amount'])>0.01:
                aux_total_reforma = res['total']['reform_amount']    
            writer.append(['','TOTALES',res['total']['planned_amount'],aux_total_reforma,res['total']['codif_amount'],res['total']['paid_amount_mes'],'{:,.2f}'.format(por_pagado_mes),res['total']['paid_amount'],'{:,.2f}'.format(por_pagado),saldo_acumulado,'{:,.2f}'.format(por_saldo)])
            #total funcion
            res_f=self._get_totales_funcion(cr, uid, ids)
            if res_f:
                writer.append(['','TOTAL FUNCION',res_f[0],res_f[1],res_f[2],res_f[3],res_f[4],res_f[5],res_f[6],res_f[7],res_f[8]])
            #total egreso
            res_e=self._get_totales_egreso(cr, uid, ids)
            if res_e:
                writer.append(['','TOTAL EGRESOS',res_e[0],res_e[1],res_e[2],res_e[3],res_e[4],res_e[5],res_e[6],res_e[7],res_e[8]])
        writer.save("evGastoProgramaPagado.xls")
        out = open("evGastoProgramaPagado.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evGastoProgramaPagado.xls'})
        return True    

    def printEvaluacionPrograma(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
#        data['budget_id'] = context['active_id']
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.programa','form': data}
#        datas = {'ids': [report.id], 'model': 'evaluacion.budgeti','form': data,'budget_id': context.get('active_id')}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_programa',
            'model': 'evaluacion.programa',
            'datas': datas,
            'nodestroy': True,                        
            }

    _columns = dict(
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        nivel = fields.integer('Nivel'),
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )
evaluacionBudgetPrograma()

class evaluacionBudgetProgramaComprometido(osv.TransientModel):
    _name = 'evaluacion.programa.comprometido'

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            aux_percent = 0
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['commited_amount'] += data_suma['commited_amount']
                res[data['post'].parent_id.code]['commited_amount_mes'] += data_suma['commited_amount_mes']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['commited_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                    aux_percent_mes = (res[data['post'].parent_id.code]['commited_amount_mes']*100)/res[data['post'].parent_id.code]['codif_amount']
                    res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
                else:
                    res[data['post'].parent_id.code]['percent_sal'] = 0
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_rec_mes'] = 100 - aux_percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'codif_amount':data['codif_amount'],
                    'commited_amount':data['commited_amount'],
                    'commited_amount_mes':data['commited_amount_mes'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_rec_mes':data['percent_rec_mes'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)

    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        context2 = {}
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            program_id = this.program_id.id
        c_b_lines_obj = self.pool.get('budget.item')
        now = datetime.now()
        time = now.strftime("%Y-%m-%d")
        if time>='2023-07-30':
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','=',program_id),('project_id.state','=','exec')])
        else:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','=',program_id)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}    
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                    
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.commited_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.commited_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.commited_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.commited_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                    aux_percent_sal = 100 - aux_percent_rec
                else:
                    aux_percent_sal = 0
                aux_percent_sal = 100 - aux_percent_rec
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'paid_amount':line.paid_amount,   
                    'commited_amount':line.commited_amount,  
                    'commited_amount_mes':line2.commited_amount,  
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_rec_mes':aux_percent_rec_mes,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.paid_amount - line.codif_amount
                aux_percent_rec = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['paid_amount']+=line.paid_amount
                res_line[line.budget_post_id.id]['commited_amount']+=line.commited_amount
                res_line[line.budget_post_id.id]['commited_amount_mes']+=line2.commited_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'commited_amount': 0.00,
            'commited_amount_mes': 0.00,
            'paid_amount': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'percent_super': 0.00,
            'superavit': 0.00,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['commited_amount']+=line_totales['commited_amount']
                res_line['total']['commited_amount_mes']+=line_totales['commited_amount_mes']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['to_rec']+=line_totales['to_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line

    def _get_totales_funcion(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        program_obj = self.pool.get('project.program')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from#self.datas['form']['date_from']
            date_to = this.date_to
            program_id = this.program_id.id
            resumen = this.poa_id
        c_b_lines_obj = self.pool.get('budget.item')
        program_code = this.program_id.sequence[0:1]
        if this.program_id.sequence[2]!='1':
            return False
        program_ids = program_obj.search(cr, uid, [])
        pr_ids = []
        if program_ids:
            for program_id in program_ids:
                programa = program_obj.browse(cr, uid, program_id)
                if programa.sequence[0:1]==program_code:
                    pr_ids.append(programa.id)
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.commited_amount
            comp_corte += line.commited_amount
        saldo = final_funcion - comp_mes
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result

    def _get_totales_egreso(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        program_obj = self.pool.get('project.program')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from#self.datas['form']['date_from']
            date_to = this.date_to
            program_id = this.program_id.id
            resumen = this.poa_id
        c_b_lines_obj = self.pool.get('budget.item')
        program_code = this.program_id.sequence[0:1]
        if this.program_id.sequence!='1.1':
            return False
        program_ids = program_obj.search(cr, uid, [])
        pr_ids = []
        if program_ids:
            for program_id in program_ids:
                pr_ids.append(program_id)
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.commited_amount
            comp_corte += line.commited_amount
        saldo = final_funcion - comp_mes
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result

    def exporta_excel_evprc(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE PROGRAMA COMPROMETIDO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','INICIAL','REFORMAS','FINAL','COMPROMETIDO MES','%','COMP. CORTE','%','SALDO','%'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = por_pagado_mes = saldo_acumulado = por_saldo_mes = por_saldo = 0 
            for values in dic_ord:
                if values['code']!=0 and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if values['nivel']<=5:
                        aux1 = len(values['code'])
                        if aux1>6 and aux1<=9:
                            aux = values['code'][0:]
                        elif aux1>9:
                            aux = values['code'][0:]
                        else:
                            aux = values['code']
                        aux_1 = aux_2 = aux_saldo =  0
                        aux_rf = 0
                        if abs(values['reform_amount'])>0.01:
                            aux_rf = values['reform_amount']
                        writer.append([aux,values['general_budget_name'],values['planned_amount'],aux_rf,values['codif_amount'],values['commited_amount_mes'],'{:,.2f}'.format(values['percent_rec_mes']),values['commited_amount'],'{:,.2f}'.format(values['percent_rec']),values['to_rec'],'{:,.2f}'.format(values['percent_sal'])])
            if res['total']['codif_amount']>0:
                por_pagado = (res['total']['commited_amount']*100) / res['total']['codif_amount']
                por_pagado_mes = (res['total']['commited_amount_mes']*100) / res['total']['codif_amount']
            else:
                por_pagado = (res['total']['commited_amount']*100) 
                por_pagado_mes = (res['total']['commited_amount_mes']*100)
            saldo_acumulado = abs(res['total']['codif_amount'] - res['total']['commited_amount'])
            por_saldo = 100 - por_pagado
            por_saldo_mes = 100 - por_pagado_mes
            aux_total_reforma = 0
            if abs(res['total']['reform_amount'])>0.01:
                aux_total_reforma = res['total']['reform_amount']    
            writer.append(['','TOTALES',res['total']['planned_amount'],aux_total_reforma,res['total']['codif_amount'],res['total']['commited_amount_mes'],'{:,.2f}'.format(por_pagado_mes),res['total']['commited_amount'],'{:,.2f}'.format(por_pagado),saldo_acumulado,'{:,.2f}'.format(por_saldo)])
            #total funcion
            res_f=self._get_totales_funcion(cr, uid, ids)
            if res_f:
                writer.append(['','TOTAL FUNCION',res_f[0],res_f[1],res_f[2],res_f[3],res_f[4],res_f[5],res_f[6],res_f[7],res_f[8]])
            #total egresos
            res_e=self._get_totales_egreso(cr, uid, ids)
            if res_e:
                writer.append(['','TOTAL EGRESOS',res_e[0],res_e[1],res_e[2],res_e[3],res_e[4],res_e[5],res_e[6],res_e[7],res_e[8]])
        writer.save("evGastoProgramaComprometido.xls")
        out = open("evGastoProgramaComprometido.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evGastoProgramaComprometido.xls'})
        return True    

    def printEvaluacionProgramaComprometido(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
#        data['budget_id'] = context['active_id']
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.programa.comprometido','form': data}
#        datas = {'ids': [report.id], 'model': 'evaluacion.budgeti','form': data,'budget_id': context.get('active_id')}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_programa_comprometido',
            'model': 'evaluacion.programa.comprometido',
            'datas': datas,
            'nodestroy': True,                        
            }

    _columns = dict(
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        nivel = fields.integer('Nivel'),
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )
evaluacionBudgetProgramaComprometido()

class fondoProgramaLine(osv.TransientModel):
    _name = 'fondo.programa.line'
    _columns = dict(
        p_id = fields.many2one('fondo.programa','Programa'),
        budget_id = fields.many2one('budget.item','Partida'),
        inicial = fields.float('Inicial'),
        reforma = fields.float('Reforma'),
        codificado = fields.float('Codificado'),
        comprometido = fields.float('Comprometido'),
        saldo = fields.float('Saldo por comprometer'),
    )
fondoProgramaLine()
class fondoPrograma(osv.TransientModel):
    _name = 'fondo.programa'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        disponible = fields.float('Total Disponible'),
        line_ids = fields.one2many('fondo.programa.line','p_id','Detalle'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def exporta_excel_fppp(self, cr, uid, ids, context=None):
        obj = self.pool.get('fondo.programa')
        obj.loadSaldoPrograma(cr, uid, ids, context)
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['FONDO PROGRAMA'])
            aux_programa = this.program_id.sequence + ' - ' + this.program_id.name
            writer.append(['PROGRAMA',aux_programa])
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
        writer.save("fondoPrograma.xls")
        out = open("fondoPrograma.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'fondoPrograma.xls'})
        return True    

    def printSaldoPrograma(self, cr, uid, ids, context):
        obj = self.pool.get('fondo.programa')
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        obj.loadSaldoPrograma(cr, uid, ids, context)
        datas = {'ids': [report.id], 'model': 'report.fondo.programa'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fondo.programa',
            'model': 'fondo.programa',
            'datas': datas,
            'nodestroy': True,                        
        }
    
    def loadSaldoPrograma(self, cr, uid, ids, context):
        line_obj = self.pool.get('fondo.programa.line')
        item_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            ant_ids = line_obj.search(cr, uid, [('p_id','=',this.id)])
            if ant_ids:
                line_obj.unlink(cr, uid, ant_ids)
            item_ids = item_obj.search(cr, uid, [('program_id','=',this.program_id.id),('poa_id','=',this.poa_id.id)])
            context = {'by_date':True,'date_start': this.poa_id.date_start, 'date_end':this.poa_id.date_end ,'poa_id':this.poa_id.id}
            for line in item_obj.browse(cr,uid,item_ids, context=context):
                aux = line.codif_amount-line.commited_amount,
                line_id = line_obj.create(cr, uid, {
                    'p_id':this.id,
                    'budget_id':line.id,
                    'inicial':line.planned_amount,
                    'reforma':line.reform_amount,
                    'codificado':line.codif_amount,
                    'comprometido':line.commited_amount,
                    'saldo':line.commited_balance,
                })
        return True

fondoPrograma()
#############por programa

class WizardProjectTaskAvance(osv.TransientModel):
    _name = 'wizard.project.task.avance'

    def onchange_avance(self, cr, uid, ids, avance, last):
        res = {}
        if not avance:
            return res
        if avance < last:
            res = {'warning': {'title': 'Error', 'message': 'El avance es incorrecto.'}, 'value': {'new_avance': 0}}
        return res
        
    _columns = dict(
        project_id = fields.many2one('project.project', 'Proyecto', readonly=True),
        task_id = fields.many2one('project.task', 'Actividad', readonly=True),
        last_avance = fields.float('Ultimo Avance Registrado', readonly=True),
        last_date = fields.date('Fecha de Ultimo Avance', readonly=True),
        name = fields.char('Descripción', size=128, required=True),
        new_avance = fields.float('Nuevo Avance (%)', required=True),
        archivo = fields.binary('Archivo'),
        valor = fields.boolean('Con Valores?'),
        tipo_budget = fields.selection([('Olympo','Olympo'),('General','General'),('RiobambaFox','RiobambaFox')],'Tipo Migrar'),
        )

    def get_project(self, cr, uid, context):
        data = False
        if context.get('active_id', False):
            data = self.pool.get('project.task').read(cr, uid, context.get('active_id'), ['project_id'])['project_id']
        return data[0]

    def get_task(self, cr, uid, context):
        return context.get('active_id', False)

    def get_last(self, cr, uid, context):
        task_id = context.get('active_id')
        last = self.pool.get('project.task.avance').get_last(cr, uid, task_id)
        return last

    def get_last_date(self, cr, uid, context):
        task_id = context.get('active_id')
        last = self.pool.get('project.task.avance').get_last_date(cr, uid, task_id)
        return last        

    def budgetNuevo(self, cr, uid, ids, context):
        task = self.pool.get('project.task').browse(cr, uid, context['active_id'])
        item_obj = self.pool.get('budget.item')
        data = self.read(cr, uid, ids)[0]
        if task.task_ant:
            for line in task.task_ant.budget_planned_ids:
                valor_aux = 0
                if data['valor']:
                    valor_aux = line.planned_amount 
                item_id = item_obj.create(cr, uid, {
                    'task_id':task.id,
                    'name':line.budget_post_id.name,
                    'budget_post_id':line.budget_post_id.id,
                    'planned_amount':valor_aux,
                })
        return True

    def migrar_budget(self, cr, uid, ids, context):
        item_obj = self.pool.get('budget.item')
        post_obj = self.pool.get('budget.post')
        project_obj = self.pool.get('project.project')
        project_program = self.pool.get('project.program')
        data = self.read(cr, uid, ids)[0]
        wiz = self.browse(cr, uid, ids, context)[0]
        project = wiz.project_id
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            #veo si es de ingreso o gasto basado en el parent
            if project.type_budget=='ingreso':
                for r in range(sh.nrows)[1:]:
                    aux_budget = sh.cell(r,0).value
                    aux_budget_str = str(aux_budget)
                    budget_str = aux_budget_str.replace('.','')
                    post_ids = post_obj.search(cr, uid, [('code','=',budget_str)])
                    if post_ids:
                        item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('task_id','=',project.tasks[0].id)],limit=1)
                        if item_ids:
                            item_obj.write(cr, uid, item_ids[0],{
                                'planned_amount':sh.cell(r,2).value,
                            })
                        else:
                            item_id = item_obj.create(cr, uid, {
                                'budget_post_id':post_ids[0],
                                'task_id':project.tasks[0].id,
                                'planned_amount':sh.cell(r,2).value,
                            }) 
                    else:
                        print "NO BUDGET", budget_str
            else:
                for r in range(sh.nrows)[1:]:
                    aux_budget = sh.cell(r,0).value
                    aux_p_nombre = ustr(sh.cell(r,1).value)
                    if aux_budget[6:7]=='.':
                        aux_program_code = str(aux_budget[7:11]) 
                        aux_budget_str = str(aux_budget)[0:6]
                    else:
                        aux_program_code = str(aux_budget[9:]) 
                        aux_budget_str = str(aux_budget)[0:8]
                    program_ids = project_program.search(cr, uid, [('sequence','=',aux_program_code)])
                    if program_ids:
                        project_ids = project_obj.search(cr, uid, [('state','=','open'),('poa_id','=',project.poa_id.id),('program_id','=',program_ids[0])])
                        if project_ids:
                            project = project_obj.browse(cr, uid, project_ids[0])
                            budget_str = aux_budget_str.replace('.','')
                            post_ids = post_obj.search(cr, uid, [('code','=',budget_str)])
                            if post_ids:
                                item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('task_id','=',project.tasks[0].id)],limit=1)
                                if item_ids:
                                    item_obj.write(cr, uid, item_ids[0],{
                                        'planned_amount':sh.cell(r,2).value,
                                    })
                                else:
                                    item_id = item_obj.create(cr, uid, {
                                        'budget_post_id':post_ids[0],
                                        'task_id':project.tasks[0].id,
                                        'planned_amount':sh.cell(r,2).value,
                                    }) 
                            else:
                                print "NO BUDGET - ", budget_str+' - ', aux_p_nombre
                        else:
                            print "NO PROYECTO de programa",aux_program_code
                    else:
                        print "NO Pograma",aux_program_code
        return True

    def migrar_budget2(self, cr, uid, ids, context):
        item_obj = self.pool.get('budget.item')
        post_obj = self.pool.get('budget.post')
        project_obj = self.pool.get('project.project')
        data = self.read(cr, uid, ids)[0]
        wiz = self.browse(cr, uid, ids, context)[0]
        project = wiz.project_id
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            riobamba = fox = False
            band_aux = True
            #for r in range(sh.nrows)[1:]:
            if band_aux:
                if data['tipo_budget']:
                    if data['tipo_budget']=='RiobambaFox':
                        for r in range(sh.nrows)[1:]:
                            type_obj = self.pool.get('budget.user.type')
                            type_ids = type_obj.search(cr, uid, [('name','=','Corriente')],limit=1)
                            if project.type_budget=='ingreso':
                                aux_budget = ustr(sh.cell(r,0).value)[0:10]
                                aux_nivel = ustr(sh.cell(r,0).value)[10:12]
                                if int(aux_nivel)>0:
                                    aux_budget = ustr(sh.cell(r,0).value)[0:12]
                                budget_str = aux_budget.replace('.','')
                                aux_parent = budget_str[0:len(budget_str)-2]
                                parent_ids = post_obj.search(cr, uid, [('code','=',aux_parent)])
                                post_ids = post_obj.search(cr, uid, [('code','=',budget_str)])
                                if post_ids:
                                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('task_id','=',project.tasks[0].id)],limit=1)
                                    if item_ids:
                                        item_obj.write(cr, uid, item_ids[0],{
                                            'planned_amount':sh.cell(r,2).value,
                                        })
                                    else:
                                        item_id = item_obj.create(cr, uid, {
                                            'budget_post_id':post_ids[0],
                                            'task_id':project.tasks[0].id,
                                            'planned_amount':sh.cell(r,2).value,
                                        }) 
                                else:
                                    print "NO BUDGETE============================",budget_str 
                                    post_id = post_obj.create(cr, uid, {
                                        'code':budget_str,
                                        'name':ustr(sh.cell(r,1).value),
                                        'internal_type':'ingreso',
                                        'budget_type_id':type_ids[0],
                                        'parent_id':parent_ids[0],
                                    })
                                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_id),('task_id','=',project.tasks[0].id)],limit=1)
                                    if item_ids:
                                        item_obj.write(cr, uid, item_ids[0],{
                                            'planned_amount':sh.cell(r,2).value,
                                        })
                                    else:
                                        item_id = item_obj.create(cr, uid, {
                                            'budget_post_id':post_id,
                                            'task_id':project.tasks[0].id,
                                            'planned_amount':sh.cell(r,2).value,
                                        }) 
                                    print "NO BUDGET", budget_str, ustr(sh.cell(r,1).value)
                            else:
                                #aux_budget = ustr(sh.cell(r,0).value)[4:11]
                                aux_value = int(sh.cell(r,2).value)
                                if not aux_value>0:
                                    continue
                                aux_budget = ustr(sh.cell(r,0).value)#[4:]
                                aux_obra = int(ustr(sh.cell(r,0).value)[14:17])
                                if aux_obra>0:
                                    aux_budget = ustr(sh.cell(r,0).value)[4:]
                                    budget_str = aux_budget.replace('.','')
                                    aux_parent = budget_str[0:len(budget_str)-4]
                                else:
                                    if int(aux_budget[11:13])>0:
                                        if int (aux_budget[14:17])>0:
                                            budget_str = aux_budget[4:].replace('.','')
                                        else:
                                            budget_str = aux_budget[4:13].replace('.','')
                                    else:
                                        budget_str = aux_budget[4:11].replace('.','')
                                    aux_budget = budget_str#ustr(sh.cell(r,0).value)[4:11]
                                    aux_parent = budget_str[0:len(budget_str)-2]
                                #budget_str = aux_budget.replace('.','')
                                parent_ids = post_obj.search(cr, uid, [('code','=',aux_parent)])
                                post_ids = post_obj.search(cr, uid, [('code','=',budget_str)])
                                if post_ids:
                                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('task_id','=',project.tasks[0].id)],limit=1)
                                    if item_ids:
                                        item_obj.write(cr, uid, item_ids[0],{
                                            'planned_amount':sh.cell(r,2).value,
                                        })
                                    else:
                                        item_id = item_obj.create(cr, uid, {
                                            'budget_post_id':post_ids[0],
                                            'task_id':project.tasks[0].id,
                                            'planned_amount':sh.cell(r,2).value,
                                        }) 
                                else:
                                    print "NO PARTIDA",':',budget_str
                                    if parent_ids:
                                        post_id = post_obj.create(cr, uid, {
                                            'code':budget_str,
                                            'name':ustr(sh.cell(r,1).value),
                                            'internal_type':'gasto',
                                            'budget_type_id':type_ids[0],
                                            'parent_id':parent_ids[0],
                                        })
                                    else:
                                        post_id = post_obj.create(cr, uid, {
                                            'code':budget_str,
                                            'name':ustr(sh.cell(r,1).value),
                                            'internal_type':'gasto',
                                            'budget_type_id':type_ids[0],
                                        })
                                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_id),('task_id','=',project.tasks[0].id)],limit=1)
                                    if item_ids:
                                        item_obj.write(cr, uid, item_ids[0],{
                                            'planned_amount':sh.cell(r,2).value,
                                        })
                                    else:
                                        item_id = item_obj.create(cr, uid, {
                                            'budget_post_id':post_id,
                                            'task_id':project.tasks[0].id,
                                            'planned_amount':sh.cell(r,2).value,
                                        }) 
                    elif data['tipo_budget']=='General':
                        for r in range(sh.nrows)[1:]:
                            aux_budget = ustr(sh.cell(r,0).value)
                            budget_str = aux_budget.replace('.','')
                            post_ids = post_obj.search(cr, uid, [('code','=',budget_str)])
                            if post_ids:
                                item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('task_id','=',project.tasks[0].id)],limit=1)
                                if item_ids:
                                    item_obj.write(cr, uid, item_ids[0],{
                                        'planned_amount':sh.cell(r,2).value,
                                    })
                                else:
                                    item_id = item_obj.create(cr, uid, {
                                        'budget_post_id':post_ids[0],
                                        'task_id':project.tasks[0].id,
                                        'planned_amount':sh.cell(r,2).value,
                                    }) 
                            else:
                                print "NO BUDGET", budget_str
                    elif data['tipo_budget']=='Olympo':
                        ## primero verificacion
                        aux_type = 15
                        for r in range(sh.nrows)[1:]:
                            aux_budget = ustr(sh.cell(r,0).value)
                            budget_str = aux_budget[4:10]
                            if aux_budget[11:14]!='000':
                                budget_str = aux_budget[4:14].replace('.','')
                            post_ids = post_obj.search(cr, uid, [('code','=',budget_str)])
                            if post_ids:
                                post_id = post_ids[0]
                            else:
                                print budget_str,';',ustr(sh.cell(r,1).value)
                                str_padre = budget_str[0:6]
                                parent_ids = post_obj.search(cr, uid, [('code','=',str_padre)],limit=1)
                                if parent_ids:
                                    parent_id = parent_ids[0]
                                else:
                                    print "NO PAPA============", ';',str_padre
                                    parent_id = post_obj.create(cr, uid, {
                                        'code':str_padre,
                                        'name':'PAPA AUX',
                                        'internal_type':'view',
                                        'budget_type_id':aux_type,
                                    })
                                post_id = post_obj.create(cr, uid, {
                                    'code':budget_str,
                                    'name':ustr(sh.cell(r,1).value),
                                    'internal_type':'normal',
                                    'budget_type_id':aux_type,
                                    'parent_id':parent_id,
                                })
                            item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_id),('task_id','=',project.tasks[0].id)],limit=1)
                            if item_ids:
                                item_obj.write(cr, uid, item_ids[0],{
                                    'planned_amount':sh.cell(r,2).value,
                                })
                            else:
                                item_id = item_obj.create(cr, uid, {
                                    'budget_post_id':post_id,
                                    'task_id':project.tasks[0].id,
                                    'planned_amount':sh.cell(r,2).value,
                                })
                    elif data['tipo_budget']=='Olympo2':
                        ## primero verificacion
                        aux_type = 15
                        for r in range(sh.nrows)[1:]:
                            aux_budget = ustr(sh.cell(r,0).value)
                            budget_str = aux_budget[9:15]
                            if aux_budget[16:19]!='000':
                                budget_str = aux_budget[9:19].replace('.','')
                            post_ids = post_obj.search(cr, uid, [('code','=',budget_str)])
                            if post_ids:
                                post_id = post_ids[0]
                            else:
                                print budget_str,';',ustr(sh.cell(r,1).value)
                                str_padre = budget_str[0:6]
                                parent_ids = post_obj.search(cr, uid, [('code','=',str_padre)],limit=1)
                                if parent_ids:
                                    parent_id = parent_ids[0]
                                else:
                                    print "NO PAPA============", ';',str_padre
                                    parent_id = post_obj.create(cr, uid, {
                                        'code':str_padre,
                                        'name':'PAPA AUX',
                                        'internal_type':'view',
                                        'budget_type_id':aux_type,
                                    })
                                post_id = post_obj.create(cr, uid, {
                                    'code':budget_str,
                                    'name':ustr(sh.cell(r,1).value),
                                    'internal_type':'normal',
                                    'budget_type_id':aux_type,
                                    'parent_id':parent_id,
                                })
                            item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_id),('task_id','=',project.tasks[0].id)],limit=1)
                            if item_ids:
                                item_obj.write(cr, uid, item_ids[0],{
                                    'planned_amount':sh.cell(r,2).value,
                                })
                            else:
                                item_id = item_obj.create(cr, uid, {
                                    'budget_post_id':post_id,
                                    'task_id':project.tasks[0].id,
                                    'planned_amount':sh.cell(r,2).value,
                                })
        return True

    def action_register_avance(self, cr, uid, ids, context):
        close_task = False
        wiz = self.browse(cr, uid, ids, context)[0]
        if wiz.new_avance > 100:
            raise osv.except_osv('Error', u'No puede registrar más del 100% de avance de la actividad')
        if wiz.new_avance == 100:
            close_task = True
        data = {'name': wiz.name, 'executed': wiz.new_avance, 'task_id': wiz.task_id.id, 'date_done': time.strftime('%Y-%m-%d %H:%M:%S')}
        self.pool.get('project.task.avance').create(cr, uid, data)
        return {'type': 'ir.actions.act_window_close'}

    _defaults = dict(
        project_id = get_project,
        task_id = get_task,
        last_avance = get_last,
        last_date = get_last_date
        )

    def _check_vals(self, cr, uid, ids):
        for obj in self.browse(cr, uid, ids):
            if obj.last_avance > obj.new_avance:
                return False
        return True

    _constraints = [(_check_vals, 'Avance incorrecto.', ['Registro de Avance'])]


class WizardAddCondition(osv.TransientModel):
    _name = 'wizard.project.condition'

    def action_save_ok(self, cr, uid, ids, context):
        wiz = self.browse(cr, uid, ids, context)[0]
        if not wiz.ok:
            raise osv.except_osv('Aviso', u'No ha marcado como Cumplido / Realizado la condición seleccionada.')
        c_id = wiz.condition_id.id
        cond_name = ' '.join([wiz.condition_id.name, '(CUMPLIDO)'])
        self.pool.get('project.condition').write(cr, uid, c_id, {'name': cond_name, 'done': True})
        return {'type': 'ir.actions.act_window_close'}
    
    _columns = dict(
        project_id = fields.many2one('project.project', 'Proyecto', readonly=True),
        condition_id = fields.many2one('project.condition', string='Condición de Cierre', required=True, domain="[('project_id','=',project_id)]"),
        ok = fields.boolean('Entregado / Realizado ?'),
        )

    def _get_project(self, cr, uid, context=None):
        """
        Carga el valor por defecto del campo project_id
        """
        if not context.get('active_id'):
            return False
        return context.get('active_id')    

    _defaults = dict(
        project_id = _get_project,
        )

class WizardExecKpi(osv.TransientModel):
    _name = 'wizard.project.execute.kpi'

    def action_save_exec(self, cr, uid, ids, context):
        done = False
        work_obj = self.pool.get('project.kpi.work')
        wiz = self.browse(cr, uid, ids, context)[0]
        work_amount = work_obj.get_last(cr, uid, wiz.kpi_id.id, wiz.project_id.id)        
        if wiz.amount_executed <= 0 or wiz.amount_executed < work_amount:
            raise osv.except_osv('Error', 'El avance registrado es incorrecto.')
        if wiz.amount_executed >= wiz.kpi_id.planned:
            done = True
        work_data = {'name':wiz.name, 'detail_id': wiz.kpi_id.id,
                     'project_id': wiz.project_id.id,
                     'exec_done': wiz.amount_executed, 'kpi_id': wiz.kpi_id.kpi_id.id}
        w_id = work_obj.create(cr, uid, work_data)
        self.pool.get('project.kpi.detail').write(cr, uid, wiz.kpi_id.id, {'done': done})
        return {'type': 'ir.actions.act_window_close'}

    def _compute_kpi_planned(self, cr, uid, ids, fields, args, context=None):
        w_obj = self.pool.get('project.kpi.work')
        kpi_obj = self.pool.get('project.kpi.detail')
        if context is None:
            context = {}
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = 0
            kpi_data = kpi_obj.read(cr, uid, obj.kpi_id.id, ['planned'])
            res[obj.id] = kpi_data['planned']
        return res

    def _compute_kpi_status(self, cr, uid, ids, fields, args, context=None):
        w_obj = self.pool.get('project.kpi.work')
        kpi_obj = self.pool.get('project.kpi.detail')
        if context is None:
            context = {}
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = 0
            res[obj.id] = w_obj.get_last(cr, uid, obj.kpi_id.id, obj.project_id.id)
        return res

    def _compute_kpi_date(self, cr, uid, ids, fields, args, context=None):
        w_obj = self.pool.get('project.kpi.work')
        kpi_obj = self.pool.get('project.kpi.detail')
        if context is None:
            context = {}
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = 0
            res[obj.id] = w_obj.get_last_date(cr, uid, obj.kpi_id.id, obj.project_id.id)
        return res        

    _columns = dict(
        name = fields.char('Detalle de Avance', size=128, required=True),
        project_id = fields.many2one('project.project', 'Proyecto', readonly=True),
        kpi_id = fields.many2one('project.kpi.detail', 'Indicador', required=True, readonly=True),
        user_id = fields.many2one('res.users', 'Usuario', readonly=True),
        planned = fields.function(_compute_kpi_planned, method=True, string='Planificado Según Unidad de Medida', readonly=True),
        status = fields.function(_compute_kpi_status, method=True, string='Ultimo Avance (UdM)',
                                 help="Avance realizado en la unidad de medida del indicador", readonly=True),
        last_date = fields.function(_compute_kpi_date, method=True, string='Fecha Ultimo registro', readonly=True),
        amount_executed = fields.float('Avance', help="Indicar el avance registrado de la meta (en la unidad de medida del indicador)"),
        )


    def _get_project(self, cr, uid, context):
        data = False
        if context.get('active_id', False):
            data = self.pool.get('project.kpi.detail').read(cr, uid, context.get('active_id'), ['project_id'])['project_id']
        return data[0]

    def _get_user(self, cr, uid, context=None):
        return uid

    def _get_kpi_id(self, cr, uid, context):
        return context.get('active_id', False)

    _defaults = dict(
        project_id = _get_project,
        user_id = _get_user,
        kpi_id = _get_kpi_id
        )

    def onchange_kpi(self, cr, uid, ids, kpi_id, project_id):
        w_obj = self.pool.get('project.kpi.work')
        res = {'value': {}}
        if kpi_id:
            kpi_data = self.pool.get('project.kpi.detail').read(cr, uid, kpi_id, ['planned'])
            res['value']['status'] = w_obj.get_last(cr, uid, kpi_id, project_id)
            res['value']['planned'] = kpi_data['planned']
        return res

            
class ProjectWizardActivity(osv.TransientModel):

    _name = 'project.wizard.activity'

    def action_open_activities(self, cr, uid, ids, context):
        wiz = self.browse(cr, uid, ids, context)[0]
        project_id = wiz.project_id and str(wiz.project_id.id) or False
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'gt_project_project', 'action_view_task2')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        if project_id:
            result['domain'] = "[('project_id','=',%s)]" % project_id
            cxt = eval(result['context'])
            cxt.update({'search_default_project_id': int(project_id), 'default_project_id': int(project_id)})
            result['context'] = str(cxt)
        return result        

    _columns = dict(
        project_id = fields.many2one('project.project', 'Proyecto', required=True),
        )


class ProjectWizardKpi(osv.TransientModel):
    _name = 'project.wizard.kpi'

    def action_open_kpi(self, cr, uid, ids, context):
        wiz = self.browse(cr, uid, ids, context)[0]
        project_id = wiz.project_id and str(wiz.project_id.id) or False
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'gt_project_project', 'action_view_kpi')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        if project_id:
            result['domain'] = "[('project_id','=',%s)]" % project_id
            cxt = eval(result['context'])
            cxt.update({'search_default_project_id': int(project_id), 'default_project_id': int(project_id)})
            result['context'] = str(cxt)
        return result
    
    _columns = dict(
        project_id = fields.many2one('project.project', 'Proyecto', required=True),
        )


class WizardProjectBudgetTask(osv.TransientModel):
    _name = 'wizard.project.budget.task'

    def _get_task(self, cr, uid, context=None):
        return context.get('active_id', False)

    def _get_department(self, cr, uid, context=None):
        if not context.get('active_id'):
            return False
        task = self.pool.get('project.task').browse(cr, uid, context.get('active_id'))
        return task.project_id.department_id.id

    def _get_total(self, cr, uid, context=None):
        if not context.get('active_id'):
            return False
        task = self.pool.get('project.task').browse(cr, uid, context.get('active_id'))
        return task.project_id.amount_total

    def _get_total(self, cr, uid, context=None):
        if not context.get('active_id'):
            return False
        task = self.pool.get('project.task').browse(cr, uid, context.get('active_id'))
        return task.project_id.amount_total

    def _get_project_total(self, cr, uid, context=None):
        if not context.get('active_id'):
            return False
        task = self.pool.get('project.task').browse(cr, uid, context.get('active_id'))
        return task.project_id.amount_budget

    def _get_budget_projects(self, cr, uid, context=None):
        if not context.get('active_id'):
            return False
        task = self.pool.get('project.task').browse(cr, uid, context.get('active_id'))
        return task.project_id.amount_projects

    def _get_task_amount(self, cr, uid, context=None):
        if not context.get('active_id'):
            return False
        task = self.pool.get('project.task').browse(cr, uid, context.get('active_id'))
        return task.planned_amount

    def _get_fy(self, cr, uid, context=None):
        if not context.get('active_id'):
            return False
        task = self.pool.get('project.task').browse(cr, uid, context.get('active_id'))
        return task.project_id.fy_id.id

    def _get_budget_planned(self, cr, uid, context=None):
        if not context.get('active_id'):
            return False
        task = self.pool.get('project.task').browse(cr, uid, context.get('active_id'))
        bids = []
        for bud in task.budget_planned_ids:
            data = {'acc_budget_id': bud.acc_budget_id.id,
                    'name': bud.name,
                    'planned_amount': bud.planned_amount,
                    'budget_id': bud.id}
            bids.append((0,0,data))
        return bids

    def onchange_fy(self, cr, uid, ids, fy_id):
        res = {'value': {}}
        if not fy_id:
            return res
        pids = []
        period_ids = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=',fy_id),('special','=',False)])
        for p in period_ids:
            pids.append((0,0,{'period_id': p, 'amount': 0}))
        res['value']['expense_planned_ids'] = pids
        return res    
    
    _columns = dict(
        department_id = fields.many2one('hr.department', 'Coordinación Dirección', readonly=True),
        task_id = fields.many2one('project.task', 'Actividad', readonly=True),
        amount_total= fields.float('Límite Presupuestario de Coordinación', readonly=True),
        amount_projects = fields.float('Presupuesto en Otros Proyectos', readonly=True),
        budget_project = fields.float('Presupuestado Actual de Proyecto', readonly=True),
        task_amount = fields.float('Presupuesto de Actividad', readonly=True),
        available = fields.float('Disponible', readonly=True),
        fy_id = fields.many2one('account.fiscalyear', 'Ejercicio Fiscal'),
        budget_planned_ids = fields.one2many('project.budget.plan.wiz', 'wiz_id', 'Presupuestación'),        
        expense_planned_ids = fields.one2many('project.expense.plan.wiz',  'wiz_id', 'Detalle de Gasto'),
        )

    _defaults = dict(
        task_id = _get_task,
        department_id = _get_department,
        amount_projects = _get_budget_projects,
        amount_total = _get_total,
        budget_project = _get_project_total,
        task_amount = _get_task_amount,
        budget_planned_ids = _get_budget_planned
        )    

    def check_budget(self, cr, uid, wiz):
        total = sum([b.planned_amount for b in wiz.budget_planned_ids])
        if total+wiz.budget_project > wiz.amount_total:
            raise osv.except_osv('Error', u'No puede superar el límite de la coordinación.')
        return True

    def action_save_budget(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids, context)[0]
        bud_obj = self.pool.get('project.budget.plan')
        self.check_budget(cr, uid, wiz)
        for bud in wiz.budget_planned_ids:
            data = {'name': bud.name,
                    'acc_budget_id': bud.acc_budget_id.id,
                    'planned_amount': bud.planned_amount,
                    'task_id': wiz.task_id.id}            
            if bud.budget_id:
                bud_obj.write(cr, uid, bud.budget_id.id, data)
            else:
                bud_obj.create(cr, uid, data)
        return {'type': 'ir.actions.act_window_close'}


class ProjectBudgetPlanWiz(osv.TransientModel):
    _name = 'project.budget.plan.wiz'
    _columns = dict(
        budget_id = fields.many2one('budget.item', 'Linea de Presupuesto planificado'),
        wiz_id = fields.many2one('wizard.project.budget.task', 'Asistente'),
        acc_budget_id = fields.many2one('account.analytic.account', string='Partida Presupuestaria',
                                        domain=[('type','=','normal'),('usage','=','budget'),('to_project','=',True)],
                                        required=True),
        name = fields.char('Descripción', size=128, required=True),
        planned_amount = fields.float('Monto', required=True),
        )


class ProjectExpensePlanWiz(osv.TransientModel):
    _name = 'project.expense.plan.wiz'
    _columns = dict(
        wiz_id = fields.many2one('wizard.project.budget.task', 'Asistente'),
        period_id = fields.many2one('account.period', 'Periodo', required=True),
        amount = fields.float('Monto', required=True),
        )    


class ProjectUpdateTaskWork(osv.TransientModel):
    _name = 'project.update.task.work'
    _columns = dict(
        project_id = fields.many2one('project.project', 'Proyecto', required=True),
        task_id = fields.many2one('project.task', 'Actividad', required=True),
        state = fields.selection([('draft','draft'),('select','select'),('none','none')], string='Estado'),
        date = fields.date('Fecha Registrada', readonly=True),
        new_avance = fields.float('Nuevo Avance'),
        work_id = fields.many2one('project.task.avance', 'Avance Registrado'),
        name = fields.char('Descripción', size=128, readonly=True),
        date_done = fields.datetime('Fecha de Registro', readonly=True),
        executed = fields.integer('Ejecutado', readonly=True),
        )

    _defaults = dict(
        state = 'draft',
        )

    def action_next(self, cr, uid, ids, context):
        data = {'state':'select'}
        avance_obj = self.pool.get('project.task.avance')        
        wiz = self.browse(cr, uid, ids[0], context)
        task_id = wiz.task_id.id
        work_id = avance_obj.search(cr, uid, [('task_id','=',task_id)], order='date_done DESC', limit=1)
        if not work_id:
            self.write(cr, uid, ids, {'state':'none'})
            return True
        work = avance_obj.browse(cr, uid, work_id[0])        
        data['work_id'] = work.id
        data['name'] = work.name
        data['date_done'] = work.date_done
        data['executed'] = work.executed
        self.write(cr, uid, ids, data)
        return True

    def action_update_work(self, cr, uid, ids, context=None):
        flag = False
        data = {}
        avance_obj = self.pool.get('project.task.avance')        
        wiz = self.browse(cr, uid, ids[0], context)
        to_update = wiz.work_id.id
        data = {'executed': wiz.new_avance}        
        task_id = wiz.task_id.id
        w_id = wiz.work_id.id
        work_id = avance_obj.search(cr, uid, [('task_id','=',task_id),('id','!=',w_id)], order='date_done DESC', limit=1)
        if not work_id:
            flag = True
        if flag:
            avance_obj.write(cr, uid, to_update, data)
            return {'type': 'ir.actions.act_window_close'}
        work = avance_obj.browse(cr, uid, work_id[0])        
        if work.executed > wiz.new_avance:
            raise osv.except_osv('Error', u'En avance a actualizar no puede ser menor al penúltimo registrado.')
        avance_obj.write(cr, uid, to_update, data)
        return {'type': 'ir.actions.act_window_close'}                    

    
class ProjectUpdateKpiWork(osv.TransientModel):
    _name = 'project.update.kpi.work'

    _columns = dict(
        project_id = fields.many2one('project.project', 'Proyecto', required=True),
        kpid_id = fields.many2one('project.kpi.detail', 'Indicador', required=True),
        avance_id = fields.many2one('project.kpi.work', 'Avance Registrado'),
        state = fields.selection([('draft','draft'),('select','select'),('none','none')], string='Estado'),
        kpi_id = fields.many2one('project.kpi.detail', 'Indicador', readonly=True),
        name = fields.char('Descripción', size=256, readonly=True),
        planned = fields.float('Avance Registrado', readonly=True),
        date = fields.date('Fecha Registrada', readonly=True),
        new_avance = fields.float('Nuevo Avance'),
        )

    _defaults = dict(
        state = 'draft'
        )

    def action_next(self, cr, uid, ids, context=None):
        """
        Lee el ultimo registro de avance para ser actualizado
        """
        kpi_obj = self.pool.get('project.kpi.work')
        wiz = self.browse(cr, uid, ids[0], context)
        project_id = wiz.project_id.id
        kpi_id = wiz.kpid_id.id
        work_id = kpi_obj.search(cr, uid, [('project_id','=',project_id),('detail_id','=',kpi_id)], order='date desc, id desc', limit=1)
        if not work_id:
            self.write(cr, uid, ids, {'state': 'none'})
            return True
        work = kpi_obj.browse(cr, uid, work_id)[0]
        data = {'state':'select',
                'avance_id': work_id[0],
                'kpi_id': work.detail_id.id,
                'name': work.name,
                'planned': work.exec_done,
                'date': work.date}
        self.write(cr, uid, ids, data)
        return True

    def action_update_work(self, cr, uid, ids, context=None):
        """
        Actualiza el ultimo registro de avance seleccionado
        """
        flag = False
        data = {}
        wiz = self.browse(cr, uid, ids[0], context)
        kpi_obj = self.pool.get('project.kpi.work')
        project_id = wiz.project_id.id
        kpi_id = wiz.kpid_id.id        
        to_update = wiz.avance_id.id
        new_avance = wiz.new_avance
        work_id = kpi_obj.search(cr, uid, [('project_id','=',project_id),('detail_id','=',kpi_id),('id','!=',to_update)], order='date desc, id desc', limit=1)
        if not work_id:
            flag = True
        else:
            work = kpi_obj.browse(cr, uid, work_id)[0]
        if flag:
            data = {'exec_done': new_avance}
            kpi_obj.write(cr, uid, to_update, data)
            return {'type': 'ir.actions.act_window_close'}
        if work.exec_done > new_avance:
            raise osv.except_osv('Error', u'No puede registrar un avance inferior al penúltimo registrado.')
        data['exec_done'] = new_avance
        kpi_obj.write(cr, uid, to_update, data)
        return {'type': 'ir.actions.act_window_close'}        
        
    
class ProjectImport(osv.TransientModel):

    _name = 'project.wizard.import'

    def get_value(self, cr, uid, model, field, value):
        res_value = self.pool.get(model).search(cr, uid, [(field,'=',value)], limit=1)
        if not res_value:
            raise osv.except_osv('Error', 'Modelo: %s; No se encontro %s %s'% (model,field,value))
        return res_value[0]

    def action_import_projects(self, cr, uid, ids, context):
        import xlrd
        project_obj = self.pool.get('project.project')
        wiz = self.read(cr, uid, ids, ['filed'])[0]
        data_file = wiz['filed']
        arch_xls = base64.b64decode(data_file)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_index(0)
        headers = sh.row_values(0)
        for rownum in range(sh.nrows-1):
            row_value =  sh.row_values(rownum+1)
            data = {headers[0]: row_value[0],
                    headers[1]: self.get_value(cr, uid, 'project.type', 'name', row_value[1]),
                    headers[2]: row_value[2],
                    headers[3]: self.get_value(cr, uid, 'project.program', 'name', row_value[3]),
                    headers[4]: self.get_value(cr, uid, 'project.estrategy', 'name', row_value[4]),
                    headers[5]: self.get_value(cr, uid, 'project.axis', 'name', row_value[5]),
                    headers[6]: self.get_value(cr, uid, 'hr.department', 'name', row_value[6]),
                    headers[7]: 1,
                    headers[8]: '2014-01-01',
                    headers[9]: '2014-12-31',
                    headers[10]: row_value[10],
                    headers[11]: row_value[11],
                    headers[12]: row_value[12],
                    headers[13]: row_value[13]}
            data.update(project_obj.onchange_type(cr, uid, [], data[headers[1]])['value'])
            project_id = project_obj.create(cr, uid, data)
            print "Proyecto creado con id: %s %s" % (project_id,row_value[0])
        return True

    _columns = dict(
        filed = fields.binary('Archivo de datos', required=True),
        )


class WizardMassingState(osv.TransientModel):

    _name = 'project.wizard.change.state'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
        Redefinicion de vista de form para aplicar el domain
        """
        res = super(WizardMassingState, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        doc = res['arch']
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='fy_id']"):
            node.set('domain', "[('date_stop', '<', '%s'),('state','=','draft')]" % time.strftime('%Y-%m-%d'))
        res['arch'] = etree.tostring(doc)
        return res

    def action_close(self, cr, uid, ids, context):
        """
        Metodo que implementa el cierre de los proyectos
        por ejercicio fiscal
        """
        project_obj = self.pool.get('project.project')
        wiz = self.browse(cr, uid, ids, context)[0]
        res = project_obj.search(cr, uid, [('fy_id','=',wiz.fy_id.id),('state','in',['exec','pending'])])
        #wkf stuff signal_close_poa
        if res:
            wkf_service = netsvc.LocalService("workflow")
            wkf_service.trg_validate(uid, 'project.project', res, 'signal_close_poa', cr)
        return self.write(cr, uid, ids, {'state':'ok'})#{'type': 'ir.actions.act_window_close'}        

    _columns = dict(
        fy_id = fields.many2one('account.fiscalyear', 'Ejercicio Fiscal', required=True),
        state = fields.selection([('init','init'),
                                  ('ok','ok')],required=True)
        )

    _defaults = {
        'state': 'init'
        }


class WizardProjectExpost(osv.Model):
    _name = 'wizard.project.expost'

    def action_expost(self, cr, uid, ids, context):
        """
        Metodo que implementa el registro de avance
        del indicador expost
        """
        wiz = self.browse(cr, uid, ids, context)[0]
        #planned = wiz.plan_id.planned
        self.pool.get('project.expost.plan').write(cr, uid, wiz.plan_id.id, {'executed': wiz.executed})
        return {'type': 'ir.actions.act_window_close'}
        

    _columns = {
        'project_id': fields.many2one('project.project', string='Projecto',
                                      required=True, domain=[('state','=','expost')]),
        'kpi_id': fields.many2one('project.kpi.expost', 'Indicador', required=True),
        'plan_id': fields.many2one('project.expost.plan', 'Planificado', required=True),
        'executed': fields.float('Avance')
        }

    def _check_amount(self, cr, uid, ids):
        for obj in self.browse(cr, uid, ids):
            if obj.executed < 0:
                return False
        return True

    _constraints = [(_check_amount, 'Valor debe ser mayor a cero.', ['Avance'])]


class WizardUpdateBudgetPost(osv.Model):
    _name = 'wizard.update.budget.post'

    _columns = {
        'data': fields.binary('Archivo CSV'),
        }

    def action_cuentas(self,cr, uid, ids, context=None):
        post_obj = self.pool.get('account.budget.post')
        account_obj = self.pool.get('account.account')
        with open("/home/openerp/cuentas.partidas1.csv") as ccp:
            reader = csv.reader(ccp, delimiter=';')
            no_ctas = 0
            no_posts = 0
            posts2 = 0
            for row in reader:
                account_c_ids = []
                account_p_ids = []
                childs = []
                cta = row[0].split(' ')[0]
                cxc = str(row[5])!='0' and row[5] or False
                cxp = str(row[6])!='0' and row[6] or False
                account_id = account_obj.search(cr, uid, [('code','=',cta)], limit=1)
                account_obj.write(cr, uid, account_id, {'account_c_ids': [(5)], 'account_p_ids': [(5)]})
                if account_id:
                    childs = account_obj.search(cr, uid, [('id','child_of',account_id),('type','in',['other','payable','receivable'])])
                if cxc:
                    cxc_ids = account_obj.search(cr, uid, [('id','child_of',cxc),('type','in',['other','receivable'])])
                    account_c_ids += cxc_ids
                if cxp:
                    cxp_ids = account_obj.search(cr, uid, [('id','child_of', cxp),('type','in',['other','payable'])])
                    account_p_ids += cxp_ids
                if not childs:
                    print "Cuenta no encontrada %s"% cta                    
                else:
                    print cta
                    for acc in account_c_ids:
                        account_obj.write(cr, uid, childs, {'account_c_ids': [(4, acc)]})
                    for acp in account_p_ids:
                        account_obj.write(cr, uid, childs, {'account_p_ids': [(4, acp)]})
        return True

    def action_update_budget(self, cr, uid, ids, context=None):
        post_obj = self.pool.get('account.budget.post')
        account_obj = self.pool.get('account.account')                    
        with open("/home/openerp/account2.csv", "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            no_ctas = 0
            no_posts = 0
            posts2 = 0
            for row in reader:
                account_ids = []
                cta = row[0].split(' ')[0]
                p1 = row[1]
                p2 = row[2]
                if int(p1) == 0:
                    p1 = False
                if int(p2) == 0:
                    p2 = False
                p1s = post_obj.search(cr, uid, [('code','=',p1)], limit=1)
                p2s = post_obj.search(cr, uid, [('code','=',p2)], limit=1)
                post_obj.write(cr, uid, p1s+p2s, {'account_ids':[(5)]})
                account_id = account_obj.search(cr, uid, [('code','=',cta)], limit=1)
                if account_id:
                    ex_ids = account_obj.search(cr, uid, [('id', 'child_of', account_id) ] )
                    account_ids.append(account_id[0])
                    account_ids += ex_ids
                else:
                    print "cuenta no encontrada:", cta
                if cta == '1.5.1.38.99.':
                    print "caso especial ! ", cta
                    print "hijas !: ", account_ids
                if p1s:
                    account_ids = list(set(account_ids))
                    if account_ids:
                        for acc in account_ids:
                            post_obj.write(cr, uid, p1s, {'account_ids': [(4, acc)]})
                if p2s:
                    if account_ids:
                        for acc in account_ids:
                            post_obj.write(cr, uid, p2s, {'account_ids': [(4, acc)]})
            print "cuentas no encontradas: %s, partidas: %s" % (no_ctas, no_posts)
        return True


class WizardProjectInfvialReport(osv.TransientModel):
    _name = 'wizard.project.infv.report'

    def get_weeks(self, cr, uid, context):
        meses = {1: 'ENE',
                 2 : 'FEB', 3: 'MAR',
                 4: 'ABR', 5: 'MAY',
                 6: 'JUN', 7: 'JUL',
                 8: 'AGO', 9: 'SEP',
                 10: 'OCT', 11: 'NOV',
                 12: 'DIC'}
        conf_obj = self.pool.get('project.configuration')
        res = conf_obj.search(cr, uid, [('active','=',True)], limit=1)[0]
        data = conf_obj.browse(cr, uid, res)
        import calendar
        weeks = []
        for m in range(1,13):
            res = calendar.month(2014, m)
            for i in res.split('\n')[2:-1]:
                l = i.split()
                week = '%s/%s-%s/%s' % (l[0],meses[m], l[len(l)-1], meses[m])
                weeks.append((week, week))
        return weeks

    _columns = {
        'date': fields.date('Fecha de Informe', required=True, readonly=True),
        'user_id': fields.many2one('res.users', string='Responsable',
                                   required=True),
        'type_id': fields.many2one('project.type', string='Tipo de Proyecto', readonly=True),
        'state': fields.selection([('exec', 'Ejecución'),
                                  ('exec_done', 'Ejecución Terminada'),
                                  ('exec_ok', 'Ejecución Aprobada'),
                                  ('done', 'Finalizado'),
                                  ('done_wo_end', 'Cerrado sin Terminar'),
                                  ('done_poa', 'Cerrado por Ejercicio Fiscal'),
                                  ('pending', 'Suspendido'),
                                  ('expost', 'ExPOST'),
                                  ('expost_done', 'ExPost Terminado'),
                                  ('expost_ok', 'ExPost Aprobado'),
                                  ('cancelled', 'Cancelado'),
                                  ('replaning', 'Replanificación')],
                                  string='Estado', required=True),
        'build_id': fields.many2one('project.build.program', 'Programa'),
        'build_type_id': fields.many2one('project.build.type', 'Tipo de Obra'),
        'indole_id': fields.many2one('project.build.indole', 'Indole de Obra'),
        'mode_id': fields.many2one('project.build.mode', 'Modalidad'),
        'canton_id': fields.many2one('res.country.state.canton', 'Cantón'),
        'parish_id': fields.many2one('res.country.state.parish', 'Parroquia'),
        'group_by': fields.selection([('canton_id','Cantón'),
                                      ('build_program_id','Programa'),
                                      ('none', 'Ninguno')], string='Agrupado por', required=True),
        'all_users': fields.boolean('Consolidado?', help="Esta opción permite ver todos los reporte (no aplica el filtro responsable)"),
        'months': fields.boolean('Mensual'),
        'fy_id': fields.many2one('account.fiscalyear', 'Año de Ejecución', readonly=True),
        'weeks': fields.selection(get_weeks, string='Semanas')
        }

    def _get_type(self, cr, uid, context=None):
        res = self.pool.get('project.type').search(cr, uid, [('show_fields','=',True)], limit=1)
        return res and res[0] or False

    def _get_fiscalyear(self, cr, uid, context=None):
        conf_obj = self.pool.get('project.configuration')
        res = conf_obj.search(cr, uid, [('active','=',True)], limit=1)[0]
        data = conf_obj.read(cr, uid, res, ['fiscalyear_exec_id'])
        return data['fiscalyear_exec_id'][0]

    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'type_id': _get_type,
        'user_id': lambda self, cr, uid, context: uid,
        'state': 'exec',
        'group_by': 'none',
        'fy_id': _get_fiscalyear
        }

    def build_domain(self, cr, uid, wizard):
        domain = [('type_id','=',wizard.type_id.id),('state','=',wizard.state)]
        if not wizard.all_users:
            domain.append(('user_id','=',wizard.user_id.id))
        wizard.build_id and domain.append(('build_program_id','=',wizard.build_id.id))
        wizard.build_type_id and domain.append(('build_type_id','=',wizard.build_type_id.id))
        wizard.indole_id and domain.append(('build_indole_id','=',wizard.indole_id.id))
        wizard.mode_id and domain.append(('build_mode_id','=',wizard.mode_id.id))
        wizard.canton_id and domain.append(('canton_id','=',wizard.canton_id.id))
        wizard.parish_id and domain.append(('parish_id','=',wizard.parish_id.id))
        return domain

    def print_report(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        TODO: que permita seleccionar el mes
        '''
        proj_obj = self.pool.get('project.project')
        if not context:
            context = {}
        wiz = self.browse(cr, uid, ids, context)[0]
        domain = self.build_domain(cr, uid, wiz)
        p_ids = proj_obj.search(cr, uid, domain)
        if not p_ids:
            raise osv.except_osv('Aviso', 'El usuario %s no tiene proyectos asignados.' % wiz.user_id.name)
        datas = {'ids': p_ids,
                 'model': 'project.project',
                 'date_report': wiz.date,
                 'group_by': wiz.group_by,
                 'all_users': wiz.all_users,
                 'responsable': wiz.user_id.name,
                 'week': wiz.weeks}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'project_infvial1_report',
            'model': 'project.project',
            'datas': datas,
            'nodestroy': True,                        
            }        
        
class WizardProjectInfvialReport(osv.TransientModel):
    _inherit = 'wizard.project.infv.report'
    _name = 'wizard.project.infv.s.report'

    def build_domain(self, cr, uid, wizard):
        domain = [('type_id','=',wizard.type_id.id),('state','=',wizard.state)]
        wizard.build_id and domain.append(('build_program_id','=',wizard.build_id.id))
        wizard.build_type_id and domain.append(('build_type_id','=',wizard.build_type_id.id))
        wizard.indole_id and domain.append(('build_indole_id','=',wizard.indole_id.id))
        wizard.mode_id and domain.append(('build_mode_id','=',wizard.mode_id.id))
        wizard.canton_id and domain.append(('canton_id','=',wizard.canton_id.id))
        wizard.parish_id and domain.append(('parish_id','=',wizard.parish_id.id))
        return domain
    
    def print_report(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de liquidacion de compra
        '''
        proj_obj = self.pool.get('project.project')
        if not context:
            context = {}
        wiz = self.browse(cr, uid, ids, context)[0]
        domain = self.build_domain(cr, uid, wiz)
        p_ids = proj_obj.search(cr, uid, domain)
        if not p_ids:
            raise osv.except_osv('Aviso', 'El usuario %s no tiene proyectos asignados.' % wiz.user_id.name)
        datas = {'ids': p_ids,
                 'model': 'project.project',
                 'date_report': wiz.date,
                 'group_by': wiz.group_by,
                 'all_users': wiz.all_users,
                 'responsable': wiz.user_id.name,
                 'week': wiz.weeks,
                 'fy': wiz.fy_id.name}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'project_infvial2_report',
            'model': 'project.project',
            'datas': datas,
            'nodestroy': True,                        
            }


