#-*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2010 SIA "KN dati". (http://kndati.lv) All Rights Reserved.
#                    General contacts <info@kndati.lv>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from tools import ustr
from report import report_sxw
from report.report_sxw import rml_parse
import time
import datetime
from datetime import datetime
from datetime import timedelta
import sys


class Parser(report_sxw.rml_parse):
    '''
    Procesos para mostrar datos
    '''   
    def cell(self,i,value):	
        self.tiempo_trabajado = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        l=''
        aux_= len(self.Date_marcs_id)    
        if value=="employee":  
            l=self.Employee[i]            
        if value=="sum_time":                     
            try:
                aux=str(self.aux_time[i*aux_][0]) + ':' + str(self.aux_time[i*aux_][1]) + ':' + str(self.aux_time[i*aux_][2])
                l=aux
            except:
                pass
        if value=="sum_time_delay":  
            try:
                aux=str(self.aux_time_delay[i*aux_][3]) + ':' + str(self.aux_time_delay[i*aux_][4]) + ':' + str(self.aux_time_delay[i*aux_][5])
                l=aux
            except:
                pass
        if value=="sum_time_extra":
            try: 
                aux=str(self.aux_time_extra[i*aux_][6]) + ':' +str(self.aux_time_extra[i*aux_][7]) + ':' +str(self.aux_time_extra[i*aux_][8])
                l=aux
            except:
                pass
        if value=="sum_time_real":
            print '**********************'
            print self.aux_time_real
            print self.aux_time_real[i*aux_][9]
            try: 
                aux=str(self.aux_time_real[i*aux_][9]) + ':' +str(self.aux_time_real[i*aux_][10]) + ':' +str(self.aux_time_real[i*aux_][11])
                print aux
                l=aux
            except:
                pass
	return l 
    
    def sumar_tiempo(self,detalle_tiempo,tipo):
        hora_resumen = detalle_tiempo.split(':')
        try:
            k=0
            if tipo=='trab':
                k=0
            if tipo=='delay':
                    k=3
            if tipo=='extra':
                    k=6        
            if tipo=='real':
                k=9                
            self.tiempo_trabajado[k+0] = self.tiempo_trabajado[k+0] + int(hora_resumen[0])
            self.tiempo_trabajado[k+1] = self.tiempo_trabajado[k+1] + int(hora_resumen[1])
            self.tiempo_trabajado[k+2] = self.tiempo_trabajado[k+2] + int(hora_resumen[2])
            while self.tiempo_trabajado[k+2]>=60:
                self.tiempo_trabajado[k+1] = self.tiempo_trabajado[k+1] + 1
                self.tiempo_trabajado[k+2] = self.tiempo_trabajado[k+2] - 60
            while self.tiempo_trabajado[k+1]>=60:
                self.tiempo_trabajado[k+0] = self.tiempo_trabajado[k+0] + 1
                self.tiempo_trabajado[k+1] = self.tiempo_trabajado[k+1] - 60
        except:
            pass                
        return self.tiempo_trabajado
        
        
    def cell_date(self,i,value):
        aux=l=aux_='' 
        suma=''    
        
        if value=="date_marcs":  
            try:
                l=self.Date_marcs[i]
            except:
                pass
        if value=="dia":            
            try:  
                l=self.Date_marcs[i]            
                h_regist = datetime.strptime(str(self.Date_marcs[i]), "%Y-%m-%d")
                aux=ustr(h_regist.strftime("%A"))
            except:
                pass
            l = aux[:2]       
        if value=="trab": 
            obj_trab = self.pool.get('assistance.resumen.diario.line').search(self.cr, self.uid, [('resumen_diario_id','=', self.Date_marcs_id[i]),
                                                                                                      ('name','=', 'trabajado')])                              
            for each_employee in self.pool.get('assistance.resumen.diario.line').browse(self.cr,self.uid,obj_trab,context= None):                               
                aux_= each_employee.tiempo    
                try:
                    suma=self.sumar_tiempo(each_employee.tiempo,'trab')
                except:
                    pass       
            self.aux_time.append(suma)            
            l = aux_                               
        if value=="fal": 
            obj_trab = self.pool.get('assistance.resumen.diario.line').search(self.cr, self.uid, [('resumen_diario_id','=', self.Date_marcs_id[i]),
                                                                                                      ('name','=', 'atraso')])
            aux_time_delay=[]
            for each_employee in self.pool.get('assistance.resumen.diario.line').browse(self.cr,self.uid,obj_trab,context= None):
                l= each_employee.tiempo
                try:
                    suma=self.sumar_tiempo(each_employee.tiempo,'delay')
                except:
                    pass   
                self.aux_time_delay.append(suma)                     
        if value=="add":  
            obj_trab = self.pool.get('assistance.resumen.diario.line').search(self.cr, self.uid, [('resumen_diario_id','=', self.Date_marcs_id[i]),
                                                                                                  ('name','=', 'hextra')])
            aux_time_extra=[]
            for each_employee in self.pool.get('assistance.resumen.diario.line').browse(self.cr,self.uid,obj_trab,context= None):
                l= each_employee.tiempo
                try:
                    suma =self.sumar_tiempo(each_employee.tiempo,'extra')
                except:
                    pass
            self.aux_time_extra.append(suma)  
        if value=="real": 
            obj_trab = self.pool.get('assistance.resumen.diario.line').search(self.cr, self.uid, [('resumen_diario_id','=', self.Date_marcs_id[i]),
                                                                                                      ('name','=', 'hreal')])                             
            for each_employee in self.pool.get('assistance.resumen.diario.line').browse(self.cr,self.uid,obj_trab,context= None):                               
                aux_= each_employee.tiempo    
                try:
                    suma=self.sumar_tiempo(each_employee.tiempo,'real')
                except:
                    pass       
            self.aux_time_real.append(suma) 
            l = aux_                                
        if value=="action": 
            try:
                if not self.acciones[str(self.Date_marcs[i][0])]:
                    l=self.Date_marcs[i][0]
                else:
                    l=self.acciones[str(self.Date_marcs[i][0])]
            except:
                pass                                                  
        if value=="action_type":
            try:  
                if not self.tipo_acciones[str(self.Date_marcs[i][1])]:
                    l=self.Date_marcs[i][1]
                else:
                    l= self.tipo_acciones[str(self.Date_marcs[i][1])]
            except:
                pass
        if value=="date_dbo":  
            l=self.Date_marcs[i][2]
        if value=="date_spetial":  
            l=self.Date_marcs[i][3]           
        if value=="gt_employee_id":  
            l=self.Date_marcs[i][4]
        if value=="address":  
            l=self.Date_marcs[i][5]
        if value=="mins_delay":
            try:
                if not self.Date_marcs[i][6]:
                    l=''
                else:
                    l=self.Date_marcs[i][6]
            except:
                pass
        if value=="state":
            try: 
                if not self.estados[str(self.Date_marcs[i][7])]:
                    l=self.Date_marcs[i][7]
                else:
                    l=self.estados[str(self.Date_marcs[i][7])]
            except:
                pass
        if value=="hour_reference":  
            l=self.Date_marcs[i][8]
        if value=="assent_type_id":  
            l=self.Date_marcs[i][9]            
	if not l:
		return ''
	else:
	        return l    
    
    def cell_hour(self,i,value):
	l=""
        if value=="hour_marcs":  
            l=self.Hour_marcs[i]
        return l    
      
   
    def employee(self,o):
        num_student=0
        for each_employee in o:
            self.Resume_id.append(each_employee.id)          
#        obj_notes = self.pool.get('assistance.resumen.diario').search(self.cr, self.uid, [('name','=', o.name.id)])
#        for each_employee in self.pool.get('assistance.resumen.diario').browse(self.cr,self.uid,obj_notes,context= None):                       
            if not each_employee.name.id in self.Employee_id:
                name_employee=''
                try:
                    name_employee = name_employee + ' ' + ustr(each_employee.name.name) 
                except:
                    pass
                try:
                    if each_employee.name.name1: 
                        name_employee =  name_employee +' ' +  ustr(each_employee.name.name1) 
                except:
                    pass
                try:
                    name_employee =  name_employee +' ' +  ustr(each_employee.name.last_name) 
                except:
                    pass
                try:
                    if each_employee.name.last_name1:
                        name_employee =  name_employee +' ' + ustr(each_employee.name.last_name1) 
                except:
                    pass                    
                self.Employee.append(name_employee)
                self.Employee_id.append(each_employee.name.id)               
                num_student=num_student+1
        self.Date_marcs=[]
        self.Date_marcs_id =[]
        return num_student
             
    def marcs_(self,i): 
        self.tiempo_trabajado = [0,0,0,0,0,0,0,0,0,0,0,0]
        num_attendance=0
        self.Date_marcs=[]
        self.Date_marcs_id =[]
        obj_notes = self.pool.get('assistance.resumen.diario').search(self.cr, self.uid, [('id','in',self.Resume_id),
                                                                                          ('name','=', int(self.Employee_id[i]))],order='date')
        
        for each_attendance in self.pool.get('assistance.resumen.diario').browse(self.cr,self.uid,obj_notes,context= None):                       
            self.Date_marcs.append(each_attendance.date)
            self.Date_marcs_id.append(each_attendance.id)
            num_attendance=num_attendance+1                     
        return num_attendance 
        
    def marcs_detail(self,i,j):                
        num_attendance=0
        self.Hour_marcs=[]
        obj_notes = self.pool.get('hr.attendance').search(self.cr, self.uid, [('resumen_diario_id','=', int(self.Date_marcs_id[j])),
                                                                              '|',('action','!=', 'action'),
                                                                              ('action_type','=', 'inconsistency'),
                                                                              ], order='date_spetial') 
        for each_attendance in self.pool.get('hr.attendance').browse(self.cr,self.uid,obj_notes,context= None):                   
            h_regist = datetime.strptime(str(each_attendance.date_spetial), "%Y-%m-%d %H:%M:%S")
            h_regist= + timedelta(hours=-5) + h_regist
            self.Hour_marcs.append(h_regist.strftime("%H:%M:%S"))
            num_attendance=num_attendance+1        
        return num_attendance
               
    def attendance(self,o):
        num_student=0
        for each_attendance in o:
            self.Resume_id.append(each_attendance.id)                                 
            if not each_attendance.employee_id.id in self.Employee_id:
                name_employee=''
                try:
                    name_employee = name_employee +  ustr(each_attendance.employee_id.name) 
                except:
                    pass
                try:
                    if each_attendance.employee_id.name1:
                        name_employee =  name_employee +' '+  ustr(each_attendance.employee_id.name1) 
                except:
                    pass
                try:
                    name_employee =  name_employee + ' '+ ustr(each_attendance.employee_id.last_name) 
                except:
                    pass
                try:
                    if each_attendance.employee_id.last_name1:
                        name_employee =  name_employee +' '+  ustr(each_attendance.employee_id.last_name1) 
                except:
                    pass
                self.Employee.append(name_employee)
                self.Employee_id.append(each_attendance.employee_id.id)               
                num_student=num_student+1
        return num_student
    def assent_(self,i): 
        num_attendance=0
        self.Date_marcs=[]
        self.Date_marcs_id =[]
        obj_notes = self.pool.get('hr.attendance').search(self.cr, self.uid, [('id','in',self.Resume_id),
                                                                                          ('employee_id','=', int(self.Employee_id[i]))],order='date_spetial')
        for each_attendance in self.pool.get('hr.attendance').browse(self.cr,self.uid,obj_notes,context= None):         
            self.Date_marcs.append([each_attendance.action,
                                    each_attendance.action_type,
                                    each_attendance.date_dbo,
                                    each_attendance.date_spetial,
                                    each_attendance.gt_employee_id.name,
                                    each_attendance.address,
                                    each_attendance.mins_delay,
                                    each_attendance.state,
                                    each_attendance.hour_reference,
                                    each_attendance.assent_type_id.name, ])
            num_attendance=num_attendance+1                   
        return num_attendance

    def marcacion(self,i):     
	aux=''
        k=i+2
        j=k/2        
        l=i+1
        if l%2==0:
            aux ='Sal ' + str(int(j))
        else:    
            aux ='Ent ' + str(int(j))
        return aux
               
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({                    
	    'marcacion':self.marcacion,
            'employee':self.employee,         
            'cell':self.cell,
            'cell_date':self.cell_date,
            'marcs_detail':self.marcs_detail,
            'cell_hour':self.cell_hour,            
            'marcs_':self.marcs_,
            'attendance': self.attendance,
            'assent_':self.assent_,
            'sumar_tiempo':self.sumar_tiempo,
        })
        self.aux_time= []
        self.aux_time_delay=[]
        self.aux_time_real=[]
        self.aux_time_extra=[]
        self.tiempo_trabajado = [0,0,0,0,0,0,0,0,0,0,0,0]
        self.Employee=[]
        self.sum_time=[]
        self.Employee_id=[]
        self.Date_marcs=[]
        self.Hour_marcs=[]
        self.Date_marcs_id =[]
        self.Resume_id =[]
        self.estados = {'draft':'Borrador',
                   'open':'Confirmado',
                   'cancel':'Cancelado',
                   'close':'Cerrado',
                  }
        self.acciones = {'sign_in': 'Ingreso',
                  'sign_out': 'Salida' ,
                  'action': 'Evento',
                  }
        self.tipo_acciones ={'marc':'Marcacion',
                        'delay':'Atraso',
                        'before':'Salida antes',
                        'assent':'Sancion',
                        'notification':'Notificacion',
                        'notice':'Aviso',
                        'inconsistency':'Inconsistencia',
                        'invalid':'Invalido',
                        'excuse':'Valido'}     
  

