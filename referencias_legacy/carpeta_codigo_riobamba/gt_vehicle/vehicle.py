# -*- coding: utf-8 -*-
##############################################################################
#
# MARIO CHOGLLO
#
##############################################################################

from osv import osv, fields
import time
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from tools import ustr

class incidentDriver(osv.Model):
    _name = 'incident.driver'
    _description="Incidentes"
        
    def _get_type(self, cr, uid, context):               
        res=''               
        if 'tipo' in context:
            if context['tipo']=='planta_mod':
                res='planta'
            else:              
                res = context['tipo']
        return res
    
    def validar_tiempo(self, cr, uid, ids, fecha1,context=None):
        res_value = {}        
        if fecha1:
            time_fecha1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_fecha1 = time_fecha1.replace(second=00)
            res_value['fecha']=str(time_fecha1)   
            if str(time_fecha1)>str(time.strftime('%Y-%m-%d %H:%M:%S')):
                return {'warning': {'title':'Advertencia','message':'La Fecha no puede ser mayor a la actual'},'value':res_value}                
        return {'value':res_value}
        
    _columns = dict(
        name = fields.many2one('vehicle.vehicle','Vehículo',required=True),
        fecha = fields.datetime('Fecha',required=True),
        desc = fields.text('Observación',required=True),
        driver_id = fields.many2one('vehicle.driver','Chofer',required=True),
        tipo = fields.char('Tipo', size=28),            
        )
    
    _defaults = dict(
        driver_id = lambda self, cr, uid, c: self.pool.get('vehicle.driver').browse(cr, uid, uid, c).id ,        
        tipo = _get_type, 
        )
incidentDriver()

class vehicleDriver(osv.Model):
    _name = 'vehicle.driver'
    _description="Chofer"

    _LIC_TYPE = [('a','A'),('b','B'),('c','C'),('d','D'),('e','E')]
    _INTERNAL_TYPE = [('planta','Institucional'),('contratado','Contratado')]


    def create(self, cr, uid, vals, context):        
        vehicle_incident = self.pool.get('vehicle.incident')
        incident_driver = self.pool.get('incident.driver')
        if 'incident_ids' in vals and len(vals['incident_ids'])>0:              
            for this in vals['incident_ids']:            
                if this[2]:                     
                    if str(this[2]['fecha'])>str(time.strftime('%Y-%m-%d %H:%M:%S')):
                        raise osv.except_osv('Error', 'La Fecha del incidente no puede ser mayor a la actual')
                    else:
                        id_reg=super(vehicleDriver, self).create(cr, uid,vals, context)
                        vehicle_incident.create(cr, uid, {
                        'user_id':uid,
                        'driver_id':id_reg,
                        'name':this[2]['fecha'],
                        'detail':this[2]['desc'],
                        'vehicle_id':this[2]['name'],
                        })    
                    return id_reg
        else:                    
            return super(vehicleDriver, self).create(cr, uid,vals, context) 

    def write(self, cr, uid, ids, vals, context):        
        vehicle_incident = self.pool.get('vehicle.incident')
        incident_driver = self.pool.get('incident.driver')             
        vals_incident={}
        if 'incident_ids' in vals:            
            for this in vals['incident_ids']:            
                if this[2]:
                        if 'fecha' in this[2] and 'desc' in this[2] and 'name' in this[2]:                                        
                            if str(this[2]['fecha'])>str(time.strftime('%Y-%m-%d %H:%M:%S')):
                                raise osv.except_osv('Error', 'La Fecha del incidente no puede ser mayor a la actual')
                            else:                                                                    
                                vehicle_incident.create(cr, uid, {
                                'user_id':uid,
                                'driver_id':ids[0],
                                'name':this[2]['fecha'],
                                'detail':this[2]['desc'],
                                'vehicle_id':this[2]['name'],
                                })            
                        else:
                 
                            if 'fecha' in this[2]:
                                if str(this[2]['fecha'])>str(time.strftime('%Y-%m-%d %H:%M:%S')):
                                    raise osv.except_osv('Error', 'La Fecha del incidente no puede ser mayor a la actual')
                                else:
                                    vals_incident['name']=this[2]['fecha']                              
                            if 'desc' in this[2]:
                                vals_incident['detail']=this[2]['desc']                                                            
                            if 'name' in this[2]:
                                vals_incident['vehicle_id']=this[2]['name']
                            vehicle_incident.write(cr, uid, this[1],vals_incident)                                                
        return super(vehicleDriver, self).write(cr, uid, ids,vals, context) 
    
    def unlink(self, cr, uid, ids, context):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar choferes')
        return False

    def _get_type(self, cr, uid, context):  
        if 'driver_type' in context:
            res = context['driver_type']
        else:
            res='contratado'               
        return res
    
    _columns = dict(
        incident_ids = fields.one2many('incident.driver','driver_id','Detalle Incidentes'),
        employee_id = fields.many2one('hr.employee','Empleado'),
        name = fields.char('Nombres/Apellidos',size=128,required=True),
        ci = fields.char('Cedula/RUC',size=13,required=True),
        telf = fields.char('Teléfono Casa',size=10),
        telf_oficina = fields.char('Teléfono Oficina',size=10),
        direccion = fields.char('Dirección Domicilio',size=128),
        sex = fields.selection([('male','Hombre'),('female','Mujer')],'Sexo'),
        fec_nac = fields.date('Fecha Nacimiento'),
        tipo_licencia = fields.selection(_LIC_TYPE,'Tipo Licencia'),
        fec_emision = fields.date('Fecha Emisión'),
        fec_caducidad = fields.date('Fecha Caducidad'),
        observaciones = fields.text('Observaciones'),
        driver_type = fields.selection(_INTERNAL_TYPE,'Tipo'),
        )

    _defaults = dict(
        driver_type = _get_type,
        tipo_licencia = "c",
        fec_emision = time.strftime('%Y-%m-%d'),
        fec_caducidad = time.strftime('%Y-%m-%d'),
        )

    _sql_constraints = [
        ('unique_cedula','unique(ci)','La cedula debe ser unica, verifique si esta mal ingresada o el chofer ya esta registrado')
        ]

class vehicleColor(osv.Model):
    _name= 'vehicle.color'
    _description="Color"
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar el registro')
        return False

    _columns = dict(
        name = fields.char('Color',size=16,required=True),
        )

class vehicleStateConservation(osv.Model):
    _name = 'vehicle.state.conservation'

    _columns = dict(
        name = fields.char('Estado Conservacion',size=20,required=True),
        )

vehicleStateConservation()

class vehicleMark(osv.Model):
    _name= 'vehicle.mark'
    _description="Marca"

            
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar marcas de vehículos')
        return False

    _columns = dict(
        name = fields.char('Marca',size=32,required=True),
        )   
vehicleMark() 

class vehicleModel(osv.Model):
    _name= 'vehicle.model'
    _description="Modelo"


    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar modelos vehículos')
        return False

    _columns = dict(
        name = fields.char('Modelo',size=64,required=True),
        )    

class vehicleUpdate(osv.Model):
    _name = 'vehicle.update'
    _description="Actualizar Kilometraje"

    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar registros de actualización de kilometraje')
        return False

    _columns = dict(
        name = fields.many2one('res.users','Usuario'),
        date = fields.datetime('Fecha'),
        km_ant = fields.integer('Km. Anterior'),
        km_new = fields.integer('Km. Nuevo'),
        note = fields.char('Observaciones',size=64),
        vehicle_id = fields.many2one('vehicle.vehicle','Vehículo'),
        )

class vehicleRouteKm(osv.Model):
    _name = 'vehicle.route.km'
    _description="Rutas"
 
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar registros de rutas')
        return False

    _columns = dict(
        responsable_id = fields.many2one('hr.employee','Responsable'),
        name = fields.char('Ruta',size=128,required=True),
        date_start = fields.datetime('Fecha Salida'),
        date_end = fields.datetime('Fecha Regreso'),
        km_start = fields.integer('Km. Incial'),
        km_end = fields.integer('Km. Final'),
        vehicle_id = fields.many2one('vehicle.vehicle','Vehículo'),
        )

class vehicleDriverDate(osv.Model):
    _name = 'vehicle.driver.date'
    _description="Chofer"
        
    def _get_type(self, cr, uid, context):    
        res=''               
        if 'tipo' in context:
            if context['tipo']=='planta_mod':
                res='planta'
            else:              
                res = context['tipo']
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar registros de choferes entre fechas')
        return False

    _columns = dict(
        name = fields.many2one('vehicle.driver','Chofer',required=True),
        date_start = fields.date('Fecha Desde',required=True),
        date_stop = fields.date('Fecha Hasta',required=True),
        vehicle_id = fields.many2one('vehicle.vehicle','Vehículo'),
        actual=fields.boolean('Actual'),
        tipo = fields.char('Tipo', size=28),
        )

    _defaults = dict(
        date_start = time.strftime('%Y-%m-%d'),
        date_stop = time.strftime('%Y-%m-%d'),
        tipo = _get_type,        
        )

class vehicleIncident(osv.Model):
    _name = 'vehicle.incident'
    _description="Incidentes"
    

    def _get_user(self, cr, uid, context=None):
        return uid

    _columns = dict(
        user_id = fields.many2one('res.users','Usuario'),
        driver_id = fields.many2one('vehicle.driver','Chofer'),
        name = fields.datetime('Fecha'),
        detail = fields.char('Incidente',size=256),
        vehicle_id = fields.many2one('vehicle.vehicle','Vehículo'),
        )

    _defaults = dict(
        name = time.strftime('%Y-%m-%d %H:%M:%S'),
        user_id = _get_user,
        )


class vehicleRepair(osv.Model):
    _name = 'vehicle.repair'
    _description="Vehículo Reparado"
    _OPC = [('danio','En Reparación'),('reparado','Reparado')]
    _columns = dict(
        user_id = fields.many2one('res.users','Usuario',required=True),
        desc=fields.text('Descripcion'),
        name = fields.datetime('Fecha'),
        opc = fields.selection(_OPC,'Estado'),
        vehicle_id = fields.many2one('vehicle.vehicle','Vehículo'),
        )
    
    _defaults = dict(
        name = time.strftime('%Y-%m-%d %H:%M:%S'),
        opc = 'danio',
        )

vehicleRepair()

class vehicleAtribute(osv.Model):
    _name = 'vehicle.atribute'
    _columns = dict(
        name = fields.char('Caracteristica',size=128,required=True),
        )
vehicleAtribute()

class vehicleAtributeLine(osv.Model):
    _name = 'vehicle.atribute.line'
    _columns = dict(
        name = fields.many2one('vehicle.atribute','Caracteristica',required=True),
        value = fields.char('Valor',size=128,required=True),
        vehicle_id = fields.many2one('vehicle.vehicle','Vehiculo'),
        )
vehicleAtribute()

class vehicleVehicle(osv.Model):
    _name = 'vehicle.vehicle'    
    _description = 'Vehículo'

    _INTERNAL_TYPE = [('planta','Institucional'),('contratado','Contratado'),('planta_mod','Institucional')]
    _VEHICLE_STATE = [('disponible','Disponible'),('ocupado','Ocupado'),
                      ('danado','En Reparación'),('asignado','Asignado')]
    _VEHICLE_CREATE = [('t','True'),('f','False')]
    _VEHICLE_ESTADO = [('borrador','borrador'),('guardado','guardado'),('guardado_inst','guardado institucional'),
                       ('low','Dado de Baja')]

       
    def _validar_anio(self, cr, uid, ids):
        result = False        
        fecha = str(time.strftime('%Y-%m-%d %H:%M:%S'))
        fecha_anio=fecha.split("-")[0]            
        for obj in self.browse(cr, uid, ids):
            if int(obj.anio)>int(fecha_anio):
                return False
            else:                
                    result = True
        return result 
        
    def vehicle_repair(self, cr, uid, ids, *args):
        vehicle_obj = self.pool.get('vehicle.vehicle')
        repair_obj = self.pool.get('vehicle.repair')
        context = {}
        context['vehicle_type']='contratado'
        for this in self.browse(cr, uid, ids):
            if not this.state=='ocupado':
                vehicle_obj.write(cr, uid, this.id,{
                        'state' : 'danado',
                        },context)
                repair_obj.create(cr, uid,{
                        'user_id':uid,
                        'name':time.strftime('%Y-%m-%d %H:%M:%S'),
                        'opc':'danio',
                        'vehicle_id':this.id,
                        })
            else:
                raise osv.except_osv('Error', 'No pueden pasar a repación si el vehículo se encuentra ocupado')
        return True

    def vehicle_ok(self, cr, uid, ids, *args):
        vehicle_obj = self.pool.get('vehicle.vehicle')
        repair_obj = self.pool.get('vehicle.repair')
        context = {}
        context['vehicle_type']='contratado'
        for this in self.browse(cr, uid, ids):
            if this.state=='danado':
                vehicle_obj.write(cr, uid, this.id,{
                        'state' : 'disponible',
                    },context)
                repair_obj.create(cr, uid, {
                        'user_id':uid,
                        'name':time.strftime('%Y-%m-%d %H:%M:%S'),
                        'opc':'reparado',
                        'vehicle_id':this.id,
                        })
            else:
                raise osv.except_osv('Error de usuario', 'Solo puede realizar esta acción en vehículos dañados')
        return True

    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar vehículos')
        return False
    
    def name_get(self, cr, uid, ids, context=None):
         if context is None:
            context = {}
         if not ids:
            return []
         res = []
         reads = self.browse(cr, uid, ids, context=context)
         for record in reads:
             name = (record.cadena)
             res.append((record.id, name))         
         return res
     
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_name = self.search(cr, uid, [('cadena', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_name))
        return self.name_get(cr, uid, ids, context=context)
    
    def _check_chofer(self, cr, uid, ids):
        result = False
        for obj in self.browse(cr, uid, ids):
            if obj.vehicle_type=='planta' or obj.vehicle_type=='planta_mod':
                return True
            else:
                if obj.driver_ids:
                    result = True
        return result        
        
    def create(self, cr, uid, vals, context):
        #envio de vehiculo a tabla de SIIM
        marca_obj = self.pool.get('vehicle.mark')
        estado_cons = self.pool.get('vehicle.state.conservation')
#        import pg
#        usuario='postgres'
#        clave='manager'
#        base='Tracker_pruebas'
#        puerto=5432
#        conexion=pg2.connect(dbname=base,user=usuario,passwd=clave,port=puerto)
#        marca = marca_obj.browse(cr, uid, vals['marca_id'])
#        estado = estado_cons.browse(cr, uid, vals['state_id'])
#        desc = vals['name'] + ' ' + marca.name
#        aux = 1
#        aux_next = 'nextval'
#        seq = 'seqposicion'
#        consulta = "insert into objeto_rastreado (id,descripcion,\"tipoObjRastreado\",marca,anio,\"estadoConservacion\",\"tipoCombustible\",\"galonesPromedio\") values ("+aux_next+'('+"'"+seq+"'"+')'+','+"'"+desc+"'"+','+str(aux)+','+"'"+str(marca.name)+"'"+','+str(vals['anio'])+','+str(aux)+','+str(aux)+','+str(aux)+')'
#        print "CONSULTA SQL", consulta
#        respuesta=conexion.query(consulta)
#        conexion.close()
        ##
        cont=0  
        if 'driver_ids' in vals:            
            if len(vals['driver_ids'])>0:
                for line in vals['driver_ids']:            
                    if line[2]['date_stop']<line[2]['date_start']:
                        raise osv.except_osv(('Error'), 'La Fecha Fin no puede ser menor a la Fecha Inicio')
                    if line[2]['actual']==True:
                        cont=cont+1
                if cont==0:
                    raise osv.except_osv(('Error'), 'El vehículo debe tener un chofer actual')
                if cont>1:
                    raise osv.except_osv(('Error'), 'El Vehículo no puede tener más de dos choferes actuales')                                      
                if context['vehicle_type']=='planta':            
                    if context['create_opc']=='f':
                        raise osv.except_osv(('Error Permisos !'), 'No puede crear vehículos institucionales desde esta opción')
                    
                else:            
                    marca_obj = self.pool.get('vehicle.mark')
                    marca = marca_obj.browse(cr, uid, vals['marca_id'])
                    modelo_obj = self.pool.get('vehicle.model')
                    modelo = modelo_obj.browse(cr, uid, vals['model_id'])
                    color_obj = self.pool.get('vehicle.color')
                    color = color_obj.browse(cr, uid, vals['color_id'])            
                    vals['cadena']="Contratado-"+str(vals['name'])+"/"+str(marca.name)+"/"+str(modelo.name)+"/"+str(color.name)+'/'+str(vals['anio'])                
                    if vals['km']<=0 and context['vehicle_type']=='contratado':
                        raise osv.except_osv(('Error'), 'Debe ingresar el Kilometraje Inicial del Vehículo')
                #llamar al asistente
                vals['estado']='guardado'                
            else:
                raise osv.except_osv(('Error'), 'Verifique que el vehiculo al menos tenga un chofer')
        return super(vehicleVehicle, self).create(cr, uid, vals, context=context)
               
    def write(self, cr, uid, ids, vals, context):      
        cont_driver=0
        driver_date=False
        vehicle_obj=self.pool.get('vehicle.vehicle').browse(cr, uid, ids)
        driver_obj=self.pool.get('vehicle.driver.date')   
        ids_drivers=[]     
        if 'driver_ids' in vals:            
            for line in vals['driver_ids']:
                ids_drivers.append((line[1],line[2]))                         
            for list_driver in ids_drivers:   
                if list_driver[0]: 
                    id=self.pool.get('vehicle.driver.date').browse(cr, uid, list_driver[0])             
                    driver_date=self.pool.get('vehicle.driver.date').search(cr, uid,[('name','=',id.name.id)])               
                if list_driver[1]:                    
                    if "actual" in list_driver[1]: 
                        if list_driver[1]['actual']==True:
                            cont_driver+=1                            
                            for drivers in vehicle_obj:
                                for driver in drivers.driver_ids:                                    
                                    if driver.id==list_driver[0]:                            
                                        if driver.name.employee_id:
                                            if "date_start" in list_driver[1] and "date_stop" in list_driver[1]:
                                                cr.execute('select id from hr_holidays where employee_id='+str(driver.name.employee_id.id)+' and CAST (date_to AS DATE)>=%s and CAST (date_from AS DATE)<=%s and state=%s and type=%s',(list_driver[1]['date_start'],list_driver[1]['date_stop'],'validate','remove',))                            
                                                ids_holidays = map(lambda x: x[0], cr.fetchall())                        
                                                if ids_holidays:
                                                    raise osv.except_osv(('Error'), 'El chofer actual no esta disponible para ese rango fechas')
                                            if "date_start" in list_driver[1] and not "date_stop" in list_driver[1]:
                                                date_stop=driver.date_stop
                                                cr.execute('select id from hr_holidays where employee_id='+str(driver.name.employee_id.id)+' and CAST (date_to AS DATE)>=%s and CAST (date_from AS DATE)<=%s and state=%s and type=%s',(list_driver[1]['date_start'],date_stop,'validate','remove',))                            
                                                ids_holidays = map(lambda x: x[0], cr.fetchall())                        
                                                if ids_holidays:
                                                    raise osv.except_osv(('Error'), 'El chofer actual no esta disponible para ese rango fechas')
                                            if "date_stop" in list_driver[1] and "date_start" in list_driver[1]:
                                                date_start=driver.date_start
                                                cr.execute('select id from hr_holidays where employee_id='+str(driver.name.employee_id.id)+' and CAST (date_to AS DATE)>=%s and CAST (date_from AS DATE)<=%s and state=%s and type=%s',(date_start,list_driver[1]['date_stop'],'validate','remove',))                            
                                                ids_holidays = map(lambda x: x[0], cr.fetchall())                        
                                                if ids_holidays:
                                                    raise osv.except_osv(('Error'), 'El chofer actual no esta disponible para ese rango fechas')                                            
                    #Validadcion de choferes disponible cuanod se modifican ambas fechas                
                    if driver_date:
                        if "date_start" in list_driver[1] and "date_stop" in list_driver[1]:
                            for drivers_date in driver_obj.browse(cr,uid,driver_date):                                 
                                if drivers_date.id==list_driver[0]:
                                    if drivers_date.actual==True:
                                        cont_driver+=1
                                        if drivers_date.name.employee_id:
                                            #Verifica si el chofer que es empleado tiene ausencias
                                            cr.execute('select id from hr_holidays where employee_id='+str(drivers_date.name.employee_id.id)+' and CAST (date_to AS DATE)>=%s and CAST (date_from AS DATE)<=%s and state=%s and type=%s',(list_driver[1]['date_start'],list_driver[1]['date_stop'],'validate','remove',))
                                            ids_holidays = map(lambda x: x[0], cr.fetchall())                                                                        
                                            if ids_holidays:
                                                    raise osv.except_osv(('Error'), 'El chofer no disponible para esa fecha')
                                        if list_driver[1]['date_start']>list_driver[1]['date_stop']:
                                            raise osv.except_osv(('Error'), 'La Fecha Fin no puede ser menor a la Fecha Inicio')
                                else:
                                    if drivers_date.actual==True:                                    
                                        if drivers_date.name.employee_id:
                                            if drivers_date.name.employee_id.id and id.name.employee_id.id:                                
                                                if drivers_date.name.employee_id.id==id.name.employee_id.id:
                                                    if drivers_date.date_stop>=list_driver[1]['date_start'] and drivers_date.date_start<=list_driver[1]['date_stop']:
                                                        raise osv.except_osv(('Error'), 'El chofer actual ya tiene asignado un vehículo en ese rango de fechas')                        
                        if "date_start" in list_driver[1] and not "date_stop" in list_driver[1]:                       
                            for drivers_date in driver_obj.browse(cr,uid,driver_date):                   
                                date_stop_driver=id.date_stop
                                if drivers_date.id==list_driver[0]:
                                    if drivers_date.actual==True:
                                        cont_driver+=1
                                        if drivers_date.name.employee_id:
                                            cr.execute('select id from hr_holidays where employee_id='+str(drivers_date.name.employee_id.id)+' and CAST (date_to AS DATE)>=%s and CAST (date_from AS DATE)<=%s and state=%s and type=%s',(list_driver[1]['date_start'],date_stop_driver,'validate','remove',))
                                            ids_holidays = map(lambda x: x[0], cr.fetchall())                                                                        
                                            if ids_holidays:
                                                    raise osv.except_osv(('Error'), 'El chofer no disponible para esa fecha')
                                        if drivers_date.date_stop<list_driver[1]['date_start']:
                                            raise osv.except_osv(('Error'), 'La Fecha Fin no puede ser menor a la Fecha Inicio')
                                else:
                                    if drivers_date.actual==True:                                    
                                        if drivers_date.name.employee_id:
                                            if drivers_date.name.employee_id.id and id.name.employee_id.id:                                
                                                if drivers_date.name.employee_id.id==id.name.employee_id.id:
                                                    if drivers_date.date_stop>=list_driver[1]['date_start'] and drivers_date.date_start<=date_stop_driver:
                                                        raise osv.except_osv(('Error'), 'El chofer actual ya tiene asignado un vehículo en ese rango de fechas')
                        if "date_stop" in list_driver[1] and not "date_start" in list_driver[1]:
                            for drivers_date in driver_obj.browse(cr,uid,driver_date):                    
                                date_start_driver=id.date_start
                                if drivers_date.id==list_driver[0]:
                                    if drivers_date.actual==True:
                                        cont_driver+=1
                                        if drivers_date.name.employee_id:
                                            cr.execute('select id from hr_holidays where employee_id='+str(drivers_date.name.employee_id.id)+' and CAST (date_to AS DATE)>=%s and CAST (date_from AS DATE)<=%s and state=%s and type=%s',(date_start_driver,list_driver[1]['date_stop'],'validate','remove',))
                                            ids_holidays = map(lambda x: x[0], cr.fetchall())                                                                        
                                            if ids_holidays:
                                                    raise osv.except_osv(('Error'), 'El chofer no disponible para esa fecha')
                                        if drivers_date.date_start>list_driver[1]['date_stop']:
                                            raise osv.except_osv(('Error'), 'La Fecha Fin no puede ser menor a la Fecha Inicio')
                                else:
                                    if drivers_date.actual==True:                                    
                                        if drivers_date.name.employee_id:
                                            if drivers_date.name.employee_id.id and id.name.employee_id.id:                                
                                                if drivers_date.name.employee_id.id==id.name.employee_id.id:
                                                    if drivers_date.date_stop>=date_start_driver and drivers_date.date_start<=list_driver[1]['date_stop']:
                                                        raise osv.except_osv(('Error'), 'El chofer actual ya tiene asignado un vehículo en ese rango de fechas')                        
                else:                
                    for drivers in vehicle_obj:
                        for driver in drivers.driver_ids:
                            if driver.id==list_driver[0]:
                                if driver.actual==True:                                    
                                    cont_driver+=1                                 
            if cont_driver==0:
               raise osv.except_osv(('Error'), 'El vehiculo debe tener un chofer actual')
            if cont_driver>1:
               raise osv.except_osv(('Error'), 'No puede tener mas de dos choferes actuales en el vehículo')    
        if 'vehicle_type' in context:                                                
            if context['vehicle_type']=='planta':
               if 'number' in vals:
                   number=vals['number']
                   for line in vehicle_obj:
                       cadena=line.cadena                                                                                   
                       vals['cadena']=cadena.split("-")[0]+'#'+str(number)+'-'+cadena.split("-")[1]
               else: 
                   for line in vehicle_obj:
                       number =line.number 
               if 'marca_id' in vals or 'model_id' in vals or 'color_id' in vals or 'name' in vals or 'anio' in vals:                   
                    if 'marca_id' in vals:                 
                        marca_obj = self.pool.get('vehicle.mark')
                        marca = marca_obj.browse(cr, uid, vals['marca_id'])
                    else:
                        for line in vehicle_obj:
                           marca_obj = self.pool.get('vehicle.mark')
                           marca = marca_obj.browse(cr, uid, line.marca_id.id)
                    if 'model_id' in vals:
                        model_obj = self.pool.get('vehicle.model')
                        modelo = model_obj.browse(cr, uid, vals['model_id'])
                    else:
                        for line in vehicle_obj:
                           model_obj = self.pool.get('vehicle.model')
                           modelo = model_obj.browse(cr, uid, line.model_id.id)
                    if 'color_id' in vals:
                        color_obj = self.pool.get('vehicle.color')
                        color = color_obj.browse(cr, uid, vals['color_id'])            
                    else:
                        for line in vehicle_obj:
                           color_obj = self.pool.get('vehicle.color')
                           color = color_obj.browse(cr, uid, line.color_id.id)                                                    
                    if 'name' in vals:
                        name = vals['name']
                    else:
                        for line in vehicle_obj:
                            name =line.name                                                                              
                    if 'anio' in vals:
                        anio = vals['anio']
                    else:
                        for line in vehicle_obj:                                
                            anio =line.anio                   
                    if number==0:                                            
                        vals['cadena']="Institucional-"+str(name)+"/"+str(marca.name)+"/"+str(modelo.name)+"/"+str(color.name)+'/'+str(anio)
                    else:
                        vals['cadena']="Institucional#"+str(number)+'-'+str(name)+"/"+str(marca.name)+"/"+str(modelo.name)+"/"+str(color.name)+'/'+str(anio)
               if 'estado' in context:           
                   if 'create_opc' in context:
                       if context['create_opc']=='f' and context['estado']=='borrador':
                           vals['estado']='borrador'
                           vals['vehicle_type']='planta_mod'
                   if context['estado']=='low':
                       vals['estado']='low'
               else:                            
                   vals['estado']='guardado'
                   vals['vehicle_type']='planta'
                   if 'asigned_department' in vals:   
                       if vals['asigned_department']==True:
                            vals['state']='asignado'   
                       if vals['asigned_department']==False:
                            vals['state']='disponible'      
            else:                
                if 'marca_id' in vals or 'model_id' in vals or 'color_id' in vals or 'name' in vals or 'anio' in vals:
                    if 'marca_id' in vals:                 
                        marca_obj = self.pool.get('vehicle.mark')
                        marca = marca_obj.browse(cr, uid, vals['marca_id'])
                    else:
                        for line in vehicle_obj:
                           marca_obj = self.pool.get('vehicle.mark')
                           marca = marca_obj.browse(cr, uid, line.marca_id.id)
                    if 'model_id' in vals:
                        model_obj = self.pool.get('vehicle.model')
                        modelo_string = model_obj.browse(cr, uid, vals['model_id'])
                    else:
                        for line in vehicle_obj:
                           model_obj = self.pool.get('vehicle.model')
                           modelo_string = model_obj.browse(cr, uid, line.model_id.id)
                    if 'color_id' in vals:
                        color_obj = self.pool.get('vehicle.color')
                        color = color_obj.browse(cr, uid, vals['color_id'])            
                    else:
                        for line in vehicle_obj:
                           color_obj = self.pool.get('vehicle.color')
                           color = color_obj.browse(cr, uid, line.color_id.id)                
                    if 'name' in vals:
                        name = vals['name']            
                    else:
                        for line in vehicle_obj:
                           name =line.name  
                    if 'anio' in vals:
                        anio = vals['anio']            
                    else:
                        for line in vehicle_obj:
                           anio =line.anio                                                                                 
                    vals['cadena']="Contratado-"+str(name)+"/"+str(marca.name)+"/"+str(modelo_string.name)+"/"+str(color.name)+"/"+str(anio)                    
        return super(vehicleVehicle, self).write(cr, uid,ids, vals, context)
    
    def _get_type(self, cr, uid, context):                
        if 'vehicle_type' in context:
            res = context['vehicle_type']
        else:
            res='contratado'               
        return res
       
    _columns = dict(
        atribute_ids = fields.one2many('vehicle.atribute.line','vehicle_id','Caracteristicas'),
        activo = fields.boolean('Activo',readonly=True),       
        name = fields.char('Placa',size=8,required=True,),
        number = fields.integer('Número Institucional'),
        photo =  fields.binary('Photo'),
        vehicle_type = fields.selection(_INTERNAL_TYPE ,'Tipo'),
        marca_id = fields.many2one('vehicle.mark' ,'Marca', required=True),
        model_id = fields.many2one('vehicle.model' ,'Modelo', required=True),
        color_id = fields.many2one('vehicle.color','Color',required=True),
        state_id = fields.many2one('vehicle.state.conservation','Estado Fisico',required=True),
        engine = fields.char('Motor',size=32,required=True),
        chasis = fields.char('Chasis',size=32,required=True),
        anio = fields.integer('Año Fabricación',required=True),
        km = fields.integer('Km. Actual',required=True),
        owner_id = fields.many2one('res.partner','Propietario'),
        driver_ids = fields.one2many('vehicle.driver.date','vehicle_id','Choferes'),
        historial_ids = fields.one2many('vehicle.route.km','vehicle_id','Historial Viajes'),
        update_ids = fields.one2many('vehicle.update','vehicle_id','Historial Modificaciones KM'),
        state = fields.selection(_VEHICLE_STATE,'Estado'),
        estado = fields.selection(_VEHICLE_ESTADO,'Estado crear'),
        create_opc = fields.selection(_VEHICLE_CREATE,'Opcion'),
        incident_ids = fields.one2many('vehicle.incident','vehicle_id','Detalle Incidentes'),
        repair_ids = fields.one2many('vehicle.repair','vehicle_id','Detalle Reparaciones'),
        cadena = fields.char('Cadena',size=128,required=True),
        category_id = fields.many2one('vehicle.category','Categoría'),
        department_id = fields.many2one('hr.department', 'Departamento'),
        asigned_department = fields.boolean('Asignado a Departamento'),
                
        )

    _defaults = dict(        
        state = 'disponible',
        estado = 'borrador',
        vehicle_type= _get_type,
        create_opc = 'f',
        activo = True
        )

    _sql_constraints = [
        ('unique_placa','unique(name)','La placa debe ser unica, verifique si esta mal ingresada o el vehiculo ya esta registrado')
        ]
    
    _constraints = [
        (_check_chofer,'Verifique que el vehiculo al menos tenga un chofer',['driver_ids']),
        (_validar_anio, 'Verifique el año de Fabricación del Vehículo', ['anio'])
        ]

class movilizationOrderPersonal(osv.Model):
    _name = 'movilization.order.employee'
 
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar registros de detalle de empleados')
        return False

    _columns = dict(
        employee_id = fields.many2one('hr.employee','Empleado'),
        mov_id = fields.many2one('movilization.order','Orden Movilización'),
        )

class routeLine(osv.Model):
    _name = 'route.line'
    _order = 'sec asc'
    _description="Rutas"
    
    def create(self, cr, uid, vals, context=None):    
        mov_id = vals['mov_id']
        mov_obj = self.pool.get('movilization.order')
        mov = mov_obj.browse(cr, uid, mov_id)
        vals['sec'] = len(mov.route_ids) + 1
        res_id = super(routeLine, self).create(cr, uid, vals, context=context)
        return res_id

    def _amount_km_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            aux = this.km_final - this.km_inicial
        res[this.id] = aux
        return res

    def _get_default_country(self, cr, uid, context=None):
        id = self.pool.get('res.country').search(cr, uid, [('name','ilike','Ecuador')], context=context)   
        name= self.pool.get('res.country').browse(cr, uid, id, context=context)  
        return name[0].id
    
    def _get_default_state(self, cr, uid, context=None):
        id = self.pool.get('res.country.state').search(cr, uid, [('name','ilike','AZUAY')], context=context)   
        name= self.pool.get('res.country.state').browse(cr, uid, id, context=context)                            
        return name[0].id
    
    
#    def onchange_country(self, cr, uid,ids, country_ids, context=None):   
#        #on_change: carga el departamento  y el custodio actual del activo
#        name= self.pool.get('res.country').browse(cr, uid, country_ids, context=context)        
#        res = {'value': {}}
#        if name.name!='Ecuador':            
#            res['value'] = {'state_id': '',
#                        'parroquia_id': '',
#                        'id_country':False}
#        if name.name=='Ecuador':
#            res['value'] = {'id_country':True}            
#        return res   
        
    
    def onchange_state_id(self, cr, uid, ids, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        res = {'value': {}}
        if country_ids!=64:            
            res['value'] = {'parroquia_id_desde': '',
                        'canton_id_desde':''}      
        return res   
    
    
    _columns = dict(
        sec = fields.integer('Secuencia'),
        desde = fields.char('Desde',size=32,required=True),
        hasta = fields.char('Hasta',size=32,required=True),
        country_id=fields.many2one('res.country', 'País'),
        state_id_desde=fields.many2one('res.country.state','Provincia'),
        canton_id_desde=fields.many2one('res.country.state.canton','Cantón'),      
        parroquia_id_desde=fields.many2one('res.country.state.parish', 'Parroquia'),
        state_id_hasta=fields.many2one('res.country.state','Provincia'),
        canton_id_hasta=fields.many2one('res.country.state.canton','Cantón'),      
        parroquia_id_hasta=fields.many2one('res.country.state.parish', 'Parroquia'),        
        km_inicial = fields.integer('Km. Inicial'),
        km_final = fields.integer('Km. Final'),
        km = fields.function(_amount_km_line, string='Total Km. Ruta', type="integer", store=True),
        mov_id = fields.many2one('movilization.order','Orden Movilización'),
        state = fields.related('mov_id','state', type='char', 
                               string='Estado', store=True),
        id_country= fields.boolean('Id Country'),                    
        )

    _defaults = {
        'state_id_desde': _get_default_state,
        'state_id_hasta': _get_default_state,
        'country_id': _get_default_country,
        'id_country': True,       
        }

class movilizationOrder(osv.Model):
    _name = 'movilization.order'
    _order= 'ref desc'
    _description="Solicitud de Movilización"
    
    _MOVILIZATION_STATE = [('draft','Borrador'),('solicitado','Solicitado'),
                           ('agrupado','Agrupado'),('aprobado','Aprobado por Dir/Cor'),('asignado','Vehículo Asignado'),('realizado','Finalizado'),('anulado','Anulado')]

    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            if not formulario.state=='draft':
                raise osv.except_osv('Error', 'Solo es posible eliminar solicitudes de movilización borrador')
        return False
    
    def responsable_usuario(self, cr, uid, context=None):        
        group_id = self.pool.get('ir.model.data').search(cr, uid, [('name','=','group_vehicle_user')])
        if group_id:            
            group_id = self.pool.get('ir.model.data').browse(cr, uid,group_id )        
            rel= cr.execute('select * from res_groups_users_rel where uid='+str(uid)+' and gid='+str(group_id[0].res_id))
            rel = cr.dictfetchall()
            if rel:
                empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
                if empleado_id:
                    empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id[0])
                    return empleado.id
            else:
                return False
        else: 
            return False
            
    def responsable(self, cr, uid, context=None):      
        group_id = self.pool.get('ir.model.data').search(cr, uid, [('name','=','group_vehicle_user')])
        if group_id:
            group_id = self.pool.get('ir.model.data').browse(cr, uid,group_id )        
            rel= cr.execute('select * from res_groups_users_rel where uid='+str(uid)+' and gid='+str(group_id[0].res_id))
            rel = cr.dictfetchall()
            if rel:
                empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
                if empleado_id:
                    empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id[0])
                    return True
            else:
                return False
        else:
            return False
        
    def departamento_usuario(self, cr, uid, context=None):               
        empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
        if empleado_id:
            empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id[0])
            return empleado.department_id.id
        else:
            return False

    def _get_movilization_state(self, cr, uid, context=None):
       if 'state_vehicle' in context:
           return context['state_vehicle']
       else:
           return 'draft' 
       
    def _get_movilization_vehicle(self, cr, uid, context=None):
       if 'vehicle_id' in context:
           return context['vehicle_id']
       else:
           return False

    def create(self, cr, uid, vals, context):                  
        obj_sequence = self.pool.get('ir.sequence')
        vals['ref'] = obj_sequence.get(cr, uid, 'movilization.order') 
        line_employee_obj = self.pool.get('movilization.order.employee')            
        line_employee_obj_resp = self.pool.get('movilization.order.employee')
        posicion = 0 
        if 'route_ids' in vals:   
            for line in vals['route_ids']:
                posicion = posicion + 1
                if posicion==1:
                    anterior_desde = line[2]['desde']
                    anterior_hasta = line[2]['hasta']
                else:
                    if line[2]['desde']==anterior_hasta:
                        anterior_desde = line[2]['desde']
                        anterior_hasta = line[2]['hasta']
                    else:
                        raise osv.except_osv(('Advertencia!'),('Debe coincidir el destino y la llegada de las rutas'))
        if vals['return_date']<vals['movilization_date']:
            raise osv.except_osv(('Advertencia!'), ('La Fecha-Hora de retorno no puede se menor a la Fecha-Hora de salida'))                    
        ind=1
        if 'asigned_depart' in vals:
            if vals['asigned_depart']==True:
                vehicle = self.pool.get('vehicle.vehicle').browse(cr, uid, [vals['vehicle_id_asigned']])
                vals['km_start']=vehicle[0].km 
                vals['vehicle_des']=vehicle[0].cadena
                if vehicle[0].driver_ids:                
                    for chofer in vehicle[0].driver_ids:
                        if chofer.actual==True:
                            chofer_name=chofer.name.name
                            vals['chofer']=chofer_name
                            ind=ind+1          
                    if ind==0:
                            raise osv.except_osv('Error', 'No se puede asignar un vehículo a la solicitud ya que el vehículo no tiene asignado un chofer actual')                                                                         
                else:
                            raise osv.except_osv('Error', 'No se puede asignar un vehículo a la solicitud ya que el vehículo no tiene choferes debe asignar por lo menos un chofer a este vehículo')
        if vals['responsable']==True:
            group_id = self.pool.get('ir.model.data').search(cr, uid, [('name','=','group_vehicle_user')])
            if group_id:
                group_id = self.pool.get('ir.model.data').browse(cr, uid,group_id )        
                rel= cr.execute('select * from res_groups_users_rel where uid='+str(uid)+' and gid='+str(group_id[0].res_id))            
                rel = cr.dictfetchall()
                if rel:
                    empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
                    if empleado_id:
                        empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id[0])
                        vals['responsable_id']=empleado.id
                            
        id_reg=super(movilizationOrder, self).create(cr, uid, vals, context=None)                        
        rel= cr.execute('select * from employee_movi_rel')
        rel = cr.dictfetchall()
        for rel_line in rel:                   
            if (str(id_reg)==str(rel_line['mov_id']) and str(vals['responsable_id'])==str(rel_line['emp_id'])):
                ind=0
                break                                
            else:
                ind=1
        if ind==1:
            cr.execute('INSERT INTO employee_movi_rel (mov_id, emp_id) VALUES ('+str(id_reg)+','+ str(vals['responsable_id'])+')')
        line_employee_obj.create(cr,uid,{"mov_id":id_reg,
                                        "employee_id":vals['responsable_id'],           
                                        })
        for line in vals['employee_ids']:
            for id_emp in line[2]:
                line_employee_obj.create(cr,uid,{"mov_id":id_reg,
                                        "employee_id":id_emp,                                                                        
                                        })
        return id_reg
    
    def _amount_km(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            for line in this.route_ids:                
                aux += line.km
            res[this.id] = aux
        return res

    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id):
        ind=0
        if not vehicle_id:
            return {}
        vehicle = self.pool.get('vehicle.vehicle').browse(cr, uid, vehicle_id)
        if vehicle.driver_ids:
            for chofer in vehicle.driver_ids:
                if chofer.actual==True:
                    chofer_name=chofer.name.name
                    ind=ind+1          
            if ind==0:
                    raise osv.except_osv('Error', 'El vehículo no tiene asignado un chofer actual')                                                                         
        else:
                    raise osv.except_osv('Error', 'El vehículo no tiene choferes debe asignar por lo menos un chofer a este vehículo')                                
        return {'value':{'km_start': vehicle.km,'chofer':chofer_name,'vehicle_id_id':vehicle_id}}

    def mail_user_solicitar(self, cr, uid, ids,  context=None):
        email_to_emp = []
        email_from_emp = []        
        mail_name=False        
        director=''            
        group_id = self.pool.get('ir.model.data').search(cr, uid, [('name','=','group_vehicle_manager')])
        if group_id:
            group_id = self.pool.get('ir.model.data').browse(cr, uid,group_id )
            rel= cr.execute('select * from res_groups_users_rel where gid='+str(group_id[0].res_id))            
            rel = cr.dictfetchall()      
            if rel:
                for rel_line in rel:                  
                    empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',rel_line['uid'])])
                    if empleado_id:
                        empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id[0])
                        if empleado.work_email:
                            email_to_emp+=[empleado.work_email]        
            line = self.browse(cr, uid, ids, context=context)[0]        
            email_to_emp=list(set(email_to_emp))            
            if email_to_emp:
                depart_id = self.pool.get('hr.department').search(cr,uid, [('name','ilike','ADMINISTRACION Y LOGISTICA')])
                depart_id = self.pool.get('hr.department').browse(cr,uid,depart_id)[0]
                if depart_id:
                    if depart_id.manager_id:
                        director=ustr(depart_id.manager_id.complete_name.upper())
                subject_emp = 'ÓRDEN DE MOVILIZACIÓN ' +str(line.ref)
                body_emp= "Para: "+ director+"\n"
                body_emp += 'Responsable: '+ustr(line.responsable_id.complete_name)+"\n"
                body_emp += 'Departamento: '+line.department_id.name+"\n"+'Fecha/Hora Salida: '+str(line.movilization_date)+"\n"+'Fecha/Hora Retorno : '+str(line.return_date)+"\n"
                body_emp += 'Detalle de Actividades: '+line.desc+"\n"
                body_emp += 'Recorrido:\n'
                for routes in line.route_ids:                
                    body_emp +='Ruta '+str(routes.sec)+':   '+routes.desde+'     '+routes.hasta+"\n"             
                if subject_emp or body_emp:                        
                    mail_ids=self.pool.get('ir.mail_server').search(cr, uid, [], context = context)                
                    for mails_obj in self.pool.get('ir.mail_server').browse(cr, uid, mail_ids, context):
                        if mails_obj.smtp_user:
                            empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
                            if empleado_id:
                                empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id[0])
                                if empleado.work_email:
                                    email_from_emp+=[empleado.work_email]
                        email_from_emp=list(set(email_from_emp))                                              
                        if email_from_emp:                            
                            ir_mail_server = self.pool.get('ir.mail_server')                        
                            msg = ir_mail_server.build_email(email_from=email_from_emp, email_to=email_to_emp, subject= subject_emp, body=body_emp,)
                            try:                        
                                ir_mail_server.send_email(cr, uid, msg, context=context)                                
                            except:
                                pass
                        else:
                            pass
        return True
        
    def movilization_solicitar(self, cr, uid, ids, *args):
        mov_obj = self.pool.get('movilization.order')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')        
        context = {}
        for this in self.browse(cr, uid, ids):      
            if this.asigned_depart==True:                
                fecha_today=time.strftime('%Y-%m-%d %H:%M:%S')
                day_week=time.strftime('%w-%W')
                day_week1=[int(day_week.split("-")[0]),int(day_week.split("-")[1])+1]
                semana= int(datetime(*time.strptime(this.movilization_date.split(" ")[0],"%Y-%m-%d")[0:3]).strftime("%W"))+1
                dia= int(datetime(*time.strptime(this.movilization_date.split(" ")[0],"%Y-%m-%d")[0:3]).strftime("%w"))
                day_week2=[dia,semana]               
                if day_week1[0]==5 and day_week1[1]+1==day_week2[1] :
                    if time.strftime('%H:%M:%S')>'12:00:00':
                        id_reg=mov_obj.write(cr, uid, this.id,{
                        'state' : 'solicitado',
                        'name' : time.strftime('%Y-%m-%d %H:%M:%S'),                  
                        })
                        message_obj=self.pool.get('alert')
                        message_id=message_obj.create(cr, uid, {'descripcion': 'Usted esta realizando la Planificación Vehicular fuera del horario establecido en el Reglamento'})                                                        
                        return {
                                'name':"Alerta",
                                'type': 'ir.actions.act_window',                                
                                'res_model': 'alert',
                                'target':'new',
                                'view_type':'form',
                                'view_mode':'form',
                                'res_id': message_id,  
                                'nodestroy': True                                  
                                }                       
                if day_week1[0]>=5 and day_week1[1]+1==day_week2[1] :
                    id_reg=mov_obj.write(cr, uid, this.id,{
                        'state' : 'solicitado',
                        'name' : time.strftime('%Y-%m-%d %H:%M:%S'),                  
                        })      
                    message_obj=self.pool.get('alert')
                    message_id=message_obj.create(cr, uid, {'descripcion': 'Usted esta realizando la Planificación Vehicular fuera del horario establecido en el Reglamento'})                                                
                    return {
                            'name':"Alerta",
                            'type': 'ir.actions.act_window',                                
                            'res_model': 'alert',
                            'target':'new',
                            'view_type':'form',
                            'view_mode':'form',
                            'res_id': message_id,  
                            'nodestroy': True                                  
                            }                                                                   
                if day_week1[1]==day_week2[1]:                                                
                    message_obj=self.pool.get('alert')                                    
                    message_id=message_obj.create(cr, uid, {'descripcion': 'Usted esta intentando realizar la Planificación Vehicular para la semana actual'})                                                           
                    return {
                            'name':"Alerta",
                            'type': 'ir.actions.act_window',                                
                            'res_model': 'alert',
                            'target':'new',
                            'view_type':'form',
                            'view_mode':'form',
                            'res_id': message_id,  
                            'nodestroy': True                                  
                            }   
                if day_week1[1]>day_week2[1]:                                                
                    message_obj=self.pool.get('alert')
                    message_id=message_obj.create(cr, uid, {'descripcion': 'Usted esta intentando realizar la Planificación Vehicular para semana pasadas'})                                    
                    return {
                            'name':"Alerta",
                            'type': 'ir.actions.act_window',                                
                            'res_model': 'alert',
                            'target':'new',
                            'view_type':'form',
                            'view_mode':'form',
                            'res_id': message_id,  
                            'nodestroy': True                                  
                            }
                mov_obj.write(cr, uid, this.id,{
                    'state' : 'solicitado',
                    'name' : time.strftime('%Y-%m-%d %H:%M:%S'),
                     })                  
                self.mail_user_solicitar(cr, uid, [this.id])
            else:      
                mov_obj.write(cr, uid, this.id,{
                    'state' : 'solicitado',
                    'name' : time.strftime('%Y-%m-%d %H:%M:%S'),
                     })                                            
        result = mod_obj.get_object_reference(cr, uid, 'gt_vehicle', args[0]['view_id'])
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context={})[0]                   
        return result
    
    def mail_user_alert(self, cr, uid, ids,  context=None):
        email_to_emp = []    
        mail_name=False        
        group_id = self.pool.get('ir.model.data').search(cr, uid, [('name','=','group_vehicle_manager')])
        if group_id:
            group_id = self.pool.get('ir.model.data').browse(cr, uid,group_id )
            rel= cr.execute('select * from res_groups_users_rel where gid='+str(group_id[0].res_id))            
            rel = cr.dictfetchall()      
            if rel:
                for rel_line in rel:                  
                    empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',rel_line['uid'])])
                    if empleado_id:
                        empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id[0])
                        if empleado.work_email:
                            email_to_emp+=[empleado.work_email]        
            line = self.browse(cr, uid, ids, context=context)[0]        
            email_to_emp=list(set(email_to_emp))
            if email_to_emp:
                subject_emp = 'ÓRDEN DE MOVILIZACIÓN ' +str(line.ref) + ' APROBADA'             
                body_emp  = 'Responsable: '+ustr(line.responsable_id.complete_name)+"\n"
                body_emp += 'Departamento: '+line.department_id.name+"\n"+'Fecha/Hora Salida: '+str(line.movilization_date)+"\n"+'Fecha/Hora Retorno : '+str(line.return_date)+"\n"
                body_emp += 'Detalle de Actividades: '+line.desc+"\n"
                body_emp += 'Recorrido:\n'
                for routes in line.route_ids:                
                    body_emp +='Ruta '+str(routes.sec)+':   '+routes.desde+'     '+routes.hasta+"\n"             
                if subject_emp or body_emp:                        
                    mail_ids=self.pool.get('ir.mail_server').search(cr, uid, [], context = context)                
                    for mails_obj in self.pool.get('ir.mail_server').browse(cr, uid, mail_ids, context):
                        if mails_obj.smtp_user:
                            mail_name= mails_obj.smtp_user            
                        if mail_name:                            
                            ir_mail_server = self.pool.get('ir.mail_server')                        
                            msg = ir_mail_server.build_email(email_from=mail_name , email_to=email_to_emp, subject= subject_emp, body=body_emp,)
                            try:                        
                                ir_mail_server.send_email(cr, uid, msg, context=context)                                
                            except:
                                pass
                        else:
                            pass
        return True
    
    def movilization_aprobar(self, cr, uid, ids, *args):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        mov_obj = self.pool.get('movilization.order')
        for this in self.browse(cr, uid, ids):        
            if this.asigned_depart==True:
                id_reg=mov_obj.write(cr, uid, this.id,{
                    'state' : 'asignado',                   
                     })
            else:
                id_reg=mov_obj.write(cr, uid, this.id,{
                    'state' : 'aprobado',                   
                     })   
                self.mail_user_alert(cr, uid, [this.id])                                       
        result = mod_obj.get_object_reference(cr, uid, 'gt_vehicle', args[0]['view_id'])
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context={})[0]            
        return result

    def print_order(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        order = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [order.id], 'model': 'movilization.order'}
        if order.vehicle_id:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'Salvoconducto',
                'model': 'movilization.order',
                'datas': datas,
                'nodestroy': True,                        
                }
        if order.vehicle_id_asigned:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'SalvoconductoAsignado',
                'model': 'movilization.order',
                'datas': datas,
                'nodestroy': True,                        
                } 
                 
    def print_memo(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        order = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [order.id], 'model': 'movilization.order'}       
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'vehicleRoute',
                'model': 'movilization.order',
                'datas': datas,
                'nodestroy': True,                        
                }
                
    def movilization_asignar(self, cr, uid, ids, *args):
        ind=0
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        mov_obj = self.pool.get('movilization.order')
        vehicle_obj = self.pool.get('vehicle.vehicle')
        context = {}
        context['vehicle_type']='contratado'
        for this in self.browse(cr, uid, ids):
            if this.vehicle_id or this.vehicle_id_asigned:
                if this.vehicle_id:
                    vehicle = self.pool.get('vehicle.vehicle').browse(cr, uid, this.vehicle_id.id)
                if this.vehicle_id_asigned:
                    vehicle = self.pool.get('vehicle.vehicle').browse(cr, uid, this.vehicle_id_asigned.id)
                if vehicle.driver_ids:                
                    for chofer in vehicle.driver_ids:
                        if chofer.actual==True:
                            chofer_name=chofer.name.name
                            ind=ind+1          
                    if ind==0:
                            raise osv.except_osv('Error', 'No se puede asignar un vehículo a la solicitud ya que el vehículo no tiene asignado un chofer actual')                                                                         
                else:
                            raise osv.except_osv('Error', 'No se puede asignar un vehículo a la solicitud ya que el vehículo no tiene choferes debe asignar por lo menos un chofer a este vehículo')
                vehicle_obj.write(cr, uid, this.vehicle_id.id,{
                        'state':'ocupado',
                        },context)
                mov_obj.write(cr, uid, this.id,{
                        'state' : 'asignado',
                        'km_start':this.vehicle_id.km,
                        'chofer':chofer_name,
                        'vehicle_des':this.vehicle_id.cadena,
                        })
            else:
                            raise osv.except_osv('Error', 'Debe asignar un vehículo a la órden de movilizacíon')
        result = mod_obj.get_object_reference(cr, uid, 'gt_vehicle', args[0]['view_id'])
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context={})[0]            
        return result
    
    def movilization_realizado(self, cr, uid, ids, context):              
        for this in self.browse(cr, uid, ids):
            if this.return_date>=time.strftime('%Y-%m-%d %H:%M:%S'):
                raise osv.except_osv('Error', 'Fecha de retorno de la solicitud, todavía no se ha cumplido')
        context = dict(context, active_ids=ids, active_model=self._name)
        trip_id = self.pool.get("vehicle.exec").create(cr, uid, {}, context=context)
        return {
            'name':"Detalle de Rutas",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'vehicle.exec',
            'res_id': trip_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }

    def _check_route(self, cr, uid, ids):
        result = False
        for obj in self.browse(cr, uid, ids):
            if obj.route_ids:
                result = True
        return result
    
    def name_get(self, cr, uid, ids, context=None):
         if context is None:
            context = {}
         if not ids:
            return []
         res = []
         reads = self.browse(cr, uid, ids, context=context)
         for record in reads:
             name = (record.ref)
             res.append((record.id, name))         
         return res
     
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_name = self.search(cr, uid, [('ref', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_name))
        return self.name_get(cr, uid, ids, context=context)
    
    def validar_tiempo_actual(self, cr, uid, ids, fecha1,context=None):
        res_value = {}                      
        if fecha1:
            time_fecha1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_date1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_fecha1 = time_fecha1.replace(second=00)
            res_value['movilization_date']=str(time_fecha1)        
            if str(time_date1)<=str(datetime.now()-timedelta(seconds=10)):
                res_value['movilization_date']=""
                return {'warning': {'title':'Advertencia','message':'La fecha no puede ser menor a la actual'},'value':res_value}
        return {'value':res_value}
    
    def validar_tiempo(self, cr, uid, ids, fecha1, fecha2,context=None):
        res_value = {}       
        if fecha1:
            time_fecha1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_date1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_fecha1 = time_fecha1.replace(second=00)
            res_value['movilization_date']=str(time_fecha1)                   
        if fecha2:
            time_fecha2 = datetime.strptime(fecha2, "%Y-%m-%d %H:%M:%S")
            time_fecha2 = time_fecha2.replace(second=00)
            res_value['return_date']=str(time_fecha2)        
        if fecha1 and fecha2:
            time_salida = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_llegada = datetime.strptime(fecha2, "%Y-%m-%d %H:%M:%S")
            time_fecha1 = time_fecha1.replace(second=00)
            res_value['movilization_date']=str(time_fecha1)
            time_fecha2 = time_fecha2.replace(second=00)
            res_value['return_date']=str(time_fecha2)
            if time_fecha1>=time_fecha2:
                time_fecha1 = time_fecha1.replace(second=00)
                time_fecha2 = time_fecha2.replace(second=00)
                res_value['movilization_date']=str(time_fecha1)
                res_value['return_date']=str(time_fecha2)
                return {'warning': {'title':'Advertencia','message':'La Fecha de retorno debe ser mayor a la de salida'},'value':res_value}
        return {'value':res_value}
    
    def fields_get(self, cr, uid, allfields=None, context=None):
        ret = super(movilizationOrder, self).fields_get(cr, uid,allfields=allfields, context=context)
        group_id = self.pool.get('ir.model.data').search(cr, uid, [('name','=','group_vehicle_user')])
        if group_id:
            group_id = self.pool.get('ir.model.data').browse(cr, uid,group_id )        
            rel= cr.execute('select * from res_groups_users_rel where uid='+str(uid)+' and gid='+str(group_id[0].res_id))            
            rel = cr.dictfetchall()
            if rel:
                    empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
                    if empleado_id:
                        if 'vehicle_id' in ret:
                            ret['vehicle_id']['readonly'] = False
                        else:
                            if 'vehicle_id' in ret:
                                ret['vehicle_id']['readonly'] = True
           
            return ret
        else:
            return False
    
    _columns = dict(
        department_id_vehicle = fields.related('vehicle_id_asigned','department_id', type='many2one', 
                                    relation="hr.department", string='Departamento', 
                                    readonly=True ,store=True),
        origin = fields.char('Origen',size=64,readonly=True, help="Es el número de solicitud de movilización padre en la que esta agrupada"),
        ref = fields.char('Número',size=20,readonly=True),
        name = fields.datetime('Fecha Solicitud', readonly=True),
        department_id = fields.many2one('hr.department', 'Departamento'),
        user_id = fields.many2one('res.users','Creado por',readonly=True),
        responsable_id = fields.many2one('hr.employee','Responsable',required=True),
        responsable_vehiculo = fields.many2one('hr.employee','Responsable del Vehículo',required=True),
        movilization_date = fields.datetime('Fecha/Hora Salida',required=True),
        return_date = fields.datetime('Fecha/Hora Retorno',required=True),
        vehicle_id = fields.many2one('vehicle.vehicle','Vehículo',readonly=False),        
        vehicle_id_asigned = fields.many2one('vehicle.vehicle','Vehículo'),
        km_start = fields.integer('Km Inicial', readonly=True),
        km_end = fields.integer('Km Final'),
        km_total = fields.function(_amount_km, string='Total Km. Ruta Aprox.', type="integer", store=True, method=True),
        desc = fields.text('Detalle Actividades'),
        state = fields.selection(_MOVILIZATION_STATE,'Estado',readonly=True),
        employee_ids = fields.many2many('hr.employee', 'employee_movi_rel','mov_id','emp_id','Empleados'),
        route_ids = fields.one2many('route.line','mov_id','Ruta'),
        movilization_order_id = fields.many2one('movilization.order','Solicitud Agrupada',help="Es la solicitud padre en la cual fue agrupada esta solicitud",readonly=True),
        observaciones = fields.text('Observaciones Vehículo'),
        observaciones_anulado = fields.text('Observaciones Anulación'),
        chofer = fields.char('Chofer',size=128,readonly=True),
        padre = fields.char('Padre',size=10),
        responsable = fields.boolean('Responsable'),
        asigned_depart = fields.boolean('Planificación Semanal'),
        vehicle_des = fields.char('Vehículo',size=128),        
        )

    _defaults = dict(          
        state = _get_movilization_state,   
        vehicle_id = _get_movilization_vehicle,             
        responsable_id= responsable_usuario,
        responsable= responsable,
        user_id = lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
        padre = 'f',
        department_id= departamento_usuario,
        )
    
    _constraints = [
        (_check_route,'Verifique que la solicitud al menos tenga una ruta',['route_ids']),
        ]

movilizationOrder()

class vehicleConfiguration(osv.Model):
    _name = "vehicle.configuration"
    _description="Configuración"


    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No puede eliminar la configuración del Tipo Activo relacionado a vehículos')
        return False
    
    def _check_reg(self, cr, uid, ids):    
        obj=self.search(cr, uid,[])
        if len(obj)>1:
            result=False
        else:
            result=True        
        return result
     
    def write(self, cr, uid, ids, vals, context):      
        obj= self.browse(cr, uid, ids)
        if 'name' in vals:
            if obj[0].name.id==vals['name']:
                return super(vehicleConfiguration, self).write(cr, uid,ids, vals, context=None)
            else:
                raise osv.except_osv('Error', 'No puede modificar la configuración del Tipo Activo relacionado a vehículos')
                return False

    _columns = dict(
        name = fields.char('Cta Activo',size=32),#fields.many2one('gt.account.asset.tipo',"Tipo Activo",required=True),
        )
    _constraints = [
        (_check_reg,'La cuenta de Tipo Activos ya ha sido configurada, no puede crear otra cuenta',['name']),
        
        ]
vehicleConfiguration()

class vehicleCategory(osv.Model):
    _name = "vehicle.category"
    _description="Categoría de Vehículos"

    _INTERNAL_TYPE = [('planta','Institucional'),('contratado','Contratado')]

       
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No pueden eliminar la configuración de categorías de vehículos')
        return False
    
    
    _columns = dict(
        name = fields.char('Categoría',size=32,required=True),
        cost_day= fields.float('Costo por Día'),
        cost_km= fields.float('Costo por Kilometraje'),
        
        )

vehicleCategory()

class vehicleAsistencia(osv.Model):
    _name = "vehicle.asistencia"
    _description="Registro de Asistencia de Vehículos Contratados"
    _order= 'fecha desc'
    
    _columns = dict(
        vehicle_id = fields.many2one('vehicle.vehicle' ,'Vehículo',required=True),
        responsable_id = fields.many2one('hr.employee' ,'Responsable del Día',required=True),
        fecha = fields.date('Fecha',required=True),                
        hora_entrada= fields.float('Hora Entrada',required=True),
        hora_salida= fields.float('Hora Salida',required=True),              
        )
           
    def validar_hora(self, cr, uid,horas): 
        for line in self.browse(cr, uid, horas):        
            if line.hora_entrada>=0 and line.hora_entrada<=23.59 :                    
                return True
            else:
                return False
            if line.hora_salida>=0 and line.hora_salida<=23.59 :                    
                return True
            else:
                return False
            if line.hora_entrada>line.hora_salida:            
                return False
            else:
                return True        
            
    def validar_tiempo(self, cr, uid, ids, fecha1,context=None):
        res_value = {}        
        if fecha1:
            res_value['fecha']=fecha1
            if str(fecha1)>str(time.strftime('%Y-%m-%d')):
                res_value['fecha']=""
                return {'warning': {'title':'Advertencia','message':'La fecha no puede ser mayor a la actual'},'value':res_value}                  
        return {'value':res_value}
    
    _sql_constraints = [
        ('unique_vehicle_day','unique(vehicle_id,fecha)','Ya esta registrado esta asistencia la asistencia de este dia')
        ]
    
    _defaults = dict(
        hora_entrada="8",
        hora_salida="18",        
        )
    
    _constraints = [
        (validar_hora,'Inconsistencia en la Horas, verifique y vuelva a ingresar',['hora_entrada','hora_salida']),
        ]
vehicleAsistencia()
