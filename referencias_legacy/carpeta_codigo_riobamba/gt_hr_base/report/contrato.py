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

class ocacionalesw(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ocacionalesw, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_cargo': self.get_cargo,
        })

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux

report_sxw.report_sxw('report.ocacionalesw',
                       'hr.contract', 
                       'addons/gt_hr_base/report/ocacionalesw.mako',
                       parser=ocacionalesw,
                       header=True)

class indefinidow(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(indefinidow, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_cargo': self.get_cargo,
        })

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux

report_sxw.report_sxw('report.indefinidow',
                       'hr.contract', 
                       'addons/gt_hr_base/report/indefinidow.mako',
                       parser=indefinidow,
                       header=True)

class codtrabajow(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(codtrabajow, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_cargo': self.get_cargo,
        })

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux

report_sxw.report_sxw('report.codtrabajow',
                       'hr.contract', 
                       'addons/gt_hr_base/report/codtrabajow.mako',
                       parser=codtrabajow,
                       header=True)

