# -*- coding: utf-8 -*-
##############################################################################
#
#mario chogllo
#
##############################################################################

from time import strftime, strptime
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from osv import osv, fields
import sys 
import os 
import zipfile
import re
from tools import ustr
import base64
import unicodedata


class DocxWizard(osv.TransientModel):
    _name = 'docx.wizard'
    
    _columns = {
        'name': fields.char('name', size=10),
        'tipo': fields.selection([('certificado','Certificado'),('indefinido','Contrato indefinido'),('cod_trabajo','Cod. Trabajo'),('serv_ocacionales','Servicios ocacionales')],'Plantilla a generar',required=True),
        'file': fields.binary('Archivo'),
        'filename': fields.char('Filename', size=32),
        }

    def generate_template(self, cr, uid, ids, context={}):
        parameter_obj = self.pool.get('ir.config_parameter')
        addons_path_ids = parameter_obj.search(cr, uid, [('key','=','addons_path')],limit=1)
        if not addons_path_ids:
            raise osv.except_osv('Error de configuracion', 'No existe path de plantillas definido, es un parametro de sistema addons_path.')
        addons_path = parameter_obj.browse(cr, uid, addons_path_ids[0])
        wizard_obj = self.pool.get('docx.wizard')
        wizard  = wizard_obj.browse(cr, uid, ids[0])
        for o in self.pool.get('hr.contract').browse(cr, uid, context['active_ids']):
            if wizard.tipo == 'indefinido':
                templateDocx = zipfile.ZipFile(addons_path.value+"/gt_hr_base/data/indefinido.docx")
            elif wizard.tipo == 'cod_trabajo':
                templateDocx = zipfile.ZipFile(addons_path.value+"/gt_hr_base/data/cod_trabajo.docx")
            elif wizard.tipo == 'serv_ocacionales':
                templateDocx = zipfile.ZipFile(addons_path.value+"/gt_hr_base/data/serv_ocacionales.docx")
            elif wizard.tipo == 'certificado':
                templateDocx = zipfile.ZipFile(addons_path.value+"/gt_hr_base/data/certificado.docx")                
            nuevo = "/tmp/"+str(o.id)+"new.docx"
            newDocx = zipfile.ZipFile(nuevo, "w")
            for file in templateDocx.filelist:
                content = templateDocx.read(file)
                encontrados = []
                busqueda = re.findall(r"{{.*?}}", content)
                if len(busqueda)>0:
                    for tex in busqueda:
                        tex_aux = tex.replace("{{","")
                        tex_aux = tex_aux.replace("}}","")
                        tex_aux = tex_aux.replace("&quot;","\"")
                        var_aux = eval(tex_aux)
                        if not var_aux:
                            var_aux = ''
                        if var_aux == False:
                            var_aux = ""
                        if isinstance(var_aux, unicode):
                            var_aux = unicodedata.normalize('NFKD',var_aux).encode('ascii','ignore')
                        elif isinstance(var_aux, int):
                            var_aux = str(var_aux)
                        elif isinstance(var_aux, float):
                            var_aux = str(var_aux)
                        content = content.replace(tex, var_aux)
                newDocx.writestr(file.filename, content)
            templateDocx.close()
            newDocx.close()
            file_aux = open(nuevo, "rb")
            data_aux = file_aux.read()
            data_64 = base64.encodestring(data_aux)
            wizard_obj.write(cr, uid, [wizard.id], {'filename': "Plantilla.docx", 'file':data_64})
    
DocxWizard()

class hrDeduction(osv.osv):

    _name = 'hr.deduction'
    _descripcion = 'Deducciones Imp. a la Renta'
    _order = 'name asc, code desc'

    _columns = dict(
        code = fields.char('Código',required=True,size=8),
        name = fields.char('Nombre',required=True,size=32),
        description = fields.text('Descripción'),
        )

hrDeduction()

###ADD weeks in WAGE TYPE PERIOD LINE

class hrWorkPeriodLine(osv.osv):
    
    _name = 'hr.work.period.line'
    
    _columns = dict(
        state = fields.selection([('abierto','Abierto'),('cerrado','Cerrado')],'Estado'),
        name = fields.char('Periodo',size=10),
        date_start = fields.date('Inicio Periodo'),
        date_stop = fields.date('Fin Periodo'),
        period_id = fields.many2one('hr.work.period','Periodo'),
        week_ids = fields.one2many('hr.week','wt_id','Semanas'),
        month = fields.char('Mes',size=10),
        month2 = fields.char('Mes C',size=8),
        p1 = fields.char('Periodo',size=2),
        )

    def write(self, cr, uid, ids, vals, context=None):
        raise osv.except_osv('Error', 'No puede editar periodos.')

    def create(self, cr, uid, vals, context=None):
        #validar que no se duplique
        period_line_obj = self.pool.get('hr.work.period.line')
        period_ids = period_line_obj.search(cr, uid, [('name','=',vals['name'])])
        if len(period_ids)>0:
            raise osv.except_osv('Error', 'No puede crear un periodo con el mismo nombre.')
        period_ids = period_line_obj.search(cr, uid, [('date_start','=',vals['date_start'])])
        if len(period_ids)>0:
            raise osv.except_osv('Error', 'No puede crear un periodo con la misma fecha inicio.')
        period_ids = period_line_obj.search(cr, uid, [('date_stop','=',vals['date_stop'])])
        if len(period_ids)>0:
            raise osv.except_osv('Error', 'No puede crear un periodo con la misma fecha final.')
        return super(hrWorkPeriodLine, self).create(cr, uid, vals, context=None)

    _defaults = dict(
        state = 'abierto',
        )
    
hrWorkPeriodLine()

class hrCalendarLine(osv.osv):
    
    _name = 'hr.calendar.line'
    
    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv('Error', 'No pueden eliminar días festivos ya ingresados')
        return True

    _columns = dict(
        period_id = fields.many2one('hr.work.period','Periodo'),
        date = fields.date('Día Festivo',required=True),
        )
    
hrCalendarLine()

class hrWorkPeriod(osv.osv):
    _name = 'hr.work.period'
    
    STATE_SELECTION = [
        ('draft', 'Borrador'),
        ('generated','Generado'),
    ]

    _columns = dict(
        basic_wage = fields.float('Salario Basico',required=True,help="Coloque aqui el valor del salario basico vigente por ley, si usted realiza una actualización de sueldo masiva a todo el personal que percibe el salario basico, el sistema buscará a todos los que tengan este valor y los modificará"),
        hour_start = fields.float('Hora Inicio Mañana'),
        hour_end = fields.float('Hora Fin Mañana'),
        hour_start_aft = fields.float('Hora Inicio Tarde'),
        hour_end_aft = fields.float('Hora Fin Tarde'),
        hour_start_ext = fields.float('Hora Inicio Extraordinarias'),
        hour_end_ext = fields.float('Hora Fin Extraordinarias'),
        name = fields.char('Descripción.',size=24,required=True,states={'confirmed':[('readonly',True)]}),
        date_start = fields.date('Fec.Inicio',required=True,states={'confirmed':[('readonly',True)]}),
        date_stop = fields.date('Fec.Final',required=True,states={'confirmed':[('readonly',True)]}),
        intervalo = fields.selection([('0.5','Quincenal'),('1','Mensual')],'Periodos',required=True,
                                     states={'confirmed':[('readonly',True)]}),
        line_ids = fields.one2many('hr.work.period.line','period_id','Lineas',
                                   states={'confirmed':[('readonly',True)]}),
        calendar_ids = fields.one2many('hr.calendar.line','period_id','Lineas Calendario',
                                   states={'confirmed':[('readonly',True)]}),
        state = fields.selection(STATE_SELECTION, 'State', readonly=True),
        activo = fields.boolean('Activo'),
        )

    def unlink(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.state=='generated':
                if this.line_ids:
                    raise osv.except_osv('Error', 'No pueden eliminar periodos generados')
        return super(hrWorkPeriod, self).unlink(cr, uid, ids, context=None)

    def create(self, cr, uid, vals, context=None):
        period_obj = self.pool.get('hr.work.period')
        period_ids = period_obj.search(cr, uid, [('name','=',vals['name'])])
        a = True
        if a:
            if len(period_ids)>1:
                raise osv.except_osv('Error', 'No puede crear un periodo con el mismo nombre.')
            period_ids = period_obj.search(cr, uid, [('date_start','=',vals['date_start'])])
            if len(period_ids)>1:
                raise osv.except_osv('Error', 'No puede crear un periodo con la misma fecha inicio.')
            period_ids = period_obj.search(cr, uid, [('date_stop','=',vals['date_stop'])])
            if len(period_ids)>1:
                raise osv.except_osv('Error', 'No puede crear un periodo con la misma fecha final.')
    #        vals['state'] = 'generated'
            return super(hrWorkPeriod, self).create(cr, uid, vals, context=None)

    def period_draft_generate(self,cr, uid, ids, context=None):
        period_obj = self.pool.get('hr.work.period')
        for this in self.browse(cr, uid, ids):
            period_ids = period_obj.search(cr, uid, [('name','=',this.name)])
            if len(period_ids)>1:
                raise osv.except_osv('Error', 'No puede crear un periodo con el mismo nombre.')
            period_ids = period_obj.search(cr, uid, [('date_start','=',this.date_start)])
            if len(period_ids)>1:
                raise osv.except_osv('Error', 'No puede crear un periodo con la misma fecha inicio.')
            period_ids = period_obj.search(cr, uid, [('date_stop','=',this.date_stop)])
            if len(period_ids)>1:
                raise osv.except_osv('Error', 'No puede crear un periodo con la misma fecha final.')
        for periodo in self.browse(cr, uid, ids, context=context):
            return self.generar_periodos2(cr, uid, ids, context, int(float(periodo.intervalo)))

    def generar_periodos2(self,cr, uid, ids, context=None, interval=1):
        num_semanas = 2
        obj_semana = self.pool.get('hr.week')
        line_obj  =self.pool.get('hr.work.period.line')
        #import pdb
        #pdb.set_trace()
        print 2
        for fy in self.browse(cr, uid, ids, context=context):
            interval_t = interval==0 and 0.5 or 1
            interval = 1
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            #ds = fy.date_start
            #print type(ds)
            while ds<datetime.strptime(fy.date_stop, '%Y-%m-%d'):
                temp_d = 0
                #import pdb
                #pdb.set_trace()
                de = ds + relativedelta(months=interval, days=-1)                
                if interval_t == 0.5:
                    num_semanas=1
                    temp_d = de.day // 2
                    de2 = ds + relativedelta(days=temp_d)
                    de3 = de2 + relativedelta(days=1)
                if de.strftime('%Y-%m-%d')>fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')
                if temp_d != 0:
                    line_id=line_obj.create(cr, uid, {
                        'name': ds.strftime('%m/%Y'),
                        'date_start': ds.strftime('%Y-%m-%d'),
                        'date_stop': de2.strftime('%Y-%m-%d'),
                        'period_id': fy.id,                
                        })
                    line2_id=line_obj.create(cr, uid, {
                        'name': ds.strftime('%m/%Y'),
                        'date_start': de3.strftime('%Y-%m-%d'),
                        'date_stop': de.strftime('%Y-%m-%d'),
                        'period_id': fy.id,
                        })
                else:
                    line_id=line_obj.create(cr, uid, {
                        'name': ds.strftime('%m/%Y'),
                        'date_start': ds.strftime('%Y-%m-%d'),
                        'date_stop': de.strftime('%Y-%m-%d'),
                        'period_id': fy.id,
                        'month':ds.strftime('%B'),
                        'month2':ds.strftime('%m'),
                        'p1':ds.strftime('%y'),
                        })
                ds = ds + relativedelta(months=interval)
        return self.write(cr, uid, ids,{'state':'generated'})
    
    def _check_active(self, cr, uid, ids):
        result = True
        tabla_obj = self.pool.get('hr.work.period')
        tabla_ids = tabla_obj.search(cr, uid, [('activo','=',True)])
        if len(tabla_ids)>1:
            result = False
        return result

    _defaults = dict(
        state = 'draft',
        intervalo = '1',
        activo = False,
        name = 'Periodo Salarial - ',
        )

    _constraints = [
        (_check_active,'Solo puede tener una tabla activa',['name']),
        ]

hrWorkPeriod()


###IR TABLE SRI

class hrBaseRetention(osv.osv):
    
    _name = 'hr.base.retention'
    _description = 'Tabla de Retencion Impuesto a la Renta'
    _order = 'name asc'    

    _columns = dict(
        name = fields.char('Descripción',required=True , size=40),
        period_id = fields.many2one('hr.work.period','Anio Laboral',required=True), 
        active = fields.boolean('Activa'),
        retention_line = fields.one2many('hr.base.retention.line', 'retention_id', 'Detalle'),
        projection_max_line = fields.one2many('hr.projection.max', 'retention_id', 'Max. Deduccion'),
        max_deduction = fields.float('Maximo deducible'),
        )

    _defaults = dict(
        name = 'Tabla de Retención',
        max_deduction = 0,
        )
hrBaseRetention()

class hrBaseRetentionLine(osv.osv):

    _name = 'hr.base.retention.line'
    _description = 'Lineas Retención IR'
    _rec_name = 'basic_fraction'
    _order = 'basic_fraction asc'

    _columns= dict(
        basic_fraction = fields.float('Fracción Básica', required=True),
        excess_to = fields.float('Exceso Hasta', required=True),
        basic_fraction_tax = fields.float('Imp. Fracción Básica', required=True),
        percent = fields.float('% Fracción Excedente', required=True),
        retention_id = fields.many2one('hr.base.retention','Detalle', ondelete='cascade'),
        )

hrBaseRetentionLine()

class hrProjectionMax(osv.osv):
    _name = 'hr.projection.max'
    _description = 'Máximo valor deducción'
    _order = 'name asc'
    _columns = dict(
        name = fields.many2one('hr.deduction','Deduccion',required=True),
        max_value = fields.float('Valor. max deducir',required=True),
        retention_id = fields.many2one('hr.base.retention','Detalle', ondelete='cascade'),
        )

hrProjectionMax()

class hrGrupoActividad(osv.Model):
    _name = 'grupo.actividad'
    _columns = dict(
        name = fields.char('Actividad',size=256),
    )
hrGrupoActividad()

class hrGrupoLine(osv.Model):
    _name = 'grupo.ocupacional.line'
    _columns = dict(
        ocupacional_id = fields.many2one('grupo.ocupacional','Grupo Ocupacional'),
        job_id = fields.many2one('hr.job','Cargo/Departamento',required=True),
        line_ids = fields.many2many('grupo.actividad','g_a_id','g_id','a_id','Actividades'),
    )
hrGrupoLine()

class hrGrupoOcupacional(osv.osv):
    _name = 'grupo.ocupacional'
    _columns = dict(
        name = fields.char('Nombre', size = 64),
        grado = fields.char('Grado',size=5),
        escala = fields.selection([('grados_20','20 Grados'),('jerarquico_superior','Nivel Jerárquico Superior')],'Escala'),
        rmu = fields.float('RMU', help="Valor referencial de la Remuneración Mensual"),
        description = fields.text('Descripción'),
        )
hrGrupoOcupacional()

class hrJobLine(osv.osv):
    _name='hr.job.line'
    _columns={
        'name':fields.char('Nombre',size=128,required=True),
        }

hrJobLine()

class budgetDistributivo(osv.Model):
    _name = 'budget.distributivo'
    _columns = dict(
        name = fields.char('Codigo',size=64,required=True),
    )
budgetDistributivo()

class hrJobConstraint(osv.osv):
    _inherit='hr.job'
    _order='name asc, department_id asc'
    
    def name_get2(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            if record.department_id:
                name = record.name + ' - ' + record.department_id.name
            else:
                name = record.name
            res.append((record.id, name))
        return res

    def unlink(self, cr, uid, ids, *args, **kwargs):
        employee_obj = self.pool.get('hr.employee')
        lista_emp = []
        for job in self.browse(cr, uid, ids):
            employee_ids = employee_obj.search(cr, uid, [('job_id','=',job.id)])
            if employee_ids:
                for employee_id in employee_ids:
                    empleado = employee_obj.browse(cr, uid, employee_id)
                    lista_emp.append(empleado.complete_name)
            if lista_emp:
                str_empleados = ''
                for emp in lista_emp:
                    str_empleados += emp + ' - '  
                raise osv.except_osv(('Operacion no permitida !'), ('El cargo esta relacionado en los empleados %s ') % (str_empleados))
        return super(hrJobConstraint, self).unlink(cr, uid, ids, *args, **kwargs)

    _columns = {
        'budget_id': fields.many2one('budget.distributivo','Partida Distributivo'),
        'name': fields.char('Cargo Institucional', size=200, required=True, select=True),
        'grupo_id': fields.many2one('grupo.ocupacional','Grupo ocupacional'),
        'active': fields.boolean('Activo'),
        'escala':fields.char('Escala',size=5),
        'grado':fields.char('Grado',size=5),
        'disponible':fields.boolean('Disponible'),
    }
    
    _defaults = dict(
        active = True,
        )

hrJobConstraint()

class sectorialComision(osv.osv):
    _name = 'sectorial.comision'
    _columns = dict(
        name = fields.char('Nombre',size=32,required=True),
        number = fields.integer('Número',required=True),
        )
sectorialComision()

class hrSectorialTable(osv.osv):
    _name = 'hr.sectorial.table'
    _description = 'Tabla Sectorial'
    _order = 'name asc'

    def set_vigente(self, cr, uid, ids, context,*args):
        sectorial_obj = self.pool.get('hr.sectorial.table')
        tablas=sectorial_obj.browse(cr, uid, ids)
        for tabla in tablas:
            sectorial_obj.write(cr, uid, tabla.id,{
                    'state':'vig',
                    })
        return True


    def set_antigua(self, cr, uid, ids, context,*args):
        tablas=self.pool.browse(cr, uid, ids)
        for tabla in tablas:
            self.write(cr, uid, tabla_.id,{
                    'state':'ant',
                    'vigente':True,
                    })
        return True

    _columns = dict(
        name = fields.char('Descripción',size=32,required=True),
        year = fields.integer('Año',required=True),
        vigente = fields.boolean('Vigente'),
        line_ids = fields.one2many('hr.sectorial.table.line','table_id','Lineas'),
        state = fields.selection([('draft','Borrador'),('vig','Vigente'),('ant','Antigua')],'Estado'),
        )

    _defaults = dict(
        state = 'draft',
        )

    _sql_constraints = [
        ('unique_vigente','unique(vigente)','Solo puede tener una tabla vigente.')
        ]

hrSectorialTable()

class sectorialRama(osv.osv):
    _name = 'sectorial.rama'
    _description = 'Ramas Sectorial'
    _columns = dict(
        name = fields.char('Rama Actividad',size=128,required=True),
        descripcion = fields.text('Descripción'),
        )

sectorialRama()

class hrSectorialTableLine(osv.osv):
    _name = 'hr.sectorial.table.line'
    _description = 'Lineas Sectorial'
    _LEVEL = [('art','Artesano'),('bas','Básica'),('bach','Bachillerato'),
              ('sup','Superior Técnico'),('egr','Egresado'),('tercer','Tercer Nivel'),
              ('cuarto','Cuarto Nivel')]
    
    _columns = dict(
        comision_id = fields.many2one('sectorial.comision','Comisión Sectorial',required=True),
        name = fields.many2one('sectorial.rama','Rama de actividad',required=True),
        job_id = fields.many2one('hr.job.line','Cargo y/o Función'),
        level = fields.selection(_LEVEL,'Nivel'),
        code = fields.char('Codigo',size=13),
        value = fields.float('Tarifa Min. Sectorial',required=True),
        table_id = fields.many2one('hr.sectorial.table','Tabla'),
        vigente = fields.related('table_id', 'vigente', type='boolean', string='Vigente', store=True),
        )
hrSectorialTableLine()

## Configuracion basica

class configBase(osv.osv):

    _name = 'hr.base.configuration'
    _columns = dict(
        desc = fields.char('Descripción',size=100),
#        coef_a = fields.float('Coef. Desc. Atrasos', digits=(14,6),
#                              help="Coeficiente con el cual se calculara el valor a descontar por concepto de atrasos"),
        basic_value = fields.float('Valor Basico Ley',
                                   help="Es el valor del salario basico unificado segun la legislacion ecuatoriana"),
        min_vacation = fields.integer('Dias Vacaciones', 
                                      help="Es el número de dias que se asigna al empleado al cumplir un año de labores"),
        max_accumulate = fields.integer('Max. Dias Acumulables', 
                                      help="Es el número de dias máximo que un empleado puede acumular"),
        activo = fields.boolean('Activo'),
        )

    _sql_constraints = [
        ('activo_', 'unique (activo)', 'Debe esxistir solo una configuración activa !')
        ]
    
configBase()

