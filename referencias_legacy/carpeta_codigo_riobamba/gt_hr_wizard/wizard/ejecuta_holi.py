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

class ejecutaHoli(osv.TransientModel):

   _name ='ejecuta.holi'
   _columns = dict(
      name = fields.char('Descripcion(Perido 20.. - 20..)',size=32),
      date_start = fields.date('Fecha Desde'),
      date_stop = fields.date('Fecha Hasta'),
   )
   
   def ejecuta_holi(self, cr, uid, ids, context):
      employee_obj = self.pool.get('hr.employee')
      holi_obj = self.pool.get('holidays.period')
      if context is None:
         context = {}
      data = self.read(cr, uid, ids)[0]
      aux_name = data['name']
      aux_date_start = data['date_start']
      aux_date_stop = data['date_stop']
      cr.execute('''select employee_id from hr_contract where activo=True group by employee_id''')
      result = cr.fetchall()
      for employee_id in result:
         holi_obj.create(cr, uid, {
            'name':aux_name,
            'date_start':aux_date_start,
            'date_stop':aux_date_stop,
            'employee_id':employee_id[0],
         })
      return {'type':'ir.actions.act_window_close' }

ejecutaHoli()


