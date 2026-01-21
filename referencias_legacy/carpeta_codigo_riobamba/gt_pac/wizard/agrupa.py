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
from gt_tool import XLSWriter

class exportPac(osv.TransientModel):
   _name = 'export.pac'
   _columns = dict(
      year_id = fields.many2one('account.fiscalyear','Period'),
      pac_ids = fields.many2many('purchase.pac','exp_e_p','e_id','p_id','PAC'),
      tipo = fields.selection([('Todo','Todo'),('Seleccionar','Seleccionar')],'Opcion'),
      datas = fields.binary('Archivo'),
      datas_fname = fields.char('Nombre archivo', size=32),
   )

   def exportaPac(self, cr, uid, ids, context):
      pac_obj = self.pool.get('purchase.pac')
      if context is None:
         context = {}
      pac_ids = []
      for data in self.browse(cr, uid, ids):
         writer = XLSWriter.XLSWriter()
         cabecera_all = ['Departamento','Producto','Tipo Compra','Unidad','Cantidad','Precio Unitario','Total','Cuatrimestre 1','Cuatrimestre 2','Cuatrimestre 3','Tipo Producto','Catalogo Electronico','Tipo Procedimiento','Fondo BID','Regimen','Tipo Presupuesto']
         writer.append(cabecera_all)
         if data.tipo=='Todo':
            pac_ids = pac_obj.search(cr, uid, [('year_id','=',data.year_id.id)])
         else:
            for pac in data.pac_ids:
               pac_ids.append(pac.id)
         for pac_id in pac_ids:
            pac = pac_obj.browse(cr, uid, pac_id)
            aux_department = pac.department_id.name
            for line in pac.line_ids:
               auxc1 = auxc2 = auxc3 = auxcat = bid = 'No'
               if line.p1:
                  auxc1 = 'Si'
               if line.p2:
                  auxc2 = 'Si'
               if line.p3:
                  auxc3 = 'Si'
               if line.catalogo:
                  auxcat = 'Si'
               if line.bid:
                  bid = 'Si'
               linea_pac = [aux_department,line.name.name,line.tipo,line.uom.name,line.qty,line.pu,line.total,auxc1,auxc2,auxc3,line.tipo_producto,auxcat,line.procedimiento.name,bid,line.regimen,line.tipo_budget]
               writer.append(linea_pac)
         writer.save("pac.xls")
         out = open("pac.xls","rb").read().encode("base64")
         self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'pac.xls'})
      return True

   _defaults = dict(
      tipo = 'Todo',
   )
exportPac()

class agrupaPac(osv.TransientModel):
   _name ='agrupa.pac'
   _columns = dict(
      department_id = fields.many2one('hr.department', 'Departamento',required=True),
      pac_ids = fields.many2many('purchase.pac','p_a_id','p_id','a_id','Pac Agrupar'),
      user_id = fields.many2one('res.users','Creado por'),
   )
   
   def agrupa_pac(self, cr, uid, ids, context):
      pac_obj = self.pool.get('purchase.pac')
      pac_line_obj = self.pool.get('purchase.pac.line')
      if context is None:
         context = {}
      for data in self.browse(cr, uid, ids):
         if data.user_id.context_department_id.id!=data.department_id.id:
            raise osv.except_osv(('Error de usuario'), ('Solo el usuario del mismo departamento puede agrupar'))
         if data.pac_ids:
            pac_aux = data.pac_ids[0]
            aux_desc = 'PAC CONSOLIDADO DE ' + data.department_id.name
            pac_id = pac_obj.create(cr, uid, {
               'name':aux_desc,
               'creado_id':uid,
               'department_id':data.department_id.id,
               'year_id':pac_aux.year_id.id,
               'state':'Borrador',
            })
            for pac in data.pac_ids:
               for line in pac.line_ids:
                  pac_line_obj.write(cr, uid, line.id,{
                     'pac_id':pac_id,
                  })
      return {'type':'ir.actions.act_window_close' }

   def _get_user(self,cr, uid, ids,context=None):
      return uid

   _defaults = dict(
      user_id = _get_user,
   )

agrupaPac()


