# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-now Gnuthink Software Labs Co. Ltd. (<http://www.gnuthink.com>).
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
import time
import datetime
import pdb

class asistente_calculadora_linea(osv.osv_memory):
    _name = 'calculadora.line'
    _description = 'Linea de costos en viáticos - calculadora'
    _columns = {
                'detalle': fields.char('Detalle', size=50),
                'cantidad': fields.float('Cantidad'),
                'valor': fields.float('Valor'),
                'solicitud_id': fields.many2one('calculadora', 'Solicitud de Viáticos'),
                }
    
    def _validar_mayor_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.valor < 0:
            return False
        if obj.cantidad < 0:
            return False
        return True
    
asistente_calculadora_linea()

class calculadora_destinos(osv.osv_memory):
    _name = 'calculadora.destinos'
    _description = 'Linea de destinos en viaticos - calculadora'
    _columns = {
                'name': fields.selection([('nacional','Nacional'),('internacional','Internacional')], 'Tipo'),
                'ciudad_id': fields.many2one('res.country.state.canton', 'Localidad'),
                'pais_id': fields.many2one('viaticos.zonas.internacional.coeficientes', 'Pais'),
                'ciudad_internacional': fields.char('Ciudad', size=40),
                'fecha_salida': fields.datetime('Desde (fecha y hora)'),
                'fecha_llegada': fields.datetime('Hasta (fecha y hora)'),
                'solicitud_id': fields.many2one('calculadora', 'Solicitud de Viáticos'),
                }
    
    _defaults = {
                 'name': 'nacional',
                 }
    
    def resetear_destinos(self, cr, uid, ids, context={}):
        return {'value':{'pais_id': False,
                         'ciudad_id': False}}
    
    def segundos_a_cero(self, cr, uid, ids, fecha, campo, context=None):
        time_fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
        time_fecha = time_fecha.replace(second=00)
        return {'value':{campo: str(time_fecha)}}

calculadora_destinos()


class asistente_calculadora(osv.osv_memory):
    _name = 'calculadora'
    _description = 'Calculador de viaticos'
    
    def devolver_datos_empleado(self, cr, uid, ids, empleado_id, context=None):
        value = {}
        obj_employee = self.pool.get('hr.employee')
        empleado = obj_employee.browse(cr, uid, empleado_id, context)
        if empleado.job_id:
            value['job_id'] = empleado.job_id.id
            value['department_id'] = empleado.department_id.id
        return {'value': value}
    
    def _calculate_total_solicitud_facturas(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        tabla = self.pool.get('viaticos.tabla').browse(cr, uid, 1, context)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            for detalle in line.detalle_solicitud:
                if detalle.detalle.find(" Nacional") >= 0:
                    res[line.id] = res[line.id] + detalle.valor
            res[line.id] = (res[line.id]/100)*tabla.porcentaje_nacional
        return res
    
    def _calculate_total_informe_facturas(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        tabla = self.pool.get('viaticos.tabla').browse(cr, uid, 1, context)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            for detalle in line.detalle_informe:
                if detalle.detalle.find(" Nacional") >= 0:
                    res[line.id] = res[line.id] + detalle.valor
            res[line.id] = (res[line.id]/100)*tabla.porcentaje_nacional
        return res
    
    def _calculate_total_solicitud(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            for detalle in line.detalle_solicitud:
                res[line.id] = res[line.id] + detalle.valor
        return res
    
    _columns = {
                'department_id': fields.many2one('hr.department', 'Departamento'),
                'employee_id': fields.many2one('hr.employee', 'Servidor'),
                'job_id': fields.many2one('hr.job', 'Cargo'),
                'fecha_salida': fields.datetime('Fecha y hora de salida'),
                'fecha_llegada': fields.datetime('Fecha y hora de llegada'),
                'detalle_solicitud': fields.one2many('calculadora.line', 'solicitud_id', 'Detalle de solicitud'),
                'total_porcentaje_facturas': fields.float('Porcentaje a justificar', help="Porcentaje a justificar mediante facturas por el viatico nacional"),
                'total_solicitud': fields.float('Solicitud - Total ($)'),
                'total_solicitud_facturas': fields.float('Total a justificar ($)', help="Valor a justificar mediante facturas por el viatico nacional, segun informacion de la solicitud"),
                'destinos_solicitud': fields.one2many('calculadora.destinos', 'solicitud_id', 'Destinos de solicitud'),
                }

        
    def fecha_inicio_fin(self, cr, uid, id, context={}):
        resultado = "nada"
        fecha_salida = False
        fecha_llegada = False
        registro = self.browse(cr, uid, id, context)
        if registro.destinos_solicitud:
            for destino in registro.destinos_solicitud:
                if fecha_salida==False:
                    fecha_salida = datetime.datetime.strptime(destino.fecha_salida, "%Y-%m-%d %H:%M:%S")
                fecha_llegada = datetime.datetime.strptime(destino.fecha_llegada, "%Y-%m-%d %H:%M:%S")
            resultado = fecha_llegada - fecha_salida
            if resultado.seconds >= 6*3600:
                resultado = "subsistencia"
            elif resultado.seconds >= 4*3600:
                resultado = "alimentacion"
        self.write(cr, uid, [id], {'fecha_salida': fecha_salida,
                                   'fecha_llegada': fecha_llegada}, context)
        return resultado
    
    def calcular(self, cr, uid, ids, context={}):
        for registro in self.browse(cr, uid, ids, context):
            if self.fecha_inicio_fin(cr, uid, registro.id, context) != "nada":
                self.calcular_detalle(cr, uid, registro.id, context)
        return True
    
    def calcular_detalle(self, cr, uid, id, context={}):
        resultados = []
        lineas = self.pool.get('viaticos.destinos')
        obj_tabla = self.pool.get('viaticos.tabla.line')
        obj_detalle = self.pool.get('calculadora.line')
        registro = self.browse(cr, uid, id, context)
        fecha_salida = datetime.datetime.strptime(registro.fecha_salida, "%Y-%m-%d %H:%M:%S") #DIA Y HORA DE SALIDA
        fecha_llegada = datetime.datetime.strptime(registro.fecha_llegada, "%Y-%m-%d %H:%M:%S") #DIA Y HORA DE RETORNO
        fecha_salida = fecha_salida - datetime.timedelta(hours=5)
        fecha_llegada = fecha_llegada - datetime.timedelta(hours=5)
        #print fecha_llegada
        empleado = registro.employee_id
        nivel = empleado.job_id.nivel_viaticos_id
        if registro.destinos_solicitud:
            bandera=False
            try:
                registros = obj_detalle.search(cr, uid, [('solicitud_id','=',id)])
                obj_detalle.unlink(cr, uid, registros)
            except:
                pass
            fecha_calculo = fecha_salida
            while fecha_calculo<=fecha_llegada:
                fecha_calculo_1 = fecha_calculo + datetime.timedelta(hours=4)
                fecha_calculo_2 = fecha_calculo + datetime.timedelta(hours=6)
                fecha_calculo_3 = fecha_calculo + datetime.timedelta(hours=24)
                fecha_calculo_3 = fecha_calculo_3.replace(hour=8, minute=0, second=0)
                bandera_viatico = False
                if fecha_calculo_3>=fecha_salida and fecha_calculo_3<=fecha_llegada:
                    for destino in registro.destinos_solicitud:
                        fecha_1 = datetime.datetime.strptime(destino.fecha_salida, "%Y-%m-%d %H:%M:%S")
                        fecha_1 = fecha_1 - datetime.timedelta(hours=5)
                        fecha_2 = datetime.datetime.strptime(destino.fecha_llegada, "%Y-%m-%d %H:%M:%S")
                        fecha_2 = fecha_2 - datetime.timedelta(hours=5)
                        if fecha_calculo_3>=fecha_1 and fecha_calculo_3<=fecha_2:
                            if destino.name == 'nacional':
                                id_tabla = obj_tabla.search(cr, uid, [('zona_id','=',destino.ciudad_id.zona_viaticos_id.id),
                                                                      ('nivel_id','=',nivel.id),])
                                try:
                                    id_tabla = obj_tabla.search(cr, uid, [('zona_id','=',destino.ciudad_id.zona_viaticos_id.id),
                                                                      ('nivel_id','=',nivel.id),])
                                except:
                                    raise osv.except_osv('Error', 'No se encuentra configurada la tabla para este cargo y destino, comuniquese con el administrador del sistema')
                                if id_tabla:
                                    for tabla in obj_tabla.browse(cr, uid, id_tabla, context):
                                        ids_detalles = obj_detalle.search(cr, uid, [('solicitud_id','=',id),
                                                                                    ('detalle','like','Viatico - ' + 'Nacional: ' + destino.ciudad_id.name)])
                                        if not ids_detalles:
                                            obj_detalle.create(cr, uid, {'solicitud_id': id,
                                                               'detalle': 'Viatico - ' + 'Nacional: ' + destino.ciudad_id.name,
                                                               'cantidad': 1,
                                                               'valor': tabla.valor_viatico})
                                            bandera=True
                                        else:
                                            registro_detalle = obj_detalle.browse(cr, uid, ids_detalles[0])
                                            obj_detalle.write(cr, uid, [registro_detalle.id], {'cantidad': registro_detalle.cantidad + 1,
                                                                                               'valor': registro_detalle.valor + tabla.valor_viatico})
                            if destino.name == 'internacional':
                                coeficiente = destino.pais_id.coeficiente
                                for nivel_internacional in destino.pais_id.cabecera_id.niveles:
                                    if nivel_internacional.name == nivel:
                                        ids_detalles = obj_detalle.search(cr, uid, [('solicitud_id','=',id),
                                                                                    ('detalle','like','Viatico - ' + 'Internacional: ' + destino.pais_id.name.name)])
                                        if not ids_detalles:
                                            obj_detalle.create(cr, uid, {'solicitud_id': id,
                                                           'detalle': 'Viatico - ' + 'Internacional: ' + destino.pais_id.name.name,
                                                           'cantidad': 1,
                                                           'valor': coeficiente*nivel_internacional.valor_viatico})
                                            bandera=True
                                        else:
                                            registro_detalle = obj_detalle.browse(cr, uid, ids_detalles[0])
                                            obj_detalle.write(cr, uid, [registro_detalle.id], {'cantidad': registro_detalle.cantidad + 1,
                                                                                               'valor': registro_detalle.valor + coeficiente*nivel_internacional.valor_viatico})
                elif fecha_calculo_2>=fecha_salida and fecha_calculo_2<=fecha_llegada:
                    for destino in registro.destinos_solicitud:
                        fecha_1 = datetime.datetime.strptime(destino.fecha_salida, "%Y-%m-%d %H:%M:%S")
                        fecha_1 = fecha_1 - datetime.timedelta(hours=5)
                        fecha_2 = datetime.datetime.strptime(destino.fecha_llegada, "%Y-%m-%d %H:%M:%S")
                        fecha_2 = fecha_2 - datetime.timedelta(hours=5)
                        if fecha_calculo_2>=fecha_1 and fecha_calculo_2<=fecha_2:
                            if destino.name == 'nacional':
                                id_tabla = obj_tabla.search(cr, uid, [('zona_id','=',destino.ciudad_id.zona_viaticos_id.id),
                                                                      ('nivel_id','=',nivel.id),])
                                try:
                                    id_tabla = obj_tabla.search(cr, uid, [('zona_id','=',destino.ciudad_id.zona_viaticos_id.id),
                                                                      ('nivel_id','=',nivel.id),])
                                except:
                                    raise osv.except_osv('Error', 'No se encuentra configurada la tabla para este cargo y destino, comuniquese con el administrador del sistema')
                                if id_tabla:
                                    for tabla in obj_tabla.browse(cr, uid, id_tabla, context):
                                        obj_detalle.create(cr, uid, {'solicitud_id': id,
                                                           'detalle': 'Subsistencia - ' + 'Nacional: ' + destino.ciudad_id.name,
                                                           'cantidad': 1,
                                                           'valor': tabla.valor_subsistencia})
                                        bandera=True
                            if destino.name == 'internacional':
                                coeficiente = destino.pais_id.coeficiente
                                for nivel_internacional in destino.pais_id.cabecera_id.niveles:
                                    if nivel_internacional.name == nivel:
                                        obj_detalle.create(cr, uid, {'solicitud_id': id,
                                                           'detalle': 'Subsistencia - ' + 'Internacional: ' + destino.pais_id.name.name,
                                                           'cantidad': 1,
                                                           'valor': coeficiente*nivel_internacional.valor_subsistencia})
                                        bandera=True
                elif fecha_calculo_1>=fecha_salida and fecha_calculo_1<=fecha_llegada:
                    for destino in registro.destinos_solicitud:
                        fecha_1 = datetime.datetime.strptime(destino.fecha_salida, "%Y-%m-%d %H:%M:%S")
                        fecha_1 = fecha_1 - datetime.timedelta(hours=5)
                        fecha_2 = datetime.datetime.strptime(destino.fecha_llegada, "%Y-%m-%d %H:%M:%S")
                        fecha_2 = fecha_2 - datetime.timedelta(hours=5)
                        if fecha_calculo_1>=fecha_1 and fecha_calculo_1<=fecha_2:
                            if destino.name == 'nacional':
                                id_tabla = obj_tabla.search(cr, uid, [('zona_id','=',destino.ciudad_id.zona_viaticos_id.id),
                                                                      ('nivel_id','=',nivel.id),])
                                try:
                                    id_tabla = obj_tabla.search(cr, uid, [('zona_id','=',destino.ciudad_id.zona_viaticos_id.id),
                                                                      ('nivel_id','=',nivel.id),])
                                except:
                                    raise osv.except_osv('Error', 'No se encuentra configurada la tabla para este cargo y destino, comuniquese con el administrador del sistema')
                                if id_tabla:
                                    for tabla in obj_tabla.browse(cr, uid, id_tabla, context):
                                        obj_detalle.create(cr, uid, {'solicitud_id': id,
                                                           'detalle': 'Alimentacion - ' + 'Nacional: ' + destino.ciudad_id.name,
                                                           'cantidad': 1,
                                                           'valor': tabla.valor_alimentacion})
                                        bandera=True
                            if destino.name == 'internacional':
                                coeficiente = destino.pais_id.coeficiente
                                for nivel_internacional in destino.pais_id.cabecera_id.niveles:
                                    if nivel_internacional.name == nivel:
                                        obj_detalle.create(cr, uid, {'solicitud_id': id,
                                                           'detalle': 'Subsistencia - ' + 'Internacional: ' + destino.pais_id.name.name,
                                                           'cantidad': 1,
                                                           'valor': coeficiente*nivel_internacional.valor_subsistencia})
                                        bandera=True
                fecha_calculo = fecha_calculo_3
            if bandera==False:
                raise osv.except_osv('Error', 'El tiempo registrado no es considerado para un viatico')
            total = 0
            for detalle in registro.detalle_solicitud:
                total += detalle.valor
            tabla = self.pool.get('viaticos.tabla').browse(cr, uid, 1, context)
            self.write(cr, uid, [id], {'total_solicitud': total,
                                       'total_porcentaje_facturas': tabla.porcentaje_nacional,
                                       'total_solicitud_facturas': (total/100)*tabla.porcentaje_nacional})
            
asistente_calculadora()