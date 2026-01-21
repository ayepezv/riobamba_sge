# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import osv, fields
import time

class stockRequisitionLine(osv.Model):
    _name = 'stock.requisition.line'

    def onchange_quantity(self, cr, uid, ids, qty):
        """ On change of qty 
        @param qty: quantity of product
        @return: Dictionary of values
        """
        if qty<=0:
            raise osv.except_osv(('Error de usuario'), ('La cantidad debe ser mayor a cero'))
        return True

    def onchange_product_line(self, cr, uid, ids, product_id):
        """ On change of product 
        @param product_id: Product id
        @return: Dictionary of values
        """
        result = {}
        if not product_id:
            return {'value': result}
        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_id)
        result['uom_id'] = product.uom_id.id
        return {'value': result}

    _columns = dict(
        req_id = fields.many2one('stock.requisition','Requerimiento'),
        product_id = fields.many2one('product.product','Producto',required=True),
        qty = fields.float('Cantidad'),
        uom_id = fields.related('product_id','uom_id',type='many2one',readonly=True,
                                relation='product.uom',string='Unidad Medida',store=True)
        )

    _defaults = dict(
        qty = 1,
        )

stockRequisitionLine()

class stockRequisition(osv.Model):
    _name = 'stock.requisition'
    _order = 'date desc'


    def _get_depto_solicitante(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            if this.solicitant_id.department_id.id:
                res[this.id] = this.solicitant_id.department_id.id
            else:
                raise osv.except_osv(('Error !'), ('El empleado que solicita no tiene asignado un departamento '))
        return res    

    def _get_app_user_id(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id] = {
                'app_user_id': False,
                'app_employee_id': False,
            }
            if record.solicitant_id.department_id.coordinador_id:
                if record.solicitant_id.department_id.coordinador_id.user_id:
                    if record.solicitant_id.user_id.id != record.solicitant_id.department_id.coordinador_id.user_id.id:
                        result[record.id] = {
                            'app_user_id': record.solicitant_id.department_id.coordinador_id.user_id.id,
                            'app_employee_id': record.solicitant_id.department_id.coordinador_id.id
                        }
                    else:
                        if record.solicitant_id.department_id.manager_id:
                            result[record.id] = {
                                'app_user_id': record.solicitant_id.department_id.manager_id.user_id.id,
                                'app_employee_id': record.solicitant_id.department_id.manager_id.id
                            }
                else:
                    raise osv.except_osv(('Error de configuracion'), ('El jefe departamental no tiene configurado un usuario'))
            else:
                raise osv.except_osv(('Error de configuracion'), ('El departamento del usuario no tiene asignado el jefe'))
        return result
    
    _columns = dict(
        flag = fields.boolean('Bandera'),
        state = fields.selection([('Borrador','Borrador'),('Solicitado','Solicitado'),('Aprobado','Aprobado')],'Estado'),
        create_user_id = fields.many2one('res.users','Creado por'),
        app_user_id =  fields.function(_get_app_user_id, type='many2one', multi="app", store=True, relation="res.users", string="Usuario Aprobacion"),
        app_employee_id =  fields.function(_get_app_user_id, type='many2one', multi="app", store=True, relation="hr.employee", string="Empleado Aprobacion"),
        date = fields.date('Fecha'),
        name = fields.char('Codigo',size=10),
        solicitant_id = fields.many2one('hr.employee','Solicitado por'),
        recibe_id = fields.many2one('hr.employee','Recibe:'),
        unidad_id = fields.function(_get_depto_solicitante, type='many2one', relation='hr.department',
                                    store=True,string='Departamento'), 
        #fields.many2one('hr.department',"Unidad Req."),
        bodega_id = fields.many2one('stock.location','Bodega'),
        objeto_id_id = fields.many2one('account.asset.asset','Vehiculo/Maquinaria'),
        project_id = fields.many2one('project.project','Proyecto'),
        move_lines = fields.one2many('stock.requisition.line','req_id','Detalle'),
        note = fields.text('Observaciones'),
        validate_id = fields.many2one('hr.employee','Autoriza Firma',help="Persona que autoriza, si vacio toma el jefe del departamento"),
        )

    def onchange_solicitant(self, cr, uid, ids, solicitant_id, context={}):
        for this in self.browse(cr, uid, ids):
            vals={}
            return {'value':{'unidad_id':this.solicitant_id.department_id.id}}

    def create(self, cr, uid, vals, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        usuario = self.pool.get('res.users').browse(cr, uid, uid)
        solicitant_id = self.pool.get('hr.employee').browse(cr, uid, vals['solicitant_id'])
        vals['name'] = obj_sequence.get(cr, uid, 'stock.requisition')
        return super(stockRequisition, self).create(cr, uid, vals, context=None)

    def draft_confirmed(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """
        for this in self.browse(cr, uid, ids):
            for line in this.move_lines:
                if line.product_id.qty_available < 0:
                    raise osv.except_osv(('Error !'), 'No puede solicitar el producto %s tiene disponible %s y esta solicitando %s'%(line.product_id.name,str(line.product_id.qty_available),str(line.qty)))
        self.write(cr, uid, ids, {'state': 'Solicitado'})
        return True

    def _prepare_order_picking(self, cr, uid, order, context=None):
        return {
            'ie_type':type_compra[0],
            'type_internal_menu':'in',
            'is_oc':True,
            'responsable_id':order.solicitant_id.id,
            'solicitant_id':order.req_id.solicitant_id.id,
            'unidad_id':order.req_id.department_id.id,
            'name': '/',#self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
            'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
            'date': order.date_order,
            'type': 'in',
            'internal_type':'in',
            'address_id': order.dest_address_id.id or order.partner_address_id.id,
            'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
            'purchase_id': order.id,
            'company_id': order.company_id.id,
            'move_lines' : [],
            'bodega_id' : bodega_id,
            'presp_ref' : order.req_id.presp_ref.id,
            'partner_id' : order.partner_id.id,
            }   

    def return_draft(self, cr, uid, ids, context=None):
        req_obj = self.pool.get('stock.requisition')
        for this in self.browse(cr, uid, ids):
            if uid==this.create_user_id.id or uid==this.app_user_id.id:
                req_obj.write(cr, uid, this.id,{
                        'state':'Borrador',
                        })
            else:
                raise osv.except_osv(('Error de acceso'), ('Solo el usuario creador o aprobador del requerimiento puede regresar a borrador'))
        return True

    def confirm_aprobe(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """
        #crea el picking en draft
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
#        picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context),context)  
        self.write(cr, uid, ids, {'state': 'Aprobado'})
        return True

    def print_rqm(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de retencion
        '''                
        if not context:
            context = {}
        picking = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [picking.id],
                 'model': 'stock.requisition'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'stock.picking.rqm',
            'model': 'stock.requisition',
            'datas': datas,
            'nodestroy': True,            
                }

    def _get_user(self, cr, uid, ids, context=None):
        return uid

    def _get_department(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        if user.employee_id:
            if user.employee_id.department_id:
                return user.employee_id.department_id.id
            else:
                raise osv.except_osv(('Error de configuracion'), ('El empleado no tiene asignado un departamento'))
        else:
            raise osv.except_osv(('Error de configuracion'), ('El usuario no tiene empleado asociado'))

    _defaults = dict(
        flag = False,
        state = 'Borrador',
        create_user_id = _get_user,
        unidad_id = _get_department,
        date = lambda *a: time.strftime('%Y-%m-%d'),
        )

stockRequisition()
