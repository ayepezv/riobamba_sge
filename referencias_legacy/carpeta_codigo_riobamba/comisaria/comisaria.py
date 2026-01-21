# -*- coding: utf-8 -*-
##############################################################################
#
# GADMLI
#
##############################################################################


from osv import osv, fields
from decimal_precision import decimal_precision as dp
import time

class predio(osv.Model):
    _name = 'predio'
    _description = 'predios'
    _order = 'name'
    
#verificar tamaño del predio
    def _check_predio_tamano(self, identificador):
        if len(identificador) == 18:
            return True
        elif len(identificador) > 18:
            return False
        else:
            if len(identificador) < 18:
                return  False
        
#verificar que el predio sea entero

    def _check_predio(self, cr, uid, ids):
        for predio in self.browse(cr, uid, ids):
                try:
                    ident=int(predio.name)
                except ValueError:
                    raise osv.except_osv(('Aviso !'), 'El predio no puede contener caracteres')
                return self._check_predio_tamano(predio.name)
                          
    def _check_identificador_unico_predio(self, cr, uid, ids):
        predio_obj = self.pool.get('predio')# se pasa el objeto predio a predio_obj es decir todos los campos de esa clase o tabla
        for pre in self.browse(cr, uid, ids):# se hace la lectura actual del formulario en el que estamos
            predio_ids = predio_obj.search(cr, uid, [('name','=',pre.name),('id','!=',pre.id)]) #COMO ES LA COMPARACION del id
            if predio_ids:
                return False
        return True

    _columns = dict(
        name=fields.char('Numero de Predio',size=18, required= True, help='Numero de Predio: Pro-Can-Parr-Zon-Sec-Man-Pred' ), 
        cliente_id=fields.many2one('cliente','Cliente'), #muchas predios pertenecen a un cliente
                                 #nombre del objeto, y la etiquetaa

)

    _constraints = [
        (_check_identificador_unico_predio,'El identificador es unico, por favor verifiquelo',['name']),
        (_check_predio, 'Error el Numero de predio es de 18 caracteres', ['name'])
        ]


    _defaults = dict(
        name = '0',
        )
predio()

class cliente(osv.Model):
    _name = 'cliente'
    _description = 'clientes'
    _order = 'name'
    
#verificar la cedula
    def _check_cedula(self, identificador):
        if len(identificador) == 13 and not identificador[10:13] == '001':
            return False
        elif len(identificador) > 10:
            return False
        else:
            if len(identificador) < 10:
                return  False
        coef = [2,1,2,1,2,1,2,1,2]
        cedula = identificador[:9]
        suma = 0
        for c in cedula:
            val = int(c) * coef.pop()
            suma += val > 9 and val-9 or val
        result = 10 - ((suma % 10)!=0 and suma%10 or 10)
        if result == int(identificador[9:10]):
            return True
        else:
            return False

#verificar el ruc

    def _check_ruc(self, cliente):
        ruc = cliente.cedula
        if len(ruc) == 13:
            return True
        else:
            return False

#hace la primera verificacion
    def _check_ced_ruc(self, cr, uid, ids):
        for cliente in self.browse(cr, uid, ids):
            if cliente.type_ced_ruc == 'otro':
                return True
            if not cliente.cedula:
                return True
            if cliente.type_ced_ruc == 'pasaporte':
                return True
            if cliente.type_ced_ruc == 'cedula':
                try:
                    ident=int(cliente.cedula)
                except ValueError:
                    raise osv.except_osv(('Aviso !'), 'Cedula no puede contener caracteres')
                return self._check_cedula(cliente.cedula)
            elif cliente.type_ced_ruc == 'ruc':
                try:
                    ident=int(cliente.cedula)
                except ValueError:
                    raise osv.except_osv(('Aviso !'), 'RUC no puede contener caracteres')
                return self._check_ruc(cliente)
            else:
                return False                   

    def _check_identificador_unico(self, cr, uid, ids):
        cliente_obj = self.pool.get('cliente')
        for cliente in self.browse(cr, uid, ids):
            cliente_ids = cliente_obj.search(cr, uid, [('cedula','=',cliente.cedula),('id','!=',cliente.id)]) #COMO ES LA COMPARACION
            if cliente_ids:
                return False
        return True

    _columns = dict(
        cedula=fields.char('Cedula / RUC',size=13, required= True, help='Idenficacion o Registro Unico de Contribuyentes' ), 
 	name=fields.char('Nombre',size=128),
	direccion=fields.char('Direccion',size=128),
	telefono=fields.char('telefono',size=20),
	sexo = fields.selection([('M','Masculino'),('F','Femenino')],'Sexo'),
        type_ced_ruc = fields.selection([('cedula','Cedula'),
                                          ('ruc','RUC'),
                                          ('pasaporte','Pasaporte'),
                                          ('otro', 'OTRO')], 'Tipo ID', required=True),
)

    _constraints = [
        (_check_identificador_unico,'El identificador es unico, por favor verifiquelo',['cedula']),
        (_check_ced_ruc, 'Error en su Cedula/RUC/Pasaporte', ['cedula'])
        ]

    _defaults = dict(
        cedula = '0',
        )
cliente()



class multa(osv.Model):
    _name = 'multa'
    _description = 'multas'
    _order = 'name'
    
    _columns = dict(
        name=fields.char('descripcion',size=555), # SE AUMENTO
        ordenanza_id=fields.many2one('ordenanza','Ordenanza'), #muchas multas pertenecen a una ordenanza
)
multa()

class ordenanza(osv.Model):
    _name = 'ordenanza'
    _description = 'ordenanzas'
    _order = 'name'
    
    _columns = dict(
        name=fields.char('descripcion',size=255),
)
ordenanza()

class notificacion(osv.Model):
    _name = 'notificacion'
    _description = 'notificaciones'
    _order = 'name'
    

    def print_notificacion(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de retencion
        '''                
        if not context:
            context = {}
        caja = self.browse(cr, uid, ids, context)[0]  #busca un registro el que estaactualmente
        datas = {'ids' : [caja.id],
                 'model': 'notificacion'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'notificacion',  
            'model': 'notificacion',
            'datas': datas,
            'nodestroy': True,            
                }

    def print_multa(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte 
        '''
        for this in self.browse(cr, uid, ids):                
            if this.fecha2 == False and this.fecha3 == False:
                raise osv.except_osv('Advertencia','Debe haber ingresado las fechas de la 2da y 3era notificación')
	        return False
            else:
                if not context:
                    context = {}
                caja2 = self.browse(cr, uid, ids, context)[0]  #busca un registro el que estaactualmente
                datas2 = {'ids' : [caja2.id],
                         'model': 'notificacion'}
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'reporte_notificacion_multa',  
                    'model': 'notificacion',
                    'datas': datas2,
                    'nodestroy': True,            
                     }

    def print_todas_notificaciones(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de retencion
        '''                
        if not context:
            context = {}
        caja1 = self.browse(cr, uid, ids, context)[0]  #que hace o solo busca el primer registro
        datas1 = {'ids' : [caja1.id],
                 'model': 'notificacion'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'notificacion_all',  
            'model': 'notificacion',
            'datas': datas1,
            'nodestroy': True,            
                }

    def pulsar_cliente(self,cr,ids,context=None):
        return {'value':{'predio_id':''}}

    def pulsar_ordenanza(self,cr,ids,context=None):
        return {'value':{'multa_id':''}}

    def _get_user(self, cr, uid, ids, context=None):
        return uid

    def return_borrador(self, cr, uid, ids, context=None):  # esta de arreglar
        self.write(cr, uid, ids, {'state':'Borrador','notificacion1':False})
        return True

    def return_notificacion1(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'Notificacion1','notificacion2':False})
        return True

    def cambia_notificacion1(self, cr, uid, ids, context=None):
	
        for this in self.browse(cr, uid, ids):
                if this.name=='/':
                    obj_sequence = self.pool.get('ir.sequence')  # vamos a otro objeto para coger algun valor y colocamos en una variable
                    aux_name = obj_sequence.get(cr, uid, 'notificacion')
                    self.write(cr, uid, ids, {'state':'Notificacion1','name':aux_name,'notificacion1':True})# modifico los campos de notificacion1 y name
                else:
                    self.write(cr, uid, ids, {'state':'Notificacion1','notificacion1':True})# modifico el campo State: notificacion 1	
        return True

    def cambia_notificacion2(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
	    if this.notificacion1==True and this.fecha2 != False and this.empleado_id2 != False:
                self.write(cr, uid, ids, {'state':'Notificacion2','notificacion2':True})
            else:
                raise osv.except_osv('Advertencia','Debe ingresar la segunda fecha de Notificacion o el policia que le notificó por segunda vez')
	        return False
        return True


    def cambia_notificacion3(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.notificacion2==True and this.notificacion1==True and this.fecha3 != False and this.empleado_id3 != False:
                self.write(cr, uid, ids, {'state':'Notificacion3','notificacion3':True})
            else:
                raise osv.except_osv('Advertencia','Debe ingresar la Tercera fecha de Notificación o el policia que le notificó por tercera vez')
	        return False
        return True



    def _check_notificacion_unica(self, cr, uid, ids):
        notificacion_obj = self.pool.get('notificacion')
        for notificacion in self.browse(cr, uid, ids):
            notificacion_ids = notificacion_obj.search(cr, uid, [('multa_id','=',notificacion.multa_id.id),		('ordenanza_id','=',notificacion.ordenanza_id.id),('cliente_id','=',notificacion.cliente_id.id),('predio_id','=',notificacion.predio_id.id)])
            if len(notificacion_ids)>1:#
                return False
        return True

    def _compute_total(self, cr, uid, ids, a, b, c): # explicar por que coje con todas esas variables
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            aux = aux + 1
        res[this.id] = aux
        return res

    _columns = dict(
	name=fields.char('Codigo',size=5),
	fecha=fields.date('Fecha 1era Not.'),
        fecha2=fields.date('Fecha 2da Not.'),
	fecha3=fields.date('Fecha 3ra Not.'),
        fecha_actual=fields.date('Fecha Informe'),
        create_user_id = fields.many2one('res.users','Creado por'), 
 	notificacion1 = fields.boolean('Primera Notificacion'),
 	notificacion2 = fields.boolean('Segunda Notificacion'),
 	notificacion3 = fields.boolean('Tercera Notificacion Multa'),
 	direccion=fields.char('Direccion',size=128),
	observaciones=fields.text('Observaciones',size=255),
	ordenanza_id=fields.many2one('ordenanza','Ordenanza'),
        multa_id=fields.many2one('multa','Multa'),
	cliente_id=fields.many2one('cliente','Cliente'),
	predio_id=fields.many2one('predio','Predio'),
	empleado_id=fields.many2one('hr.employee','Policia que notificó por primera vez'),
        empleado_id2=fields.many2one('hr.employee','Policia que notificó por segunda vez'),
        empleado_id3=fields.many2one('hr.employee','Policia que notificó por tercera vez'),
        supervisor_id=fields.many2one('hr.employee','Supervisor de Comisaría'),
        comisario_id=fields.many2one('hr.employee','Comisario Municipal'),
	state = fields.selection([('Borrador','Borrador'),('Notificacion1','Notificacion 1'),('Notificacion2','Notificacion 2'),('Notificacion3','Notificacion 3 Multa')],'Estado'),
	foto =  fields.binary('foto'),
        foto1 =  fields.binary('foto1'),
        foto2 =  fields.binary('foto2'),
        foto3 =  fields.binary('foto3'),
        #cantidad = fields.float('Total Value',  digits_compute=dp.get_precision('state')),
        cantidad = fields.function(_compute_total,string='Total',type="float",store=True),
)
    _constraints = [
        (_check_notificacion_unica,'El cliente ya tiene notificacion en esa ordenanza con ese articulo, No puede crearlo',['multa_id'])
       
        ]

    _defaults = dict(
	name = '/',
        state = 'Borrador',
        create_user_id = _get_user,
	notificacion1=False,
        fecha = lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        fecha_actual = lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        
        )
notificacion()



