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

class reforma_programa(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(reforma_programa, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'generate_dict': self.generate_dict,
            'all_programas': self.all_programas,
        })

    def generate_dict(self, obj,programa):
        line_obj = self.pool.get('reform.programa.line')
        lines_ids = line_obj.search(self.cr, self.uid, [('p_id','=',obj.id),('program_id','=',programa.id)])
        #mandar browse de los roles
        return line_obj.browse(self.cr, self.uid, lines_ids)

    def all_programas(self, obj):
        programas = []
        programas_aux = []
        programas_ids = []
        programa_obj = self.pool.get('project.program')
        for line in obj.line_ids:
            if not line.program_id.sequence in programas_aux:
                programas_aux.append(line.program_id.sequence)
                programas.append({'sequence':line.program_id.sequence})
        data = sorted(programas, key=lambda k: k['sequence'])    
        for programa_sort in data:
            programa_ids = programa_obj.search(self.cr, self.uid, [('sequence','=',programa_sort['sequence'])],limit=1)
            if not programa_ids:
                print "NO POGAMA", programa_sort['sequence']
            programas_ids.append(programa_ids[0])
        return programa_obj.browse(self.cr, self.uid, programas_ids)#programas

      
report_sxw.report_sxw('report.reforma_programa',
                       'reform.programa', 
                       'addons/gt_project_project/report/reforma_programa.mako',
                       parser=reforma_programa,
                       header=False)
