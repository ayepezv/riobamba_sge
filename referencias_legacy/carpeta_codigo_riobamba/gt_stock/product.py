# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import decimal_precision as dp

class cpc(osv.Model):
    _name = 'cpc.code'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            #if record.employee_id.employee_lastname and record.employee_id.name:
            #    name = '%s %s' % (record.employee_id.employee_lastname, record.employee_id.name)
                name = record.name + " - " + record.desc
                res.append((record.id, name))
        return res

    _columns = dict(
        name = fields.char('Código',size=10,required=True),
        desc = fields.char('Descripción',size=256,required=True),
        )

class templateModified(osv.Model):
    _inherit = 'product.template'
    _columns = dict(
        p_a = fields.float('PA'),
        type = fields.selection([('product','Bien'),
                                 ('service','Servicio'),
                                 ('asset','Activo Fijo')],
                                'Product Type', required=True, help="Will change the way procurements are processed. Consumable are product where you don't manage stock."),
        standard_price = fields.float('Cost Price', required=True, digits=(10,10), 
                                      help="Product's cost for accounting stock valuation. It is the base price for the supplier price."),
#        uom_po_id = fields.related('uom_id','id', type='many2one', 
 #                                           relation='product.uom',string='UdMC', store=True)
        )

    _defaults = dict(
        cost_method = 'average',
 #       valuation = 'real_time'
    )

    def write(self, cr, uid, ids, vals, context=None):
        if 'uom_id' in vals:
            vals['uom_po_id']=vals['uom_id']
            vals['uos_id']=vals['uom_id']
        osv.osv.write(self, cr, uid, ids, vals, context=context)
#        return super(templateModified, self).write(cr, uid, ids, vals, context=context)

templateModified()

class productCategory(osv.Model):
    _inherit = 'product.category'
    _columns = dict(
        code = fields.char('Codigo',size=32),
        name = fields.char('Nombre',size=256,required=True),
    )

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            if record.code:
                name = record.code + ' - ' + record.name + ' - ' + record.budget
            else:
                name = record.name + ' - ' + record.budget 
            res.append((record.id, name))
        return res

productCategory()    

class product_subcategory(osv.Model):
    _name = 'product.subcategory'
    _columns = dict(
        account_code = fields.char('Codigo Cuenta',size=64),
        code = fields.char('Codigo',size=32),
        categ_id = fields.many2one('product.category','Categoria',required=True),
        name = fields.char('Nombre',size=64,required=True),
        parent_id = fields.many2one('product.subcategory','Categoria Padre'),
    )
product_subcategory()

class productModified(osv.Model):
    _inherit = 'product.product'

#    def write(self, cr, uid, ids, vals):
#        for this in self.browse(cr, uid, ids):
#            if this.qty_available>0:
#                if vals.has_key('categ_id'):
#                    raise osv.except_osv(('Error !'), ('No se pueden modificar la categoria de un producto con existencias esto afecta al inventario'))
#        return super(productModified, self).write(self, cr, uid, ids, vals)

    def create(self, cr, uid, vals, context):
        parameter_obj = self.pool.get('ir.config_parameter')
        subcateg_obj = self.pool.get('product.subcategory')
        product_obj = self.pool.get('product.product')
        migracion_ids = parameter_obj.search(cr, uid, [('key','=','migracion')],limit=1)
        if migracion_ids:
            migracion = parameter_obj.browse(cr, uid, migracion_ids[0]).value
            if migracion=='Si':
                return super(productModified, self).create(cr, uid, vals, context=None)
        else:
            codigo_ids = parameter_obj.search(cr, uid, [('key','=','codproducto')],limit=1)
            if codigo_ids:
                code_p = parameter_obj.browse(cr, uid, codigo_ids[0]).value
                if code_p=='completo':
                    categ_obj = self.pool.get('product.category')
                    product_obj = self.pool.get('product.product')
                    categoria = categ_obj.browse(cr, uid, vals['categ_id'])
                    if categoria.code:
                        product_ids = product_obj.search(cr, uid, [('categ_id','=',vals['categ_id'])])
                        if product_ids:
                            sequence = len(product_ids)
                        else:
                            sequence = 1
                        aux_armado = str(sequence).zfill(3)
                        code_aux = categoria.code
                        band = True
                        while band:
                            if categoria.parent_id:
                                code_aux += categoria.parent_id.code
                                categoria = categoria.parent_id
                            else:
                                band = False
                        code_aux = code_aux + aux_armado
                        vals['default_code'] = code_aux
                elif code_p=='mil':
                    if vals['type']=='service':
                        obj_sequence = self.pool.get('ir.sequence')
                        vals['default_code'] = obj_sequence.get(cr, uid, 'product.product')
                    else:
                        if vals['subcateg_id']:
                            product_ids = product_obj.search(cr, uid, [('type','!=','service'),('subcateg_id','=',vals['subcateg_id'])],order='code_aux desc')
                            if product_ids:
                                product = product_obj.browse(cr, uid, product_ids[0])
                                code_ant = int(product.default_code[9:])
                                subcateg = subcateg_obj.browse(cr, uid, vals['subcateg_id'])
                                code_aux_sc = subcateg.code
                                aux_next = str(code_ant+1).zfill(5)
                                code_aux = code_aux_sc + '-' + aux_next
                                vals['default_code']=code_aux
                            else:
                                subcateg = subcateg_obj.browse(cr, uid, vals['subcateg_id'])
                                aux_next = str(1).zfill(5)
                                code_aux_sc = subcateg.code
                                code_aux = code_aux_sc + '-' + aux_next
                                vals['default_code']=code_aux
                else:
                    obj_sequence = self.pool.get('ir.sequence')
                    vals['default_code'] = obj_sequence.get(cr, uid, 'product.product')
            else:
                obj_sequence = self.pool.get('ir.sequence')
                vals['default_code'] = obj_sequence.get(cr, uid, 'product.product')
            return super(productModified, self).create(cr, uid, vals, context=None)

    def copy(self, cr, uid, id, default={}, context=None, done_list=[], local=False):
        raise osv.except_osv(('Error de usuario !'), ('No puede duplicar el registros'))    

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name','')
            code = d.get('default_code',False)
            qty = d.get('qty_available','')
            udm = d.get('udm')
            iva = d.get('iva')
            tipo = d.get('tipo')
            categ_id = d.get('categ_id')
            if code:
                name = '[%s] %s [%s] [%s] [%s]' % (code,name,qty,udm,categ_id)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)

        result = []
        for product in self.browse(cr, user, ids, context=context):
            sellers = filter(lambda x: x.name.id == partner_id, product.seller_ids)
            iva = 'SIN IVA'
            aux_categ = ''
            if product.categ_id.budget:
                if product.categ_id.code:
                    aux_categ = product.categ_id.name + ' ' + product.categ_id.budget + ' ' + product.categ_id.code
                else:
                    aux_categ = product.categ_id.name + ' ' + product.categ_id.budget
            if product.supplier_taxes_id:
                for impuesto in product.supplier_taxes_id:
                    if impuesto.tax_group == 'vat':
                        iva = 'CON IVA'
            if sellers:
                for s in sellers:
                    tipo_aux = product.type
                    if tipo_aux == 'product':
                        tipo = 'BIENES'
                    elif tipo_aux == 'asset':
                        tipo = 'ACTIVOS'
                    else:
                        tipo = 'SERVICIOS'
                    mydict = {
                              'id': product.id,
                              'name': product.name,
                              'default_code': product.default_code,
                              'variants': product.variants,
                              'qty_available':product.qty_available,
                              'udm':product.uom_id.name,
                              'iva':iva,
                              'tipo':tipo,
                    'categ_id':aux_categ,
                               }
                    result.append(_name_get(mydict))
            else:
                tipo_aux = product.type
                if tipo_aux == 'product':
                    tipo = 'BIENES'
                elif tipo_aux == 'asset':
                    tipo = 'ACTIVOS'
                else:
                    tipo = 'SERVICIOS'
                mydict = {
                          'id': product.id,
                          'name': product.name,
                          'default_code': product.default_code,
                          'variants': product.variants,
                          'qty_available':product.qty_available,
                          'udm':product.uom_id.name,
                          'iva':iva,
                          'tipo':tipo,
                    'categ_id':aux_categ,
                          }
                result.append(_name_get(mydict))
        return result

#    def name_get(self, cr, uid, ids, context=None):
#        # return product with stock 
#        res = {}
#        for m in self.browse(cr, uid, ids, context=context):
#            if m.default_code:
#                aux = m.default_code + m.name + str(m.qty_available)
#            else:
#                aux = m.name + str(m.qty_available)
#            aux = m.name
 #           res[m.id] = aux
 #       return res.items  

    def _account_expense(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = this.property_account_expense.id 
        return res    

    def _stock_value(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.standard_price * line.qty_available
        return res

    def _get_code_int(self, cr, uid, ids, name, args, context=None):
        res = {}
        for product in self.browse(cr, uid, ids):
            if product.default_code:
                #aux = asset.code.replace('.','')
                #aux1 = aux.replace('-','')
                aux1 = ''
                aux = product.default_code
                tamanio = len(product.default_code)-1
                for i in range(len(product.default_code)):
                    if aux[tamanio] == '-':
                        tamanio += 1
                        break
                    else:
                        tamanio -= 1
                aux1 = aux[tamanio:]
                res[product.id] = aux1
        return res

    _columns = dict(
        pos = fields.boolean('Punto Venta'),
        p_a = fields.float('PA'),
        code_aux = fields.function(_get_code_int, store=True, string='codeInt',type='char',size=128),
        stock_value = fields.function(_stock_value, type="float", store=True,string='Valorado', digits_compute= dp.get_precision('Account')),
        uid_id = fields.many2one('res.users','Usuario'),
        cpc_id = fields.many2one('cpc.code','CPC'),
        expense_account_id = fields.function(_account_expense, type='many2one', relation='account.account',
                                             store=True,string='Acc Expense'),
        id_ext = fields.char('Id. Ext',size=5),
 #       is_siim = fields.boolean('Factura Siim'),
        subcateg_id = fields.many2one('product.subcategory','Subfamilia'),
        budget_id = fields.many2one('budget.post','Partida Presupuestaria Ingreso'),
       # cuenta_id = fields.many2one('account.account','Cuenta Contable'),
        convenio_pago = fields.boolean('Permitir Convenio pago'),
#        modulo_id = fields.many2one('siim.modulo','Modulo'),
        metodo_calculo = fields.selection([('fix','Valor Fijo'),('code','Formula Python')],'Tipo calculo venta',
                                          help='Elija la forma de calculo, si es un valor fijo o se basa en una formula, tabla, ordenanza'),
        formula_calculo = fields.text('Formula calculo',help='Aqui coloque la formula de calculo del monto a cobrar'),
        )

    def _get_uid(self, cr, uid, ids, context=None):
        return uid

    def _check_product_code(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.type in ('service','asset'):
                return True
            code = this.default_code
            if len(code)>7:
                raise osv.except_osv(('Error de usuario'), ('El codigo debe ser maximo de 7 caracteres'))
            if code[2:3] != '_':
                raise osv.except_osv(('Error de usuario'), ('El tercer caracter del codigo debe ser guion bajo'))
        return True

    _constraints = [
        ]     

    _sql_constraints = [('unique_product_code', 'unique(default_code,property_account_expense)', u'El código del bien/servicio es único.')]

    _defaults = dict(
        sale_ok = False,
        uid_id = _get_uid,
        type = 'product',
        )

