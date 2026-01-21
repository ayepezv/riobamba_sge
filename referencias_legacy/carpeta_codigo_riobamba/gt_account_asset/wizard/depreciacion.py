# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

import time
from osv import fields, osv
from time import strftime

class depreciaLine(osv.Model):
   _name = 'deprecia.line'
   _columns = dict(
      d_id = fields.many2one('asset.deprecia','Depreciacion'),
      category_id = fields.many2one('account.asset.category','Categoria'),
      num = fields.integer('Numero Activos'),
      total = fields.float('Monto Total'),
   )
depreciaLine()

class depreciaActivoDet(osv.Model):
   _name = 'deprecia.activo.det'
   _columns = dict(
      de_id = fields.many2one('asset.deprecia','Deprecia'),
      asset_id = fields.many2one('account.asset.asset','Activo'),
      amount = fields.related('line_id','amount',type='float',string="Monto",store=True),
      line_id = fields.many2one('account.asset.depreciation.line','Depreciacion'),
   )
depreciaActivoDet()
class assetDeprecia(osv.Model):

   _name ='asset.deprecia'
   _columns = dict(
      det_ids = fields.one2many('deprecia.activo.det','de_id','Detalle Activos'),
      year_id = fields.many2one('account.fiscalyear','Anio Depreciar'),
      line_ids = fields.one2many('deprecia.line','d_id','Detalle'),
      state = fields.selection([('Borrador','Borrador'),('Ejecutado','Ejecutado')],'Estado'),
   )

   _defaults = dict(
      state ='Borrador',
   )

   def imprimeDep(self, cr, uid, ids, context):
        if not context:
            context = {}
        dep = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [dep.id], 'model': 'asset.deprecia'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'deprecia',
            'model': 'asset.deprecia',
            'datas': datas,
            'nodestroy': True,                        
            }      
        
   def ejecutaDep(self, cr, uid, ids, context):
      log_obj = self.pool.get('log.deprecia')
      asset_obj = self.pool.get('account.asset.asset')
      deprecia_obj = self.pool.get('asset.deprecia')
      for this in self.browse(cr, uid, ids):
         if this.year_id.state=='done':
            raise osv.except_osv('Error de configuracion', 'El anio fiscal esta cerrado, no puede ejecutar esta accion')         
         for line in this.det_ids:
            aux = 'Depreciacion ' + this.year_id.name
            aux_valor = line.asset_id.depreciacion + line.amount
            log_obj.create(cr, uid, {
               'asset_id':line.asset_id.id,
               'date':this.year_id.date_stop,
               'line_id':line.line_id.id,
               'desc':aux,
               'anterior':line.asset_id.depreciacion,
               'valor':line.amount,
               'actual':aux_valor,
            })
            #sumo la dep del activo
            valor_actual = line.asset_id.purchase_value - aux_valor
            asset_obj.write(cr,uid, [line.asset_id.id],{
               'depreciacion':aux_valor,
               'valor_actual':valor_actual,
               'dep_periodo':line.amount,
            })
            deprecia_obj.write(cr, uid, this.id, {'state':'Ejecutado'})
      return True

   def generaComprobanteDep(self, cr, uid, ids, context):
      move_obj = self.pool.get('account.move')
      period_obj = self.pool.get('account.period')
      journal_obj = self.pool.get('account.journal')
      move_line_obj = self.pool.get('account.move.line')
      for this in self.browse(cr, uid, ids):
        state_aux = 'draft'
        company_aux = 1
        currency_aux = 2
        depreciation_date = this.year_id.date_stop
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
        for line in this.line_ids:
           categoria = line.category_id
           move_line_obj.create(cr, uid, {
              'name': categoria.name,
              'ref': categoria.name,
              'move_id': move_id,
              'account_id': categoria.account_depreciation_id.id,
              'debit': 0.0,
              'credit': line.total,
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
              'debit': line.total,
              'period_id': period_ids and period_ids[0] or False,
              'journal_id': journal_ids[0],
              'currency_id': currency_aux,
              'date': depreciation_date,
           })
      return move_id

   def computeActivo(self, cr, uid, ids, context):
      dep_line = self.pool.get('account.asset.depreciation.line')
      deprecia_obj = self.pool.get('deprecia')
      deprecia_line_obj = self.pool.get('deprecia.line')
      category_obj = self.pool.get('account.asset.category')
      det_obj = self.pool.get('deprecia.activo.det')
      asset_obj = self.pool.get('account.asset.asset')
      category_ids = category_obj.search(cr, uid, [('deprecia','=',True)])
      if not category_ids:
         raise osv.except_osv(('Error de configuración'), ('No existen categorias a depreciar'))
      for this in self.browse(cr, uid, ids):
         id_aux = this.id
         line_ant_ids = deprecia_line_obj.search(cr, uid, [('d_id','=',id_aux)])
         if line_ant_ids:
            deprecia_line_obj.unlink(cr, uid, line_ant_ids)
         det_anterior_ids = det_obj.search(cr, uid, [('de_id','=',id_aux)])
         if det_anterior_ids:
            det_obj.unlink(cr, uid, det_anterior_ids)
         for category_id in category_ids:
            #aqui estaban los estate=open y debe cojer todo no importa la tabal esta ya
#            line_ids = dep_line.search(cr, uid, [('depreciation_date','>=',this.year_id.date_start),('depreciation_date','<=',this.year_id.date_stop),
#                                                 ('category_id','=',category_id),('state','=','open'),('type','=','Larga Duracion')])
#            asset_ids = asset_obj.search(cr, uid, [('category_id','=',category_id),('','',)])
            line_ids = dep_line.search(cr, uid, [('depreciation_date','>=',this.year_id.date_start),('depreciation_date','<=',this.year_id.date_stop),
                                                 ('category_id','=',category_id),('type','=','Larga Duracion'),('asset_id.state','=','open')])
            if line_ids:
               aux_total = 0
               for line_id in line_ids:
                  line = dep_line.browse(cr, uid, line_id)
                  #agrega el log en el activo
                  aux_total_dep = 0
                  aux_total_dep = line.asset_id.depreciacion + line.amount
                  if aux_total_dep<=line.asset_id.value_residual:
                     det_obj.create(cr, uid, {
                        'asset_id':line.asset_id.id,
                        'line_id':line.id,
                        'de_id':id_aux,
                     })
                     aux_total += line.amount
               deprecia_line_obj.create(cr, uid, {
                  'd_id':id_aux,
                  'category_id':category_id,
                  'num':len(line_ids),
                  'total':aux_total,
               })
      return True

   def computeActivo2(self, cr, uid, ids, context):
      #se uso para corregir la dep rio cuando no considerba los estados en lineas y algunas estabn draft
      dep_line = self.pool.get('account.asset.depreciation.line')
      deprecia_obj = self.pool.get('deprecia')
      deprecia_line_obj = self.pool.get('deprecia.line')
      category_obj = self.pool.get('account.asset.category')
      det_obj = self.pool.get('deprecia.activo.det')
      category_ids = category_obj.search(cr, uid, [('deprecia','=',True)])
      if not category_ids:
         raise osv.except_osv(('Error de configuración'), ('No existen categorias a depreciar'))
      for this in self.browse(cr, uid, ids):
         id_aux = this.id
         line_ant_ids = deprecia_line_obj.search(cr, uid, [('d_id','=',id_aux)])
         if line_ant_ids:
            deprecia_line_obj.unlink(cr, uid, line_ant_ids)
         det_anterior_ids = det_obj.search(cr, uid, [('de_id','=',id_aux)])
         if det_anterior_ids:
            det_obj.unlink(cr, uid, det_anterior_ids)
         for category_id in category_ids:
            #aqui estaban los estate=open y debe cojer todo no importa la tabal esta ya
#            line_ids = dep_line.search(cr, uid, [('depreciation_date','>=',this.year_id.date_start),('depreciation_date','<=',this.year_id.date_stop),
#                                                 ('category_id','=',category_id),('state','=','open'),('type','=','Larga Duracion')])
            line_ids = dep_line.search(cr, uid, [('depreciation_date','>=',this.year_id.date_start),('depreciation_date','<=',this.year_id.date_stop),
                                                 ('category_id','=',category_id),('type','=','Larga Duracion'),('state','=','draft')])
            if line_ids:
               aux_total = 0
               for line_id in line_ids:
                  line = dep_line.browse(cr, uid, line_id)
                  #agrega el log en el activo
                  det_obj.create(cr, uid, {
                     'asset_id':line.asset_id.id,
                     'line_id':line.id,
                     'de_id':id_aux,
                  })
                  aux_total += line.amount
               deprecia_line_obj.create(cr, uid, {
                  'd_id':id_aux,
                  'category_id':category_id,
                  'num':len(line_ids),
                  'total':aux_total,
               })
      return True

   def depreciarActivo2(self, cr, uid, ids, context):
      asset_obj = self.pool.get('account.asset.asset')
      category_obj = self.pool.get('acccount.asset.category')
      category_ids = category_obj.search(cr, uid, [('deprecia','=',True)])
      if not category_ids:
         raise osv.except_osv(('Error de configuración'), ('No existen categorias a depreciar'))
      for this in self.browse(cr, uid, ids):
         date_deprecia_aux = datetime.strptime(this.year_id.date_stop,'%Y-%m-%d').split('-')
         date_deprecia = date(int(date_deprecia_aux[0]), int(date_deprecia_aux[1]), int(date_deprecia_aux[2]))
         for category_id in category_ids:
            monto_categoria = 0
            category = category_obj.browse(cr, uid, category_id)
            num_anios = category.method_number
            asset_ids = asset_obj.search(cr, uid, [('category_id','=',category_id),('state','=','open'),('value_residual','>',0)])
            if asset_ids:
               for asset_id in asset_ids:
                  asset = asset_obj.browse(cr, uid, asset_id)
                  num_anios_activo = asset.method_number
                  if num_anios_activo > num_anios:
                     num_anios = num_anios_activo
                  date_compra_aux = datetime.strptime(asset.purchase_date,'%Y-%m-%d').spli('-')
                  date_compra = date( int(date_compra_aux[0]), int(date_compra_aux[1]), int(date_compra_aux[2]) )
                  resta = date_deprecia - date_compra
                  anios = resta.days/365 
                  if anios<num_anios:
                     #deprecia
                     monto_deprecia = 1 
                  monto_categoria += monto_deprecia
      return True
   
assetDeprecia()


