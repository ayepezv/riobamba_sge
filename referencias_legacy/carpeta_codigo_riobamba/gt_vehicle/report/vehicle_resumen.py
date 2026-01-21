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


from datetime import *
import time
from report import report_sxw
import calendar
from osv import osv, fields
from tools import ustr

class vehicleResumen(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(vehicleResumen, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                '_months_year':self._months_year,
                'lines':self.lines,
                'sum_km':self.sum_km,
               
                })   
        
    def set_context(self, objects, data, ids, report_type=None):       
        objects=self.pool.get('vehicle.vehicle').browse(self.cr,self.uid,data['form']['vehicle_id'])      
        if objects[0].vehicle_type=='contratado':
            return super(vehicleResumen, self).set_context(objects, data, ids, report_type=report_type)
        else:
            raise osv.except_osv('Error', 'Reporte solo para vehículos contratados')
            
        
    def _months_year(self,resumen):  
        res = {}                       
        depart_id = self.pool.get('hr.department').search(self.cr, self.uid, [('name','ilike','ADMINISTRACION Y LOGISTICA')])
        depart_id = self.pool.get('hr.department').browse(self.cr, self.uid,depart_id)[0]
        if depart_id:
            if depart_id.manager_id:
                res['director']=ustr(depart_id.manager_id.complete_name.upper())         
        group_id = self.pool.get('ir.model.data').search(self.cr,self.uid, [('name','=','group_vehicle_manager')])
        if group_id:
            group_id = self.pool.get('ir.model.data').browse(self.cr, self.uid,group_id )          
            id_admin=1   
            rel= self.cr.execute('select * from res_groups_users_rel where uid!='+str(id_admin)+' and gid='+str(group_id[0].res_id))
            rel = self.cr.dictfetchall()       
            if rel:
                empleado_id = self.pool.get('hr.employee').search(self.cr, self.uid, [('user_id','=',rel[0]['uid'])]) 
                if empleado_id:
                    empleado = self.pool.get('hr.employee').browse(self.cr, self.uid, empleado_id[0])
                    res['manager']=ustr(empleado.complete_name.upper())                  
        month = calendar.month_name[int(self.datas['form']['months'])]
        res['month']=month.upper()
        res['year']=self.datas['form']['years']
        return res   
    
    def lines(self,resumen):                             
        year=self.datas['form']['years']   
        total_km=0
        total_days=0
        vector_days=[]
        month = calendar.month_name[int(self.datas['form']['months'])]   
        days=calendar.monthrange(int(year), int(self.datas['form']['months']))[1]           
        vector_days=range(int(days))
        i=ind=pos=0       
        for i in range(int(days)):      
            vector_days[i]=[i+1]                      
        mov_obj = self.pool.get('movilization.order')
        asis_obj = self.pool.get('vehicle.asistencia')                  
        mov_ids=mov_obj.search(self.cr,self.uid,[('vehicle_id','=',resumen.id),('state','=','realizado')])
        asis_ids=asis_obj.search(self.cr,self.uid,[('vehicle_id','=',resumen.id)])        
        for line in mov_obj.browse(self.cr,self.uid,mov_ids):            
            mov_year= datetime.strptime(line.movilization_date, "%Y-%m-%d %H:%M:%S").year
            mov_month= datetime.strptime(line.movilization_date, "%Y-%m-%d %H:%M:%S").month
            mov_days= datetime.strptime(line.movilization_date, "%Y-%m-%d %H:%M:%S").day
            hour_start=line.movilization_date.__str__().split(' ')[1].__str__().split(':00')[0]
            hour_stop=line.return_date.__str__().split(' ')[1].__str__().split(':00')[0]                    
            if int(self.datas['form']['months'])==int(mov_month) and int(self.datas['form']['years'])==int(mov_year):                        
                if len(vector_days[int(mov_days)-1])<=2:
                    ind+=1                                      
                    name_route=line.route_ids[0].desde
                    km_start=line.km_start
                    km_stop=line.km_end
                    for wizard_line in line.route_ids:
                        name_route=name_route+"-"+wizard_line.hasta                                 
                    vector_days[int(mov_days)-1]=[int(mov_days),'','','',name_route,km_start,km_stop,int(km_stop)-int(km_start)]
                else:
                    ind+=1                                      
                    name_route=line.route_ids[0].desde
                    km_start=line.km_start
                    km_stop=line.km_end                    
                    for wizard_line in line.route_ids:
                        name_route=name_route+"-"+wizard_line.hasta
                    vector_days[int(mov_days)-1][4]+=", "+name_route
                    if km_start<vector_days[int(mov_days)-1][5]:                                                
                        vector_days[int(mov_days)-1][5]=km_start
                    if km_stop>vector_days[int(mov_days)-1][6]:                        
                        vector_days[int(mov_days)-1][6]=km_stop
                    vector_days[int(mov_days)-1][7]=int(vector_days[int(mov_days)-1][6])-int(vector_days[int(mov_days)-1][5])
        from datetime import *
        for line in asis_obj.browse(self.cr,self.uid,asis_ids):
            mov_year= datetime.strptime(line.fecha, "%Y-%m-%d").year
            mov_month= datetime.strptime(line.fecha, "%Y-%m-%d").month
            mov_days= datetime.strptime(line.fecha, "%Y-%m-%d").day
            hour_start = time(hour=int(line.hora_entrada), minute=int((line.hora_entrada-int(line.hora_entrada))*60))            
            hour_stop= time(hour=int(line.hora_salida), minute=int((line.hora_salida-int(line.hora_salida))*60))
            if int(self.datas['form']['months'])==int(mov_month) and int(self.datas['form']['years'])==int(mov_year):
                if len(vector_days[int(mov_days)-1])<=2:
                    ind+=1
                    vector_days[int(mov_days)-1]=[int(mov_days),hour_start.strftime('%H:%M'),hour_stop.strftime('%H:%M'),ustr(line.responsable_id.complete_name),"-","-","-","0"]
                else:  
                    ind+=1                  
                    vector_days[int(mov_days)-1][1]=hour_start.strftime('%H:%M')
                    vector_days[int(mov_days)-1][2]=hour_stop.strftime('%H:%M')
                    vector_days[int(mov_days)-1][3]=ustr(line.responsable_id.complete_name)
        if ind<=0:  
            raise osv.except_osv('Error!!', ustr('No existen recorridos ni registros de asistencia para el vehículo ')+ ustr(resumen.name))
        return vector_days
    
    def sum_km(self,resumen):                 
        total=0
        total_km=0
        total_days=cost_days=cost_kms=iva=total_cost=cost_total=0     
        result=[]                   
        days=[]
        mov_obj = self.pool.get('movilization.order')          
        vehicle_obj = self.pool.get('vehicle.vehicle').browse(self.cr,self.uid,resumen.id)    
        asis_obj = self.pool.get('vehicle.asistencia')                     
        mov_ids=mov_obj.search(self.cr,self.uid,[('vehicle_id','=',resumen.id),('state','=','realizado')])
        asis_ids=asis_obj.search(self.cr,self.uid,[('vehicle_id','=',resumen.id)])
        for line in mov_obj.browse(self.cr,self.uid,mov_ids):
            mov_year= datetime.strptime(line.movilization_date, "%Y-%m-%d %H:%M:%S").year
            mov_month= datetime.strptime(line.movilization_date, "%Y-%m-%d %H:%M:%S").month
            mov_days= datetime.strptime(line.movilization_date, "%Y-%m-%d %H:%M:%S").day
            if int(self.datas['form']['months'])==int(mov_month) and int(self.datas['form']['years'])==int(mov_year):                      
                total_km+=int(line.km_total)
                days+=[mov_days]
        for line in asis_obj.browse(self.cr,self.uid,asis_ids):
            mov_year= datetime.strptime(line.fecha, "%Y-%m-%d").year
            mov_month= datetime.strptime(line.fecha, "%Y-%m-%d").month
            mov_days= datetime.strptime(line.fecha, "%Y-%m-%d").day
            if int(self.datas['form']['months'])==int(mov_month) and int(self.datas['form']['years'])==int(mov_year):
                days+=[mov_days]                            
        days=list(set(days))
        total_days=len(days)
        if vehicle_obj.category_id:
            cost_days=round(int(total_days)*vehicle_obj.category_id.cost_day,2)
            cost_kms=round(int(total_km)*vehicle_obj.category_id.cost_km,2)
        else:            
            
            raise osv.except_osv('Error!!', ustr('Le falta configurar la categoría del vehículo contratado ')+ ustr(vehicle_obj.name))            
        cost_total=round(cost_days+cost_kms,2)        
        iva=round(cost_total*0.12,2)
        total_cost=round(iva+cost_total,2)
        res = {
                    'total_km' : total_km,
                    'total_days' : total_days,
                    'cost_days' : cost_days,
                    'cost_kms' : cost_kms,
                    'iva' : iva,
                    'total_cost' : total_cost,
                    'subtotal_cost' : cost_total,
                }
        result.append(res)
        return result
            
                                                
report_sxw.report_sxw('report.Recorrido', 'vehicle.print.resumen', 'gt_vehicle/report/vehicle_resumen.rml', parser=vehicleResumen, header=False)

