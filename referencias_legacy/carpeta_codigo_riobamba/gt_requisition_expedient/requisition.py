# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Gnuthink Software Labs Cia. Ltda.
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

from osv import osv, fields
import time
import netsvc
from tools.translate import _

class logRequisition(osv.Model):
    _name = 'requisition.log'
    _order = 'date desc'
    _columns = dict(
        name = fields.many2one('res.users','Usuario'),
        date = fields.datetime('Fecha'),
        action = fields.char('Acción',size=64),
        desc = fields.char('Observación',size=256),
        req_log_id = fields.many2one('purchase.requisition','Solicitud'),
        )

    _defaults=dict(
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        )
logRequisition

class PurchaseReqModified(osv.Model):
    
    _inherit='purchase.requisition'
    _order = 'date_start desc, name desc'
    _description = 'Requisicion Compra Modificada'

    def _compute_money(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            for po in this.purchase_select_ids:
                if po.select_item:
                    aux += po.amount_total
#                for po_line in po.order_line:
#                    if po_line.select:
#                        aux += po_line.price_subtotal
        res[this.id] = aux
        return res

    def _compute_money_cot(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            for po in this.purchase_ids:
                if po.select_item:
                    aux += po.amount_total
#                for po_line in po.order_line:
#                    if po_line.select:
                        #aux += po_line.price_subtotal
        res[this.id] = aux
        return res

    def cargar_observaciones_presupuesto(self, cr, uid, ids, prf, context={}):
        res_dev = {'value': {}}
        #import pdb
        #pdb.set_trace()
        prf_obj = self.pool.get('crossovered.budget.certificate')
        if prf:
            presupuesto = prf_obj.browse(cr, uid, prf, context)
            res_dev['value'] = {'description':presupuesto.description}
        return res_dev

    def onchange_prf(self, cr, uid, ids, prf):
        res_dev = {'value': {}}
        res_list = []
        account_ids_prf = []
        sc_obj = self.pool.get('purchase.requisition')
        categ_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        prf_obj = self.pool.get('crossovered.budget.certificate')
        for prf_ in prf_obj.browse(cr, uid, [prf]):
            for line in prf_.line_ids:
                for acc_id in line.budget_line_id.general_budget_id.account_ids:
                    account_ids_prf.append(acc_id.id)
        categ_ids = categ_obj.search(cr, uid, [])
        categ_aux = []
        for categ_id in categ_ids:
            categ = categ_obj.browse(cr, uid, categ_id)
            account_id = categ.property_account_expense_categ.id
#            print "KJHHHHHHHHHHHHHHHHHHHHH", account_id, account_ids_prf, len(categ_ids)
            if account_id in account_ids_prf:
#                print "COINCIDE", 
                categ_aux.append(categ_id)
#        product_ids = product_obj.search(cr, uid, ['|',('categ_id','in',categ_aux),('property_account_expense','in',account_ids_prf)])
        srv_ids = product_obj.search(cr, uid, [('type','=','service')])
        if len(categ_aux)>0:
            product_ids = product_obj.search(cr, uid, [('categ_id','in',categ_aux)])
        else:
            product_ids = product_obj.search(cr, uid, [])
        p_total = []
        for p in product_ids:
            p_total.append(str(p))
        for srv_id in srv_ids:
            p_total.append(str())
        res_dev['value']['list_ids'] = ' '.join(p_total)
        res_dev['value']['line_ids'] = []
        return res_dev

    def onchange_code(self, cr, uid, ids, type_id):
        res_dev = {'value': {}}
        res_list = []
        if type_id:
            if type_id == 'product':
                res_list.append('product')
                res_list.append('consu')
            if type_id in ('service','asset'):
                res_list.append(type_id)
            elif type_id=='pa':
                res_list.append('product')
                res_list.append('asset')
            elif type_id=='ps':
                res_list.append('product')
                res_list.append('service')
        print "STR========================", res_list
        res_dev['value']['str_tipos'] = ' '.join(res_list)
        res_dev['value']['line_ids'] = []
        return res_dev

    def _func_onchange_code(self, cr, uid, ids, type_id):
        res_dev = {'value': {}}
        res_list = []
        if type_id:
            if type_id == 'product':
                res_list.append('product')
                res_list.append('consu')
            if type_id in ('service','asset'):
                res_list.append(type_id)
            elif type_id=='pa':
                res_list.append('product')
                res_list.append('asset')
            elif type_id=='ps':
                res_list.append('product')
                res_list.append('service')
        res_dev['value']['str_tipos'] = str(res_list)
        res_dev['value']['line_ids'] = []
        return res_dev

    _columns = dict(
        total_compra = fields.function(_compute_money,string='Total Aut. (Inc. IVA)$',type="float",store=True,
                                       help="Total en USD que suma cada uno de los items de las cotizaciones aprobadas"),
        total_cotizaciones = fields.function(_compute_money_cot,string='Total Cotiz. Selec. (Inc. IVA) $',type="float",
                                             store=True, help="Es el total en USD que suma cada uno de los items de cada una de las cotizaciones recomendadas"),
        sgd_id = fields.many2one('doc_expedient.expedient','Trámite',
                                 help="Tramite relacionado al proceso si usted no lo selecciona este se crea automáticamente"),
#        solicitant_id = fields.many2one('hr.employee','Solicitante',required=True),
        usr_solicitant_id = fields.related('solicitant_id','user_id', type='many2one', 
                                           relation='res.users',string='Usr. Solicitante', store=True),
        #fields.many2one('res.users','Solicitante',required=True),
#        solicitant_id = fields.related('usr_solicitant_id','employee_id', type='many2one', 
#                                            relation='hr.employee',string='Solicitante', store=True),
        solicitant_id = fields.many2one('hr.employee','Solicitante',required=True),
#        user_solicitant_id = fields.related('solicitant_id','user_id', type='many2one', 
#                                            relation='res.users',string='Usuario Solicitante', store=True),
        anulant_id = fields.many2one('res.users','Anulado por'),
        aprobador_id = fields.many2one('res.users','Aprobado por'),
        recibe_id = fields.many2one('hr.employee','Recibe'),
        log_ids = fields.one2many('requisition.log','req_log_id','Solicitud'),
#        state = fields.selection([('draft','Borrador'),('in_progress','Sol.Ingresada'),('aproved','Aprobado/Reg.Cotización'),('recomended','Recomendado'),('select','Seleccionado/Autorizado'),('comprometed','Presupuesto Comprometido'),('cancel','Cancelled'),('done','Finalizado')], 'State', required=True),
        state = fields.selection([('draft','Borrador'),('in_progress','En Proceso'),
                                  ('aproved','Reg.Cotización'),
                                  ('recomended','Recomendado'),('select','Autorizado'),
                                  ('cancel','Anulada'),
                                  ('group','Agrupada'),('done','Realizado')], 
                                 'State', required=True),
        department_id = fields.many2one('hr.department','Unidad Req.',help="Es el departamento del solicitante, se carga automaticamente al crear el documento"),
        purchase_id = fields.many2one('purchase.order','Order Compra Relacionada'),
        active = fields.boolean('Agrupada'),
        justifi = fields.char('Justificación',size=128),
        presp_ref = fields.many2one('crossovered.budget.certificate','Presupuesto Ref.',help="Permite seleccionar los presupuestos referenciales certificados y que no esten siendo utilizados en otro proceso, al anular una solicitud de compra este presupuesto se libera y puede ser utilizado en un nuevo proceso"),
        observation = fields.char('Comentario',size=256,
                                  help="Coloque aquí su comentario referente al proceso de la solicitud de compra"),
        cotizar_all = fields.boolean('Cotizar todo',help="Si usted selecciona esta opción las cotizaciones a los diferentes proveedores se crearán con las cantidades requeridas, caso contrario se realizarán solamente con la diferencia o faltante en inventario"),
        unidad_id = fields.many2one('stock.location','Bodega',required=True,readonly=True),
        referencia_bodega = fields.char('Referencia',size=32),
        picking_id = fields.many2one('stock.picking','Egreso',readonly=True),
        criterio_rec = fields.text('Criterio Recomendación'),
        criterio_sel = fields.text('Criterio Selección'),
        tabla_id = fields.many2one('purchase.config.infima','Periodo Fiscal'),
        revert = fields.boolean('Devuelto'),
        total_items = fields.integer('Total Items'),
        contract_object = fields.selection([('product','Bienes y Consumibles'),('service','Servicios'),('asset','Activos'),
                                            ('pa','Bienes y Activos'),('ps','Bienes y Servicios')],
                                           'Objeto Compra',required="1"),
#        str_tipos = fields.function(_func_onchange_code,string='dom'
#                                    ,type='char',size=16,store=False),#
        str_tipos = fields.char('Tipos',size=32),
        list_ids = fields.text('Ids prodictos'),
        purchase_select_ids = fields.one2many('purchase.order','requisition_select_id','Cotizaciones',
                                              states={'done': [('readonly', True)]}),
        code_po = fields.char('Codigo Interno', size=16),
        objeto_id_id = fields.many2one('account.asset.asset','Vehiculo/Maquinaria'),
        )

    def generate_line(self, cr, uid, ids, context=None):
        req_obj = self.pool.get('purchase.requisition.line')
        for this in self.browse(cr, uid, ids):
            lista = [line.id for line in this.line_ids]
            req_obj.unlink(cr, uid, lista)
            for line in this.presp_ref.line_ids:
                req_obj.create(cr, uid, {
                        'presp_ref':this.presp_ref.id,
                        'partida_id':line.budget_line_id.id,
                        'requisition_id':this.id,
                        })
        return True



    def print_solicitud_proveedor(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir la solicitud de compra
        '''        
        if not context:
            context = {}
        solicitud = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [solicitud.id], 'model': 'purchase.requisition'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'solicitud',
            'model': 'purchase.requisition',
            'datas': datas,
            'nodestroy': True,                        
            }


    def print_solicitud(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir la solicitud de compra
        '''        
        if not context:
            context = {}
        solicitud = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [solicitud.id], 'model': 'purchase.requisition'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase.req',
            'model': 'purchase.requisition',
            'datas': datas,
            'nodestroy': True,                        
            }        

    def print_cuadro(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir el cuadro comparativo
        '''        
        if not context:
            context = {}
        solicitud = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [solicitud.id], 'model': 'purchase.requisition'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase.req.cuadro',
            'model': 'purchase.requisition',
            'datas': datas,
            'nodestroy': True,                        
            }

    def print_cuadro_aut(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir el cuadro comparativo autorizado
        '''        
        if not context:
            context = {}
        solicitud = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [solicitud.id], 'model': 'purchase.requisition'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase.req.cuadro.aut',
            'model': 'purchase.requisition',
            'datas': datas,
            'nodestroy': True,                        
            }        

    def _generate_log(self, cr, uid, id, state, context=None ):
        req_obj = self.pool.get('purchase.requisition')
        log_obj = self.pool.get('requisition.log')
        req=req_obj.browse(cr, uid, id)
        log_obj.create(cr, uid, {
                'name':uid,
                'action':state,
                'req_log_id':id,
                'desc':req.observation,
                'date':time.strftime('%Y-%m-%d %H:%M:%S')  
                })
        req_obj.write(cr, uid, id, {
                'observation':'',
                })
        return True

    def tender_select_stop(self, cr, uid, id, context):
        self.write(cr, uid, id, {'state':'cancel'})
        self._generate_log(cr, uid, ids[0],'X Anulada')
        return True

    def tender_cancel(self, cr, uid, ids, context=None):
        purchase_order_obj = self.pool.get('purchase.order')
        for purchase in self.browse(cr, uid, ids, context=context):
            for purchase_id in purchase.purchase_ids:
                if str(purchase_id.state) in('draft','wait'):
                    purchase_order_obj.action_cancel(cr,uid,[purchase_id.id])
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def tender_start_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'} ,context=context)
        self._generate_log(cr, uid, ids[0],'<-- Borrador')
        return True

    def tender_progress_start(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'} ,context=context)
        self._generate_log(cr, uid, ids[0],'<-- Borrador')
        return True

    def tender_start(self, cr, uid, ids, context=None):
        #crera lineas en base al presupuesto referencial
        req_obj = self.pool.get('purchase.requisition.line')
        for this in self.browse(cr, uid, ids):
            for line in this.presp_ref.line_ids:
                req_obj.create(cr, uid, {
                        'presp_ref':this.presp_ref.id,
                        'partida_id':line.budget_line_id.id,
                        'requisition_id':this.id,
                        })
        self.write(cr, uid, ids, {'state':'start'} ,context=context)
        self._generate_log(cr, uid, ids[0],'En Proceso')
        return True


    def _validate_budget_position(self, cr, uid, ids, context=None ):
#        for this in self.browse(cr, uid, ids):
#            acc_ids = []
#            for prf_line in this.presp_ref.line_ids:
#                acc_ids = prf_line.budget_line_id.general_budget_id.account_ids
#            for line in this.line_ids:
#                acc_id = line.product_id.categ_id.property_account_expense_categ
#                if not acc_id in acc_ids:
#                    raise osv.except_osv(('Error !'), 'Verifique los productos seleccionados el producto %s no corresponde a ninguna partida del presupuesto referencial, verifique las partidas o el producto'%(line.product_id.default_code + ' ' +line.product_id.name))
        return True

    def tender_in_progress(self, cr, uid, ids, context=None):
        config_obj = self.pool.get('purchase.config.infima')
        budget_obj = self.pool.get('crossovered.budget.certificate')
        config_ids = config_obj.search(cr, uid, [('activo','=',True)],limit=1)
        self._validate_budget_position(cr, uid, ids)
        if config_ids:
            config = config_obj.browse(cr, uid, config_ids[0])
            monto_maximo = config.monto_maximo
        else:
            raise osv.except_osv(('Error de configuración'), ('No tiene tabla de configuración de montos activa, por favor configure una'))
        for this in self.browse(cr, uid, ids):
            solicitant_user = this.usr_solicitant_id.id
            if this.presp_ref.amount_total > monto_maximo:
                raise osv.except_osv(('Error de usuario'), ('El monto del presupuesto referencial %s es mayor al permitido para realizar el proceso de infima cuantía %s') %(str(this.presp_ref.amount_total),str(monto_maximo)))
            total_items = len(this.line_ids)
            if len(this.line_ids)>0:
                for line in this.line_ids:
                    if not line.product_id:
                        raise osv.except_osv(('Error Usuario'), ('Debe seleccionar un producto por favor verifique en cada linea este seleccionado un producto'))
                self.write(cr, uid, ids, {'state':'in_progress',
                                          'revert':False,
                                          'total_items':total_items,
                                          'tabla_id':config.id,} ,context=context)
                budget_obj.write(cr, uid, this.presp_ref.id, {'is_lock':True})
                self._generate_log(cr, uid, ids[0],'En proceso')
                ##crear tarea relacionada al tramite
                task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : str('Inicia proceso') ,
                                                                             'description': 'Servidor: ' + this.solicitant_id.complete_name + ' ' + 'Iniciado el proceso de adquisiciones',
                                                                             'department': this.department_id.id,
                                                                             'employee_id' : this.solicitant_id.id,
                                                                             'job_id': this.solicitant_id.job_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id':this.sgd_id.id,
                                                                             'state': 'done',
                                                                             'assigned_user_id':this.user_id.id,
                                                                             }, context=context)        
            else:
                raise osv.except_osv(('Error Usuario'), ('Debe ingresar por lo menos una linea en la solicitud de compra'))
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'gt_government_procedure', 'action_purchase_requisition_alone')
        id_view = result and result[1] or False
        result = act_obj.read(cr, uid, [id_view], context=context)[0]
        return result
    
    def tender_aproved_progress(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'in_progress'} ,context=context)
        self._generate_log(cr, uid, ids[0],'<-- En proceso')
        return True

    def tender_aprovedd(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'aproved',
                                  'revert':False,} ,context=context)
        self._generate_log(cr, uid, ids[0],'Aprobado')
        for this in self.browse(cr, uid, ids):
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                         'other_action' : str('Aprueba compra') ,
                                                                         'description': 'Servidor: ' + this.solicitant_id.complete_name + ' ' + 'Aprobado el proceso',
                                                                         'department': this.department_id.id,
                                                                         'employee_id' : this.solicitant_id.id,
                                                                         'job_id': this.solicitant_id.job_id.id,
                                                                         'user_id': uid,
                                                                         'expedient_id':this.sgd_id.id,
                                                                         'state': 'done',
                                                                         'assigned_user_id':this.user_id.id,
                                                                         }, context=context)        
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'gt_government_procedure', 'action_purchase_requisition_aprobe_documental')
        id_view = result and result[1] or False
        result = act_obj.read(cr, uid, [id_view], context=context)[0]
        return result

    def tender_recomended_aproved(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'aproved'} ,context=context)
        self._generate_log(cr, uid, ids[0],'<-- Aprobado')
        return True

    def _validate_money(self, cr, uid, ids, context=None, opc=1):
#        for this in self.browse(cr, uid, ids):
#            aux = 0
#            if opc==1:
#                for po in this.purchase_ids:
#                    for line in po.order_line:
#                        if line.select:
#                            aux += line.price_subtotal
#                if aux>this.presp_ref.amount_certified:
#                    raise osv.except_osv(('Error !'), 'No puede sobrepasar el monto del presupuesto referencial, este es de %s y el total de solicitud es %s '%(str(t#his.presp_ref.amount_certified),str(aux)))
            #QUitar para q funqeu
#            else:
#                if this.total_compra>this.presp_ref.amount_total:
#                    raise osv.except_osv(('Error !'), 'No puede sobrepasar el monto del presupuesto referencial, este es de %s y el total de solicitud es %s '%(str(this.presp_ref.amount_total),str(this.total_compra)))
        return True

    def _validate_lines(self, cr, uid, ids, context=None, opc=1):
        #Aqui se deberia validar solamente que no se compre mas de lo pedido
        j = 0
        band = True
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                total_solicitud = line.product_qty
                aux = 0 
                if opc==1:
                    for po in this.purchase_ids:
                        for po_line in po.order_line:
                            if (po_line.product_id.id == line.product_id.id) and po_line.select:
                                aux += po_line.product_qty
                else:
                    for po in this.purchase_select_ids:
                        for po_line in po.order_line:
                            if (po_line.product_id.id == line.product_id.id) and po_line.select:
                                aux += po_line.product_qty
                if aux<1:
                    raise osv.except_osv(('Error !'), 'No puede comprar CERO, esta comprando %s del producto %s y la solicitud es por %s'%(str(aux),line.product_id.name,str(line.product_qty)))
        return True


    def tender_recomended(self, cr, uid, ids, context=None):
        #verificar q solo este recomendada una cotizacion
        #crear wizard q muestra el numero de items y le avisa cuantos esta yendo a buy
        po_obj = self.pool.get('purchase.order')
        j = 0
        for this in self.browse(cr, uid, ids):
            if not len(this.purchase_ids)>=1:
                raise osv.except_osv(('Error usuario'), ('Debe registrar por lo menos una cotización de proveedor'))
#            for purchase in this.purchase_ids:
#                for purchase_line in purchase.order_line:
#                    if purchase_line.select:
#                        j +=1
#            if j != len(this.line_ids):
                #validar las lineas de la solicitud contra las lineas de las cotizaciones
            validate = self._validate_lines(cr, uid, ids, context, 1)
            validate_money = self._validate_money(cr, uid, ids, context, 1)
#            if not validate:
#                raise osv.except_osv(('Error usuario'), ('Debe seleccionar el mismo numero de items solicitados, en las cotizaciones de proveedor'))
            ids_clonados = []
            vals = {}
            name_aux = ''
            if this.criterio_rec:
                for po in this.purchase_ids:
                    vals = po_obj.copy_data(cr, uid, po.id)
                    name_aux = vals['name']
                    name_aux = name_aux + ' '
                    vals['name'] = name_aux
                    vals['requisition_select_id'] = this.id
                    vals['requisition_id'] = ''
                    id_po_creado = po_obj.create(cr, uid, vals)
#                    po_obj.write(cr, uid, id_po_creado,{'requisition_select_id':this.id})
#                ids_clonados.append(id_po_creado)
                self.write(cr, uid, ids, {'state':'recomended',
                                          #'purchase_select_ids':(0,0,ids_clonados),
                                          'revert':False,} ,context=context)
                self._generate_log(cr, uid, ids[0],'Recomendado')
                task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : str('Recomienda oferta(s)') ,
                                                                             'description': 'Servidor: ' + this.solicitant_id.complete_name + 'Recomienda la oferta',
                                                                             'department': this.department_id.id,
                                                                             'employee_id' : this.solicitant_id.id,
                                                                             'job_id': this.solicitant_id.job_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id':this.sgd_id.id,
                                                                             'state': 'done',
                                                                             'assigned_user_id':this.user_id.id,
                                                                             }, context=context)
            else:
                raise osv.except_osv(('Error usuario'), ('Por favor emita los criterios de recomendación'))
#            else:
#                raise osv.except_osv(('Advertencia'), ('Debe recomendar una cotización de proveedor'))
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'gt_government_procedure', 'action_purchase_requisition_recomendar')
        id_view = result and result[1] or False
        result = act_obj.read(cr, uid, [id_view], context=context)[0]
        return result

    def tender_selected_recomended(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'recomended'} ,context=context)
        self._generate_log(cr, uid, ids[0],'<-- Recomendado')
        return True

    def tender_select(self, cr, uid, ids, context=None):
        j = 0
        presp_obj = self.pool.get('crossovered.budget.certificate')
        presp_line = self.pool.get('crossovered.budget.certificate.line')
        for this in self.browse(cr, uid, ids):
            if not len(this.purchase_ids)>=1:
                raise osv.except_osv(('Error usuario'), ('Debe registrar por lo menos una cotización de proveedor'))
            validate = self._validate_lines(cr, uid, ids, context, 0)
            validate_money = self._validate_money(cr, uid, ids, context, 0)
#            if not validate:
#                raise osv.except_osv(('Error usuario'), ('Debe seleccionar el mismo numero de items solicitados, en las cotizaciones de proveedor'))
            if this.criterio_sel:
                self.write(cr, uid, ids, {'state':'select',
                                          'revert':False,} ,context=context)
                self._generate_log(cr, uid, ids[0],'Seleccionado/Autorizado')
#                presp_ref = presp_obj.browse(cr, uid, this.presp_ref.id)
#                presp_line.write(cr, uid, presp_ref.line_ids[0].id,{'amount_compromised':this.total_compra})
                #presp_obj.write(cr, uid, this.presp_ref.id,{'amount_commited':this.total_compra})
                task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : str('Autoriza compra') ,
                                                                             'description': 'Servidor: ' + this.solicitant_id.complete_name + ' Autoriza la(s) oferta(s)',
                                                                             'department': this.department_id.id,
                                                                             'employee_id' : this.solicitant_id.id,
                                                                             'job_id': this.solicitant_id.job_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id':this.sgd_id.id,
                                                                             'state': 'done',
                                                                             'assigned_user_id':this.user_id.id,
                                                                             }, context=context)
            else:
                raise osv.except_osv(('Error usuario'), ('Por favor emita los criterios de selección'))
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'gt_government_procedure', 'action_purchase_requisition_comprometer')
        id_view = result and result[1] or False
        result = act_obj.read(cr, uid, [id_view], context=context)[0]
        return result
   
    def tender_comprometed_recomended(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'select'} ,context=context)
        self._generate_log(cr, uid, ids[0],'<-- Seleccionar')
        return True

    def tender_comprometed(self, cr, uid, ids, context=None):
#        for this in self.browse(cr, uid, ids):
#            if this.presp_ref.state=='compromised':
#                self.write(cr, uid, ids, {'state':'comprometed'} ,context=context)
#                self._generate_log(cr, uid, ids[0],'Comprometido')
#            else:
#                  raise osv.except_osv('Error', 'Verifique que el presupuesto referencial este comprometido')
        return True

    def tender_reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def tender_picking(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        for this in self.browse(cr, uid, ids):
            #crear picking and moves from req
            j = 0
            picking_id = picking_obj.create(cr, uid, {
                    'name':this.name,
                    'type':'internal',
                    'move_type':'one',
                    'receptor_id':this.recibe_id.id,
                    })
            for line in this.line_ids:
                if line.product_id.type != 'service':
                    j += 1
                    move_obj.create(cr, uid, {
                            'name':this.name,
                            'product_id':line.product_id.id,
                            'product_qty':line.product_qty,
                            'product_uom':line.product_uom_id.id,
                            'picking_id':picking_id,
                            'location_id':1,
                            'location_dest_id':1,
                            })
            if j==0:
                picking_obj.unlink(cr, uid, picking_id)
            self._generate_log(cr, uid, ids[0],'Realizado')
            self.write(cr, uid, ids, {'state':'done',
                                      'picking_id':picking_id,} ,context=context)
        return True

    def tender_done(self, cr, uid, ids, context=None):
        '''verificar las existencias de inventario, si existe todo se genera solo el picking
           si no hay nada se genera la OC con el total caso contrario se genera la OC solamente 
           por la diferencia
        '''
        location_obj = self.pool.get('stock.location')
        purchase_obj = self.pool.get('purchase.order')
        po_line_obj = self.pool.get('purchase.order.line')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        prf_obj = self.pool.get('crossovered.budget.certificate')
        compromiso_line = self.pool.get('crossovered.budget.certificate.line')
        for this in self.browse(cr, uid, ids):
#            if not this.presp_ref.state=='compromised':
#                  raise osv.except_osv('Error', 'Verifique que el presupuesto referencial este comprometido')
            #crear picking and moves from req
            j = 0
#            picking_id = picking_obj.create(cr, uid, {
#                    'name':this.name,
#                    'type':'internal',
#                    'move_type':'one',
#                    'project_id':this.presp_ref.project_id.id,
#                    'location_id':this.unidad_id.id,
#                    'bodega_id':this.unidad_id.id,
#                    'tramite_id':this.sgd_id.id,
#                    'responsable_id':this.solicitant_id.id,
#                    })
#            for line in this.line_ids:
#                if line.product_id.type='asset'
#                if line.product_id.type in ('product','consu'):
#                    j += 1
#                    context['type']='internal'
#                    context['crear'] = False
#                    move_obj.create(cr, uid, {
#                            'name':this.name,
#                            'product_id':line.product_id.id,
#                            'product_qty':line.product_qty,
#                            'product_uom':line.product_uom_id.id,
#                            'picking_id':picking_id,
#                        },context=context)
#            if j==0:
#                picking_obj.unlink(cr, uid, [picking_id])
            n = 0
            for line_c in this.purchase_ids:
                purchase_obj.write(cr, uid, line_c.id, {
                        'select':False,
                        })
            for line in this.purchase_select_ids:
                m = 0
                #Aqui se debe recorrre cada OC y si tiene una lineas seleccionado queda activo else no
                for line_line in line.order_line:
                    if line_line.select:
                        m += 1
                        n += 1
                    else:
                        po_line_obj.unlink(cr, uid, line_line.id)
                if m>0:
                    purchase_obj.write(cr, uid, line.id,{'req_id':this.id,'tramite_id':this.sgd_id.id,
                                                         'presp_ref':this.presp_ref.id,'solicitant_id':this.usr_solicitant_id.id,
                                                         'is_finish':True})
                    prf_obj.write(cr, uid, this.presp_ref.id,{'partner_id':line.partner_id.id})
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'purchase.order', line.id, 'purchase_confirm', cr)
                    #Ejecutar el flujo para que apruebe directo la OC
                else:
                    purchase_obj.write(cr, uid, line.id, {
                            'select':False,
                            })
            if n>0:
                self.write(cr, uid, this.id, {
                        'state':'done',
                        'revert':False,
                        })
                self._generate_log(cr, uid, ids[0],'Realizado')
                task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : str('Finaliza proceso') ,
                                                                             'description': 'Servidor: ' + this.solicitant_id.complete_name + ' ' + 'Finaliza el proceso',
                                                                             'department': this.department_id.id,
                                                                             'employee_id' : this.solicitant_id.id,
                                                                             'job_id': this.solicitant_id.job_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id':this.sgd_id.id,
                                                                             'state': 'done',
                                                                             'assigned_user_id':this.user_id.id,
                                                                             }, context=context)
            else:
                raise osv.except_osv('Error de usuario', 'No ha seleccionado ninguna linea en las cotizaciones')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'gt_government_procedure', 'action_purchase_requisition_finalizar')
        id_view = result and result[1] or False
        result = act_obj.read(cr, uid, [id_view], context=context)[0]
        return result

    def create(self, cr, uid, vals, context=None):
        emp_obj = self.pool.get('hr.employee')
        obj_sequence = self.pool.get('ir.sequence')
        vals['name'] = obj_sequence.get(cr, uid, 'purchase.order.requisition')
#        user = self.pool.get('res.users').browse(cr, uid, uid)
        solicitante = emp_obj.browse(cr, uid, vals['solicitant_id'])
        if solicitante.user_id:
            dept_id = solicitante.user_id.context_department_id.id 
        else:
            dept_id = solicitante.department_id.id
        resumen = ""
        if vals['description']:
            resumen = vals['description']
#        usuario = self.pool.get('res.users').browse(cr, uid, vals['usr_solicitant_id'])
        solicitant_id = self.pool.get('hr.employee').browse(cr, uid, vals['solicitant_id'])
        if dept_id:
            vals['department_id'] = dept_id
        if vals['sgd_id']:
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                         'other_action' : str('Solicitud de compra') ,
                                                                         'description': 'Servidor: ' + solicitant_id.complete_name,
                                                                         'department': solicitant_id.department_id.id,
                                                                         'employee_id' : solicitant_id.id,
                                                                         'job_id': solicitant_id.job_id.id,
                                                                         'user_id': uid,
                                                                         'expedient_id':vals['sgd_id'],
                                                                         'state': 'done',
                                                                         'assigned_user_id':uid,
                                                                         }, context=context)
        else:
            resume = str('Solicitud de compra: ') + vals['name']
            expedient_id= self.pool.get('doc_expedient.expedient').create(cr, uid,{'name': resume,
                                                                                   'state': 'draft',
                                                                                   'ubication':'internal',
                                                                                   'resumen': resume}, context=context)
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                         'other_action' : str('Solicitud de compra') ,
                                                                         'description': 'Servidor: ' + solicitant_id.complete_name,
                                                                         'department': solicitant_id.department_id.id,
                                                                         'employee_id' : solicitant_id.id,
                                                                         'job_id': solicitant_id.job_id.id,
                                                                         'user_id': uid,
                                                                         'expedient_id':expedient_id,
                                                                         'state': 'done',
                                                                         'assigned_user_id':uid,
                                                                         }, context=context)
            vals['sgd_id']=expedient_id
            self.pool.get('doc_expedient.expedient').action_draft_created(cr, uid, [expedient_id],context)
        self.pool.get('doc_expedient.task').write(cr, uid, [task_id], {'state':'done'})
        return super(PurchaseReqModified, self).create(cr, uid, vals, context=None)

    
    def write(self, cr, uid, ids, vals , context=None):
        req_line = self.pool.get('purchase.requisition.line')
        if vals.has_key('contract_object'):
            if vals['contract_object']:
                line_ids = req_line.search(cr, uid, [('requisition_id','=',ids[0])])
                if line_ids:
                    req_line.unlink(cr, uid, line_ids)
        return super(PurchaseReqModified, self).write(cr, uid, ids ,vals, context=None)

    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            if formulario.name != '/':
                raise osv.except_osv('Error', 'No pueden eliminar solicitudes que han iniciado proceso')
        return True

#    def write(self, cr, uid, ids, vals, context=None):
#        req_obj = self.pool.get('purchase.requisition')
#        #req_ids = req_obj.search(cr, uid, [()])
#        repetidos = []
#        #for req_id in req_ids:
#            #Buscar el producto de la linea en todas las lineas de pedidos, si encuentra agregar a la lista de repetidos
#            #El mensaje presentado debe ser de toda la lista
#        return super(PurchaseReqModified, self).write(cr, uid, ids, vals, context=None)
#        return True

    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        """
        Create New RFQ for Supplier
        """
        if context is None:
            context = {}
        assert partner_id, 'Debe seleccionar un proveedor'
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        fiscal_position = self.pool.get('account.fiscal.position')
        supplier = res_partner.browse(cr, uid, partner_id, context=context)
        delivery_address_id = res_partner.address_get(cr, uid, [supplier.id], ['delivery'])['delivery']
        supplier_pricelist = supplier.property_product_pricelist_purchase or False
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            if supplier.id in filter(lambda x: x, [rfq.state <> 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
                print "MSG"
#                 raise osv.except_osv(_('Warning'), _('You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % rfq.state)
            location_id = requisition.warehouse_id.lot_input_id.id
            po_ids = len(requisition.purchase_ids)
            #debe tomar la secuencia de PO OJOOOOO
            seq =requisition.name + "-" +str(po_ids)
            purchase_id = purchase_order.create(cr, uid, {
                    'name':seq,
                    'origin': requisition.name,
                    'partner_id': supplier.id,
                    'partner_address_id': delivery_address_id,
                    'pricelist_id': supplier_pricelist.id,
                    'location_id': location_id,
                    'company_id': requisition.company_id.id,
                    'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                    'requisition_id':requisition.id,
                    'warehouse_id':requisition.warehouse_id.id ,
            })
            res[requisition.id] = purchase_id
            for line in requisition.line_ids:
                k = 0
                product = line.product_id
                seller_price, qty, default_uom_po_id, date_planned = self._seller_details(cr, uid, line, supplier, context=context)
#                taxes_ids = product.supplier_taxes_id
                if product.default_code:
                    srt_aux = product.default_code + ' ' + product.name
                else:
                    srt_aux = product.name
                if len(product.supplier_taxes_id)<0:
                     raise osv.except_osv(('Error de configuración'), ('El producto %s no tiene configurado impuestos') %(str_aux))
                taxes_ids = []
                for impuesto in product.supplier_taxes_id:
                    if impuesto.tax_group=="vat" or impuesto.tax_group=="ice":
                        taxes_ids.append(impuesto)
                taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
                #if not requisition.cotizar_all:
                #    qty_stock = product.qty_available
                #    qty = abs(qty_stock - qty)
                if qty>0:
                    k += 1
                    line_desc = ''
                    if line.desc:
                        line_desc = line.desc
                    desc = product.partner_ref+' '+line_desc
                    purchase_order_line.create(cr, uid, {
                            'order_id': purchase_id,
                            'name': desc,
                            'product_qty': qty,
                            'product_id': product.id,
                            'qty_available':product.qty_available,
                            'product_uom': default_uom_po_id,
                            'price_unit': 0,
                            'date_planned': date_planned,
                            'notes': product.description_purchase,
                            'taxes_id': [(6, 0, taxes)],
                            'presp_ref':requisition.presp_ref.id,
                            }, context=context)
                if not k>0:
                    purchase_order.write(cr, uid, purchase_id,{
                            'select':False,
                            })
        return res

    def _get_account_period(self, cr, uid, ids, context=None):
        #sacar el periodo de la fecha de creacion
#        account_fiscalyear_obj = self.pool.get('account.fiscalyear')
#        date = time.strftime('%Y-%m-%d')
        config_obj = self.pool.get('purchase.config.infima')
#        account_fiscalyear_ids = account_fiscalyear_obj.search(cr, uid, [('date_start','<',date),('date_stop','>',date)],limit=1)
        config_ids = config_obj.search(cr, uid, [('activo','=',True)],limit=1)
        if config_ids:
#            config = config_obj.browse(cr, uid, config_ids[0])
            aux = config_ids[0]
            return aux
        else:
            raise osv.except_osv(('Error de configuración'), ('No tiene tabla de infima cuantia activa, por favor configure una'))
        return True
        
    def _get_bodega(self, cr, uid, ids, context=None):
        bodega_obj = self.pool.get('stock.location')
        bodega_ids = bodega_obj.search(cr, uid, [('is_general','=',True)],limit=1)
        if len(bodega_ids)<1:
            raise osv.except_osv(('Error de configuración'), ('No esta definida la bodega general para la recepción'))
        return bodega_ids[0]

    def _get_department(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        return user.context_department_id.id

    def _check_product_bodega(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            a = 0
            if len(this.line_ids)>0:
#                bodega_id = this.line_ids[0].product_id.location_id.id
                for line in this.line_ids:
                    if line.product_id.type in ('product','consu'):
                        if a == 0:
                            bodega_id = line.product_id.location_id_id.id
                            a = 1
                        if line.product_id.location_id_id.id != bodega_id:
                            return False
        return True

#    def _check_product(self, cr, uid, ids):
#        result = True
#        for obj in self.browse(cr, uid, ids):#
#            if obj.product_qty > 0 and obj.price_unit > 0:
#                result = True
#        return result

    def onchange_solicitant_sol(self, cr, uid, ids, solicitant_id, context={}):
        emp_obj = self.pool.get('hr.employee')
        empleado = emp_obj.browse(cr, uid, solicitant_id)
        vals = {}
        if empleado.user_id:
            return {'value':{'department_id':empleado.user_id.context_department_id.id}} 
        else:
            return {'value':{'department_id':empleado.department_id.id}}


    _defaults = dict(
        name = '/',
        active = True,
#        department_id = _get_department,
        unidad_id = _get_bodega,
        contract_object = 'product',
        str_tipos='0',
        date_start = lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
#        tabla_id = _get_account_period,
        )

    _constraints = [
        (_check_product_bodega,'No puede mezclar productos de varias bodegas en la solicitud',[]),
        ] 

PurchaseReqModified()

class purchaseRequisitionLine(osv.Model):
    _inherit = 'purchase.requisition.line'
    _columns = dict(
        desc = fields.char('Características',size=512),
        code = fields.char('Codigo',size=16),
        presp_ref = fields.many2one('crossovered.budget.certificate','Pres. Referecial'),
        partida_id = fields.many2one('crossovered.budget.lines','Partida Presp.'),
        product_uom_id = fields.related('product_id', 'uom_id', type='many2one', relation='product.uom',
                                  string='UDM', store=True, readonly=True),
        state = fields.related('requisition_id', 'state', type='char',
                               string='Solicitud', store=True, readonly=True),
#        qty_aproved = fields.integer('Cant. Aprobada',readonly=True),
        )

    def write(self, cr, uid, id, vals, context=None):
        req_line = self.pool.get('purchase.requisition.line')
        product_obj = self.pool.get('product.product')
        if vals.get('product_id'):
            product = product_obj.browse(cr, uid, vals['product_id'])
            vals['code']=product.default_code,
        return super(purchaseRequisitionLine, self).write(cr, uid, id ,vals, context=None)

    def create(self, cr, uid, vals, context=None):
        req_line = self.pool.get('purchase.requisition.line')
        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, vals['product_id'])
        line_id = super(purchaseRequisitionLine, self).create(cr, uid, vals, context=None)
        req_line.write(cr, uid, line_id,{
                'code':product.default_code,
#                'presp_ref':vals['presp_ref']
                })
        return line_id    

    def onchange_product_id(self, cr, uid, ids, product_id,product_uom_id, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        value = {'product_uom_id': ''}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            value = {'product_uom_id': prod.uom_id.id,'product_qty':1.0,'code':prod.default_code}
        return {'value': value}

    _defaults = dict(
        state = 'draft',
        )

#    _sql_constraints = [
#        ('producto', 'unique (product_id,requisition_id)', 'Debe existir solo una linea por producto!')
#        ]

purchaseRequisitionLine()

