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

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from report import report_sxw
import calendar
from osv import osv, fields
from tools import ustr

class salvoconducto1(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(salvoconducto1, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                    'concat_name':self.concat_name,
                    'director_name':self.director_name,
                })
                    
    def concat_name(self, rutas): #members_name
        ruta=""       
        for line in rutas:
            ruta+= ustr(line.desde)+"-"+ustr(line.hasta)+", "               
        ruta=ruta[:-2]       
        return ruta
    
    def director_name(self): #members_name
        res={}              
        depart_id = self.pool.get('hr.department').search(self.cr, self.uid, [('name','ilike','ADMINISTRACION Y LOGISTICA')])
        depart_id = self.pool.get('hr.department').browse(self.cr, self.uid,depart_id)[0]
        if depart_id:
            if depart_id.manager_id:
                res['director']=ustr(depart_id.manager_id.complete_name.upper())+"\n"+ustr(depart_id.manager_id.job_id.name.upper())
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
                    if empleado.mobile_phone:                        
                        res['manager']=ustr(empleado.complete_name.upper())+' Telf: '+ustr(empleado.mobile_phone)
                    else:
                        res['manager']=ustr(empleado.complete_name.upper())+' Telf: -- '
        return res
        
report_sxw.report_sxw('report.Salvoconducto', 'movilization.order', 'gt_vehicle/report/salvoconducto1.rml', parser=salvoconducto1, header=False)

class salvoconducto2(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(salvoconducto2, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                        'concat_name':self.concat_name,
                        'director_name':self.director_name,
                })
    def concat_name(self, rutas): #members_name
        ruta=""            
        for line in rutas:
            ruta+= ustr(line.desde)+"-"+ustr(line.hasta)+", "               
        ruta=ruta[:-2]            
        return ruta
    
    def director_name(self): #members_name        
        res={}               
        depart_id = self.pool.get('hr.department').search(self.cr, self.uid, [('name','ilike','ADMINISTRACION Y LOGISTICA')])
        depart_id = self.pool.get('hr.department').browse(self.cr, self.uid,depart_id)[0]
        if depart_id:
            if depart_id.manager_id:
                res['director']=ustr(depart_id.manager_id.complete_name.upper())+"\n"+ustr(depart_id.manager_id.job_id.name.upper())
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
                    if empleado.mobile_phone:                        
                        res['manager']=ustr(empleado.complete_name.upper())+' Telf: '+ustr(empleado.mobile_phone)
                    else:
                        res['manager']=ustr(empleado.complete_name.upper())+' Telf: -- '
        return res
        
        
report_sxw.report_sxw('report.SalvoconductoAsignado', 'movilization.order', 'gt_vehicle/report/salvoconducto2.rml', parser=salvoconducto1, header=False)

