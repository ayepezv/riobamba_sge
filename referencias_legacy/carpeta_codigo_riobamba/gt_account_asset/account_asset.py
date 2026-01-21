# -*- coding: utf-8 -*-
##############################################################################
# Mario Chogllo
# mariofchogllo@gmail.com
##############################################################################

import time
from time import strftime
from osv import osv, fields
from tools import ustr
import decimal_precision as dp
import datetime
from datetime import date
from datetime import datetime
from time import strftime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from tools.translate import _ 

def _employee_get(obj, cr, uid, context=None):
    '''
    devuelve el usuario que crea el objeto
    '''
    ids = obj.pool.get('res.users').search(cr, uid, [('id', '=', uid)], context=context)
    return ids and ids[0] or False


class deptAsset(osv.Model):
    _inherit = 'hr.department'
    
    def _get_total_activos(self, cr, uid, ids, name, args, context=None):
        res = {}
        asset_obj = self.pool.get('account.asset.asset')
        aux = 0
        for this in self.browse(cr, uid, ids):
            asset_ids = asset_obj.search(cr, uid, [('department_id','=',this.id)])
            if asset_ids:
                aux = len(asset_ids)
            res[this.id] = aux
        return res

    _columns = dict(
        total_activos = fields.function(_get_total_activos, store=True, string='Total Activos',type='integer'),
    )
deptAsset()

class accountAssetDepLine(osv.Model):
    _inherit = 'account.asset.depreciation.line'

    _columns = dict(
        
        category_id = fields.related('asset_id','category_id', type='many2one',relation="account.asset.category", string='Categoria',readonly=True, store=True),
        state = fields.related('asset_id','state', type='char',size=32,string='Estado',readonly=True, store=True),
        type = fields.related('asset_id','type', type='char',size=32,string='Tipo',readonly=True, store=True),
    )

    def create_move(self, cr, uid, ids, context=None):
        #en ids llega las lineas de depreciacion
        can_close = False
        if context is None:
            context = {}
        dep_line = self.pool.get('account.asset.depreciation.line')
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        category_obj = self.pool.get('account.asset.category')
        journal_obj = self.pool.get('account.journal')
        created_move_ids = []
        categorias = []
        values = {}
        #sacar las categorias
#        aux = '''select category_id from account_asset_depreciation_line group by category_id'''
        aux = '''select category_id from account_asset_depreciation_line,account_asset_category where account_asset_category.id=account_asset_depreciation_line.category_id and account_asset_category.deprecia=True group by category_id'''
        cr.execute(aux)
        for row in cr.fetchall():
            categorias.append(row[0])
        #itero por cada categoria las lineas de depreciacion y acumulamos categorya:valor en diccionario
        for category_id in categorias:
            aux_valor = 0 
            asset_ids = asset_obj.search(cr, uid, [('category_id','=',category_id)])
            if asset_ids:
                for asset_id in asset_ids:
                    asset = asset_obj.browse(cr, uid, asset_id)
#            dep_line_ids = dep_line.search(cr, uid, [('category_id','=',category_id),('id','in',ids)])
#            for dep_line_id in dep_line_ids:
#                line = dep_line.read(cr, uid, dep_line_id,['amount'])
                #calcular el valor en base al numero de anios, valor compra y fecha
#                aux_valor += line['amount']
#            values[category_id]=aux_valor
        #implementa asiento depreciacion
        state_aux = 'draft'
        company_aux = 1
        currency_aux = 2
        depreciation_date = time.strftime('%Y-%m-%d')
        aux_ref = "ASIENTO DE DEPRECIACION - " + depreciation_date
        period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
        journal_ids = journal_obj.search(cr, uid, [('name','=','DIARIO')],limit=1)
        if not journal_ids:
            raise osv.except_osv('Error de configuracion', 'No existe diario con descripcion DIARIO, cree uno')         
        move_vals = {
            'name': '/',
            'date': depreciation_date,
            'ref': aux_ref,
            'period_id': period_ids and period_ids[0] or False,
            'journal_id': journal_ids[0],
            'narration':aux_ref,
            'partner_id':company_aux,
        }
        move_id = move_obj.create(cr, uid, move_vals, context=context)
        for val_line in values:
            categoria = category_obj.browse(cr, uid, val_line)
            aux_amount = values[val_line]
            move_line_obj.create(cr, uid, {
                'name': categoria.name,
                'ref': categoria.name,
                'move_id': move_id,
                'account_id': categoria.account_depreciation_id.id,
                'debit': 0.0,
                'credit': aux_amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_ids[0],
                'currency_id': currency_aux,
                'date': depreciation_date,
            })
            move_line_obj.create(cr, uid, {
                'name': categoria.name,
                'ref': categoria.name,
                'move_id': move_id,
                'account_id': categoria.account_expense_depreciation_id.id,
                'credit': 0.0,
                'debit': aux_amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_ids[0],
                'currency_id': currency_aux,
                'date': depreciation_date,
            })
        created_move_ids.append(move_id)
        return created_move_ids

    def auxDep(self, cr, uid, ids, context):
        for line in self.browse(cr, uid, ids, context=context):
            if currency_obj.is_zero(cr, uid, line.asset_id.currency_id, line.remaining_value):
                can_close = True
            depreciation_date = line.asset_id.prorata and line.asset_id.purchase_date or time.strftime('%Y-%m-%d')
            company_currency = line.asset_id.company_id.currency_id.id
            current_currency = line.asset_id.currency_id.id
            context.update({'date': depreciation_date})
            amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
            sign = line.asset_id.category_id.journal_id.type = 'purchase' and 1 or -1
            asset_name = line.asset_id.name
            reference = line.name
            #esta loco 
            move_vals = {
                'name': '/',
#                'name': asset_name,
                'date': depreciation_date,
                'ref': reference,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': line.asset_id.category_id.journal_id.id,
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            journal_id = line.asset_id.category_id.journal_id.id
            partner_id = line.asset_id.partner_id.id
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and - sign * line.amount or 0.0,
                'date': depreciation_date,
            })
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
                'credit': 0.0,
                'debit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * line.amount or 0.0,
                'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
                'date': depreciation_date,
                'asset_id': line.asset_id.id
            })
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            created_move_ids.append(move_id)
            if can_close:
                asset_obj.write(cr, uid, [line.asset_id.id], {'state': 'close'}, context=context)
        return created_move_ids

accountAssetDepLine()

class noBienes(osv.TransientModel):
    _name = 'asset.no.bienes'
    _columns = dict(
        employee_id = fields.many2one('hr.employee','Funcionario'),
        create_user_id = fields.many2one('res.users','Creado Por'),
    )

    def print_certificado(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        if not context:
            context = {}
        cert = self.browse(cr, uid, ids, context)[0]
        asset_ids = asset_obj.search(cr, uid, [('employee_id','=',cert.employee_id.id),('state','=','open')])
        if asset_ids:
            raise osv.except_osv('Error', 'El funcionario si posse bienes')         
        datas = {'ids' : [cert.id],
                 'model': 'asset.no.bienes'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'no.bienes',
            'model': 'asset.no.bienes',
            'datas': datas,
            'nodestroy': True,            
                }

        def _get_usr(self, cr, uid, ids, context=None):
            return uid

        _defaults = dict(
            create_user_id = _get_usr,
        )

noBienes()

class gt_account_asset_rbodega(osv.osv):
    _description = 'Responsable de bodegas'
    _name = 'gt.account.asset.rbodega' 
    _columns = {'name': fields.many2one('hr.employee', 'Responsable de bodega',required=True), }
    def create(self, cr, uid, vals, context=None):
        """        
            verifica que solo exista un responsable de bodega
        """          
        ids_income=self.pool.get('gt.account.asset.rbodega').search(cr, uid, [], context=context)
        print ids_income
        if len(ids_income)>=1:
            raise osv.except_osv('Error', 'No puede crear mas de un responsable de bodega')         
        res = super(gt_account_asset_rbodega, self).create(cr, uid, vals, context=context)        
        return res
gt_account_asset_rbodega()

class account_asset_transfer_head(osv.Model):
    #transferencia de n activos entre custodios
    _name = 'account.asset.transfer.head'
    _description = 'Account Assets Transfer'
    _order = 'date DESC'
    STATES_VALUE = {'draft': [('readonly', False)]}
    _columns = {'name': fields.char('Código de Transferencia', size=32,readonly=True),
                'document_name': fields.char('Documento', size=64),
                'created_id' : fields.many2one('res.users','Creado por', store=True),                
                'detail': fields.text('Justificacion', required=True),
                'is_asset_unique' :fields.boolean('Transferir activo único'),
                'unique_asset': fields.many2one('account.asset.asset',
                                            string='Activo a Transferir',),
                'transfer_ids': fields.one2many('account.asset.transfer',
                                        'transfer_id',
                                        'Transferencia'),                
                'autorizado_por': fields.many2one('hr.employee', 'Autorizado por',required=True,
                                              readonly=True, states=STATES_VALUE),
                'valor_total': fields.float('Costo', size= 20,readonly=True,),
                'emp_old_id': fields.many2one('hr.employee', 'Custodio Actual',required=True),                
                'emp_new_id': fields.many2one('hr.employee', 'Nuevo Custodio',required=True,
                                              readonly=True, states=STATES_VALUE),
                'emp_new2_id': fields.many2one('hr.employee', 'Nuevo Custodio Secundario',
                                              readonly=True, states=STATES_VALUE),
                'date': fields.date('Fecha de Transferencia', required=True,
                                        states=STATES_VALUE),
                'entidad':fields.char('Persona o Entidad',size=128),
                'tipo':fields.selection([('Entrega','Entrega'),('Devolucion','Devolucion'),('Traspaso','Traspaso'),
                                         ('Comodato','Comodato'),('Donacion','Donacion')],'Tipo'),
                'state': fields.selection([('draft', 'Borrador'),
                                           ('cancel', 'Cancelado'),
                                           ('confirmed', 'Confirmado')],readonly=True,
                                          string='Estado', required=True),}

    _defaults = {
        'state': 'draft',
        'name': '/',
      #  'date': time.strftime('%Y-%m-%d'),
        'created_id': _employee_get,  
        'is_asset_unique':False,  
        'valor_total':0  ,           
        'tipo':'Traspaso',
        }
    
    #_sql_constraints = [('unique_transfer_code', 'unique(name)', u'El código de la transferencia debe ser único')]
    def marcar_assets(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('account.asset.transfer')
        for this in self.browse(cr, uid, ids):
            if this.transfer_ids:
                for line in this.transfer_ids:
                    if line.selected:
                        line_obj.write(cr, uid, line.id,{
                            'selected':False,
                        })
                    else:
                        line_obj.write(cr, uid, line.id,{
                            'selected':True,
                        })
        return True
        
    def cargar_assets(self, cr, uid, ids, context=None):
        #carga todos los activos del custodio
        transfer_obj = self.pool.get('account.asset.transfer')
        for obj in self.browse(cr, uid, ids, context):
            if obj.is_asset_unique==False:
                asset_ids= self.pool.get('account.asset.asset').search(cr, uid, [('employee_id','=', obj.emp_old_id.id),
                                                                                 ('state','in',['open','review','no_depreciate'])
                                                                                ])                      
                if asset_ids:
                    unlink_prop= self.pool.get('account.asset.transfer').search(cr, uid, [('transfer_id','=',obj.id)])
                    self.pool.get('account.asset.transfer').unlink(cr, uid, unlink_prop)
                    for obj_assets in self.pool.get('account.asset.asset').browse(cr, uid, asset_ids, context):
                        #if not obj_assets.department_id.id:
                        #    raise osv.except_osv('Error', 'Es necesario que el custodio tenga registrado un departamento')     
                        if not obj.emp_new_id.department_id.id:
                            raise osv.except_osv('Error', 'Es necesario que el nuevo custodio tenga registrado un departamento')
                        create_id=self.pool.get('account.asset.transfer').create(cr, uid, {'transfer_id': obj.id,
                                                                                           'created_id':obj.created_id.id,
                                                                                           'asset_id':obj_assets.id,
                                                                                           'autorizado_por':obj.autorizado_por.id,
                                                                                           'dep_old_id':obj_assets.department_id.id,
                                                                                           'emp_old_id':obj.emp_old_id.id,
                                                                                           'dep_new_id':obj.emp_new_id.department_id.id,
                                                                                           'emp_new_id':obj.emp_new_id.id,
                                                                                           'detail':ustr(obj.detail),
                                                                                           'state':'draft',
                                                                                           'name':''}, context=None)
            else:
                lineas = transfer_obj.search(cr, uid, [('asset_id','=',obj.unique_asset.id),('transfer_id','=',obj.id)])
                if not lineas:
                    for obj_assets in self.pool.get('account.asset.asset').browse(cr, uid, [obj.unique_asset.id], context):                    
                        create_id=self.pool.get('account.asset.transfer').create(cr, uid, {'transfer_id': obj.id,
                                                                                           'created_id':obj.created_id.id,
                                                                                           'asset_id':obj.unique_asset.id,
                                                                                           'autorizado_por':obj.autorizado_por.id,
                                                                                           'dep_old_id':obj.unique_asset.department_id.id,
                                                                                           'emp_old_id':obj.emp_old_id.id,
                                                                                           'dep_new_id':obj.emp_new_id.department_id.id,
                                                                                           'emp_new_id':obj.emp_new_id.id,
                                                                                           'detail':ustr(obj.detail),
                                                                                           'selected':True,
                                                                                           'state':'draft',
                                                                                           'name':''}, context=None)                                
        #self.write(cr, uid, ids, {'state': 'confirmed'})
        return True    

    def calculate_total(self, cr, uid, ids, context=None):
        #calcula el total del monto de los activos transferidos
        total=0
        for obj in self.browse(cr, uid, ids, context):
            for  transfer_line in obj.transfer_ids:            
                total=total+transfer_line.asset_id.purchase_value
        return total
      
    def transf_confirm(self, cr, uid, ids, context=None):
        #confirma la transferencia del activo, cambia le nombre del custodio y el departamento
        user_obj = self.pool.get('res.users')
        total=0
        for obj in self.browse(cr, uid, ids, context):
            #validar jefa
            user = user_obj.browse(cr, uid, uid)
#            if not uid==user.context_department_id.coordinador_id.user_id.id:
#                raise osv.except_osv('Error', 'Usted no puede ejecutar esta accion')
            if not obj.transfer_ids:
                raise osv.except_osv('Error', 'No existen activos a transferir')
            else:
                for transfer_line in obj.transfer_ids:
                    if transfer_line.selected==True:
                        total=total+transfer_line.asset_id.purchase_value            
                        self.pool.get('account.asset.transfer').transf_confirm(cr, uid, [transfer_line.id], context=None)
                    else:
                        #self.pool.get('account.asset.transfer').write(cr, uid, [transfer_line.id], {'state': 'draft'})
                        self.pool.get('account.asset.transfer').unlink(cr, uid, [transfer_line.id])  
            if not obj.transfer_ids:      
                raise osv.except_osv('Error', 'No  ha seleccionado activos para transferir')                                                     
        self.write(cr, uid, ids, {'state': 'confirmed', 'valor_total':total})
        return True

    def transf_set_anulado(self, cr, uid, ids, context=None):            
        line_obj = self.pool.get('account.asset.transfer')
        for obj in self.browse(cr, uid, ids, context):
            for transfer_line in obj.transfer_ids:
                line_obj.write(cr, uid, transfer_line.id,{
                    'state':'cancel',
                })
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True    

    def transf_reversa(self, cr, uid, ids, context=None):        
        #cancela la transferencia del activo
        line_obj = self.pool.get('account.asset.transfer')
        asset_obj = self.pool.get('account.asset.asset')
        for obj in self.browse(cr, uid, ids, context):
            for transfer_line in obj.transfer_ids:
                asset_obj.write(cr, uid, transfer_line.asset_id.id,{
                    'employee_id':obj.emp_old_id.id,
                    'department_id':obj.emp_old_id.department_id.id,
                })
                line_obj.write(cr, uid, transfer_line.id,{
                    'state':'draft',
                })
        self.write(cr, uid, ids, {'state': 'draft'})
        return True    

    def transf_cancel(self, cr, uid, ids, context=None):        
        #cancela la transferencia del activo
        for obj in self.browse(cr, uid, ids, context):
            for  transfer_line in obj.transfer_ids:            
                self.pool.get('account.asset.transfer').transf_cancel(cr, uid, [transfer_line.id], context=None)         
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True    
    
    def onchange_emp_old_id(self, cr, uid, ids, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        res = {'value': {}}
        res['value'] = {'unique_asset': '',
                        'emp_new_id':''}      
        return res
    '''
    def get_dept_employee(self, cr, uid, ids, id_account_asset, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        res = {'value': {}}
        inform_type_ids= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', id_account_asset)])
        for obj_inform_type in self.pool.get('account.asset.asset').browse(cr, uid, inform_type_ids, context):
            res['value'] = {'dep_old_id': obj_inform_type.department_id.id,
                            'emp_old_id': obj_inform_type.employee_id.id}      
        return res
    '''
    def unlink(self, cr, uid, ids, context=None):
        #no permite eliminar transferencias
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar una transferencia')
        return False    

    def create(self,cr,uid,vals,context=None):
        #crea el activo con el secuencial
        res=[]
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'account.asset.transfer')
        res= super(account_asset_transfer_head,self).create(cr, uid, vals,context=context)
        return res
account_asset_transfer_head()

class account_asset_transfer(osv.Model):
    #transferencia entre custodios de activo
    _name = 'account.asset.transfer'
    _description = 'Account Assets Transfer'
    _order = 'selected DESC'    
    _columns = {'name': fields.related('transfer_id', 'name',readonly=True,type="char",
                                     string="Código",store=True),
                'selected':fields.boolean(''), 
                'created_id' : fields.many2one('res.users','Creado por', store=True, readonly=True, required=True),
                'detail': fields.related('transfer_id', 'detail',readonly=True,type="char",
                                     string="Justificación", store=True ),                
                'autorizado_por': fields.many2one('hr.employee', 'Autorizado por',
                                              readonly=True, required=True),
                'transfer_id': fields.many2one('account.asset.transfer.head',
                                            string='Transferencia',
                                            readonly=True, required=True),
                'asset_id': fields.many2one('account.asset.asset',
                                            string='Activo a Transferir',
                                            readonly=True, required=True),
                'purchase_value': fields.related('asset_id', 'purchase_value',readonly=True,type="float",
                                     string="Valor de Compra" ),
                'dep_old_id': fields.many2one('hr.department', 'Departamento Anterior',
                                              ), 
                'emp_old_id': fields.many2one('hr.employee', 'Custodio Anterior',
                                              required=True, readonly=True),
                'dep_new_id': fields.many2one('hr.department', 'Departamento a Transferir',
                                              readonly=True, required=True),     
                'emp_new_id': fields.many2one('hr.employee', 'Nuevo Custodio',
                                              required=True, readonly=True),
                'date': fields.date('Fecha de Transferencia',
                                    readonly=True, required=True),                
                'state_asset': fields.related('asset_id', 'state',readonly=True,type="selection", string='Estado de activo',
                                        selection=[('draft', 'Borrador'),
                                                   ('open', 'Operativo'),
                                                   ('review', 'En revisión'),
                                                   ('prev_close', 'Baja solicitada'),
                                                   ('no_depreciate', 'Operativo-no depreciable'),
                                                   ('close', 'Dado de baja'),
                                                   ]),
                'state': fields.selection([('draft', 'Borrador'),
                                           ('cancel', 'Cancelado'),
                                           ('confirmed', 'Confirmado')],readonly=True,
                                          string='Estado', required=True),}
    _defaults = {
        'state': 'draft',
        'name': '/',
        'date': strftime('%Y-%m-%d'),
        #'created_id': _employee_get,                 
        }
    
    #_sql_constraints = [('unique_transfer_code', 'unique(name)', u'El código de la transferencia debe ser único')]    
      
    def transf_confirm(self, cr, uid, ids, context=None):
        #confirma la transferencia del activo, cambia le nombre del custodio y el departamento
        for obj_transfer in self.pool.get('account.asset.transfer').browse(cr, uid, ids, context):
            asset_id= obj_transfer.asset_id.id
            if obj_transfer.transfer_id.tipo in ('Comodato','Donacion'):
                self.pool.get('account.asset.asset').write(cr, uid, [asset_id], {'department_id': obj_transfer.dep_new_id.id,
                                                                                 'state2':obj_transfer.transfer_id.tipo,
                                                                                 'employee_id': obj_transfer.transfer_id.emp_new_id.id,},context)
            else:
                self.pool.get('account.asset.asset').write(cr, uid, [asset_id], {'department_id': obj_transfer.dep_new_id.id,
                                                                                 'employee_id': obj_transfer.transfer_id.emp_new_id.id,},context)
            move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'transferencia'}, context=None)
            self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': asset_id,'move_id':move_id}, context=None)
            ##self.pool.get('gt.account.asset.moves').create(cr, uid, {'asset_id': ids[0],'type':'transferencia'}, context=None)         
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True
    
    def transf_cancel(self, cr, uid, ids, context=None):        
        #cancela la transferencia del activo
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True    
    '''
    def get_dept_employee(self, cr, uid, ids, id_account_asset, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        res = {'value': {}}
        inform_type_ids= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', id_account_asset)])
        for obj_inform_type in self.pool.get('account.asset.asset').browse(cr, uid, inform_type_ids, context):
            res['value'] = {'dep_old_id': obj_inform_type.department_id.id,
                            'emp_old_id': obj_inform_type.employee_id.id}      
        return res
    '''
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state !='draft':
                raise osv.except_osv('Error', 'No puede eliminar una transferencia')                
        return osv.osv.unlink(self, cr, uid, ids, context=context)    

   # def create(self,cr,uid,vals,context=None):
   #     res=[]
   #     vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'account.asset.transfer')
   #     res= super(account_asset_transfer,self).create(cr, uid, vals,context=context)
   #     return res
account_asset_transfer()

class assetSubcateg(osv.Model):
    _name = 'asset.asset.subcateg'

    def create(self, cr, uid, vals, context):
        sub_obj = self.pool.get('asset.asset.subcateg')
        if vals.has_key('parent_id') and vals['parent_id']!=False:
            parent = sub_obj.browse(cr, uid, vals['parent_id'])
            if parent.code:
                len_aux = len(parent.code) - 4
                aux_subcode = parent.code
                sub_ids = sub_obj.search(cr, uid, [('code','like',aux_subcode),('categ_id','=',vals['categ_id'])])
                if sub_ids:
                    seq = len(sub_ids)
                else:
                    seq = 1
                aux_sec = str(seq).zfill(4)
                vals['code'] = parent.code + '.' + aux_sec
        return super(assetSubcateg, self).create(cr, uid, vals, context=None)

    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_cedula = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_cedula))
        if name:
            ids_name = self.search(cr, uid, [('code', operator, name)] + args, limit=limit, context=context)
            ids = list(set(ids + ids_name))
        return self.name_get(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            if record.code:
                name = record.code + ' - ' + record.name
            else:
                name = record.name
            res.append((record.id, name))
        return res

    _columns = dict(
        parent_id = fields.many2one('asset.asset.subcateg','Familia Padre'),
        cuenta_contable = fields.char('CC',size=32),
#        cuenta_contable = fields.related('account_id', 'code_aux',readonly=True,type="char",size=32,
#                                         string="Cuenta Contable", store=True ),
        #        account_id = fields.related('categ_id','cuenta_ingreso',type='many2one',relation='account.account',string='Cuenta'),
        type_asset = fields.selection([('sujeto_control','Bien Sujeto a Control'),('Ambos','Ambos'),
                                       ('larga_duracion','Bien de Larga Duración')], string='Tipo'),
        code = fields.char('Codigo',size=32),
        categ_id = fields.many2one('account.asset.category','Familia',required=True),
        name = fields.char('Nombre',size=32),
        )
assetSubcateg()

class AccountAssetProperty(osv.Model):
    _name = 'account.asset.property'
    _description = 'Properties Assets'   
     
    def get_by_name(self, cr, uid, name):
        """
        Metodo que devuelve el valor de una propiedad
        @name: propiedad a buscar
        return: valor encontrado caso contrario False
        """
        res_ids = self.search(cr, uid, [('name','=',name)], limit=1)
        if not res:
            return False
        data = self.read(cr, uid, res_ids[0], ['value'])
        return data['value'] 
    
    _columns = dict(      
        name = fields.many2one('gt.tipo.properties', 'Propiedad', required=True),
        value = fields.char('Valor', size=128),
        needed_field = fields.related('name', 'all_asset',readonly=True,type="boolean",
                                             string="Requerido", store=True ),        
        asset_id = fields.many2one('account.asset.asset', 'Activo Fijo'),        
        )
        
AccountAssetProperty()  
  
class assetDonar(osv.TransientModel):
    _name = 'account.asset.donar'
    _columns = dict(
        name = fields.text('Justificación', required=True),               
        state = fields.selection([('Donacion','Donacion'),('Comodato','Comodato')],'Estado'),
        asset_id = fields.many2one('account.asset.asset','Activo', required=True),                     
    )

    def asignar_justificacion_donar(self, cr, uid, ids, context):
        datos=[]
        message=original_message=message_=''
        for obj in self.browse(cr, uid, ids, context):
            id_activo=context.get('active_id')
            asset_id= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', id_activo)])
            user_id= obj.pool.get('res.users').search(cr, uid, [('id', '=', uid)], context=context)
            for usuarios in self.pool.get('res.users').browse(cr, uid, user_id, context):
                user_name= usuarios.name        
            for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid,asset_id, context):
                if  obj_asset.low_reason:
                    original_message=obj_asset.low_reason
                message = 'Modificado:  ' + str(time.strftime('%Y-%m-%d %H:%M:%S'),) + ustr('\nJustificación:  ') +ustr(obj.name)+'\n\n'            
            message_= ustr (original_message)+ustr(message)
        datos = {'message_': message_,
                 'message': message,
                 'asset_id': asset_id,}
        return datos

    def action_donar_asset(self, cr, uid, ids, context):
        #Justificación para el botón en revisión
        datos=self.asignar_justificacion_donar(cr, uid, ids, context)                     
        self.pool.get('account.asset.asset').write_activos_(cr, uid, datos['asset_id'], {'low_reason':datos['message_'],
                                                                                         'new_low_reason':datos['message'],'justific':True}, context)
        for this in self.read(cr, uid, ids):
            self.pool.get('account.asset.asset').write(cr, uid,datos['asset_id'], 
                                                       {
                                                           'state2': this['state'],
                                                       },context=context)  
        return {'type':'ir.actions.act_window_close'}
        return True 

    def _get_asset_donar(self, cr, uid, context): 
        asset_id=''
        id_activo=context.get('active_id')
        asset_ids= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', id_activo)])
        for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid, asset_ids):
            asset_id= obj_asset.id
        return asset_id  

    _defaults = dict(
        asset_id = _get_asset_donar,
    ) 
assetDonar()

class gt_account_asset_justificacion(osv.osv_memory):
    '''
    pide una justificacion para cada acciohn en activos
    '''
    _name = 'gt.account.asset.justificacion'
    _description = 'Solicita justificacion para modificar activos' 
    _columns = {
                'name': fields.text('Justificación', required=True),               
                'asset_id' : fields.many2one('account.asset.asset','Activo', required=True),                     
        }

    def get_asset_id(self, cr, uid, context): 
        #carga el nombre de la Póliza
        asset_id=''
        id_activo=context.get('active_id')
        asset_ids= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', id_activo)])
        for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid, asset_ids):
            asset_id= obj_asset.id
        return asset_id  

    def asignar_justificacion(self, cr, uid, ids, context):
        #permite asignar la justificación para cada una de las acciones
        datos=[]
        message=original_message=message_=''
        for obj in self.browse(cr, uid, ids, context):
            id_activo=context.get('active_id')
            asset_id= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', id_activo)])
            user_id= obj.pool.get('res.users').search(cr, uid, [('id', '=', uid)], context=context)
            for usuarios in self.pool.get('res.users').browse(cr, uid, user_id, context):
                user_name= usuarios.name        
            for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid,asset_id, context):
                if  obj_asset.low_reason:
                    original_message=obj_asset.low_reason
                message = 'Modificado:  ' + str(time.strftime('%Y-%m-%d %H:%M:%S'),) + ustr('\nJustificación:  ') +ustr(obj.name)+'\n\n'            
            message_= ustr (original_message)+ustr(message)
        datos = {'message_': message_,
                 'message': message,
                 'asset_id': asset_id,}
        return datos

    def action_validate_asset(self, cr, uid, ids, context):
        #Justificación para el botón confirmar activo
        datos=self.asignar_justificacion(cr, uid, ids, context)                
        self.pool.get('account.asset.asset').write_activos_(cr, uid, datos['asset_id'], {'low_reason':datos['message_'],'new_low_reason':datos['message'],'justific':True}, context)
        self.pool.get('account.asset.asset').validate(cr, uid, datos['asset_id'], context=None)        
        return {'type':'ir.actions.act_window_close'}
        return True 
    
    def action_low_asset(self, cr, uid, ids, context):
        #Justificación para el botón dar de baja
        datos=self.asignar_justificacion(cr, uid, ids, context)                        
        self.pool.get('account.asset.asset').write_activos_(cr, uid, datos['asset_id'], {'low_reason':datos['message_'],'new_low_reason':datos['message'],'justific':True}, context)
        self.pool.get('account.asset.asset').set_to_low(cr, uid, datos['asset_id'], context=None)
        return {'type':'ir.actions.act_window_close'}
        return True 
    
    def action_low_asset_previo(self, cr, uid, ids, context):
        #Justificación para el botón solicitar baja
        datos=self.asignar_justificacion(cr, uid, ids, context)                        
        self.pool.get('account.asset.asset').write_activos_(cr, uid, datos['asset_id'], {'low_reason':datos['message_'],'new_low_reason':datos['message'],'justific':True}, context)
        self.pool.get('account.asset.asset').set_to_low_previo(cr, uid, datos['asset_id'], context=None)
        return {'type':'ir.actions.act_window_close'}
        return True
    
    def action_review_asset(self, cr, uid, ids, context):
        #Justificación para el botón en revisión
        datos=self.asignar_justificacion(cr, uid, ids, context)                     
        self.pool.get('account.asset.asset').write_activos_(cr, uid, datos['asset_id'], {'low_reason':datos['message_'],'new_low_reason':datos['message'],'justific':True}, context)
        self.pool.get('account.asset.asset').write(cr, uid,datos['asset_id'], {'state': 'review'}, context=context)  
        return {'type':'ir.actions.act_window_close'}
        return True 
    
    def delete_account(self, cr, uid, ids, context=None):
        #no permite modificar el estado del activo si el asiento ha sido contabilizado
        for obj in self.browse(cr,uid,ids,context):
            for obj_asset in self.pool.get('account.asset.asset').browse(cr,uid,[obj.asset_id.id],context):
                if obj_asset:
                    move_ids=self.pool.get('account.move').search(cr, uid, [('asset_id','=', obj_asset.id)])
                    if move_ids:
                        for obj_move in self.pool.get('account.move').browse(cr,uid,move_ids,context):
                            if obj_move.state=='draft':
                                unlink_prop= self.pool.get('account.move.line').search(cr, uid, [('move_id','=',obj_move.id)])
                                self.pool.get('account.move.line').unlink(cr, uid, unlink_prop)
                                self.pool.get('account.move').unlink(cr, uid, [obj_move.id])
                            else:
                                raise osv.except_osv('Error', 'Para cambiar el estado del activo debe cancelar el asiento existente')
        return True
    
    def action_draft_asset(self, cr, uid, ids, context):
        #Justificación para el botón en dar de baja
        self.delete_account(cr, uid, ids, context)
        datos=self.asignar_justificacion(cr, uid, ids, context)                        
        self.pool.get('account.asset.asset').write_activos_(cr, uid, datos['asset_id'], {'low_reason':datos['message_'],'new_low_reason':datos['message'],'justific':True}, context)        
        self.pool.get('account.asset.asset').set_to_draft(cr, uid, datos['asset_id'], context=None)
        return {'type':'ir.actions.act_window_close'}
        return True           
    
    _defaults = {
                 'asset_id':get_asset_id,
                 } 


class logDeprecia(osv.Model):
    _name = 'log.deprecia'
    _columns = dict(
        asset_id = fields.many2one('account.asset.asset','Activo Fijo'),
        date = fields.date('Fecha'),
        line_id = fields.many2one('account.asset.depreciation.line','Ref. Linea Depreciacion'),
        desc = fields.char('Detalle Log',size=128),
        anterior = fields.float('Anterior'),
        valor = fields.float('Valor'),
        actual = fields.float('Actual'),
    )
logDeprecia()
class assetArea(osv.Model):
    _name = 'asset.area'
    _columns = dict(
        name = fields.char('Area',size=256),
    )
assetArea()
class assetSeccion(osv.Model):
    _name = 'asset.seccion'
    _columns = dict(
        name = fields.char('Seccion',size=256),
    )
assetSeccion()
class assetSubseccion(osv.Model):
    _name = 'asset.subseccion'
    _columns = dict(
        name = fields.char('Subseccion',size=256),
    )
assetSubseccion()
class assetDestino(osv.Model):
    _name = 'asset.destino'
    _columns = dict(
        name = fields.char('Destino',size=256),
    )
assetDestino()

class assetDireccion(osv.Model):
    _name = 'asset.direccion'
    _columns = dict(
        name = fields.char('Direccion',size=256),
    )
assetDireccion()

class assetActividad(osv.Model):
    _name = 'asset.actividad'
    _columns = dict(
        name = fields.char('Actividad',size=128),
    )
assetActividad()

class assetEstructura(osv.Model):
    _name = 'asset.estructura'
    _columns = dict(
        name = fields.char('Estructura',size=128),
    )
assetEstructura()

class assetMotivo(osv.Model):
    _name = 'asset.motivo'
    _columns = dict(
        name = fields.char('Motivo',size=64,required=True),
    )
assetMotivo()
class account_asset(osv.Model):
    _inherit = 'account.asset.asset'       

    def copy(self, cr, uid, id, default={}, context=None, done_list=[], local=False):
        raise osv.except_osv(('Error de usuario !'), ('No puede duplicar el registros'))

    def action_reactivar(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, [this.id],{
                'state':'draft',
            })
        return True

    def action_asset(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'modificacion','name':this.code,'cause':'Reactivacion'}, context=None)
            self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': this.id,'move_id':move_id}, context=None)
            self.write(cr, uid, this.id,{
                'state':'draft',
            })
        return True

    def updateDepre(self, cr, uid, ids, context=None):
        return True
        asset_obj = self.pool.get('account.asset.asset')
        asset_ids = asset_obj.search(cr, uid, [('state','=','open')])
        if asset_ids:
            for asset_id in asset_ids:
                asset = asset_obj.browse(cr, uid, asset_id)
                if asset.salvage_value==0:
                    aux_new = (asset.purchase_value * 0.10)
                    asset_obj.write(cr, uid, asset_id,{
                        'salvage_value':aux_new,
                    })
                self.compute_depreciation_board(cr, uid, [asset_id], context=context)
        return True

    def onchange_pv(self, cr, uid, ids, valor, context={}):
        vals = {}
        aux = valor * 0.10
        return {'value':{'salvage_value':aux}} 

    def name_get(self, cr, uid, ids, context=None):        
        # el name_ger devuelve el Código del activo, (el name no es único)
        if not len(ids):
            return []
        res = []
        for record in self.read(cr, uid, ids, ['id','code','name'], context=context):
            try:
                aux = ustr(record['code']) +'/'+ ustr(record['name'])
                res.append((record['id'], aux ))
            except:
                pass
        return res
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        # devuelve el nombre y código del activo
        ids = []
        ids_descrip = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_descrip))
        if name:
            code = self.search(cr, uid, [('code', operator, name)] + args, limit=limit, context=context)           
            ids = list(set(ids + code))
        return self.name_get(cr, uid, ids, context=context)
    
    def create_account_egreso(self, cr, uid, ids,ref, context=None):
        # crea el asiento de egreso del activo
        invoice_id=partner_id=''
        move_ids=self.pool.get('gt.account.asset.moves.relation').search(cr, uid, [('id','=', ref)])
        for obj_move in self.pool.get('gt.account.asset.moves.relation').browse(cr,uid,move_ids,context):
            reference=obj_move.name
            justific=obj_move.cause
        for obj in self.pool.get('account.asset.asset').browse(cr,uid,ids,context):
            values={'ref':reference,'journal_id':obj.category_id.journal_id.id,'name':obj.name, 'asset_id':obj.id}
            move_id=self.pool.get('account.move').create(cr, uid, values, context=None)
            line_baja={'name':obj.name,
                         'ref':reference,
                         'account_id':obj.category_id.cuenta_baja.id,
                         'debit':'',
                         'credit':obj.purchase_value,
                         'quantity':1,
                         'move_id':move_id,
                         'statement_id':'',
                         'narration':obj.name,
                         }
            line_ingreso={'name':obj.name,
                         'ref':reference,
                         'account_id':obj.category_id.cuenta_ingreso.id,
                         'debit':obj.purchase_value,
                         'credit':'',
                         'quantity':1,
                         'move_id':move_id,
                         'statement_id':'',
                         'narration':obj.name,
                         }
            line_ids=self.pool.get('account.move.line').create(cr, uid, line_baja, context=None)                    
            line_ids=self.pool.get('account.move.line').create(cr, uid, line_ingreso, context=None)
        return True       
    
    def reload_codenr(self, cr, uid, ids, context={}):
        asset_obj = self.pool.get('account.asset.asset')
        asset_ids = asset_obj.search(cr, uid, [])
        if asset_ids:
            for asset_id in asset_ids:
                asset = asset_obj.browse(cr, uid, asset_id)
                code_ant = asset.code
                inicio = code_ant.find('-')
                code_a = code_ant[:inicio]
                code_aux = code_ant[inicio+1:]
                fin = code_aux.find('-')
                code_aux_2 = code_aux[fin+1:]
                code_new  = code_a + '-' +code_aux_2
                asset_obj.write(cr, uid, asset_id,{
                    'code_ant':code_ant,
                    'code':code_new,
                })
                print "ant y nuevo", code_ant,code_new
        return True

    def validate_activo(self, cr, uid, ids, context={}):
        # coloca el activo en estado abierto, y genera el codigo
        asset_obj = self.pool.get('account.asset.asset')
        code_val=sequence=False
        unique_asset=False
        for obj in self.browse(cr, uid, ids, context):
            if obj.purchase_value<=0:
                raise osv.except_osv(('Error de usuario !'), ('El valor de compra debe ser mayor a cero'))
            code_val= obj.code           
            if obj.parent_id==False or obj.parent_id=='':
                unique_asset=True
            if not obj.code:
                obj_sequence = self.pool.get('ir.sequence')
                aux_secuencia = obj_sequence.get(cr, uid, 'account.asset')
            else:
                aux_secuencia = obj.secuencia
            if not obj.type == 'Larga Duracion':
                if not obj.code:
                    code_aux = ustr(self.generate_code_aux(cr, uid, obj))+'-'+ustr(sequence)
                    sequence= self.generate_sequence(cr, uid,obj)
                    parameter_obj = self.pool.get('ir.config_parameter')
                    asset_obj = self.pool.get('account.asset.asset')
                    codifica = '0'
                    codifica_ids = parameter_obj.search(cr, uid, [('key','=','activocode')],limit=1)
                    if codifica_ids:
                        codifica = parameter_obj.browse(cr, uid, codifica_ids[0]).value
                    if codifica=='Basic':
                        code = ustr(self.generate_code(cr, uid, obj))+'.'+ustr(sequence)
                        aux_secuencia = sequence
                    elif codifica =='S':
                        code = ustr(self.generate_code(cr, uid, obj))+'.'+ustr(sequence)
                    elif codifica=='O':
                        code = ustr(self.generate_code(cr, uid, obj))+'.'+ustr(sequence)
                    else:
                        code = ustr(self.generate_code(cr, uid, obj))+'-'+ustr(sequence)
                    move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {
                            'type':'secuencial_ingreso',
                            'name':sequence
                            }, context=None)
                    self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {
                            'asset_id': int(ids[0]),'move_id':move_id
                            }, context=None)
                    if unique_asset==True:
                        return self.write(cr, uid, ids, {'state':'open', 'code': code,'family':code,code_aux:code_aux,'secuencia':aux_secuencia}, context)
                    else:
                        return self.write(cr, uid, ids, {'state':'open', 'code': code,code_aux:code_aux,'secuencia':aux_secuencia}, context)
                else:
                    if unique_asset==True:
                        return self.write(cr, uid, ids, {'state':'open', 'family':code,'secuencia':aux_secuencia}, context)
                    else:
                        return self.write(cr, uid, ids, {'state':'open','secuencia':aux_secuencia}, context)
            else:
                #if obj.purchase_value>=obj.income_id.cost:
                if not obj.code:
                    sequence= self.generate_sequence(cr, uid,obj)
                    parameter_obj = self.pool.get('ir.config_parameter')
                    asset_obj = self.pool.get('account.asset.asset')
                    codifica = '0'
                    codifica_ids = parameter_obj.search(cr, uid, [('key','=','activocode')],limit=1)
                    if codifica_ids:
                        codifica = parameter_obj.browse(cr, uid, codifica_ids[0]).value
                    if codifica=='Basic':
                        code = ustr(self.generate_code(cr, uid, obj))+'.'+ustr(sequence)
                    elif codifica =='S':
                        code = ustr(self.generate_code(cr, uid, obj))+'.'+ustr(sequence)
                    elif codifica=='O':
                        code = ustr(self.generate_code(cr, uid, obj))+'.'+ustr(sequence)
                    elif codifica=='M':
                        code = ustr(self.generate_code(cr, uid, obj))+'-'+ustr(sequence)
                    else:
                        code = ustr(self.generate_code(cr, uid, obj))+'-'+ustr(sequence)
                    code_aux = ustr(self.generate_code_aux(cr, uid, obj))+'-'+ustr(sequence)
                    #code = ustr(self.generate_code(cr, uid, obj))+'.'+ustr(sequence)                           
                #else:
                #    raise osv.except_osv('Error', 'El tipo de Transacción exige que el valor de compra sea mayor a    ' +str(obj.income_id.cost))
            #secuencia de ingreso
        #busco si hay activos ya con ese codigo si lo hay raise
        if not obj.code:
            asset_igual_ids = asset_obj.search(cr, uid, [('code','=',code)])
            if asset_igual_ids:
                raise osv.except_osv('Error', 'Existe ya un activo con ese codigo, el codigo es unico ' +str(code))
        else:
            asset_igual_ids = asset_obj.search(cr, uid, [('code','=',obj.code),('id','!=',obj.id)])
            if asset_igual_ids:
                raise osv.except_osv('Error', 'Existe ya un activo con ese codigo, el codigo es unico ' +str(obj.code))
        if not code_val:
            move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'secuencial_ingreso','name':sequence}, context=None)
            #self.create_account_ingreso(cr, uid, ids,sequence, context)
            self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': int(ids[0]),'move_id':move_id}, context=None)
            if unique_asset==True:
                ##self.pool.get('gt.account.asset.moves').create(cr, uid, {'asset_id': int(ids[0]),'type':'secuencial_ingreso','name':sequence}, context=None) 
                return self.write(cr, uid, ids, {'state':'open', 'code': code,'family':code,'code_aux':code_aux,'secuencia':sequence}, context)
            else:
                return self.write(cr, uid, ids, {'state':'open', 'code': code,'code_aux':code_aux,'secuencia':sequence}, context)
        else:
            #self.create_account_ingreso(cr, uid, ids,'Activo reconfirmado', context)
            res= self.write(cr, uid, ids, {'state':'open','secuencia':sequence}, context)            
            return res

    def validate(self, cr, uid, ids, context={}):
        # llama al proceso que valida para confirmar activo
        return self.validate_activo(cr, uid, ids, context)
    
    def onchange_country(self, cr, uid, ids, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        res = {'value': {}}
        res['value'] = {'state_id': '',
                        'parroquia': '',
                        'canton_id':''}      
        return res 
    
    def onchange_state_id(self, cr, uid, ids, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        res = {'value': {}}
        res['value'] = {'parroquia': '',
                        'canton_id':''}      
        return res      
    
    def onchange_canton_id(self, cr, uid, ids, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        res = {'value': {}}
        res['value'] = {'parroquia': '',
                        }      
        return res

    def onchange_departamento(self, cr, uid, ids, department_id):
        return {'value': {'employee_id': False}}
        
    def generate_sequence(self, cr, uid,obj):
        # devuelve secuencia para code
        parameter_obj = self.pool.get('ir.config_parameter')
        asset_obj = self.pool.get('account.asset.asset')
        codifica = '0'
        codifica_ids = parameter_obj.search(cr, uid, [('key','=','activocode')],limit=1)
        if codifica_ids:
            codifica = parameter_obj.browse(cr, uid, codifica_ids[0]).value
        if codifica=='Basic':
            vacio = "'" + "'"
            sql = '''select id from account_asset_asset where category_id=%s and code!=%s order by secuencia desc''' % (obj.category_id.id,vacio)
#            sql = '''select id,cast(code_int as int) from account_asset_asset where category_id=%s and code!=%s order by code_int desc''' % (obj.category_id.id,vacio)
            cr.execute(sql)
            #import pdb
            #pdb.set_trace()
            asset_ids = cr.fetchall()
            if asset_ids:
                sequence_num = len(asset_ids)+1#int(asset_ids[0][1]) + 1
#                ultimo_activo = asset_obj.browse(cr, uid, asset_ids[0][0])
#                len_aux = len(ultimo_activo.code) - 4
#                code_aux = int(ultimo_activo.code[len_aux:].replace('.',''))
#                sequence_num = code_aux + 1
            else:
                sequence_num = 1 
            aux_sec = str(sequence_num).zfill(5)
        elif codifica=='S':  #RI
            #asset_ids = asset_obj.search(cr, uid, [('subcateg_id','=',obj.subcateg_id.id),('code','!=','')],order='code_int')
            vacio = "'" + "'"
            sql = '''select id,cast(code_int as int) from account_asset_asset where subcateg_id=%s and code!=%s order by code_int desc''' % (obj.subcateg_id.id,vacio)
            cr.execute(sql)
            asset_ids = cr.fetchall()
            if asset_ids:
                sequence_num = int(asset_ids[0][1]) + 1
#                ultimo_activo = asset_obj.browse(cr, uid, asset_ids[0][0])
#                len_aux = len(ultimo_activo.code) - 4
#                code_aux = int(ultimo_activo.code[len_aux:].replace('.',''))
#                sequence_num = code_aux + 1
            else:
                sequence_num = 1 
            aux_sec = str(sequence_num).zfill(3)
        elif codifica=='O':  #LI
            asset_ids = asset_obj.search(cr, uid, [('subcateg_id','=',obj.subcateg_id.id)])
            sequence_num = len(asset_ids) + 1
            aux_sec = str(sequence_num).zfill(4)
        elif codifica=='M': #MIL
            asset_ids = asset_obj.search(cr, uid, [('category_id','=',obj.category_id.id),('state','!=','draft')],order='code_sec_aux desc')
            if asset_ids:
                last_asset = asset_obj.browse(cr, uid, asset_ids[0])
                last_num = int(last_asset.code[4:])
                sequence_num = last_num+1
                aux_sec = sequence_num
            else:
                aux_sec = 1
        else: #NR - EM
            sequence_num = self.pool.get('ir.sequence').get(cr, uid, 'account.asset')        
            aux_sec = sequence_num
        return aux_sec

    def generate_code_aux(self, cr, uid, asset):
        # genera el código del activo cuando el activo es colocado en estado operativo
        #sequence_num = self.pool.get('ir.sequence').get(cr, uid, 'account.asset')
        if asset.employee_id.department_id.sequence:
            if asset.category_id.code:
                code = asset.category_id.code + '-'
                aux = code
            else:
                raise osv.except_osv(('Error de configuracion !'), ('La categoria de activo fijo no tiene codigo asignado '))
        else:
            raise osv.except_osv(('Error de configuracion !'), ('El departamento no tiene codigo asignado'))
        return aux       

    def generate_code(self, cr, uid, asset):
        # genera el código del activo cuando el activo es colocado en estado operativo
        #sequence_num = self.pool.get('ir.sequence').get(cr, uid, 'account.asset')
        parameter_obj = self.pool.get('ir.config_parameter')
        codifica = '0'
        codifica_ids = parameter_obj.search(cr, uid, [('key','=','activocode')],limit=1)
        if codifica_ids:
            codifica = parameter_obj.browse(cr, uid, codifica_ids[0]).value
        if asset.employee_id.department_id.sequence:
            if asset.category_id.code:
                if codifica=='Basic':
                    if asset.category_id.code:
                        categoria_code = asset.category_id.code
                    else:
                        raise osv.except_osv(('Error de configuracion !'), ('La categoria de activo no tiene codigo '))
                    aux = categoria_code
                elif codifica=='S':
                    if asset.category_id.code:
                        categoria_code = asset.category_id.code
                    else:
                        raise osv.except_osv(('Error de configuracion !'), ('La categoria de activo no tiene codigo '))
                    if asset.subcateg_id.code:
                        code_familia = asset.subcateg_id.code
                    else:
                        raise osv.except_osv(('Error de configuracion !'), ('La Sub categoria de activo no tiene codigo '))
                    aux = categoria_code + '.' + code_familia
                elif codifica=='O':
                    code_familia = asset.subcateg_id.code
                    aux = code_familia
                    aux = aux[0:3] + '.' + aux[3:6] + '.' + aux[6:9]
                elif codifica=='M':
                    code_familia = asset.category_id.code[7:].replace('.','')
                    aux = code_familia
                else:
                    cen = asset.employee_id.department_id.sequence
                    code = asset.category_id.code + '-'
                    aux = code + cen
            else:
                raise osv.except_osv(('Error de configuracion !'), ('La categoria de activo fijo no tiene codigo asignado '))
        else:
            raise osv.except_osv(('Error de configuracion !'), ('El departamento no tiene codigo asignado'))
        return aux  
    
    def _amount_residual_actual(self, cr, uid, ids, name, args, context=None):
        cr.execute("""SELECT
                l.asset_id as id, round(SUM(abs(l.debit-l.credit))) AS amount
            FROM
                account_move_line l
            WHERE
                l.asset_id IN %s GROUP BY l.asset_id """, (tuple(ids),))
        res=dict(cr.fetchall())
        for asset in self.browse(cr, uid, ids, context):
            res[asset.id] = asset.purchase_value - res.get(asset.id, 0.0) - asset.depreciacion
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    def _get_account_asset(self, cr, uid, ids, name, args, context=None):
        res = {}
        for asset in self.browse(cr, uid, ids):
            if asset.category_id:
                res[asset.id] = asset.category_id.cuenta_ingreso.code_aux
        return res

    def _get_prcAnual(self, cr, uid, ids, name, args, context=None):
        res = {}
        for asset in self.browse(cr, uid, ids):
            if asset.method_number:
                res[asset.id] = 100.00/float(asset.method_number)
        return res

    def _get_prcMensual(self, cr, uid, ids, name, args, context=None):
        res = {}
        for asset in self.browse(cr, uid, ids):
            if asset.method_number:
                res[asset.id] = 100.00/(float(asset.method_number)*12)
        return res

    def _get_codesec(self, cr, uid, ids, name, args, context=None):
        res = {}
        for asset in self.browse(cr, uid, ids):
            if asset.code:
                aux = asset.code.replace('-','')
                if aux.isdigit():
                    res[asset.id] = int(aux)
        return res

    def _get_codeint(self, cr, uid, ids, name, args, context=None):
        res = {}
        for asset in self.browse(cr, uid, ids):
            if asset.code:
                #aux = asset.code.replace('.','')
                #aux1 = aux.replace('-','')
                aux1 = ''
                aux = asset.code
                tamanio = len(asset.code)-1
                for i in range(len(asset.code)):
                    if aux[tamanio] == '.':
                        tamanio += 1
                        break
                    else:
                        tamanio -= 1
                aux1 = aux[tamanio:]
                res[asset.id] = aux1
        return res

    def _compute_board_undone_dotation_nb(self, cr, uid, asset, depreciation_date, total_days, context=None):
        if asset.method_number >= asset.category_id.method_number:
            undone_dotation_number = asset.method_number
        else:
            undone_dotation_number = asset.category_id.method_number
        if asset.method_time == 'end':
            end_date = datetime.strptime(asset.method_end, '%Y-%m-%d')
            undone_dotation_number = 0
            while depreciation_date <= end_date:
                depreciation_date = (datetime(depreciation_date.year, depreciation_date.month, depreciation_date.day) + relativedelta(months=+asset.method_period))
                undone_dotation_number += 1
        if asset.prorata:
            undone_dotation_number += 1
        return undone_dotation_number-1

    def _compute_board_amount(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None):
        #by default amount = 0
        amount = 0
        if asset.method_number<=0:
            return amount
        if i == undone_dotation_number:
            amount = residual_amount
        else:
            if asset.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if asset.prorata:
                    if asset.method_number >= asset.category_id.method_number:
                        amount = amount_to_depr / asset.method_number
                    else:
                        amount = amount_to_depr / asset.category_id.method_number
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        days += 1
                        amount = (amount_to_depr / asset.method_number) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (amount_to_depr / asset.method_number) / total_days * (total_days - days)
            elif asset.method == 'degressive':
                amount = residual_amount * asset.method_progress_factor
                if asset.prorata:
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * (total_days - days)
        return amount

    def compute_depreciation_aux(self, cr, uid, id, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        asset_obj = self.pool.get('account.asset.asset')
        asset = asset_obj.browse(self.cr, self.uid, id)
        amount_to_depr = residual_amount = asset.value_residual
        if asset.prorata:
            depreciation_date = datetime.strptime(self._get_last_depreciation_date(self.cr, self.uid, [asset.id], context)[asset.id], '%Y-%m-%d')
        else:
            # depreciation_date = 1st January of purchase year
            purchase_date = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
            depreciation_date = datetime(purchase_date.year, 1, 1)
        day = depreciation_date.day
        month = depreciation_date.month
        year = depreciation_date.year
        total_days = (year % 4) and 365 or 366

        undone_dotation_number = self._compute_board_undone_dotation_nb(cr, uid, asset, depreciation_date, total_days, context=context)
        for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
            i = x + 1
            amount = self._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)
            residual_amount -= amount
            vals = {
                 'amount': amount,
                 'asset_id': asset.id,
                 'sequence': i,
                 'name': str(asset.id) +'/' + str(i),
                 'remaining_value': residual_amount,
                 'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                 'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
            }
            depreciation_lin_obj.create(cr, uid, vals, context=context)
            # Considering Depr. Period as months
            depreciation_date = (datetime(year, month, day) + relativedelta(months=+asset.method_period))
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
        return True    

    def compute_depreciation_board(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.value_residual == 0.0:
                continue
            posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_check', '=', True)])
            old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)

            amount_to_depr = residual_amount = asset.value_residual
            if asset.prorata:
                depreciation_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
            else:
                # depreciation_date = 1st January of purchase year
                purchase_date = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
                depreciation_date = datetime(purchase_date.year, 1, 1)
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb(cr, uid, asset, depreciation_date, total_days, context=context)
            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                i = x + 1
                amount = self._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)
                residual_amount -= amount
                vals = {
                     'amount': amount,
                     'asset_id': asset.id,
                     'sequence': i,
                     'name': str(asset.id) +'/' + str(i),
                     'remaining_value': residual_amount,
                     'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                     'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                }
                last_dep_id = depreciation_lin_obj.create(cr, uid, vals, context=context)
                # Considering Depr. Period as months
                depreciation_date = (datetime(year, month, day) + relativedelta(months=+asset.method_period))
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
            #verifico la ultima depreciacion si es mayor a la ultima linea le generamos uno nuevo con el saldo
            last_dep = depreciation_lin_obj.browse(cr, uid, last_dep_id)
            last_dep_a = depreciation_lin_obj.browse(cr, uid, last_dep_id-1)
            if last_dep.amount > last_dep_a.amount:
                diferencia = abs(last_dep.amount - last_dep_a.amount)
                vals = {
                    'amount': diferencia,
                    'asset_id': asset.id,
                    'sequence': i+1,
                    'name': str(asset.id) +'/' + str(i),
                    'remaining_value': residual_amount,
                    'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                    'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                }
                last_dep_id_new = depreciation_lin_obj.create(cr, uid, vals, context=context)
                depreciation_lin_obj.write(cr, uid, last_dep_id,{'amount':last_dep_a.amount})
        return True    

    def compute_depreciation_board_migrado(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.value_residual == 0.0:
                continue
            antes_2015 = despues_2015 = 0 
            line_2015_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id),
                                                                  ('depreciation_date','>=','2015-01-01'),('depreciation_date','<=','2015-31-12')])
            if line_2015_ids:
                depreciation_lin_obj.write(cr, uid, line_2015_ids[0],{
                    'amount':asset.dep_periodo,
                })
            #monto antes 2015
            antes_2015 = asset.depreciacion - asset.dep_periodo
            line_antes_2015_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id),
                                                                        ('depreciation_date','<','2015-01-01')])
            if line_antes_2015_ids:
                antes_2015_valor = antes_2015/len(line_antes_2015_ids)
                for line_antes_2015_id in line_antes_2015_ids:
                    depreciation_lin_obj.write(cr, uid, line_antes_2015_id,{
                        'amount':antes_2015_valor,
                    })  
            #monto despues 2015
            despues_2015 = asset.value_residual - asset.depreciacion
            if despues_2015>0:
                line_despues_2015_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id),
                                                                              ('depreciation_date','>=','2016-01-01')])
                if line_despues_2015_ids:
                    despues_2015_valor = despues_2015/len(line_despues_2015_ids)
                    for line_despues_2015_id in line_despues_2015_ids:
                        depreciation_lin_obj.write(cr, uid, line_despues_2015_id,{
                            'amount':despues_2015_valor,
                        })  
            else:
                line_despues_2015_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id),
                                                                              ('depreciation_date','>=','2016-01-01')])
                if line_despues_2015_ids:
                    depreciation_lin_obj.unlink(cr, uid, line_despues_2015_ids)
        return True    

    def compute_depreciation_board_migrado2(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.value_residual == 0.0:
                continue
            aux_valor = asset.value_residual - asset.depreciacion
            amount_to_depr = residual_amount = aux_valor#asset.value_residual
            dep_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('name', '!=','Migrado'),('depreciation_date','>=','2016-01-01')])
            if dep_line_ids:
                print "SI DEP LINES", asset.code
                aux_monto = aux_valor/len(dep_line_ids)
                if dep_line_ids:
                    for dep_line_id in dep_line_ids:
                        depreciation_lin_obj.write(cr, uid, dep_line_id,{'amount':aux_monto,})
                dep_line_ids2 = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('name', '!=','Migrado'),('id','not in',dep_line_ids)])
                #if dep_line_ids2:
                #    depreciation_lin_obj.unlink(cr, uid, dep_line_ids2)
            else:
                print "NO DEP LINES", asset.code
                dep_line_ids2 = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('name', '!=','Migrado'),('id','not in',dep_line_ids)])
                #if dep_line_ids2:
                #    depreciation_lin_obj.unlink(cr, uid, dep_line_ids2)
        return True    

    def _checkAssetValues(self, cr, uid, ids):
        #return True
        asset_obj = self.pool.get('account.asset.asset')
        for obj in self.browse(cr, uid, ids):
            if obj.depreciacion>obj.purchase_value:
                raise osv.except_osv(('Error de usuario !'), ('El valor de depreciacion no puede ser mayor al valor de compra'))
            if obj.purchase_value<0:
                raise osv.except_osv(('Error de usuario !'), ('El valor de compra no puede ser menor a cero'))
            if obj.depreciacion<0:
                raise osv.except_osv(('Error de usuario !'), ('El valor de depreciacion no puede ser menor a cero'))
            if obj.salvage_value<0:
                raise osv.except_osv(('Error de usuario !'), ('El valor de salvaguarda no puede ser menor a cero'))
            if obj.valor_actual<0:
                raise osv.except_osv(('Error de usuario !'), ('El valor actua no puede ser menor a cero'))
            if obj.value_residual<0:
                raise osv.except_osv(('Error de usuario !'), ('El valor residual no puede ser menor a cero'))
        return True

    def _get_deprecia(self, cr, uid, ids, name, args, context=None):
        res = {}
        for asset in self.browse(cr, uid, ids):
            if asset.category_id:
                res[asset.id] = asset.category_id.deprecia
        return res

    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        cr.execute("""SELECT
                l.asset_id as id, round(SUM(abs(l.debit-l.credit))) AS amount
            FROM
                account_move_line l
            WHERE
                l.asset_id IN %s GROUP BY l.asset_id """, (tuple(ids),))
        res=dict(cr.fetchall())
        for asset in self.browse(cr, uid, ids, context):
            res[asset.id] = asset.purchase_value - res.get(asset.id, 0.0) - asset.salvage_value
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    _order = 'code desc,create_date desc'
    _defaults = dict(
        prorata = True,
    )
    _constraints = [
        (_checkAssetValues,
         ustr('Los montos no pueden ser negativos.'),[ustr('Valor Actual'), 'Valor Actual']),
        ]
    _columns = {
        'legalizado':fields.boolean('Legalizado'),
        'fecha_legalizacion':fields.date('Fecha Legalizacion'),
        'budget_id':fields.many2one('budget.item','Partida Presupuestaria'),
        'rqm_ids':fields.one2many('stock.requisition','objeto_id_id','Detalle Requerimientos Bodega'),
        'value_residual': fields.function(_amount_residual, method=True, digits_compute=dp.get_precision('Account'), string='Residual Value',store=True),
        'dep_periodo':fields.float('Dep. Periodo', digits_compute=dp.get_precision('Account')),
        'updated':fields.boolean('Actualizado'),
        'purchase_value': fields.float('Gross value ', required=True, digits_compute=dp.get_precision('Account'), 
                                       readonly=True, states={'draft':[('readonly',False)]}),
        'deprecia': fields.related('category_id', 'deprecia',type="boolean",
                               string="Deprecia", store=True ),
#        'depreciable':fields.function(_get_deprecia, store=True, string='Depreciable',type='boolean'),
        'actividad_id':fields.many2one('asset.actividad','Actividad'),
        'estructura_id':fields.many2one('asset.estructura','Estructura'),
        'partida':fields.char('Partida',size=32),
        'date_ingreso':fields.date('Fecha Ingreso'),
        'area_id':fields.many2one('asset.area','Area'),
        'seccion_id':fields.many2one('asset.seccion','Seccion'),
        'subseccion_id':fields.many2one('asset.subseccion','Subseccion'),
        'employee_id2':fields.many2one('hr.employee','Custodio Secundario'),
#        'purchase_value': fields.float('Valor Compra', required=True),
        'secuencia':fields.char('Secuencia',size=10),
        'destino_id':fields.many2one('asset.destino','Destino'),
        'direccion_id':fields.many2one('asset.direccion','Direccion'),
        'origen_fondo':fields.selection([('Propios','Propios'),('Donacion','Donacion'),('Mixto','Mixto'),('Terceros','Terceros')],'Origen de fondos'),
        'date_garantia':fields.date('Garantia Hasta'),
        'log_ids':fields.one2many('log.deprecia','asset_id','Detalle Depreciado'),
        'depreciacion_anterior':fields.float('Anterior'),
        #'dep_ids':fields.one2many('dep.line','Linea',),
        'code_aux':fields.char('Cod. Anterior',size=32),
        'code_ant':fields.char('Cod. Anterior',size=32),
        'code_sec':fields.function(_get_codesec, store=True, string='codeSEc',type='integer'),
        'code_int':fields.function(_get_codeint, store=True, string='codeInt',type='char',size=128),
        'code_sec_aux':fields.function(_get_codesec, store=True, string='codeSEcAux',type='integer'),
        'code_sec_aux1':fields.function(_get_codesec, store=True, string='codeSEcAux',type='integer'),
        'prc_anual':fields.function(_get_prcAnual, store=True, string='% Dep Anual',type='float'),
        'prc_mensual':fields.function(_get_prcMensual, store=True, string='% Dep. Mensual',type='float'),
        'foto': fields.binary('Foto'),
        'otros_accesorios':fields.text('Accesorios Descripcion'),
#        'cuenta_contable':fields.char('Cuenta',size=32),#function(_get_account, store=True, string='Cuenta Contable',type='char',size=32),
        'cuenta_contable':fields.function(_get_account_asset, store=True, string='Cuenta Contable',type='char',size=32),
        'date_entrega':fields.date('Fecha Entrega'),
        'marca':fields.char('Marca',size=32),
        'modelo':fields.char('Modelo',size=32),
        'color':fields.char('Color',size=12),
        'depreciacion':fields.float('Depreciacion Acumulada', digits=(16,2)),
        'valor_actual':fields.function(_amount_residual_actual,store=True,method=True, digits_compute=dp.get_precision('Account'), string='Valor Actual'),
        'noemp':fields.boolean('No empleado'),
    #    'estado_fisico':
        'subcateg_id':fields.many2one('asset.asset.subcateg','Sub Categoria'),
        'type':fields.selection([('Larga Duracion','Larga Duracion'),('Sujeto a Control','Sujeto a Control')],'Tipo Bien'),
        'code': fields.char('Código', size=64),        
        'serial_number': fields.char('Número de Serie', size=32),
        'invoice_id': fields.char('Numero de factura',size=20),
        'invoice_line_id': fields.many2one('account.invoice.line', 'Linea de Factura relacionada', select=True),
        'description': fields.char('Descripción', size=128),
        'department_id': fields.many2one('hr.department', 'Departamento'),
        'family': fields.char('Grupo relacional', size=32,readonly=True),
        'transaction_id': fields.many2one('gt.account.asset.transaction', 'Transacción'),
        'transac_comodato':fields.boolean('Transacción Comodato'),
        'country_id' :  fields.many2one('res.country', 'Pais'),        
        'state_id' : fields.many2one('res.country.state','Provincia'),
        'canton_id' : fields.many2one('res.country.state.canton','Canton'),
        'city' : fields.many2one('res.country.state.city','Ciudad'),       
        'parroquia' : fields.many2one('res.country.state.parish', 'Parroquia'), 
        'name': fields.char('Descripción', size=128),
        'from_duplicate': fields.many2one('gt.account.asset.duplicar', 'Creado duplicado'),        
        'employee_id': fields.many2one('hr.employee', 'Custodio'),
        'referencia': fields.char('Referencia', size=255),
        'detalle_baja': fields.char('Detalle de Baja', size=255),
        'asiento_contable_ids': fields.one2many('account.move',
                                        'asset_id',
                                        'Asientos contables'),
        'history_value': fields.float('Costo', size= 20),
        'transfer_ids': fields.one2many('account.asset.transfer',
                                        'asset_id',
                                        'Detalle de Transferencias'),
        'componentes_ids': fields.one2many('gt.account.asset.componente',
                                        'asset_id',
                                        'Componentes'),
        'low_reason': fields.text('Historial de Justificaciones'),
        'justific' :fields.boolean('Se ha registrado una Justificación'), 
        'new_low_reason': fields.text('Justificación', size=64),
        'from_factura':fields.boolean('Ingresado desde factura'),
        'asset_property_ids': fields.one2many('account.asset.property',
                                        'asset_id', string='Propiedades'),                
        'asset_moves_ids': fields.one2many('gt.account.asset.moves.relation',
                                        'asset_id', string='Movimientos', readonly=True),
        's_date_comodato':fields.date('Fecha de Inicio'),
        's_date_siniestro':fields.date('Fecha de Siniestro'),
        'e_date_comodato':fields.date('Fecha de Fin'),
        'baja_date': fields.date('Fecha de Baja',
                                    readonly=True),
        'ins_relacionada': fields.many2one('res.partner', 'Institucion relacionada'),
        'persona_rel': fields.char('Persona relacionada', size=128, readonly=True),
        'state': fields.selection([('draft', 'Borrador'),
                                   ('open', 'Operativo'),
                                   ('no_depreciate', 'Operativo-no depreciable'),
                                   ('review', 'En revisión'),
                                   ('prev_close', 'Baja Solicitada'),                                   
                                   ('close', 'Dado de baja'),
                                   ],'Estado', store=True, readonly=True, required=True),
        'state2':fields.selection([('Donacion','Donacion'),('Comodato','Comodato')],'Estado Externo'),
        'condicion':fields.selection([('Baja','Baja'),('Bueno','Bueno'),('Malo','Malo'),('Regular','Regular'),('Reparacion','Reparacion')],'Condicion'),
    }

    def onchange_trans(self, cr, uid, ids, transaction_id, context=None):
        '''
        on_change: valida la familia del activo
        '''
        res = {'value': {}}
        for obj_asset in self.pool.get('gt.account.asset.transaction').browse(cr, uid, [int(transaction_id)], context):
            
            if obj_asset.transac_comodato==True:
                
                res['value'] = {'transac_comodato': True}
            else:
                res['value'] = {'transac_comodato': False}
        return res
     
    def onchange_parent_id(self, cr, uid, ids, asset_id, context=None):
        '''
        on_change: valida la familia del activo
        '''
        res = {'value': {}}
        asset_ids= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', asset_id)])
        for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid, asset_ids, context):
            res['value'] = {'family': obj_asset.code}      
        return res
    
    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        '''
        on_change: carga el Código del tipo
        '''
        res = {'value': {}}
        tipo_ids= self.pool.get('account.asset.category').search(cr, uid, [('id','=', category_id)])
        for obj_tipo in self.pool.get('account.asset.category').browse(cr, uid, tipo_ids, context):
            res['value'] = {#'tipo_id': obj_tipo.tipo_id.id,
                'method_time': obj_tipo.method_time,
                'method': obj_tipo.method,
                'method_end': obj_tipo.method_end,
                'method_progress_factor': obj_tipo.method_progress_factor,
                'method_number': obj_tipo.method_number,
                'method_period': obj_tipo.method_period,
                'prorata': obj_tipo.prorata,
                #'state_id':65,
                #'canton_id':162,
                #'years': obj_tipo.method_number,
                'open_asset': obj_tipo.open_asset,
            }      
        return res
    
    def get_property_ids(self, cr, uid, vals, context=None):
        #
        asset_property=[] 
        #cat_id=self.pool.get('account.asset.category').browse(cr,uid,vals['category_id'],context)
        #tipo_id=cat_id.tipo_id.id
        #if tipo_id:
        if vals.has_key("tipo_id"):
            properties= self.pool.get('gt.tipo.properties').search(cr, uid, ['|',('tipo_id','=', int(vals["tipo_id"])),('all_asset','=', True)])   
            for propiedad in self.pool.get('gt.tipo.properties').browse(cr, uid, properties, context):  
                prop_id=self.pool.get('account.asset.property').create(cr, uid, {'name': propiedad.id}, context=None)
                asset_property.append(int(prop_id))
            return asset_property
        else:
            return False

    def write(self, cr, uid, ids, vals , context=None):
        band = False
        department_obj = self.pool.get('hr.department')
        parameter_obj = self.pool.get('ir.config_parameter')
        activo_ids = parameter_obj.search(cr, uid, [('key','=','activoCodificaDepartamento')],limit=1)
        if activo_ids:
            aux_activo = parameter_obj.browse(cr, uid, activo_ids[0]).value
            if aux_activo=='Si':
                for asset in self.browse(cr, uid, ids):
                    if vals.has_key('department_id'):
                        new_dept = department_obj.browse(cr, uid, vals['department_id'])
                        if asset.code_aux:
                            code_aux = asset.code_aux
                            inicio = code_aux.find('-')
                            if not new_dept.sequence:
                                raise osv.except_osv(('Error de configuracion !'), ('El departamento no esta codificado, por favor asigne un codigo '))
                            aux_1 = code_aux[0:inicio]
                            aux_2 = code_aux[inicio+1:]
                            code_new = ustr(aux_1 + '-' + new_dept.sequence + '-' +aux_2)
                            vals['code']=str(code_new)
                return super(account_asset, self).write(cr, uid, ids ,vals, context=None)
        else:
            return super(account_asset, self).write(cr, uid, ids ,vals, context=None)
                      
    def create_activo(self, cr, uid, vals, context=None):
        """        
        Carga las propiedades del activo
        """          
        res=[]  
        propiedades=self.get_property_ids(cr, uid, vals, context=None)       
        if propiedades:
            res=super(account_asset, self).create(cr, uid, vals, context=context) 
            self.pool.get('account.asset.property').write(cr, uid,propiedades , {'asset_id': res}, context=context)
        else:
            res = super(account_asset, self).create(cr, uid, vals, context=context)
        if vals.has_key("from_factura"):
            if vals['from_factura']==False:
                move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'ingreso','cause':'Registrado en sistema'}, context=None)
                self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': res,'move_id':move_id}, context=None)                         
        ##self.pool.get('gt.account.asset.moves').create(cr, uid, {'asset_id': res,'type':'ingreso'}, context=None)   
        else:
            move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'ingreso','cause':'Registrado en sistema'}, context=None)
            self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': res,'move_id':move_id}, context=None)                
        return res
    
    def create(self, cr, uid, vals, context=None):
        '''
        llama proceso par crear activos
        '''
        return self.create_activo(cr, uid, vals, context)
    
    def verificar_familia(self, cr, uid, ids, vals, context=None): 
        for obj in self.browse(cr,uid,ids, context):  
            if vals.has_key("parent_id"):
                if vals['parent_id']==False or vals['parent_id']=='':
                    vals['family']=obj.code
                else:                    
                    asset_ids= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', vals['parent_id'])])  
                    for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid, asset_ids, context):
                        vals['family']=obj_asset.code
            else:
                if obj.parent_id:
                    asset_ids= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', obj.parent_id.id)])
                    for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid, asset_ids, context):
                         vals['family']=obj_asset.code
                else:
                    if obj.code=='' or obj.code==False:
                        if vals.has_key("code"):
                            vals['family']=vals['code']
                    else:
                        vals['family']=obj.code                                                
        return vals
    
    def write_activos_(self, cr, uid, ids, vals, context=None): 
        '''
            graba los cambios del activo, genera un movimiento por cada cambio
            valida si se cambia la categoria, para modificar las propiedades
        '''
        campos={"transaction_id":'Tipo de Transacción', "category_id":'Cuenta contable','code':'Referencia/Codigo',
                "name":'Clase de activo', "name":'Descripción', "history_value":'Valor',
                "purchase_value":'Valor de Compra', "salvage_value":'Salvaguarda', "value_residual":'Valor residual', 
                "currency_id":'Moneda',
                "partner_id":'Proveedor', "purchase_date":'Fecha de compra', "parent_id":'Activo Padre', 
                "department_id":'Departamento de custodio',
                "employee_id":'Custodio', "asset_property_ids":'Propiedades', "policy_id":'Póliza', 
                "insured_amount":'Monto de póliza',
                "temporal_policy_ids":'Póliza temporal', "sinister_ids":'Siniestro', 
                "note":'Notas', "method_time":'Metodo de tiempo', "prorata":'Tiempo prorrateado', "history_ids":'Historia',
                "depreciation_line_ids":'Lineas de depreciación', "sinister_ids":'Siniestros', "method_end":'Fecha final',
                "method_period":'Longitud del período', "method_number":'Número de depreciación', "method":'Método de cálculo',
                "country_id":"Pais","state_id":"Provincia","canton_id":"Cantón","city":"Ciudad",
                "state":'Estado'
                }
        estados={'draft':'Borrador',
                 'open':'Operativo',
                 'prev_close':'Solicita Baja',
                 'review':'En revisión',
                 'no_depreciate':'Operativo-no depreciable',
                 'close':'Dado de baja'}
        jutific_=''
        if vals !={}:
            for obj in self.browse(cr,uid,ids, context):                        
                res=[]
                notes=jutific_=''
                needed_fields=[]
                if vals.has_key("category_id"):
                    unlink_prop= self.pool.get('account.asset.property').search(cr, uid, [('asset_id','=', int(ids[0]))])
                    self.pool.get('account.asset.property').unlink(cr, uid, unlink_prop)
                    propiedades=self.get_property_ids(cr, uid, vals, context=None)
                    self.pool.get('account.asset.property').write(cr, uid,propiedades , {'asset_id': int(ids[0])}, context=context)
                for value_ in vals:                
                    try:
                        if not str(value_)==str('justific') and not str(value_)==str('new_low_reason') and not str(value_)==str('low_reason'):
                            valor_=vals[value_]
                            if str(value_)==str('state'):
                                notes=notes + ustr(campos[value_])+': '+ustr(estados[vals[value_]])+'.  '
                            else:
                                notes=notes + ustr(campos[value_])+': '+ustr(vals[value_])+'.  '
                    except:
                        if not str(value_)==ustr('justific') and not str(value_)==ustr('new_low_reason') and not str(value_)==ustr('low_reason'):
                            notes=notes + ustr(value_)
                if notes !='marca_idmodel_idstate_propiedadescolor_id' and notes != 'Estado.    Referencia/Codigo.    ' and notes != '' :                    
                    if vals.has_key("new_low_reason"):
                        jutific_=vals['new_low_reason']
                    else:
                        try:
                            jutific_=obj.new_low_reason
                        except:
                            pass
                    move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'modificacion','cause':notes, 'justificacion':jutific_}, context=None)
                    self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': ids[0],'move_id':move_id}, context=None)
                 ##   self.pool.get('gt.account.asset.moves').create(cr, uid, {'asset_id': ids[0],'type':'modificacion','cause':notes, 'justificacion':obj.new_low_reason}, context=None)
        vals = self.verificar_familia(cr, uid, ids, vals, context=None)
        res=super(account_asset, self).write(cr, uid, ids, vals, context=None)       
        return res 
    
#    def write(self, cr, uid, vals, context=None):
        # llama al write de activos fijos        
#        return self.write_activos_(cr, uid, vals, context)                 
             
    def _employee_get(obj, cr, uid, context=None):
        # devuelve el usuario actual
        ids = obj.pool.get('res.users').search(cr, uid, [('id', '=', uid)], context=context)
        return ids and ids[0] or False  
        
    def in_review(self, cr, uid, ids, context=None):
        #cambia el estado "en revisión"
        return self.write(cr, uid, ids, {'state': 'review'}, context=context)   
     
    def set_to_low_activo(self, cr, uid, ids, date,context=None):
        '''
        permite dar de baja el activo manualmente 
        PROCESO SUJETO A REVISIÓN BAJO POLITICAS DE ACTIVOS FIJOS
        ********************************   NO DEFINITIVO
        
        for obj in self.browse(cr, uid, ids, context=None):
            if not obj.new_low_reason:
                raise osv.except_osv(('Error ! \n Para dar de baja se debe indicar la razón'), ('Digitarlo en la pestaña "justificacion"'))
            else:
                if str(obj.new_low_reason).strip() == '':
                    raise osv.except_osv(('Error ! \n Debe indicar la razón'), ('Digitarlo en la pestaña "justificacion"'))
                else:
                    uid_name=''
                    id_user_= self._employee_get(cr, uid, context=None)
                    if id_user_:
                        for obj_user in obj.pool.get('res.users').browse(cr, uid, [id_user_], context=None):
                            uid_name=obj_user.name
                    if obj.low_reason:
                        first_msg=str(obj.low_reason)+ '\n\n'
                    else:
                        first_msg=''
        '''
        for obj in self.browse(cr, uid, ids, context=None):
            move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'dado_baja'}, context=None)        
            move_relation_id=self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': ids[0],'move_id':move_id}, context=None)
            #        self.create_account_egreso(cr, uid, ids,move_relation_id, context)
            ##self.pool.get('gt.account.asset.moves').create(cr, uid, {'asset_id': ids[0],'type':'dado_baja'}, context=None)       
            return self.write(cr, uid, ids, {'state': 'close','baja_date':date,}, context=context)
    
    def set_to_low(self, cr, uid, ids,date, context=None):
        '''
        permite dar de baja el activo manualmente         
        '''
        return self.set_to_low_activo(cr, uid, ids, date,context)
    
    def set_to_low_activo_previo(self, cr, uid, ids, context=None):        
        #coloca al activo en estado borrador
        return self.write(cr, uid, ids, {'state': 'prev_close'}, context=context)  
      
    def set_to_low_previo(self, cr, uid, ids, context=None):
        '''
        permite dar de baja el activo manualmente         
        '''
        return self.set_to_low_activo_previo(cr, uid, ids, context)
   
    def unlink(self, cr, uid, ids, context=None):
        # redefine unlink para que no elimine activos en ningun momento
        for asset in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un Activo')
        return False

    def action_vefificar_activos_comodato(self, cr, uid, context=None):   
        ##verifica la caducidad de transacciones por comodato, por 10 d'ias     
        policy_ids= self.pool.get('account.asset.asset').search(cr, uid, [('state', '=', 'open'),
                                                                          ('transac_comodato','=',True)])
        for obj_policy in self.pool.get('account.asset.asset').browse(cr, uid, policy_ids, context):
            number_day=10    
            date_policy= datetime.strptime(str(obj_policy.e_date_comodato), "%Y-%m-%d"  ) 
            send_day= date_policy +timedelta(days=-int(10))
            compare_day=send_day.strftime('%Y-%m-%d')
            if time.strftime('%Y-%m-%d')>=compare_day:    
                responsable_id= self.pool.get('gt.account.asset.rbodega').search(cr, uid, [])
                for responsable_id in self.pool.get('gt.account.asset.rbodega').browse(cr, uid, responsable_id, context):
                    emp_responsable=responsable_id.name.id
                    dep_responsable=responsable_id.name.department_id.id
                    job_responsable= responsable_id.name.job_id.id,
                    user_responsable=responsable_id.name.user_id.id              
                asset_text  ='Activo:  '+ obj_policy.name +'\nCodigo:   '+obj_policy.code+'\nFecha inicio:   '+obj_policy.s_date_comodato+'\nFecha fin   '+obj_policy.e_date_comodato+'\nEmpresa relacionada   '+ustr(obj_policy.ins_relacionada.name)+'\nTransaccion:   '+obj_policy.transaction_id.name
                self.pool.get('res.request').create(cr, uid, {'name':  ustr('Transaccion comodato por finalizar: ')+ustr(date_policy),
                                                              'priority': '1',
                                                              'module': 'Activos Fijos',                                                       
                                                              'active': True,
                                                              'act_to': user_responsable,
                                                              'trigger_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                              'state': 'waiting',
                                                              'ref_doc1': 'account.asset.asset,%d'% (obj_policy.id,),
                                                              'body':asset_text,
                                                          })                
account_asset()

class gt_account_asset_moves(osv.osv):
    '''
    MOVIMIENTO DE ACTIVOS
    '''
    def create(self, cr, uid, vals, context=None):
        """        
        establece el Código para tipo de subtipo
        """      
        if vals['type']=='ingreso':      
            vals['name']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.registro.ingreso'))  
            return super(gt_account_asset_moves, self).create(cr, uid, vals, context=context)        
        if vals['type']=='dado_baja':      
            vals['name']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.registro.baja'))  
            return super(gt_account_asset_moves, self).create(cr, uid, vals, context=context)
        if vals['type']=='transferencia':      
            vals['name']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.registro.transferencia'))  
            return super(gt_account_asset_moves, self).create(cr, uid, vals, context=context)
        if vals['type']=='modificacion':      
            vals['name']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.registro.actualizacion'))  
            return super(gt_account_asset_moves, self).create(cr, uid, vals, context=context)
        return super(gt_account_asset_moves, self).create(cr, uid, vals, context=context)
    
    _description = 'Movimiento de activos' 
    _name = 'gt.account.asset.moves'  
    _columns = {'name': fields.char('Código', size=64, readonly=True,),
                'created_id' : fields.many2one('res.users','Creado por', store=True),
                'asset_moves_ids': fields.one2many('gt.account.asset.moves.relation',
                                        'move_id', string='Movimientos', readonly=True),
                #'asset_id': fields.many2one('account.asset.asset',string='Activo',readonly=True),
                #'relation_': fields.many2one('account.asset.asset',string='Activo',readonly=True),
                'cause': fields.text('Causa'),
                'justificacion': fields.text('Justificación'),
                'type': fields.selection([('ingreso', 'Registro en sistema'),                                          
                                          ('secuencial_ingreso', 'Secuencial Ingreso'),
                                          ('modificacion', 'Modificación'),
                                          ('transferencia', 'Transferencia'),
                                          ('dado_baja', 'Dado de baja'),
                                          ],'Movimiento', store=True, readonly=True, required=True),                                                                                                                                           
                }                                         
    _defaults = {
        'created_id': _employee_get,                 
        }           
                  
    def unlink(self, cr, uid, ids, context=None):
        # redefien unlink para que no elimine movimientos
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro de movimiento de bienes')
        return False    
         
gt_account_asset_moves()


class gt_account_asset_moves_relation(osv.osv):
    '''
    relaciona los movimientos con los activos, rompe relacion m2m
    '''    
    _description = 'Movimiento de activos' 
    _name = 'gt.account.asset.moves.relation'  
    _order = 'date_create DESC'
    _columns = {'name': fields.related('move_id', 'name',readonly=True,type="char",
                                     string="Codigo", store=True ),
                'created_id': fields.related('move_id','created_id', type='many2one',
                                   relation="res.users", string='Creado por',
                                   readonly=True, store=True),
                'cause': fields.related('move_id', 'cause',readonly=True,type="text",
                                     string="Causa", store=True ),
                'justificacion': fields.related('move_id', 'justificacion',readonly=True,type="text",
                                     string="Justificación", store=True ),
                'date_create':fields.date('Fecha de creación', size=64, required=True),
                'type': fields.related('move_id', 'type',readonly=True,type="selection", string='Tipo',
                                     selection=[('ingreso', 'Registro en sistema'),                                          
                                          ('secuencial_ingreso', 'Secuencial Ingreso'),
                                          ('modificacion', 'Modificación'),
                                          ('transferencia', 'Transferencia'),
                                          ('dado_baja', 'Dado de baja'),
                                          ], store=True ),
                'state': fields.related('asset_id', 'state',readonly=True,type="selection", string='Estado de activo',
                                        selection=[('draft', 'Borrador'),
                                                   ('open', 'Operativo'),
                                                   ('review', 'En revisión'),
                                                   ('prev_close', 'En revisión'),
                                                   ('no_depreciate', 'Operativo-no depreciable'),
                                                   ('close', 'Dado de baja'),
                                                   ]),
                'asset_id': fields.many2one('account.asset.asset',string='Activo',readonly=True),  
                'move_id': fields.many2one('gt.account.asset.moves',string='Movimiento',readonly=True),                                                                                                                                                         
                }  
                                                                    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro de movimiento de bienes')
        return False
    
    _defaults = {        
        'date_create': lambda *a: time.strftime("%Y-%m-%d"),
    }        
              
gt_account_asset_moves_relation()


class gt_tipo_property(osv.osv):
    '''
    Propiedades por Tipo
    '''    
    
    def get_by_name(self, cr, uid, name):
        """
        Metodo que devuelve el valor de una propiedad
        @name: propiedad a buscar
        return: valor encontrado caso contrario False
        """
        res_ids = self.search(cr, uid, [('name','=',name)], limit=1)
        if not res:
            return False
        data = self.read(cr, uid, res_ids[0], ['name'])
        return data['value'] 

    def create(self, cr, uid, vals, context=None):
        """        
        establece el Código para la propiedad
        """          
        vals['code']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.account.asset.tipo.property'))
        res = super(gt_tipo_property, self).create(cr, uid, vals, context=context)        
        return res 
           
    _description = 'Propiedades por tipo de bien' 
    _name = 'gt.tipo.properties'  
    _columns = dict(
        name = fields.char('Propiedad', size=64, required=True),
        code = fields.char('Código', size=64, readonly=True),
        all_asset =fields.boolean('Obligatorio para todos los activos'),        
        )   
 
    _sql_constraints = [('unique_asset_property', 'unique(name)', u'La propiedad es única.')]

    def unlink(self, cr, uid, ids, context=None):
        # redefine unlink para que no pueda eliminar propiedades de tipos
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro de tipo de propiedad de activos')
        return False 
    
gt_tipo_property()


class gt_account_asset_hr_employee_(osv.osv):
    '''
    Agregar  Relacion de usuario y sus activos a cargo
    '''
    _inherit = 'hr.employee'
    _columns = {'account_asset_ids_': fields.one2many('account.asset.asset',
                                                     'employee_id',
                                                     'Detalle de activos',
                                                     readonly=True),}   
gt_account_asset_hr_employee_() 

class gt_account_account_move(osv.osv):
    '''
    Agrega relacin con activo fijo
    '''
    _inherit = 'account.move'
    _columns = {'asset_id': fields.many2one('account.asset.asset','Activo',
                                                     readonly=True),}   
gt_account_account_move() 


class account_asset_category(osv.osv):
    '''
    agrega el campo code a la categoria
    '''
    _inherit = 'account.asset.category'

    def _get_code_abreviado(self, cr, uid, ids, name, args, context=None):
        res = {}
        for category in self.browse(cr, uid, ids):
            if category.code:
                res[category.id] = category.code[7:].replace('.','')
        return res

    _columns = {
        'code_aux':fields.function(_get_code_abreviado, store=True, string='Codigo Extra',type='char',size=3),
        'deprecia':fields.boolean('Genera depreciacion',help="Si marca este campo, los activos que pertenecen a esta categoria seran depreciados contablemente"),
        'code': fields.char('Código', size=12),                
        'cuenta_baja': fields.many2one('account.account','Cuenta contable para baja', required=True),
        'cuenta_ingreso': fields.many2one('account.account','Cuenta contable para ingreso', required=True),
        'type_asset': fields.selection([('sujeto_control','Bien Sujeto a Control'),
                                        ('larga_duracion','Bien de Larga Duración')], string='Tipo',
                                        required=True,),
        }

    _defaults = {
        'type_asset': 'larga_duracion',
        }

#    def create(self, cr, uid, vals, context=None):
#        """        
#        establece el Código para la categorís
#        """          
#        vals['code']=str(self.pool.get('ir.sequence').get(cr, uid, 'account.asset.category'))  
#        res = super(account_asset_category, self).create(cr, uid, vals, context=context)        
#        return res 
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        # devuelve el nombre y código del activo
        ids = []
        ids_descrip = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_descrip))
        if name:
            code = self.search(cr, uid, [('code', operator, name)] + args, limit=limit, context=context)           
            ids = list(set(ids + code))
        return self.name_get(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        #devuelve el name del tipo de categoria
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            if record.code:
                name = record.code + ' - ' + record.name
            else:
                name = record.name
            res.append((record.id, name))
        return res
        
    _sql_constraints = [('name_category_unique', 'unique(name)', 
                         u'No se pueden repetir registros con el mismo nombre de categoría')]
    
account_asset_category()


class gt_account_asset_transaction(osv.osv):
    '''
    CREA TIPO DE TRANSACCIÖN
    '''
    _description = 'Transacción' 
    _name = 'gt.account.asset.transaction'  
    _columns = {'name': fields.char('Tipo de Transacción', size=64, required=True),       
                'code': fields.char('Código', size=64, readonly=True,),  
                'transac_comodato':fields.boolean('Transacción Comodato'),
                #'start_date':fields.boolean('Fecha inicio',readonly=True,),
                #'end_date':fields.boolean('Fecha fin',readonly=True,),
                'is_accounting':fields.boolean('Interfaz con cartera')}  

                             
    _sql_constraints = [('name_unique', 'unique(name)', u'El nombre de la transación debe ser único')]    
      
    def create(self, cr, uid, vals, context=None):
        """        
        establece el Código para tipo de Transacción
        """          
        code_t= str(self.pool.get('ir.sequence').get(cr, uid, 'gt.account.asset.transaction')) 
        vals['code']=code_t  
        res = super(gt_account_asset_transaction, self).create(cr, uid, vals, context=context)        
        return res        
                            
    def unlink(self, cr, uid, ids, context=None):
        # redefine unlink par que no pueda eliminar transacciones
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', ustr('No puede eliminar un registro de tipo de transacción'))
        return False 
                 
gt_account_asset_transaction()


class gt_account_asset_income(osv.osv):
    '''
    Tipo de activo a ingresar
    '''
    _description = 'Tipo de activo a ingresar' 
    _name = 'gt.account.asset.income'  
    _columns = {'name': fields.char('Clasificador', size=64, required=True),       
                'code': fields.char('Código', size=64, readonly=True,),
                'cost': fields.float('Costo de adquisición igual o mayor', size= 20),
                'depreciate':fields.boolean('Es depreciable'),}           
                    
    _sql_constraints = [('name_unique', 'unique(name)', u'El nombre del tipo de activo debe ser único')]    
      
    def create(self, cr, uid, vals, context=None):
        """        
            establece el Código para tipo de Ingreso de Bien
        """          
        ids_income=self.pool.get('gt.account.asset.income').search(cr, uid, [], context=context)
        if len(ids_income)>2:
            raise osv.except_osv('Error', 'No puede crear mas tipos de bienes')
        code_t= str(self.pool.get('ir.sequence').get(cr, uid, 'gt.account.asset.income')) 
        vals['code']=code_t  
        res = super(gt_account_asset_income, self).create(cr, uid, vals, context=context)        
        return res   
                                 
    def unlink(self, cr, uid, ids, context=None):
        # redefine unlink para que no pueda eliminar tipos de bien
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro de Clasificador de bien')
        return False   
               
gt_account_asset_income()

class product_add_category(osv.Model):
    
    #agrega al producto el campo categoría, conocido como cuenta contable del bien
    
    _inherit = 'product.product'
    _columns = dict(
        asset_category_id = fields.many2one('account.asset.category','Cuenta contable del activo'),
        )

class gt_account_asset_tipo_acta(osv.osv):
    '''
    tipo acta de entrega
    '''
    _description = 'Manejo de tipo de acta de activos' 
    _name = 'gt.account.asset.tipo.acta'  
    _columns = {'name': fields.char('Tipo de acta', size=64, required=True),
                'description': fields.char('Descripción', size=256, required=True),       
                'code': fields.char('Código', size=64, readonly=True,),  
                'words': fields.text('Palabras clave', required=True),
                'words2': fields.text('Palabras clave', required=True),
                'texto': fields.text('Texto', required=True)}             
                  
    _defaults = {
        'words': 'Codigo_bien\nDescripcion_bien\nClasificador_bien\nSubtipo_bien\nClase_bien\nTipo_bien',
        'words2': 'Custodio_bien\nDepartamento_custodio\nNuevo_departamento\nNuevo_custodio\nEntregado_por'#\nNombre_poliza\nCodigo_poliza\nMonto_poliza\nFecha_de_acta',               
        }
    
    _sql_constraints = [('name_unique', 'unique(name)', u'El nombre del tipo de acta debe ser único')]    
      
    def create(self, cr, uid, vals, context=None):
        """        
        establece el Código para tipo de tipo
        """           
        vals['code']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.account.asset.tipo.acta'))  
        res = super(gt_account_asset_tipo_acta, self).create(cr, uid, vals, context=context)        
        return res       
                             
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro de tipo de acta de activos')
        return False    
              
gt_account_asset_tipo_acta()

class gt_account_asset_acta(osv.osv):
    '''
    Generacion de actas
    '''
    _description = 'Manejo de acta de activos' 
    _name = 'gt.account.asset.acta' 
    _order = 'name DESC' 
    _columns = {'name': fields.char('Codigo', size=64, readonly=True),  
                'tipo_acta_id' : fields.many2one('gt.account.asset.tipo.acta','Tipo de Acta', store=True, required=True),  
                'department_id': fields.many2one('hr.department', 'Departamento',required=True,),                
                'employee_id': fields.many2one('hr.employee', 'Empleado/Custodio',required=True,),
                'new_department_id': fields.many2one('hr.department', 'Nuevo Departamento',required=True,), 
                'new_employee_id': fields.many2one('hr.employee', 'Nuevo Custodio',required=True,),
                'entrega_id': fields.many2one('hr.employee', 'Entregado por',required=True,),
                'asset_id': fields.many2one('account.asset.asset', 'Activo Fijo',required=True),      
                'texto': fields.text('Texto', ),
                'created_id' : fields.many2one('res.users','Creado por', store=True), 
                'date': fields.date('Fecha', required=True,
                                    readonly=True),
                'state': fields.selection([('draft', 'Borrador'),
                                           ('open', 'Entregada'),
                                           ('cancel', 'Anulada'),
                                           ],readonly=True,
                                          string='Estado', ),
                }   
    _defaults = {
        'state': 'draft', 
        'date': strftime('%Y-%m-%d'),
        'created_id': _employee_get,   
        }     
                               
    #_sql_constraints = [('name_unique', 'unique(code)', u'El nombre del tipo de acta debe ser único')]
    
    def verificar_acta(self, cr, uid, ids, context=None):
        #cambia el estado "en revisión"
        texto=''
        for obj in self.browse(cr,uid,ids, context):
            try:
                texto=obj.texto
                texto=texto.replace("Codigo_bien", obj.asset_id.code)
                texto=texto.replace('Descripcion_bien', obj.asset_id.name)
                texto=texto.replace('Fecha_de_acta', ustr(time.strftime("%A, %d de %m del %Y")))
                texto=texto.replace('Custodio_bien', obj.asset_id.employee_id.employee_lastname+'  '+obj.asset_id.employee_id.employee_name)
                texto=texto.replace('Departamento_custodio', obj.asset_id.department_id.name)
                texto=texto.replace('Nuevo_departamento', obj.new_department_id.name)
                texto=texto.replace('Nuevo_custodio', obj.new_employee_id.employee_lastname+'  '+obj.new_employee_id.employee_name)
                texto=texto.replace('Entregado_por', obj.entrega_id.employee_lastname+'  '+obj.entrega_id.employee_name)  
            except:
                pass                          
        return self.write(cr, uid, ids, {'text': texto}, context=context) 
    '''
    def write(self, cr, uid, ids, vals, context=None): 
        # carga directamente la categoria el las lineas de factura en base al producto seleccionado, en el write
        for obj in self.browse(cr,uid,ids, context):
            if not obj.name:
                vals['name']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.account.asset.acta'))
        res=super(gt_account_asset_acta, self).write(cr, uid, ids, vals)          
        return res 
    '''        
    
    def acta_open(self, cr, uid, ids, context=None):
        #cambia el estado "en open"
        return self.write(cr, uid, ids, {'state': 'open'}, context=context) 
    
    def acta_cancel(self, cr, uid, ids, context=None):
        #cambia el estado "en cancel"
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
    
    def acta_close(self, cr, uid, ids, context=None):
        #cambia el estado "en close"
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)    
    
    def onchange_tipo_acta_id(self, cr, uid, ids, tipo_acta_id, context=None):
        '''
        on_change: carga el Código del tipo
        '''
        res = {'value': {}}
        tipo_ids= self.pool.get('gt.account.asset.tipo.acta').search(cr, uid, [('id','=', tipo_acta_id)])
        for obj_tipo in self.pool.get('gt.account.asset.tipo.acta').browse(cr, uid, tipo_ids, context):
            res['value'] = {'texto': obj_tipo.texto}      
        return res  
    
    def onchange_asset_id(self, cr, uid, ids, tipo_acta_id,texto,activo_id, context=None):
        '''
        on_change: carga el Código del tipo
        '''
        res = {'value': {}}
        asset_ids= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', activo_id)])   
        if activo_id !=False:
            for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid, asset_ids, context):
                texto=texto.replace("Codigo_bien", obj_asset.code)
                texto=texto.replace('Descripcion_bien', obj_asset.name)
                texto=texto.replace('Fecha_de_acta', ustr(time.strftime("%A, %d de %m del %Y")))
                texto=texto.replace('Custodio_bien', obj_asset.employee_id.employee_lastname+'  '+obj_asset.employee_id.employee_name)
                texto=texto.replace('Departamento_custodio', obj_asset.department_id.name)
                #texto=texto.replace('Nuevo_departamento', obj_asset.income_id.name)
                #texto=texto.replace('Nuevo_custodio', obj_asset.employee_id.name)
                #texto=texto.replace('Entregado_por', obj_asset.department_id.name)
        else:
             tipo_ids= self.pool.get('gt.account.asset.tipo.acta').search(cr, uid, [('id','=', tipo_acta_id)])
             for obj_tipo in self.pool.get('gt.account.asset.tipo.acta').browse(cr, uid, tipo_ids, context):
                 texto=obj_tipo.texto
        res['value'] = {'texto': texto}      
        return res
    
    def onchange_departamento_id(self, cr, uid, ids, employee_id, context=None):
        '''
        on_change: vacia el empleado si se cambia el departamento
        '''        
        res = {'value': {}}
        res['value'] = {'employee_id':''}      
        return res
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        '''
        on_change: vacia el empleado si se cambia el departamento
        '''        
        res = {'value': {}}
        res['value'] = {'asset_id':'',
                        'new_employee_id':''}      
        return res
    
    def onchange_nuevo_departamento_id(self, cr, uid, ids, new_department_id,texto, context=None):
        '''
        on_change: carga el departamento
        '''
        res = {'value': {}}
        department_id= self.pool.get('hr.department').search(cr, uid, [('id','=', new_department_id)])   
        for obj_asset in self.pool.get('hr.department').browse(cr, uid, department_id, context):            
            texto=texto.replace('Nuevo_departamento', obj_asset.name)
        res['value'] = {'texto': texto,
                        'new_employee_id':''}      
        return res
    
    def onchange_nuevo_empleado_id(self, cr, uid, ids, new_employee,texto, context=None):
        '''
        on_change: carga el nuevo empleado
        '''
        res = {'value': {}}
        new_employee_id= self.pool.get('hr.employee').search(cr, uid, [('id','=', new_employee)])
        for obj_asset in self.pool.get('hr.employee').browse(cr, uid, new_employee_id, context):           
            texto=texto.replace('Nuevo_custodio', obj_asset.employee_lastname+'  '+obj_asset.employee_name)
        res['value'] = {'texto': texto,}      
        return res
    
    def onchange_entregado_id(self, cr, uid, ids, new_employee,texto, context=None):
        '''
        on_change: carga el nuevo empleado
        '''
        res = {'value': {}}
        new_employee_id= self.pool.get('hr.employee').search(cr, uid, [('id','=', new_employee)])   
        for obj_asset in self.pool.get('hr.employee').browse(cr, uid, new_employee_id, context):            
            texto=texto.replace('Entregado_por', obj_asset.employee_lastname+'  '+obj_asset.employee_name)
        res['value'] = {'texto': texto,}      
        return res        
    
    def create(self, cr, uid, vals, context=None):
        """        
        establece el Código para tipo de tipo
        """          
        vals['name']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.account.asset.acta'))  
        res = super(gt_account_asset_acta, self).create(cr, uid, vals, context=context)        
        return res       
                             
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un acta')
        return False 
                 
gt_account_asset_acta()

class gt_account_asset_componente(osv.osv):
    '''
    componentes de activos
    '''
    _description = 'componentes de activos' 
    _name = 'gt.account.asset.componente'  
    _columns = {'name': fields.char('Nombre', size=128),       
                'value': fields.char('Descripción', size=128),  
                'cantidad': fields.integer('Cantidad'),
                'marca': fields.char('Marca', size=128),
                'modelo':fields.char('Modelo', size=128),
                'serie': fields.char('Serie', size=128),
                'state':fields.selection([('Operativo','Operativo'),('Daniado','Daniado'),('Baja','Baja')],'Estado'),
                'asset_id': fields.many2one('account.asset.asset',
                                            string='Activo',
                                            ),
                'employee_id':fields.many2one('hr.employee','Funcionario'),
                'activo':fields.char('Activo',size=16),
                'empleado':fields.char('Funcionario',size=16),
                }                           
    #_sql_constraints = [('name_unique', 'unique(name)', u'La descripción del componente debe ser única')]    
             
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro de componentes de activo')
        return False    
              
gt_account_asset_componente()

class gt_account_asset_baja_masiva(osv.osv):
    '''
    subtipo o tipo de activo
    '''
    _description = 'Baja de activos' 
    _name = 'gt.account.asset.baja.masiva'
    _order = 'date DESC'
    _columns = {'name': fields.char('Código', size=64,readonly=True), 
                'move_id':fields.many2one('account.move','Comprobante Contable'),
                'document': fields.char('Documento', size=128),
                'valor_total': fields.float('Total', size= 20,readonly=True),
                'created_id' : fields.many2one('res.users','Creado por', required=True,
                                               readonly=True),  
                'date': fields.date('Fecha', required=True),   
                'autorizado_por': fields.many2one('hr.employee', 'Autorizado por',required=True),   
                'custodio_id': fields.many2one('hr.employee', 'Custodio'),
                'detail': fields.text('Justificación', required=True),
                'asset_ids': fields.one2many('gt.account.asset.baja.masiva.det',
                                             'baja_masiva',
                                             'Detalle de activos'),
                'motivo_id':fields.many2one('asset.motivo','Motivo'),
                'is_asset_unique' :fields.boolean('Seleccionar Activo'),
                'unique_asset': fields.many2one('account.asset.asset',
                                                string='Activo a baja',),
                'state': fields.selection([('draft', 'Borrador'),
                                           ('cancel', 'Cancelado'),
                                           ('confirmed', 'Confirmado')],readonly=True,
                                          string='Estado', required=True),}                               
    _defaults = {
        'date': strftime('%Y-%m-%d'),
        'created_id': _employee_get,             
        'state': 'draft',
        }    
              
    def create(self, cr, uid, vals, context=None):            
        #establece el Código para la baja
        vals['name']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.account.asset.baja.masiva'))  
        res = super(gt_account_asset_baja_masiva, self).create(cr, uid, vals, context=context)        
        return res
    
    def cargar_activos(self, cr, uid, ids, context=None):
        #carga todos los activos del custodio
        baja_line_obj = self.pool.get('gt.account.asset.baja.masiva.det')
        for obj in self.browse(cr, uid, ids, context):
            if obj.is_asset_unique==False:
                unlink_prop= self.pool.get('gt.account.asset.baja.masiva.det').search(cr, uid, [('baja_masiva','=',obj.id)])
                self.pool.get('gt.account.asset.baja.masiva.det').unlink(cr, uid, unlink_prop)
                asset_ids= self.pool.get('account.asset.asset').search(cr, uid, [('state','=','prev_close'),
                                                                                 ('employee_id','=',obj.custodio_id.id)
                                                                                ])            
                if asset_ids:
                    for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid, asset_ids, context):
                        create_id=self.pool.get('gt.account.asset.baja.masiva.det').create(cr, uid, {
                                'baja_masiva': obj.id,
                                'created_id': obj.created_id.id,
                                'date': strftime('%Y-%m-%d %H:%M:%S'),
                                'autorizado_por': obj.autorizado_por.id,
                                'asset_id':obj_asset.id,
                                }, context=None)  
            else:
                lineas = baja_line_obj.search(cr, uid, [('asset_id','=',obj.unique_asset.id),('baja_masiva','=',obj.id)])
                if not lineas:
                    create_id=self.pool.get('gt.account.asset.baja.masiva.det').create(cr, uid, {
                        'baja_masiva': obj.id,
                        'created_id': obj.created_id.id,
                        'date': strftime('%Y-%m-%d %H:%M:%S'),
                        'autorizado_por': obj.autorizado_por.id,
                        'asset_id':obj.unique_asset.id,
                        'selected':True,
                    }, context=None)  
        return True
    
    def verificar_mensaje(self, cr, uid, ids,detail, context):
        datos=[]
        message=original_message=message_=''
        for obj_asset in self.pool.get('account.asset.asset').browse(cr, uid, [ids], context):            
            if  obj_asset.low_reason:
                    original_message=obj_asset.low_reason
                    message = 'Modificado:  ' + str(time.strftime('%Y-%m-%d %H:%M:%S'),) + ustr('\nJustificación:  ') +ustr(detail)+'\n\n'            
                    message_= ustr (original_message)+ustr(message)
        datos = {'message_': message_,
                 'message': message}
        return datos

    def contabiliza_baja(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        parameter_obj = self.pool.get('ir.config_parameter')
        account_obj = self.pool.get('account.account')
        for this in self.browse(cr, uid, ids):
            if this.move_id:
                if this.move_id.state=='posted':
                    raise osv.except_osv('Error de usuario', 'No puede ejecutar esta accion exista ya un comprobante contabilizado de esta baja')
            else:
                journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
                if not journal_ids:
                    raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
                period_ids = period_obj.find(cr, uid, this.date)
                if not period_ids:
                    raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
                aux_name = 'BAJA Nro ' + this.name + ' ' + this.detail
                move_id = move_obj.create(cr, uid, {
                    'ref': aux_name,
                    'narration':aux_name,
                    'journal_id': journal_ids[0],
                    'date': this.date,
                    'period_id':period_ids[0],
                    'state':'draft',
                    'afectacion':False,
                    'partner_id':1,
                    'type':'Baja',
                    'type2_id':'Inventario',
                    'no_cp':True,
                })
            
            for line in this.asset_ids:
                #salen 3 lineas por cada activo
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':line.asset_id.category_id.cuenta_baja.id,
                    'credit':line.purchase_value,
                    'name':line.asset_id.code,
                    'partner_id':1,
                })
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':line.asset_id.category_id.account_depreciation_id.id,
                    'debit':line.asset_id.depreciacion,
                    'name':'Depreciacion',
                    'partner_id':1,
                })
                aux = line.purchase_value - line.asset_id.depreciacion
                #tomar de parametros la cuenta patbaja
                cta_ids = parameter_obj.search(cr, uid, [('key','=','patbaja')],limit=1)
                if cta_ids:
                    aux_cta = parameter_obj.browse(cr, uid, cta_ids[0]).value
                    account_cta_ids = account_obj.search(cr, uid, [('code','=',aux_cta)],limit=1)
                    if account_cta_ids:
                        account_id = account_cta_ids[0]
                    else:
                        account_id = line.asset_id.category_id.account_depreciation_id.id
                else:
                    account_id = line.asset_id.category_id.account_depreciation_id.id
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':account_id,
                    'debit':aux,
                    'name':'Patrimonio Gobierno Seccional',
                    'partner_id':1,
                })
        return True

    def confirmar_baja(self, cr, uid, ids, context=None):
        #confirma la baja de los n activos
        det_obj = self.pool.get('gt.account.asset.baja.masiva.det')
        total=0
        ids_tasks=[]
        period_obj = self.pool.get('account.period')
        for obj in self.browse(cr, uid, ids, context): 
            period_ids = period_obj.search(cr, uid, [('state','=','draft'),('date_start','<=',obj.date),('date_stop','>=',obj.date)])
            if not period_ids:
                raise osv.except_osv('Error de usuario', 'No existen periodo contable abierto para la fecha de baja')
            if not obj.asset_ids:
                raise osv.except_osv('Error', 'No existen activos a dar de baja')
            else:
                for  obj_detail in obj.asset_ids:
                    if obj_detail.selected==True:
                        #busco que no este dado ya de baja
                        otras_bajas = det_obj.search(cr, uid, [('asset_id','=',obj_detail.asset_id.id),('id','!=',obj_detail.id)])
                        if otras_bajas:
                            raise osv.except_osv('Error', 'No puede seleccionar nuevamente un activo que esta en otra baja ' +str(obj_detail.asset_id.code))
                        ##
                        total=total+obj_detail.asset_id.purchase_value
                        datos=self.verificar_mensaje(cr, uid, obj_detail.asset_id.id,obj.detail, context)
                        self.pool.get('account.asset.asset').write_activos_(cr, uid, [obj_detail.asset_id.id], {'low_reason':datos['message_'],'new_low_reason':datos['message'],'justific':True}, context)
                        self.pool.get('account.asset.asset').set_to_low(cr, uid, [obj_detail.asset_id.id],obj.date, context=None)
                    else:
                        self.pool.get('gt.account.asset.baja.masiva.det').unlink(cr, uid, [obj_detail.id])
        self.write(cr, uid, ids, {'state': 'confirmed','valor_total':total})
        return True    
                             
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro de baja de activos')
        return False    
              
    def baja_set_draft(self, cr, uid, ids, context=None):
        baja_obj = self.pool.get('gt.account.asset.baja.masiva')
        asset_obj = self.pool.get('account.asset.asset')
        for this in self.browse(cr, uid, ids):
            for activo_id in this.asset_ids:
                asset_obj.write(cr, uid, activo_id.asset_id.id,{'state':'prev_close'})
            baja_obj.write(cr, uid, this.id,{'state':'draft'})
        return True

    def _checkBajaDate(self, cr, uid, ids):
        period_obj = self.pool.get('account.period')
        for obj in self.browse(cr, uid, ids):
            period_ids = period_obj.search(cr, uid, [('date_start','<=',obj.date),('date_stop','>=',obj.date),('state','=','draft')])
            if period_ids:
                return True
            else:
                raise osv.except_osv(('Error de usuario !'), ('La fecha de baja debe estar dentro de un periodo contable abierto'))
                return False

    _constraints = [
        (_checkBajaDate,
         ustr('La fecha debe ser de un periodo abierto contablemente.'),[ustr('Fecha Baja'), 'Fecha Baja']),
        ]

gt_account_asset_baja_masiva()


class gt_account_asset_duplicar(osv.osv):
    '''
    duplica n veces un activo
    '''
    _description = 'Manejo de tipo de activos' 
    _name = 'gt.account.asset.duplicar'
    _order = 'date DESC'
    _columns = {'name': fields.char('Código', size=64,readonly=True),                                 
                'created_id' : fields.many2one('res.users','Creado por', required=True,
                                              readonly=True),  
                'date': fields.date('Fecha', required=True,
                                    readonly=True),                                      
                'asset_id': fields.many2one('account.asset.asset',
                                            string='Activo a Duplicar',
                                            readonly=True, required=True), 
                'asset_ids': fields.one2many('account.asset.asset',
                                        'from_duplicate', string='Bienes creados'), 
                'asset_number': fields.integer('Número de activos a duplicar', required=True),
                'detail': fields.text('Justificación', required=True),     
#                'invoice_id': fields.related('asset_id','invoice_id', type='many2one',
#                                   relation="account.invoice", string='Factura',
#                                   readonly=True),                
                'description': fields.related('asset_id', 'name',readonly=True,type="char",
                                     string="Description"),
                'transaction_id' : fields.related('asset_id','transaction_id', type='many2one',
                                   relation="gt.account.asset.transaction", string='Transacción',
                                   readonly=True, store=True),
                'category_id' : fields.related('asset_id','category_id', type='many2one',
                                   relation="account.asset.category", string='Cuenta Contable',
                                   readonly=True, store=True),
                'partner_id' : fields.related('asset_id','partner_id', type='many2one',
                                   relation="res.partner", string='Proveedor',
                                   readonly=True),
                'purchase_value': fields.related('asset_id', 'purchase_value',readonly=True,type="float",
                                     string="Valor de Compra"),                              
                'state': fields.selection([('draft', 'Borrador'),
                                           ('cancel', 'Cancelado'),
                                           ('open', 'Abierto'),
                                           ('confirmed', 'Confirmado')],readonly=True,
                                          string='Estado', required=True),}                               
    _defaults = {
        'date': strftime('%Y-%m-%d'),
        'created_id': _employee_get,             
        'state': 'draft',
        }    
                                
    def create(self, cr, uid, vals, context=None):            
        #establece el Código para la baja
        vals['name']=str(self.pool.get('ir.sequence').get(cr, uid, 'gt.account.asset.duplicar'))  
        res = super(gt_account_asset_duplicar, self).create(cr, uid, vals, context=context)        
        return res

    def onchange_asset_duplica(self, cr, uid, ids, asset_id, context=None):
        '''
        on_change: carga el Código del tipo
        '''
        res = {'value': {}}
        tipo_ids= self.pool.get('account.asset.asset').search(cr, uid, [('id','=', asset_id)])
        for obj_tipo in self.pool.get('account.asset.asset').browse(cr, uid, tipo_ids, context):      
            res['value'] = {
                'transaction_id': obj_tipo.transaction_id.id,                            
                'invoice_id': obj_tipo.invoice_id,
                'category_id': obj_tipo.category_id.id,
                'partner_id': obj_tipo.partner_id.id,
                'history_value': obj_tipo.history_value,
                'purchase_value': obj_tipo.purchase_value,
                'purchase_date': obj_tipo.purchase_date,
                'description': obj_tipo.name,      
                'department_id': obj_tipo.department_id.id,
                'employee_id': obj_tipo.employee_id.id,                      
                }      
        return res    
 
    def confirma_duplicar(self, cr, uid, ids, context=None):
        total=0
        ids_tasks=[]
        move_id=''
        for obj in self.browse(cr, uid, ids, context): 
            if int(obj.asset_number)>0:                
                for j in range(0,int(obj.asset_number)): 
                    aux_tipo = 'Larga Duracion'
                    if obj.asset_id.category_id.type_asset=='sujeto_control':
                        aux_tipo = 'Sujeto a Control'
                    vals = {                            
                        'name': obj.asset_id.name,
                        'transaction_id': obj.asset_id.transaction_id.id,
                        'purchase_value': obj.asset_id.purchase_value,  
                        'from_duplicate':obj.id,                       
                        'purchase_date': obj.asset_id.purchase_date,   
                        'invoice_id': obj.asset_id.invoice_id,
                        'category_id': obj.asset_id.category_id.id,
                        'subcateg_id': obj.asset_id.subcateg_id.id,
                        'partner_id': obj.asset_id.partner_id.id,
                        'history_value': obj.asset_id.history_value,
                        'salvage_value':obj.asset_id.salvage_value,
                        'value_residual':obj.asset_id.value_residual,
                        'state': 'draft',
                        'method_number':obj.asset_id.method_number,
                        'method_period':obj.asset_id.method_period,
                        'type':aux_tipo,
                        }
                    asset_id = self.pool.get('account.asset.asset').create(cr, uid, vals, context=context)
                    if obj.asset_id.componentes_ids:    
                        print obj.asset_id.componentes_ids
                        for obj_componente in obj.asset_id.componentes_ids:               
                            self.pool.get('gt.account.asset.componente').copy(cr, uid, obj_componente.id, {'serie':'','asset_id':asset_id}, context=context)                            
                    if move_id==False:
                        move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'asset_id': asset_id,'type':'ingreso','cause':'Registrado en sistema'}, context=None)
                    if move_id!='':
                        self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': asset_id,'move_id':move_id}, context=None)
            else: 
                raise osv.except_osv('Error', 'El número de activos a duplicar debe ser mayor a 0 (cero)')                               
        self.write(cr, uid, ids, {'state': 'open','valor_total':total})
        return True
    
    def confirma_activos_duplicados(self, cr, uid, ids, context=None):
        asset_ids=[]
        for obj in self.browse(cr, uid, ids, context): 
            if obj.asset_ids:
                for asset_id in obj.asset_ids:
                    if not asset_id.employee_id or not asset_id.department_id or not asset_id.serial_number:
                        raise osv.except_osv('Error', 'Todos los activos deben registrar número de serie, departamento y custodio')
                    else:
                        self.pool.get('account.asset.asset').write_activos_(cr, uid, [asset_id.id], {'low_reason':'','new_low_reason':obj.detail,'justific':True}, context)
                        self.pool.get('account.asset.asset').validate(cr, uid, [asset_id.id], context=None)
            else:
                raise osv.except_osv('Error', 'No se ha creado ningun activo')
        self.write(cr, uid, ids, {'state': 'confirmed'})
    def cancelar_duplica(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=None)
                             
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar eliminar un registro')
        return False              
gt_account_asset_duplicar()


class gt_account_asset_baja_masiva_det(osv.osv):
    '''
    subtipo o tipo de activo
    '''
    _description = 'Detalle Baja Activos' 
    _name = 'gt.account.asset.baja.masiva.det'
    _columns = {'baja_masiva': fields.many2one('gt.account.asset.baja.masiva', 'Tramite de baja',readonly=True),                
                'created_id' : fields.many2one('res.users','Creado por', required=True,
                                              readonly=True),  
                'date': fields.date('Fecha', required=True,
                                    readonly=True),    
                'selected':fields.boolean(''),
                'detail': fields.related('baja_masiva', 'detail',readonly=True,type="char",
                                     string="Justificación", store=True ),
                'description': fields.related('asset_id', 'name',readonly=True,type="char",
                                     string="Descripción"), 
                'serial_number': fields.related('asset_id', 'serial_number',readonly=True,type="char",
                                     string="Nº Serie" ),                
                'autorizado_por': fields.many2one('hr.employee', 'Autorizado por',
                                              readonly=True, required=True),                
                'asset_id': fields.many2one('account.asset.asset',
                                            string='Activo a Transferir',
                                            readonly=True, required=True),
                'purchase_value': fields.related('asset_id', 'purchase_value',readonly=True,type="float",
                                     string="Valor de Compra" ),
                'purchase_residual': fields.related('asset_id', 'value_residual',readonly=True,type="float",
                                     string="Valor Residual" ),
                'purchase_actual': fields.related('asset_id', 'valor_actual',readonly=True,type="float",
                                     string="Valor" ),
                'department_id': fields.related('asset_id','department_id', type='many2one',
                                   relation="hr.department", string='Departamento Actual',
                                   readonly=True, store=True),
                'employee_id': fields.related('asset_id','employee_id', type='many2one',
                                   relation="hr.employee", string='Custodio Actual',
                                   readonly=True, store=True),               
                'state_asset': fields.related('asset_id', 'state',readonly=True,type="selection", string='Estado de activo',
                                        selection=[('draft', 'Borrador'),
                                                   ('open', 'Operativo'),
                                                   ('review', 'En revisión'),
                                                   ('prev_close', 'En revisión'),
                                                   ('no_depreciate', 'Operativo-no depreciable'),
                                                   ('close', 'Dado de baja'),
                                                   ]),}                               
    _defaults = {
        'date': strftime('%Y-%m-%d'),
        'created_id': _employee_get,                     
        }                
      
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.baja_masiva.state!='draft':
                raise osv.except_osv('Error', 'No puede eliminar el registro')                
        return osv.osv.unlink(self, cr, uid, ids, context=context)      
              
gt_account_asset_baja_masiva_det()


class account_invoice_line_(osv.osv):
    '''
    procedimiento que permite crear en borrador los activos desde la factura de proveedor
    crea los n activos por linea de factura en estado borrador
    '''
    _inherit = 'account.invoice.line'
    
    def write(self, cr, uid, ids, vals, context=None): 
        # carga directamente la categoria el las lineas de factura en base al producto seleccionado, en el write
        for obj in self.browse(cr,uid,ids, context):
            res=[]
            if obj.product_id.type=="asset":
                vals['asset_category_id']=obj.product_id.asset_category_id.id 
        res=super(account_invoice_line_, self).write(cr, uid, ids, vals)          
        return res 
    
    
##     def product_id_change_categ(self, cr, uid, ids, product, categ_id, obra_programa, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, invoice_address_id=False, currency_id=False, context=None, company_id=None):
##         if context is None:
##             context = {}

##         categ_obj = self.pool.get('product.category')
##         company_id = company_id if company_id != None else context.get('company_id',False)
##         context = dict(context)
##         context.update({'company_id': company_id})
##         if not partner_id:
##             raise osv.except_osv(_('No Partner Defined !'),_("You must first select a partner !") )
##         if not categ_id:
##             result = {'warning': {'title':'No seleccionó una categoría', 'message': 'Debe selecionar primero la línea de producto.'},
##                       'value': {'product_id': False}}
##             return result
##         if not product:
##             if type in ('in_invoice', 'in_refund'):
##                 return {'value': {}, 'domain':{'product_uom':[]}}
##             else:
##                 return {'value': {'price_unit': 0.0}, 'domain':{'product_uom':[]}}
##         part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
##         fpos_obj = self.pool.get('account.fiscal.position')
##         fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False

##         if part.lang:
##             context.update({'lang': part.lang})
##         result = {}
##         res = self.pool.get('product.product').browse(cr, uid, product, context=context)
##         #CAMBIO PARA CTA CONTABLE DE CATEG DE PRODUCTO
##         #TODO: REVISAR SI LOS ITEMS DE INVENTARIO SON POR BODEGA
##         #Revisar la tabla de cuentas para eleccion de cta contable ctas.categ
##         ctas_categ_obj = self.pool.get('ctas.categ')
##         categ = categ_obj.browse(cr, uid, categ_id, context=context)
## #        if categ_id:
## #            categ = categ_line
##         if type in ('out_invoice','out_refund'):
##             a = categ.property_account_income_categ.id#res.product_tmpl_id.property_account_income.id
##             if not a:
##                 a = res.categ_id.property_account_income_categ.id
##         else:
##             a = ctas_categ_obj.get_by_category(cr, uid, categ_id, categ.budget, obra_programa)
##             #a = categ_line.property_account_expense_categ.id#res.product_tmpl_id.property_account_expense.id
##             if not a:
##                 a = res.product_tmpl_id.property_account_expense.id #res.categ_id.property_account_expense_categ.id

##         if context.get('account_id',False):
##             # this is set by onchange_account_id() to force the account choosen by the
##             # user - to get defaults taxes when product have no tax defined.
##             a = context['account_id']            

##         a = fpos_obj.map_account(cr, uid, fpos, a)
##         if a:
##             result['account_id'] = a
##             result['account_number'] = self.pool.get('account.account').browse(cr, uid, a, context=context).code

##         if type in ('out_invoice', 'out_refund'):
##             taxes = res.taxes_id and res.taxes_id or categ.taxes_id and categ.taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
##         else:
##             taxes = res.supplier_taxes_id and res.supplier_taxes_id or categ.supplier_taxes_id and categ.supplier_taxes_id \
##                     or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
##         context.update({'budget_type': categ.budget, 'aplic_id': categ.presp_aplic_id.id})
##         tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes, context)
##         if type in ('in_invoice', 'in_refund'):
##             result.update( {'price_unit': price_unit or res.standard_price,'invoice_line_tax_id': tax_id} )
##         else:
##             result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})
##         result['name'] = res.partner_ref

##         domain = {}
##         result['uos_id'] = res.uom_id.id or uom or False
##         result['note'] = res.description
##         if result['uos_id']:
##             res2 = res.uom_id.category_id.id
##             if res2:
##                 domain = {'uos_id':[('category_id','=',res2 )]}

##         res_final = {'value':result, 'domain':domain}
##         if res.type=='asset':
##             res_final['value']['asset_category_id'] = res.asset_category_id.id
##         else:
##             res_final['value']['asset_category_id'] = False

##         if not company_id or not currency_id:
##             return res_final

##         company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
##         currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

##         if company.currency_id.id != currency.id:
##             if type in ('in_invoice', 'in_refund'):
##                 res_final['value']['price_unit'] = res.standard_price
##             new_price = res_final['value']['price_unit'] * currency.rate
##             res_final['value']['price_unit'] = new_price

##         if uom:
##             uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
##             if res.uom_id.category_id.id == uom.category_id.id:
##                 new_price = res_final['value']['price_unit'] * uom.factor_inv
##                 res_final['value']['price_unit'] = new_price
##         return res_final

    
    def asset_create(self, cr, uid, lines, context=None):
        '''
        No crea activos desde la factura
        '''                     
        return True
    
    def asset_create(self, cr, uid, lines, context=None):
        '''
        permite crear activos desde la factura
        '''                     
        return True

account_invoice_line_()

class Invoice(osv.osv):
    
    _inherit = 'account.invoice'
    _columns = {
                'move_asset_id': fields.many2one('account.move','Asiento complemento'),}


    def create_account_ingreso(self, cr, uid, ids,diario_id, context=None):
        # crea el asiento de ingreso del activo
        invoice_id=partner_id=''
        for obj in self.browse(cr,uid,ids,context): 
            values={'ref':obj.reference,'journal_id':diario_id, 'asset_id':''}
            move_id=self.pool.get('account.move').create(cr, uid, values, context=None)               
        return move_id
    
    def create_line_ingreso(self, cr, uid, ids, move_id, lineas_vals, context=None):
        # crea las lineas de asiento
        for obj in self.browse(cr,uid,ids,context): 
            for category_lines in lineas_vals:
                for category_value in self.pool.get('account.asset.category').browse(cr, uid,[category_lines], context):
                     line_ingreso={'name':category_value.name,
                                   'ref':obj.reference,
                                   'invoice_id':obj.id,
                                   'account_id':category_value.cuenta_ingreso.id,
                                   'debit':lineas_vals[category_lines],
                                   'credit':'',
                                   'quantity':1,
                                   'move_id':move_id,
                                   'statement_id':'',
                                   'narration':'',
                             }
                     line_egreso={'name':category_value.name,
                                  'ref':obj.reference,
                                  'invoice_id':obj.id,
                                  'account_id':category_value.cuenta_baja.id,
                                  'debit':'',
                                  'credit':lineas_vals[category_lines],
                                  'quantity':1,
                                  'move_id':move_id,
                                  'statement_id':'',
                                  'narration':'',
                                  }
                     line_ids=self.pool.get('account.move.line').create(cr, uid, line_ingreso, context=None)                                
                     line_ids=self.pool.get('account.move.line').create(cr, uid, line_egreso, context=None)
                print lineas_vals[category_lines]            
                           
        return True
    
    def create_asiento_complementario(self, cr, uid, ids, context=None):
        """
        crea el asiento complementario del ingreso de activos
        solo para los que son bienes sujetos a control
        """
        line_assets = {}
        diario_id = False
        move_data = {}
        move_obj = self.pool.get('account.move')
        for obj in self.browse(cr,uid,ids, context):
            credito = 0
            flag = False
            for line in obj.invoice_line:
                if not line.product_id.type == 'asset':
                    continue
                flag = True
                journal = line.product_id.asset_category_id.journal_id
                category = line.product_id.asset_category_id
                if not line_assets.get(category.id):
                    line_assets[category.id] = {'name': line.product_id.name,
                                                'product_id': line.product_id.id,
                                                'ref': obj.reference and obj.reference or line.invoice_number,
                                                'date': obj.date_invoice,
                                                'account_id': category.account_depreciation_id.id,
                                                'debit': 0
                                                }
                line_assets[category.id]['debit'] += line.price_total
                credito += line.price_total
            if not flag:
                continue
            line_ids = [(0,0,v) for k, v in line_assets.items()]
            line_credit = (0,0,{'name': 'COMPLEMENTO DE ACTIVO FIJO',
                                'ref': obj.reference and obj.reference or line.invoice_number,
                                'date': obj.date_invoice,
                                'account_id': category.account_expense_depreciation_id.id,
                                'credit': credito})
            line_ids.append(line_credit)
            move_data = {'ref': obj.supplier_number,
                         'period_id': obj.period_id.id,
                         'journal_id': journal.id,
                         'line_id': line_ids}
            move_id = move_obj.create(cr, uid, move_data)
            if journal.entry_posted:
                move_obj.post(cr, uid, [move_id], context)
            self.write(cr, uid, obj.id, {'move_asset_id': move_id})
        return True

    def delete_asiento_complementario(self, cr, uid, ids, context=None):
        """
        Elimina el asiento complementario de activos fijos
        """
        for obj in self.browse(cr,uid,ids, context):     
            if obj.move_asset_id:        
                self.pool.get('account.move').button_cancel(cr, uid, [obj.move_asset_id.id], context=context)
                self.pool.get('account.move').unlink(cr, uid, [obj.move_asset_id.id])
        return True                 
       
Invoice()
