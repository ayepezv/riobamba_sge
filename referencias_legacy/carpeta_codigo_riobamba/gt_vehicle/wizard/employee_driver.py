# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from osv import fields, osv
from time import strftime
from tools import ustr

class driverEmployee(osv.osv_memory):
   _name = 'driver.employee'
   _description="Choferes"

   def create_driver(self, cr, uid, ids, context):
       mod_obj = self.pool.get('ir.model.data')
       act_obj = self.pool.get('ir.actions.act_window')
       driver_obj = self.pool.get('vehicle.driver')
       chofer_obj = self.pool.get('hr.employee')
       if context is None:
           context = {}
       for this in self.browse(cr, uid, ids):
          nombre = ustr(this.employee_id.complete_name)
          if this.employee_id.house_phone:
             telf = this.employee_id.house_phone
          driver_obj.create(cr, uid,{
                'employee_id':str(this.employee_id.id),
                'name':nombre,
                'ci':this.employee_id.name,
                'telf':this.employee_id.house_phone,
                'telf_oficina':this.employee_id.work_phone,
                'direccion':this.employee_id.address,
                'sex':this.employee_id.gender,
                'marital_id':this.employee_id.marital_id.id,
                'fec_nac':this.employee_id.birthday,                
                'tipo_licencia':'c',
                'fec_caducidad':time.strftime("%Y-%m-%d"),
                'driver_type':'planta',
                  },context)    
          chofer_obj.write(cr, uid, this.employee_id.id,{
                        'driver' : True,
                        },context)
       result = mod_obj.get_object_reference(cr, uid, 'gt_vehicle', context['view_id'])
       id = result and result[1] or False
       result = act_obj.read(cr, uid, [id], context={})[0]            
       return result
   
   _columns = dict(       
       employee_id = fields.many2one('hr.employee', 'Empleado Relacionado',required=True),       
       )
   

driverEmployee()

class Employee(osv.Model):
  _inherit = "hr.employee"
   
  _columns = dict(           
       driver= fields.boolean('Chofer'),       
       )
    
#  def write(self, cr, uid, ids, vals, context):
#       vals_driver={}
#       chofer_obj = self.pool.get('hr.employee')
#       driver_obj = self.pool.get('vehicle.driver')
#       if context is None:
#           context = {}
#       if not 'driver' in vals: 
#           for this in self.browse(cr, uid, ids):                
#                if this.driver:        
#                    ci = this.name
#                    if 'name' in vals:
#                        vals_driver['ci']=vals['name']
#                    if 'employee_first_name' in vals:
#                        vals_driver['name']=vals['employee_first_name']+" "+this.employee_second_name+" "+this.employee_first_lastn#ame+" "+this.employee_second_lastname
#                    if 'employee_second_name' in vals:
#                        vals_driver['name']=this.employee_first_name+" "+vals['employee_second_name']+" "+this.employee_first_lastn#ame+" "+this.employee_second_lastname
#                    if 'employee_first_lastname' in vals:
#                        vals_driver['name']=this.employee_first_name+" "+this.employee_second_name+" "+vals['employee_first_lastnam#e']+" "+this.employee_second_lastname
#                    if 'employee_second_lastname' in vals:
#                        vals_driver['name']=this.employee_first_name+" "+this.employee_second_name+" "+this.employee_first_lastname#+" "+vals['employee_second_lastname']
#                    if 'employee_first_name' in vals and 'employee_second_name' in vals and 'employee_first_lastname' in vals and '#employee_second_lastname' in vals:
#                        vals_driver['name']=vals['employee_first_name']+" "+vals['employee_second_name']+" "+vals['employee_first_l#astname']+" "+vals['employee_second_lastname']
#                    if 'house_phone' in vals:
#                        vals_driver['telf']=vals['house_phone']
#                    if 'work_phone' in vals:
#                        vals_driver['telf_oficina']=vals['work_phone']
#                    if 'address' in vals:
#                        vals_driver['direccion']=vals['address']
 #                   if 'gender' in vals:
 #                       vals_driver['sex']=vals['gender']
 #                   if 'marital_id' in vals:
 #                       vals_driver['marital_id']=vals['marital_id']
 #                   if 'birthday' in vals:
 #                       vals_driver['fec_nac']=vals['birthday']
 #                   driver_id = driver_obj.search(cr, uid, [('ci','=',ci)])          
 #                   driver_obj.write(cr, uid, driver_id,vals_driver,context
 #                             )                
  #     return super(Employee, self).write(cr, uid,ids, vals, context=None)
            
  _defaults = dict(
        
        driver = False,
        )
   
Employee()


