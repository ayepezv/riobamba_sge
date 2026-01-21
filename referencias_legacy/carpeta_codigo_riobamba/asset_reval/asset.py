# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from time import strftime, strptime
from osv import osv, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta

class revalorizaCategoriaLineLine(osv.TransientModel):
    _name = 'revaloriza.categoria.line.line'
    _columns = dict(
        l_id = fields.many2one('revaloriza.categoria.line','Reporte'),
        rev_id = fields.many2one('account.asset.reval','Revalorizacion'),
    )
revalorizaCategoriaLineLine()

class revalorizaCategoriaLine(osv.TransientModel):
    _name = 'revaloriza.categoria.line'
    _columns = dict(
        c_id = fields.many2one('revaloriza.categoria','Reporte'),
        categ_id = fields.many2one('account.asset.category','Categoria de activo'),
        line_ids = fields.one2many('revaloriza.categoria.line.line','l_id','Detalle'),
    )
revalorizaCategoriaLine()
class revalorizaCategoria(osv.TransientModel):
    _name = 'revaloriza.categoria'
    _columns = dict(
        date_start = fields.date('Desde'),
        date_stop = fields.date('Hasta'),
        line_ids = fields.one2many('revaloriza.categoria.line','c_id','Detalle'),
    )
    
    def printRevalorizaCateg(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'revaloriza.categoria'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'reval_categ',
            'model': 'revaloriza.categoria',
            'datas': datas,
            'nodestroy': True,                        
            }

    def generaReporteCateg(self, cr, uid, ids, context=None):
        reval_obj = self.pool.get('account.asset.reval')
        categ_obj = self.pool.get('account.asset.category')
        line_obj = self.pool.get('revaloriza.categoria.line')
        line_line_obj = self.pool.get('revaloriza.categoria.line.line')
        for this in self.browse(cr, uid, ids):
            categ_ids = categ_obj.search(cr, uid, [])
            if categ_ids:
                for categ_id in categ_ids:
                    reval_ids = reval_obj.search(cr, uid, [('date','>=',this.date_start),('date','<=',this.date_stop),('category_id','=',categ_id)])
                    if reval_ids:
                        line_id = line_obj.create(cr, uid, {
                            'c_id':this.id,
                            'categ_id':categ_id,
                        })
                        for rev_id in reval_ids:
                            line_line_obj.create(cr, uid, {
                                'l_id':line_id,
                                'rev_id':rev_id,
                            })
        return True
            

revalorizaCategoria()

class activoTotal(osv.TransientModel):
    _inherit = 'activo.total'

    def printActivoTotal(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'activo.total'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'activo_totalrev',
            'model': 'activo.total',
            'datas': datas,
            'nodestroy': True,                        
            }
activoTotal()

class revalCotiza(osv.Model):
    _name = 'reval.cotiza'
    _columns = dict(
        rev_id = fields.many2one('account.asset.reval','Revalorizacion'),
        name = fields.many2one('res.partner','Proveedor',required=True),
        num = fields.char('Numero Cotizacion',size=10,required=True),
        monto = fields.float('Valor'),
    )
revalCotiza()

class accountAssetDepLine(osv.Model):
    _inherit = 'account.asset.depreciation.line'
    _columns = dict(
        rev_id = fields.many2one('account.asset.reval','Revalorizacion'),
    )
accountAssetDepLine()

class accountAssetReval(osv.Model):
    _name = 'account.asset.reval'
    _description = 'Revalorizacion de activos fijos'
    
    def write(self, cr, uid, id, vals, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        if vals.get('asset_id'):
            asset = asset_obj.browse(cr, uid, vals['asset_id'])
            vals['valor_ant']=asset.purchase_value
            vals['dep_acumulada_ant']=asset.depreciacion
            vals['residual_ant']=asset.value_residual
        return super(accountAssetReval, self).write(cr, uid, id ,vals, context=None)

    def create(self, cr, uid, vals, context):
        asset_obj = self.pool.get('account.asset.asset')
        asset = asset_obj.browse(cr, uid, vals['asset_id'])
        vals['valor_ant']=asset.purchase_value
        vals['dep_acumulada_ant']=asset.depreciacion
        vals['residual_ant']=asset.value_residual
        vals['anios_ant']=asset.method_number
        vals['actual_ant']=asset.valor_actual
        rev_id = super(accountAssetReval, self).create(cr, uid, vals, context=None)
        return rev_id    

    def unlink(self, cr, uid, ids, *args, **kwargs):
        for reg in self.browse(cr, uid, ids):
            if reg.name!='/':
                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar registros con numero'))
        return super(accountAssetReval, self).unlink(cr, uid, ids, *args, **kwargs)    

    def rev_calcula(self, cr, uid, ids, context=None):
        rev_obj = self.pool.get('account.asset.reval')
        proporcion = 0
        for this in self.browse(cr, uid, ids,context=None):
            if this.valor>0:
                dep_proporcion = (this.valor*this.dep_acumulada_ant)/this.valor_ant 
                res_proporcion = (this.valor*this.residual_ant)/this.valor_ant
                rev_obj.write(cr, uid, this.id,{
                    'nueva_depreciacion':dep_proporcion,
                    'residual_actual':res_proporcion,
                })
        return True

    def rev_autoriza(self, cr, uid, ids, context=None):
        rev_obj = self.pool.get('account.asset.reval')
        obj_sequence = self.pool.get('ir.sequence')
        for this in self.browse(cr, uid, ids):
            #validar que no sea el mismo activo en la misma fecha
            rev_ids = rev_obj.search(cr, uid, [('asset_id','=',this.asset_id.id),('date','=',this.date),('id','!=',this.id)])
            if rev_ids:
                raise osv.except_osv(('Operación no permitida !'), ('No puede tener revalorizacion del mismo activo en la misma fecha'))
            if this.name=='/':
                aux_name = obj_sequence.get(cr, uid, 'account.asset.reval')
                rev_obj.write(cr, uid, ids[0],{'state':'Autorizado','name':aux_name})
            else:
                rev_obj.write(cr, uid, ids[0],{'state':'Autorizado'})
        return True

    def rev_ejecuta(self, cr, uid, ids, context=None):
        rev_obj = self.pool.get('account.asset.reval')
        asset_obj = self.pool.get('account.asset.asset')
        log_obj = self.pool.get('log.deprecia')
        dep_obj = self.pool.get('account.asset.depreciation.line')
        for this in self.browse(cr, uid, ids):
            asset_obj.write(cr, uid, [this.asset_id.id],{'revalorizado':True,'valor':this.valor,'anios_depreciacion':this.depreciacion,
                                                         'residual_actual':this.residual_actual,'fecha_revalorizado':this.date})
            #crear la linea de la depreciacion que se carga en la revalorizacion
            aux_desc = 'Revalorizacion ' + this.name
            log_obj.create(cr, uid, {
                'asset_id':this.asset_id.id,
                'date':this.date,
                'desc':aux_desc,
                'valor':this.nueva_depreciacion,
            })
            dep_obj.create(cr, uid, {
                'asset_id':this.asset_id.id,
                'depreciation_date':this.date,
                'amount':this.nueva_depreciacion,
                'name':aux_desc,
                'type':'Larga Duracion',
                'rev_id':this.id,
                'sequence':1,
                'remaining_value':0,
                'depreciated_value':this.nueva_depreciacion,
            })
        rev_obj.write(cr, uid, ids[0],{'state':'Ejecutado'})
        return True

    def rev_borrador(self, cr, uid, ids, context=None):
        rev_obj = self.pool.get('account.asset.reval')
        asset_obj = self.pool.get('account.asset.asset')
        rev_obj.write(cr, uid, ids[0],{'state':'Borrador'})
#        for this in self.browse(cr, uid, ids):
#            asset_obj.write(cr, uid, [this.asset_id.id],{'purchase_value':this.valor_ant,
#                                                         'salvage_value':this.residual_ant,
#                                                         'depreciacion':this.dep_acumulada_ant,
#                                                         'method_number':this.anios_ant,
#                                                     })
        return True

    def onchange_asset_reval(self, cr, uid, ids, asset_id, context={}):
        asset_obj = self.pool.get('account.asset.asset')
        asset = asset_obj.browse(cr, uid, asset_id)
        vals = {}
        return {'value':{'valor_ant':asset.purchase_value,'dep_acumulada_ant':asset.depreciacion,'residual_ant':asset.value_residual,
                         'actual_ant':asset.valor_actual,'anios_ant':asset.method_number}}

    def _amount_revaloriza(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        po_line_obj = self.pool.get('purchase.order.line')
        po_obj = self.pool.get('purchase.order')
        fiscal_obj = self.pool.get('account.fiscal.position')
        base_i = 0
        for revaloriza in self.browse(cr, uid, ids, context=context):
            res[revaloriza.id] = {
                'diferencia': 0.0,
                }
            aux = 0
            aux = revaloriza.valor - revaloriza.valor_ant 
            res[revaloriza.id]['diferencia'] = aux
        return res

    _columns = dict(
        diferencia = fields.function(_amount_revaloriza, string='Diferencia', multi="tl",store=True),
        category_id = fields.related('asset_id','category_id',relation='account.asset.category',type='many2one',store=True,string="Categoria"),
        depreciation_line_ids = fields.one2many('account.asset.depreciation.line','rev_id','Depreciacion'),
        name = fields.char('Numero',size=6),
        asset_id = fields.many2one('account.asset.asset','Activo',required=True),
        date = fields.date('Fecha Revalorizacion'),
        perito_id = fields.many2one('res.partner','Evaluador',required=True),
        autorizado_id = fields.many2one('hr.employee','Autorizado por'),
        comision_ids = fields.many2many('hr.employee','rev_pa_id','rev_id','pa_id','Comision'),
        valor_ant = fields.float('Valor Anterior $'),
        fecha_ant = fields.date('Fecha Anterior'),
        dep_acumulada_ant = fields.float('Dep. Acumulada Anterior'),
        anios_ant = fields.integer('Anios Anterior'),
        nueva_depreciacion = fields.float('Dep. Acumulada'),
        residual_ant = fields.float('Residual Anterior'),
        actual_ant = fields.float('Valor Actual Anterior'),
        valor = fields.float('Nuevo Valor $',help="Valor adicional revalorizado"),
        fecha = fields.date('Fecha compra'),
        residual_actual = fields.float('Residual'),
        depreciacion = fields.integer('Anios Depreciacion'),
        state = fields.selection([('Borrador','Borrador'),('Autorizado','Autorizado'),('Ejecutado','Ejecutado')],'Estado'),
        move_id = fields.many2one('account.move','Asiento Contable'),
        cotiza_ids = fields.one2many('reval.cotiza','rev_id','Detalle Cotizaciones'),
    )
    _defaults = dict(
        state = 'Borrador',
        name = '/',
    )

accountAssetReval()

class assetReval(osv.Model):
    _inherit = 'account.asset.asset'
    _columns = dict(
        fecha_revalorizado = fields.date('Fecha Revalorizacion'),
        residual_actual = fields.float('Residual'),
        anios_depreciacion = fields.integer('Anios Depreciacion'),
        valor = fields.float('Nuevo Valor $'),
        nueva_depreciacion = fields.float('Dep. Acumulada'),
        revalorizado = fields.boolean('Revalorizado'),
        rev_ids = fields.one2many('account.asset.reval','asset_id','Detalle Revalorizacion'),
    )

    def recompute_dep(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('account.asset.depreciation.line')
        monto_a_depreciar = monto_anio = 0
        for this in self.browse(cr, uid, ids):
            aux_10 = this.valor * 0.10
            monto_a_depreciar = this.valor - aux_10
            if monto_a_depreciar>0 and this.depreciacion>0:
                monto_anio = monto_a_depreciar / this.anios_depreciacion
                lines_dep_antes = line_obj.search(cr, uid, [('asset_id','=',this.id)],order='depreciation_date desc')
                linea_antes = line_obj.browse(cr, uid, lines_dep_antes[0])
                fecha_revalorizado = datetime.strptime(this.fecha_revalorizado, '%Y-%m-%d')
                #depreciation_date = datetime(fecha_revalorizado.year, 1, 1)
                day = fecha_revalorizado.day
                month = fecha_revalorizado.month
                year = fecha_revalorizado.year
                depreciation_date = (datetime(year, month, day) + relativedelta(months=+this.method_period))
                aux_seq = linea_antes.sequence
                for i in range(this.anios_depreciacion):
                    line_obj.create(cr, uid, {'asset_id':this.id,'amount':monto_anio,'type':'Larga Duracion','name':'Revalorizado','remaining_value':0,
                                              'depreciated_value':0,'state':'open','depreciation_date':depreciation_date.strftime('%Y-%m-%d'),'sequence':aux_seq})
                    day = depreciation_date.day
                    month = depreciation_date.month
                    year = depreciation_date.year
                    aux_seq += 1
                    depreciation_date = (datetime(year, month, day) + relativedelta(months=+this.method_period))
        return True

assetReval()
