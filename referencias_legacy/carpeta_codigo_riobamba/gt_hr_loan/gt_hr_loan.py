# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from time import strftime
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser

class hr_ie_line_pago(osv.osv):
    _inherit = 'hr.ie.line'
    _columns = {
                'pago_id': fields.many2one('hr.payroll.loan', 'Prestamo', ondelete='cascade'),
                }
    
hr_ie_line_pago()

class hr_payroll_loan(osv.osv):

    _name="hr.payroll.loan"
    _description="Prestamos Empleados"

 
    def unlink(self, cr, uid, ids, *args, **kwargs):
        loan_line_obj = self.pool.get('hr.ie.line')
        for loan in self.browse(cr, uid, ids):
            if loan.state=='aprobado':
                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar prestamos validados'))
            elif loan.line_ids:
                for l in loan.line_ids:
                    if l.state!='draft':
                        raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar prestamos con pagos pendientes'))
            else:
                line_ids = loan_line_obj.search(cr, uid, [('pago_id','=',loan.id)])
                loan_line_obj.unlink(cr, uid, line_ids)
        return super(hr_payroll_loan, self).unlink(cr, uid, ids, *args, **kwargs)    

    def recompute_loan(self, cr, uid, ids, context,*args):
        if context is None:
            context = {}
        loan_pool = self.pool.get('hr.payroll.loan')
        period_pool=self.pool.get('hr.work.period.line')
        loan_line_pool=self.pool.get('hr.ie.line')
        loan_obj = loan_pool.browse(cr, uid, ids)
        aux=0
        for line_ in loan_obj:
            for line in line_.line_ids:
                if line.state=='pendiente':
                    loan_line_pool.write(cr, uid, line.id,{'state':'draft'})
                    aux=aux+line.valor
            loan_pool.create(cr, uid, {
                    'name':'Refinanciamiento '+line_.name,
                    'amount':aux,
                    'fecha_solicitud':date.today(),
                    'employee_id':line_.employee_id.id,
                    'state':'draft',
                    'category_id':line_.category_id.id,
                    'observaciones':'Prestamo Refinanciado',
                    })
        loan_pool.write(cr, uid, line_.id,{'state':'refi','amount':aux,'user_refi':uid})
        return True

    def prestamo_draft_cancel(self, cr, uid, id, *args):
        objetos = self.browse(cr, uid, id)
        line_obj=self.pool.get('hr.ie.line')
        for objeto in objetos:
            for line in objeto.line_ids:
                if line.state=="pendiente":
                    line_obj.write(cr, uid, line.id,{
                            'state':'draft',
                            })
            self.write(cr, uid, objeto.id,{
                    'state':'anulado',
                    })
        return True

    def draft_to_aprobar(self, cr, uid, id, *args):
        for obj in self.browse(cr, uid, id):
            self.write(cr, uid, id, {'fecha_ap': strftime('%Y-%m-%d'),'state':'aprobado','user_ap':uid})
            j = obj.num_pagos
            monto_pago=(obj.amount+obj.interes_valor+(obj.amount*obj.interes/100))/j
            obj_ie_line= self.pool.get('hr.ie.line')
            saldo=(obj.amount+obj.interes_valor+(obj.amount*obj.interes/100))
            #buscar los meses de pago
            ids = self.pool.get('hr.work.period.line').search(cr, uid,[('date_start','>=',obj.period_id.date_start)])
            if len(ids)<j:
                raise osv.except_osv(('Operación no permitida!'),
                                     'Debe tener generados los periodos correspondientes para el prestamo')
            for pago in range(j):
                p_line = obj_ie_line.create(cr, uid, {
                                                      'name': obj.employee_id.complete_name,
                                                      'employee_id': obj.employee_id.id,
                                                      'date': obj.fecha,
                                                      'valor': monto_pago,
                                                      'categ_id': obj.category_id.id,
                                                      'period_id': ids[pago],
                                                      'state': 'pendiente',
                                                      'pago_id': obj.id,
                                                      })

    def prestamo_draft_aprobar(self, cr, uid, id, *args):
        for obj in self.browse(cr, uid, id):
            self.write(cr, uid, id, {'fecha_ap': strftime('%Y-%m-%d'),'state':'aprobado','user_ap':uid})
            j = obj.num_pagos
            monto_pago=(obj.amount+obj.interes_valor+(obj.amount*obj.interes/100))/j
            self.write(cr, uid, id,{'a_pagar':monto_pago*j,'saldo_pendiente':monto_pago*j})
            loan_line_obj = self.pool.get('hr.payroll.loan.line')
            saldo=(obj.amount+obj.interes_valor+(obj.amount*obj.interes/100))
            bandera=False
            #for i in range(j):
            i=-1
            k=0
            segundo=obj.segunda_quincena
            while k < j:
                i+=1
                k+=1
                ids = self.pool.get('hr.work.period.line').search(cr, uid,[('date_start','>=',obj.period_id.date_start)])
                if obj.is_one==True and len(ids)<((j+1)/2):
                    raise osv.except_osv(('Operación no permitida !'), 
                                         'Debe tener generados los periodos correspondientes para el prestamo')
                elif obj.is_one==False and len(ids)<j:
                    raise osv.except_osv(('Operación no permitida !'), 
                                         'Los pagos de los prestamos deben estar dentro del presente año fiscal')
                saldo=saldo-monto_pago
                if obj.is_one and bandera==False and segundo==True:
                    p_line = loan_line_obj.create(cr, uid, {
                        'period_id':ids[i],
                        'prestamo_id':obj.id,
                        'name':'Prestamo Empresa',
                        'num_pago':k,
                        'total':monto_pago,
                        'state':'pendiente',
                        'saldo':saldo,
                        'employee_id':obj.employee_id.id,
                        })
                    bandera=False
                    segundo=False
                elif obj.is_one and bandera==False:
                    p_line = loan_line_obj.create(cr, uid, {
                        'period_id':ids[i],
                        'prestamo_id':obj.id,
                        'name':'Prestamo Empresa',
                        'num_pago':k,
                        'total':monto_pago,
                        'state':'pendiente',
                        'saldo':saldo,
                        'employee_id':obj.employee_id.id,
                        'is_one':True,
                        })
                    bandera=True
                    i-=1
                else:
                    p_line = loan_line_obj.create(cr, uid, {
                        'period_id':ids[i],
                        'prestamo_id':obj.id,
                        'name':'Prestamo Empresa',
                        'num_pago':k,
                        'total':monto_pago,
                        'state':'pendiente',
                        'saldo':saldo,
                        'employee_id':obj.employee_id.id,
                        })
                    bandera=False
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

    _columns={
        'name':fields.char('Concepto',size=50,required=True,readonly=True,
                           states={'draft':[('readonly',False)]}),
        'amount':fields.float('Cantidad',required=True,readonly=True,
                              states={'draft':[('readonly',False)]}),
        'interes_valor':fields.float('Interés(Valor)',readonly=True,states={'draft':[('readonly',False)]}),
        'interes':fields.float('Interés(%)',readonly=True,states={'draft':[('readonly',False)]}),
        'a_pagar':fields.float('A Pagar'),
        'num_pagos':fields.integer('# Pagos',readonly=True,states={'draft':[('readonly',False)]}),
        'saldo_pendiente':fields.float('Saldo Pend.'),
        'pendiente':fields.integer('# Pagos Pendiente'),
        'fecha':fields.date('Fecha Solicitud',readonly=True,states={'draft':[('readonly',False)]}),
        'fecha_ap':fields.date('Fecha Aprobacion'),
        'period_id':fields.many2one('hr.work.period.line','Periodo Inicial',
                                    help="Define desde que mes se le empieza a cobrar al empleado",readonly=True,
                                    states={'draft':[('readonly',False)]}),
        'employee_id':fields.many2one('hr.employee','Empleado',required=True,readonly=True,
                                      states={'draft':[('readonly',False)]}),
        'state':fields.selection([('draft','Borrador'),('aprobado','Aprobado'),
                                  ('refi','Refinanciado'),('anulado','Anulado')],"Estado"),        
        'pagos_ids':fields.one2many('hr.payroll.loan.line','prestamo_id','Pagos'),
        'line_ids': fields.one2many('hr.ie.line', 'pago_id', 'Detalle de Pagos'),
        'observaciones':fields.text('Observaciones'),
        'user_ap':fields.many2one('res.users','Realizado por:'),
        'user_ref':fields.many2one('res.users','Refinanciado por:'),
        'category_id':fields.many2one('hr.salary.rule','Cabecera Salarial',readonly=True,states={'draft':[('readonly',False)]}),
        'is_one':fields.boolean('Aplica a Quincenas?',
                                help="Marque esta casilla si los pagos serán generados para cada quincena",
                                readonly=True, states={'draft':[('readonly',False)]}),
        'segunda_quincena':fields.boolean('A partir segunda quincena?',
                                help="Marque esta casilla si los pagos serán generados para cada quincena, a partir de la segunda quincena",
                                readonly=True, states={'draft':[('readonly',False)]}),
         }
    

    _defaults={
        'state': 'draft',
        'fecha': strftime('%Y-%m-%d'),
        'interes':0,
        'num_pagos':1,
        }

    _constraints = [
        (_check_number,'Número invalido debe ser mayor a 0 y menor a 100',['interes']),
        ]

hr_payroll_loan()

class hr_payroll_loan_line(osv.osv):
    _name='hr.payroll.loan.line'
    _columns={
        'name':fields.char('Descripcion',size=32),
        'period_id':fields.many2one('hr.work.period.line','Periodo'),
        'prestamo_id':fields.many2one('hr.payroll.loan','Prestamo', ondelete='cascade'),
        'employee_id':fields.many2one('hr.employee','Empleado'),
        'num_pago':fields.integer('Num. Pago'),
        'total':fields.float('Total'),
        'saldo':fields.float('Saldo'),
        'state':fields.selection([('pendiente','Pendiente'),('pagado','Pagado'),('anulado','Anulado')],'Estado'),
        'is_one':fields.boolean('Aplica a Quincena?',
                                help="Indica si este valor será agregado en la quincena, de no estar activado este valor será agregado en el rol mensual"),
        'categ_id' : fields.related('prestamo_id', 'category_id', type='many2one', relation='hr.salary.rule', string='Cabecera Salarial', store=True),
        #'type' : fields.related('categ_id', 'type', type='selection', selection=[('allowance','Prima'),('deduction','Deduccion'),], string='Tipo', store=True),
        }
    
hr_payroll_loan_line()
