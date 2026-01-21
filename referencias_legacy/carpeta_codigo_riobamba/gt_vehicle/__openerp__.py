# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
{
    "name" : "Gestión Vehicular",
    "version" : "0.1",
    "author" : "Gnuthink Co. Ltd.",
    "category" : "Generic Modules/Vehicle",
    "website" : "http://www.gnuthink.com",
    "description": """
    This module allows you to manage your vehicles, and our movilization
    """,
    "depends" : ["hr","country_ec",
                 "gt_document_manager"],
    "init_xml" : [],
    "update_xml" : [
        "security/vehicle_groups_security.xml",
        "wizard/order_cancel_view.xml",
        "wizard/incident_driver_view.xml",
        "wizard/vehicle_repair_view.xml",
        "wizard/vehicle_repair_ok_view.xml",
        "wizard/alert_view.xml",
        "vehicle_view.xml",
        "taller_view.xml",
        "combustible_view.xml",
        #"hr_department_view.xml",
        "vehicle_view_dep.xml",
        "security/ir.model.access.csv",
       # "vehicular_programming_workflow.xml",
        "vehicle_sequence.xml",
        "report/report.xml",
        "wizard/vehicle_update_km_view.xml",
        "wizard/vehicle_activate_view.xml",
        "wizard/employee_driver_view.xml",
        "wizard/group_order_view.xml",
        "wizard/vehicle_trip_exec_view.xml",
        "wizard/vehicle_km_start_view.xml",
     ],
    "active": False,
    "installable": True,
}
