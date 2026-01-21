# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
##############################################################################
import addons
from osv import fields, osv
import time
import datetime
from tools import ustr
from gt_tool import XLSWriter
##reporte de viaticos LOTAIP
class viaticoLotaip(osv.TransientModel):
    _name = 'viatico.lotaip'
    _columns = dict(
        date_start = fields.date('Desde'),
        date_end = fields.date('Hasta'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def calcular_exportar_lotaip(self, cr, uid, ids, context=None):
        viatico_obj = self.pool.get('viaticos.solicitud')
        for this in self.browse(cr, uid, ids):
            viatico_ids = viatico_obj.search(cr, uid, [('state','=','Pagado'),('fecha_solicitud','>=',this.date_start),('fecha_solicitud','<=',this.date_end)])
            writer = XLSWriter.XLSWriter()
            writer.append([ustr('Art. 7 de la Ley Orgánica de Transparencia y Acceso a la Información Pública - LOTAIP')])
            writer.append([ustr('n) Los viáticos, informes de trabajo y justificativos de movilización nacional o internacional de las autoridades, dignatarios y funcionarios públicos')])
            writer.append([ustr('Viáticos nacionales')])
            writer.append([ustr('Nombres y apellidos de las y los servidores públicos'),ustr('Puesto insitucional'),ustr('Fecha de inicio del viaje'),ustr('Fecha de finalización del viaje'),ustr('Motivo del viaje'),ustr('Informe de actividades y productos alcanzados con justificativos de movilización'),ustr('Valor del viático')])
            if viatico_ids:
                total_completo = total_nacional = total_internacional = 0
                tvn = tvi = tpn = tpi = tc = tpt = ta = tm = tmv = 0
                for viatico_id in viatico_ids:
                    viatico = viatico_obj.browse(cr, uid, viatico_id)
                    if viatico.destinos_solicitud:
                        if viatico.destinos_solicitud[0].name=='nacional':
                            for line in viatico.detalle_solicitud:
                                if line.detalle=='VIATICOS':
                                    tvn += line.valor
                                elif line.detalle=='PASAJE AEREO NACIONAL':
                                    tpn += line.valor
                                elif line.detalle=='COMBUSTIBLE':
                                    tc += line.valor
                                elif line.detalle=='PASAJE TERRESTRE':
                                    tpt += line.valor
                                elif line.detalle=='MANTENIMIENTO VEHICULO':
                                    tmv += line.valor
                                elif line.detalle=='ALIMENTACION':
                                    ta += line.valor
                                elif line.detalle=='MOVILIZACION':
                                    tm += line.valor
                                else:
                                    a = 0
                            total_nacional += viatico.total_solicitud
                            writer.append([viatico.employee_id.complete_name,viatico.employee_id.job_id.name,viatico.fecha_salida,viatico.fecha_llegada,viatico.actividades_solicitud,viatico.actividades_informe,viatico.total_solicitud])
                writer.append([ustr('Viáticos Internacionales')])
                writer.append([ustr('Nombres y apellidos de las y los servidores públicos'),ustr('Puesto insitucional'),ustr('Fecha de inicio del viaje'),ustr('Fecha de finalización del viaje'),ustr('Motivo del viaje'),ustr('Informe de actividades y productos alcanzados con justificativos de movilización'),ustr('Valor del viático')])
                for viatico_id in viatico_ids:
                    viatico = viatico_obj.browse(cr, uid, viatico_id)
                    if viatico.destinos_solicitud:
                        if viatico.destinos_solicitud[0].name=='internacional':
                            for line in viatico.detalle_solicitud:
                                if line.detalle=='VIATICOS INTERNACIONAL':
                                    tvi += line.valor
                                elif line.detalle=='PASAJE AEREO INTERNACIONAL':
                                    tpi += line.valor
                                elif line.detalle=='COMBUSTIBLE':
                                    tc += line.valor
                                elif line.detalle=='PASAJE TERRESTRE':
                                    tpt += line.valor
                                elif line.detalle=='MANTENIMIENTO VEHICULO':
                                    tmv += line.valor
                                elif line.detalle=='ALIMENTACION':
                                    ta += line.valor
                                elif line.detalle=='MOVILIZACION':
                                    tm += line.valor
                                else:
                                    a = 0
                            total_internacional += viatico.total_solicitud
                            writer.append([viatico.employee_id.complete_name,viatico.employee_id.job_id.name,viatico.fecha_salida,viatico.fecha_llegada,viatico.actividades_solicitud,viatico.actividades_informe,viatico.total_solicitud])
                total_completo = total_nacional + total_internacional
                writer.append([ustr('TOTAL VIATICOS Y SUBSISTENCIAS NACIONALES'),tvn])
                writer.append([ustr('TOTAL VIATICOS Y SUBSISTENCIAS INTERNACIONALES'),tvi])
                writer.append([ustr('TOTAL PASAJES AEREOS NACIONALES'),tpn])
                writer.append([ustr('TOTAL PASAJES AEREOS INTERNACIONALES'),tpi])
                writer.append([ustr('TOTAL GASTO COMBUSTIBLE'),tc])
                writer.append([ustr('TOTAL MANTENIMIENTO VEHICULO'),tmv])
                writer.append([ustr('TOTAL ALIMENTACION'),ta])
                writer.append([ustr('TOTAL MOVILIZACION'),tm])
                writer.append([ustr('TOTAL REPOSICIONES PASAJES TERRESTRES'),tpt])
                writer.append([ustr('TOTAL GASTOS VIATICOS Y MOVILIZACIONES'),total_completo])
                writer.append([ustr('FECHA ACTUALIZACIÓN DE LA INFORMACIÓN:')])
                writer.append([ustr('PERIODICIDAD DE ACTUALIZACIÓN DE LA INFORMACIÓN:'),'MENSUAL'])
                writer.append([ustr('UNIDAD POSEEDORA DE LA INFORMACIÓN - LITERAL n):')])
                writer.append([ustr('RESPONSABLE DE LA UNIDAD POSEEDORA DE LA INFORMACIÓN DEL LITERAL n):')])
                writer.append([ustr('CORREO ELECTRÓNICO DEL O LA RESPONSABLE DE LA UNIDAD POSEEDORA DE LA INFORMACIÓN:')])
                writer.append([ustr('NÚMERO TELEFÓNICO DEL O LA RESPONSABLE DE LA UNIDAD POSEEDORA DE LA INFORMACIÓN:')])
        writer.save("InformeViaticos.xls")
        out = open("InformeViaticos.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'InformeViaticos.xls'})
        return True            

    def calcular_exportar_lotaip3(self, cr, uid, ids, context=None):
        viatico_obj = self.pool.get('viaticos.solicitud')
        xls_path = addons.get_module_resource('gt_doc_viaticos','xls','InformeViaticos.xls')
        rb = open_workbook(xls_path,formatting_info=True)
        directorio = os.system("mkdir viaticos")
        for this in self.browse(cr, uid, ids, context):
            viatico_ids = viatico_obj.search(cr, uid, [('fecha_solicitud','>=',this.date_start),('fecha_solicitud','<=',this.date_end)])
            #escritura de datos en el formulario de excel
            wb = copy(rb)
            ws = wb.get_sheet(0)
            if viatico_ids:
                aux = 4
                for viatico_id in viatico_ids:
                    viatico = viatico_obj.browse(cr, uid, viatico_id)
#                    ws.write(aux,0,viatico.employee_id.complete_name)
                    ws.getCells().insertRows(2,1)
#                    ws.insert_row(aux,0,viatico.employee_id.complete_name)
                    aux += 1
            #almacenamiento de datos
            nombre = "viaticos/InformeViaticos.xls"
            wb.save(nombre)
            out = open(nombre,"rb").read().encode("base64")
            self.write(cr, uid, this.id, {'datas':out, 'name':"InformeViaticos.xls",'datas_fname': 'InformeViaticos.xls'})

    _defaults = dict(
        date_start = time.strftime('%Y-%m-%d'),
        date_end = time.strftime('%Y-%m-%d'),
    )

viaticoLotaip()
##

class hr_job_viaticos(osv.osv):
    #Agregamos el campo necesario para la configuracion de viaticos en los puestos de trabajo
    _inherit = 'hr.job'
    _columns = {
        'nivel_viaticos_id': fields.many2one('viaticos.niveles', 'Nivel para Viáticos'),
    }
    
hr_job_viaticos()

class niveles(osv.osv):
    _name = 'viaticos.niveles'
    _description = 'Niveles usados para el cálculo de viáticos'
    
    _columns = {
                'name': fields.char('Nombre del Nivel', size=20),
                'cargos_ids': fields.one2many('hr.job', 'nivel_viaticos_id', 'Cargos'),
                }
niveles()

class city_viaticos(osv.osv):
    #Agregamos el campo necesario para la configuracion de viaticos en los cantones
    _inherit = 'res.country.state.canton'
    _columns = {
                'zona_viaticos_id': fields.many2one('viaticos.zonas', 'Zona para Viáticos'),
                }
    
city_viaticos()

class zonas(osv.osv):
    _name = 'viaticos.zonas'
    _description = 'Zonas usadas para el cálculo de Viáticos - Nacional'
        
    _columns = {
                'name': fields.char('Nombre de la Zona', size=40),
                'ciudad_ids': fields.one2many('res.country.state.canton', 'zona_viaticos_id', 'Cantones'),
                'salidas': fields.boolean('Considera salidas al campo?', help='Activar si la zona es también considerada para salidas al campo')
                }
zonas()

class pais_viaticos(osv.osv):
    #Agregamos el campo necesario para la configuracion de viaticos internacionales en paises
    _inherit = 'res.country'
    _columns = {
                'zona_viaticos_id': fields.many2one('viaticos.zonas.internacional', 'Zona para Viáticos'),
                }
pais_viaticos()


class zonas_internacionales(osv.osv):
    _name = 'viaticos.zonas.internacional'
    _description = 'Tabla para el cálculo de Viáticos - Internacional'
    
    _columns = {
                'name': fields.char('Descripcion', size=100),
                'niveles': fields.one2many('viaticos.zonas.internacional.niveles', 'cabecera_id', 'Niveles'),
                'coeficientes': fields.one2many('viaticos.zonas.internacional.coeficientes', 'cabecera_id', 'Coeficientes por País'),
                }
    
    _defaults = {
                 'name': 'Tabla de configuración para Viáticos Internacionales'
                 }
    
    def create(self, cr, uid, values, context=None):
        ids = self.search(cr, uid, [])
        if ids:
            raise osv.except_osv('Error de configuración', 'Debe existir solo 1 registro de configuración')
        else:
            return super(zonas_internacionales, self).create(cr, uid, values, context=context)
        
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar el registro de configuración')
        return False
    
zonas_internacionales()


class zonas_internacionales_coeficientes(osv.osv):
    _name = 'viaticos.zonas.internacional.coeficientes'
    _description = 'Coeficientes para el cálculo de Viáticos - Internacional'
    _order = 'nombre asc'
    _columns = {
                'name': fields.many2one('res.country', 'País', domain=[('id','!=',64)]),
                'nombre': fields.related('name', 'name', type="char", size=50, store=True, string="Pais"),
                'coeficiente': fields.float('Coeficiente'),
                'cabecera_id': fields.many2one('viaticos.zonas.internacional','Reglamento Viáticos - Internacional')
                }
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.name.name
            res.append((record.id, name))
        return res
    
zonas_internacionales_coeficientes()

class zonas_internacionales_niveles(osv.osv):
    _name = 'viaticos.zonas.internacional.niveles'
    _description = 'Zonificación para el cálculo de Viáticos - Internacional'
    
    _columns = {
                'name': fields.many2one('viaticos.niveles', 'Nivel'),
                'valor_viatico': fields.float('Valor viático'),
                'valor_subsistencia': fields.float('Valor subsistencia'),
                'cabecera_id': fields.many2one('viaticos.zonas.internacional','Reglamento Viáticos - Internacional')
                }
zonas_internacionales_niveles()


class tabla_viaticos_line(osv.osv):
    _name = 'viaticos.tabla.line'
    _description = 'Linea de la tabla de cálculo para viáticos nacionales'
    _order = 'zona_id asc, nivel_id asc'
    
    def _validar_mayor_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.valor_viatico < 0:
            return False
        if obj.valor_subsistencia < 0:
            return False
        if obj.valor_alimentacion < 0:
            return False
        return True
    
    _columns = {
                'tabla_id': fields.many2one('viaticos.tabla', 'Tabla de Viáticos'),
                'zona_id': fields.many2one('viaticos.zonas', 'Zona'),
                'nivel_id': fields.many2one('viaticos.niveles', 'Nivel'),
                'valor_viatico': fields.float('Valor viático'),
                'valor_subsistencia': fields.float('Valor subsistencia'),
                'valor_alimentacion': fields.float('Valor alimentación'),
                'descripcion': fields.text('Descripción'),
                }
    
    _sql_constraints = [
                        ('unico_zona_nivel', 'UNIQUE(zona_id,nivel_id)', 'Solo puede configurar una vez el par Zona-Nivel') 
                        ]
    
    _constraints = [
                    (_validar_mayor_cero, 'Los valores deben ser superiores a cero', ['valor_viatico','valor_subsistencia','valor_alimentacion']),
                    ]
    
tabla_viaticos_line()

class tabla_viaticos(osv.osv):
    _name = 'viaticos.tabla'
    _description = 'Tabla para el cálculo de viáticos'
    
    def _validar_porcentaje(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.porcentaje_nacional < 0 or obj.porcentaje_nacional > 100:
            return False
        return True
    
    _columns = {
                'name': fields.char('Descripcion', size=100),
                'porcentaje_nacional': fields.float('Porcentaje nacional a ser justificado', help="Porcentaje entre 0-100 que debe ser justificado mediante facturas por gastos nacionales"),
                'line_ids': fields.one2many('viaticos.tabla.line', 'tabla_id', 'Detalle'),
                }
    
    _defaults = {
                 'name': 'Tabla de configuracion para Viáticos Nacionales'
                 }

    _constraints = [
                    (_validar_porcentaje, 'El valor es un porcentaje que debe estar entre 0 - 100', ['valor']),
                    ]
    
    def create(self, cr, uid, values, context=None):
        ids = self.search(cr, uid, [])
        if ids:
            raise osv.except_osv('Error de configuración', 'Debe existir solo 1 registro de configuración')
        else:
            return super(tabla_viaticos, self).create(cr, uid, values, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar el registro de configuración')
        return False
    
tabla_viaticos()

class viaticos_account(osv.osv):
    _name = 'viaticos.account'
    _description = 'Tabla de configuracion de viáticos con la seccion financiera'
    
    _columns = {
                #'project_id': fields.many2one('project.project', 'Proyecto'),
                'active': fields.boolean('Configuracion Activa'),
                'pay_account_id': fields.many2one('account.account', 'Cuenta de Viatico'),
                'expense_account_id': fields.many2one('account.account', 'Cuenta de Banco'),
                'journal_id': fields.many2one('account.journal', 'Diario'),
                
                #'budget_line_id': fields.many2one('crossovered.budget.lines','Partida Presupuestaria'),
                }
    
viaticos_account()

class viaticoRuta(osv.Model):
    _name = 'viatico.ruta'
    _columns = dict(
        name = fields.char('Ruta',size=32),
    )
viaticoRuta()

class viaticos_destinos(osv.osv):
    _name = 'viaticos.destinos'
    _description = 'Linea de destinos en viaticos'
    _columns = {
        'name': fields.selection([('nacional','Nacional'),('internacional','Internacional')], 'Tipo'),
        'ciudad_id': fields.many2one('res.country.state.canton', 'Localidad'),
        'country_id':fields.many2one('res.country', 'Pais'),
        'pais_id': fields.many2one('viaticos.zonas.internacional.coeficientes', 'País'),
        'ciudad_internacional': fields.char('Ciudad', size=32),
    #'ciudad_internacional': fields.many2one('res.country.state.city','Ciudad'),
        'fecha_salida': fields.datetime('Desde'),
        'fecha_llegada': fields.datetime('Hasta'),
        'solicitud_id': fields.many2one('viaticos.solicitud', 'Solicitud de Viáticos'),
        'informe_id': fields.many2one('viaticos.solicitud', 'Informe de Viáticos'),
        'tipo_nombre':fields.char('Nombre Transporte',size=32),
        'tipo':fields.selection([('Aereo','Aereo'),('Terrestre','Terrestre'),('Propio','Propio'),('Otros','Otros')],'Tipo Transporte'),
        'ruta_id':fields.many2one('viatico.ruta','Ruta'),
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

viaticos_destinos()


class solicitud_line(osv.osv):
    _name = 'viaticos.solicitud.line'
    _description = 'Linea de costos en viáticos'
    _columns = {
        #'detalle': fields.char('Detalle', size=50,required=True),
        'detalle':fields.selection([('VIATICOS','VIATICOS NACIONAL'),('VIATICOS INTERNACIONAL','VIATICOS INTERNACIONAL'),
                                    ('PASAJE AEREO NACIONAL','PASAJE AEREO NACIONAL'),('MANTENIMIENTO VEHICULO','MANTENIMIENTO VEHICULO'),
                                    ('ALIMENTACION','ALIMENTACION'),('MOVILIZACION','MOVILIZACION'),
                                    ('PASAJE AEREO INTERNACIONAL','PASAJE AEREO INTERNACIONAL'),('COMBUSTIBLE','COMBUSTIBLE'),
                                    ('PASAJE TERRESTRE','PASAJE TERRESTRE')],'Detalle',required=True),
        'cantidad': fields.float('Cantidad'),
        'valor': fields.float('Valor'),
        'solicitud_id': fields.many2one('viaticos.solicitud', 'Solicitud de Viáticos'),
        'informe_id': fields.many2one('viaticos.solicitud', 'Informe de Viáticos'),
    }
    
    def _validar_mayor_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.valor < 0:
            return False
        if obj.cantidad < 0:
            return False
        return True

    _constraints = [
                    (_validar_mayor_cero, 'En el detalle, el valor y la cantidad deben ser mayores a cero', ['valor', 'cantidad']),
                    ]
    
solicitud_line()

class solicitud_transporte(osv.osv):
    _name = 'viaticos.solicitud.transporte'
    _description = 'Transporte en formulario de viáticos'
    _columns = {
                #'name': fields.char('Nombre del transporte', size=30),
                'tipo': fields.selection([('aereo','Aéreo'),('terrestre','Terrestre'),('maritimo','Maritimo'),('otro','Otro')],'Tipo de transporte'),
                'origen': fields.char('Origen', size=30),
                'destino': fields.char('Destino', size=30),
                'name': fields.char('Descripción del transporte', size=30),
                'reembolso': fields.boolean('Solicita reembolso?', help="Active este campo en caso de solicitar un reembolso de este valor. ACTIVARLO NO ASEGURA QUE USTED RECIBA EL VALOR SOLICITADO. El caso será analizado por Talento Humano"),
                'valor': fields.float('Valor'),
                'fecha_salida': fields.datetime('Fecha y hora de salida'),
                'fecha_llegada': fields.datetime('fecha y hora de llegada'),
                'solicitud_id': fields.many2one('viaticos.solicitud', 'Solicitud de Viáticos'),
                'informe_id': fields.many2one('viaticos.solicitud', 'Informe de Viáticos'),
                }
    
    
    def validar_tiempo(self, cr, uid, ids, fecha1, fecha2, context=None):
        #funcion para colocar los segundos de las fechas en cero, ademas de validar que la fecha 2 sea mayor a la fecha1
        res_value = {}
        if fecha1:
            time_fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_fecha1 = time_fecha1.replace(second=00)
            res_value['fecha_salida']=str(time_fecha1)
        if fecha2:
            time_fecha2 = datetime.datetime.strptime(fecha2, "%Y-%m-%d %H:%M:%S")
            time_fecha2 = time_fecha2.replace(second=00)
            res_value['fecha_llegada']=str(time_fecha2)
        if fecha1 and fecha2:
            time_salida = datetime.datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_llegada = datetime.datetime.strptime(fecha2, "%Y-%m-%d %H:%M:%S")
            if time_salida>=time_llegada:
                return {'warning': {'title':'Advertencia','message':'La fecha de llegada debe ser mayor a la de salida'}}
        return {'value':res_value}
    
    def _valor_mayor_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.valor < 0:
            return False
        return True

    _constraints = [
                    (_valor_mayor_cero, 'En los campos de transporte, el valor debe ser mayor a cero', ['valor']),
                    ]
    
solicitud_transporte()

class viaticos_log(osv.osv):
    _name = 'viaticos.log'
    _description = 'Historial en la solicitud e informe de viáticos'
    _order = "fecha desc"
    _columns = {
                'name': fields.char('Descripción', size=128, required=True),
                'user_id': fields.many2one('res.users','Usuario Responsable', required=True),
                'fecha': fields.datetime('Fecha de creación', required=True),
                'viatico_id': fields.many2one('viaticos.solicitud', 'Viático'),
                }
    
    _defaults = {
                 'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                 }
    
viaticos_log()

class viaticos_facturas_tipo(osv.osv):
    _name = 'viaticos.facturas.tipo'
    _description = 'Tipo de Facturas para el informe de viaticos'
    _order = "name asc"
    _columns = {
                'name': fields.char('Tipo', size=50, required=True),
                }
    
viaticos_facturas_tipo()

class viaticos_facturas(osv.osv):
    _name = 'viaticos.facturas'
    _description = 'Facturas para el informe de viaticos'
    _order = "fecha asc"
    _columns = {
                'name': fields.char('Núm. de factura', size=20, required=True),
                'descripcion': fields.char('Descripción', size=100),
                'tipo_id': fields.many2one('viaticos.facturas.tipo','Tipo de Gasto', required=True),
                'fecha': fields.date('Fecha de factura', required=True),
                'city_id': fields.many2one('res.country.state.canton','Localidad'),
                'viatico_id': fields.many2one('viaticos.solicitud', 'Viático'),
                'proveedor': fields.char('Proveedor', size=50),
                'valor': fields.float('Valor', required=True),
                }
    
    def _validar_mayor_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.valor <= 0:
            return False
        return True

    _constraints = [
                    (_validar_mayor_cero, 'El valor debe ser mayor a cero', ['valor']),
                    ]
    
viaticos_facturas()


class solicitud_viaticos(osv.osv):
    _name = 'viaticos.solicitud'
    _description = 'Solicitud de viaticos'
    _order = 'name desc, id desc'
    
    def _cargar_departamento_empleado(self, cr, uid, context=None):
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return usuario.context_department_id.id

    def cambiar_departamento(self, cr, uid, ids, department_id, context={}):
        return {'value':{'employee_id': False}}
    
    def _cargar_empleado(self, cr, uid, context=None):
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        empleado = usuario.employee_id
        return empleado.id

    def _cargar_usuario(self, cr, uid, context=None):
        return uid
    
    def _cargar_puesto_empleado(self, cr, uid, context=None):
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return usuario.job_id.id
    
    def _calculate_total_solicitud_facturas(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        tabla = self.pool.get('viaticos.tabla').browse(cr, uid, 1, context)
 #       for line in self.browse(cr, uid, ids, context=context):
 #           res[line.id] = 0
 #           for detalle in line.detalle_solicitud:
 #               if detalle.detalle.find(" Nacional") >= 0:
 #                   res[line.id] = res[line.id] + detalle.valor
 #           res[line.id] = (res[line.id]/100)*tabla.porcentaje_nacional
        return res
    
    def _calculate_total_solicitud_empleado(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        tabla = self.pool.get('viaticos.tabla').browse(cr, uid, 1, context)
#        for line in self.browse(cr, uid, ids, context=context):
#            res[line.id] = 0
#            for detalle in line.detalle_solicitud:
#                if detalle.detalle.find(" Nacional") >= 0:
#                    res[line.id] = res[line.id] + detalle.valor
#            res[line.id] = (res[line.id]/100.0)*(100.0-tabla.porcentaje_nacional)
        return res
    
    def _calculate_total_porcentaje_facturas(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        tabla = self.pool.get('viaticos.tabla').browse(cr, uid, 1, context)
#        for line in self.browse(cr, uid, ids, context=context):
#            res[line.id] = tabla.porcentaje_nacional
        return res
    
    def _calculate_total_porcentaje_empleado(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        tabla = self.pool.get('viaticos.tabla').browse(cr, uid, 1, context)
 #       for line in self.browse(cr, uid, ids, context=context):
 #           res[line.id] = 100.0 - tabla.porcentaje_nacional
        return res
    
    def _calculate_total_informe_facturas(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        tabla = self.pool.get('viaticos.tabla').browse(cr, uid, 1, context)
  #      for line in self.browse(cr, uid, ids, context=context):
  #          res[line.id] = 0
  #          for detalle in line.detalle_informe:
  #              if detalle.detalle.find(" Nacional") >= 0:
  #                  res[line.id] = res[line.id] + detalle.valor
  #          res[line.id] = (res[line.id]/100)*tabla.porcentaje_nacional
        return res
    
    def _calculate_total_informe_empleado(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        tabla = self.pool.get('viaticos.tabla').browse(cr, uid, 1, context)
#        for line in self.browse(cr, uid, ids, context=context):
#            res[line.id] = 0
#            for detalle in line.detalle_informe:
#                if detalle.detalle.find(" Nacional") >= 0:
#                    res[line.id] = res[line.id] + detalle.valor
#            res[line.id] = (res[line.id]/100)*(100 - tabla.porcentaje_nacional)
        return res
    
    def _calculate_total_solicitud(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            for detalle in line.detalle_solicitud:
                res[line.id] = res[line.id] + detalle.valor
        return res
    
    def _calculate_total_facturas(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
#        for line in self.browse(cr, uid, ids, context=context):
#            res[line.id] = 0
#            for factura in line.facturas_ids:
#                res[line.id] = res[line.id] + factura.valor
        return res
    
    def _calculate_total_informe(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
#        for line in self.browse(cr, uid, ids, context=context):
#            res[line.id] = 0
#            for detalle in line.detalle_informe:
#                res[line.id] = res[line.id] + detalle.valor
        return res
    
    def _calculate_fecha_salida(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            for detalle in line.detalle_informe:
                res[line.id] = res[line.id] + detalle.valor
        return res

    def _obtener_jefe(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
#        for line in self.browse(cr, uid, ids, context=context):
#            res[line.id] = 0
#            if line.department_id.manager_id.id == line.employee_id.id:
#                res[line.id] = line.department_id.parent_id.manager_id.id
#            else:
#                res[line.id] = line.department_id.manager_id.id
        return res
    
    def _calculate_total_reajuste(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.total_facturas >= line.total_informe_facturas:
                res[line.id] = line.total_informe - line.total_anticipo
            else:
                res[line.id] = (line.total_informe - line.total_anticipo) - (line.total_informe_facturas - line.total_facturas)
                #if line.total_facturas >= line.total_informe_empleado:
                #    res[line.id] = (line.total_informe - line.total_anticipo) - line.total_informe_facturas + line.total_facturas + line.total_informe_empleado
                #else:
                #    res[line.id] = line.total_informe_empleado - line.total_anticipo
        return res
    
    def _get_bank(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        for this in self.browse(cr, uid, ids):
            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',this.employee_id.name)])
            if partner_ids:
                cuenta_ids = bank_obj.search(cr, uid, [('partner_id','=',partner_ids)])
                if cuenta_ids:
                    res[this.id] = cuenta_ids[0]
        return res

    _columns = {
        'hora_inicio_actividades':fields.float('Hora Inicio Actividades'),
        'autorizado_id': fields.many2one('hr.employee','Autorizado por'),
        'aprobado_id': fields.many2one('hr.employee','Aprobado por'),
        'bank_id':fields.function(_get_bank, type="many2one",relation="res.partner.bank",string='Cuenta Banco'),
        'ciudad_comision':fields.many2one('res.country.state.canton','Ciudad Comision'),
        'is_viatico':fields.boolean('VIATICOS'),
        'is_movilizacion':fields.boolean('MOVILIZACIONES'),
        'is_subsistencia':fields.boolean('SUBSISTENCIAS'),
        'is_alimentacion':fields.boolean('ALIMENTACION'),
        'name': fields.char('N. Orden de movilización', size=10),
        'jefe_id': fields.function(_obtener_jefe, method=True, type='integer', string='Jefe', store=True),
        'fecha_solicitud': fields.date('Fecha de solicitud'),
        'fecha_informe': fields.datetime('Fecha de informe'),
        'department_id': fields.many2one('hr.department', 'Departamento'),
        'department_name': fields.char('Departamento', size=50),
        'employee_id': fields.many2one('hr.employee', 'Servidor'),
        'usuario_id': fields.many2one('res.users', 'Usuario'),
        'job_id': fields.many2one('hr.job', 'Cargo'),
        'ocupational_id': fields.many2one('grupo.ocupacional', 'Grupo Ocupacional'),
        'de_sindicato': fields.boolean('Sindicato de Obreros', help='Marque la casilla en caso de que la orden de movilización pertenezca al sindicato de obreros'),
        'fecha_salida': fields.datetime('Fecha y hora de salida'),
        'fecha_llegada': fields.datetime('Fecha y hora de llegada'),
        'transporte_ids': fields.one2many('viaticos.solicitud.transporte', 'informe_id', 'Transporte Utilizado'),
        'transporte_solicitud_ids': fields.one2many('viaticos.solicitud.transporte', 'solicitud_id', 'Transporte Solicitado'),
        'unidad_miembros': fields.char('Servidores que integran la comisión', size=256),
        'actividades_informe': fields.text('Actividades'),
        'actividades_solicitud': fields.text('Actividades'),
        'detalle_solicitud': fields.one2many('viaticos.solicitud.line', 'solicitud_id', 'Detalle de solicitud'),
        'detalle_informe': fields.one2many('viaticos.solicitud.line', 'informe_id', 'Detalle de informe'),
        #totales en al solicitud
        'total_solicitud': fields.function(_calculate_total_solicitud, method=True, type='float', string='Solicitud - Total ($)', store=True),
        'total_porcentaje_facturas': fields.function(_calculate_total_porcentaje_facturas, method=True, type='float', string='Necesita justificación (%)', store=True, help="Porcentaje a justificar mediante facturas por el viático nacional"),
        'total_porcentaje_empleado': fields.function(_calculate_total_porcentaje_empleado, method=True, type='float', string='No necesita justificación (%)', store=True, help="Porcentaje a favor del empleado, sin necesesidad de justificarlo mediante facturas por el viático nacional"),
        'total_solicitud_facturas': fields.function(_calculate_total_solicitud_facturas, method=True, type='float', string='($)', store=True, help="Valor a justificar mediante facturas por el viático nacional (calculado usando la información de la solicitud)"),
        'total_solicitud_empleado': fields.function(_calculate_total_solicitud_empleado, method=True, type='float', string='($)', store=True, help="Valor a favor del empleado, sin necesidad de justificar mediante facturas por el viático nacional (calculado usando la información de la solicitud)"),
        'total_anticipo': fields.float('Anticipo - Total ($)'),
        #totales en el informe
        'total_informe': fields.function(_calculate_total_informe, method=True, type='float', string='Total ($)', store=True),
        'total_facturas': fields.function(_calculate_total_facturas, method=True, type='float', string='Facturas - Total ($)', store=True),
        'total_porcentaje_facturas2': fields.function(_calculate_total_porcentaje_facturas, method=True, type='float', string='Necesita justificación (%)', store=True, help="Porcentaje a justificar mediante facturas por el viático nacional"),
        'total_porcentaje_empleado2': fields.function(_calculate_total_porcentaje_empleado, method=True, type='float', string='No necesita justificación (%)', store=True, help="Porcentaje a favor del empleado, sin necesesidad de justificarlo mediante facturas por el viático nacional"),
        'total_informe_facturas': fields.function(_calculate_total_informe_facturas, method=True, type='float', string='($)', store=True, help="Valor a justificar mediante facturas por el viático nacional (calculado usando la información del informe)"),
    'total_informe_empleado': fields.function(_calculate_total_informe_empleado, method=True, type='float', string='($)', store=True, help="Valor a favor del empleado, sin necesidad de justificar mediante facturas por el viático nacional (calculado usando la información del informe)"),
        'total_reajuste': fields.function(_calculate_total_reajuste, method=True, type='float', string='Total a cancelar ($)', store=True, help="Si el valor es positivo se debe proceder al pago, de ser negativo, se debe crear el descuento en el Rol de Pagos"),
        #
        #                'state': fields.selection([('draft','Borrador'),('solicitud1','Solicitado'),('solicitud2','Aprobado Jefe Superior'),('solicitud3','Aprobado Prefectura / Ingresar Informe'),('informe1','Informe enviado'),('informe2','Informe aprobado Jefe superior'),('done','Aprobado TTHH'),('end','Finalizado'),('cancel','Rechazado'),('anulado','Anulado')], 'Estado'),
        'state': fields.selection([('draft','Borrador'),('solicitud1','Solicitado'),('done','Realizado'),('Pagado','Pagado'),('anulado','Anulado')], 'Estado'),
        'destinos_solicitud': fields.one2many('viaticos.destinos', 'solicitud_id', 'Destinos de solicitud'),
        'destinos_informe': fields.one2many('viaticos.destinos', 'informe_id', 'Destinos de informe'),
        'log_id': fields.one2many('viaticos.log','viatico_id','Historial'),
        'facturas_ids': fields.one2many('viaticos.facturas','viatico_id','Facturas'),
        'confirmar_facturas': fields.boolean('Confirmar facturas ingresadas', help='Debe activar este casillero para confirmar que las facturas ingresadas y el monto total es el correcto'),
        'anticipo_id': fields.many2one('account.move','Anticipo'),
        'observaciones':fields.text('Observaciones'),
    }
    
    _defaults = {
                 'state': 'draft',
                 'department_id': _cargar_departamento_empleado,
                 'employee_id': _cargar_empleado,
                 'usuario_id': _cargar_usuario,
                 'job_id': _cargar_puesto_empleado,
                 'de_sindicato': False,
                 }
    
    def onchange_facturas(self, cr, uid, ids, facturas, context=None):
        print facturas
        total = 0
        obj_facturas = self.pool.get('viaticos.facturas')
        for factura in facturas:
            if factura[0]==4: #registro existente en la BD
                registro_factura = obj_facturas.browse(cr, uid, factura[1], context)
                total = total + registro_factura.valor
            if factura[0]==2: #registro existente eliminado
                total = total + 0
            if factura[0]==1: #registro existente modificado
                if factura[2].has_key('valor'):
                    total = total + factura[2]['valor']
            if factura[0]==0: #nuevo registro
                if factura[2].has_key('valor'):
                    total = total + factura[2]['valor']
        return {'value': {'total_facturas':total}}
    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar una solicitud que ya inicio el proceso')
        return False
    
    def create(self, cr, uid, values, context=None):
        values['fecha_solicitud'] = time.strftime("%Y-%m-%d %H:%M:%S")
        if values['employee_id']:
            empleado = self.pool.get('hr.employee').browse(cr, uid, values['employee_id'], context=context)
            if empleado.user_id:
                values['job_id'] = empleado.user_id.job_id.id
            else:
                values['job_id'] = empleado.job_id.id
        return super(solicitud_viaticos, self).create(cr, uid, values, context=context)


    def write(self, cr, uid, ids, values, context=None):
        if values.has_key('employee_id'):
            empleado = self.pool.get('hr.employee').browse(cr, uid, values['employee_id'], context=context)
            if empleado.user_id:
                values['job_id'] = empleado.user_id.job_id.id
            else:
                values['job_id'] = empleado.job_id.id
        return super(solicitud_viaticos, self).write(cr, uid, ids, values, context=context)

    
    def create_request(self, cr, uid, titulo, cuerpo, destinatario, context):
        return self.pool.get('res.request').create(cr, uid, {'name': titulo,
                                                             'priority': '1',
                                                             'active': True,
                                                             'act_to': destinatario,
                                                             'trigger_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                             'state': 'waiting',
                                                             #'ref_doc1': 'gt.insurance.inform,%d'% (obj_inform.id,),
                                                             'body':cuerpo
                                                             })
        
    def devolver_cargo(self, cr, uid, ids, employee_id, context=None):
        value = {}
        if employee_id:
            empleado = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            if empleado.user_id:
                value['job_id'] = empleado.user_id.job_id.id
            else:
                value['job_id'] = empleado.job_id.id
        return {'value': value}
    


    def solicitar_anticipo(self, cr, uid, ids, context={}):
        obj_account_move = self.pool.get("account.move")
        obj_account_move_line = self.pool.get("account.move.line")
        obj_configuration = self.pool.get("viaticos.account")
        configuracion_id = obj_configuration.search(cr, uid, [('active','=',True)])
        if configuracion_id:
            configuracion = obj_configuration.browse(cr, uid, configuracion_id[0])
            registro = self.browse(cr, uid, ids[0])
            move_id = obj_account_move.create(cr, uid, {'ref': 'Viatico: ' + registro.name,
                                                        'journal_id': configuracion.journal_id.id,
                                                        'date': time.strftime("%Y-%m-%d"),
                                                        'state':'draft'}, context=context)
            debit_id = obj_account_move_line.create(cr, uid, {'name': registro.employee_id.complete_name,
                                                              'move_id': move_id,
                                                              'account_id': configuracion.pay_account_id.id,
                                                              'debit': registro.total_solicitud,
                                                              'credit': 0.00})
            credit_id = obj_account_move_line.create(cr, uid, {'name': registro.employee_id.complete_name,
                                                               'move_id': move_id,
                                                               'account_id': configuracion.expense_account_id.id,
                                                               'debit': 0.00,
                                                               'credit': registro.total_solicitud})
            return self.write(cr, uid, [registro.id], {'anticipo_id': move_id})
        pass
        
    def fecha_inicio_fin(self, cr, uid, id, context={}):
        resultado = "alimentacion"
        return resultado
        fecha_salida = False
        fecha_llegada = False
        registro = self.browse(cr, uid, id, context)
        if registro.destinos_informe:
            for destino in registro.destinos_informe:
                if fecha_salida==False:
                    fecha_salida = datetime.datetime.strptime(destino.fecha_salida, "%Y-%m-%d %H:%M:%S")
                fecha_llegada = datetime.datetime.strptime(destino.fecha_llegada, "%Y-%m-%d %H:%M:%S")
            resultado = fecha_llegada - fecha_salida
            if resultado.seconds >= 6*3600:
                resultado = "subsistencia"
            elif resultado.seconds >= 4*3600:
                resultado = "alimentacion"
        elif registro.destinos_solicitud:
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
    
    def calcular_detalle(self, cr, uid, id, context={}):
        return True ##MARIO
        resultados = []
        lineas = self.pool.get('viaticos.destinos')
        obj_tabla = self.pool.get('viaticos.tabla.line')
        obj_detalle = self.pool.get('viaticos.solicitud.line')
        registro = self.browse(cr, uid, id, context)
        fecha_salida = datetime.datetime.strptime(registro.fecha_salida, "%Y-%m-%d %H:%M:%S") #DIA Y HORA DE SALIDA
        fecha_llegada = datetime.datetime.strptime(registro.fecha_llegada, "%Y-%m-%d %H:%M:%S") #DIA Y HORA DE RETORNO
        fecha_salida = fecha_salida - datetime.timedelta(hours=5)
        fecha_llegada = fecha_llegada - datetime.timedelta(hours=5)
        #print fecha_llegada
        empleado = registro.employee_id
        nivel = empleado.job_id.nivel_viaticos_id
        if registro.destinos_informe:
            try:
                registros = obj_detalle.search(cr, uid, [('informe_id','=',id)])
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
                    for destino in registro.destinos_informe:
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
                                    raise osv.except_osv('Error', 'No se encuentra configurada la tabla para este cargo y destino, comuníquese con el administrador del sistema')
                                if id_tabla:
                                    for tabla in obj_tabla.browse(cr, uid, id_tabla, context):
                                        ids_detalles = obj_detalle.search(cr, uid, [('informe_id','=',id),
                                                                                    ('detalle','like','Viatico - ' + 'Nacional: ' + destino.ciudad_id.name)])
                                        if not ids_detalles:
                                            obj_detalle.create(cr, uid, {'informe_id': id,
                                                           'detalle': 'Viatico - ' + 'Nacional: ' + destino.ciudad_id.name,
                                                           'cantidad': 1,
                                                           'valor': tabla.valor_viatico})
                                        else:
                                            registro_detalle = obj_detalle.browse(cr, uid, ids_detalles[0])
                                            obj_detalle.write(cr, uid, [registro_detalle.id], {'cantidad': registro_detalle.cantidad + 1,
                                                                                               'valor': registro_detalle.valor + tabla.valor_viatico})
                                        
                            if destino.name == 'internacional':
                                coeficiente = destino.pais_id.coeficiente
                                for nivel_internacional in destino.pais_id.cabecera_id.niveles:
                                    if nivel_internacional.name == nivel:
                                        ids_detalles = obj_detalle.search(cr, uid, [('informe_id','=',id),
                                                                                    ('detalle','like','Viatico - ' + 'Internacional: ' + destino.pais_id.name.name)])
                                        if not ids_detalles:
                                            obj_detalle.create(cr, uid, {'informe_id': id,
                                                           'detalle': 'Viatico - ' + 'Internacional: ' + destino.pais_id.name.name,
                                                           'cantidad': 1,
                                                           'valor': coeficiente*nivel_internacional.valor_viatico})
                                        else:
                                            registro_detalle = obj_detalle.browse(cr, uid, ids_detalles[0])
                                            obj_detalle.write(cr, uid, [registro_detalle.id], {'cantidad': registro_detalle.cantidad + 1,
                                                                                               'valor': registro_detalle.valor + coeficiente*nivel_internacional.valor_viatico})
                elif fecha_calculo_2>=fecha_salida and fecha_calculo_2<=fecha_llegada:
                    for destino in registro.destinos_informe:
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
                                    raise osv.except_osv('Error', 'No se encuentra configurada la tabla para este cargo y destino, comuníquese con el administrador del sistema')
                                if id_tabla:
                                    for tabla in obj_tabla.browse(cr, uid, id_tabla, context):
                                        obj_detalle.create(cr, uid, {'informe_id': id,
                                                           'detalle': 'Subsistencia - ' + 'Nacional: ' + destino.ciudad_id.name,
                                                           'cantidad': 1,
                                                           'valor': tabla.valor_subsistencia})
                                    
                            if destino.name == 'internacional':
                                coeficiente = destino.pais_id.coeficiente
                                for nivel_internacional in destino.pais_id.cabecera_id.niveles:
                                    if nivel_internacional.name == nivel:
                                        obj_detalle.create(cr, uid, {'informe_id': id,
                                                           'detalle': 'Subsistencia - ' + 'Internacional: ' + destino.pais_id.name.name,
                                                           'cantidad': 1,
                                                           'valor': coeficiente*nivel_internacional.valor_subsistencia})
                elif fecha_calculo_1>=fecha_salida and fecha_calculo_1<=fecha_llegada:
                    for destino in registro.destinos_informe:
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
                                    raise osv.except_osv('Error', 'No se encuentra configurada la tabla para este cargo y destino, comuníquese con el administrador del sistema')
                                if id_tabla:
                                    for tabla in obj_tabla.browse(cr, uid, id_tabla, context):
                                        obj_detalle.create(cr, uid, {'informe_id': id,
                                                           'detalle': 'Alimentacion - ' + 'Nacional: ' + destino.ciudad_id.name,
                                                           'cantidad': 1,
                                                           'valor': tabla.valor_alimentacion})
                            if destino.name == 'internacional':
                                coeficiente = destino.pais_id.coeficiente
                                for nivel_internacional in destino.pais_id.cabecera_id.niveles:
                                    if nivel_internacional.name == nivel:
                                        obj_detalle.create(cr, uid, {'informe_id': id,
                                                           'detalle': 'Subsistencia - ' + 'Internacional: ' + destino.pais_id.name.name,
                                                           'cantidad': 1,
                                                           'valor': coeficiente*nivel_internacional.valor_subsistencia})
                fecha_calculo = fecha_calculo_3
            #total = 0
            #for detalle in registro.detalle_informe:
            #    total += detalle.valor
            #self.write(cr, uid, [id], {'total_informe': total,
            #                           'total_reajuste': total-registro.total_solicitud})
        elif registro.destinos_solicitud:
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
                                    raise osv.except_osv('Error', 'No se encuentra configurada la tabla para este cargo y destino, comuníquese con el administrador del sistema')
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
                                    raise osv.except_osv('Error', 'No se encuentra configurada la tabla para este cargo y destino, comuníquese con el administrador del sistema')
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
                                    raise osv.except_osv('Error', 'No se encuentra configurada la tabla para este cargo y destino, comuníquese con el administrador del sistema')
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
                #quitado
#            if bandera==False:
#                raise osv.except_osv('Error de configuración', 'El tiempo no puede ser considerado para un viático, o la información de su cargo no se encuentra configurada para el cálculo.')
            #total = 0
            #for detalle in registro.detalle_solicitud:
            #    total += detalle.valor
            #self.write(cr, uid, [id], {'total_solicitud': total})
        
    def anular(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'anulado'})
    
    def rechazar(self, cr, uid, ids, context=None):
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        for solicitud in self.browse(cr, uid, ids, context):
            log_obj=self.pool.get('viaticos.log')
            log_obj.create(cr, uid, {
                              'name': 'VIATICO RECHAZADO',
                              'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                              'viatico_id': solicitud.id,
                              'user_id': uid,
                              })
        return self.write(cr, uid, ids, {'state': 'cancel'})
   
    def viatico_ejecutado(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'})
        return True

    def viatico_pagado(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'Pagado'})
        return True
     
    def solicitud_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def draft_solicitud1(self, cr, uid, ids, context=None):
        #con este procedimiento se coloca el viatico en solicitado
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        for solicitud in self.browse(cr, uid, ids, context):
            empleado = solicitud.employee_id
            if not solicitud.name:
                aux_number = self.pool.get('ir.sequence').get(cr, uid, 'viaticos.solicitud')
                descrip = ' Orden de Movilizacion: ' + aux_number + '\n' + ' Servidor: ' + ustr(empleado.complete_name) + '\n'
                super(solicitud_viaticos, self).write(cr, uid, ids, {'state': 'solicitud1','name':aux_number,})
            else:
                descrip = ' Orden de Movilizacion: ' + solicitud.name + '\n' + ' Servidor: ' + ustr(empleado.complete_name) + '\n'
                super(solicitud_viaticos, self).write(cr, uid, ids, {'state': 'solicitud1'})
            if solicitud.destinos_solicitud:
                if self.fecha_inicio_fin(cr, uid, solicitud.id, context) != 'nada':
                    self.calcular_detalle(cr, uid, solicitud.id, context)
                    super(solicitud_viaticos, self).write(cr, uid, ids, {'job_id': empleado.job_id.id})
                    log_obj=self.pool.get('viaticos.log')
                    log_obj.create(cr, uid, {
                                          'name': 'Solicitud enviada',
                                          'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                                          'viatico_id': solicitud.id,
                                          'user_id': uid,
                                          })
                else:
                    raise osv.except_osv('Error', 'No se puede continuar con el proceso, la información ingresada no corresponde para un viático')
            else:
                raise osv.except_osv('Error', 'Debe ingresar destinos')
        return True
    
    def solicitud1_solicitud2(self, cr, uid, ids, context=None):
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        for solicitud in self.browse(cr, uid, ids, context):
            log_obj=self.pool.get('viaticos.log')
            log_obj.create(cr, uid, {
                              'name': 'Solicitud aprobada por JEFE SUPERIOR',
                              'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                              'viatico_id': solicitud.id,
                              'user_id': uid,
                              })
        self.write(cr, uid, ids, {'state': 'solicitud2'})
        return True
    
    def solicitud2_solicitud3(self, cr, uid, ids, context=None):
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        for solicitud in self.browse(cr, uid, ids, context):
            for destino in solicitud.destinos_solicitud:
                ciudad = False
                pais = False
                if destino.ciudad_id:
                    ciudad = destino.ciudad_id.id
                if destino.pais_id:
                    pais = destino.pais_id.id
                self.pool.get('viaticos.destinos').create(cr, uid, {'name': destino.name,
                                                                    'ciudad_id': ciudad,
                                                                    'pais_id': pais,
                                                                    'fecha_salida': destino.fecha_salida,
                                                                    'fecha_llegada': destino.fecha_llegada,
                                                                    'informe_id':destino.solicitud_id.id})
            for detalle in solicitud.detalle_solicitud:
                self.pool.get('viaticos.solicitud.line').create(cr, uid, {'informe_id': destino.solicitud_id.id,
                                                                          'detalle': detalle.detalle,
                                                                          'cantidad': detalle.cantidad,
                                                                          'valor': detalle.valor})
            log_obj=self.pool.get('viaticos.log')
            log_obj.create(cr, uid, {
                              'name': 'Solicitud aprobada por PREFECTO',
                              'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                              'viatico_id': solicitud.id,
                              'user_id': uid,
                              })
        self.write(cr, uid, ids, {'state': 'solicitud3'})
        return True
    
    def solicitud3_informe1(self, cr, uid, ids, context=None):
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        for registros in self.browse(cr, uid, ids, context):
            if not registros.actividades_informe:
                raise osv.except_osv('Error', 'El empleado aún no ha ingresado el informe completo')
            if registros.confirmar_facturas==False:
                raise osv.except_osv('Error', 'Debe indicar que las facturas ingresadas son las correctas, activando el campo "Confirmar facturas ingresadas"')
        for solicitud in self.browse(cr, uid, ids, context):
            if self.fecha_inicio_fin(cr, uid, solicitud.id, context) != 'nada':
                self.calcular_detalle(cr, uid, solicitud.id, context)
                log_obj=self.pool.get('viaticos.log')
                log_obj.create(cr, uid, {
                                  'name': 'Informe enviado',
                                  'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                                  'viatico_id': solicitud.id,
                                  'user_id': uid,
                                  })
        self.write(cr, uid, ids, {'state': 'informe1', 'fecha_informe': time.strftime("%Y-%m-%d %H:%M:%S")})
        return True
    
    def informe1_informe2(self, cr, uid, ids, context=None):
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        for solicitud in self.browse(cr, uid, ids, context):
            log_obj=self.pool.get('viaticos.log')
            log_obj.create(cr, uid, {
                              'name': 'Informe aprobado por JEFE SUPERIOR',
                              'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                              'viatico_id': solicitud.id,
                              'user_id': uid,
                              })
        self.write(cr, uid, ids, {'state': 'informe2'})
        return True
    
    def informe2_done(self, cr, uid, ids, context=None):
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        for solicitud in self.browse(cr, uid, ids, context):
            log_obj=self.pool.get('viaticos.log')
            log_obj.create(cr, uid, {
                              'name': 'Informe aprobado por TALENTO HUMANO',
                              'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                              'viatico_id': solicitud.id,
                              'user_id': uid,
                              })
        return self.write(cr, uid, ids, {'state': 'done'})
    
    
    def comprobar_fechas_destinos(self, cr, uid, ids, destinos, context={}):
        obj_destinos = self.pool.get('viaticos.destinos')
        if destinos:
            if not ids:
                posicion = 0
                for destino_vista in destinos:
                    posicion = posicion + 1
                    time_salida = datetime.datetime.strptime(destino_vista[2]['fecha_salida'], "%Y-%m-%d %H:%M:%S")
                    time_llegada = datetime.datetime.strptime(destino_vista[2]['fecha_llegada'], "%Y-%m-%d %H:%M:%S")
                    time_salida = time_salida - datetime.timedelta(hours=5)
                    time_llegada = time_llegada - datetime.timedelta(hours=5)
                    dia_llegada = time_llegada.replace(hour=00, minute=00, second=00)
                    if posicion==1:
                        anterior_salida = time_salida
                        anterior_llegada = time_llegada
                    else:
                        if time_llegada>time_salida:
                            if time_salida>anterior_llegada:
                                if time_salida.day==anterior_llegada.day:
                                    anterior_salida = time_salida
                                    anterior_llegada = time_llegada
                                else:
                                    return {'warning': {'title':'Advertencia','message':'Debe coincidir el día de llegada de un destino, con la de salida del siguiente destino'}}
                            else:
                                return {'warning': {'title':'Advertencia','message':'Las fechas deben ser colocadas en orden'}}
                        else:
                            return {'warning': {'title':'Advertencia','message':'Las fechas de llegada debe ser mayor a la de salida'}}
            else:
                posicion = 0
                for destino_vista in destinos:
                    if destino_vista[0]!=2:
                        posicion = posicion + 1
                        if destino_vista[0]==0:
                            time_salida = datetime.datetime.strptime(destino_vista[2]['fecha_salida'], "%Y-%m-%d %H:%M:%S")
                            time_llegada = datetime.datetime.strptime(destino_vista[2]['fecha_llegada'], "%Y-%m-%d %H:%M:%S")
                            time_salida = time_salida - datetime.timedelta(hours=5)
                            time_llegada = time_llegada - datetime.timedelta(hours=5)
                            dia_llegada = time_llegada.replace(hour=00, minute=00, second=00)
                            if posicion==1:
                                anterior_salida = time_salida
                                anterior_llegada = time_llegada
                            else:
                                if time_llegada>time_salida:
                                    if time_salida>anterior_llegada:
                                        if time_salida.day==anterior_llegada.day:
                                            anterior_salida = time_salida
                                            anterior_llegada = time_llegada
                                        else:
                                            return {'warning': {'title':'Advertencia','message':'Debe coincidir el día de llegada de un destino, con la de salida del siguiente destino'}}
                                    else:
                                        return {'warning': {'title':'Advertencia','message':'Las fechas deben ser colocadas en orden'}}
                                else:
                                    return {'warning': {'title':'Advertencia','message':'Las fechas de llegada debe ser mayor a la de salida'}}
                        else:
                            destino = obj_destinos.browse(cr, uid, int(destino_vista[1]))
                            print destino_vista
                            time_salida = datetime.datetime.strptime(destino.fecha_salida, "%Y-%m-%d %H:%M:%S")
                            time_llegada = datetime.datetime.strptime(destino.fecha_llegada, "%Y-%m-%d %H:%M:%S")
                            time_salida = time_salida - datetime.timedelta(hours=5)
                            time_llegada = time_llegada - datetime.timedelta(hours=5)
                            if destino_vista[0]==1:
                                if destino_vista[2].has_key('fecha_salida'):
                                    time_salida = datetime.datetime.strptime(destino_vista[2]['fecha_salida'], "%Y-%m-%d %H:%M:%S")
                                    time_salida = time_salida - datetime.timedelta(hours=5)
                                if destino_vista[2].has_key('fecha_llegada'):
                                    time_llegada = datetime.datetime.strptime(destino_vista[2]['fecha_llegada'], "%Y-%m-%d %H:%M:%S")
                                    time_llegada = time_llegada - datetime.timedelta(hours=5)
                            dia_llegada = time_llegada.replace(hour=00, minute=00, second=00)
                            if posicion==1:
                                anterior_salida = time_salida
                                anterior_llegada = time_llegada
                            else:
                                if time_llegada>time_salida:
                                    if time_salida>anterior_llegada:
                                        if time_salida.day==anterior_llegada.day:
                                            anterior_salida = time_salida
                                            anterior_llegada = time_llegada
                                        else:
                                            return {'warning': {'title':'Advertencia','message':'Debe coincidir el día de llegada de un destino, con la de salida del siguiente destino'}}
                                    else:
                                        return {'warning': {'title':'Advertencia','message':'Las fechas deben ser colocadas en orden'}}
                                else:
                                    return {'warning': {'title':'Advertencia','message':'Las fechas de llegada debe ser mayor a la de salida'}}
    
    
solicitud_viaticos()
