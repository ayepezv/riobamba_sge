# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from time import strftime, strptime
import base64
import xlrd
from XLSWriter import XLSWriter
import decimal_precision as dp
from osv import osv, fields

_STATE = [('draft','Borrador'),('pendiente','Aprobado/Pendiente Pago'),('pagado','Pagado')]

class hrVariosLine(osv.osv):
   _name = 'hr.varios.line'
   _description = 'Detalle Pagos Varios'
   _order = 'name_partner asc'

   def _validar_mayor_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.monto <= 0 or obj.descuento < 0 or obj.valor <0:
            return False
        return True
           
   _columns = dict(
      monto_anticipo = fields.float('Monto Anticipo'),
      name = fields.many2one('res.partner','Beneficiario',required=True),
      name_partner = fields.related('name','name',type='char',size=64,store=True),
      varios_id = fields.many2one('hr.varios','Pagos varios',ondelete='cascade'),
      descontado_id = fields.many2one('hr.employee','Empleado Descontado'),
      monto = fields.float('Valor',required=True, digits_compute=dp.get_precision('Account')),
      descuento = fields.float('Descuento', digits_compute=dp.get_precision('Account')),
      valor = fields.float('Valor Total', digits_compute=dp.get_precision('Account')),
      period_id = fields.related('varios_id','period_id',type="many2one",relation='account.period',string="Periodo",store=True),
       )

   _constraints = [
       (_validar_mayor_cero, 'Los valores deben ser mayor o igual a cero', ['monto']),
   ]
   
hrVariosLine()

class hrVarios(osv.osv):
    _name = 'hr.varios'
    _description = 'Pagos Varios'
    _order = 'id desc'

    _columns = dict(
       name = fields.text('Descripcion',required=True,states={'draft': [('readonly', False)]}),
       period_id = fields.many2one('account.period','Periodo',required=True,readonly=True,
                                   states={'draft': [('readonly', False)]}),
       observaciones = fields.char('Observaciones',size=128,readonly=True,states={'draft': [('readonly', False)]}),
       total = fields.float('Total'),
       line_ids = fields.one2many('hr.varios.line','varios_id','Detalle',readonly=True,states={'draft': [('readonly', False)]}),
       state = fields.selection(_STATE,'Estado'),
       archivo = fields.binary('Archivo'),
        )

    def load_varios_excel(self, cr, uid, ids, context=None):
       partner_obj = self.pool.get('res.partner')
       line_obj = self.pool.get('hr.varios.line')
       for this in self.browse(cr, uid, ids):
          anterior_ids = line_obj.search(cr, uid, [('varios_id','=',this.id)])
          line_obj.unlink(cr, uid, anterior_ids)
          if this.archivo:
             id_this = this.id
             arch = this.archivo
             arch_xls = base64.b64decode(arch)
             book = xlrd.open_workbook(file_contents=arch_xls)
             sh = book.sheet_by_name(book.sheet_names()[0])
             context={}
             for r in range(sh.nrows)[1:]:
                if sh.cell(r,0).value and sh.cell(r,1).value and sh.cell(r,2).value:
                  aux_ced = str(sh.cell(r,0).value)
                  partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced)],limit=1)
                  if not partner_ids:
                      raise osv.except_osv(('Error Datos !'),
                                           ("No existe beneficiario '%s'") % (aux_ced)) 
                  line_obj.create(cr,uid, {
                     'name':partner_ids[0],
                     'varios_id':id_this,
                     'monto':sh.cell(r,2).value,
                     'descuento':sh.cell(r,3).value,
                  })
       return True

    def print_varios(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.hr.varios'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.varios',
            'model': 'hr.varios',
            'datas': datas,
            'nodestroy': True,                        
            }

    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.state!='draft':
                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar, solo puede realizar esta operacion en estado Borrador'))
        return super(hrVarios, self).unlink(cr, uid, ids, *args, **kwargs)
    
    def a_borrador_varios(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'draft'})
        return True
 
    def pendiente_varios(self, cr, uid, ids, context=None):
       line_obj = self.pool.get('hr.varios.line')
       for this in self.browse(cr, uid, ids):
          for line in this.line_ids:
             aux_tot = line.monto - line.descuento - line.monto_anticipo
             line_obj.write(cr, uid, line.id,{
                'valor':aux_tot,
             })
       self.write(cr, uid, this.id,{'state':'pendiente'})
       return True

    _defaults = dict(
        state = 'draft',
        )

hrVarios()


class accountBeneficiario(osv.Model):
   _name = 'account.beneficiario'
   _columns = dict(
      name = fields.many2one('res.partner','Beneficiario'),
      valor = fields.float('Monto'),
      a_id = fields.many2one('account.move','Registro Contable'),
   )

accountBeneficiario()

class accountMovePago(osv.Model):
   _inherit = 'account.move'
   _columns = dict(
      varios_id = fields.many2one('hr.varios','Pagos Varios TTHH'),
      beneficiario_ids = fields.one2many('account.beneficiario','a_id','Detalle Beneficiarios'),
      archivo = fields.binary('Archivo'),
   )

   def creaVarios(self, cr, uid, ids, context=None):
       varios_obj = self.pool.get('hr.varios')
       line_obj = self.pool.get('hr.varios.line')
       for this in self.browse(cr, uid, ids):
          if this.varios_id:
             anterior_ids = line_obj.search(cr, uid, [('varios_id','=',this.varios_id.id)])
             if anterior_ids:
                line_obj.unlink(cr, uid, anterior_ids)
                varios_id = this.varios_id.id
          else:
             varios_id = varios_obj.create(cr, uid, {
                'name':this.narration,
                'period_id':this.period_id.id,
                'state':'pendiente',
             })
          for line in this.beneficiario_ids:  
             line_obj.create(cr,uid, {
                'name':line.name.id,
                'varios_id':varios_id,
                'valor':line.valor,
                'monto':line.valor,
             })
       self.write(cr, uid, ids, {'varios_id':varios_id,})
       return True

   def loadVariosExcel(self, cr, uid, ids, context=None):
      line_obj = self.pool.get('account.beneficiario')
      partner_obj = self.pool.get('res.partner')
      for this in self.browse(cr, uid, ids):
         antes_ids = line_obj.search(cr, uid,[('a_id','=',this.id)])
         if antes_ids:
            line_obj.unlink(cr, uid, antes_ids)
         if this.archivo:
            id_this = this.id
            arch = this.archivo
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
               if sh.cell(r,0).value and sh.cell(r,1).value and sh.cell(r,2).value:
                  aux_ced = str(sh.cell(r,0).value)
                  partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced)],limit=1)
                  if not partner_ids:
                     print "NO"
                     #raise osv.except_osv(('Error Datos !'),
                     #                     ("No existe beneficiario '%s'") % (aux_ced))
                  else:
                     line_obj.create(cr, uid, {
                        'a_id':this.id,
                        'name':partner_ids[0],
                        'valor':sh.cell(r,2).value,
                     })
         else:
            raise osv.except_osv(('Error Datos !'),
                                 ("No existe archivo para importar"))
      return True
    
   def loadVarios(self, cr, uid, ids, context=None):
      line_obj = self.pool.get('account.beneficiario')
      for this in self.browse(cr, uid, ids):
         antes_ids = line_obj.search(cr, uid,[('a_id','=',this.id)])
         if antes_ids:
            line_obj.unlink(cr, uid, antes_ids)
         for line in this.varios_id.line_ids:
            line_obj.create(cr, uid, {
               'a_id':this.id,
               'name':line.name.id,
               'valor':line.valor,
            })
      return True
         
accountMovePago()
