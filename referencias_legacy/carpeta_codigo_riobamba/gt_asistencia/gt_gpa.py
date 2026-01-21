# -*- coding: utf-8 -*-
##############################################################################
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
from tools import ustr
import time
from osv import fields, osv
from tools.translate import _
from datetime import datetime
from datetime import timedelta
from time import gmtime, localtime


class gt_assent_type(osv.osv):
    '''
    Tipo de Sancion -- Assent type
    '''
    _description = 'Tipo de Sancion' 
    _name = 'gt.assent.type'  
    _columns = {'name': fields.char('Tipo de Sancion', size=64, required=True),
                'code': fields.char('Prioridad', size=32, required=True),
                'next_assent_id': fields.many2one('gt.assent.type','Sancion siguiente', size= 64),
                'notification_type': fields.many2one('gt.report.type','Notificación', size= 32),
                'number_max': fields.integer('Número máximo de sanciones', size=32),                
                'min_assent': fields.boolean('Es sanción mínima'),
                'max_assent': fields.boolean('Sancion Máxima'),
                'notification': fields.boolean('Requiere Notificación'),                
                'max_anual': fields.boolean('Máximo minutos anuales'),
                'max_month': fields.boolean('Máximo minutos mensuales'),               
                'minutes_max_anual': fields.integer('Número máximo minutos anuales', size=32),
                'minutes_max_month': fields.integer('Número máximo minutos mensuales', size=32),
                }
    _order='code asc'
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro')
        return False      
gt_assent_type()


class gt_report_type(osv.osv):
    '''
    Tipo de Notificacion
    '''
    _description = 'Tipo de Notificación o reporte' 
    _name = 'gt.report.type'  
    _columns = {'name': fields.char('Nombre de Notificación', size=64, required=True),
                'employee_id' : fields.many2one('hr.employee','Empleado'),
                'head': fields.char('Cabecera', size=256, ),
                'body_1': fields.text('Cuerpo', readonly=True),
                'body_2': fields.text('Cuerpo',),
                'body_3': fields.text('Contenido de Sancion'),
                'body_4': fields.char('Sancion Generada', size=256, ),
                'closure': fields.char('Cierre',size=256),
                } 
    _defaults = {        
        'body_1': 'head = ' + str(time.strftime('%A,%d de %B del %Y')) + str(' \nemployee_id = Nombre del Empleado\nemployee_ci=CI del empleado\ne_mail=Correo del empleado\nday_event = fecha de acontecimiento\nevent_causes = Causa\nassent_name = Nombre de Sancion generada' )                 
    }
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro')
        return False  
gt_report_type()

class gt_clock_name(osv.osv):
    '''
    Nombre para el reloj
    '''
    _description = 'Nombre para el reloj' 
    _name = 'gt.clock.name'  
    _columns = {'name': fields.char('Reloj', size=128, required=True),
                'ip' : fields.char('IP',size=16, required=True),
                } 
    _defaults = {        
        'name': ''                  
    }
    def _clock_get(obj, cr, uid,ip, context=None):
        ids = obj.pool.get('gt.clock.name').search(cr, uid, [('ip', '=', ip)], context=context)   
        if ids:
            for obj_reloj in obj.browse(cr, uid, ids, context):
                return obj_reloj.name
        else:
            return ip
        #return ids and ids[0] or False
    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro')
        return False  
gt_clock_name()


class gt_resource_calendar(osv.osv):
    '''
    Resource Calendar -HERENCIA RESOURCE - AGREGAR CAMPO 
    '''
    _description="Resource Calendar"
    _inherit = 'resource.calendar'
    _columns = {'schedule_half': fields.float('Hora de división de jornada', required=True)}     
gt_resource_calendar()


def _employee_get(obj, cr, uid, context=None):
    ids = obj.pool.get('res.users').search(cr, uid, [('id', '=', uid)], context=context)
    return ids and ids[0] or False


def get_activate(obj, cr, uid, context=None):
    days_add=0
    obj_configuration =  obj.pool.get('gt.field.workable').search(cr, uid, [], context=context)
    if obj_configuration:
        for obj_configuration in obj.pool.get('gt.field.workable').browse(cr, uid, obj_configuration, context):
            days_add=int(obj_configuration.name)    
    return datetime.today()+timedelta(days=  days_add)


def verify_marc_day(self, cr, uid, emp_id, h_regist, context=None):
        '''
        Verifica el numero de marcaciones del dia'
        ''' 
        mac_number=0
        semana = {'lunes':0 , 'monday': 0, 'Monday': 0,
                      'martes':1 , 'tuesday': 1, 'Tuesday': 1, 
                      'miércoles':2 , 'wednesday': 2, 'miercoles':2, 'Wednesday': 2,
                      'jueves':3 , 'thursday': 3,  'Thursday': 3,
                      'viernes':4 , 'friday': 4,  'Friday': 4,
                      'sabado':5 , 'saturday': 5, 'sábado':5,  'Saturday':5,
                      'domingo':6 , 'sunday': 6, 'sunday': 6}
        
        h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")
        employee_ids= self.pool.get('hr.employee').search(cr, uid, [('id',"=", emp_id)])
        for obj_employee in self.pool.get('hr.employee').browse(cr, uid, employee_ids, context):
            str_hour = obj_employee.contract_id.work_id.schedule_half 
            if str_hour:
                dec= (30*(int((str_hour-int(str_hour))*100)))/50
                med_day = time.strftime('%H:%M:%S', time.strptime(str(int(str_hour)) + ':' + str(dec), '%H:%M'))
                calendar_ids = self.pool.get('resource.calendar.attendance').search(cr, uid, [('dayofweek', '=', ustr(semana[h_regist.strftime("%A")])),
                                                                                          ('calendar_id','=',obj_employee.contract_id.work_id.id),
                                                                                          ], context=context) 
            mac_number = int(len(calendar_ids))*2       
        return mac_number


def verify_marcs_day(self, cr, uid, emp_id, h_regist, context=None):
        '''
        Verifica el numero de marcaciones exactas para el empleado
        para determinado dia
        '''
        semana = {'lunes':0 , 'monday': 0, 'Monday': 0,
                      'martes':1 , 'tuesday': 1, 'Tuesday': 1, 
                      'miércoles':2 , 'wednesday': 2, 'miercoles':2, 'Wednesday': 2,
                      'jueves':3 , 'thursday': 3,  'Thursday': 3,
                      'viernes':4 , 'friday': 4,  'Friday': 4,
                      'sabado':5 , 'saturday': 5, 'sábado':5,  'Saturday':5,
                      'domingo':6 , 'sunday': 6, 'sunday': 6}
        marcs_number = add = 0
        marcs = same = False  
        permission_today=''   
        h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")
        date = h_regist.strftime("%Y-%m-%d")
        only_date= datetime.strptime(str(date), "%Y-%m-%d")                
        time_eval= + timedelta(days=0) + only_date
        h_from= datetime.strptime(str(time_eval), "%Y-%m-%d %H:%M:%S")
        time_eval= + timedelta(days=1) + only_date        
        h_to= datetime.strptime(str(time_eval), "%Y-%m-%d %H:%M:%S")
        employee_ids= self.pool.get('hr.employee').search(cr, uid, [('id',"=", emp_id)])
        for obj_employee in self.pool.get('hr.employee').browse(cr, uid, employee_ids, context):
            str_hour = obj_employee.contract_id.work_id.schedule_half
            if str_hour: 
                dec= (30*(int((str_hour-int(str_hour))*100)))/50
                med_day = time.strftime('%H:%M:%S', time.strptime(str(int(str_hour)) + ':' + str(dec) + ':00', '%H:%M:%S'))
                calendar_ids = self.pool.get('resource.calendar.attendance').search(cr, uid, [('dayofweek', '=', int(semana[h_regist.strftime("%A")])),
                                                                                  ('calendar_id','=',obj_employee.contract_id.work_id.id),
                                                                                  ], context=context)
                suppose_mars= int(len(calendar_ids))
                permission_today= self.pool.get('hr.holidays').search(cr, uid, [('employee_id', '=', emp_id),
                                                                      ('state', '=', 'validate'),
                                                                      ('date_from', '>', h_from.strftime("%Y-%m-%d %H:%M:%S")),
                                                                      ('date_to', '<', h_to.strftime("%Y-%m-%d %H:%M:%S")),
                                                                      ], context=context)
            if permission_today:                
                for obj_permission in self.pool.get('hr.holidays').browse(cr, uid, permission_today, context):
                    permission_start=h_regist = datetime.strptime(str(obj_permission.date_from), "%Y-%m-%d %H:%M:%S")                     
                    permision_end=datetime.strptime(str(obj_permission.date_to), "%Y-%m-%d %H:%M:%S")
                    perm_start = permission_start.strftime("%H:%M:%S")
                    perm_end = permision_end.strftime("%H:%M:%S")
                    hours_to_compare = get_in_out(self, cr, uid, [], [emp_id], semana, perm_start, int(semana[h_regist.strftime("%A")]))
                    starf_h =hours_to_compare[1]
                    end_h= hours_to_compare[2]
                    if perm_start <= starf_h and perm_end < end_h:
                        add=0      
                        same=True                                       
                    else:
                        if perm_start <= starf_h and perm_end >= end_h:
                            #print 'Inicia antes y termina despues de fin'
                            if suppose_mars==1:
                                marcs=False
                            else:          
                                if perm_end <= med_day and perm_start <= med_day:
                                    add=-2 
                                else:
                                    if perm_start > med_day and perm_end > med_day:
                                        add=-2 
                                    else:
                                        hours_end_compare = get_in_out(self, cr, uid, [], [emp_id], semana, perm_end, int(semana[h_regist.strftime("%A")]))
                                        if perm_start <= starf_h and perm_end >= hours_end_compare[2] :
                                            marcs=False
                                        else:
                                            if perm_start <= starf_h and perm_end < hours_end_compare[2] :
                                                add=-2                                                                                                                                           
                        else:
                            if perm_start > starf_h and perm_end < end_h:
                                add=2
                                #print 'Inicia despues y termina antes'
                            else:
                                if perm_start > starf_h and perm_end >= end_h:
                                    if suppose_mars==1:
                                        same=True
                                    if perm_end < med_day:
                                        same=True                                        
                                    else:
                                        hours_end_compare = get_in_out(self, cr, uid, [], [emp_id], semana, perm_end, int(semana[h_regist.strftime("%A")]))
                                        if perm_end < hours_end_compare[2] : 
                                            same=True
                                        else:
                                            add=-2
            else:            
                no_marc= self.pool.get('hr.holidays').search(cr, uid, [('employee_id', '=', emp_id),
                                                                          ('state', '=', 'validate'),
                                                                          ('date_from', '<', h_from.strftime("%Y-%m-%d %H:%M:%S")),
                                                                          ('date_to', '>', h_to.strftime("%Y-%m-%d %H:%M:%S")),
                                                                          ], context=context)
                if no_marc:
                    result= 'False'
                else:
                    permission_start= self.pool.get('hr.holidays').search(cr, uid, [('employee_id', '=', emp_id),
                                                                      ('state', '=', 'validate'),
                                                                      ('date_from', '>=', h_from.strftime("%Y-%m-%d %H:%M:%S")),
                                                                      ('date_from', '<=', h_to.strftime("%Y-%m-%d %H:%M:%S")),
                                                                      ('date_to', '>', h_to.strftime("%Y-%m-%d %H:%M:%S")),
                                                                      ], context=context)
                    
                    if permission_start:
                        for obj_permission in self.pool.get('hr.holidays').browse(cr, uid, permission_start, context):
                            permission_start=h_regist = datetime.strptime(str(obj_permission.date_from), "%Y-%m-%d %H:%M:%S")                                                
                            perm_start = permission_start.strftime("%H:%M:%S")
                            permision_end=datetime.strptime(str(obj_permission.date_to), "%Y-%m-%d %H:%M:%S")
                            perm_end = permision_end.strftime("%H:%M:%S")
                            hours_to_compare = get_in_out(self, cr, uid, [], [emp_id], semana, perm_start, int(semana[h_regist.strftime("%A")]))
                            starf_h =hours_to_compare[1]    
                            end_h= hours_to_compare[2]                           
                            if perm_start <= starf_h:
                                if suppose_mars==1:
                                    marcs= 'False'
                                else:
                                    if perm_start < med_day:                                                                       
                                        exact=0
                                        marcs= 'False'
                                    else:
                                        if perm_start > med_day:
                                            add=-2                               
                            else:
                                if perm_start > starf_h and  perm_start <= end_h:
                                    if suppose_mars==1:
                                        same=True
                                    else:                                        
                                        if perm_start < med_day:
                                            add=-2                                         
                                        else:
                                            same=True
                                else:
                                    if perm_start >= end_h:
                                        if suppose_mars==1:
                                            add=-2 
                                        else:                                        
                                            if perm_start < med_day:
                                                add=-2                                            
                                            else: 
                                                same=True                                                                                                          
                    else:
                        permission_end= self.pool.get('hr.holidays').search(cr, uid, [('employee_id', '=', emp_id),
                                                                                      ('state', '=', 'validate'),
                                                                                      ('date_from', '<', h_from.strftime("%Y-%m-%d %H:%M:%S")),
                                                                                      ('date_to', '>=', h_from.strftime("%Y-%m-%d %H:%M:%S")),
                                                                                      ('date_to', '<=', h_to.strftime("%Y-%m-%d %H:%M:%S")),
                                                                                      ], context=context)
                        if permission_end:
                            for obj_permission in self.pool.get('hr.holidays').browse(cr, uid, permission_end, context):
                                permision_end=datetime.strptime(str(obj_permission.date_to), "%Y-%m-%d %H:%M:%S")
                                perm_end = permision_end.strftime("%H:%M:%S")
                                hours_to_compare = get_in_out(self, cr, uid, [], [emp_id], semana, perm_end, int(semana[h_regist.strftime("%A")]))
                                starf_h =hours_to_compare[1]    
                                end_h= hours_to_compare[2]                           
                                if perm_end <= starf_h:                               
                                    if suppose_mars==1:
                                        same=True                                       
                                    else:
                                        if perm_end < med_day:                                                                       
                                           same=True                                      
                                        else:
                                            add=-2                                                                                                                          
                                else:
                                    if perm_end > starf_h and  perm_end < end_h:
                                        if suppose_mars==1:
                                            same=True
                                        else:                                        
                                            if perm_end < med_day:
                                                same=True                                          
                                            else:
                                                add=-2 
                                    else:
                                        if perm_end >= end_h:
                                            #print 'termina despues de salida'
                                            if suppose_mars==1:
                                                marcs=False  
                                            else:                                        
                                                if perm_end < med_day:
                                                    add=-2                                           
                                                else:
                                                    exact=0
                                                    marcs=False                                                                                                                                              
        if marcs:
            result=False
        else:
            if same:
                result='same'
            else:
                result=add
        return result
                                                                           
                    
class resumen_diario_line(osv.osv):
    _name = 'assistance.resumen.diario.line'
    _columns = {
                'name': fields.selection([('atraso','Tiempo atraso'),
                                          ('trabajado','Tiempo Total'),
                                          ('hnormal','Bajo Horario'),
                                          ('hreal','Horas Reales'),
                                          ('hextra','Tiempo adicional Laborado')], 'Tipo'),
                'employee_id': fields.many2one('hr.employee', 'Empleado', required=True),
                'fecha': fields.date('Fecha'),
                'tiempo': fields.time('Tiempo'),
                'resumen_diario_id': fields.many2one('assistance.resumen.diario', 'Resumen Diario'),
                }
    _order='name DESC'  
    _defaults = {
        'tiempo':'00',        
    }
    

resumen_diario_line()


class resumen_diario(osv.osv):
    _name = 'assistance.resumen.diario'
    _columns = {
                'name': fields.many2one('hr.employee', 'Empleado'),
                'date': fields.date('Fecha'),
                'marcaciones_ids': fields.one2many('hr.attendance', 'resumen_diario_id', 'Marcaciones del dia'),
                'detalle_ids': fields.one2many('assistance.resumen.diario.line', 'resumen_diario_id', 'Detalle del dia'),
                }
    def unlink(self, cr, uid, ids, context=None):
        summary = self.read(cr, uid, ids, [], context=context)
        unlink_ids = []
        
        raise osv.except_osv(_('Error!'), _('No se puede eliminar un resumen de marcaciones'))
       # for s in summary:
       #     as_summary = self.pool.get('assistance.resumen.diario.line')
       #     summary_line= as_summary.search(cr, uid, [('resumen_diario_id','=', s['id'])])                   
       #     unlink_ids.append(s['id'])
       #     self.pool.get('assistance.resumen.diario.line').unlink(cr, uid, summary_line)
        #return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)               
                
    def _compute_day(self, cr, uid, marcs, context=None,):
        resultado={'atraso':0,
                   'trabajado':timedelta(hours=0),
                   'hextra':timedelta(hours=0)}
        time_work=0
        marcs_ = []
        for marc in marcs:
            attendance_id =  self.pool.get('hr.attendance').search(cr, uid, [('id', '=', int(marc))], context=context)
            for obj_attendance in self.pool.get('hr.attendance').browse(cr, uid, attendance_id, context):
                marcs_.append(obj_attendance)
        sum_day=timedelta(hours=0)
        for register_in in marcs_:       
            resultado['atraso'] = resultado['atraso'] + register_in.mins_delay 
            total_time=timedelta(hours=0) 
            if register_in.action == 'sign_in':
                h_regist_in = datetime.strptime(str(register_in.date_spetial), "%Y-%m-%d %H:%M:%S")                
                #h_in= + timedelta(hours=-5) + h_regist_in
                h_in=  h_regist_in
                for register_out in marcs_:
                    if register_out.action == 'sign_out':
                         h_regist_out = datetime.strptime(str(register_out.date_spetial), "%Y-%m-%d %H:%M:%S")
                         #h_out= + timedelta(hours=-5) + h_regist_out 
                         h_out= h_regist_out
                         time_work = h_out - h_in                       
                         if time_work > timedelta(hours=0):                         
                              if total_time == timedelta(hours=0):
                                  total_time=time_work
                              else:
                                  if time_work<total_time:
                                      total_time=time_work                
                sum_day=sum_day+total_time  
                resultado['trabajado'] = sum_day
        return resultado
    
    def number_hour(self, cr, uid, id_emp,semana, day_code, context= None):  
        exist_schedule=False 
        calendar_ids=''
        basic_time =timedelta(hours=0)
        id_emp = self.pool.get('hr.employee').search(cr, uid, [('id', '=', id_emp),], context=context)    
        for obj_employee in self.pool.get('hr.employee').browse(cr, uid, id_emp, context):
            calendar_ids = self.pool.get('resource.calendar.attendance').search(cr, uid, [('dayofweek', '=', ustr(day_code) ),
                                                                                          ('calendar_id','=',obj_employee.contract_id.work_id.id),
                                                                                          ], context=context)
        if calendar_ids:
            for obj_calendar in self.pool.get('resource.calendar.attendance').browse(cr, uid, calendar_ids, context):
                basic_time= basic_time + (timedelta(hours=obj_calendar.hour_to) - timedelta(hours=obj_calendar.hour_from))                        
        return basic_time
    def recalcular(self, cr, uid,ids, context=None): 
        for obj in self.browse(cr, uid, ids, context):
            employee=obj.name.id
            end_=datetime.strptime(str(obj.date), "%Y-%m-%d")
            end=end_.strftime("%Y-%m-%d")
            start= str(datetime.strptime(str(timedelta(days=-1) + datetime.strptime(str(end), "%Y-%m-%d")), "%Y-%m-%d %H:%M:%S"))
            start = datetime.strptime(str(start), "%Y-%m-%d %H:%M:%S")
            start_ = start.strftime("%Y-%m-%d")
            marc_ids= self.pool.get('hr.attendance').search(cr, uid, [('resumen_diario_id','=',obj.id),
                                                                      ('action','!=','action'),])
            #for obj_marcacion in self.pool.get('hr.attendance').browse(cr, uid, marc_ids, context):
            #    print obj_marcacion.date_spetial
            resumen_line =self.pool.get('assistance.resumen.diario.line').search(cr, uid, [('resumen_diario_id','=',obj.id),])
            self.pool.get('assistance.resumen.diario.line').unlink(cr, uid, resumen_line)
            self._create_resumen(cr,uid,employee, end_, marc_ids,context)
           # print marc_ids
            

    def _create_resumen(self,cr,uid,employee_id,date,marcs,context):
        semana = {'lunes':0 , 'monday': 0, 'Monday': 0,
                      'martes':1 , 'tuesday': 1, 'Tuesday': 1, 
                      'miércoles':2 , 'wednesday': 2, 'miercoles':2, 'Wednesday': 2,
                      'jueves':3 , 'thursday': 3,  'Thursday': 3,
                      'viernes':4 , 'friday': 4,  'Friday': 4,
                      'sabado':5 , 'saturday': 5, 'sábado':5,  'Saturday':5,
                      'domingo':6 , 'sunday': 6, 'sunday': 6}
        ind_dia = int(semana[date.strftime("%A")])
        hours_norm = self.number_hour(cr, uid, employee_id,semana,ind_dia)
        ids_resumen=self.search(cr, uid, [('name','=',employee_id),
                                          ('date','=',date)])
        if not(ids_resumen):
            id_resumen = self.create(cr,uid,{'name':employee_id,'date':date,})
            self.pool.get('hr.attendance').write(cr,uid,marcs,{'resumen_diario_id':id_resumen})                                      
        else:
            obj_detalle = self.pool.get('assistance.resumen.diario.line')
            for id_resumen in ids_resumen:
                #self.pool.get('hr.attendance').write(cr,uid,marcs,{'resumen_diario_id':id_resumen})
                ids_detalles = obj_detalle.search(cr, uid, [('resumen_diario_id','=', id_resumen)])
                obj_detalle.unlink(cr, uid, ids_detalles)                            
                resultado = self._compute_day(cr,uid,marcs,context)
                self.pool.get('assistance.resumen.diario.line').create(cr, uid, {'name': 'hnormal',
                                                                                 'employee_id': employee_id,
                                                                                 'fecha': date,
                                                                                 'tiempo': hours_norm,
                                                                                 'resumen_diario_id': id_resumen,
                                                                                    })
                self.pool.get('assistance.resumen.diario.line').create(cr, uid, {'name': 'trabajado',
                                                                                 'employee_id': employee_id,
                                                                                 'fecha': date,
                                                                                 'tiempo': resultado['trabajado'],
                                                                                 'resumen_diario_id': id_resumen,
                                                                                    })
                if resultado['trabajado'] <=timedelta(hours=0):
                    tiempo_real=resultado['trabajado']

                else:
                    tiempo_real=hours_norm-(timedelta(minutes=int(resultado['atraso'])))
                    if tiempo_real <=timedelta(hours=0):
                        tiempo_real =timedelta(hours=0)
                self.pool.get('assistance.resumen.diario.line').create(cr, uid, {'name': 'hreal',
                                                                                 'employee_id': employee_id,
                                                                                 'fecha': date,
                                                                                 'tiempo': tiempo_real,
                                                                                 'resumen_diario_id': id_resumen,
                                                                                    })
                self.pool.get('assistance.resumen.diario.line').create(cr, uid, {'name': 'atraso',
                                                                                 'employee_id': employee_id,
                                                                                 'fecha': date,
                                                                                 'tiempo': timedelta(minutes=int(resultado['atraso'])),
                                                                                 'resumen_diario_id': id_resumen,
                                                                                    })
                if resultado['trabajado'] > timedelta(hours=0) and resultado['trabajado']> hours_norm:
                    self.pool.get('assistance.resumen.diario.line').create(cr, uid, {'name': 'hextra',
                                                                                     'employee_id': employee_id,
                                                                                     'fecha': date,
                                                                                     'tiempo': (resultado['trabajado']-hours_norm),
                                                                                     'resumen_diario_id': id_resumen,
                                                                                        })
            
    def iniciar_detalles(self):
        obj_attendance = self.pool.get('hr.attendance')
        for resumen in self.browse(cr, uid, ids, context):
            pass
        ids_attendance = obj_attendance.search(cr, uid, [('date_spetial', '=', resumen.date),
                                                         ('date_spetial', '=', resumen.date)])
        pass            
resumen_diario()                     

        
class academic_hr_attendance_inherit(osv.osv):
    '''
    #==========> HERENCIA ATTENDANCE - AGREGAR CAMPO 
    '''
    _inherit = "hr.attendance"
    _order = 'date_spetial DESC'
    _columns = {'history_id' : fields.many2one('gt.history','Historial'),
                'action_type': fields.selection([('marc', 'Marcacion'),('delay', 'Atraso'),
                                                 ('before', 'Salida antes'), ('assent', 'Sancion'),
                                                 ('notification', 'Notificacion'),
                                                 ('notice', 'Aviso'),
                                                 ('inconsistency', 'Inconsistencia'),
                                                 ('invalid', 'Invalido'),
                                                 ('excuse', 'Valido'),
                                                 ],'Razon Accion',
                                                required=True),
                
                'assent_type_id': fields.many2one('gt.assent.type','Sancion', size= 64),
                'attendance_id': fields.many2one('hr.attendance','Evento Relacionado', size= 64),               
                'gt_employee_id': fields.many2one('res.users','Empleado'), 
                'indicted': fields.boolean('Cuantificado', readonly=True),
                'not_normal': fields.boolean('Se cuantifica', readonly=True), 
                'notes': fields.char('Notas', size=528, readonly=True),
                'date_dbo': fields.char('Fecha DB', size=528),
                'date_spetial':fields.datetime('Fecha de accion'),     
                'body': fields.text('Correo', readonly=True),
                'address': fields.char('Reloj',size=128),
                #'address':fields.many2one('gt.clock.name','Reloj'),
                'mins_delay':fields.float('Minutos no laborados', size= 16, readonly=True),
                'hour_reference' : fields.char("Hora de Referencia", size=16, readonly=True),
                'state': fields.selection([('draft', 'Borrador'),
                       ('open', 'Confirmado'),
                       ('cancel', 'Cancelado'),
                       ('close', 'Cerrado'),
                      ],'Estado', required=True),
                'reason': fields.char('Motivo', size=528),
                'who_cancel': fields.many2one('res.users','Quien Cancela',readonly=True),
                #'who_cancel': fields.many2one('hr.employee', "Quien Cancela", readonly=True ),
                'history_cancel': fields.boolean('Cancelado en historial', readonly=True),
                'obs_cancel':fields.char('Observaciones al cancelar', size=128, readonly=True ),
                'resumen_diario_id': fields.many2one('assistance.resumen.diario','Resumen Diario'),
                }
    _defaults = {
        'action_type':'marc',
        'mins_delay':0,
        'state':'draft',
        'action':'sign_in',
        'indicted':False,
        'not_normal':False,
        'history_id':'',
        'notes':'',
        'date_dbo':'',
        'gt_employee_id': _employee_get,
        'who_cancel': _employee_get,
        'history_cancel':False,
        'date_spetial': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    def unlink(self, cr, uid, ids, context=None):
        summary = self.read(cr, uid, ids, [], context=context)
        unlink_ids = []
     #   for s in summary:
     #       as_summary = self.pool.get('assistance.resumen.diario')
     #       summary_line= as_summary.search(cr, uid, [('marcaciones_ids','=', s['id'])])                   
     #       if summary_line == []:                
     #           unlink_ids.append(s['id'])
     #       else:
           #raise osv.except_osv(_('Error!'), _('No puede eliminar marcaciones'))
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
     
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not len(ids):
            return []
        res = []
        for record in self.read(cr, uid, ids, ['user_id','name','action_type',], context=context):
            res.append((record['id'], record['name'] + ' '+ record['action_type']))
        return res
    
    def write(self, cr, uid, ids, values, context=None):
        semana = {'lunes':0 , 'monday': 0, 'Monday': 0,
                      'martes':1 , 'tuesday': 1, 'Tuesday': 1, 
                      'miércoles':2 , 'wednesday': 2, 'miercoles':2, 'Wednesday': 2,
                      'jueves':3 , 'thursday': 3,  'Thursday': 3,
                      'viernes':4 , 'friday': 4,  'Friday': 4,
                      'sabado':5 , 'saturday': 5, 'sábado':5,  'Saturday':5,
                      'domingo':6 , 'sunday': 6, 'sunday': 6}
        super(academic_hr_attendance_inherit, self).write(cr, uid, ids, values)
        for obj_attendance in self.browse(cr,uid,ids,context):                  
            if obj_attendance.action !='action' and obj_attendance.action_type=='marc' and  not obj_attendance.hour_reference:
                h_regist = datetime.strptime(str(obj_attendance.date_spetial), "%Y-%m-%d %H:%M:%S")                 
                #hour_regist = time.strftime('%H:%M:%S', time.strptime(str(int(h_regist.hour)-5) + ':' + str(int(h_regist.minute))+ ':' + str(int(h_regist.second)), '%H:%M:%S'))
                hour_regist = time.strftime('%H:%M:%S', time.strptime(str(int(h_regist.hour)) + ':' + str(int(h_regist.minute))+ ':' + str(int(h_regist.second)), '%H:%M:%S'))
                registro_accion = get_vals_action(self, cr, uid, values, context, obj_attendance.employee_id.id, h_regist,obj_attendance.id)
                hours_to_compare = get_in_out(self, cr, uid, values, [obj_attendance.employee_id.id], semana, hour_regist, int(semana[h_regist.strftime("%A")]) )#, id_emp, hour_regist,semana , context) 
                h_in =  hours_to_compare[1]
                h_out = hours_to_compare[2] 
                values['notes']=''
                values['action'] = registro_accion 
                values['date_dbo'] = obj_attendance.date_dbo
                if hours_to_compare[0]:
                    'entra a crear registros'
                    if (registro_accion == 'sign_in' and hour_regist <= h_in) or (registro_accion == 'sign_out'and hour_regist > h_out):                        
                        values['action_type'] = 'marc'
                        if registro_accion == 'sign_in': 
                            values['hour_reference']= h_in 
                            values['action'] = 'sign_in'  
                        else:  
                            values['hour_reference']= h_out
                            values['action'] = 'sign_out'                                   
                    else:                
                        if registro_accion == 'sign_in' and hour_regist > h_in:                            
                            values['hour_reference']= h_in 
                            absence = _verify_absence(self, cr, uid, obj_attendance.employee_id.id, 'sign_in', h_regist, registro_accion)
                            if absence[0]==False:                       
                                values = create_delay(self, cr, uid, values, context, obj_attendance.employee_id.id, hour_regist, h_in, obj_attendance.history_id.id, registro_accion)  
                                hour_regist                              
                            else:                               
                                values['action_type'] = 'marc'
                                values['notes'] = 'Permiso'    
                                values['hour_reference']= h_in                                                                                                                                                    
                        else:
                            if registro_accion== 'sign_out' and hour_regist < h_out:
                                values['hour_reference']= h_out 
                                absence = _verify_absence(self, cr, uid, obj_attendance.employee_id.id, 'sign_out', h_regist, registro_accion)                                
                                if absence[0]==False: 
                                    values = create_delay(self, cr, uid, values, context, obj_attendance.employee_id.id, hour_regist, h_out,  obj_attendance.history_id.id, registro_accion)                                                                    
                                else:
                                    values['hour_reference']= h_out
                                    values['action_type'] = 'marc' 
                                    values['notes'] = 'Permiso'
                                     
            super(academic_hr_attendance_inherit, self).write(cr, uid, ids, values, context=context)
            if obj_attendance.resumen_diario_id:
                obj_resumen = self.pool.get('assistance.resumen.diario')
                ids_marcaciones = self.search(cr, uid, [('resumen_diario_id', '=', obj_attendance.resumen_diario_id.id)])
                h_regist = datetime.strptime(str(obj_attendance.date_spetial), "%Y-%m-%d %H:%M:%S")
                date = h_regist.strftime("%Y-%m-%d")
                aux=datetime.strptime(str(date), "%Y-%m-%d")
                obj_resumen._create_resumen(cr,uid,obj_attendance.employee_id.id, aux, ids_marcaciones,context)
            else:
                h_regist = datetime.strptime(str(obj_attendance.date_spetial), "%Y-%m-%d %H:%M:%S")
                date = h_regist.strftime("%Y-%m-%d")
                aux=datetime.strptime(str(date), "%Y-%m-%d")
                obj_resumen = self.pool.get('assistance.resumen.diario')
                ids_resumen = obj_resumen.search(cr, uid, [('name', '=', obj_attendance.employee_id.id),
                                                           ('date', '=', aux)])
                if not ids_resumen:
                    obj_resumen._create_resumen(cr,uid,obj_attendance.employee_id.id, aux, ids,context)
                    obj_resumen._create_resumen(cr,uid,obj_attendance.employee_id.id, aux, ids,context)
                else:
                    for id_resumen in ids_resumen:
                        ids_marcaciones = self.search(cr, uid, [('resumen_diario_id', '=', id_resumen)])
                        ids_marcaciones.append(ids[0])
                        super(academic_hr_attendance_inherit, self).write(cr, uid, ids, {'resumen_diario_id': id_resumen}, context=context)
                        obj_resumen._create_resumen(cr,uid,obj_attendance.employee_id.id, aux, ids_marcaciones,context)                                                                                   
            return True

    
    def _create_actions_his(self, cr, uid, vals, context):
        employee_idd = int(vals['employee_id'])        
        employee_id_ =  self.pool.get('hr.employee').search(cr, uid, [('id', '=', employee_idd)], context=context)
        for obj_employee in self.pool.get('hr.employee').browse(cr, uid, employee_id_, context):    
            id_history=''        
            try:               
                id_history=vals['history_id']
            except:
                id_history='False'
            if not id_history:
                    try:
                        history_id_ =  self.pool.get('gt.history').search(cr, uid, [('employee_id', '=', obj_employee.id),
                                                                                    ('state', '=', 'open')
                                                                                    ], context=context)
                        vals['history_id']=history_id_[0]
                    except:
                        id_history=''
        return vals
    
    def create(self, cr, uid, vals, context=None):
        """        
        busca el historial padre --Establece el tipo de evento correspondiente
        Crea el evento
        """
        res=[]
        if vals:
            if vals['action'] != 'action':
                semana = {'lunes':0 , 'monday': 0, 'Monday': 0,
                      'martes':1 , 'tuesday': 1, 'Tuesday': 1, 
                      'miércoles':2 , 'wednesday': 2, 'miercoles':2, 'Wednesday': 2,
                      'jueves':3 , 'thursday': 3,  'Thursday': 3,
                      'viernes':4 , 'friday': 4,  'Friday': 4,
                      'sabado':5 , 'saturday': 5, 'sábado':5,  'Saturday':5,
                      'domingo':6 , 'sunday': 6, 'sunday': 6}
                exist_schedules=_create_action(self, cr, uid, vals, context, semana)
                #print 'ENTRA A CREAR ACCION'
                if exist_schedules[1] == True:
                    vals = exist_schedules[0]
                res = super(academic_hr_attendance_inherit, self).create(cr, uid, vals, context=context)
            else:
                if vals['action_type'] == 'assent':              
                    vals = _create_assent(self, cr, uid, vals, context)
                    res = super(academic_hr_attendance_inherit, self).create(cr, uid, vals, context=context)
                else:  
                    if vals['action_type'] == 'notification':
                        vals['mins_delay']=0
                        vals= _create_notification(self, cr, uid, vals, context)
                        res = super(academic_hr_attendance_inherit, self).create(cr, uid, vals, context=context) 
                    else:  
                        if vals['action_type'] == 'notice':    
                            vals = self._create_actions_his(cr, uid, vals, context)                        
                            res = super(academic_hr_attendance_inherit, self).create(cr, uid, vals, context=context)                                                  
                        else:  
                            if vals['action_type'] == 'inconsistency':  
                                vals = self._create_actions_his(cr, uid, vals, context)                       
                                res = super(academic_hr_attendance_inherit, self).create(cr, uid, vals, context=context)
                            else:  
                                if vals['action_type'] == 'excuse':   
                                    vals = self._create_actions_his(cr, uid, vals, context)                         
                                    res = super(academic_hr_attendance_inherit, self).create(cr, uid, vals, context=context)
                                else:  
                                    if vals['action_type'] == 'invalid':  
                                        vals = self._create_actions_his(cr, uid, vals, context)                          
                                        res = super(academic_hr_attendance_inherit, self).create(cr, uid, vals, context=context)
            try:
                #h_regist = timedelta(hours=(-5)) + datetime.strptime(str(vals['date_spetial']), "%Y-%m-%d %H:%M:%S")
                h_regist =  datetime.strptime(str(vals['date_spetial']), "%Y-%m-%d %H:%M:%S")
                #print str(res) + ' - ' + str(h_regist)
                date = h_regist.strftime("%Y-%m-%d")
                aux= datetime.strptime(str(date), "%Y-%m-%d")
                obj_resumen = self.pool.get('assistance.resumen.diario')
                ids_resumen = obj_resumen.search(cr, uid, [('name', '=', vals['employee_id']),
                                                           ('date', '=', aux)])
                if not ids_resumen:
                    obj_resumen._create_resumen(cr,uid,vals['employee_id'], aux, [res],context)
                    obj_resumen._create_resumen(cr,uid,vals['employee_id'], aux, [res],context)
                else:
                    for id_resumen in ids_resumen:
                        ids_marcaciones = self.search(cr, uid, [('resumen_diario_id', '=', id_resumen)])
                        ids_marcaciones.append(res)
                        super(academic_hr_attendance_inherit, self).write(cr, uid, [res], {'resumen_diario_id': id_resumen}, context=context)
                        obj_resumen._create_resumen(cr,uid,vals['employee_id'], aux, ids_marcaciones,context)
            except:
                pass
            return res                                                           

    def cancel_history(self, cr, uid, ids, context):
        cont=0
        for obj in self.browse(cr, uid, ids, context):
            if obj.state=='cancel' and obj.history_cancel==False:
                history_id =  self.pool.get('gt.history').search(cr, uid, [('id','=', obj.history_id.id)], context=context)
                for obj_history in self.pool.get('gt.history').browse(cr, uid, history_id, context):
                   if obj.not_normal==True:
                    if not obj.assent_type_id:                        
                        cont=obj_history.counter_assent
                        if int(cont)== 0:
                            new_number=(obj_history.type_assent_id.number_max )-1
                            text="Es posible que este evento haya disparado una sancion  " + ustr(obj_history.type_assent_id.next_assent_id.name) + '. VERIFICAR '
                    else:
                        if int(obj_history.type_assent_id_acu.code) > int(obj.assent_type_id.code):
                         text="El historial presenta una sacion de mayor rango, verificar sus causas"
                        else:
                            if int(obj_history.type_assent_id_acu.code) == int(obj.assent_type_id.code):
                                cont_acum= (obj_history.counter_assent_acu)-1
academic_hr_attendance_inherit()

def _verify_time_delay(self, cr, uid, hour_regist,h_real,history_id,minutes, registro_accion, vals):
    '''
    verrifica si el tiempo del atraso amerita una sanción
    '''    
    context = {}
    added_minutes =0
    minutes_real=0
    atendance_id = ''
    history_id =  self.pool.get('gt.history').search(cr, uid, [('id', '=', history_id),], context=context)
    if history_id:        
        for obj_history in self.pool.get('gt.history').browse(cr, uid, history_id, context):
            if vals['date_dbo']:
                h_register_ = datetime.strptime(str(vals['date_dbo']), "%Y-%m-%d %H:%M:%S")
                #new_date= + timedelta(hours=5) + h_register_
                new_date=  h_register_
                date_spetial_ = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
            else:                
                date_spetial_=vals['date_spetial']
         
            if registro_accion == 'sign_in':
                added_minutes = datetime.strptime(hour_regist, "%H:%M:%S") - datetime.strptime(h_real, "%H:%M:%S")
            else:            
                added_minutes = datetime.strptime(h_real, "%H:%M:%S") - datetime.strptime(hour_regist, "%H:%M:%S")                                     
            if added_minutes:            
                sum_minutes = obj_history.month_minute + int((added_minutes.seconds + added_minutes.microseconds / 1000000.0) / 60.0)                
                sum_anual = obj_history.anual_minute + int((added_minutes.seconds + added_minutes.microseconds / 1000000.0) / 60.0)
                minutes_real= int((added_minutes.seconds + added_minutes.microseconds / 1000000.0) / 60.0)
                self.pool.get('gt.history').write(cr,uid,obj_history.id,{'month_minute':sum_minutes,'anual_minute':sum_anual})                
            if minutes_real:            
                assent_anual = self.pool.get('gt.assent.type').search(cr, uid, [('max_anual', '=', True)], context = context)
                for assent in self.pool.get('gt.assent.type').browse(cr, uid, assent_anual, context):
                    if assent.minutes_max_anual<sum_anual:
                        atendance_id= self.pool.get('hr.attendance').create(cr,uid, {'action': 'action',
                                                                       'history_id': obj_history.id,
                                                                       'action_type': 'assent',
                                                                       'date_spetial': date_spetial_,
                                                                       'assent_type_id': assent.id,
                                                                       'employee_id': obj_history.employee_id.id,
                                                                       'notes':'' + str(assent.minutes_max_anual) + '  minutos anuales',
                                                                       'not_normal': True},context=context)
                          
                        self.pool.get('gt.history').write(cr,uid,obj_history.id,{'anual_minute':0})                 
                assent_month = self.pool.get('gt.assent.type').search(cr, uid, [('max_month', '=', True)], context = context)            
                for assent in self.pool.get('gt.assent.type').browse(cr, uid, assent_month, context):
                    if assent.minutes_max_month<sum_minutes:
                        atendance_id =self.pool.get('hr.attendance').create(cr,uid, {'action': 'action',
                                                                       'history_id': obj_history.id,
                                                                       'employee_id': obj_history.employee_id.id,
                                                                       'action_type': 'assent',
                                                                       'date_spetial': date_spetial_,
                                                                       'assent_type_id': assent.id ,
                                                                       'notes': str(assent.minutes_max_month) + '  minutos mensuales',
                                                                       'not_normal': True},context=context)  
                        self.pool.get('gt.history').write(cr,uid,obj_history.id,{'month_minute':0})
    return [minutes_real , atendance_id]                                   


def _verify_absence(self, cr, uid, employee_id, type_action, h_regist, registro_accion):
    '''
    Verifica si exste permiso para ese día y hora
    '''
    result=False
    context = {}
    sum_minutes=minutes=0
    holidays= self.pool.get('hr.holidays')    
    dt_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")    
    date_regist = dt_regist.strftime("%Y-%m-%d")
    hour_r = dt_regist.strftime("%H:%M:%S")
    assent_types= holidays.search(cr, uid, [('employee_id', '=', employee_id),
                                            ('state', '=', 'validate')
                                            ], context=context)
                                            #consultar si puede haber otro campo de compar
    id_emp = self.pool.get('hr.employee').search(cr, uid, [('id', '=', employee_id),], context=context)
    for obj_employee in self.pool.get('hr.employee').browse(cr, uid, id_emp, context):
        str_hour = obj_employee.contract_id.work_id.schedule_half #REVISAR TIME
        if str_hour:
            dec= (30*(int((str_hour-int(str_hour))*100)))/50
            med_day = time.strftime('%H:%M:%S', time.strptime(str(int(str_hour)) + ':' + str(dec), '%H:%M'))
    for assent in holidays.browse(cr, uid, assent_types, context):  
      if str_hour:
        t_from = datetime.strptime(assent.date_from, "%Y-%m-%d %H:%M:%S")
        t_to = datetime.strptime(assent.date_to, "%Y-%m-%d %H:%M:%S")               
        date_assent=t_to.strftime("%Y-%m-%d")           
        date_assentf=t_from.strftime("%Y-%m-%d")                  
        assent_end = t_to.strftime("%H:%M:%S")                   
        assent_start = t_from.strftime("%H:%M:%S")                 
        if date_regist == date_assent == date_assentf:
            if registro_accion == 'sign_in':
                if hour_r < med_day and assent_end < med_day:                    
                    if hour_r <= assent_end and hour_r > assent_start:
                        minutes=0
                        result =True 
                else:
                    if hour_r >= med_day and assent_end >= med_day:                                                                     
                        if hour_r <= assent_end and hour_r > assent_start:                            
                            minutes=0
                            result =True                                                                                                                
            else:
                if hour_r < med_day and assent_start < med_day:                    
                    if hour_r >= assent_start and hour_r < assent_end:
                        minutes=0  
                        result =True                                         
                else:                    
                    if hour_r >= med_day and assent_start >= med_day:                       
                        if hour_r >= assent_start and hour_r < assent_end:
                            minutes=0
                            result =True
        else:
            if registro_accion == 'sign_in':
                if hour_r < med_day and assent_end < med_day:                    
                    if hour_r <= assent_end:
                        minutes=0
                        result =True 
                else:
                    if hour_r >= med_day and assent_end >= med_day:                                                                     
                        if hour_r <= assent_end:                            
                            minutes=0
                            result =True
            else:
                if hour_r < med_day and assent_start < med_day:                    
                    if hour_r >= assent_start:
                        minutes=0  
                        result =True                                         
                else:                    
                    if hour_r >= med_day and assent_start >= med_day:                       
                        if hour_r >= assent_start:
                            minutes=0
                            result =True
                                     
    return [result, minutes]


def get_in_out(self, cr, uid, vals,id_emp,semana,hour_regist, day_code, context= None):  
    '''
    devuelve hora de entrada y salida del horario de la jorana correspondiente
    '''
    exist_schedule=False 
    calendar_ids=''
    h_in=h_out=hour_from=0
    id_emp = self.pool.get('hr.employee').search(cr, uid, [('id', '=', id_emp[0]),], context=context)
    for obj_employee in self.pool.get('hr.employee').browse(cr, uid, id_emp, context):
        str_hour = obj_employee.contract_id.work_id.schedule_half #REVISAR TIME
        if str_hour:
            dec= (30*(int((str_hour-int(str_hour))*100)))/50
            
            med_day = time.strftime('%H:%M:%S', time.strptime(str(int(str_hour)) + ':' + str(dec), '%H:%M'))
            calendar_ids = self.pool.get('resource.calendar.attendance').search(cr, uid, [('dayofweek', '=', ustr(day_code)),
                                                                                      ('calendar_id','=',obj_employee.contract_id.work_id.id),
                                                                                      ], context=context)
    if calendar_ids:
          exist_schedule=True 
          if len(calendar_ids)==2:            
            for obj_calendar in self.pool.get('resource.calendar.attendance').browse(cr, uid, calendar_ids, context):
                dato_in = obj_calendar.hour_from                
                min_in=abs((30*(int((dato_in-int(dato_in))*100)))/50)                   
                h_in = time.strftime('%H:%M:%S', time.strptime(str(int(dato_in)) + ':' + str(int(min_in)), '%H:%M'))                
                dato_out = obj_calendar.hour_to  
                min_out=abs((30*(int((dato_out-int(dato_out))*100)))/50)                              
                h_to = time.strftime('%H:%M:%S', time.strptime(str(int(dato_out)) + ':' + str(int(min_out)), '%H:%M'))
                if hour_regist < med_day and h_in < med_day:
                    hour_from= h_in
                    h_out=h_to
                else:     
                    if hour_regist >= med_day and h_in > med_day:  
                        hour_from= h_in
                        h_out=h_to                                             
          else:
            for obj_calendar in self.pool.get('resource.calendar.attendance').browse(cr, uid, calendar_ids, context):
                dato_in = obj_calendar.hour_from
                dato_out = obj_calendar.hour_to   
                min_in=abs((30*(int((dato_in-int(dato_in))*100)))/50)  
                min_out= abs((30*(int((dato_out-int(dato_out))*100)))/50)  
                hour_from = time.strftime('%H:%M:%S', time.strptime(str(int(dato_in)) + ':' + str(int(min_in)), '%H:%M'))
                h_out = time.strftime('%H:%M:%S', time.strptime(str(int(dato_out)) + ':' + str(int(min_out)), '%H:%M'))
          return [exist_schedule, hour_from, h_out]


def structure_body(self, cr, uid, vals, context, id_emp, id_assent):
    id_emp = self.pool.get('hr.employee').search(cr, uid, [('id', '=', id_emp),], context=context)    
    for obj_employee in self.pool.get('hr.employee').browse(cr, uid, id_emp, context):
        email_body=''
        cadena=''
        if obj_employee.receives_notifications== True:
            obj_configuration =  self.pool.get('gt.field.workable').search(cr, uid, [], context=context)
            if id_assent == '':
                if obj_configuration:
                    for obj_configuration in self.pool.get('gt.field.workable').browse(cr, uid, obj_configuration, context):
                        cadena= obj_configuration.body_mail
                        if cadena:                                                        
                            if  vals['mins_delay'] != 0:                            
                                email_body=cadena.replace("delay_minutes", str(vals['mins_delay']))
            else:
                id_assent = self.pool.get('gt.report.type').search(cr, uid, [('id', '=', id_assent),], context=context)
                for obj_assent in self.pool.get('gt.report.type').browse(cr, uid, id_assent, context):
                    cadena= obj_assent.body_2
                    if cadena:
                        email_body=cadena.replace("assent_name", obj_assent.name)
            if cadena:                          
                email_body=email_body.replace("head", str(time.strftime('%d de %B del %Y')))
                aux=''
                aux= ustr(obj_employee.complete_name)            
                email_body=email_body.replace("employee_id", aux)                        
                email_body = email_body.replace("employee_ci", obj_employee.name)
                correo_employee=ustr(obj_employee.work_email)
                try:
                    if obj_employee.email:
                        correo_employee = ustr(obj_employee.work_email) + ',  ' + str(obj_employee.email)
                except:
                    pass
                email_body=email_body.replace("e_mail", correo_employee )                
                try:
                    email_body=email_body.replace("day_event", str(vals['date_dbo']))                    
                except:
                     day_event_exist=''                
                try:
                    if day_event_exist=='':
                        email_body=email_body.replace("day_event", str(vals['date_spetial']))                    
                except:
                    email_body=email_body.replace("day_event", str(time.strftime('%d de %B del %Y')))                                                        
                try:                   
                    if vals['action_type']== 'delay':                        
                        email_body=email_body.replace("event_causes", 'Atraso')                        
                    else:
                        if vals['action_type']== 'before':
                            email_body=email_body.replace("event_causes", 'Salida antes')
                        else:
                            email_body=email_body.replace("event_causes", vals['notes'])
                except:
                    email_body=email_body.replace("event_causes", '')
                     
                email_body=email_body.replace("notification_action", vals['notes'])                                                                                            
    return email_body                            


def create_delay(self, cr, uid, vals, context, id_emp,hour_regist,h_in,obj_history_id,registro_accion):
    '''
    Crea atrasos
    '''
    id_emp = self.pool.get('hr.employee').search(cr, uid, [('id', '=', id_emp),], context=context)    
    for obj_employee in self.pool.get('hr.employee').browse(cr, uid, id_emp, context):
        time_not_work = _verify_time_delay(self, cr, uid, hour_regist, h_in, obj_history_id, False, registro_accion, vals )
        vals['action_type'] = 'delay'
        vals['not_normal'] = 'True'   
        coach_mail=''                                                             
        vals['mins_delay']=int(time_not_work[0])        
        if time_not_work[1]:
            vals['attendance_id']=int(time_not_work[1])
        if obj_employee.receives_notifications== True:                               
            coach_mail=''
            obj_configuration =  self.pool.get('gt.field.workable').search(cr, uid, [], context=context)
            if obj_configuration:
                for obj_configuration in self.pool.get('gt.field.workable').browse(cr, uid, obj_configuration, context):
                    vals['notes']=''
                    email_body= structure_body(self, cr, uid, vals, context, id_emp,'')
                    email_cc= ustr(obj_configuration.mail_copy).split(',')
            coach_mail=obj_employee.coach_id.work_email            
            if coach_mail:
                email_cc.append(coach_mail)
            email_cc.append(ustr(obj_employee.work_email))
            try:
                if obj_employee.email:
                    email_cc.append(obj_employee.email)
            except:
                pass                
            vals['body']=send_mail(self, cr, uid, [email_cc, email_body, 'Fuera de Horario'])        
    return vals


def get_vals_action(self, cr, uid, vals, context, employee_id, date_marc, attendance_id):
    '''
    Valida si se trata de  marcacion de entrada o marcacion de salida.
    para marcaciones creadas manualmente.
    '''
    id_emp = self.pool.get('hr.employee').search(cr, uid, [('id', '=', employee_id),], context=context)    
    for obj_employee in self.pool.get('hr.employee').browse(cr, uid, id_emp, context):
        date_old_marc = datetime.strptime(str(date_marc), "%Y-%m-%d %H:%M:%S")
        start_ = date_old_marc.strftime("%Y-%m-%d")            
        end= str(datetime.strptime(str(timedelta(days=1) + datetime.strptime(str(start_), "%Y-%m-%d")), "%Y-%m-%d %H:%M:%S"))
        end = datetime.strptime(str(end), "%Y-%m-%d %H:%M:%S")
        end_ = end.strftime("%Y-%m-%d")
        if not attendance_id:
            marc_ids= self.pool.get('hr.attendance').search(cr, uid, [('employee_id','=',obj_employee.id),
                                                                      ('date_spetial','>=',start_),
                                                                      ('date_spetial','<',end_),
                                                                      ('action','!=','action'),])
        else:
            marc_ids= self.pool.get('hr.attendance').search(cr, uid, [('id','!=',attendance_id),
                                                                      ('employee_id','=',obj_employee.id),
                                                                      ('date_spetial','>=',start_),
                                                                      ('date_spetial','<',end_),
                                                                      ('action','!=','action'),])
        if not marc_ids:
            return 'sign_in'
        else:
            if (len(marc_ids) % 2) == 0:
                return 'sign_in'
            else:
                return 'sign_out'                       
     
    
def _create_action(self, cr, uid, vals, context, semana):
    '''
    Crea acciones
    '''        
    result=[[],False] 
    exist_schedule = False
    registro_accion = 'sign_in'    
    h_in=h_out= dato_in=dato_out=0   
    email_body=''
    now = datetime.now()
    #print 'ENTRA A CREAR LA ACCION'
    if not vals['date_dbo']:        
        h_regist = datetime.strptime(str(vals['date_spetial']), "%Y-%m-%d %H:%M:%S")
        #hour_regist = time.strftime('%H:%M:%S', time.strptime(str(int(h_regist.hour)-5) + ':' + str(int(h_regist.minute))+ ':' + str(int(h_regist.second)), '%H:%M:%S'))
        hour_regist = time.strftime('%H:%M:%S', time.strptime(str(int(h_regist.hour)) + ':' + str(int(h_regist.minute))+ ':' + str(int(h_regist.second)), '%H:%M:%S'))
        if vals['employee_id']:            
            id_emp = self.pool.get('hr.employee').search(cr, uid, [('id', '=', int(vals['employee_id'])),], context=context)
            history_id =  self.pool.get('gt.history').search(cr, uid, [('employee_id', '=', id_emp[0]),
                                                                       ('start_date', '<=', time.strftime('%Y-%m-%d')),
                                                                       ('end_date', '>=', time.strftime('%Y-%m-%d')),
                                                                       ('state', '=', 'open')], context=context)    
    else:        
        h_regist = datetime.strptime(str(vals['date_dbo']), "%Y-%m-%d %H:%M:%S")
        date = h_regist.strftime("%Y-%m-%d")
        only_date= datetime.strptime(str(date), "%Y-%m-%d")                       
        #hour_regist = time.strftime('%H:%M:%S', time.strptime(str(int(h_regist.hour)) + ':' + str(int(h_regist.minute))+ ':' + str(int(h_regist.second)), '%H:%M:%S'))    
        hour_regist = time.strftime('%H:%M:%S', time.strptime(str(int(h_regist.hour)) + ':' + str(int(h_regist.minute))+ ':0' , '%H:%M:%S'))
        id_emp=[int(vals['employee_id'])]
        h_register_ = datetime.strptime(str(vals['date_dbo']), "%Y-%m-%d %H:%M:%S")
        new_date= h_register_ #+ timedelta(hours=5) 
        vals['date_spetial']= datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
        history_id =  self.pool.get('gt.history').search(cr, uid, [('employee_id', '=', id_emp[0]),
                                                                   ('state', '=', 'open')
                                                                   ], context=context)
        if len(history_id)>1:
            raise osv.except_osv(_('Error'), _('Existe más de un historial activo para el empleado. Es necesario cancelar los historiales anteriores'))            
    if history_id:
        for obj_history in self.pool.get('gt.history').browse(cr, uid, [history_id[0]], context):   
            if vals['date_dbo']:
                date_spetial_=vals['date_dbo']
                state_direct=True
            else:
                date_spetial_= vals['date_spetial'] 
                state_direct=False
            for obj_employee in self.pool.get('hr.employee').browse(cr, uid, id_emp, context):
                if state_direct:
                    #print 'VERIFICA ESTADO EN E SISTEMA' +str(obj_employee.state_system)                     
                    if obj_employee.state_system == True:
                        registro_accion ='sign_out'
                        vals['action'] = 'sign_out'  
                        if  vals['date_dbo']:
                            self.pool.get('hr.employee').write(cr,uid,[obj_employee.id],{'state_system':False},context=None)
                    else:            
                        registro_accion ='sign_in' 
                        vals['action'] = 'sign_in'   
                        if  vals['date_dbo']: 
                            self.pool.get('hr.employee').write(cr,uid,[obj_employee.id],{'state_system':True},context=None)
                else:
                   registro_accion = get_vals_action(self, cr, uid, vals, context, obj_employee.id, vals['date_spetial'],'' ) 
                   vals['action'] = registro_accion
                import pdb
                pdb.set_trace()                                                                  
                if obj_employee.contract_id.marc_employee== False:
                    vals['action_type'] = 'marc'
                    exist_schedule=True
                    hours_to_compare = get_in_out(self, cr, uid, vals, id_emp, semana, hour_regist, int(semana[h_regist.strftime("%A")]) )
                else:                                         
                  hours_to_compare = get_in_out(self, cr, uid, vals, id_emp, semana, hour_regist, int(semana[h_regist.strftime("%A")]) )#, id_emp, hour_regist,semana , context)
                  exist_schedule= hours_to_compare[0]
                if exist_schedule:
                    h_in= hours_to_compare[1]                
                    h_out= hours_to_compare[2]                                                                                                      
                    if (registro_accion == 'sign_in' and hour_regist <= h_in) or (registro_accion == 'sign_out'and hour_regist > h_out):                        
                        vals['action_type'] = 'marc'
                        if registro_accion == 'sign_in': 
                            vals['hour_reference']= h_in 
                        else:  
                            vals['hour_reference']= h_out                                 
                    else:              
                        if registro_accion == 'sign_in' and hour_regist > h_in:
                            
                            vals['hour_reference']= h_in 
                            absence = _verify_absence(self, cr, uid, obj_employee.id, 'sign_in', h_regist, registro_accion)
                            if absence[0]==False:                              
                                vals = create_delay(self, cr, uid, vals, context, obj_employee.id, hour_regist, h_in, obj_history.id, registro_accion)  
                                hour_regist                              
                            else:                               
                                vals['action_type'] = 'marc'
                                vals['notes'] = 'Permiso'    
                                vals['hour_reference']= h_in                                                                                                                                                    
                        else:
                            if registro_accion== 'sign_out' and hour_regist < h_out:
                                vals['hour_reference']= h_out 
                                absence = _verify_absence(self, cr, uid, obj_employee.id, 'sign_out', h_regist, registro_accion)                                
                                if absence[0]==False: 
                                    vals = create_delay(self, cr, uid, vals, context, obj_employee.id, hour_regist, h_out, obj_history.id, registro_accion)                                    
                                else:
                                    vals['hour_reference']= h_out
                                    vals['action_type'] = 'marc' 
                                    vals['notes'] = 'Permiso'                                                              
                else:
                    vals['action_type']='inconsistency'
                    vals['action']='action'
                    vals['notes']='No existe horario de trabajo establecido para el usuario el dia en que se realizo la marcacion',
            
                if int(obj_history.counter_assent) == 0 and vals['action_type'] != 'marc' and  exist_schedule==True:
                    assent_type = self.pool.get('gt.assent.type').search(cr, uid, [('min_assent', '=', True),], context = context)                                                                                   
                    self.pool.get('gt.history').write(cr,uid,obj_history.id,{'counter_assent':int(obj_history.counter_assent) + 1,'type_assent_id':assent_type[0]})
                else:
                    if int(obj_history.counter_assent) > 0 and vals['action_type'] != 'marc' and  exist_schedule==True:                              
                        if int(obj_history.counter_assent)  < obj_history.type_assent_id.number_max:
                            self.pool.get('gt.history').write(cr,uid,obj_history.id,{'counter_assent':int(obj_history.counter_assent)+1})
                        else:
                            assent_types= self.pool.get('hr.attendance').search(cr, uid, [('not_normal', '=', True),
                                                                                          ('action', '!=', 'action'),
                                                                                          ('indicted','=',False),], context=context)
                            self.pool.get('hr.attendance').write(cr,uid,assent_types,{'indicted':True})                              
                            self.pool.get('gt.history').write(cr,uid,obj_history.id,{'counter_assent':1})  
                            #print 'AQUI ENTRA A CREAR EL REGISTRO'                                                                        
                            atendance_id=self.pool.get('hr.attendance').create(cr,uid, {'action': 'action',
                                                                                        'history_id': obj_history.id,
                                                                                        'action_type': 'assent',
                                                                                        'date_spetial': date_spetial_,
                                                                                        'employee_id': obj_employee.id,
                                                                                        'assent_type_id': obj_history.type_assent_id.next_assent_id.id,
                                                                                        'notes': ''+ str(obj_history.type_assent_id.number_max) + ' - ' + ustr(obj_history.type_assent_id.name),
                                                                                        'not_normal': True},context=context)
                            
                            vals['attendance_id']=atendance_id                                                                                                                                    
                vals['history_id'] = obj_history.id  
        result = [vals, exist_schedule]
    else:
        vals['notes']='No existe un historial activo para el usuario' 
        vals['action_type']='inconsistency'
        vals['action']='action'
    return  result          
            
    
def _create_assent(self, cr, uid, vals, context): 
    '''
    crea sanciones
    '''         
    for obj_type in self.pool.get('gt.assent.type').browse(cr, uid, [int(vals['assent_type_id'])], context):
        if obj_type.max_assent == False:
            for obj_history in self.pool.get('gt.history').browse(cr, uid, [int(vals['history_id'])], context):
                if obj_type.notification:
                    if obj_history.employee_id.receives_notifications:
                        try:                    
                            atendance_id=self.pool.get('hr.attendance').create(cr,uid, {'action': 'action',
                                                                             'employee_id': obj_history.employee_id.id,
                                                                            'history_id': vals['history_id'],
                                                                            'date_spetial':datetime.strptime(str(vals['date_spetial']), "%Y-%m-%d %H:%M:%S") ,
                                                                            'action_type': 'notification',
                                                                            'assent_type_id':vals['assent_type_id'],
                                                                            'notes': ustr(vals['notes']), #+ '.   Enviada a:   ' + obj_history.employee_id.work_email ,
                                                                            'not_normal': False},context=context)
                        except:
                            atendance_id=self.pool.get('hr.attendance').create(cr,uid, {'action': 'action',
                                                                             'employee_id': obj_history.employee_id.id,
                                                                            'history_id': vals['history_id'],                                                                            
                                                                            'action_type': 'notification',
                                                                            'assent_type_id':vals['assent_type_id'],
                                                                            'notes': ustr(vals['notes']), #+ '.   Enviada a:   ' + obj_history.employee_id.work_email ,
                                                                            'not_normal': False},context=context)
                            
                        vals['attendance_id']=atendance_id                                                                                                                                                               
                if not obj_history.type_assent_id_acu:
                     self.pool.get('gt.history').write(cr,uid,obj_history.id,{'counter_assent_acu':1,'type_assent_id_acu':int(vals['assent_type_id'])})
                else:
                    if obj_history.type_assent_id_acu.code == obj_type.code:  
                        self.pool.get('gt.history').write(cr,uid,obj_history.id,{'counter_assent_acu':int(obj_history.counter_assent_acu)+1})
                    else:
                        if obj_history.type_assent_id_acu.code < obj_type.code:
                            self.pool.get('gt.history').write(cr,uid,obj_history.id,{'counter_assent_acu':1,'type_assent_id_acu':int(vals['assent_type_id'])})                               
            ids_actions = self.pool.get('hr.attendance').search(cr, uid, [('not_normal', '=', True), 
                                                                       ('action', '=', 'action'),
                                                                          ('employee_id', '=', obj_history.employee_id.id),
                                                                          ('indicted','=',False), 
                                                                          ('assent_type_id','=',vals['assent_type_id']),
                                                                          ], context=context)
            if len(ids_actions) + 1 > obj_type.number_max: 
                vals['indicted']=True                       
                self.pool.get('hr.attendance').write(cr,uid,ids_actions,{'indicted':True})                                                        
                atendance_id = self.pool.get('hr.attendance').create(cr,uid, {'action': 'action',
                                        'history_id': vals['history_id'],
                                        'action_type': 'assent',
                                        'employee_id': obj_history.employee_id.id,
                                        'date_spetial': datetime.strptime(str(vals['date_spetial']), "%Y-%m-%d %H:%M:%S"),
                                        'assent_type_id':obj_type.next_assent_id.id,
                                        'notes': '' + ustr(obj_type.number_max) + ' -  ' + ustr(obj_type.name),
                                        'not_normal': True},context=context)
                vals['attendance_id']=atendance_id
        else:
            for obj_history in self.pool.get('gt.history').browse(cr, uid, [int(vals['history_id'])], context):
                if obj_history.type_assent_id_acu.id == int(vals['assent_type_id']):
                    self.pool.get('gt.history').write(cr,uid,obj_history.id,{'counter_assent_acu':int(obj_history.counter_assent_acu)+1})
                else:
                    self.pool.get('gt.history').write(cr,uid,obj_history.id,{'counter_assent_acu':1,'type_assent_id_acu':int(vals['assent_type_id'])})                                                
    return vals


def _create_notification(self, cr, uid, vals, context): 
    '''
    crea evento de tipo notificacion y manda a crear la notificacion como objeto
    '''                                                                                                                         
    for obj_type in self.pool.get('gt.assent.type').browse(cr, uid, [int(vals['assent_type_id'])], context):
        id_notification=obj_type.notification_type.id
        email_body=''
        email_cc=[]
        if id_notification:            
            for obj_notification in self.pool.get('gt.report.type').browse(cr, uid, [id_notification], context):
                obj_configuration =  self.pool.get('gt.field.workable').search(cr, uid, [], context=context)
                if obj_configuration:
                    for obj_configuration in self.pool.get('gt.field.workable').browse(cr, uid, obj_configuration, context):
                        email_cc= ustr(obj_configuration.mail_copy).split(',')                
                employee_name = 'Nombre del empleado'
                for obj_history in self.pool.get('gt.history').browse(cr, uid, [int(vals['history_id'])], context):
                    employee_name= obj_history.employee_id.last_name + '  '+  obj_history.employee_id.name
                    coach_mail= obj_history.employee_id.coach_id.work_email
                    if coach_mail:    
                        email_cc.append(coach_mail)
                    email_cc.append(obj_history.employee_id.work_email)
                    try:
                        if obj_history.employee_id.email:
                            email_cc.append(obj_history.employee_id.email)
                    except:
                        pass
                    email_body = structure_body(self, cr, uid, vals, context, obj_history.employee_id.id, obj_notification.id)                                                         
            vals['body']= send_mail(self, cr, uid, [email_cc, email_body, obj_notification.name])    
                       
    return vals

  
def send_mail(obj, cr, uid, vals, context=None):
    mail_ids=obj.pool.get('ir.mail_server').search(cr, uid, [], context = context)
    for mails_obj in obj.pool.get('ir.mail_server').browse(cr, uid, mail_ids, context):
        if mails_obj.smtp_user:
            mail_name= mails_obj.smtp_user            
    if mail_name: 
        ir_mail_server = obj.pool.get('ir.mail_server')
        #msg = ir_mail_server.build_email(email_from=mail_name , email_to=vals[0], subject= vals[2], body=vals[1],)
    try:     
        msg = ir_mail_server.build_email(email_from=mail_name + str('@azuay.gob.ec') , email_to=vals[0], subject= vals[2], body=vals[1],)
    except:
        #print vals[1]
        pass
        ir_mail_server.send_email(cr, uid, msg, context=context)
        return vals[1]
    return 
    
    
class gt_history(osv.osv):
    '''
    Assent
    '''
    _description = 'Historial Mensual' 
    _name = 'gt.history'  
    _columns = {'name': fields.char('Nombre', size=64, required=True),
                'start_date': fields.date('Fecha de Inicio',required=True),
                'end_date': fields.date('Fecha de Fin',required=True),
                'counter_assent':fields.integer('Atrasos actuales', size= 20, ),
                'type_assent_id': fields.many2one('gt.assent.type','Tipo', size= 64,),
                'counter_assent_acu':fields.integer('Sanciones acumuladas', size= 20,),
                'type_assent_id_acu': fields.many2one('gt.assent.type','Tipo', size= 64,),                                
                'state': fields.selection([('draft', 'Borrador'),('open', 'Abierto'),
                                           ('cancel', 'Cancelado'),
                                           ('close', 'Cerrado')],'Estado',),
                'employee_id' : fields.many2one('hr.employee','Empleado', required=True),
                'event_ids' : fields.one2many('hr.attendance','history_id','Eventos'),
                'anual_minute' :fields.integer('Atrasos Anuaes (min)', ),
                'month_minute' :fields.integer('Atrasos Mensuales (min)',),
                'wizard_id' : fields.many2one('gt.wizard.history','Empleado'),
                }     
    def gt_gpa_history_draft(self, cr, uid, ids):
        self.write(cr, uid, ids, { 'state': 'draft' })
        return True
    def gt_gpa_history_open(self, cr, uid, ids):
        self.write(cr, uid, ids, { 'state': 'open' })
        return True
    def gt_gpa_history_close(self, cr, uid, ids):
        self.write(cr, uid, ids, { 'state': 'close' })
        return True 
    def gt_gpa_history_cancel(self, cr, uid, ids):
        self.write(cr, uid, ids, { 'state': 'cancel' })
        return True 
        
    _defaults = {
        'state': 'draft',
        'counter_assent':0,
        'anual_minute':0,
        'month_minute':0,        
    }                     
gt_history()

 
class gt_wizard_history(osv.osv):
    '''
    Crea historial por tipo de contrato; 
    se cambia el hr_regime: hr.contract.type
    '''
    _description = 'Wizard Creacion historial' 
    _name = 'gt.wizard.history'  
    _columns = {'name': fields.char('Fecha de Ejecucion', size=64, required=True, readonly=True),
                'start_date':fields.date('Fecha de Inicio', store=True, required=True),
                'end_date': fields.date('Fecha de Fin', required=True),
                'regime': fields.many2one('hr.contract.type','Tipo de contrato', size= 64, required=True),
                'first_history': fields.boolean('Primer Historial'),
                'name_history':fields.char('Nombre', size=64, required=True),  
                'indicted': fields.boolean('Ya procesado', readonly=True),              
                'employee_id': fields.many2one('res.users','Empleado'),
                'prev_history': fields.many2one('gt.wizard.history','Historial Anterior', size= 64),
                'prev_start_date': fields.char('Fecha de Inicio', size=64, readonly=True, store=True),          
                'prev_end_date': fields.date('Fecha de Fin', store=True),
                'history_ids': fields.one2many('gt.history','wizard_id','Historial', ondelete='cascade'),
                'state': fields.selection([('draft', 'Borrador'),
                                           ('open', 'Abierto'),
                                           ('cancel', 'Cancelado'),
                                           ('close', 'Cerrado')],'Estado',)
                }        
    _defaults = {
                 'employee_id': _employee_get,
                 'state': 'draft',
                 'indicted': False,
                 'name': time.strftime('%B/%d/%Y')
                 }   
    def cancelar_historial(self, cr, uid, ids,context=None):        
        #cancela registro de historiales cuando aun estan esn estado borrador
        for obj in self.browse(cr, uid, ids, context):
            for  obj_individual in obj.history_ids:            
                self.pool.get('gt.history').gt_gpa_history_cancel(cr, uid, [obj_individual.id])         
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
    def cerrar_historial(self, cr, uid, ids,context=None):        
        #cancela registro de historiales cuando aun estan esn estado borrador
        for obj in self.browse(cr, uid, ids, context):
            for  obj_individual in obj.history_ids:            
                self.pool.get('gt.history').gt_gpa_history_close(cr, uid, [obj_individual.id])         
        self.write(cr, uid, ids, {'state': 'close'})
        return True 
    def abrir_manual(self, cr, uid, ids,context=None):        
        #cancela registro de historiales cuando aun estan esn estado borrador
        for obj in self.browse(cr, uid, ids, context):
            hist_abiertors= self.search(cr, uid, [('state','=', 'open'),
                                     ('regime','=', obj.regime.id)], context=context)
            
            if hist_abiertors:
                raise osv.except_osv(_('Error'), _('Ya exite un historial de marcaciones activo para el tipo de contrato indicado.'))
            else:
                if obj.history_ids:
                    for  obj_individual in obj.history_ids:            
                        self.pool.get('gt.history').gt_gpa_history_open(cr, uid, [obj_individual.id])         
                else:
                    raise osv.except_osv(_('Error'), _('No se han cargado registros de empleados'))
        self.write(cr, uid, ids, {'state': 'open'})
        return True         
   
    def unique_his(self, cr, uid,ids, context=None):
        correct_start=False
        for obj in self.browse(cr, uid, ids, context):
            employe_ids=self.employee_x_contract(cr, uid, obj.regime.id,obj.start_date,obj.end_date, context)
            #employe_ids =  self.pool.get('hr.employee').search(cr, uid, [('regime','=', obj.regime.id)], context=context)
            for obj_employee in self.pool.get('hr.employee').browse(cr, uid, employe_ids, context):
                history_ids = self.pool.get('gt.history').search(cr, uid, [('wizard_id','=',obj.id),
                                                                       ('employee_id','=',obj_employee.id)], context=context)
                if not history_ids:
                        id_his=self.pool.get('gt.history').create(cr,uid, {'name': obj.name_history,
                                                                        'employee_id': obj_employee.id,
                                                                        'start_date': obj.start_date,
                                                                        'state': obj.state,
                                                                        'wizard_id': obj.id,
                                                                        'end_date': obj.end_date},context=context)
                        self.pool.get('gt.history').write(cr,uid,id_his,{'state':obj.state})
        return correct_start

    def load_date(self, cr, uid, ids, wizard_id, context=None):
        res = {'value': {}}
        for obj_wizard_h in self.pool.get('gt.wizard.history').browse(cr, uid, [wizard_id], context):
            res['value'] = {'prev_start_date': obj_wizard_h.start_date,
                            'prev_end_date': obj_wizard_h.end_date,}      
        return res 
    
    def load_date_start(self, cr, uid, ids, date, context=None):
        res = {'value': {}}
        previous_date= datetime.strptime(date, "%Y-%m-%d")
        new_date= + timedelta(days=1) + previous_date            
        return res 
    
    def employee_x_contract(self, cr, uid, ids,start_date,end_date, context):
        #Verifica los contratos activos para la fecha de creacion en base al tipo de contrato
        # en base a ello devuelve el litado de empleados para el historial
        employee_ids=[]
        if ids!='all':
            contract_ids =  self.pool.get('hr.contract').search(cr, uid, [('type_id','=', ids),
                                                                          ('date_start','<=', start_date),
                                                                          '|',('date_end','>', start_date),
                                                                          ('date_end','=', False),                                                                          
                                                                          ], context=context)   
        else:
            contract_ids =  self.pool.get('hr.contract').search(cr, uid, [('date_start','<=', start_date),
                                                                          '|',('date_end','>', start_date),
                                                                          ('date_end','=', False),                                                                          
                                                                          ], context=context)
            
        for obj_contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context):
            employee_ids.append(obj_contract.employee_id.id)
        return employee_ids            

    def create_history(self, cr, uid, ids, context):
        #verifiva los empleados activos para la fecha y crea los historiales correspondientes
        correct_start=False
        for obj in self.browse(cr, uid, ids, context):
            if obj.prev_history:
                if (timedelta(days=1) + datetime.strptime(obj.prev_end_date, "%Y-%m-%d"))== datetime.strptime(obj.start_date, "%Y-%m-%d") :
                    correct_start=True                                                                    
                else:                   
                    raise osv.except_osv(_('Error'), _('Las fechas de FIN del historial anterior y la fecha de INICIO de nuevo historial deben variar exactamente por 1 día'))
            else:
                correct_start=True                
            if correct_start:                               
                if datetime.strptime(obj.start_date, "%Y-%m-%d")<datetime.strptime(obj.end_date, "%Y-%m-%d") :
                    history_ids = self.pool.get('gt.history').search(cr, uid, [('wizard_id','=',obj.id)], context=context)
                    self.pool.get('gt.history').unlink(cr, uid, history_ids)   
                    if obj.prev_history.end_date!=obj.prev_end_date and obj.prev_history:                                                                                                        
                        self.pool.get('gt.wizard.history').write(cr,uid,[obj.prev_history.id],{'end_date':obj.prev_end_date})
                        history_ids = self.pool.get('gt.history').search(cr, uid, [('wizard_id','=',obj.prev_history.id)], context=context) 
                        self.pool.get('gt.history').write(cr,uid,history_ids,{'end_date':obj.prev_end_date})                           
                    if obj.prev_history:
                         self.pool.get('gt.wizard.history').write(cr,uid,[obj.prev_history.id],{'indicted':True})
                    employe_ids=self.employee_x_contract(cr, uid, obj.regime.id,obj.start_date,obj.end_date, context)
                    if employe_ids:                                                     
                        for obj_employee in self.pool.get('hr.employee').browse(cr, uid, employe_ids, context):
                            self.pool.get('gt.history').create(cr,uid, {'name': obj.name_history,
                                                                        'employee_id': obj_employee.id,
                                                                        'start_date': obj.start_date,
                                                                        'wizard_id': obj.id,
                                                                            'end_date': obj.end_date},context=context)
                    else:
                        raise osv.except_osv(_('Error'), _('No existen empleados con contratos activos para la fecha seleccionada'))
                        
                        
                else:
                    raise osv.except_osv(_('Error'), _('La fecha de fin debe ser mayor a la fecha inicial'))
    
    def unlink(self, cr, uid, ids, context=None):
        head = self.read(cr, uid, ids, [], context=context)
        unlink_ids = []
        for s in head:
            if s['state']=='draft':
                history_ids= self.pool.get('gt.history').search(cr, uid, [('wizard_id','=', s['id'])])   
                self.pool.get('gt.history').unlink(cr, uid, history_ids)
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Error'), _('No puede eliminar un historial abierto o cerrado'))   
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    
    def action_activate_history(self, cr, uid, context=None):
        #activa los historiales y de en caso de que exista cierra el historial anterior                
        history_ids= self.pool.get('gt.wizard.history').search(cr, uid, [('state', '=', 'draft'),
                                                                         ('start_date', '=', time.strftime('%Y-%m-%d'))])
        counter_assent=0
        type_assent=''
        for obj_w_history in self.pool.get('gt.wizard.history').browse(cr, uid, history_ids, context):            
            history_ind_ids= self.pool.get('gt.history').search(cr, uid, [('wizard_id', '=', obj_w_history.id)])            
            self.pool.get('gt.history').write(cr,uid,history_ind_ids,{'state':'open'})
            prev_id = obj_w_history.prev_history.id
            if prev_id:                
                history_ind2_ids= self.pool.get('gt.history').search(cr, uid, [('wizard_id', '=', prev_id)])
                for history_ind in self.pool.get('gt.history').browse(cr, uid, history_ind2_ids, context):                   
                    counter_assent=history_ind.counter_assent_acu
                    type_assent=history_ind.type_assent_id_acu.id
                    history_new_id= self.pool.get('gt.history').search(cr, uid, [('wizard_id', '=', obj_w_history.id),
                                                                                 ('employee_id', '=', history_ind.employee_id.id),])
                                        
                    self.pool.get('gt.history').write(cr,uid,history_new_id,{'counter_assent_acu':counter_assent,
                                                                             'type_assent_id_acu':type_assent,
                                                                             'anual_minute':history_ind.anual_minute})                 
                self.pool.get('gt.history').write(cr,uid,history_ind2_ids,{'state':'close'})
                self.pool.get('gt.wizard.history').write(cr,uid,prev_id,{'state':'close'})
            self.pool.get('gt.wizard.history').write(cr,uid,[obj_w_history.id],{'state':'open'})
gt_wizard_history()


class gt_field_workable(osv.osv):
    '''
    Datos laborables
    '''
    _description = 'Datos laborables' 
    _name = 'gt.field.workable'  
    _columns = {'name': fields.integer('Minutos entre marcacion', size=8, required=True),
                'consult': fields.text('Consulta sql', size=64, readonly=True),    
                'body_1': fields.text(''),
                'body_mail': fields.text('Miutos no laborados'), 
                'body_2': fields.char('minutos no laborados', size=64),                
                'start_date': fields.date('Fecha para reproceso'),
                'specific_date': fields.boolean('Fecha específica'),    
                'mail_copy': fields.char('Copia correo', size=128),      
                }     
       
    _defaults = {
        'name': 5,
        'body_1': 'head = ' + ustr(time.strftime('%A,%d de %B del %Y')) + ustr(' \nemployee_id = Nombre del Empleado\nemployee_ci=CI del empleado\ne_mail=Corre  del empleado\nday_event = fecha de acontecimiento\nevent_causes = Causa\ndelay_minutes = Minutos no laborados') ,               
        'consult':"SELECT  NOMINA.NOMINA_COD, ASISTNOW.ASIS_ING, ASISTNOW.ASIS_HORA FROM NOMINA INNER JOIN ASISTNOW ON ASISTNOW.ASIS_ID = NOMINA.NOMINA_ID WHERE ASISTNOW.ASIS_ING >= ' + start + ' AND ASISTNOW.ASIS_ING < ' + end +' ORDER BY ASISTNOW.ASIS_ING ASC",
        'specific_date':False
    } 
    def _check_unique(self, cr, uid, ids, context=None):  
        result=True
        certificate_ = []
        for obj_areas_line in self.browse(cr,uid,ids,context):
            subject_line = self.pool.get('gt.field.workable')
            s_line= subject_line.search(cr, uid, []) 
            if len(s_line) <2:
                result=True
            else:
                result=False
                
        return result

    _constraints = [(_check_unique, 'No puede existir mas de una configuración básica! ', ['name']),]
    def get_hours_less_five(self):       
        start_d = datetime.strptime( str(time.strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        #end= str(datetime.strptime(str(timedelta(hours=-5) + start_d), "%Y-%m-%d %H:%M:%S"))        
        end= str(datetime.strptime(str(timedelta(hours=+0) + start_d), "%Y-%m-%d %H:%M:%S"))
        return end    
    
        
    
    def sql_conecc(self, cr, uid,text_log,start,end, context=None):
        #try:
        import pyodbc
        conn = pyodbc.connect('DRIVER={FreeTDS};PORT=1433;SERVER=170.17.0.103;DATABASE=ONLYCONTROL;UID=open_erp;PWD=openerp;')
        cur = conn.cursor()
        #except:
        #    raise osv.except_osv(_('Error!'), _('Falló conexión con servidor de Base de datos. IP 170.17.0.103'))        
        #import pymssql
        #conn = pymssql.connect(host='170.17.0.103:1433',user='open_erp',password='openerp',database='ONLYCONTROL')
        #cur = conn.cursor()         
        text_log =text_log + 'Conexion establecida: '+ str(self.get_hours_less_five()) + '\n'                                                              
        cur.execute("SELECT  NOMINA.NOMINA_COD, ASISTNOW.ASIS_ING, ASISTNOW.ASIS_ZONA, ASISTNOW.ASIS_HORA, ASISTNOW.ASIS_NOVEDAD \
                    FROM NOMINA INNER JOIN ASISTNOW ON ASISTNOW.ASIS_ID = NOMINA.NOMINA_ID \
                    WHERE ASISTNOW.ASIS_ING < '" + end +"' AND ASISTNOW.ASIS_ING >= '" + start +"' AND ASISTNOW.ASIS_NOVEDAD ='1' ORDER BY ASISTNOW.ASIS_ING ASC")
                    #WHERE NOMINA.NOMINA_COD ='0101879658' and ASISTNOW.ASIS_ING < '" + end +"' AND ASISTNOW.ASIS_ING >= '" + start +"' AND ASISTNOW.ASIS_NOVEDAD ='1' ORDER BY ASISTNOW.ASIS_ING ASC")                                  
        return[cur.fetchall(),text_log]
    def close_sql_conecc(self, cr, uid, context=None):
        import pyodbc
        conn = pyodbc.connect('DRIVER={FreeTDS};PORT=1433;SERVER=170.17.0.103;DATABASE=ONLYCONTROL;UID=open_erp;PWD=openerp;')
        conn.commit()
        conn.close

    def create_event_button(self, cr, uid, context=None):
        res={}
        start=no_schedule=text_log=''
        number_marcs=0
        semana = {'lunes':0 , 'monday': 0, 'Monday': 0,
                      'martes':1 , 'tuesday': 1, 'Tuesday': 1, 
                      'miércoles':2 , 'wednesday': 2, 'miercoles':2, 'Wednesday': 2,
                      'jueves':3 , 'thursday': 3,  'Thursday': 3,
                      'viernes':4 , 'friday': 4,  'Friday': 4,
                      'sabado':5 , 'saturday': 5, 'sábado':5,  'Saturday':5,
                      'domingo':6 , 'sunday': 6, 'sunday': 6}     
        configuration_ids =  self.pool.get('gt.field.workable').search(cr, uid, [], context=context)
        if configuration_ids:          
            for obj_configuration in self.pool.get('gt.field.workable').browse(cr, uid, configuration_ids, context):
                today_=str(self.get_hours_less_five())
                today__ = datetime.strptime(str(today_), "%Y-%m-%d %H:%M:%S")
                date_selected = today__.strftime("%Y-%m-%d")
                if obj_configuration.start_date == date_selected:                    
                    raise osv.except_osv(_('Error!'), _('La fecha para reprocesamiento debe ser anterior a la fecha actual'))
                else:                    
                    try:    
                        start_s = datetime.strptime(str(obj_configuration.start_date), "%Y-%m-%d")                                             
                        try:
                            start_d = datetime.strptime(str(obj_configuration.start_date), "%Y-%m-%d")
                            start=str(start_d)
                            minutes_before=int(obj_configuration.name) 
                            end= str(datetime.strptime(str(timedelta(days=1) + start_d), "%Y-%m-%d %H:%M:%S"))
                        except:
                            raise osv.except_osv(_('Error!'), _('Error en lectura de fecha'))
                    except:
                        pass 
        no_schedule=''
        text_log ='INICIA PROCESO DE LECTURA DE MARCACIONES \n'
        log_id = self.pool.get('gt.process.log').create(cr,uid, {'result': text_log,},context=context)
        sql_information= self.sql_conecc(cr, uid,text_log,start,end, context=None)
        row=sql_information[0]
        text_log=sql_information[1]
        self.pool.get('gt.process.log').write(cr,uid,log_id,{'result':text_log})
        record_numbers_log= len(row)  
        text_log = text_log +'Fecha mayor a:  '+ str(start)+'  Fecha menor o igual a:' + str(end) + '\n'    
        text_log = text_log +  'Lectura de ' + str(record_numbers_log) + ' registros desde la base de datos :' + str(self.get_hours_less_five()) + '\n'        
        if row:     
            text_log = text_log +  'Inicia procesamiento de datos :' + str(self.get_hours_less_five()) + '\n'        
            to_date_log= start
            self.pool.get('gt.process.log').write(cr,uid,[log_id],{'records_number':record_numbers_log,
                                                                          'result':text_log,
                                                                          'date_process':to_date_log}) 
            minutes_before=0
            #employees_ids = self.pool.get('gt.wizard.history').employee_x_contract(cr, uid,'all',start,end, context) 
            #employees_ids = self.pool.get('hr.employee').search(cr, uid, [],context = context)#('ci','=','0102255098
            #import pdb
            #pdb.set_trace()
            employees_ids = self.pool.get('gt.wizard.history').employee_x_contract(cr, uid,'all',start,end, context)                                   
            for obj_employee in self.pool.get('hr.employee').browse(cr, uid, employees_ids, context):
                history_ids =  self.pool.get('gt.history').search(cr, uid, [('employee_id', '=', obj_employee.id),
                                                                           ('state', '=', 'open')
                                                                           ], context=context)
                try:
                    history_id_=history_ids[0]                       
                except:
                    history_id_=''
                procesado=False  
                rows_all = row         
                marcs=[] 
                rows=''
                time_eval=0    
                for rows in rows_all:                      
                    ci_employee= rows[0]
                    h_regist= rows[1]
                    if obj_employee.name == ci_employee:                             
                        if time_eval==0:  
                            if  rows[4] == '1' or not rows[4]:                                                       
                                time_eval= + timedelta(minutes=minutes_before) + h_regist                                                 
                                marcs.append(rows)
                            else:
                                procesado=True  
                        else:                                                                                          
                            if h_regist > time_eval:
                                if rows[4] == '1' or not rows[4]:
                                    marcs.append(rows)
                                else:
                                    procesado=True
                            else:
                                #VERIFICA QUE ENTRE MARCACIONES EXISTA EL TIEMPO MINIMO REQUERIDO                               
                                new_date=  h_regist
                                h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S") 
                                self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                               'employee_id':obj_employee.id,
                                                                               'indicted':False,
                                                                               'action_type':'invalid',
                                                                               'history_id':history_id_,
                                                                               'not_normal':False,
                                                                               'date_dbo':h_regist,                                                                                                                                                      
                                                                               'notes': 'Marcacion invalida',
                                                                               'action':'action'},context=context)                                                       
                            time_eval= + timedelta(minutes=minutes_before) + h_regist
                if  marcs == []:                    
                    if obj_employee.contract_id.marc_employee==True:
                        calendar_ids = self.pool.get('resource.calendar.attendance').search(cr, uid, [('dayofweek', '=', semana[h_regist.strftime("%A")] ),
                                                                                                      ('calendar_id','=',obj_employee.contract_id.work_id.id),
                                                                                                      ], context=context)     
                        if not procesado and calendar_ids:
                            start_d_ = datetime.strptime(str(start), "%Y-%m-%d %H:%M:%S")                            
                            end_= str(datetime.strptime(str(timedelta(hours=0) + start_d_), "%Y-%m-%d %H:%M:%S"))
                            att_id =self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                               'employee_id':obj_employee.id,
                                                                               'indicted':False,
                                                                               'action_type':'notice',
                                                                               'history_id':history_id_,
                                                                               'not_normal':False,
                                                                               'date_dbo':'',
                                                                               'date_spetial': datetime.strptime(str(end_), "%Y-%m-%d %H:%M:%S"),
                                                                               'body':'No registra Marcaciones  :' + str(start),
                                                                               'notes': 'Inconsistencia del Sistema',
                                                                               'action':'action'},context=context)
                else:
                    #print '**********************************************'
                    #print obj_employee.complete_name
                    calendar_ids = self.pool.get('resource.calendar.attendance').search(cr, uid, [('dayofweek', '=', str(semana[h_regist.strftime("%A")]) ),
                                                                                                      ('calendar_id','=',obj_employee.contract_id.work_id.id),
                                                                                                      ], context=context)
                    if not calendar_ids:
                        no_schedule= 'Marcacion registrada para dia fuera de horario',
                    h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")                    
                    number_marcs =verify_marc_day(self, cr, uid,obj_employee.id,h_regist,context)
                    #MARCACIONES NORMALES PARA HORARIO                              
                     
                    if int(len(marcs))==int(number_marcs):     
                                   
                        Array_marcs=[]                       
                        for obj_marc in marcs:                            
                            h_register_ = datetime.strptime(str(obj_marc[1]), "%Y-%m-%d %H:%M:%S")
                            #new_date= + timedelta(hours=5) + h_register_
                            new_date= h_register_
                            h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                            #print 'PARA VERIFICAR HORA'     
                            #print h_register                                        
                            id_marcs = self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                   'employee_id':obj_employee.id,
                                                                                   'indicted':False,
                                                                                   'action':'sign_in',
                                                                                   'action_type':'marc',
                                                                                   'not_normal':False,
                                                                                   'history_id':history_id_,
                                                                                   'date_dbo':obj_marc[1],
                                                                                   'date_spetial':h_register,
                                                                                   'notes': no_schedule,
                                                                                   #'address':obj_marc[2],
                                                                                   'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,obj_marc[2],context=None),
                                                                                   'action':'sign_in'},context=context)               
                    else:  
                        if (len(marcs) % 2) != 0:
                            h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")
                            
                            body='Numero impar de marcaciones             DIA:'+ str(start) +'\n              Listado de Marcaciones \n'
                            for marc in marcs:
                                body= body + '\nMarcacion:  '+ str(marc[1])      
                                         
                            att_id=self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                           'employee_id':obj_employee.id,
                                                                           'indicted':False,
                                                                           'date_dbo':marc[1],
                                                                           'action_type':'notice',
                                                                           'history_id':history_id_,
                                                                           'date_spetial':marc[1],
                                                                           'not_normal':False,
                                                                           #'address':marc[2],
                                                                           'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                           'body':body,
                                                                           'notes': 'Inconsistencia del Sistema - ' + ustr(no_schedule),
                                                                           'action':'action'},context=context)
                            for marc in marcs:
                                if calendar_ids: 
                                    h_register_ = datetime.strptime(str(marc[1]), "%Y-%m-%d %H:%M:%S")
                                    #new_date= + timedelta(hours=5) + h_register_   
                                    new_date=  h_register_
                                    h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                                    self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                   'employee_id':obj_employee.id,
                                                                                   'indicted':False,
                                                                                   'action_type':'inconsistency',
                                                                                   'not_normal':False,
                                                                                   'history_id':history_id_,
                                                                                   'attendance_id':att_id,
                                                                                   'date_dbo':marc[1],
                                                                                   'date_spetial':h_register,
                                                                                   'notes': no_schedule,
                                                                                   #'address':marc[2],
                                                                                   'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                                   'action':'action'},context=context)
                        else:
                            extra_mars =verify_marcs_day(self, cr, uid,obj_employee.id,h_regist,context)
                            if extra_mars=='same':
                                h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")                
                                body=ustr('Número de marcaciones inconsistente             DIA:')+ str(start) +'\nDebe registrar '+ str(len(marcs)) + ' marcaciones.\n              Listado de Marcaciones \n'
                                for marc in marcs:
                                    body= body + '\nMarcacion:  '+ str(marc[1])  
                                h_register_ = datetime.strptime(str(marc[1]), "%Y-%m-%d %H:%M:%S")
                                #new_date= + timedelta(hours=5) + h_regist_
                                new_date= h_regist_
                                h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                                att_id =self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                               'employee_id':obj_employee.id,
                                                                               'indicted':False,
                                                                               'action_type':'notice',
                                                                               'not_normal':False,
                                                                               'date_dbo':marc[1],
                                                                               'history_id':history_id_,
                                                                               'date_spetial':h_register,
                                                                               'body':body,
                                                                               'notes': 'Inconsistencia del Sistema - ' + ustr(no_schedule),
                                                                               'action':'action'},context=context)
                                for marc in marcs: 
                                    h_register_ = datetime.strptime(str(marc[1]), "%Y-%m-%d %H:%M:%S")
                                    #new_date= + timedelta(hours=5) + h_register_
                                    new_date= h_register_
                                    h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                                    self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                               'employee_id':obj_employee.id,
                                                                               'indicted':False,
                                                                               'action_type':'inconsistency',
                                                                               'not_normal':False,
                                                                               'attendance_id':att_id,
                                                                               'date_dbo':ustr(marc[1]),
                                                                               'history_id':int(history_id_),
                                                                               'date_spetial':h_register,
                                                                               'notes': ustr(no_schedule),
                                                                               #'address':marc[2],
                                                                               'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                               'action':'action'},context=context)
                            else:
                                exact_marc= number_marcs + (extra_mars)
                                if exact_marc == len(marcs):  
                                    for obj_marc in marcs:    
                                        
                                        h_register_ = datetime.strptime(str(obj_marc[1]), "%Y-%m-%d %H:%M:%S")
                                        #new_date= + timedelta(hours=5) + h_regist
                                        new_date= h_regist
                                        h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")                        
                                        self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                   'employee_id':obj_employee.id,
                                                                                   'indicted':False,
                                                                                   'action_type':'marc',
                                                                                   'not_normal':False,
                                                                                   'history_id':history_id_,
                                                                                   #'address':obj_marc[2],
                                                                                   'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,obj_marc[2],context=None),
                                                                                   'notes': no_schedule,
                                                                                   'date_dbo':str(obj_marc[1]),
                                                                                   'date_spetial':h_register,
                                                                                   'action':'sign_in'},context=context)  
                                else:
                                    h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")                            
                                    body='DIA:'+ str(start) +ustr('\n              Listado de Marcaciones \n')
                                    for marc in marcs:
                                        body= body + ustr('\nMarcacion:  ')+ str(marc[1])                    
                                    att_id=self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                   'employee_id':obj_employee.id,
                                                                                   'indicted':False,
                                                                                   'date_dbo':marc[1],
                                           'date_spetial':marc[1],
                                                                                   'action_type':'notice',
                                                                                   'history_id':history_id_,
                                                                                   'not_normal':False,
                                                                                   #'address':marc[2],
                                                                                   'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                                   'body':body,
                                                                                   'notes': 'Inconsistencia del Sistema - ' + ustr(no_schedule),
                                                                                   'action':'action'},context=context)
                                    for marc in marcs: 
                                        h_register_ = datetime.strptime(str(marc[1]), "%Y-%m-%d %H:%M:%S")
                                        #new_date= + timedelta(hours=5) + h_register_   
                                        new_date= h_register_
                                        h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                                        self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                       'employee_id':obj_employee.id,
                                                                                       'indicted':False,
                                                                                       'action_type':'inconsistency',
                                                                                       'not_normal':False,
                                                                                       'history_id':history_id_,
                                                                                       'attendance_id':att_id,
                                                                                       'date_dbo':marc[1],
                                                                                       'date_spetial':h_register,
                                                                                       'notes': no_schedule,
                                                                                       #'address':marc[2],
                                                                                       'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                                       'action':'action'},context=context)                                                        
            
            #cur.execute("UPDATE [ONLYCONTROL].[dbo].[ASISTNOW] SET ASIS_NOVEDAD = '1'\
            #WHERE ASISTNOW.ASIS_ING < '" + end +"' AND ASISTNOW.ASIS_ING >= '" + start +"' ")
            text_log = text_log +  'Termina procesamiento de informacion :' + ustr(self.get_hours_less_five()) + '\n' 
            self.pool.get('gt.process.log').write(cr,uid,[log_id],{'result':text_log})           
            self.close_sql_conecc(cr, uid, context=None)
            text_log = text_log +  ustr('Se cierra la conexión con la db :') + ustr(self.get_hours_less_five()) + '\n'
            self.pool.get('gt.process.log').write(cr,uid,[log_id],{'result':text_log}) 
        else:
            text_log = text_log +  ustr('No se registra marcaciones para la fecha.\nSe cierra la conexión con la db :') + ustr(self.get_hours_less_five())+ '\n'
            self.pool.get('gt.process.log').write(cr,uid,[log_id],{'result':text_log})        
        return res    
    def create_from_button_(self, cr, uid,ids, context=None): 
        self.create_event_button( cr, uid, context) 
        
    def create_event(self, cr, uid, context=None):
        res={}
        start=no_schedule=''
        number_marcs=0
        semana = {'lunes':0 , 'monday': 0, 'Monday': 0,
                      'martes':1 , 'tuesday': 1, 'Tuesday': 1, 
                      'miércoles':2 , 'wednesday': 2, 'miercoles':2, 'Wednesday': 2,
                      'jueves':3 , 'thursday': 3,  'Thursday': 3,
                      'viernes':4 , 'friday': 4,  'Friday': 4,
                      'sabado':5 , 'saturday': 5, 'sábado':5,  'Saturday':5,
                      'domingo':6 , 'sunday': 6, 'sunday': 6}     
        
        text_log ='INICIA PROCESO DE LECTURA DE MARCACIONES \n'
        log_id = self.pool.get('gt.process.log').create(cr,uid, {'result': text_log,},context=context)
        import pyodbc
        conn = pyodbc.connect('DRIVER={FreeTDS};PORT=1433;SERVER=170.17.0.103;DATABASE=ONLYCONTROL;UID=open_erp;PWD=openerp;')
        cur = conn.cursor()  
        #import pymssql
        #conn = pymssql.connect(host='170.17.0.103:1433',user='open_erp',password='openerp',database='ONLYCONTROL')
        #cur = conn.cursor()         
        text_log =text_log + 'Conexion establecida: '+ str(self.get_hours_less_five()) + '\n'
        self.pool.get('gt.process.log').write(cr,uid,log_id,{'result':text_log})                      
        start_real =str(self.get_hours_less_five())
        h_regist = datetime.strptime(str(start_real), "%Y-%m-%d %H:%M:%S")
        start = h_regist.strftime("%Y-%m-%d")            
        start_d = datetime.strptime(str(h_regist.strftime("%Y-%m-%d")), "%Y-%m-%d")
        start=str(start_d)
        end= str(datetime.strptime(str(timedelta(days=1) + start_d), "%Y-%m-%d %H:%M:%S"))  
        cur.execute("SELECT  NOMINA.NOMINA_COD, ASISTNOW.ASIS_ING, ASISTNOW.ASIS_ZONA, ASISTNOW.ASIS_HORA, ASISTNOW.ASIS_NOVEDAD \
                    FROM NOMINA INNER JOIN ASISTNOW ON ASISTNOW.ASIS_ID = NOMINA.NOMINA_ID \
                    WHERE ASISTNOW.ASIS_ING < '" + end +"' AND ASISTNOW.ASIS_ING >= '" + start +"' AND ASISTNOW.ASIS_NOVEDAD IS NULL ORDER BY ASISTNOW.ASIS_ING ASC")                                           
        row = cur.fetchall()  
        record_numbers_log= len(row)  
        text_log = text_log +'Fecha mayor a:  '+ str(start)+'  Fecha menor o igual a:' + str(end) + '\n'    
        text_log = text_log +  'Lectura de ' + str(record_numbers_log) + ' registros desde la base de datos :' + str(self.get_hours_less_five()) + '\n'        
        if row:     
            text_log = text_log +  'Inicia procesamiento de datos :' + str(self.get_hours_less_five()) + '\n'        
            to_date_log= start
            self.pool.get('gt.process.log').write(cr,uid,[log_id],{'records_number':record_numbers_log,
                                                                          'result':text_log,
                                                                          'date_process':to_date_log}) 
            minutes_before=0
            #employees_ids = self.pool.get('gt.wizard.history').employee_x_contract(cr, uid,'all',start,end, context) 
            employees_ids = self.pool.get('hr.employee').search(cr, uid, [],context = context)#('ci','=','0102255098')                                   
            for obj_employee in self.pool.get('hr.employee').browse(cr, uid, employees_ids, context):
                history_ids =  self.pool.get('gt.history').search(cr, uid, [('employee_id', '=', obj_employee.id),
                                                                           ('state', '=', 'open')
                                                                           ], context=context)
                try:
                    history_id_=history_ids[0]                       
                except:
                    history_id_=''
                procesado=False  
                rows_all = row         
                marcs=[] 
                rows=''
                time_eval=0    
                for rows in rows_all:                      
                    ci_employee= rows[0]
                    h_regist= rows[1]
                    if obj_employee.name == ci_employee:                             
                        if time_eval==0:  
                            if  rows[4] == '1' or not rows[4]:                                                       
                                time_eval= + timedelta(minutes=minutes_before) + h_regist                                                 
                                marcs.append(rows)
                            else:
                                procesado=True  
                        else:                                                                                          
                            if h_regist > time_eval:
                                if rows[4] == '1' or not rows[4]:
                                    marcs.append(rows)
                                else:
                                    procesado=True
                            else:
                                #VERIFICA QUE ENTRE MARCACIONES EXISTA EL TIEMPO MINIMO REQUERIDO                               
                                new_date=  h_regist
                                h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S") 
                                self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                               'employee_id':obj_employee.id,
                                                                               'indicted':False,
                                                                               'action_type':'invalid',
                                                                               'history_id':history_id_,
                                                                               'not_normal':False,
                                                                               'date_dbo':h_regist,                                                                                                                                                      
                                                                               'notes': 'Marcacion invalida',
                                                                               'action':'action'},context=context)                                                       
                            time_eval= + timedelta(minutes=minutes_before) + h_regist
                if  marcs == []:                    
                    if obj_employee.contract_id.marc_employee==True:
                        calendar_ids = self.pool.get('resource.calendar.attendance').search(cr, uid, [('dayofweek', '=', semana[h_regist.strftime("%A")] ),
                                                                                                      ('calendar_id','=',obj_employee.contract_id.work_id.id),
                                                                                                      ], context=context)     
                        if not procesado and calendar_ids:
                            start_d_ = datetime.strptime(str(start), "%Y-%m-%d %H:%M:%S")                            
                            end_= str(datetime.strptime(str(timedelta(hours=0) + start_d_), "%Y-%m-%d %H:%M:%S"))
                            att_id =self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                               'employee_id':obj_employee.id,
                                                                               'indicted':False,
                                                                               'action_type':'notice',
                                                                               'history_id':history_id_,
                                                                               'not_normal':False,
                                                                               'date_dbo':'',
                                                                               'date_spetial': datetime.strptime(str(end_), "%Y-%m-%d %H:%M:%S"),
                                                                               'body':'No registra Marcaciones  :' + str(start),
                                                                               'notes': 'Inconsistencia del Sistema',
                                                                               'action':'action'},context=context)
                else:
                    calendar_ids = self.pool.get('resource.calendar.attendance').search(cr, uid, [('dayofweek', '=', str(semana[h_regist.strftime("%A")]) ),
                                                                                                      ('calendar_id','=',obj_employee.contract_id.work_id.id),
                                                                                                      ], context=context)
                    if not calendar_ids:
                        no_schedule= 'Marcacion registrada para dia fuera de horario',
                    h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")                    
                    number_marcs =verify_marc_day(self, cr, uid,obj_employee.id,h_regist,context)
                    #MARCACIONES NORMALES PARA HORARIO                              
                     
                    if int(len(marcs))==int(number_marcs):     
                                   
                        Array_marcs=[]                       
                        for obj_marc in marcs:                            
                            h_register_ = datetime.strptime(str(obj_marc[1]), "%Y-%m-%d %H:%M:%S")
                            #new_date= + timedelta(hours=5) + h_register_
                            new_date= h_register_
                            h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                            #print 'PARA VERIFICAR HORA'     
                            #print h_register                                        
                            id_marcs = self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                   'employee_id':obj_employee.id,
                                                                                   'indicted':False,
                                                                                   'action':'sign_in',
                                                                                   'action_type':'marc',
                                                                                   'not_normal':False,
                                                                                   'history_id':history_id_,
                                                                                   'date_dbo':obj_marc[1],
                                                                                   'date_spetial':h_register,
                                                                                   'notes': no_schedule,
                                                                                   #'address':obj_marc[2],
                                                                                   'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,obj_marc[2],context=None),
                                                                                   'action':'sign_in'},context=context)               
                    else:  
                        if (len(marcs) % 2) != 0:
                            h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")
                            
                            body='Numero impar de marcaciones             DIA:'+ str(start) +'\n              Listado de Marcaciones \n'
                            for marc in marcs:
                                body= body + '\nMarcacion:  '+ str(marc[1])      
                                         
                            att_id=self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                           'employee_id':obj_employee.id,
                                                                           'indicted':False,
                                                                           'date_dbo':marc[1],
                                                                           'action_type':'notice',
                                                                           'history_id':history_id_,
                                                                           'date_spetial':marc[1],
                                                                           'not_normal':False,
                                                                           #'address':marc[2],
                                                                           'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                           'body':body,
                                                                           'notes': 'Inconsistencia del Sistema - ' + ustr(no_schedule),
                                                                           'action':'action'},context=context)
                            for marc in marcs:
                                if calendar_ids: 
                                    h_register_ = datetime.strptime(str(marc[1]), "%Y-%m-%d %H:%M:%S")
                                    #new_date= + timedelta(hours=5) + h_register_   
                                    new_date=  h_register_
                                    h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                                    self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                   'employee_id':obj_employee.id,
                                                                                   'indicted':False,
                                                                                   'action_type':'inconsistency',
                                                                                   'not_normal':False,
                                                                                   'history_id':history_id_,
                                                                                   'attendance_id':att_id,
                                                                                   'date_dbo':marc[1],
                                                                                   'date_spetial':h_register,
                                                                                   'notes': no_schedule,
                                                                                   #'address':marc[2],
                                                                                   'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                                   'action':'action'},context=context)
                        else:
                            extra_mars =verify_marcs_day(self, cr, uid,obj_employee.id,h_regist,context)
                            if extra_mars=='same':
                                h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")                
                                body=ustr('Número de marcaciones inconsistente             DIA:')+ str(start) +'\nDebe registrar '+ str(len(marcs)) + ' marcaciones.\n              Listado de Marcaciones \n'
                                for marc in marcs:
                                    body= body + '\nMarcacion:  '+ str(marc[1])  
                                h_register_ = datetime.strptime(str(marc[1]), "%Y-%m-%d %H:%M:%S")
                                #new_date= + timedelta(hours=5) + h_regist_
                                new_date= h_regist_
                                h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                                att_id =self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                               'employee_id':obj_employee.id,
                                                                               'indicted':False,
                                                                               'action_type':'notice',
                                                                               'not_normal':False,
                                                                               'date_dbo':marc[1],
                                                                               'history_id':history_id_,
                                                                               'date_spetial':h_register,
                                                                               'body':body,
                                                                               'notes': 'Inconsistencia del Sistema - ' + ustr(no_schedule),
                                                                               'action':'action'},context=context)
                                for marc in marcs: 
                                    h_register_ = datetime.strptime(str(marc[1]), "%Y-%m-%d %H:%M:%S")
                                    #new_date= + timedelta(hours=5) + h_register_
                                    new_date= h_register_
                                    h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                                    self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                               'employee_id':obj_employee.id,
                                                                               'indicted':False,
                                                                               'action_type':'inconsistency',
                                                                               'not_normal':False,
                                                                               'attendance_id':att_id,
                                                                               'date_dbo':ustr(marc[1]),
                                                                               'history_id':int(history_id_),
                                                                               'date_spetial':h_register,
                                                                               'notes': ustr(no_schedule),
                                                                               #'address':marc[2],
                                                                               'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                               'action':'action'},context=context)
                            else:
                                exact_marc= number_marcs + (extra_mars)
                                if exact_marc == len(marcs):  
                                    for obj_marc in marcs:    
                                        
                                        h_register_ = datetime.strptime(str(obj_marc[1]), "%Y-%m-%d %H:%M:%S")
                                        #new_date= + timedelta(hours=5) + h_regist
                                        new_date= h_regist
                                        h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")                        
                                        self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                   'employee_id':obj_employee.id,
                                                                                   'indicted':False,
                                                                                   'action_type':'marc',
                                                                                   'not_normal':False,
                                                                                   'history_id':history_id_,
                                                                                   #'address':obj_marc[2],
                                                                                   'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,obj_marc[2],context=None),
                                                                                   'notes': no_schedule,
                                                                                   'date_dbo':str(obj_marc[1]),
                                                                                   'date_spetial':h_register,
                                                                                   'action':'sign_in'},context=context)  
                                else:
                                    h_regist = datetime.strptime(str(h_regist), "%Y-%m-%d %H:%M:%S")                            
                                    body='DIA:'+ str(start) +ustr('\n              Listado de Marcaciones \n')
                                    for marc in marcs:
                                        body= body + ustr('\nMarcacion:  ')+ str(marc[1])                    
                                    att_id=self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                   'employee_id':obj_employee.id,
                                                                                   'indicted':False,
                                                                                   'date_dbo':marc[1],
                                           'date_spetial':marc[1],
                                                                                   'action_type':'notice',
                                                                                   'history_id':history_id_,
                                                                                   'not_normal':False,
                                                                                   #'address':marc[2],
                                                                                   'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                                   'body':body,
                                                                                   'notes': 'Inconsistencia del Sistema - ' + ustr(no_schedule),
                                                                                   'action':'action'},context=context)
                                    for marc in marcs: 
                                        h_register_ = datetime.strptime(str(marc[1]), "%Y-%m-%d %H:%M:%S")
                                        #new_date= + timedelta(hours=5) + h_register_   
                                        new_date= h_register_
                                        h_register = datetime.strptime(str(new_date), "%Y-%m-%d %H:%M:%S")
                                        self.pool.get('hr.attendance').create(cr,uid, {'state':'draft',
                                                                                       'employee_id':obj_employee.id,
                                                                                       'indicted':False,
                                                                                       'action_type':'inconsistency',
                                                                                       'not_normal':False,
                                                                                       'history_id':history_id_,
                                                                                       'attendance_id':att_id,
                                                                                       'date_dbo':marc[1],
                                                                                       'date_spetial':h_register,
                                                                                       'notes': no_schedule,
                                                                                       #'address':marc[2],
                                                                                       'address':self.pool.get('gt.clock.name')._clock_get(cr, uid,marc[2],context=None),
                                                                                       'action':'action'},context=context)                                                        
            
            #cur.execute("UPDATE [ONLYCONTROL].[dbo].[ASISTNOW] SET ASIS_NOVEDAD = '1'\
            #WHERE ASISTNOW.ASIS_ING < '" + end +"' AND ASISTNOW.ASIS_ING >= '" + start +"' ")
            text_log = text_log +  'Termina procesamiento de informacion :' + ustr(self.get_hours_less_five()) + '\n' 
            self.pool.get('gt.process.log').write(cr,uid,[log_id],{'result':text_log})           
            self.close_sql_conecc(cr, uid, context=None)
            text_log = text_log +  ustr('Se cierra la conexión con la db :') + ustr(self.get_hours_less_five()) + '\n'
            self.pool.get('gt.process.log').write(cr,uid,[log_id],{'result':text_log}) 
        else:
            text_log = text_log +  ustr('No se registra marcaciones para la fecha.\nSe cierra la conexión con la db :') + ustr(self.get_hours_less_five())+ '\n'
            self.pool.get('gt.process.log').write(cr,uid,[log_id],{'result':text_log})        
        return res
                      
gt_field_workable()

class academic_hr_employee_inherit(osv.osv):
    '''
    HERENCIA EMPLEADO - AGREGAR CAMPO 
    '''
    _inherit = "hr.employee"    
    _columns = {
                'history_ids' : fields.one2many('gt.history','employee_id','Historial',
                                                  readonly=True, ondelete='cascade'),
                'event_ids' : fields.one2many('hr.attendance','employee_id','Eventos'),                
    }    
academic_hr_employee_inherit()

class gt_process_log(osv.osv):
    '''
    contiene un log de las fechas que se ha procesado la informacion
    el total de registros procesados
    hora de inicio
    hora de fin 
    '''
    _description ="Log de procesamiento"
    _name = "gt.process.log"    
    _columns = {
                 'name': fields.datetime('Fecha que corre el proceso', required=True, select=1),
                 'date_process': fields.datetime('Fecha que se quiere procesar', select=1),
                 'records_number': fields.integer('Número de registros procesados', size=32),
                 'result':  fields.text('Notas', size=64),
                 }
    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), #please don't remove the lambda, if you remove it then the current time will not change     
        'result': ''
    }
gt_process_log()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
