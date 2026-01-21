# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from time import strftime, strptime
import decimal_precision as dp
from osv import osv, fields

_STATE = [('draft','Borrador'),('pendiente','Aprobado/Pendiente Pago'),('pagado','Pagado')]

class hrContractQuincena(osv.Model):
    _inherit = 'hr.contract'
    _columns = dict(
        quincena = fields.boolean('Recibe Quincena'),
    )
hrContractQuincena()

class hrQuincenaLineLine(osv.Model):
    _name = 'hr.quincena.line.line'
    _columns = dict(
        quincena_id = fields.related('q_id','quincena_id',type="many2one",relation='hr.quincena',string="Quincena",store=True),
        period_id = fields.related('q_id','period_id',type="many2one",relation='hr.work.period.line',string="Periodo",store=True),
        name = fields.char('desc',size=32),
        q_id = fields.many2one('hr.dept.line','Detalle',ondelete='cascade'),
        tipo_id = fields.related('contract_id','subtype_id',type="many2one",relation='hr.contract.type.type',string="Tipo Rol",store=True),
        program_id = fields.related('contract_id','program_id',type="many2one",relation='project.program',string="Programa",store=True),
        contract_id = fields.many2one('hr.contract','Contrato'),
        employee_id = fields.many2one('hr.employee','Empleado',required=True, 
                                      readonly=True),
        valor = fields.float('Valor',required=True,
                             readonly=True, digits_compute=dp.get_precision('Account')),
    )
hrQuincenaLineLine()
class hrDeptLine(osv.osv):
    _name = 'hr.dept.line'

    def _amount_total(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            aux = 0
            for line in this.line_ids:
                aux += line.valor
            res[this.id] = aux
        return res

    _columns = dict(
        period_id = fields.related('dept_id','period_id',type="many2one",relation='hr.work.period.line',string="Periodo",store=True),
        quincena_id = fields.related('dept_id','quincena_id',type="many2one",relation='hr.quincena',string="Quincena",store=True),
        name = fields.char('desc',size=16),
        dept_id = fields.many2one('hr.quincena.line','Quincena',ondelete='cascade'),
        department_id = fields.many2one('hr.department','Departamento'),
        line_ids = fields.one2many('hr.quincena.line.line','q_id','Detalle Empleado'),
        valor = fields.function(_amount_total, string='Total', type="float",store=True),
#        valor = fields.float('Total'),
    )
    

hrDeptLine()    

class hrQuincenaLine(osv.osv):
    _name = 'hr.quincena.line'
    _description = 'Detalle Quincena'
    _order = 'name'

    def _validar_mayor_cero(self, cr, uid, ids, context=None):
#        obj = self.browse(cr, uid, ids[0], context=context)
#        if obj.valor <= 0:
#            return False
        return True

    def _amount_total(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            aux = 0
            for line in this.line_ids:
                aux += line.valor
            res[this.id] = aux
        return res           

    _columns = dict(
        name = fields.char('Desc',size=64),
        quincena_id = fields.many2one('hr.quincena','Quincena',ondelete='cascade'),
        valor = fields.function(_amount_total, string='Total', type="float",store=True),
        #       valor = fields.float('Valor',required=True,
        #                            readonly=True),
        #       department_id = fields.many2one('hr.department','Departamento'),
       program_id = fields.many2one('project.program','Programa'),
       line_ids = fields.one2many('hr.dept.line','dept_id','Detalle Depto'),
       period_id = fields.related('quincena_id','period_id',type="many2one",relation='hr.work.period.line',string="Periodo",store=True),
       )

    _constraints = [
        (_validar_mayor_cero, 'Los valores deben ser superiores a cero', ['valor']),
    ]
   
hrQuincenaLine()

class quincenaEmpleado(osv.Model):
    _name = 'quincena.empleado'
    _columns = dict(
        p_id = fields.many2one('quincena.programa','Programa'),
        contract_id = fields.many2one('hr.contract','Contrato'),
        valor = fields.float('Monto', digits_compute=dp.get_precision('Account')),
        programa_id = fields.related('p_id','program_id',type='many2one',relation='project.program',string="Programa",store=True),
    )
quincenaEmpleado()
class quincenaPrograma(osv.Model):
    _name = 'quincena.programa'
    
    def _amount_total(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            aux = 0
            for line in this.line_ids:
                aux += line.valor
            res[this.id] = aux
        return res

    _columns = dict(
        t_id = fields.many2one('quincena.tipo','Tipo'),
        line_ids = fields.one2many('quincena.empleado','p_id','Detalle Empleado'),
        total = fields.function(_amount_total, string='Total', type="float",store=True),
        #total = fields.float('Total Programa'),
        program_id = fields.many2one('project.program','Programa'),
    )
quincenaPrograma()
class quincenaTipo(osv.Model):
    _name = 'quincena.tipo'

    def _amount_total(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            aux = 0
            for line in this.line_ids:
                aux += line.total
            res[this.id] = aux
        return res

    _columns = dict(
        q_id = fields.many2one('hr.quincena','Quincena'),
        line_ids = fields.one2many('quincena.programa','t_id','Detalle'),
        tipo_id = fields.many2one('hr.contract.type.type','Tipo Rol'),
        total = fields.function(_amount_total, string='Total', type="float",store=True),
#        total = fields.float('Total Rol'),
    )
quincenaTipo()
class hrQuincena(osv.osv):
    _name = 'hr.quincena'
    _description = 'Quincenas'
    _order = 'name'

    _columns = dict(
        tipo_id = fields.many2one('hr.contract.type.type','Tipo Rol'),
        name = fields.char('Descripcion',size=64,required=True,states={'draft': [('readonly', False)]}),
        period_id = fields.many2one('hr.work.period.line','Periodo',required=True,readonly=True,
                                    states={'draft': [('readonly', False)]}),
        observaciones = fields.char('Observaciones',size=128,readonly=True,states={'draft': [('readonly', False)]}),
        total = fields.float('Total', digits_compute=dp.get_precision('Account')),
        line_ids2 = fields.one2many('quincena.tipo','q_id','Detalle Tipo Rol'),
        line_ids = fields.one2many('hr.quincena.line','quincena_id','Detalle',readonly=True,states={'draft': [('readonly', False)]}),
        state = fields.selection(_STATE,'Estado'),
        journal_id = fields.many2one('account.journal','Cuenta de banco pago'),
        move_id = fields.many2one('account.move','Comprobante contable',readonly=True),
        )

    def print_quincena(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.hr.quincena'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.quincena',
            'model': 'hr.quincena',
            'datas': datas,
            'nodestroy': True,                        
            }

    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.state!='draft':
                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar, solo puede realizar esta operacion en estado Borrador'))
        return super(hrQuincena, self).unlink(cr, uid, ids, *args, **kwargs)
    

    def load_tipo(self, cr, uid, ids, context=None):
        contract_obj=self.pool.get('hr.contract')
        program_obj = self.pool.get('project.program')
        quincena_obj = self.pool.get('hr.quincena')
        tipo_obj = self.pool.get('quincena.tipo')
        line_programa_obj = self.pool.get('quincena.programa')
        empleado_line_obj =self.pool.get('quincena.empleado')
        type_obj = self.pool.get('hr.contract.type.type')
        line_line_obj = self.pool.get('hr.quincena.line.line')
        auxtotal_quincena = 0
        for this in self.browse(cr, uid, ids, context=context):
            old_line_ids = tipo_obj.search(cr, uid, [('q_id','=',this.id)], context=context)
            if old_line_ids:
                tipo_obj.unlink(cr, uid, old_line_ids, context=context)
            #sacar los tipos de rol
            tipo_ids = type_obj.search(cr, uid, [])
#            line_line_ids = line_line_obj.search(cr, uid, [('quincena_id','=',this.id)]) 
            if tipo_ids:
                for tipo_id in tipo_ids:
                    program_ids = []
                    line_line_ids = line_line_obj.search(cr, uid, [
                                                                 ('quincena_id','=',this.id),
                                                                 ('tipo_id','=',tipo_id)])
                    if line_line_ids:
                        tipo2_id = tipo_obj.create(cr, uid, {
                            'q_id':this.id,
                            'tipo_id':tipo_id,
                        })
                        aux = 150
                        for line_line_id in line_line_ids:
                            line_line = line_line_obj.browse(cr, uid, line_line_id)
                            contrato = line_line.contract_id
                            if contrato.program_id.id:
                                if not contrato.program_id.id in program_ids:
                                    program_ids.append(contrato.program_id.id)
                            else:
                                raise osv.except_osv(('Error de configuracion'), 
                                                     ('El contrato del empleado no tienen programa asignado:  '+contrato.employee_id.complete_name))
                        for program_id in program_ids:
                            programa = program_obj.browse(cr, uid, program_id)
                            line_programa_id = line_programa_obj.create(cr, uid, {
                                'name':programa.name,
                                't_id':tipo2_id,
                                'program_id':programa.id,
                            })
                            line_line_ids_2 = line_line_obj.search(cr, uid, [('quincena_id','=',this.id),
                                                                             ('program_id','=',program_id),
                                                                             ('tipo_id','=',tipo_id)])
                            for line_line_id_2 in line_line_ids_2:
                                aux2 = 150
                                line_line_2 = line_line_obj.browse(cr, uid, line_line_id_2)
                                contrato = line_line_2.contract_id
                                if contrato.porcentaje_anticipo>0:
                                    aux2 = (contrato.wage)*(contrato.porcentaje_anticipo)/(100.00)
                                empleado_line_obj.create(cr, uid,{
                                    'p_id':line_programa_id,
                                    'contract_id':contrato.id,
                                    'valor':line_line_2.valor,
                                })
            else:
                raise osv.except_osv(('Aviso !'), ('No existen contratos de quincena o no estan activos'))

    def load_tipo2(self, cr, uid, ids, context=None):
        contract_obj=self.pool.get('hr.contract')
        program_obj = self.pool.get('project.program')
        quincena_obj = self.pool.get('hr.quincena')
        tipo_obj = self.pool.get('quincena.tipo')
        line_programa_obj = self.pool.get('quincena.programa')
        empleado_line_obj =self.pool.get('quincena.empleado')
        type_obj = self.pool.get('hr.contract.type.type')
        auxtotal_quincena = 0
        for this in self.browse(cr, uid, ids, context=context):
            old_line_ids = tipo_obj.search(cr, uid, [('q_id','=',this.id)], context=context)
            if old_line_ids:
                tipo_obj.unlink(cr, uid, old_line_ids, context=context)
            #sacar los tipos de rol
            tipo_ids = type_obj.search(cr, uid, [])
            if tipo_ids:
                for tipo_id in tipo_ids:
                    program_ids = []
                    contrato_ids = contract_obj.search(cr, uid, [('activo','=',True),
                                                                 ('quincena','=',True),
                                                                 ('subtype_id','=',tipo_id)])
                    if contrato_ids:
                        tipo2_id = tipo_obj.create(cr, uid, {
                            'q_id':this.id,
                            'tipo_id':tipo_id,
                        })
                        aux = 150
                        for contrato_id in contrato_ids:
                            contrato = contract_obj.browse(cr, uid, contrato_id)
                            if contrato.program_id.id:
                                if not contrato.program_id.id in program_ids:
                                    program_ids.append(contrato.program_id.id)
                            else:
                                raise osv.except_osv(('Error de configuracion'), 
                                                     ('El contrato del empleado no tienen programa asignado:  '+contrato.employee_id.complete_name))
                        for program_id in program_ids:
                            programa = program_obj.browse(cr, uid, program_id)
                            line_programa_id = line_programa_obj.create(cr, uid, {
                                'name':programa.name,
                                't_id':tipo2_id,
                                'program_id':programa.id,
                            })
                            contrato_ids_2 = contract_obj.search(cr, uid, [('activo','=',True),
                                                                           ('quincena','=',True),
                                                                           ('program_id','=',program_id),
                                                                           ('subtype_id','=',tipo_id)])
                            for contrato_id_2 in contrato_ids_2:
                                aux2 = 150
                                contrato = contract_obj.browse(cr, uid, contrato_id_2)
                                if contrato.porcentaje_anticipo>0:
                                    aux2 = (contrato.wage)*(contrato.porcentaje_anticipo)/(100.00)
                                empleado_line_obj.create(cr, uid,{
                                    'p_id':line_programa_id,
                                    'contract_id':contrato.id,
                                    'valor':aux2,
                                })
            else:
                raise osv.except_osv(('Aviso !'), ('No existen contratos de quincena o no estan activos'))
        

    def load_employee_quincena(self, cr, uid, ids, context=None):
        contract_obj=self.pool.get('hr.contract')
        program_obj = self.pool.get('project.program')
        quincena_obj = self.pool.get('hr.quincena')
        line_obj = self.pool.get('hr.quincena.line')
        line_dept_obj = self.pool.get('hr.dept.line')
        line_line_obj =self.pool.get('hr.quincena.line.line')
        department_obj = self.pool.get('hr.department')
        program_ids = []
        department_ids = []
        auxtotal_quincena = 0
        for this in self.browse(cr, uid, ids, context=context):
            old_line_ids = line_obj.search(cr, uid, [('quincena_id','=',this.id)], context=context)
            line_obj.unlink(cr, uid, old_line_ids, context=context)
            if this.tipo_id:
                contrato_ids = contract_obj.search(cr, uid, [('activo','=',True),
                                                             ('quincena','=',True),
                                                             ('subtype_id','=',this.tipo_id.id)])
            else:
                contrato_ids = contract_obj.search(cr, uid, [('activo','=',True),
                                                             ('quincena','=',True)])
            if contrato_ids:
                aux = 150
                for contrato_id in contrato_ids:
                    contrato = contract_obj.browse(cr, uid, contrato_id)
                    if contrato.program_id.id:
                        if not contrato.program_id.id in program_ids:
                            program_ids.append(contrato.program_id.id)
                    else:
                        raise osv.except_osv(('Error de configuracion'), 
                                             ('El contrato del empleado no tienen programa asignado:  '+contrato.employee_id.complete_name))
                for program_id in program_ids:
                    programa = program_obj.browse(cr, uid, program_id)
                    line_id = line_obj.create(cr, uid, {
                        'name':programa.name,
                        'quincena_id':this.id,
                        'valor':0,
                        'program_id':programa.id,
                    })
                    if this.tipo_id:
                        contrato_ids_2 = contract_obj.search(cr, uid, [('activo','=',True),
                                                                       ('quincena','=',True),
                                                                       ('program_id','=',program_id),
                                                                       ('subtype_id','=',this.tipo_id.id)])
                    else:
                        contrato_ids_2 = contract_obj.search(cr, uid, [('activo','=',True),
                                                                       ('quincena','=',True),
                                                                       ('program_id','=',program_id),])
                    department_ids = []
                    for contrato_id_2 in contrato_ids_2:
                        contrato2 = contract_obj.browse(cr, uid, contrato_id_2)
                        if not contrato2.department_id.id in department_ids:
                            department_ids.append(contrato2.department_id.id)
                    aux_direccion = 0
                    for department_id in department_ids:
                        departamento = department_obj.browse(cr, uid, department_id)
                        line_dept_id = line_dept_obj.create(cr, uid, {
                            'dept_id':line_id,
                            'department_id':department_id,
                        })
                        if this.tipo_id:
                            contrato_ids_3 = contract_obj.search(cr, uid, [('activo','=',True),
                                                                           ('quincena','=',True),
                                                                           ('program_id','=',program_id),
                                                                           ('department_id','=',department_id),
                                                                           ('subtype_id','=',this.tipo_id.id)])
                        else:
                            contrato_ids_3 = contract_obj.search(cr, uid, [('activo','=',True),
                                                                           ('quincena','=',True),
                                                                           ('program_id','=',program_id),
                                                                           ('department_id','=',department_id)])
                        aux_dept = 0 
                        aux2 = 150
                        for contrato_id_3 in contrato_ids_3:
                            aux_dept += 150
                            contrato3 = contract_obj.browse(cr, uid, contrato_id_3)
                            if contrato3.porcentaje_anticipo>0:
                                aux2 = (contrato3.wage)*(contrato3.porcentaje_anticipo)/(100.00)
                            line_line_obj.create(cr, uid, {
                                'q_id':line_dept_id,
                                'employee_id':contrato3.employee_id.id,
                                'contract_id':contrato3.id,
                                'valor':aux2,
                            })
                            line_dept_obj.write(cr, uid, line_dept_id,{
                                'valor':aux_dept,
                            })
                        aux_direccion += aux_dept
                    line_obj.write(cr, uid, line_id,{
                        'valor':aux_direccion,
                    })
                    auxtotal_quincena += aux_direccion
                quincena_obj.write(cr, uid, this.id,{
                    'total':auxtotal_quincena,
                })
            else:
                raise osv.except_osv(('Aviso !'), ('No existen contratos de quincena o no estan activos'))

        self.load_tipo(cr, uid, ids)

    def a_borrador_quincena(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'draft'})
        return True
 
    def pendiente_quincena(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'pendiente'})
        return True

    def pay_employee_quincena(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        partner_obj = self.pool.get('res.partner')
        for this in self.browse(cr, uid, ids):
            date_start = this.period_id.date_start
            date_stop = this.period_id.date_stop
            period_ids = period_obj.find(cr, uid, date_stop)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv(('Error de configuracion !'), ('No ha definido diario de egresos'))
            if not this.journal_id:
                raise osv.except_osv(('Error de usuario !'), ('No ha seleccionado el banco'))
            aux_desc = 'Rol Quincena' + ' - ' + this.period_id.month
            aux_narration = 'Asiento nomina de obreros quincenal correspondiente al mes' + ' - ' + this.period_id.month
            move_id = move_obj.create(cr, uid, {
                'ref':aux_desc,
                'journal_id':journal_ids[0],
                'narration':aux_narration,
                'period_id':period_ids[0],
                'date':date_stop,
            })
            company_aux = 1
            currency_aux = 2
            state_aux = 'draft'
            p_id = 1
            aux_valor = 0
            for line in this.line_ids:
                for line_dept in line.line_ids:
                    for line_line in line_dept.line_ids:
                        aux_valor += line_line.valor
            move_line_obj.create(cr, uid, {
                'move_id':move_id,
                'name':'Pago Quincena Obrero',
                'partner_id':p_id,
                'account_id':this.journal_id.default_credit_account_id.id,
                'credit':aux_valor,
                'journal_id':journal_ids[0],
                'period_id':period_ids[0],
                'company_id':company_aux,
                'currency_id':currency_aux,
            })
            for line in this.line_ids:
                for line_dept in line.line_ids:
                    for line_line in line_dept.line_ids:
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',line_line.employee_id.name)],limit=1)
                        if partner_ids:
                            partner = partner_obj.browse(cr, uid, partner_ids[0])
                            if not partner.anticipo_id.id:
                                raise osv.except_osv(('Error de configuracion'), 
                                                     ('El empleado no tiene cuenta contable de anticipo:  '+line_line.employee_id.complete_name))
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_accrued) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)''',(move_id,partner.anticipo_id.id,line_line.valor,journal_ids[0],period_ids[0],state_aux,company_aux,currency_aux,date_stop,'Quincena',False,False))
#                            move_line_obj.create(cr, uid, {
#                                'move_id':move_id,
#                                'name':'Quincena Obrero',
#                                'partner_id':partner_ids[0],
#                                'account_id':partner.anticipo_id.id,
#                                'debit':line_line.valor,
#                                'journal_id':journal_ids[0],
#                                'period_id':period_ids[0],
#                                'company_id':company_aux,
#                                'currency_id':currency_aux,
#                            })
                        else:
                            raise osv.except_osv(('Error de configuracion'), 
                                                 ('El empleado no tiene cuenta contable de anticipo o proveedor:  '+line_line.employee_id.complete_name))
        self.write(cr, uid, this.id,{'state':'pagado',
                                     'move_id':move_id})
        return True

    _defaults = dict(
        state = 'draft',
        )

hrQuincena()


