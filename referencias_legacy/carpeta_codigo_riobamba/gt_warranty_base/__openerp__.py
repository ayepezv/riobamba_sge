# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2014 Gnuthink Software Cia. Ltda. (<http://gnuthink.com>).
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
    "name" : "Warranty Base",
    "version" : "0.1",
    "author" : "Gnuthink Co. Ltd.",
    "category" : "Generic",
    "website" : "http://www.gnuthink.com",
    "description": """
    Core for warranty Management
    """,
    "depends" : [],
    "init_xml" : [],
    "update_xml" : [
#                    "security/security.xml",
#                    "security/ir.model.access.csv",
        "warranty_view.xml",
    ],
    "active": False,
    "installable": True,
}
