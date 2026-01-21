#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

class vehicleDriver(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(vehicleDriver, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                })        
report_sxw.report_sxw('report.Choferes', 'vehicle.vehicle', 'gt_vehicle/report/vehicle_driver.rml', parser=vehicleDriver, header=True)

class vehicleList(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(vehicleList, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                })        
report_sxw.report_sxw('report.ListadoVehiculos', 'vehicle.vehicle', 'gt_vehicle/report/vehicle_list.rml', parser=vehicleList, header=False)

class movilizationList(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(movilizationList, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                })        
report_sxw.report_sxw('report.ListadoSolicitudes', 'movilization.order', 'gt_vehicle/report/movilization_list.rml', parser=movilizationList, header=False)


