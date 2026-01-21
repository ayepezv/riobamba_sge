# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from time import strftime, strptime
import decimal_precision as dp
from osv import osv, fields

_STATE = [('draft','Borrador'),('pendiente','Pendiente'),('pagado','Pagado'),('anulado','Anulado')]

class judicialDescuento(osv.TransientModel):
    _name = 'judicial.descuento'
    _columns = dict(
        name = fields.many2one('hr.work.period.line','Periodo'),
        date = fields.date('Fecha aplicacion'),
        tipo_rol = fields.many2one('hr.contract.type.type','Tipo Rol'),
    )
    def computeJudicial(self, cr, uid, ids, context=None):
        contract_obj = self.pool.get('hr.contract')
        head_obj = self.pool.get('hr.ie.head')
        line_obj = self.pool.get('hr.ie.line')
        rule_obj = self.pool.get('hr.salary.rule')
        for this in self.browse(cr, uid, ids):
            contract_ids = contract_obj.search(cr, uid, [('activo','=',True),('subtype_id','=',this.tipo_rol.id)])
            if contract_ids:
                rule_ids = rule_obj.search(cr, uid, [('code','=','FUNCION_JUDICIALOB')])
                if not rule_ids:
                    raise osv.except_osv(('Error de configuracion !'), ('Debe crear una regla de descuento con codigo FUNCION_JUDICIALOB'))
                head_id = head_obj.create(cr, uid, {
                    'name':rule_ids[0],
                    'period_id':this.name.id,
                    'date':this.date,
                })
                for contract_id in contract_ids:
                    contrato = contract_obj.browse(cr, uid, contract_id)
                    total = 0
                    if contrato.employee_id.judicial_ids:
                        for line_desc in contrato.employee_id.judicial_ids:
                            total += line_desc.monto
                        total = total/4.00
                        line_id = line_obj.create(cr, uid, {
                            'name': contrato.employee_id.complete_name,
                            'employee_id': contrato.employee_id.id,
                            'date': this.date,
                            'valor': float("%.2f" % total),
                            'categ_id': rule_ids[0],
                            'period_id': this.name.id,
                            'state': 'draft',
                            'head_id':head_id,
                        })
        return True
        
judicialDescuento()

class asientoAnticipo(osv.TransientModel):
    _name = 'asiento.anticipo'
    _columns = dict(
        account_id = fields.many2one('account.journal','Banco'),
        partner_id = fields.many2one('res.partner','Beneficiario'),
    )

    def asientoAnticipo(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        head_obj = self.pool.get('hr.ie.head')
        partner_obj = self.pool.get('res.partner')
        anticipo = head_obj.browse(cr, uid, context['active_id'])
        for this in self.browse(cr, uid, ids):
            journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
            period_ids = period_obj.find(cr, uid, anticipo.date)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            aux_name = anticipo.name.name + ' ' + anticipo.period_id.name
            move_id = move_obj.create(cr, uid, {
                'ref': aux_name,
                'narration':aux_name,
                'journal_id': journal_ids[0],
                'date': anticipo.date,
                'period_id':period_ids[0],
                'state':'draft',
                'afectacion':False,
                'partner_id':this.partner_id.id,
            })
            banco = 0
            for line in anticipo.line_ids:
                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',line.employee_id.name)])
                if not partner_ids:
                    print "NO patyner"
                banco += line.valor
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':anticipo.name.account_id.id,
                    'debit':line.valor,
                    'name':anticipo.name.name,
                    'partner_id':partner_ids[0],
                })
            move_line_obj.create(cr, uid, {
                'move_id':move_id,
                'account_id':this.account_id.default_debit_account_id.id,
                'credit':banco,
                'name':'pago',
                'partner_id':this.partner_id.id,
            })
        return True

asientoAnticipo()
class hrIEHead(osv.osv):
    _name = 'hr.ie.head'
    _description = 'Ingresos/Egresos'
    _order = 'name'

    _columns = dict(
        label = fields.char('Etiqueta',size=64),
        sequence = fields.related('name','sequence',type='integer',string='Secuencia',store=True),
        internal_type = fields.selection([('N','N'),('ANT','ANT')],'Tipo'),
        name = fields.many2one('hr.salary.rule','Regla Salarial',readonly=True,required=True,
                               states={'draft': [('readonly', False)]}),
        period_id = fields.many2one('hr.work.period.line','Periodo',required=True,readonly=True,
                                    states={'draft': [('readonly', False)]}),
        date = fields.date('Fecha',readonly=True,states={'draft': [('readonly', False)]}),
        observaciones = fields.char('Observaciones',size=128,readonly=True,states={'draft': [('readonly', False)]}),
        department_id = fields.many2one('hr.department','Departamento',readonly=True,states={'draft': [('readonly', False)]}),
        valor = fields.float('Porcentaje o Valor',readonly=True,states={'draft': [('readonly', False)]}, 
                             help="Si importa una hoja esto se pasara como valor o como porcentaje del salario, para porcentaje colocar valor menor a 1, siendo por ejmplo 0.5 el 50% del salario"),
        line_ids = fields.one2many('hr.ie.line','head_id','Detalle',readonly=True,states={'draft': [('readonly', False)]}),
        state = fields.selection(_STATE,'Estado'),
        verifi_ids = fields.one2many('ie.verif','ie_id','Verificado'),
        no_ids = fields.one2many('ie.no','ie_id','No verificado'),
        )

    def write(self, cr, uid, ids, vals , context=None):
        ie_line = self.pool.get('hr.ie.line')
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                ie_line.write(cr, uid, [line.id],{
                    'categ_id':this.name.id,
                    'period_id':this.period_id.id,
                })
        return super(hrIEHead, self).write(cr, uid, ids ,vals, context=None)

    def unlink(self, cr, uid, ids, *args, **kwargs):
        
        for this in self.browse(cr, uid, ids):
            if this.state!='draft':
                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar, solo puede realizar esta operacion en estado Borrador'))
            for linea in this.line_ids:
                if linea.state!='draft':
                    raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar, solo puede realizar esta operacionsi todas las lineas se encuentran en estado borrador'))
            sql ="""delete from hr_ie_line where head_id=%s"""%(this.id)
            cr.execute(sql)
        return super(hrIEHead, self).unlink(cr, uid, ids, *args, **kwargs)
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.period_id.name + ' - ' + record.name.name
            res.append((record.id, name))
        return res
        
    def verificar_descuentos(self, cr, uid, ids, context=None):
        verif_obj = self.pool.get('ie.verif') 
        no_obj = self.pool.get('ie.no')
        p_line = self.pool.get('hr.payslip.line')
        empleados_list = []
        for this in self.browse(cr, uid, ids):
            antes1 = verif_obj.search(cr, uid, [('ie_id','=',this.id)])
            verif_obj.unlink(cr, uid, antes1)
            antes2 = no_obj.search(cr, uid, [('ie_id','=',this.id)])
            no_obj.unlink(cr, uid, antes2)
            rule_id = this.name.id
            for line in this.line_ids:
                if not line.employee_id.id in empleados_list:
                    p_line_ids = p_line.search(cr, uid, [('employee_id','=',line.employee_id.id),('salary_rule_id','=',rule_id),('period_id','=',this.period_id.id)])
                    if p_line_ids:
                        line_p = p_line.browse(cr, uid, p_line_ids[0])
                        verif_obj.create(cr, uid, {
                            'ie_id':this.id,
                            'employee_id':line_p.employee_id.id,
                            'monto':line_p.total,
                        })
                    else:
                        no_obj.create(cr, uid, {
                            'ie_id':this.id,
                            'employee_id':line.employee_id.id,
                            'monto':line.valor,
                        })
                    empleados_list.append(line.employee_id.id)
        return True

    def load_employee(self, cr, uid, ids, context=None):
        r_line_obj=self.pool.get('hr.ie.head')
        emp_obj=self.pool.get('hr.employee')
        this=r_line_obj.read(cr, uid, ids) 
        con_obj=self.pool.get('hr.contract')
        line_pool=self.pool.get('hr.ie.line')
        for line in self.browse(cr, uid, ids, context=context):
            old_line_ids = line_pool.search(cr, uid, [('head_id','=',line.id)], context=context)
            line_pool.unlink(cr, uid, old_line_ids, context=context)
            for reg in this:
                val={}
                if reg['department_id']:
                    em_ids =emp_obj.search(cr, uid,[('department_id','=',reg['department_id'][0])])
                else:
                    em_ids =emp_obj.search(cr, uid,[])
                if em_ids:
                    line = self.pool.get('hr.ie.line')
                    periodo=self.pool.get('hr.work.period.line').browse(cr, uid, reg['period_id'][0])
                    for item in em_ids:
                        contrato=con_obj.search(cr, uid,[('employee_id','=',item),
                                                         ('date_start','<=',periodo.date_stop),
                                                         '|',
                                                         ('date_end','>=',periodo.date_start),
                                                         ('date_end','=',False)])
                        if contrato:
                            empleado=emp_obj.browse(cr, uid, item)
                            val['head_id']=int(",".join(map(str,ids)))            
                            val['employee_id']=item
                            val['name']=empleado.name
                            val['valor']= reg['valor']
                            val['categ_id']=reg['name'][0]
                            val['period_id']= periodo.id
                            line.create(cr, uid, val)
                else:
                    raise osv.except_osv(('Aviso !'), ('No existen empleados o no estan activos'))

    def a_borrador(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.ie.line')
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, [this.id],{'state':'draft'})
            ajustar = this.name.is_replanifica
            if ajustar:
                for line in this.line_ids:
                    if line.valor_original>0:
                        line_obj.write(cr, uid, line.id,{
                            'state':'draft',
                            'valor':line.valor_original,
                        })
                    else:
                        line_obj.write(cr, uid, line.id,{
                            'state':'draft',
                        })
            else:
                for line in this.line_ids:
                    line_obj.write(cr, uid, line.id,{
                            'state':'draft',
                        })
        return True

    def pendiente(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.ie.line')
        head_obj = self.pool.get('hr.ie.head')
        slip_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        for this in self.browse(cr, uid, ids):
            from_date = this.period_id.date_start
            to_date = this.period_id.date_stop
            head_obj.write(cr, uid, [this.id],{'state':'pendiente'})
            ajustar = this.name.is_replanifica
#            import pdb
#            pdb.set_trace()
            if ajustar:
                #==Verificar si hay otros egresos que no son ajustables aun no procesados==
                head_ids = head_obj.search(cr, uid, [('id','!=',this.id),('name.is_replanifica','!=',True),('state','=','draft'),('period_id','=',this.period_id.id)])
                if head_ids:
                    aux_rubro = ''
                    for head_id in head_ids:
                        head = head_obj.browse(cr, uid, head_id)
                        aux_rubro += head.name.name + ' - '
                    raise osv.except_osv('Error de usuario','Aun existen rubros de mayor prioridad que aun no han sido procesados, por favor procesar primero los de mayor prioridad %s.'%(aux_rubro))
                #====
                for line in this.line_ids:
                    #calcular el rol a ver si no le avanza
#                    import pdb
#                    pdb.set_trace()
                    #primero ver contrato por fecha
                    contrato_ids = contract_obj.search(cr, uid, [('employee_id','=',line.employee_id.id),('date_end','>=',this.period_id.date_start),
                                                                 ('date_end','<=',this.period_id.date_stop)])
                    band = False
                    if contrato_ids:
                        contrato = contract_obj.browse(cr, uid, contrato_ids[0])
                        band = True
                    else:
                        band = False
                        #aux_empleado = line.employee_id.complete_name
                        #raise osv.except_osv('Error de usuario','No se ha encontrado contrato en esas fechas, para el funcionario %s.'%(aux_empleado))
                    if not band:
                        contrato_ids = contract_obj.search(cr, uid, [('employee_id','=',line.employee_id.id),('activo','=',True)])
                        if contrato_ids:
                            if len(contrato_ids)>1:
                                for contrato_id in contrato_ids:
                                    contrato = contract_obj.browse(cr, uid, contrato_id)
                                    if contrato.date_start<=this.period_id.date_start:
                                        break
                            else:
                                contrato = contract_obj.browse(cr, uid, contrato_ids[0])
                    if contrato.date_start>this.period_id.date_stop:
                        aux_empleado = line.employee_id.complete_name
                        #raise osv.except_osv('Error de usuario','El contrato activo esta superior a la fecha del rol %s.'%(aux_empleado))
                    context.update({'contract':True})
                    slip_data = slip_obj.onchange_employee_id(cr, uid, [], from_date, to_date, contrato.employee_id.id, contrato.id, context=context)
                    department_id = contrato.employee_id.department_id.id
                    job_id = contrato.employee_id.job_id.id
                    res = {
                        'employee_id': contrato.employee_id.id,
                        'name': slip_data['value'].get('name', False),
                        'struct_id': contrato.struct_id.id,
                        'contract_id': contrato.id,
                        'payslip_run_id': context.get('active_id', False),
                        'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                        'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                        'date_from': from_date,
                        'date_to': to_date,
                        'department_id': department_id,
                        'job_id': job_id,
                    }
                    slip_id = slip_obj.create(cr, uid, res, context=context)
                    slip_obj.compute_sheet(cr, uid, [slip_id], context=context)
                    rol = slip_obj.browse(cr, uid, slip_id)
                    aux = rol.net - line.valor
                    if aux<0:
                        aux1 = abs(aux)
                        new_valor = line.valor - aux1
                        if new_valor<0:
                            new_valor = 0
                            #print "VALOR NEGATIVO DEL EMPLEADO", line.employee_id.complete_name,line.categ_id.name
                            #raise osv.except_osv("Error !", "El valor a descontar en el rubro %s, del empleado %s, es menor a cero"%(line.categ_id.name,line.employee_id.complete_name))
                        line_obj.write(cr,uid, line.id,{
                            'valor_original':line.valor,
                            'valor':new_valor,
                        })
                    #############
                    line_obj.write(cr, uid, line.id,{
                        'state':'pendiente',
                        'valor_original':line.valor,
                        'date':this.date,
                    })
                    slip_obj.unlink(cr, uid, [slip_id])
            else:
                for line in this.line_ids:
                    if this.date:
                        aux_date = this.date
                    else:
                        aux_date = this.period_id.date_stop
                    line_obj.write(cr, uid, line.id,{
                        'state':'pendiente',
                        'date':aux_date,
                    })
        return True

    _defaults = dict(
        state = 'draft',
        )

hrIEHead()
class ieVerif(osv.Model):
    _name = 'ie.verif'
    _columns=dict(
        ie_id = fields.many2one('hr.ie.head','Cabecera'),
        employee_id = fields.many2one('hr.employee','Empleado'),
        monto = fields.float('Valor'),
    )
ieVerif()
class ieNo(osv.Model):
    _name = 'ie.no'
    _columns=dict(
        ie_id = fields.many2one('hr.ie.head','Cabecera'),
        employee_id = fields.many2one('hr.employee','Empleado'),
        monto = fields.float('Valor'),
    )
ieNo()
class hrIELine(osv.osv):
    _name = 'hr.ie.line'
    _description = 'Lineas'
    _order = 'name_aux asc'

    
#    def _get_order(self, cr, uid, ids, context=None):
#        result = {}
#        for line in self.pool.get('hr.ie.line').browse(cr, uid, ids, context=context):
#            result[line.pago_adv_id.id] = True
#        return result.keys()   

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            name = record.categ_id.name + " - $." + str(record.valor)
            res.append((record.id, name))
        return res   
    
    def a_borrador_l(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'draft'})
           
    def realizado_l(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'pendiente'})

    def write(self, cr, uid, ids, vals , context=None):
        if vals.has_key('period_id'):
            if vals['period_id']:
                for this in self.browse(cr, uid, ids):
                    if this.head_id:
                        if this.head_id.period_id.id!=vals['period_id']:
                            raise osv.except_osv('Error al modificar', 'El detalle esta relacionado a un encabezado con periodo diferente')
        return super(hrIELine, self).write(cr, uid, ids ,vals, context=None)

    def create(self, cr, uid, values, context=None):
        if not(values.has_key('period_id')):
            if values.has_key('head_id'):
                obj_head = self.pool.get('hr.ie.head')
                cabecera = obj_head.browse(cr, uid, values['head_id'], context)
                values['period_id'] = cabecera.period_id.id
                values['categ_id'] = cabecera.name.id
            else:
                raise osv.except_osv('Error al almacenar', 'No se encuentra asignado un periodo de pago')
        values['valor_original'] = values['valor']
        return super(hrIELine, self).create(cr, uid, values, context=context)
   
    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.state!='draft':
                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar, solo puede realizar esta operacion en estado Borrador'))
        return super(hrIELine, self).unlink(cr, uid, ids, *args, **kwargs)
    
    def _validar_mayor_cero(self, cr, uid, ids, context=None):
        return True
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.valor <= 0:
            return False
        return True
           
    _columns = dict(
        label = fields.char('Etiqueta',size=64),
        cedula = fields.related('employee_id','name',type='char',size=15,store=True),
        referencia = fields.char('Referencia',size=64,readonly=True,states={'draft': [('readonly', False)]}),
        name = fields.char('Empleado',size=128),
        name_aux = fields.related('employee_id','complete_name',type='char',size=256,store=True),
        employee_id = fields.many2one('hr.employee','Empleado',required=True, 
                                      readonly=True,states={'draft': [('readonly', False)]}),
        date = fields.date('Fecha', readonly=True,states={'draft': [('readonly', False)]}),
        valor = fields.float('Valor',required=True, digits_compute=dp.get_precision('Account'),
                             readonly=True,states={'draft': [('readonly', False)]}),
        valor_original = fields.float('Valor Cargado', digits_compute=dp.get_precision('Account')),
        categ_id = fields.many2one('hr.salary.rule','Regla Salarial',required=True),#related('head_id', 'name', type='many2one', relation='hr.salary.rule', 
        #              string="Regla Salarial", store=True,readonly=True,states={'draft': [('readonly', False)]}),
        head_id = fields.many2one('hr.ie.head','Cabecera',ondelete='cascade'),
        period_id = fields.many2one('hr.work.period.line','Periodo',required=True, 
                                    readonly=True,states={'draft': [('readonly', False)]}),
        state = fields.selection(_STATE,'Estado',readonly=True),
    )
    
    _defaults = dict(
        state = 'draft',
        date = strftime("%Y-%m-%d")
    )
   
    _constraints = [
        (_validar_mayor_cero, 'Los valores deben ser superiores a cero', ['valor']),
    ]
   
hrIELine()
