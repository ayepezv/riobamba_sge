# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from time import strftime, strptime

from osv import osv, fields

_STATE = [('draft','Borrador')]



class hrCapacitacion(osv.Model):
    _name = 'hr.capacitacion'
    _description = "Cursos Dictados por la entidad"
    _MODALITY = [('v','Virtual'),('d','Distancia'),('p','Presencial'),
                 ('s','Semipresencial'),('o','Otros')]

    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv('Aviso','No se permite eliminar cursos.')

    _columns = dict(
        codigo = fields.char('Codigo',size=10),
        tipo_evento = fields.selection([('CHARLA','SOCIALIZACION'),('TALLER','TALLER'),('CURSO','CURSO'),('DIPLOMADO','DIPLOMADO'),('CONFERENCIA','CONFERENCIA')],
                                       'Tipo Evento'),
        tipo_financiamiento = fields.selection([('POR EL GAD O EP','POR EL GAD O EP'),('AUTOGESTION','AUTOGESTION'),('CONVENIO','CONVENIO')],'Tipo Financiamiento'),
        inversion = fields.float('Inversion'),
        department_id = fields.many2one('hr.department','Departamento'),
        numero_participante = fields.integer('Numero Participantes'),
        servidor_publico = fields.boolean('Dictada por servidor publico'),
        tipo_operadora = fields.selection([('PUBLICA','PUBLICA'),('PRIVADA','PRIVADA')],'Tipo Operadora'),
        lugar_capacitacion = fields.many2one('res.country.state.canton','Lugar Capacitacion'),
        name = fields.char('Nombre Curso',size=256),
        fecha_desde = fields.date('Fecha desde'),
        fecha_hasta = fields.date('Fecha hasta'),
        dictado_por = fields.many2one('res.partner','Dictado por'),
        hours =  fields.integer('Numero de horas'),
        modality = fields.selection(_MODALITY,'Modalidad'),
        tipo = fields.selection([('aprobacion','de aprobacion'),('asistencia','de asistencia')],'Tipo de Curso'),
        line_ids = fields.one2many('hr.employee.course','a_id','Detalle Personas'),
        state = fields.selection([('Registro','Registro'),('Finalizado','Finalizado')],'Estado'),
    )

    def finaliza_capacitacion(self, cr, uid, ids, context=None):
        curso_obj = self.pool.get('hr.employee.course')
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                curso_obj.write(cr, uid, line.id ,{
                    'codigo':this.codigo,
                    'name':this.name,
                    'institute':user.company_id.name,
                    'hours':this.hours,
                    'modality':this.modality,
                    'tipo':this.tipo,
                    'is_institucion':True,
                    'fecha_desde':this.fecha_desde,
                    'fecha_hasta':this.fecha_hasta,
                    'tipo_evento':this.tipo_evento,
                    'tipo_financiamiento':this.tipo_financiamiento,
                    'servidor_publico':this.servidor_publico,
                    'tipo_operadora':this.tipo_operadora,
                    'lugar_capacitacion':this.lugar_capacitacion,
                })
        self.write(cr, uid, ids, {'state':'Finalizado'})
        return True

    _defaults = dict(
        state='Registro',
        
    )

hrCapacitacion()

class employeeCourseAcademic(osv.Model):
    _inherit = 'hr.employee.course'

    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv('Aviso','No se permite eliminar cursos.')

    _columns = dict(
        codigo = fields.char('Codigo',size=10),
        presupuesto_indiviual = fields.float('Presp. Individual'),
        tipo_evento = fields.selection([('CHARLA','SOCIALIZACION'),('TALLER','TALLER'),('CURSO','CURSO'),('DIPLOMADO','DIPLOMADO'),('CONFERENCIA','CONFERENCIA')],
                                       'Tipo Evento'),
        tipo_financiamiento = fields.selection([('POR EL GAD O EP','POR EL GAD O EP'),('AUTOGESTION','AUTOGESTION'),('CONVENIO','CONVENIO')],'Tipo Financiamiento'),
        inversion = fields.float('Inversion Individual'),
        servidor_publico = fields.boolean('Dictada por servidor publico'),
        tipo_operadora = fields.selection([('PUBLICA','PUBLICA'),('PRIVADA','PRIVADA')],'Tipo Operadora'),
        lugar_capacitacion = fields.many2one('res.country.state.canton','Lugar Capacitacion'),
        estado = fields.selection([('APROBO','APROBO'),('REPROBO','REPROBO'),('NO ASISTE','NO ASISTE')],'Estado'),
        institute = fields.char('Institucion',size=256),
        fecha_desde = fields.date('Fecha desde'),
        fecha_hasta = fields.date('Fecha hasta'),
        is_institucion = fields.boolean('Dictado por la Institucion'),
        a_id = fields.many2one('hr.capacitacion','Curso Dictado'),
    )

    _defaults = dict(
        name='/',
    )

employeeCourseAcademic()
