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

class reporte_mantenimiento(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(reporte_mantenimiento, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_vehiculo_lubricante': self.get_vehiculo_lubricante,
            'get_vehiculo_mantenimiento': self.get_vehiculo_mantenimiento,
        })


    def get_vehiculo_lubricante(self,this):
        lubri_ids1 = []
        lubri_obj = self.pool.get('vehiculo.lubricante') 
        lubris_ids = [this.vehiculor_id.id]
        for vehiculor_id in lubris_ids:
            if this.opc:
                if this.date_start:
                    lubri_ids = lubri_obj.search(self.cr, self.uid, [('vehiculol_id','=',vehiculor_id),('fecha','>=',this.date_start),  
                    ('fecha','<=',this.date_stop)])
                else:
                    lubri_ids = lubri_obj.search(self.cr, self.uid, [('vehiculol_id','=',vehiculor_id),('fecha','<=',this.date_stop)])
            else:
                lubri_ids = lubri_obj.search(self.cr, self.uid, [('vehiculol_id','=',vehiculor_id)])
                    
        return lubri_obj.browse(self.cr, self.uid,lubri_ids)
       
    def get_vehiculo_mantenimiento(self,this):
        lubri_ids1 = []
        lubri_obj = self.pool.get('vehiculo.mantenimiento') 
        lubris_ids = [this.vehiculor_id.id]
        for vehiculor_id in lubris_ids:
            if this.opc:
                if this.date_start:
                    lubri_ids = lubri_obj.search(self.cr, self.uid, [('vehiculom_id','=',vehiculor_id),('date','>=',this.date_start),  
                    ('date','<=',this.date_stop)])
                else:
                    lubri_ids = lubri_obj.search(self.cr, self.uid, [('vehiculom_id','=',vehiculor_id),('date','<=',this.date_stop)])
            else:
                lubri_ids = lubri_obj.search(self.cr, self.uid, [('vehiculom_id','=',vehiculor_id)])
                    
        return lubri_obj.browse(self.cr, self.uid,lubri_ids)
       
report_sxw.report_sxw('report.reporte_mantenimiento',
                       'reporte.mantenimiento', 
                       'addonsgob/mecanica/report/reporte_mantenimiento.mako',
                       parser=reporte_mantenimiento,
                       header=False)


