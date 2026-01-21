# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################
import datetime
from tools import ustr
from osv import fields, osv
from tools.translate import _
import time
from time import strftime
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class gt_insurance_policy_type(osv.osv):
    '''
    Tipo de Póliza
    '''
    _description = 'Tipo de Póliza' 
    _name = 'gt.insurance.policy.type'  
    _columns = {'name': fields.char('Nombre del Tipo', size=64, required=True),               
                'code': fields.char('Código', size=64),}   
       
    def _type_unique(self, cr, uid, ids, context=None):
        #verifica que el nobre de tipo sea unico
        old_ids= self.search(cr, uid, [('id','!=',ids)])
        for obj in self.browse(cr,uid,ids,context):
            for old_obj in self.browse(cr,uid,old_ids,context): 
                if ustr(obj.name)==ustr(old_obj.name):
                    return False
        return True
                        
    _constraints = [(_type_unique, '\n\nEl nombre ingresado ya pertenece a otro Tipo de Póliza', ['name']),]    
          
    def create(self, cr, uid, vals, context=None):
        """        
        establece la secuencia del tipo de poliza
        """        
        codigo=self.pool.get('ir.sequence').get(cr, uid, 'gt.insurance.policy.type')
        vals['code']=codigo  
        res = super(gt_insurance_policy_type, self).create(cr, uid, vals, context=context)        
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro')
        return False
    '''
    def unlink(self, cr, uid, ids, context=None):
        # No puede eliminar el tipo de Póliza si existe una Póliza relacionada
        head = self.read(cr, uid, ids, [], context=context)
        for s in head:
            sinister_ids= self.pool.get('gt.insurance.policy').search(cr, uid, [('type_id','=',s['id'])])
            if sinister_ids:
                raise osv.except_osv(_(ustr('Error\n Tipo de P'oliza '+ustr(s['name'])+ustr(''))), _('No puede ser eliminado'))
        return osv.osv.unlink(self, cr, uid, ids, context=context)  
    '''  
gt_insurance_policy_type()


class gt_insurance_policy_brach(osv.osv):
    '''
    Ramo de Póliza
    '''
    _description = 'Ramo de Póliza' 
    _name = 'gt.insurance.policy.branch'  
    _columns = {'name': fields.char('Nombre del Ramo', size=64, required=True),               
                'code': fields.char('Código', size=64),}  
    def _branch_unique(self, cr, uid, ids, context=None):
        #verifica que el nombre del branch sea único
        old_ids= self.search(cr, uid, [('id','!=',ids)])
        for obj in self.browse(cr,uid,ids,context):
            for old_obj in self.browse(cr,uid,old_ids,context): 
                if ustr(obj.name)==ustr(old_obj.name):
                    return False
        return True
                        
    _constraints = [(_branch_unique, '\n\nEl nombre ingresado ya pertenece a otro Ramo de Póliza', ['name']),]               

    def create(self, cr, uid, vals, context=None):
        """        
        establece la secuencia del ramo de poliza
        """    
        #'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'gt.insurance.policy.type'),        
        codigo=self.pool.get('ir.sequence').get(cr, uid, 'gt.insurance.policy.branch')
        vals['code']=codigo  
        res = super(gt_insurance_policy_brach, self).create(cr, uid, vals, context=context)        
        return res
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro')
        return False
    '''        
    def unlink(self, cr, uid, ids, context=None):
        # No puede eliminar el Ramo de Póliza si existe una Póliza relacionado
        head = self.read(cr, uid, ids, [], context=context)
        for s in head:
            sinister_ids= self.pool.get('gt.insurance.policy').search(cr, uid, [('branch_id','=',s['id'])])
            if sinister_ids:
                raise osv.except_osv(_(ustr('Error\n Ramo de Poliza '+ustr(s['name'])+ustr(''))), _('No puede ser eliminado'))
        return osv.osv.unlink(self, cr, uid, ids, context=context) 
    '''
gt_insurance_policy_brach()

class gt_insurance_policy_temporal(osv.osv):
    '''
    polizas temporal
    '''
    _description = 'Póliza temporal' 
    _name = 'gt.insurance.policy.temporal'  
    _order = 'create_date DESC'
    _columns = {'name': fields.related('asset_id', 'description',
                                       type="char",relation="account.asset.asset",
                                       string="Descripción activo",  readonly=True ),
                'code_asset': fields.related('asset_id', 'code',
                                       type="char",relation="account.asset.asset",
                                       string="Código activo",  readonly=True ),
                'name_policy': fields.related('policy_id', 'name',
                                       type="char",relation="gt.insurance.policy",
                                       string="Descripción Póliza", readonly=True ),
                'code_policy': fields.related('policy_id', 'code',
                                       type="char",relation="gt.insurance.policy",
                                       string="Código Póliza", readonly=True ),
                'insured_amount': fields.float('Monto asegurado', required=True),
                #'tipo_id' : fields.many2one('gt.account.asset.tipo', 'Tipo de bien'),
                #'subtipo_id': fields.related('asset_id','subtipo_id', type='many2one',
                #                             relation="gt.account.asset.subtipo", string='Subtipo de Bien',
                #                             readonly=True,store=True),
                #'class_id': fields.related('asset_id','class_id', type='many2one',
                #                           relation="gt.account.asset.class", string='Clase de Bien',
                #                           readonly=True,store=True),
                'category_id': fields.related('asset_id','category_id', type='many2one',
                                           relation="account.asset.category", string='Cuenta Contable',
                                           readonly=True,store=True),
                #'income_id': fields.related('asset_id','income_id', type='many2one',
                #                           relation="gt.account.asset.income", string='Clasificador de bien',
                #                           readonly=True,store=True),
                'policy_id' : fields.many2one('gt.insurance.policy','Póliza', required=True, domain=[('state','in',['open'])]),
                'transfer_id' : fields.many2one('gt.insurance.policy.transfer','Actualización de póliza', readonly=True),
                'state_policy': fields.selection([('draft', 'Borrador'),
                                                  ('open', 'Activa'),
                                                  ('close', 'Cerrada'),
                                                  ('modif', 'Modificado'),
                                                  ],'Estado en póliza', readonly=True),

                'state': fields.related('asset_id', 'state',readonly=True,type="selection", string='Estado',
                                     selection=[('draft', 'Borrador'),
                                   ('open', 'Operativo'),
                                   ('review', 'En revisión'),
                                   ('transfer', 'Transferido'),
                                   ('no_depreciate', 'Operativo-no depreciable'),
                                   ('prev_close', 'Baja Solicitada'),
                                   ('close', 'Dado de baja'),
                                   ]),               
                #'insured_amount': fields.float('Monto asegurado', size=32),                 
                'asset_id': fields.many2one('account.asset.asset','Activo', required=True, domain=[('state','in',['open','review','prev_close'])],
                                            ),
                'employee_id': fields.related('asset_id','employee_id', type='many2one',
                                   relation="hr.employee", string='Custodio',
                                   readonly=True,store=True,),}
    _defaults = {       
        'state_policy':'open',       
    }    
    def poliza_unica(self, cr, uid, ids, context=None):
        #verifica que el nombre del branch sea único        
        for obj in self.browse(cr,uid,ids,context):
            poliza_temporal_id=self.search(cr, uid, [('asset_id','=', obj.asset_id)])
            if poliza_temporal_id:
                return False
            
        return True                    
    _constraints = [(poliza_unica, '\n\nEl activo ya esta asegurado en otra Pólizaaa', ['name']),]
    def onchange_asset_id_policy(self, cr, uid, ids, activo_id, context=None):
        '''
        on_change: Cuando selecciona el activo por asegurar, verifica si esta asegurado en en otra póliza 
        '''
        res = {'value': {}}
        asset_ids= self.pool.get('gt.insurance.policy.temporal').search(cr, uid, [('asset_id','=', activo_id)])
        if asset_ids:
            raise osv.except_osv('Advertencia', 'El bien ya ha sido asegurado en otra Póliza')
            res['value'] = {'asset_id':''}  
            #     
        return res
    def onchange_asst_tipo_id(self, cr, uid, ids, activo_id, context=None):
        '''
        on_change: si cambia el tipo del activo, se vacia el activo 
        '''
        res = {'value': {}}
        res['value'] = {'asset_id':''}      
        return res
    
    def _unique_asset(self, cr, uid, ids, context=None):
        #verifica que un activo no pueda estar dos veces en la misma póliza            
        for obj in self.browse(cr,uid,ids,context):
            old_ids=[]                           
            if obj.state_policy=='open':
                old_ids= self.search(cr, uid, [('id','!=',obj.id),                                           
                                               ('asset_id','=',obj.asset_id.id),                                           
                                               ('state_policy','=','open'),                                               
                                               ])
                #MODIFICAR PARA QUE VEA EL ESTADO DEL TEMPORAL Y NO DEL ACTIVO
            if old_ids:
                raise osv.except_osv('Error', 'El bien no puede estar asegurado dos veces')
                return False
        return True
    
    _constraints = [(_unique_asset, '\n\nUn activo no puede estar asegurado dos veces', ['name']),]
                                                                                                      
    def name_get(self, cr, uid, ids, context=None):        
        # el name_ger devuelve el Código del activo, (el name no es único)
        if not len(ids):
            return []
        res = []
        for record in self.read(cr, uid, ids, ['id','name','name_policy','code_asset','code_policy'], context=context):
            try:                  
                aux = ustr(record['code_policy'])+'/'+ ustr(record['name_policy'])              
                res.append((record['id'], aux ))
            except:
                pass
        return res
    
    def create(self, cr, uid, vals, context=None):
        #Crea en la polzia temporal, la relacion entre activo y poliza 
        poliza_temporal_id=self.pool.get('gt.insurance.policy.temporal').search(cr, uid, [('asset_id','=', vals['asset_id']),
                                                                                          ('state_policy','in', ['open',False,''])])
        if poliza_temporal_id:
            raise osv.except_osv('Error', 'El activo ya esta asegurado en otra póliza')
        activo_id=self.pool.get('account.asset.asset').search(cr, uid, [('id', '=', vals['asset_id'])])
        #for obj in self.pool.get('account.asset.asset').browse(cr,uid,activo_id,context):
            #if not vals.has_key("state"):
            #    vals['state']=obj.state
            #if not vals.has_key("tipo_id"):
            #    vals['tipo_id']=obj.tipo_id.id                            
        res = super(gt_insurance_policy_temporal, self).create(cr, uid, vals, context=context)        
        #self.pool.get('account.asset.asset').write_activos_(cr, uid,[vals['asset_id']], {'temporal_policy_ids': res}, context=context)
        return res    
    
    def unlink(self, cr, uid, ids, context=None):
        #Verifica que no se puedan eliminar registros
        for formulario in self.browse(cr, uid, ids, context):
            if formulario.asset_id.code:
                raise osv.except_osv('Error', 'No puede eliminar un registro de Pólizas')
        return osv.osv.unlink(self, cr, uid, ids, context=context)
     
gt_insurance_policy_temporal()

class gt_account_asset_(osv.osv):
    '''
    HERENCIA account.asset.asset - AGREGAR CAMPO para relacion con Póliza, y monto asegurado
    '''
    _description="Activo del seguro"
    _inherit = 'account.asset.asset'
    _columns = {'policy_id' : fields.one2many('gt.insurance.policy.temporal','asset_id','Pólizas temporales'),
                'transfer_codes': fields.one2many('gt.insurance.policy.tr.line','active_id','Activos a cambiar'),
                #'policy_code': fields.related('policy_id', 'code',
                #                             type="char",relation="gt.insurance.policy",
                #                             string="Codigo", store=True,  readonly=True ),
                #'temporal_policy_ids': fields.one2many('gt.insurance.policy.temporal','asset_id','Pólizas temporales'),                
                }
         
                         
    def write_activo_poliza(self, cr, uid, ids, vals, context=None):                                  
        # Proceso llamado desde gt_vehicle_asset
        res=super(gt_account_asset_, self).write(cr, uid, ids, vals)          
        return res     

    def write(self, cr, uid, ids, vals, context=None): 
        # llama al write de polizas        
        return self.write_activo_poliza(cr, uid, ids, vals, context=None)
    
    def set_to_low_activo_temporal(self, cr, uid, ids, context=None):
        #Si el activo es dado de baja, en la Póliza temporal el estado del activo se cambia a dado de baja
        for obj in self.browse(cr,uid,ids, context):          
            policy_ids= self.pool.get('gt.insurance.policy.temporal').search(cr, uid, [('asset_id', '=', obj.id)])
            if policy_ids:
                self.pool.get('gt.insurance.policy.temporal').write(cr, uid, policy_ids, {'state':'close'}, context)    

    def set_to_low_activo(self, cr, uid, ids, context=None):
        '''
        permite dar de baja el activo manualmente 
        PROCESO SUJETO A REVISIÓN BAJO POLITICAS DE ACTIVOS FIJOS
        ********************************   NO DEFINITIVO
        '''
        '''
        for obj in self.browse(cr, uid, ids, context=None):
            if not obj.new_low_reason:
                raise osv.except_osv(('Error ! \n Para dar de baja se debe indicar la razón'), ('Digitarlo en la pestaña "justificación"'))
            else:
                if str(obj.new_low_reason).strip() == '':
                    raise osv.except_osv(('Error ! \n Debe indicar la razón'), ('Digitarlo en la pestaña "justificación"'))
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
                    message = str(first_msg)+'Dado de baja por usuario:  '+ uid_name +';  '+ str(time.strftime('%Y-%m-%d %H:%M:%S'),) + '\n' +str(obj.new_low_reason)
        '''  
        move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'dado_baja'}, context=None)
        move_relation_id=self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': ids[0],'move_id':move_id}, context=None)
        self.set_to_low_activo_temporal(cr, uid, ids, context)
        self.create_account_egreso(cr, uid, ids,move_relation_id, context)
        #return self.write(cr, uid, ids, {'state': 'close','low_reason':message,'new_low_reason':''}, context=context)          
        return self.write(cr, uid, ids, {'state': 'close','baja_date':time.strftime('%Y-%m-%d')}, context=context)

    def in_review(self, cr, uid, ids, context=None):
        #Si el activo se coloca en revision, en la Póliza temporal se modifica el estado
        for obj in self.browse(cr,uid,ids, context):          
            policy_ids= self.pool.get('gt.insurance.policy.temporal').search(cr, uid, [('asset_id', '=', obj.id)])
            if policy_ids:
                self.pool.get('gt.insurance.policy.temporal').write(cr, uid, policy_ids, {'state':'review'}, context)
        return self.write(cr, uid, ids, {'state': 'review'}, context=context)
    
    def set_to_draft(self, cr, uid, ids, context=None):
        #Si el activo se coloca en borrador, en la Póliza temporal se modifica el estado
        for obj in self.browse(cr,uid,ids, context):          
            policy_ids= self.pool.get('gt.insurance.policy.temporal').search(cr, uid, [('asset_id', '=', obj.id)])
            if policy_ids:
                self.pool.get('gt.insurance.policy.temporal').write(cr, uid, policy_ids, {'state':'draft'}, context)
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
      
    def validate_poliza(self, cr, uid, ids, context=None):
        #Si el activo es colocado como operativo, en la Póliza temporal el estado del activo se cambia a dado de baja
        for obj in self.browse(cr,uid,ids, context):          
            policy_ids= self.pool.get('gt.insurance.policy.temporal').search(cr, uid, [('asset_id', '=', obj.id),
                                                                                       ('state_policy', '=', 'draft')])
            if policy_ids:
                self.pool.get('gt.insurance.policy.temporal').write(cr, uid, policy_ids, {'state_policy':'open'}, context)     
        return self.pool.get('account.asset.asset').validate_activo( cr, uid, ids, context)
    
    def validate(self, cr, uid, ids, context={}):
        # llama al proceso que valida para confirmar activo
        return self.validate_poliza(cr, uid, ids, context)                                 
gt_account_asset_()


class gt_insurance_policy(osv.osv):
    '''
    Póliza
    '''
    _description = 'Póliza' 
    _name = 'gt.insurance.policy'  
    _order = 'code DESC'
    _columns = {'name': fields.char('Descripción', size=64, required=True), 
                'code': fields.char('Código', size=32),
                'number': fields.char('Número de Póliza', size=64,required=True),
                'employee_id': fields.many2one('hr.employee', 'Responsable',required=True),
                'renewal_term': fields.integer('Plazo de renovación/dias', size=32),
                'date_issue': fields.date('Fecha de Emisión',required=True),                
                'date_start': fields.date('Fecha de Inicio',required=True),  
                'date_end': fields.date('Fecha de Fin',required=True),   
                'insured_amount': fields.float('Monto (inicial)',required=True),       
                'calculated_amount': fields.float('Monto (calculado)'),
                'prev_day': fields.integer('Dias para notificacion',required=True, 
                                           help='Número de días previos a la fecha de finalización de la póliza que se enviara notificación al resposable indicando la cercana caducidad de la misma'),
                'prima': fields.float('Prima'),
                'concept': fields.text('Concepto', required=True),
                'observation': fields.text('Observaciones'),
                'coverage': fields.text('Cobertura', required=True),
                'excluded_risk': fields.text('Riesgo excluido', required=True),
                'type_id' : fields.many2one('gt.insurance.policy.type','Tipo de Póliza',required=True),
                'branch_id' : fields.many2one('gt.insurance.policy.branch','Ramo de Póliza',required=True),                                                                                
                'active_ids': fields.one2many('gt.insurance.policy.temporal','policy_id','Activos / Póliza', domain=[('state','in',['open','review','prev_close']),('state_policy','=','open')]),
                
                #'active_ids':fields.many2many('account.asset.asset','gt_insurance_policy_asset_id','policy_id','asset_id','Activos'),
                
                'partner_id' : fields.many2one('res.partner','Proveedor'),
                'invoice_id' : fields.many2one('account.invoice','Factura'),
                'less_transfer_ids': fields.one2many('gt.insurance.policy.transfer','policy_id','Activos retirados de póliza', domain=[('state','=','close')]),
                'add_transfer_ids': fields.one2many('gt.insurance.policy.transfer','new_policy_id','Activos agregados a póliza', domain=[('state','=','close')]),
                'state': fields.selection([('draft', 'Borrador'),
                                            ('open', 'Activa'),
                                            ('close', 'Cerrada'),                                            
                                            ],'Estado', required=True, readonly=True, store=True),     
                #'temporal': fields.boolean('Poliza Temporal'),                     
                }
    _sql_constraints = [('unique_policy_number', 'unique(number)', u'El número de Póliza debe ser único')]
        
    
    def name_get(self, cr, uid, ids, context=None):        
        # el name_ger devuelve el codigo y nombre de la poliza
        if not len(ids):
            return []
        res = []
        for record in self.read(cr, uid, ids, ['id','code','name'], context=context):
            try:
                aux = ustr(record['code']) +'-'+ ustr(record['name']) 
                res.append((record['id'], aux) )
            except:
                pass
        return res 
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_name = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_name))
        if name:
            code = self.search(cr, uid, [('code', operator, name)] + args, limit=limit, context=context)           
            ids = list(set(ids + code))
        return self.name_get(cr, uid, ids, context=context)   
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro')
        return False
    '''    
    def unlink(self, cr, uid, ids, context=None):
        # solo se puede eliminar Pólizas en estado borrador
        head = self.read(cr, uid, ids, [], context=context)
        for s in head:
            if s['state']!='draft':
                raise osv.except_osv(_(ustr('Error!\n')), _('Solo puede eliminar Pólizas en estado "Borrador" ' ))
        return osv.osv.unlink(self, cr, uid, ids, context=context) 
    '''
    def create(self, cr, uid, vals, context=None):
        """        
        verifica que la fecha de cierre sea mayor a la fecha de inicio de la poliza
        """    
        res=[]        
        if int(vals['prev_day'])>0:
            if datetime.strptime(str(vals['date_issue']), "%Y-%m-%d")>datetime.strptime(str(vals['date_start']), "%Y-%m-%d") :
                raise osv.except_osv(_(ustr('Error!\n')), _(ustr('La fecha de emision debe ser menor o igual a la fecha de inicio de la Póliza')))
            else:
                if datetime.strptime(str(vals['date_start']), "%Y-%m-%d")>=datetime.strptime(str(vals['date_end']), "%Y-%m-%d") :
                   raise osv.except_osv(_(ustr('Error!\n')), _(ustr('La fecha de fin debe ser mayor a la fecha de inicio de la Póliza')))        
                else:      
                    if float(vals['insured_amount'])>0: 
                        vals['code']=self.pool.get('ir.sequence').get(cr, uid, 'gt.insurance.policy.code')     
                        res = super(gt_insurance_policy, self).create(cr, uid, vals, context=context)
                    else:  
                        raise osv.except_osv(_(ustr('Error!\n')), _(ustr('El valor asegurado de la Póliza debe ser mayor a cero')))
        else:        
                raise osv.except_osv(_(ustr('Error!\n')), _(ustr('El número de días para notificación debe ser mayor a cero')))
        return res
    
    def write2(self, cr, uid, ids, vals, context=None):
        """        
        verifica que la fecha de cierre sea mayor a la fecha de inicio de la Póliza
        """    
        res=[] 
        for obj in self.browse(cr, uid, ids, context):
            try: 
                if vals['date_start']:
                    start=str(vals['date_start'])
            except:
                start=str(obj.date_start)
            try: 
                if vals['date_end']:
                    end=str(vals['date_end'])
            except:
                end=str(obj.date_end)            
            if datetime.strptime(start, "%Y-%m-%d")>=datetime.strptime(end, "%Y-%m-%d") :
                raise osv.except_osv(_(ustr('Error!\n')), _(ustr('La fecha de fin debe ser mayor a la fecha de inicio de la Póliza')))
            else:                 
                res= super(gt_insurance_policy, self).write(cr, uid, ids, vals)               
                #if not vals.has_key("state"):
                #    new_state=obj.state 
                #else:
                #    new_state=vals['state']                   
                #policy_ids= self.pool.get('gt.insurance.policy.temporal').search(cr, uid, [('policy_id', '=', obj.id)])
                #if policy_ids:
                #    print new_state
                #    self.pool.get('gt.insurance.policy.temporal').write(cr, uid, policy_ids, {'state_policy':new_state}, context)
        return res
    
    def calcular_monto_poliza(self, cr, uid, ids, context=None):
        # calcula el monto de la poliza
        monto=0 
        for obj in self.browse(cr,uid,ids, context):          
            policy_ids= self.pool.get('gt.insurance.policy.temporal').search(cr, uid, [('policy_id', '=', obj.id),
                                                                                       ('state', 'in', ['open','review','prev_close']),
                                                                                        ('state_policy', '=', 'open')])
            if policy_ids:                
                for policy_obj in self.pool.get('gt.insurance.policy.temporal').browse(cr,uid,policy_ids, context):
                    monto=monto+policy_obj.insured_amount                                    
                self.write(cr, uid, ids, {'calculated_amount':monto}, context)  
        return True     
    def action_draft(self, cr, uid, ids, context=None):
        # cambia la Póliza a estado borrador
        self.write(cr, uid, ids, {'state' : 'draft'}, context)
        return True
    
    def action_draft_open(self, cr, uid, ids, context=None):
        # cambia la Póliza a estado abierto        
        self.write(cr, uid, ids, {'state' : 'open'}, context)
        return True

    
    def action_open_close(self, cr, uid, ids, context=None):
        # cambia la Póliza a estado cerrado
        for obj in self.browse(cr, uid, ids, context):
            if time.strftime('%Y-%m-%d')< obj.date_end:
                raise osv.except_osv(_(ustr('Error!\n')), _(ustr('Esta intentando cerrar la Póliza antes de su fecha de fin')))
            else:
                self.write(cr, uid, ids, { 'state': 'close' }, context)
        return True  
    
    def action_open_cancel(self, cr, uid, ids, context=None):
        # cambia la Póliza a estado cancelado
        self.write(cr, uid, ids, { 'state': 'cancel' }, context)
        return True   
      
    def send_mail_end_policy(self, cr, uid, context=None):   
        #envio de mal desde ppoliza, cuando se quiere enviar proformas a proveedor     
        policy_ids= self.pool.get('gt.insurance.policy').search(cr, uid, [('state', '=', 'open')])
        for obj_policy in self.pool.get('gt.insurance.policy').browse(cr, uid, policy_ids, context):
            number_day=obj_policy.prev_day     
            date_policy= datetime.strptime(str(obj_policy.date_end), "%Y-%m-%d"  ) 
            send_day= date_policy +timedelta(days=-int(number_day))
            compare_day=send_day.strftime('%Y-%m-%d')
            if time.strftime('%Y-%m-%d')>=compare_day:                
                template_obj = self.pool.get('email.template')
                template_inst = template_obj.search(cr, uid,[('name','=','Caducidad de Pólizas')])[0]
                action = template_obj.send_mail(cr, uid, template_inst, obj_policy.id, False, context)
                      
    def print_asegurados(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir activos asegurados desde boton
        '''       
        if not context:
            context = {}
        solicitud = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [solicitud.id], 'model': 'gt.insurance.policy'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_polizas',
            'model': 'gt.insurance.policy',
            'datas': datas,
            'nodestroy': True,                       
            }

    def print_informacion_poliza(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir informacion de la poliza desde boton
        '''       
        if not context:
            context = {}
        solicitud = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [solicitud.id], 'model': 'gt.insurance.policy'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_insurance_policy',
            'model': 'gt.insurance.policy',
            'datas': datas,
            'nodestroy': True,                       
            }      
    _defaults = {       
        'state':'draft',
        #'temporal':False,
        'date_issue': lambda *a: time.strftime('%Y-%m-%d'),
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d'),       
    }    
gt_insurance_policy()


class gt_insurance_policy_close_policy(osv.osv_memory):
    '''
    pide una justificación si va a cerrar antes la Póliza
    '''
    _name = 'gt.insurance.policy.close_policy'
    _description = 'Solicita justificación para cerrar la Póliza' 
    _columns = {
                'name': fields.text('Justificación'),               
                'requires_justification': fields.boolean('Requiere justificación', ), 
                'policy_id' : fields.many2one('gt.insurance.policy','Póliza'),         
                'partner_id' : fields.many2one('res.partner','Proveedor'),             
        }
    def action_open_close_policy(self, cr, uid, ids, context):
        # cambia la Póliza a estado cancelado
        for obj in self.browse(cr, uid, ids, context):
            id_activo=context.get('active_id')
            policy_id= self.pool.get('gt.insurance.policy').search(cr, uid, [('id','=', id_activo)])
            user_id= obj.pool.get('res.users').search(cr, uid, [('id', '=', uid)], context=context)
            for usuarios in self.pool.get('res.users').browse(cr, uid, user_id, context):
                user_name= usuarios.name
            if obj.requires_justification:
                for obj_policy in self.pool.get('gt.insurance.policy').browse(cr, uid, policy_id, context):
                    message = ustr('Usuario:  ')+ustr(user_name)+'.   Cerrado:  ' + str(time.strftime('%Y-%m-%d %H:%M:%S'),) + '\n' +ustr(obj.name)
                self.pool.get('gt.insurance.policy').write(cr, uid, policy_id, {'state':'close','observation':message}, context)
                return {'type':'ir.actions.act_window_close'}
            else:
                self.pool.get('gt.insurance.policy').write(cr, uid, policy_id, {'state':'close'}, context)
                return {'type':'ir.actions.act_window_close'}
        return True 

    def get_policy_id(self, cr, uid, context): 
        #carga el nombre de la Póliza
        policy_id=''
        id_activo=context.get('active_id')
        policy_id= self.pool.get('gt.insurance.policy').search(cr, uid, [('id','=', id_activo)])
        for obj_sinister in self.pool.get('gt.insurance.policy').browse(cr, uid, policy_id):
            policy_id= obj_sinister.id
        return policy_id

    def get_partner_id(self, cr, uid, context): 
        #carga el nombre de la Póliza
        policy_id=''
        id_activo=context.get('active_id')
        policy_id= self.pool.get('gt.insurance.policy').search(cr, uid, [('id','=', id_activo)])
        for obj_sinister in self.pool.get('gt.insurance.policy').browse(cr, uid, policy_id):
            policy_id= obj_sinister.partner_id.id
        return policy_id
        
    def get_justification(self, cr, uid, context): 
        #verifica si requiere justificación
        justification=False
        id_activo=context.get('active_id')
        policy_id= self.pool.get('gt.insurance.policy').search(cr, uid, [('id','=', id_activo)])
        for obj in self.pool.get('gt.insurance.policy').browse(cr, uid, policy_id):
             if time.strftime('%Y-%m-%d')< obj.date_end:
                 justification= True
        return justification
    
    _defaults = {
                 'policy_id':get_policy_id,
                 'requires_justification':get_justification,
                 'partner_id':get_partner_id,
                 } 
    
    
def _employee_get(obj, cr, uid, context=None):
    '''
    devuelve el usuario que crea el objeto
    '''
    ids = obj.pool.get('res.users').search(cr, uid, [('id', '=', uid)], context=context)
    return ids and ids[0] or False


class gt_insurance_policy_transfer_line(osv.osv):
    '''
    registro que indica los detalles de la actualizacion de Póliza del activo
    '''
    _description="Registro de actualizacion de una Póliza a otra de un activo"
    _name = 'gt.insurance.policy.tr.line'
    _columns = {'name': fields.char('Actualización de Activo', size=64,
                                    help='Representa el código con el que se registra el movimiento de un activo de una Póliza a otra'),
                'transfer_id' : fields.many2one('gt.insurance.policy.transfer','Actualización de póliza', readonly=True),
                'insured_amount': fields.float('Anterior Monto asegurado', size=64, readonly=True),
                'new_insured_amount': fields.float('Nuevo Monto asegurado', size=32),
                'old_policy_id' : fields.related('transfer_id','policy_id', type='many2one', 
                                                relation="gt.insurance.policy", string='Póliza origen', 
                                                readonly=True,),
                'new_policy_id' : fields.related('transfer_id','new_policy_id', type='many2one', 
                                                relation="gt.insurance.policy", string='Póliza destino', 
                                                readonly=True,),
                'created_id' : fields.related('transfer_id','created_id', type='many2one', 
                                                relation="res.users", string='Actualizado por', 
                                                readonly=True,),
                'active_id': fields.many2one('gt.insurance.policy.temporal','Activo a cambiar', domain=[('state','=','open')], readonly=True),
                'asset_id' : fields.related('active_id','asset_id', type='many2one', 
                                                relation="account.asset.asset", string='Activo', 
                                                readonly=True,),}
        
    '''           
    def create(self, cr, uid, vals, context=None):
        """        
        establece la secuencia de la linea de transferencia
        """                
        codigo=self.pool.get('ir.sequence').get(cr, uid, 'gt.insurance.policy.tr.line')
        vals['name']=codigo  
        res = super(gt_insurance_policy_transfer_line, self).create(cr, uid, vals, context=context)        
        return res
    '''
gt_insurance_policy_transfer_line()

    
class gt_insurance_policy_transfer(osv.osv):
    '''
    Permite la actualizacion de los activos por Póliza.
    '''
    _description = 'Registro de actualización masiva de activos de una póliza' 
    _name = 'gt.insurance.policy.transfer'  
    _order = 'date_transfer DESC'
    _columns = {'name': fields.char('Código de actualización', size=64,
                                    help='Representa el código con el que se autoriza el movimiento de el/los activos de una póliza hacia otra'),
                'date_transfer': fields.datetime('Fecha de Actualización',required=True),
                'created_id' : fields.many2one('res.users','Actualizado por', store=True),
                'policy_id' : fields.many2one('gt.insurance.policy','Póliza origen',required=True, ),#domain=[('temporal','=',False)]),                
                'number': fields.related('policy_id', 'number',
                                             type="char",relation="gt.insurance.policy",
                                             string="Número de Póliza ", store=True,  readonly=True ),
                '_state': fields.selection([('draft', 'Borrador'),
                                            ('open', 'Abierto'),                                                                                        
                                            ('close', 'Cerrado'),
                                            ],'Estado', required=True, readonly=True, store=True),
                '_new_state':fields.selection([('draft', 'Borrador'),
                                            ('open', 'Abierto'),                                                                                        
                                            ('close', 'Cerrado'),
                                            ],'Estado', required=True, readonly=True, store=True),
                'new_policy_id' : fields.many2one('gt.insurance.policy','Póliza destino',required=True),#,domain=[('temporal','=',False)]),
                'new_number': fields.related('new_policy_id', 'number',  readonly=True,
                                             type="char",relation="gt.insurance.policy",
                                             string="Número de Póliza ", store=True ),
                'active_to_trasnfer': fields.one2many('gt.insurance.policy.tr.line','transfer_id','Activos a cambiar'),
                'state': fields.selection([('draft', 'Borrador'),
                                            ('open', 'Abierto'),                                                                                        
                                            ('close', 'Confirmado'),
                                            ],'Estado', required=True, readonly=True, store=True),                          
                }
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro')
        return False
    '''    
    def unlink(self, cr, uid, ids, context=None):
        # solo se puede eliminar Pólizas en estado borrador
        head = self.read(cr, uid, ids, [], context=context)
        for s in head:
            if s['state']!='draft':
                raise osv.except_osv(_(ustr('Error!\n')), _('Solo puede ser eliminado si esta en estado "Borrador" ' ))
        return osv.osv.unlink(self, cr, uid, ids, context=context)
    '''
    _defaults = {
            'date_transfer': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
            'created_id': _employee_get,
            'state':'draft',
            }        
    def create(self, cr, uid, vals, context=None):
        """        
        verifica el stado de las Pólizas que intervienene en la transferencia al crear 
        """    
        #'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'gt.insurance.policy.type'),        
        for obj in self.pool.get('gt.insurance.policy').browse(cr, uid, [vals['policy_id']], context=None):
            vals['_state']=obj.state  
        for obj_ in self.pool.get('gt.insurance.policy').browse(cr, uid, [vals['new_policy_id']], context=None):
             vals['_new_state']= obj_.state
        res = super(gt_insurance_policy_transfer, self).create(cr, uid, vals, context=context)        
        return res
    
    def get_policy_fiels(self, cr, uid, ids, policy_id, context=None):
        # devielve el directorio correspondiente al siniestro
        res = {'value': {}}  

        for obj in self.pool.get('gt.insurance.policy').browse(cr, uid, [policy_id], context=None):
                res['value'] = {'number': obj.number,
                                '_state': obj.state,}      
        return res
    def get_new_policy_fiels(self, cr, uid, ids, policy_id, context=None):
        # devielve el directorio correspondiente al siniestro
        res = {'value': {}}            
        for obj in self.pool.get('gt.insurance.policy').browse(cr, uid, [policy_id], context=None):
                res['value'] = {'new_number': obj.number,
                                '_new_state': obj.state}      
        return res
    def get_asset_ids(self, cr, uid, ids, context):
        #crea las lineas de transferencia por activo        
        correct_start=False    
        unlink_ids=self.pool.get('gt.insurance.policy.tr.line').search(cr, uid, [('transfer_id','=', ids)])
        self.pool.get('gt.insurance.policy.tr.line').unlink(cr, uid, unlink_ids)
        for obj in self.browse(cr, uid, ids, context):
            asset_ids= self.pool.get('gt.insurance.policy.temporal').search(cr, uid, [('policy_id','=', obj.policy_id.id),
                                                                             ('state','in', ['open','review','prev_close'])])
            if asset_ids:
                for obj_asset in self.pool.get('gt.insurance.policy.temporal').browse(cr, uid, asset_ids, context):
                    self.pool.get('gt.insurance.policy.tr.line').create(cr,uid, {'name': '',
                                                                                'transfer_id': obj.id,
                                                                                'insured_amount':obj_asset.insured_amount,
                                                                                'new_insured_amount':obj_asset.insured_amount,
                                                                                'active_id': obj_asset.id,
                                                                                },context=context)   
    def write(self, cr, uid, ids, vals, context=None):
        """        
        verifica el stado de las Pólizas que intervienene en la transferencia al crear
        """    
        res=[]  
        for obj in self.browse(cr, uid, ids, context):
            vals['_state']=obj.policy_id.state
            vals['_new_state']=obj.new_policy_id.state
        res= super(gt_insurance_policy_transfer, self).write(cr, uid, ids, vals)                  
        return res
              
    def abrir_transferir_poliza(self, cr, uid, ids, context=None):
        #cambia estado de la transferencia de borradoar a abierto
        for obj in self.browse(cr, uid, ids, context):
            _state=obj.policy_id.state
            _new_state= obj.new_policy_id.state
            if obj.policy_id.id ==obj.new_policy_id.id:
                raise osv.except_osv(_(ustr('Error!\n')), _('La Pólizas origen y destino de los activos deben ser diferentes' ))
            
        self.write(cr, uid, ids, {'state': 'open',
                                  '_state': _state,
                                  '_new_state': _new_state,
                                   'name':str(self.pool.get('ir.sequence').get(cr, uid, 'gt.insurance.policy.transfer')) }, context)
        return True
     
    def confirmar_transferir_poliza(self, cr, uid, ids, context=None):
        #cambia estado de la transferencia de borradoar a abierto
        correct_start=False
        for obj in self.browse(cr, uid, ids, context):
            transfer_ids= self.pool.get('gt.insurance.policy.tr.line').search(cr, uid, [('transfer_id','=', obj.id)])
            if transfer_ids:
                for obj_transfer in self.pool.get('gt.insurance.policy.tr.line').browse(cr, uid, transfer_ids, context):               
                    self.pool.get('gt.insurance.policy.temporal').write(cr, uid, [obj_transfer.active_id.id], {'transfer_id':obj.id,
                                                                                                               'state_policy':'modif',
                                                                                                               #'state':'transfer',
                                                                                                               }, context)
                    self.pool.get('gt.insurance.policy.temporal').create(cr, uid, {'asset_id': obj_transfer.active_id.asset_id.id,
                                                                                   'policy_id': obj.new_policy_id.id,
                                                                                   'tipo_id': obj_transfer.active_id.asset_id.tipo_id.id,
                                                                                   'insured_amount':obj_transfer.new_insured_amount,
                                                                                   'state':obj_transfer.active_id.asset_id.state,
                                                                                   'state_policy':obj.new_policy_id.state,
                                                                                   'transfer_id':obj.id,
                                                                                   }, context=None)                   
                    self.pool.get('gt.insurance.policy.tr.line').write(cr, uid, obj_transfer.id, {'name':str(self.pool.get('ir.sequence').get(cr, uid, 'gt.insurance.policy.tr.line'))}, context)
                self.write(cr, uid, ids, { 'state': 'close' }, context)
                unlink_ids=self.pool.get('gt.insurance.policy.tr.line').search(cr, uid, [('transfer_id','=',False)])
                self.pool.get('gt.insurance.policy.tr.line').unlink(cr, uid, unlink_ids)
            else:
                raise osv.except_osv(_(ustr('Error!\n')), _('No existen activos a modificar' ))
        return True                
gt_insurance_policy_transfer()   

        
class gt_account_asset_rseguros(osv.osv):
    _description = 'Responsable de rseguros'
    _name = 'gt.account.asset.rseguros' 
    _columns = {'name': fields.many2one('hr.employee', 'Responsable de Seguros y Siniestros',required=True), }
    def create(self, cr, uid, vals, context=None):
        """        
            verifica que solo exista un responsable de bodega
        """          
        ids_income=self.pool.get('gt.account.asset.rseguros').search(cr, uid, [], context=context)
        if len(ids_income)>=1:
            raise osv.except_osv('Error', 'No puede crear mas de un responsable de Seguros y Siniestros')         
        res = super(gt_account_asset_rseguros, self).create(cr, uid, vals, context=context)        
        return res
    def action_vefificar_activos(self, cr, uid, context=None):  
        import datetime 
        asset_text=''
        now = datetime.datetime.now()
        end_date = date.today() + relativedelta( days = -(now.day) )
        start_date = date.today() + relativedelta( months = -1 ) + relativedelta( days = 1-(now.day) )
        asset_ids= self.pool.get('account.asset.asset').search(cr, uid, [('purchase_date', '>=', start_date),
                                                                        ('purchase_date', '<=', end_date),
                                                                        ('state', '=', 'open')])
        responsable_id= self.pool.get('gt.account.asset.rseguros').search(cr, uid, [])
        for responsable_id in self.pool.get('gt.account.asset.rseguros').browse(cr, uid, responsable_id, context):
            emp_responsable=responsable_id.name.id
            dep_responsable=responsable_id.name.department_id.id
            job_responsable= responsable_id.name.job_id.id,
            user_responsable=responsable_id.name.user_id.id
        
        if asset_ids:
            for asset_id in self.pool.get('account.asset.asset').browse(cr,uid,asset_ids, context):
                asset_text=asset_text+ustr('\nCódigo: ')+asset_id.code+ustr('       Descripción:  ')+ustr(asset_id.name)+'      Custodio:  '+ustr(asset_id.employee_id.complete_name)
            expedient_id= self.pool.get('doc_expedient.expedient').create(cr, uid,{'name':  ustr('Nuevos activos ingresados:  (')+ustr(start_date) +'/'+ustr(end_date)+')',
                                                                                                       'state': 'draft',
                                                                                                       'ubication':'internal',
                                                                                                       'resumen': asset_text}, context=context)
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                  'other_action' : str('Ingreso de activos') ,
                                                                  'description': asset_text,
                                                                  #'desc_task': obj_sinister.name.name + '\n' +obj_sinister.description,
                                                                  'department': dep_responsable,
                                                                  'employee_id' : emp_responsable,
                                                                  'job_id': job_responsable,
                                                                  'user_id': user_responsable,
                                                                  'expedient_id':expedient_id,
                                                                  'state': 'done',
                                                                  }, context=context)
            self.pool.get('doc_expedient.expedient').action_draft_created(cr, uid, [expedient_id],context)
                            #self.pool.get('doc_expedient.task').write(cr, uid, [task_id], {'state' : 'done'}, context)
        else:
            return False
        return asset_id
gt_account_asset_rseguros()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

