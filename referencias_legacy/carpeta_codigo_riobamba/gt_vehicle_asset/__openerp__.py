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
    This module allows you integrate account asset with vehicle 
    """,
    "depends" : ["gt_vehicle",
                 ],
    "init_xml" : [],
    "update_xml" : ["asset_view.xml"],
    "active": False,
    "installable": True,
}
