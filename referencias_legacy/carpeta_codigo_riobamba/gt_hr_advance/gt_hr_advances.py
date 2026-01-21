# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################

from osv import fields, osv
from time import strftime
import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser

class saldoAnticipoLineEmp(osv.TransientModel):
    _name = "saldo.anticipo.lineemp"
    _order = "name asc"
    _columns = dict(
        name = fields.char('Empleado',size=256),
        s_id = fields.many2one('saldo.anticipoemp','Saldo'),
        employee_id = fields.many2one('hr.employee','Emplado/Funcionario'),
        anticipo_id = fields.many2one('hr.payroll.advance','Anticipo'),
        monto = fields.float('Monto'),
        pagado = fields.float('Pagos'),
        saldo = fields.float('Saldo'),
    )
saldoAnticipoLineEmp()

class saldoAnticipoEmp(osv.TransientModel):
    _name = "saldo.anticipoemp"
    _columns = dict(
        date_start = fields.date('Fecha Desde'),
        date_end = fields.date('Fecha Hasta'),
        employee_id = fields.many2one('hr.employee','Empleado/Funcionario'),
        line_ids = fields.one2many('saldo.anticipo.lineemp','s_id','Detalle Anticipos'),
    )

    def imprimirSaldoAnticipo(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        saldo = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [saldo.id],
                 'model': 'saldo.anticipoemp'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'anticipoemp',
            'model': 'saldo.anticipoemp',
            'datas': datas,
            'nodestroy': True,            
        }    
    
    def calculaSaldoAnticipo(self, cr, uid, ids, context=None):
        anticipo_obj = self.pool.get('hr.payroll.advance')
        line_obj = self.pool.get('saldo.anticipo.lineemp')
        for this in self.browse(cr, uid, ids):
            sql = '''delete from saldo_anticipo_lineemp'''
            cr.execute(sql)
            if this.employee_id:
                anticipo_ids = anticipo_obj.search(cr, uid, [('employee_id','=',this.employee_id.id),('state','=','aprobado'),
                                                             ('fecha','>=',this.date_start),('fecha','<=',this.date_end)])
            else:
                anticipo_ids = anticipo_obj.search(cr, uid, [('state','=','aprobado'),('fecha','>=',this.date_start),('fecha','<=',this.date_end)])                
            if anticipo_ids:
                for anticipo_id in anticipo_ids:
                    aux_pagado = aux_saldo = 0
                    anticipo = anticipo_obj.browse(cr, uid, anticipo_id)
                    for anticipo_line in anticipo.line_ids:
                        if anticipo_line.state=='pagado':
                            aux_pagado += anticipo_line.valor
                    aux_saldo = anticipo.amount - aux_pagado
                    line_obj.create(cr, uid, {
                        's_id':this.id,
                        'name':anticipo.employee_id.complete_name,
                        'employee_id':anticipo.employee_id.id,
                        'anticipo_id':anticipo_id,
                        'monto':anticipo.amount,
                        'pagado':aux_pagado,
                        'saldo':aux_saldo,
                    }) 
        return True

saldoAnticipoEmp()

class hrAdvanceConfig(osv.Model):
    _name = 'hr.advance.config'

    def create(self, cr, uid, vals, context=None):
        config_obj = self.pool.get('hr.advance.config')
        config_ids = config_obj.search(cr, uid, [])
        if len(config_ids) > 1:
            raise osv.except_osv(('Error de configuración'), ('Solo debe tener una tabla de configuracion de anticipos'))
        line_id = super(hrAdvanceConfig, self).create(cr, uid, vals, context=None)
        return line_id    

    _columns = dict(
        name = fields.many2one('account.account','Cta. Contable',required=True),
        journal_id = fields.many2one('account.journal','Diario',required=True),
        max_month = fields.integer('Num. Maximo Meses',required=True),
        max_number = fields.integer('Num. Maximo RMU',required=True),
        )

hrAdvanceConfig()

class consolidaDescuento(osv.TransientModel):
    _name = 'consolida.descuento'
    _columns = dict(
        period_id = fields.many2one('hr.work.period.line','Periodo'),
        rule_id = fields.many2one('hr.salary.rule','Rubro'),
    )

    def consolidaDescuento(self, cr, uid, ids, context=None):
        head_obj = self.pool.get('hr.ie.head')
        line_obj = self.pool.get('hr.ie.line')
        for this in self.browse(cr, uid, ids):
            line_ids = line_obj.search(cr, uid, [('categ_id','=',this.rule_id.id),('period_id','=',this.period_id.id)])
            if line_ids:
                head_ids = head_obj.search(cr, uid, [('name','=',this.rule_id.id),('period_id','=',this.period_id.id)])
                if head_ids:
                    head_id = head_ids[0]
                else:
                    head_id = head_obj.create(cr, uid, {
                        'name':this.rule_id.id,
                        'period_id':this.period_id.id,
                    })
                for line_id in line_ids:
                    line_obj.write(cr, uid, line_id,{
                        'head_id':head_id,
                    })
        return True

consolidaDescuento()
class hr_ie_line_pago_adv(osv.osv):
    _inherit = 'hr.ie.line'

#    def _get_order(self, cr, uid, ids, context=None):
#        result = {}
#        for line in self.pool.get('hr.ie.line').browse(cr, uid, ids, context=context):
#            result[line.pago_adv_id.id] = True
#        return result.keys()       

    _columns = {
        'pago_adv_id': fields.many2one('hr.payroll.advance', 'Anticipo', 
                                       ondelete='cascade'),
        }
    
hr_ie_line_pago_adv()

class hr_payroll_advance(osv.osv):

    _name="hr.payroll.advance"
    _description="Anticipos Empleados"
    
    def write(self, cr, uid, ids,vals,context=None):
        line_obj = self.pool.get('hr.ie.line')
        contract_obj = self.pool.get('hr.contract')
        for this in self.browse(cr, uid, ids):
            if vals.has_key('category_id'):
                for line in this.line_ids:
                    line_obj.write(cr, uid, line.id,{
                        'categ_id':vals['category_id'],
                    })
            if vals.has_key('contract_id'):
                contrato = contract_obj.browse(cr, uid,vals['contract_id'])
                for line in this.line_ids:
                    line_obj.write(cr, uid, line.id,{
                        'employee_id':contrato.employee_id.id,
                    })
        return super(hr_payroll_advance, self).write(cr, uid, ids, vals,context=None)
 
    def unlink(self, cr, uid, ids, *args, **kwargs):
        advance_line_obj = self.pool.get('hr.ie.line')
        for advance in self.browse(cr, uid, ids):
            raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar anticipos, puede anularlos'))
#            if advance.state=='aprobado':
#                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar anticipos validados'))
#            elif advance.line_ids:
#                for l in advance.line_ids:
#                    if l.state!='draft':
#                        raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar anticipos con pagos pendientes'))
#            else:
#                line_ids = advance_line_obj.search(cr, uid, [('pago_adv_id','=',advance.id)])
#                advance_line_obj.unlink(cr, uid, line_ids)
        return super(hr_payroll_advance, self).unlink(cr, uid, ids, *args, **kwargs)    

    def recompute_advance(self, cr, uid, ids, context,*args):
        if context is None:
            context = {}
        advance_pool = self.pool.get('hr.payroll.advance')
        period_pool=self.pool.get('hr.work.period.line')
        advance_line_pool=self.pool.get('hr.ie.line')
        advance_obj = advance_pool.browse(cr, uid, ids)
        aux=0
        for line_ in advance_obj:
            for line in line_.line_ids:
                if line.state=='pendiente':
                    advance_line_pool.write(cr, uid, line.id,{'state':'draft'})
                    aux=aux+line.valor
            advance_pool.create(cr, uid, {
                'name':'Refinanciamiento '+line_.name,
                'amount':aux,
                'fecha_solicitud':date.today(),
                'contract_id':line_.contract_id.id,
                'employee_id':line_.contract_id.employee_id.id,
                'state':'draft',
                'category_id':line_.category_id.id,
                'observaciones':'Prestamo Refinanciado',
                'type':'Anticipo',
            })
        return True

    def prestamo_return_draft(self, cr, uid, id, *args):
        context = {}
        objetos = self.browse(cr, uid, id)
        line_obj=self.pool.get('hr.ie.line')
        advance_obj = self.pool.get('hr.payroll.advance')
        for objeto in objetos:
            for line in objeto.line_ids:
                if line.state=="pendiente":
                    line_obj.write(cr, uid, line.id,{
                            'state':'draft',
                            })
            advance_obj.write(cr, uid, id,{
                    'state':'draft',
                    },context)
        return True

    def prestamo_draft_cancel(self, cr, uid, id, *args):
        context = {}
        objetos = self.browse(cr, uid, id)
        line_obj=self.pool.get('hr.ie.line')
        line_rol_obj = self.pool.get('hr.payslip.line')
        advance_obj = self.pool.get('hr.payroll.advance')
        for objeto in objetos:
            for line in objeto.line_ids:
                if line.state=="pendiente":
                    line_rol_ids = line_rol_obj.search(cr, uid, [('salary_rule_id','=',objeto.category_id.id),('period_id','=',line.period_id.id),
                                                                 ('employee_id','=',line.employee_id.id)])
                    if not line_rol_ids:
                        line_obj.write(cr, uid, line.id,{
                            'state':'draft',
                        })
                        line_obj.unlink(cr, uid, [line.id])
            advance_obj.write(cr, uid, id,{
                    'state':'anulado',
                    },context)
        return True

    def draft_to_solicitar(self, cr, uid, id, *args):
        advance_obj = self.pool.get('hr.payroll.advance')
        advance_obj.write(cr, uid, id, {
                'state':'Solicitado'
                })
        return True


    def _create_account_journal(self, cr, uid, ids, contract, period, category, amount,context=None):
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        journal_obj = self.pool.get('account.journal')
        config_obj = self.pool.get('hr.account.configuration')
        journal_ids = journal_obj.search(cr, uid, [('type','=','bank')],limit=1)
        if not journal_ids:
            raise osv.except_osv(('Operación no permitida!'),
                                 'Debe tener por lo menos un diario de banco')
        if not contract.employee_id.bank_account_id.partner_id.id:
            raise osv.except_osv(('Operación no permitida!'),
                                 'El empleado debe tener asociado un proveedor')
        partner_id = contract.employee_id.bank_account_id.partner_id.id    
        journal = journal_obj.browse(cr, uid, journal_ids[0])
        account_id = journal.default_debit_account_id.id
        txt = 'Antic. Salario: ' + contract.employee_id.complete_name + '-' + period.name,

        voucher_id = voucher_obj.create(cr, uid, {
                'name':txt,
                'partner_id':partner_id,
                'period_id':period.id,
                'journal_id':journal_ids[0],
                'account_id':journal.default_debit_account_id.id,
                'reference':txt,
                'comment':txt,
                'narration':txt,
                'amount':amount,
                'type':'payment',
                'internal_type':'Anticipo Sueldo',
                'extra_type':'advances',
                })
        return True

    def draft_to_aprobar(self, cr, uid, id, *args):
        context = {}
        ie_obj= self.pool.get('hr.ie.line')
        aux_suma = 0
        for obj in self.browse(cr, uid, id):
            for line in obj.line_ids:
                aux_suma += line.valor
#            if aux_suma != obj.amount:
#                raise osv.except_osv(('Error de usuario'), ('El valor del anticipo debe ser igual al detalle de descuentos'))
            for line in obj.line_ids:
                ie_obj.write(cr, uid, line.id,{
                    'state':'pendiente',
                })
            self.write(cr, uid, id, {'fecha_ap': strftime('%Y-%m-%d'),'state':'aprobado','user_ap':uid},context)
        return True

    def draft_to_compute(self, cr, uid, id, *args):
        obj_ie_line= self.pool.get('hr.ie.line')
        for obj in self.browse(cr, uid, id):
            lineas_antes = obj_ie_line.search(cr, uid, [('pago_adv_id','=',obj.id)])
            if lineas_antes:
                obj_ie_line.unlink(cr, uid, lineas_antes,context={})
            j = obj.num_pagos
            j1 = obj.num_pagos * obj.pagos_por_mes
            monto_pago=(obj.amount+obj.interes_valor+(obj.amount*obj.interes/100))/j1
            print "montooo", monto_pago
            saldo=(obj.amount+obj.interes_valor+(obj.amount*obj.interes/100))
            #buscar los meses de pago
            total_pagos_aux = obj.num_pagos * obj.pagos_por_mes
            ids = self.pool.get('hr.work.period.line').search(cr, uid,[('date_start','>=',obj.period_id.date_start)])
            if len(ids)<j:
                raise osv.except_osv(('Operación no permitida!'),
                                     'Debe tener generados los periodos correspondientes para el anticipo')
            aux_date = obj.fecha 
            aux_sum_dias = 30/obj.pagos_por_mes
            aux_sec = aux_total_linea = 0
            for pago in range(j-1):
                #crear pagos mes -1
                if obj.pagos_por_mes>1:
                    #aux_sec += 1
                    #etiqueta = 'Pago '+str(aux_sec)+'/'+str(total_pagos_aux)
                    monto2 = 0
                    k = obj.pagos_por_mes
                    monto2 = monto_pago#monto_pago/k
                    for pago_2 in range(k):
                        aux_sec += 1
                        etiqueta = 'Pago '+str(aux_sec)+'/'+str(total_pagos_aux)
                        p_line = obj_ie_line.create(cr, uid, {
                            'name': obj.employee_id.complete_name,
                            'employee_id': obj.employee_id.id,
                            'date': aux_date,
                            'valor': float("%.2f" % monto_pago),
                            'categ_id': obj.category_id.id,
                            'period_id': ids[pago],
                            'state': 'draft',
                            'pago_adv_id': obj.id,
                            'label':etiqueta,
                        })
                        aux_total_linea += float("%.2f" % monto2)
                        ultima_linea = p_line
                        date = datetime.strptime(aux_date, "%Y-%m-%d")
                        aux_fin = date + timedelta(days=aux_sum_dias)
                        aux_date = aux_fin.strftime("%Y-%m-%d")  
                else:
                    aux_sec += 1
                    etiqueta = 'Pago '+str(aux_sec)+'/'+str(total_pagos_aux)
                    p_line = obj_ie_line.create(cr, uid, {
                        'name': obj.employee_id.complete_name,
                        'employee_id': obj.employee_id.id,
                        'date': aux_date,
                        'valor': float("%.2f" % monto_pago),
                        'categ_id': obj.category_id.id,
                        'period_id': ids[pago],
                        'state': 'draft',
                        'pago_adv_id': obj.id,
                        'label':etiqueta,
                    })  
                    aux_total_linea += float("%.2f" % monto_pago)
                    ultima_linea = p_line
                    date = datetime.strptime(aux_date, "%Y-%m-%d")
                    aux_fin = date + timedelta(days=aux_sum_dias)
                    aux_date = aux_fin.strftime("%Y-%m-%d")  
            if not obj.pagos_por_mes>1:
                aux_sec += 1
                etiqueta = 'Pago '+str(aux_sec)+'/'+str(total_pagos_aux)
                aux_val = obj.amount-(float("%.2f" % monto_pago)*(j-1))
                p_line = obj_ie_line.create(cr, uid, {
                    'name': obj.employee_id.complete_name,
                    'employee_id': obj.employee_id.id,
                    'date': aux_date,
                    'valor': monto_pago,#aux_val,
                    'categ_id': obj.category_id.id,
                    'period_id': ids[j-1],
                    'state': 'draft',
                    'pago_adv_id': obj.id,
                    'label':etiqueta,
                })
                aux_total_linea += float("%.2f" % monto_pago)
                ultima_linea = p_line
                date = datetime.strptime(aux_date, "%Y-%m-%d")
                aux_fin = date + timedelta(days=aux_sum_dias)
                aux_date = aux_fin.strftime("%Y-%m-%d")  
            else:
                k = obj.pagos_por_mes
                monto2 = monto_pago/k
                for pago_2 in range(k):
                    aux_sec += 1
                    etiqueta = 'Pago '+str(aux_sec)+'/'+str(total_pagos_aux)
                    p_line = obj_ie_line.create(cr, uid, {
                        'name': obj.employee_id.complete_name,
                        'employee_id': obj.employee_id.id,
                        'date': aux_date,
                        'valor': float("%.2f" % monto_pago),
                        'categ_id': obj.category_id.id,
                        'period_id': ids[j-1],
                        'state': 'draft',
                        'pago_adv_id': obj.id,
                        'label':etiqueta,
                    })
                    aux_total_linea += float("%.2f" % monto_pago)
                    ultima_linea = p_line
                    date = datetime.strptime(aux_date, "%Y-%m-%d")
                    aux_fin = date + timedelta(days=aux_sum_dias)
                    aux_date = aux_fin.strftime("%Y-%m-%d")
            if aux_total_linea>obj.amount:
                diferencia = aux_total_linea - obj.amount
                line_last = obj_ie_line.browse(cr, uid, ultima_linea)
                aux = line_last.valor
                obj_ie_line.write(cr, uid, ultima_linea,{'valor':aux-diferencia})
            elif aux_total_linea<obj.amount:
                diferencia = obj.amount - aux_total_linea
                line_last = obj_ie_line.browse(cr, uid, ultima_linea)
                aux = line_last.valor
                obj_ie_line.write(cr, uid, ultima_linea,{'valor':aux+diferencia})
            return True

    def onchange_amount(self, cr, uid, ids, amount, context=None):
        res={}
        for aux in self.browse(cr,uid,ids):
            res.update({
                    'saldo_pendiente':aux.a_pagar,
                    })
        return {
            'value':res
        }

    def onchange_interes(self, cr, uid, ids, interes, context=None):
        res={}
        for aux in self.browse(cr,uid,ids):
            res.update({
                    'a_pagar':aux.amount+(interes/100*aux.amount),
                    'saldo_pendiente':aux.amount+(interes/100*aux.amount),
                    })
        return {
            'value':res
        }
        
    def _check_number(self,cr,uid,ids):
        for aux in self.browse(cr,uid,ids):
            if aux.interes<0 or aux.interes>100:
                return False
        return True

    def _check_amount(self,cr,uid,ids):
        aux_suma = 0
        result = False
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                aux_suma += line.valor
            if aux_suma == this.amount:
                result = True
        return result

    def _check_pagos(self,cr,uid,ids):
        return True

    def onchange_garante(self, cr, uid, ids, garante_id, context={}):
        advance_obj = self.pool.get('hr.payroll.advance')
        for this in self.browse(cr, uid, ids):
            advance_ids = advance_obj.search(cr, uid, [('state','=','aprobado'),('id','!=',this.id),('garante_id','=',garante_id)])
            if advance_ids:
                raise osv.except_osv(('Error de usuario'), ('El garante seleccionado ya esta en otro anticipo, solo puede estar como garante en uno a la vez'))
        return {}

    def _get_uid(self, cr, uid, ids, context=None):
        return uid

    def _get_contract(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        emp_ids = emp_obj.search(cr, uid, [('user_id','=',uid)],limit=1)
        if emp_ids:
            contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp_ids[0])],limit=1)
            if contract_ids:
                return contract_ids[0]
            else:
                return False
                #raise osv.except_osv(('Error de usuario'), ('No existe contrato activo para el empleado'))
        else:
            return False

    def _amount_prestamo(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'saldo_pendiente': 0.0,
                }
            aux_saldo = 0
            for line_line in line.line_ids:
                if line_line.state=='pendiente':
                    aux_saldo += line_line.valor
            res[line.id]['saldo_pendiente'] = aux_saldo
            return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('hr.ie.line').browse(cr, uid, ids, context=context):
            if line:
                if line.pago_adv_id:
                    result[line.pago_adv_id.id] = True
        return result.keys()

    _columns={
        'garante_id':fields.many2one('hr.employee','Garante'),
        'type':fields.selection([('Anticipo','Anticipo'),('Planificado','Planificado')],'Tipo'),
        'name':fields.char('Concepto',size=50,required=True,readonly=True,
                           states={'draft':[('readonly',False)]}),
        'amount':fields.float('Cantidad',required=True,readonly=True,
                              states={'draft':[('readonly',False)]}),
        'interes_valor':fields.float('Interés(Valor)'),
        'interes':fields.float('Interés(%)'),
        'a_pagar':fields.float('A Pagar'),
        'num_pagos':fields.integer('# Pagos',readonly=True,
                                   states={'draft':[('readonly',False)]}),
        'pagos_por_mes':fields.integer('# Pagos Por Mes',readonly=True,help="Use esta opcion solo si hace roles semanales",
                                states={'draft':[('readonly',False)]}),
        'saldo_pendiente':fields.float('Saldo Pend.'),
#        'saldo_pendiente':fields.function(_amount_prestamo, string='Saldo', multi="tl",store={
#            'hr.ie.line': (_get_order, ['state'], 10)}),
        'pendiente':fields.integer('# Pagos Pendiente'),
        'fecha':fields.date('Fecha Solicitud',readonly=True,
                            states={'draft':[('readonly',False)]}),
        'fecha_ap':fields.date('Fecha Aprobacion'),
        'period_id':fields.many2one('hr.work.period.line','Periodo Inicial',
                                    help="Define desde que mes se le empieza a cobrar al empleado",readonly=True,
                                    states={'draft':[('readonly',False)]}),
        'contract_id':fields.many2one('hr.contract','Empleado',required=True,readonly=True,
                                      states={'draft':[('readonly',False)]}),
        'employee_id' :fields.related('contract_id', 'employee_id', type='many2one', relation='hr.employee',
                                  string='Empleado', store=True, readonly=True),
#        'employee_id':fields.many2one('hr.employee','Empleado',required=True,readonly=True,
#                                      states={'draft':[('readonly',False)]}),
        'state':fields.selection([('draft','Borrador'),('Solicitado','Solicitado'),('aprobado','Aprobado'),
                                  ('refi','Refinanciado'),('anulado','Anulado')],"Estado"),        
        'pagos_ids':fields.one2many('hr.payroll.advance.line','advance_id','Pagos'),
        'line_ids': fields.one2many('hr.ie.line', 'pago_adv_id', 'Detalle de Pagos'),
        'observaciones':fields.text('Observaciones'),
        'user_ap':fields.many2one('res.users','Realizado por:'),
        'user_id':fields.many2one('res.users','Creado por:'),
        'user_ref':fields.many2one('res.users','Refinanciado por:'),
        'category_id':fields.many2one('hr.salary.rule','Cabecera Salarial',readonly=True,states={'draft':[('readonly',False)]}),
        'is_one':fields.boolean('Aplica a Quincenas?',
                                help="Marque esta casilla si los pagos serán generados para cada quincena",
                                readonly=True, states={'draft':[('readonly',False)]}),
         }
    

    _defaults={
        'state': 'draft',
        'fecha': strftime('%Y-%m-%d'),
        'interes':0,
        'num_pagos':1,
        'user_id':_get_uid,
#        'contract_id': _get_contract,
        'pagos_por_mes':1,
        }

    _constraints = [
        (_check_number,'Número invalido debe ser mayor a 0 y menor a 100',['interes']),
#        (_check_garante,'El garante ya esta en otro anticipo',['Garante']),
#        (_check_pagos,'Cantidad de pagos invalido debe ser maximo',['Num. Pagos']),
        ]

hr_payroll_advance()

class hr_payroll_advance_line(osv.osv):
    _name='hr.payroll.advance.line'
    _columns={
        'name':fields.char('Descripcion',size=32),
        'period_id':fields.many2one('hr.work.period.line','Periodo'),
        'advance_id':fields.many2one('hr.payroll.advance','Prestamo', ondelete='cascade'),
        'employee_id':fields.many2one('hr.employee','Empleado'),
        'num_pago':fields.integer('Num. Pago'),
        'total':fields.float('Total'),
        'saldo':fields.float('Saldo'),
        'state':fields.selection([('pendiente','Pendiente'),('pagado','Pagado'),
                                  ('anulado','Anulado')],'Estado'),
        'is_one':fields.boolean('Aplica a Quincena?',
                                help="Indica si este valor será agregado en la quincena, de no estar activado este valor será agregado en el rol mensual"),
        'categ_id' : fields.related('advance_id', 'category_id', 
                                    type='many2one', relation='hr.salary.rule', 
                                    string='Cabecera Salarial', store=True),
        #'type' : fields.related('categ_id', 'type', type='selection', selection=[('allowance','Prima'),('deduction','Deduccion'),], string='Tipo', store=True),
        }
    
hr_payroll_advance_line()
