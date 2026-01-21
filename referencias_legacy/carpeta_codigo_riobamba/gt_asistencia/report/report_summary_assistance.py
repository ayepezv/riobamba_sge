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

from osv import fields, osv
from datetime import timedelta
from datetime import datetime
import time
from tools.translate import _

class assistance_summary_line(osv.osv):
    _name = 'assistance.summary.line'
    _order = 'name asc'
    _columns = {
                'name': fields.char('Empleado', size=50),
                'summary_id': fields.many2one('assistance.summary', 'Resumen de Asistencia'),
                'cedula': fields.char('Cedula', size=10),
                'employee_id': fields.many2one('hr.employee', 'Empleado', required=True),
                'date_start': fields.date('Fecha inicial'),
                'date_stop': fields.date('Fecha final'),
                'tiempo_normal': fields.char('H. Normales', size=40),
                'tiempo_trabajado': fields.char('Total H. Trabajadas', size=40),
                'tiempo_real': fields.char('H. Reales', size=40),
                'atrasos': fields.char('Atrasos', size=40),
                'hextra': fields.char('Horas Extra', size=40),
                'faltas': fields.integer('Faltas'),
                }
    
assistance_summary_line()

class assistance_summary(osv.osv):
    _name = 'assistance.summary'
    _columns = {
                'name': fields.char('Descripcion', size=50),
                'date_start': fields.date('Fecha inicial'),
                'date_stop': fields.date('Fecha final'),
		#'date_report': fields.datetime('Fecha del reporte', required=True, select=1),
                'line_ids': fields.one2many('assistance.summary.line', 'summary_id', 'Detalle de Asistencia'),
                }
    _defaults = {
#        'date_report': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), #please don't remove the lambda, if you remove it then the current time will not change     
    }    
    def unlink(self, cr, uid, ids, context=None):
        summary = self.read(cr, uid, ids, [], context=context)
        unlink_ids = []
        for s in summary:
            as_summary = self.pool.get('assistance.summary.line')
            summary_line= as_summary.search(cr, uid, [('summary_id','=', s['id'])])                  
            if summary_line == []:                
                unlink_ids.append(s['id'])
            else:
                self.pool.get('assistance.summary.line').unlink(cr, uid, summary_line)
                unlink_ids.append(s['id'])                   
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    def generar_resumen(self, cr, uid, ids, context=None):
        obj_employee = self.pool.get('hr.employee')
        obj_assistance = self.pool.get('hr.attendance')
        obj_resumen = self.pool.get('assistance.resumen.diario.line')
        obj_linea_resumen = self.pool.get('assistance.summary.line')
        for resumen in self.browse(cr, uid, ids):
            if (timedelta(days=61) + datetime.strptime(resumen.date_start, "%Y-%m-%d")) > datetime.strptime(resumen.date_stop, "%Y-%m-%d"):
                lineas_ids = obj_linea_resumen.search(cr, uid, [('summary_id','=',resumen.id)])
                if lineas_ids:
                    obj_linea_resumen.unlink(cr, uid, lineas_ids)
                employee_ids = obj_employee.search(cr, uid, [])
                for empleado in obj_employee.browse(cr, uid, employee_ids):
                    ids_resumen = obj_resumen.search(cr, uid, [('employee_id', '=', empleado.id),
                                                               ('fecha', '>=', resumen.date_start),
                                                               ('fecha', '<=', resumen.date_stop)])
                    atrasos = [0,0,0]
                    hextra = [0,0,0]
                    tiempo_normal = [0,0,0]
                    tiempo_real = [0,0,0]
                    tiempo_trabajado = [0,0,0]
                    for resumen_diario in obj_resumen.browse(cr, uid, ids_resumen):
                        hora_resumen = resumen_diario.tiempo.split(':')
                        hora_resumen[0] = int(hora_resumen[0])
                        hora_resumen[1] = int(hora_resumen[1])
                        hora_resumen[2] = int(hora_resumen[2])
                        if resumen_diario.name=='atraso':
                            atrasos[0] = atrasos[0] + hora_resumen[0]
                            atrasos[1] = atrasos[1] + hora_resumen[1]
                            atrasos[2] = atrasos[2] + hora_resumen[2]
                        if resumen_diario.name=='hreal':
                            tiempo_real[0] = tiempo_real[0] + hora_resumen[0]
                            tiempo_real[1] = tiempo_real[1] + hora_resumen[1]
                            tiempo_real[2] = tiempo_real[2] + hora_resumen[2]
                        if resumen_diario.name=='trabajado':
                            tiempo_trabajado[0] = tiempo_trabajado[0] + hora_resumen[0]
                            tiempo_trabajado[1] = tiempo_trabajado[1] + hora_resumen[1]
                            tiempo_trabajado[2] = tiempo_trabajado[2] + hora_resumen[2]
                        if resumen_diario.name=='hnormal':
                            tiempo_normal[0] = tiempo_normal[0] + hora_resumen[0]
                            tiempo_normal[1] = tiempo_normal[1] + hora_resumen[1]
                            tiempo_normal[2] = tiempo_normal[2] + hora_resumen[2]
                        if resumen_diario.name=='hextra':
                            hextra[0] = hextra[0] + hora_resumen[0]
                            hextra[1] = hextra[1] + hora_resumen[1]
                            hextra[2] = hextra[2] + hora_resumen[2]
                        while hextra[2]>=60:
                            hextra[1] = hextra[1] + 1
                            hextra[2] = hextra[2] - 60
                        while hextra[1]>=60:
                            hextra[0] = hextra[0] + 1
                            hextra[1] = hextra[1] - 60
                        while tiempo_real[2]>=60:
                            tiempo_real[1] = tiempo_real[1] + 1
                            tiempo_real[2] = tiempo_real[2] - 60
                        while tiempo_real[1]>=60:
                            tiempo_real[0] = tiempo_real[0] + 1
                            tiempo_real[1] = tiempo_real[1] - 60
                        while tiempo_normal[2]>=60:
                            tiempo_normal[1] = tiempo_normal[1] + 1
                            tiempo_normal[2] = tiempo_normal[2] - 60
                        while tiempo_normal[1]>=60:
                            tiempo_normal[0] = tiempo_normal[0] + 1
                            tiempo_normal[1] = tiempo_normal[1] - 60
                        while tiempo_trabajado[2]>=60:
                            tiempo_trabajado[1] = tiempo_trabajado[1] + 1
                            tiempo_trabajado[2] = tiempo_trabajado[2] - 60
                        while tiempo_trabajado[1]>=60:
                            tiempo_trabajado[0] = tiempo_trabajado[0] + 1
                            tiempo_trabajado[1] = tiempo_trabajado[1] - 60
                        while atrasos[2]>=60:
                            atrasos[1] = atrasos[1] + 1
                            atrasos[2] = atrasos[2] - 60
                        while atrasos[1]>=60:
                            atrasos[0] = atrasos[0] + 1
                            atrasos[1] = atrasos[1] - 60
                    id_linea = obj_linea_resumen.create(cr, uid, {'name': empleado.last_name + ' ' + empleado.name,
                                                                  'employee_id': empleado.id,
                                                                  'summary_id': resumen.id,
                                                                  'cedula': empleado.ci,
                                                                  'date_start': resumen.date_start,
                                                                  'date_stop': resumen.date_stop,
                                                                  'tiempo_normal': str(tiempo_normal[0]).rjust(3,'0')+':'+str(tiempo_normal[1]).rjust(2,'0')+':'+str(tiempo_normal[2]).rjust(2,'0'),
                                                                  'tiempo_real': str(tiempo_real[0]).rjust(3,'0')+':'+str(tiempo_real[1]).rjust(2,'0')+':'+str(tiempo_real[2]).rjust(2,'0'),
                                                                  'tiempo_trabajado': str(tiempo_trabajado[0]).rjust(3,'0')+':'+str(tiempo_trabajado[1]).rjust(2,'0')+':'+str(tiempo_trabajado[2]).rjust(2,'0'),
                                                                  'hextra': str(hextra[0]).rjust(3,'0')+':'+str(hextra[1]).rjust(2,'0')+':'+str(hextra[2]).rjust(2,'0'),
                                                                  'atrasos': str(atrasos[0]).rjust(3,'0')+':'+str(atrasos[1]).rjust(2,'0')+':'+str(atrasos[2]).rjust(2,'0'),
                                                                  'faltas':0})
                
            else:
                raise osv.except_osv(_('Error'), _('El rango de fechas máxima permitida para el reporte son 60 días'))                    
                
    
assistance_summary()
