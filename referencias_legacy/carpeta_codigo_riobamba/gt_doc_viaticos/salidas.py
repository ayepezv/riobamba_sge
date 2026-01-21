# -*- coding: utf-8 -*-
##############################################################################
#
#  Mario Chogllo
# mariofchogllo@gmail.com
##############################################################################

from osv import fields, osv
import time
import datetime
import calendar

class hr_job_salidas(osv.osv):
    #Agregamos el campo necesario para la configuracion de salidas al campo
    _inherit = 'hr.job'
    _columns = {
                'nivel_salidas_id': fields.many2one('salidas.configuration', 'Nivel para Salidas'),
                }
hr_job_salidas()

class salidas_log(osv.osv):
    _name = 'salidas.log'
    _description = 'Historial en el informe de salidas al campo'
    _order = "fecha desc"
    _columns = {
                'name': fields.char('Descripción', size=128, required=True),
                'user_id': fields.many2one('res.users','Usuario Responsable', required=True),
                'fecha': fields.datetime('Fecha de creación', required=True),
                'salida_id': fields.many2one('salidas.solicitud', 'Salida'),
                }
    
    _defaults = {
                 'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                 }
    
salidas_log()

class salidas_configuration(osv.osv):
    _name = 'salidas.configuration'
    _description = 'Tabla de configuración para salidas al campo'
    
    def _validar_mayor_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.valor < 0:
            return False
        if obj.cantidad_horas < 0:
            return False
        return True
    
    _columns = {
                'name': fields.char('Descripción', size=50),
                'period_id': fields.many2one('hr.work.period','Periódo'),
                'valor': fields.float('Valor', help="Valor que perciben los cargos indicados a continuación, en caso de gastos de alimentación (salidas al campo)"),
                'cantidad_horas': fields.float('Cantidad de Horas', help='Cantidad de horas requeridas para considerar salida al campo'),
                'cargos_ids': fields.one2many('hr.job', 'nivel_salidas_id', 'Cargos'),
                }
    
    _constraints = [
                    (_validar_mayor_cero, 'Los valores deben ser superiores a cero', ['valor','cantidad_horas']),
                    ]
    
    
    def create(self, cr, uid, values, context=None):
        ids = self.search(cr, uid, [])
        if ids:
            raise osv.except_osv('Error de configuración', 'Debe existir solo 1 registro de configuración')
        else:
            return super(salidas_configuration, self).create(cr, uid, values, context=context)

salidas_configuration()


class solicitud_salida(osv.osv):
    _name = 'salidas.solicitud'
    _description = 'Solicitud de salidas al Campo'
    _order = 'name desc, fecha_solicitud desc'
    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar una solicitud que ya inicio el proceso')
        return False
    
    def departamento_usuario(self, cr, uid, context=None):
        empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
        if empleado_id:
            empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id[0])
            return empleado.department_id.id
        return False
    
    def _calculate_tiempo(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            time_salida = datetime.datetime.strptime(line.fecha_salida, "%Y-%m-%d %H:%M:%S")
            time_llegada = datetime.datetime.strptime(line.fecha_retorno, "%Y-%m-%d %H:%M:%S")
            res[line.id] = str(time_llegada - time_salida)
        return res
    
    def calcular_tiempo(self, cr, uid, ids, salida, llegada, context=None):
        resultado = 0
        if salida and llegada:
            time_salida = datetime.datetime.strptime(salida, "%Y-%m-%d %H:%M:%S")
            time_llegada = datetime.datetime.strptime(llegada, "%Y-%m-%d %H:%M:%S")
            time_salida = time_salida.replace(second=00)
            time_llegada = time_llegada.replace(second=00)
            if time_llegada>time_salida:
                resultado = time_llegada - time_salida
                return {'value': {'fecha_salida': str(time_salida),
                                  'fecha_retorno': str(time_llegada),
                                  'tiempo': str(resultado)}}
            else:
                msgalert = {'title':'Advertencia','message':'Las fechas se encuentran colocadas incorrectamente'}
                return {'warning':msgalert}
        return {'value': {'tiempo': str(0)}}
    
    _columns = {
                'name': fields.char('Orden de Salida', size=10),
                'fecha_solicitud': fields.datetime('Fecha de elaboración'),
                'employee_id': fields.many2one('hr.employee', 'Empleado'),
                'department_id': fields.many2one('hr.department', 'Departamento'),
                #'ocupational_id': fields.many2one('grupo.ocupacional', 'Grupo Ocupacional'),
                'job_id': fields.many2one('hr.job', 'Cargo'),
                'ciudad_id': fields.many2one('res.country.state.canton', 'Cantón destino'),
                'parroquia_id': fields.many2one('res.country.state.parish', 'Parroquia destino'),
                'fecha_salida': fields.datetime('Fecha y hora de salida'),
                'fecha_retorno': fields.datetime('Fecha y hora de llegada'),
                #'tiempo': fields.char('Tiempo de salida', size=30),
                'tiempo': fields.function(_calculate_tiempo, method=True, type='char', size=30, string='Tiempo de salida', store=True),
                'actividades': fields.text('Actividades'),
                'state': fields.selection([('draft','Borrador'),('aprobado1','Informe enviado'),('aprobado2','Aprobado Jefe Superior'),('aprobado3','Aprobado Coordinador General'),('done','Aprobado TTHH'), ('pagado','Pagado en Rol'),('descartado','Rechazado')], 'Estado'),
                'valor': fields.float('Valor a cancelar en rol'),
                'period_id': fields.many2one('hr.work.period.line', 'Mes de pago en rol'),
                'log_id': fields.one2many('salidas.log','salida_id','Historial'),
                }
    
    _defaults = {
                 'state': 'draft',
                 'valor': 0,
                 'department_id': departamento_usuario,
                 }
    
    def create(self, cr, uid, values, context={}):
        obj_empleado = self.pool.get('hr.employee')
        empleado = obj_empleado.browse(cr, uid, values['employee_id'], context)
        values['job_id'] = empleado.job_id.id
        values['department_id'] = empleado.department_id.id
        values['name'] = self.pool.get('ir.sequence').get(cr, uid, 'salidas.solicitud')
        values['fecha_solicitud'] = time.strftime("%Y-%m-%d %H:%M:%S")
        return super(solicitud_salida, self).create(cr, uid, values, context=context)
    
    def buscar_departamento(self, cr, uid, ids, empleado_id, context=None):
        value = {}
        obj_employee = self.pool.get('hr.employee')
        empleado = obj_employee.browse(cr, uid, empleado_id, context)
        if empleado.job_id:
            value['job_id'] = empleado.job_id.id
            value['ocupational_id'] = empleado.ocupational_id.id
        return {'value': value}
    
    def descartar(self, cr, uid, ids, context=None):
        for peticion in self.browse(cr, uid, ids, context):
                log_obj=self.pool.get('salidas.log')
                log_obj.create(cr, uid, {
                                  'name': 'SALIDA AL CAMPO ANULADA',
                                  'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                                  'salida_id': peticion.id,
                                  'user_id': uid,
                                  })
        return self.write(cr, uid, ids, {'state': 'descartado'})
    
    def draft_aprobar1(self, cr, uid, ids, context=None):
        for peticion in self.browse(cr, uid, ids, context):
                log_obj=self.pool.get('salidas.log')
                log_obj.create(cr, uid, {
                                  'name': 'Informe enviado',
                                  'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                                  'salida_id': peticion.id,
                                  'user_id': uid,
                                  })
                return self.write(cr, uid, [peticion.id], {'state': 'aprobado1'})
    
    def aprobar1_aprobar2(self, cr, uid, ids, context=None):
        for peticion in self.browse(cr, uid, ids, context):
                log_obj=self.pool.get('salidas.log')
                log_obj.create(cr, uid, {
                                  'name': 'Informe aprobado por JEFE SUPERIOR',
                                  'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                                  'salida_id': peticion.id,
                                  'user_id': uid,
                                  })
                
        return self.write(cr, uid, ids, {'state': 'aprobado2'})
    
    def aprobar2_aprobar3(self, cr, uid, ids, context=None):
        for peticion in self.browse(cr, uid, ids, context):
                log_obj=self.pool.get('salidas.log')
                log_obj.create(cr, uid, {
                                  'name': 'Informe aprobado por COORDINADOR',
                                  'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                                  'salida_id': peticion.id,
                                  'user_id': uid,
                                  })
                
        return self.write(cr, uid, ids, {'state': 'aprobado3'})
    
    def aprobar3_realizado(self, cr, uid, ids, context=None):
        for registro in self.browse(cr, uid, ids, context):
            if registro.period_id:
                log_obj=self.pool.get('salidas.log')
                log_obj.create(cr, uid, {
                                  'name': 'Informe aprobado por TALENTO HUMANO',
                                  'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                                  'salida_id': registro.id,
                                  'user_id': uid,
                                  })
            else:
                raise osv.except_osv('Error', 'Debe indicar el periódo de pago en rol para aprobarlo')
        return self.write(cr, uid, ids, {'state': 'done'})
    
    
    
    def _fecha_en_periodo(self, cr, uid, ids, context=None):
        obj_destino = self.pool.get('res.country.state.canton')
        obj_empleado = self.pool.get('hr.employee')
        obj = self.browse(cr, uid, ids[0], context=context)
        destino = obj_destino.browse(cr, uid, obj.ciudad_id.id, context)
        empleado = obj_empleado.browse(cr, uid, obj.employee_id.id, context)
        if empleado.job_id.nivel_salidas_id:
            if empleado.job_id.nivel_salidas_id.period_id.date_start <= obj.fecha_salida and empleado.job_id.nivel_salidas_id.period_id.date_stop >= obj.fecha_salida:
                return True
            else:
                return False
        return True
    
    def _tiempo_total(self, cr, uid, ids, context=None):
        obj_destino = self.pool.get('res.country.state.canton')
        obj_empleado = self.pool.get('hr.employee')
        obj = self.browse(cr, uid, ids[0], context=context)
        #buscamos el periodo de la salida
        obj_periodo = self.pool.get('hr.work.period')
        id_periodo = obj_periodo.search(cr, uid, [('date_start','<=',obj.fecha_salida),
                                                  ('date_stop','>=',obj.fecha_retorno)])
        #buscamos la configuracion de ese periodo
        if id_periodo:
            obj_configuracion = self.pool.get('salidas.configuration')
            id_configuracion = obj_configuracion.search(cr, uid, [('period_id','=',id_periodo[0])])
            if id_configuracion:
                configuracion = obj_configuracion.browse(cr, uid, id_configuracion[0])
                time_salida = datetime.datetime.strptime(obj.fecha_salida, "%Y-%m-%d %H:%M:%S")
                time_llegada = datetime.datetime.strptime(obj.fecha_retorno, "%Y-%m-%d %H:%M:%S")
                diferencia = time_llegada - time_salida
                total_diferencia = diferencia.total_seconds()
                total_diferencia = total_diferencia / 3600
                print total_diferencia
                print configuracion.cantidad_horas
                if time_salida.day == time_llegada.day:
                    if total_diferencia >= configuracion.cantidad_horas:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
        
        

    _constraints = [
                    (_fecha_en_periodo, 'La fecha de este informe y el cargo del empleado se encuentran configurados en diferentes periodos', ['fecha_salida', 'fecha_retorno']),
                    (_tiempo_total, 'El tiempo no es considerado para una salida al campo. Consulte el tiempo necesario que se encuentra configurado', ['fecha_salida','fecha_retorno'])
                    ]
        
    
solicitud_salida()
