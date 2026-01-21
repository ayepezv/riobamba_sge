# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
# mariofchogllo@gmail.com
##############################################################################

from time import strftime, strptime
from osv import osv, fields

class ocupacionalPolitica(osv.Model):
    _name = 'ocupacional.politica'
    _columns = dict(
        name = fields.text('Definicion Politica'),
    )
ocupacionalPolitica()

class ocupacionalPreventiva(osv.Model):
    _name = 'ocupacional.preventiva'
    _columns = dict(
        name = fields.char('Nombre medida preventiva',size=128),
    )
ocupacionalPreventiva()

class riesgoCategoria(osv.Model):
    _name = 'riesgo.categoria'
    _columns = dict(
        name = fields.char('Nombre Categoria',size=32),
    )
riesgoCategoria()

class riesgoTipo(osv.Model):
    _name = 'riesgo.tipo'
    _columns = dict(
        name = fields.char('Tipo Riesgo',size=32),
        probabilidad = fields.selection([('Alta','Alta'),('Media','Media'),('Baja','Baja')],'Probabilidad'),
        severidad = fields.selection([('Leve','Leve'),('Grave','Grave'),('Muy Grave','Muy Grave')],'Severidad'),
    )
riesgoTipo()
class ocupacionalRiesgo(osv.Model):
    _name = 'ocupacional.riesgo'
    _columns = dict(
        tipo_id = fields.many2one('riesgo.tipo','Tipo Riesgo'), #solo lectura se calcula automatico segun probabilidad y severidad
        probabilidad = fields.selection([('Alta','Alta'),('Media','Media'),('Baja','Baja')],'Probabilidad'),
        severidad = fields.selection([('Leve','Leve'),('Grave','Grave'),('Muy Grave','Muy Grave')],'Severidad'),
        name = fields.text('Riesgo'),
        categoria_id = fields.many2one('riesgo.categoria','Categoria Riesgo'),
        medidas_preventivas_ids = fields.many2many('ocupacional.preventiva','r_p_id','r_id','p_id','Medidas Preventivas de riesgo'), 
    )
ocupacionalRiesgo()

class jobRiesgo(osv.Model):
    _inherit = 'hr.job'
    _columns = dict(
        riesgo_ids = fields.many2many('ocupacional.riesgo','j_r_id','j_id','r_id','Riesgos'),
    )
jobRiesgo()

class ocupacionalLugar(osv.Model):
    _name = 'ocupacional.lugar'
    _columns = dict(
        name  = fields.char('Nombre Lugar',size=32),
    )
ocupacionalLugar()

class ocupacionalParte(osv.Model):
    _name = 'ocupacional.parte'
    _columns = dict(
        name = fields.char('Parte Cuerpo',size=16),
    )
ocupacionalParte()

class ocupacionalIncidente(osv.Model):
    _name = 'ocupacional.incidente'
    _columns = dict(
        registrado_por = fields.many2one('res.users','Registrado por'),
        parte_afectada_id = fields.many2one('ocupacional.parte','Parte Cuerpo Afectada'),
        name = fields.char('Numero Incidente',size=10),
        employee_id = fields.many2one('hr.employee','Funcionario'),
        detalle = fields.text('Descripcion de los hechos'),
        riesgo_id = fields.many2one('ocupacional.riesgo','Riesgo Asociado'),
        fecha = fields.date('Fecha Ocurrencia'),
        lugar = fields.many2one('ocupacional.lugar','Lugar Ocurrio'),
        actividad = fields.many2one('grupo.actividad','Actividad Laboral Que Realizaba'),
        oficio_habitual = fields.char('Oficio Habitual',size=128),
        is_habitual = fields.boolean('Incidente ocurrio realizando su oficio habitual'),
        causas = fields.text('Causas'),
        genero_consulta = fields.boolean('Genero Consulta Medica',help="El incidente genero una consulta medica?"),
        consulta_id = fields.many2one('oemedical.appointment','Consulta Medica'),
    )
ocupacionalIncidente()
