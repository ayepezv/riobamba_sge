#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from datetime import datetime
from report import report_sxw
from tools import ustr

class vehicleRoute(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(vehicleRoute, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'sum_km':self.sum_km,
                'director_name':self.director_name,
                'get_lines':self.get_lines,
                })   
        
    def director_name(self,movilization): #members_name 
        res={}          
        depart_id = self.pool.get('hr.department').search(self.cr, self.uid, [('name','ilike','ADMINISTRACION Y LOGISTICA')])
        depart_id = self.pool.get('hr.department').browse(self.cr, self.uid,depart_id)[0]
        if depart_id:
            if depart_id.manager_id:
                res['director']=ustr(depart_id.manager_id.complete_name.upper())
        if movilization.responsable_id:
            res['solicitante']=ustr(movilization.responsable_id.complete_name.upper())+"\n"+ustr(movilization.responsable_id.job_id.name+"\n"+movilization.responsable_id.department_id.name.upper())
            depart_id = self.pool.get('hr.department').search(self.cr, self.uid, [('name','ilike',ustr(movilization.responsable_id.department_id.name))])
            depart_id = self.pool.get('hr.department').browse(self.cr, self.uid,depart_id)[0]
            if depart_id.manager_id:
                res['autorizado']=ustr(depart_id.manager_id.complete_name.upper())+"\n"+ustr(depart_id.manager_id.job_id.name.upper())+"\n"+ustr(depart_id.manager_id.department_id.name.upper())            
        return res
    
    def sum_km(self,movilization):                 
        total=0                              
        for line in movilization.route_ids:        
            total=int(total+line.km)        
        return total
    
    def get_lines(self,movilization):                 
        total=0  
        res={}   
        if movilization.vehicle_id_asigned:                       
            res['code']='#'+ustr(movilization.vehicle_id_asigned.number)+' - '+ustr(movilization.vehicle_id_asigned.name)
            for driver in movilization.vehicle_id_asigned.driver_ids:
                if driver.actual==True:                    
                    res['ci']=driver.name.ci                    
                    res['nombre']=driver.name.name                                                            
        if movilization.vehicle_id:
            if movilization.vehicle_id.vehicle_type=='planta':                
                res['code']='#'+ustr(movilization.vehicle_id.number)+' - '+ustr(movilization.vehicle_id.name)
            if movilization.vehicle_id.vehicle_type=='contratado':
                res['code']=ustr(movilization.vehicle_id.name)
            for driver in movilization.vehicle_id.driver_ids:
                if driver.actual==True:                    
                    res['ci']=driver.name.ci                    
                    res['nombre']=driver.name.name                                                            
        return res
     
report_sxw.report_sxw('report.vehicleRoute', 'movilization.order', 'gt_vehicle/report/vehicle_route.rml', parser=vehicleRoute, header=True)
