# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import fields, osv

class saldoAnticipoDetalle(osv.TransientModel):
    _name = 'saldo.anticipo.detalle'
    _columns = dict(
        l_id = fields.many2one('saldo.anticipo.line','Linea'),
        referencia = fields.char('Referencia',size=128),
        fecha = fields.date('Fecha'),
        monto = fields.float('Monto'),
    )
saldoAnticipoDetalle()
class saldoAnticipoLine(osv.TransientModel):
    _name = 'saldo.anticipo.line'
    _order = 'empleado_name asc'
    _columns = dict(
        line_ids = fields.one2many('saldo.anticipo.detalle','l_id','Detalle'),
        s_id = fields.many2one('saldo.anticipo','Saldo'),
        empleado_name = fields.related('employee_id','complete_name',type='char',size=128,store=True),
        employee_id = fields.many2one('hr.employee','Funcionario'),
        total_anticipos = fields.float('Total Anticipos'),
        total_devengado = fields.float('Total Devengado'),
        saldo = fields.float('Saldo'),
    )
saldoAnticipoLine()

class saldoAnticipo(osv.TransientModel):
    _name = 'saldo.anticipo'

    def print_saldo_anticipo(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        saldo = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [saldo.id], 'model': 'saldo.anticipo'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'saldo.anticipo',
            'model': 'saldo.anticipo',
            'datas': datas,
            'nodestroy': True,                        
            }            

    def load_saldo_anticipo(self, cr, uid, ids, context):
        voucher_obj = self.pool.get('account.voucher')
        rule_obj = self.pool.get('hr.salary.rule')
        advance_obj = self.pool.get('hr.payroll.advance')
        head_obj = self.pool.get('hr.ie.head')
        ie_line_obj = self.pool.get('hr.ie.line')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        line_obj = self.pool.get('saldo.anticipo.line')
        detalle_obj = self.pool.get('saldo.anticipo.detalle')
        varios_line_obj = self.pool.get('hr.varios.line')
        partner_obj = self.pool.get('res.partner')
        employee_obj = self.pool.get('hr.employee')
        rules_ids = []
        head_ids = []
        date_aux = '2017-01-01'
        for this in self.browse(cr, uid, ids):
            lines_antes = line_obj.search(cr, uid, [('s_id','=',this.id)])
            if lines_antes:
                line_obj.unlink(cr, uid, lines_antes)
            lines_detalle = detalle_obj.search(cr, uid, [])
            if lines_detalle:
                detalle_obj.unlink(cr, uid, lines_detalle)
            if this.employee_id:
                line_id_a = line_obj.create(cr, uid, {
                    's_id':this.id,
                    'employee_id':this.employee_id.id,
                })
                total_anticipo = total_devengado = total_saldo = 0
                advance_ids = advance_obj.search(cr, uid, [('employee_id','=',this.employee_id.id),('fecha_ap','>=',this.year_id.date_start),
                                                           ('state','=','aprobado'),('type','=','Anticipo'),('fecha_ap','<=',this.year_id.date_stop)])
                if advance_ids:
                    for advance_id in advance_ids:
                        advance = advance_obj.browse(cr, uid, advance_id)
                        detalle_obj.create(cr, uid, {
                            'l_id':line_id_a,
                            'referencia':advance.name,
                            'fecha':advance.fecha_ap,
                            'monto':advance.amount,
                        })
                        if not advance.category_id.id in rules_ids:
                            rules_ids.append(advance.category_id.id)
                        total_anticipo += advance.amount
                ##devengado
                ##pagos varios
                varios_ids1 = []
                varios_ids2 = []
                aux_monto_varios = 0
                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',this.employee_id.name)])
                if partner_ids:
                    varios_ids1 = varios_line_obj.search(cr, uid, [('monto_anticipo','>',0),('varios_id.state','in',('pendiente','pagado')),
                                                                  ('name','=',partner_ids[0])])
                partner_ids2 = partner_obj.search(cr, uid, [('ced_ruc','=',this.employee_id.name+'001')])
                if partner_ids2:
                    varios_ids2 = varios_line_obj.search(cr, uid, [('monto_anticipo','>',0),('varios_id.state','in',('pendiente','pagado')),
                                                                  ('name','=',partner_ids2[0])])
                varios_ids3 = varios_ids1 + varios_ids2
                if varios_ids3 and this.year_id.date_start<='2017-12-31':
                    for varios_id in varios_ids3:
                        varios = varios_line_obj.browse(cr, uid, varios_id)
                        aux_monto_varios = varios.monto_anticipo
                        detalle_obj.create(cr, uid, {
                            'l_id':line_id_a,
                            'referencia':varios.varios_id.name,
                            'fecha':varios.varios_id.period_id.date_stop,
                            'monto':aux_monto_varios,
                        })
                        total_devengado += aux_monto_varios
                ##roles
                rules_ids += rules_ids + head_ids
                payslip_line_ids = payslip_line_obj.search(cr, uid, [('employee_id','=',this.employee_id.id),('slip_id.date_from','>=',this.year_id.date_start)
                                                                     ,('salary_rule_id','in',rules_ids),('slip_id.date_from','<=',this.year_id.date_stop)])
                if payslip_line_ids:
                    for payslip_line_id in payslip_line_ids:
                        payslip_line = payslip_line_obj.browse(cr, uid, payslip_line_id)
                        total_devengado += payslip_line.total
                        aux_monto = (payslip_line.total)*(-1)
                        aux_rol = payslip_line.run_id.name + ' - ' + payslip_line.name
                        detalle_obj.create(cr, uid, {
                            'l_id':line_id_a,
                            'referencia':aux_rol,
                            'fecha':payslip_line.run_id.date_end,
                            'monto':aux_monto,
                        })
                saldo = total_anticipo - total_devengado
                line_obj.write(cr, uid, line_id_a, {
                    'total_anticipos':total_anticipo,
                    'total_devengado':total_devengado,
                    'saldo':saldo,
                })
            else:
                aux_sql = '''select employee_id from hr_payroll_advance where type='Anticipo' group by employee_id'''
                cr.execute(aux_sql)
                ids_employee = cr.fetchall()
                if ids_employee:
                    for id_employee in ids_employee:
                        advance_ids = advance_obj.search(cr, uid, [('employee_id','=',id_employee[0]),('fecha_ap','>=',this.year_id.date_start),
                                                                   ('state','=','aprobado'),('type','=','Anticipo'),('fecha_ap','<=',this.year_id.date_stop)])        
                        if advance_ids:
                            line_id_a = line_obj.create(cr, uid, {
                                's_id':this.id,
                                'employee_id':id_employee[0],
                            })
                            total_anticipo = total_devengado = total_saldo = 0
                            for advance_id in advance_ids:
                                advance = advance_obj.browse(cr, uid, advance_id)
                                detalle_obj.create(cr, uid, {
                                    'l_id':line_id_a,
                                    'referencia':advance.name,
                                    'fecha':advance.fecha_ap,
                                    'monto':advance.amount,
                                })
                                if not advance.category_id.id in rules_ids:
                                    rules_ids.append(advance.category_id.id)
                                total_anticipo += advance.amount
                            ##devengado
                            #varios
                            empleado = employee_obj.browse(cr, uid, id_employee[0])
                            aux_monto_varios = 0
                            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',empleado.name)])
                            varios_ids1 = varios_ids2 = []
                            if partner_ids:
                                varios_ids1 = varios_line_obj.search(cr, uid, [('monto_anticipo','>',0),('varios_id.state','in',('pendiente','pagado')),
                                                                               ('name','=',partner_ids[0])])
                            partner_ids2 = partner_obj.search(cr, uid, [('ced_ruc','=',empleado.name+'001')])
                            if partner_ids2:
                                varios_ids2 = varios_line_obj.search(cr, uid, [('monto_anticipo','>',0),('varios_id.state','in',('pendiente','pagado')),
                                                                               ('name','=',partner_ids2[0])])
                            varios_ids3 = varios_ids1 + varios_ids2
                            if varios_ids3 and this.year_id.date_start<='2017-12-31':
                                for varios_id in varios_ids3:
                                    varios = varios_line_obj.browse(cr, uid, varios_id)
                                    aux_monto_varios = varios.monto_anticipo
                                    detalle_obj.create(cr, uid, {
                                        'l_id':line_id_a,
                                        'referencia':varios.varios_id.name,
                                        'fecha':varios.varios_id.period_id.date_stop,
                                        'monto':aux_monto_varios,
                                    })
                                    total_devengado += aux_monto_varios
                            #rules_ids += rules_ids + head_ids
                            payslip_line_ids = payslip_line_obj.search(cr, uid, [('employee_id','=',id_employee[0]),('slip_id.date_from','>=',this.year_id.date_start)
                                                                                 ,('salary_rule_id','in',rules_ids),('slip_id.date_from','>=',this.year_id.date_stop)])
                            if payslip_line_ids:
                                for payslip_line_id in payslip_line_ids:
                                    payslip_line = payslip_line_obj.browse(cr, uid, payslip_line_id)
                                    total_devengado += payslip_line.total
                                    aux_monto = (payslip_line.total)*(-1)
                                    aux_rol = payslip_line.run_id.name + ' - ' + payslip_line.name
                                    detalle_obj.create(cr, uid, {
                                        'l_id':line_id_a,
                                        'referencia':aux_rol,
                                        'fecha':payslip_line.run_id.date_end,
                                        'monto':aux_monto,
                                    })
                            saldo = total_anticipo - total_devengado
                            line_obj.write(cr, uid, line_id_a, {
                                'total_anticipos':total_anticipo,
                                'total_devengado':total_devengado,
                                'saldo':saldo,
                            })
        return True
            

    _columns = dict(
        year_id = fields.many2one('account.fiscalyear','Anio'),
        employee_id = fields.many2one('hr.employee','Funcionario'),
        line_ids = fields.one2many('saldo.anticipo.line','s_id','Detalle'),
    )

saldoAnticipo()

