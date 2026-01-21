# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from time import strftime, strptime
from osv import osv, fields

class hrHistoriaFamiliar(osv.Model):
    _name = 'hr.historia.familiar'
    _columns = dict(
        m_id = fields.many2one('hr.ficha.medica','Ficha'),
        patologia_id = fields.selection([('Diabetes','Diabetes'),('Cardiovascular','Cardiovascular'),('Cancer','Cancer'),('Respiratorios','Respiratorios'),
                                         ('TBC','TBC'),('Reumatologicos','Reumatologicos'),('Neurologicos','Neurologicos'),('Mentale','Mentales'),
                                         ('Dijestivos','Dijestivos'),('Otros','Otros')],'Patologia'),
        parentezco = fields.selection([('PAPA','PAPA'),('MAMA','MAMA'),('ABUELO','ABUELO(A)'),('TIO','TIO(A)'),('HERMANO','HERMANO(A)')],'Parentezco'),
    )
hrHistoriaFamiliar()

class hrPersonalEnfermedad(osv.Model):
    _name = 'hr.personal.enfermedad'
    _columns = dict(
        name = fields.char('Nombre',size=32,required=True),
    )
hrPersonalEnfermedad()
class hrHistoriaPersonal(osv.Model):
    _name = 'hr.historia.personal'
    _columns = dict(
        m_id = fields.many2one('hr.ficha.medica','Ficha'),
        patologia_id = fields.many2one('hr.personal.enfermedad','Enfermedad'),
        nota = fields.text('Descripcion'),
    )
hrHistoriaPersonal()
class hrFichaMedica(osv.Model):
    _name = 'hr.ficha.medica'
    _columns = dict(
        name = fields.char('Numero Ficha',size=10),
        employee_id = fields.many2one('hr.employee','Funcionario'),
        familiar_ids = fields.one2many('hr.historia.familiar','m_id','Historia Familiar'),
        personal_ids = fields.one2many('hr.historia.personal','m_id','Historia Personal'),
    )
hrFichaMedica()
