# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
import time
from report import report_sxw
from osv import fields, osv
from gt_tool import XLSWriter
import re

total_todo = []
cabecera_todo = []

class rol_decimo_tercero(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rol_decimo_tercero, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'all_programas': self.all_programas,
            'all_decimo': self.all_decimo,
        })


    def all_decimo(self,decimo ,programa):
        decimo_obj = self.pool.get('hr.decimo.tercero.line')
        decimo_ids = decimo_obj.search(self.cr, self.uid, [('dec_id','=',decimo.id),('program_id','=',programa.id)])
        return decimo_obj.browse(self.cr, self.uid, decimo_ids)

    def all_programas(self, obj):
        programas = []
        programas_aux = []
        programas_ids = []
        programa_obj = self.pool.get('project.program')
        sql_programas = """select program_id from hr_decimo_tercero_line where dec_id=%s group by program_id"""%(obj.id)
        self.cr.execute(sql_programas)
        for programa_id in self.cr.fetchall():
            programa = programa_obj.browse(self.cr,self.uid,programa_id[0])
            programas.append({'sequence':programa.sequence,'programa_id':programa})
        #import pdb
        #pdb.set_trace()
        data = sorted(programas, key=lambda k: k['sequence'])
        for programa_sort in data:
            programas_ids.append(programa_sort['programa_id'])
        #programas_ids.append(programa_id[0])
        return programas_ids
    
    def all_programasNO(self, obj):
        programas = []
        programas_aux = []
        programas_ids = []
        programa_obj = self.pool.get('project.program')
        for decimo in obj.line_ids:
            if not decimo.program_id.sequence in programas_aux:
                programas_aux.append(decimo.program_id.sequence)
                programas.append({'sequence':decimo.program_id.sequence})
        data = sorted(programas, key=lambda k: k['sequence'])    
        for programa_sort in data:
            programa_ids = programa_obj.search(self.cr, self.uid, [('sequence','=',programa_sort['sequence'])],limit=1)
            if programa_ids:
                programas_ids.append(programa_ids[0])
        return programa_obj.browse(self.cr, self.uid, programas_ids)#programas

report_sxw.report_sxw('report.rol_decimo_tercero',
                       'hr.decimo.tercero', 
                       'addons/gt_hr_decimo/report/rol_decimo3.mako',
                       parser=rol_decimo_tercero,
                       header=False)

class rol_decimo_tercerodet(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rol_decimo_tercerodet, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'all_programas': self.all_programas,
            'all_decimo': self.all_decimo,
        })


    def all_decimo(self,decimo ,programa):
        decimo_obj = self.pool.get('hr.decimo.tercero.line')
        decimo_ids = decimo_obj.search(self.cr, self.uid, [('dec_id','=',decimo.id),('program_id','=',programa.id)])
        return decimo_obj.browse(self.cr, self.uid, decimo_ids)

    def all_programas(self, obj):
        programas = []
        programas_aux = []
        programas_ids = []
        programa_obj = self.pool.get('project.program')
        sql_programas = """select program_id from hr_decimo_tercero_line where dec_id=%s group by program_id"""%(obj.id)
        self.cr.execute(sql_programas)
        for programa_id in self.cr.fetchall():
            programa = programa_obj.browse(self.cr,self.uid,programa_id[0])
            programas.append({'sequence':programa.sequence,'programa_id':programa})
        #import pdb
        #pdb.set_trace()
        data = sorted(programas, key=lambda k: k['sequence'])
        for programa_sort in data:
            programas_ids.append(programa_sort['programa_id'])
        #programas_ids.append(programa_id[0])
        return programas_ids
    
    def all_programasNO(self, obj):
        programas = []
        programas_aux = []
        programas_ids = []
        programa_obj = self.pool.get('project.program')
        for decimo in obj.line_ids:
            if not decimo.program_id.sequence in programas_aux:
                programas_aux.append(decimo.program_id.sequence)
                programas.append({'sequence':decimo.program_id.sequence})
        data = sorted(programas, key=lambda k: k['sequence'])    
        for programa_sort in data:
            programa_ids = programa_obj.search(self.cr, self.uid, [('sequence','=',programa_sort['sequence'])],limit=1)
            if programa_ids:
                programas_ids.append(programa_ids[0])
        return programa_obj.browse(self.cr, self.uid, programas_ids)#programas

report_sxw.report_sxw('report.rol_decimo_tercerodet',
                       'hr.decimo.tercerodet', 
                       'addons/gt_hr_decimo/report/rol_decimo3det.mako',
                       parser=rol_decimo_tercero,
                       header=False)

class rol_decimo_cuartodet(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rol_decimo_cuartodet, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'all_programas': self.all_programas,
            'all_decimo': self.all_decimo,
            'get_cargo_rol':self.get_cargo_rol,
        })


    def get_cargo_rol(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux

    def all_decimo(self,decimo ,programa):
        decimo_obj = self.pool.get('hr.decimo.cuarto.line')
        decimo_ids = decimo_obj.search(self.cr, self.uid, [('dec_id','=',decimo.id),('program_id','=',programa.id),('acumula','=',False)])
        return decimo_obj.browse(self.cr, self.uid, decimo_ids)

    def all_programas(self, obj):
        programas = []
        programas_aux = []
        programas_ids = []
        programa_obj = self.pool.get('project.program')
        sql_programas = """select program_id from hr_decimo_cuarto_line where dec_id=%s group by program_id"""%(obj.id)
        self.cr.execute(sql_programas)
        for programa_id in self.cr.fetchall():
            programa = programa_obj.browse(self.cr,self.uid,programa_id[0])
            programas.append({'sequence':programa.sequence,'programa_id':programa})
        #import pdb
        #pdb.set_trace()
        data = sorted(programas, key=lambda k: k['sequence'])
        for programa_sort in data:
            programas_ids.append(programa_sort['programa_id'])
        #programas_ids.append(programa_id[0])
        return programas_ids
    
    def all_programasNO(self, obj):
        programas = []
        programas_aux = []
        programas_ids = []
        programa_obj = self.pool.get('project.program')
        for decimo in obj.line_ids:
            if not decimo.program_id.sequence in programas_aux:
                programas_aux.append(decimo.program_id.sequence)
                programas.append({'sequence':decimo.program_id.sequence})
        data = sorted(programas, key=lambda k: k['sequence'])    
        for programa_sort in data:
            programa_ids = programa_obj.search(self.cr, self.uid, [('sequence','=',programa_sort['sequence'])],limit=1)
            if programa_ids:
                programas_ids.append(programa_ids[0])
        return programa_obj.browse(self.cr, self.uid, programas_ids)#programas

report_sxw.report_sxw('report.rol_decimo_cuartodet',
                       'hr.decimo.cuartodet', 
                       'addons/gt_hr_decimo/report/rol_decimo4det.mako',
                       parser=rol_decimo_cuartodet,
                       header=False)

class rol_decimo_cuarto(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rol_decimo_cuarto, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'all_programas': self.all_programas,
            'all_decimo': self.all_decimo,
            'get_cargo_rol':self.get_cargo_rol,
        })


    def get_cargo_rol(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux

    def all_decimo(self,decimo ,programa):
        decimo_obj = self.pool.get('hr.decimo.cuarto.line')
        decimo_ids = decimo_obj.search(self.cr, self.uid, [('dec_id','=',decimo.id),('program_id','=',programa.id)])
        return decimo_obj.browse(self.cr, self.uid, decimo_ids)

    def all_programas(self, obj):
        programas = []
        programas_aux = []
        programas_ids = []
        programa_obj = self.pool.get('project.program')
        sql_programas = """select program_id from hr_decimo_cuarto_line where dec_id=%s group by program_id"""%(obj.id)
        self.cr.execute(sql_programas)
        for programa_id in self.cr.fetchall():
            programa = programa_obj.browse(self.cr,self.uid,programa_id[0])
            programas.append({'sequence':programa.sequence,'programa_id':programa})
        #import pdb
        #pdb.set_trace()
        data = sorted(programas, key=lambda k: k['sequence'])
        for programa_sort in data:
            programas_ids.append(programa_sort['programa_id'])
        #programas_ids.append(programa_id[0])
        return programas_ids    
    
    def all_programasNo(self, obj):
        programas = []
        programas_aux = []
        programas_ids = []
        programa_obj = self.pool.get('project.program')
        for decimo in obj.line_ids:
            if not decimo.program_id.sequence in programas_aux:
                programas_aux.append(decimo.program_id.sequence)
                programas.append({'sequence':decimo.program_id.sequence})
        data = sorted(programas, key=lambda k: k['sequence'])    
        for programa_sort in data:
            programa_ids = programa_obj.search(self.cr, self.uid, [('sequence','=',programa_sort['sequence'])],limit=1)
            if not programa_ids:
                print "NO POGAMA", programa_sort['sequence']
            programas_ids.append(programa_ids[0])
        return programa_obj.browse(self.cr, self.uid, programas_ids)#programas

report_sxw.report_sxw('report.rol_decimo_cuarto',
                       'hr.decimo.cuarto', 
                       'addons/gt_hr_decimo/report/rol_decimo4.mako',
                       parser=rol_decimo_cuarto,
                       header=False)
