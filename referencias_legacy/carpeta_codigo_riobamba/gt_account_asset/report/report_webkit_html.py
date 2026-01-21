import time
from report import report_sxw
from osv import osv
import pdb

class report_componentes(report_sxw.rml_parse):

    '''       
    def get_component_asset(self, objects):
        print '******************'
        values=[]
        datos=[]
        parent_ids=[]
        total=0
        obj_components = self.pool.get('account.asset.asset')
        asset_ids = obj_components.search(self.cr, self.uid, [('parent_id','!=', False)])
        for obj_activo in asset_ids:            
            for o in objects:
                bandera = False
                if o.id == obj_activo:                    
                    if o.parent_id.id not in parent_ids and o.parent_id.id !=False:
                        parent_ids.append(o.parent_id.id)
                        datos.append([o.parent_id.id])
                        total+=1                                                                                             
        #parent_ids.sort(lambda x,y:cmp(x[1], y[1]))
        return datos 
    '''
    def get_component_asset(self, id_parent):     
        parent_ids=[]
        total=0
        obj_components = self.pool.get('account.asset.asset')
        asset_ids = obj_components.search(self.cr, self.uid, [('parent_id','=', int(id_parent))])
        for o in self.pool.get('account.asset.asset').browse(self.cr, self.uid, asset_ids, context=None):
            if o.employee_id:
                    parent_ids.append([o.tipo_id.name,o.code,o.employee_id.complete_name,o.subtipo_id.name,o.class_id.name,o.state,o.id,o.description,o.parent_id.code])
            else:               
                    parent_ids.append([o.tipo_id.name,o.code,'',o.subtipo_id.name,o.class_id.name,o.state,o.id,o.description,o.parent_id.code])
            total+=1                                                                                             
        #parent_ids.sort(lambda x,y:cmp(x[1], y[1]))
        return parent_ids    
    
    def get_assets(self, objects):        
        datos=[]
        parent_ids=[]
        total=0
        obj_components = self.pool.get('account.asset.asset')
        asset_ids = obj_components.search(self.cr, self.uid, [])         
        for o in objects:
            if o.parent_id.id ==False: 
                if o.employee_id:
                    parent_ids.append([o.tipo_id.name,o.code,o.employee_id.complete_name,o.subtipo_id.name,o.class_id.name,o.state,o.id,o.description])
                else:               
                    parent_ids.append([o.tipo_id.name,o.code,'',o.subtipo_id.name,o.class_id.name,o.state,o.id,o.description])
                total+=1                                                                                             
        #parent_ids.sort(lambda x,y:cmp(x[1], y[1]))
        return parent_ids 
    
    def __init__(self, cr, uid, name, context):
        super(report_componentes, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'parent_ids':[],
            'get_component_asset': self.get_component_asset,
            'get_assets': self.get_assets,
        })                
                        
report_sxw.report_sxw('report.report_componentes',
                       'account.asset.asset', 
                       'addons/gt_account_asset/report/report_activos_componentes.mako',
                       parser=report_componentes,
                       header=True)

class report_employee_account_asset(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_employee_account_asset, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_employee_account_asset',
                       'hr.employee', 
                       'addons/gt_account_asset/report/report_employee_account_asset.mako',
                       parser=report_employee_account_asset,
                       header=True)

class report_employee_account_asset_detail(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_employee_account_asset_detail, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_employee_account_asset_detail',
                       'account.asset.asset', 
                       'addons/gt_account_asset/report/report_activos.mako',
                       parser=report_employee_account_asset_detail,
                       header=True)

class report_activos_movimientos(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_activos_movimientos, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_activos_movimientos',
                       'account.asset.asset', 
                       'addons/gt_account_asset/report/report_activos_movimientos.mako',
                       parser=report_activos_movimientos,
                       header=True)

class report_acta(report_sxw.rml_parse):
    
    def get_text(self, objects):
        for o in objects:
            texto=o.texto
            texto=texto.replace("\n", "<BR>")                                                                                                            
            return texto       
        
    def __init__(self, cr, uid, name, context):
        super(report_acta, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_text': self.get_text,
        })        
report_sxw.report_sxw('report.report_acta',
                       'gt.account.asset.acta', 
                       'addons/gt_account_asset/report/report_acta.mako',
                       parser=report_acta,
                       header=True)

class report_transferencias(report_sxw.rml_parse):
  
    def __init__(self, cr, uid, name, context):
        super(report_transferencias, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_transferencias',
                       'account.asset.transfer.head', 
                       'addons/gt_account_asset/report/report_transferencias.mako',
                       parser=report_transferencias,
                       header=True)

class report_baja_bienes(report_sxw.rml_parse):
  
    def __init__(self, cr, uid, name, context):
        super(report_baja_bienes, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_baja_bienes',
                       'gt.account.asset.baja.masiva', 
                       'addons/gt_account_asset/report/report_baja_bienes.mako',
                       parser=report_baja_bienes,
                       header=True)

class report_entrega_recepcion(report_sxw.rml_parse):
  
    def __init__(self, cr, uid, name, context):
        super(report_entrega_recepcion, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_entrega_recepcion',
                       'account.asset.transfer.head', 
                       'addons/gt_account_asset/report/report_entrega_recepcion.mako',
                       parser=report_entrega_recepcion,
                       header=True)
class report_ingreso_bien(report_sxw.rml_parse):
    def get_dep_mensual(self, id_parent):     
        total=0
        obj_components = self.pool.get('account.asset.depreciation.line')
        asset_ids = obj_components.search(self.cr, self.uid, [('asset_id','=', int(id_parent))])
        for o in self.pool.get('account.asset.depreciation.line').browse(self.cr, self.uid, asset_ids, context=None):
            return o.amount                                                                                          
        #parent_ids.sort(lambda x,y:cmp(x[1], y[1]))
        #return parent_ids 
    def get_dep_acumulada(self, id_parent):     
        depreciate=no_depreciate=total=0
        obj_components = self.pool.get('account.asset.depreciation.line')
        asset_ids = obj_components.search(self.cr, self.uid, [('asset_id','=', int(id_parent))])
        for obj_dep_line in self.pool.get('account.asset.depreciation.line').browse(self.cr, self.uid, asset_ids, context=None):
            if obj_dep_line.move_id:
                depreciate=depreciate+obj_dep_line.amount
        return depreciate                                                                                                  
  
    def __init__(self, cr, uid, name, context):
        super(report_ingreso_bien, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_dep_mensual': self.get_dep_mensual,
            'get_dep_acumulada': self.get_dep_acumulada,
        })        
report_sxw.report_sxw('report.report_ingreso_bien',
                       'account.asset.asset', 
                       'addons/gt_account_asset/report/report_ingreso_bien.mako',
                       parser=report_ingreso_bien,
                       header=True)

class report_impresion_etiquetas(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_impresion_etiquetas, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                })
        
report_sxw.report_sxw('report.report_impresion_etiquetas', 'account.asset.asset', 'gt_account_asset/report/report_impresion_etiquetas.rml', parser=report_impresion_etiquetas, header=False)

class report_activos_lista_componentes(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_activos_lista_componentes, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_activos_lista_componentes',
                       'account.asset.asset', 
                       'addons/gt_account_asset/report/report_activos_lista_componentes.mako',
                       parser=report_activos_lista_componentes,
                       header=True)

class report_entrega_inicial(report_sxw.rml_parse):
    def get_responsable_name(self):     
        responsable_id = self.pool.get('gt.account.asset.rbodega').search(self.cr, self.uid, [])
        if responsable_id:                       
             for obj_responsable in self.pool.get('gt.account.asset.rbodega').browse(self.cr, self.uid, responsable_id, context=None):
                 return obj_responsable.name.complete_name
        else: return ''
    def get_responsable_ci(self):     
        responsable_id = self.pool.get('gt.account.asset.rbodega').search(self.cr, self.uid, [])
        if responsable_id:                       
             for obj_responsable in self.pool.get('gt.account.asset.rbodega').browse(self.cr, self.uid, responsable_id, context=None):
                 return obj_responsable.name.name
        else: return ''
    def __init__(self, cr, uid, name, context):
        super(report_entrega_inicial, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_responsable_name': self.get_responsable_name,
            'get_responsable_ci': self.get_responsable_ci,
        })        
report_sxw.report_sxw('report.report_entrega_inicial',
                       'account.asset.asset', 
                       'addons/gt_account_asset/report/report_entrega_inicial.mako',
                       parser=report_entrega_inicial,
                       header=True)

class report_ingreso_duplicado(report_sxw.rml_parse):
    def get_dep_mensual(self, id_parent):     
        total=0
        obj_components = self.pool.get('account.asset.depreciation.line')
        asset_ids = obj_components.search(self.cr, self.uid, [('asset_id','=', int(id_parent))])
        for o in self.pool.get('account.asset.depreciation.line').browse(self.cr, self.uid, asset_ids, context=None):
            return o.amount                                                                                          
        #parent_ids.sort(lambda x,y:cmp(x[1], y[1]))
        #return parent_ids 
    def get_dep_acumulada(self, id_parent):     
        depreciate=no_depreciate=total=0
        obj_components = self.pool.get('account.asset.depreciation.line')
        asset_ids = obj_components.search(self.cr, self.uid, [('asset_id','=', int(id_parent))])
        for obj_dep_line in self.pool.get('account.asset.depreciation.line').browse(self.cr, self.uid, asset_ids, context=None):
            if obj_dep_line.move_id:
                depreciate=depreciate+obj_dep_line.amount
        return depreciate
    def __init__(self, cr, uid, name, context):
        super(report_ingreso_duplicado, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_dep_mensual': self.get_dep_mensual,
            'get_dep_acumulada': self.get_dep_acumulada,
        })        
report_sxw.report_sxw('report.report_ingreso_duplicado',
                       'gt.account.asset.duplicar', 
                       'addons/gt_account_asset/report/report_ingreso_duplicado.mako',
                       parser=report_ingreso_duplicado,
                       header=True)

class report_impresion_etiquetas_duplica(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_impresion_etiquetas_duplica, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_impresion_etiquetas_duplica',
                       'gt.account.asset.duplicar', 
                       'addons/gt_account_asset/report/report_impresion_etiquetas_duplica.rml',
                       parser=report_impresion_etiquetas_duplica,
                       header=False)

class report_impresion_etiquetas_transfer(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_impresion_etiquetas_transfer, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_impresion_etiquetas_transfer',
                       'account.asset.transfer.head', 
                       'addons/gt_account_asset/report/report_impresion_etiquetas_transfer.rml',
                       parser=report_impresion_etiquetas_transfer,
                       header=False)

class report_activos_siniestrados(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_activos_siniestrados, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_activos_siniestrados',
                       'account.asset.asset', 
                       'addons/gt_account_asset/report/report_activos_siniestrados.mako',
                       parser=report_activos_siniestrados,
                       header=False)

'''
class report_etiquetas(report_sxw.rml_parse):
           
        
    def __init__(self, cr, uid, name, context):
        super(report_etiquetas, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
report_sxw.report_sxw('report.report_etiquetas',
                       'account.asset.asset', 
                       'addons/gt_account_asset/report/report_etiquetas.mako',
                       parser=report_etiquetas,
                       header=False)
'''



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
