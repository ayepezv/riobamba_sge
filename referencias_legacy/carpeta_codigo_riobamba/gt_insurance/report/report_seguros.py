# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-now Gnuthink Software Labs Co. Ltd. (<http://www.gnuthink.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from report import report_sxw

class report_seguros(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_seguros, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                })        
report_sxw.report_sxw('report.report_seguros', 'gt.insurance.sinister.memory', 'gt_insurance/report/report_seguros.rml', parser=report_seguros, header=False)


class report_informes(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_informes, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                })
        
report_sxw.report_sxw('report.report_informes', 'gt.insurance.inform', 'gt_insurance/report/report_informes.rml', parser=report_informes, header=False)


class report_activos_siniestros(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_activos_siniestros, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                })
        
report_sxw.report_sxw('report.report_activos_siniestros', 'gt.insurance.sinister.memory', 'gt_insurance/report/report_activos_siniestros.rml', parser=report_activos_siniestros, header=False)
