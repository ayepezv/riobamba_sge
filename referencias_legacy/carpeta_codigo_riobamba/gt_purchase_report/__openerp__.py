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
    "name" : "Government Purchase Report",
    "version" : "0.1",
    "author" : "Gnuthink Co. Ltd.",
    "category" : "Generic Modules/Purchase Report",
    "website" : "http://www.gnuthink.com",
    "description": """
    This module allows you to manage your Procedures: contracts, expense, etc
    """,
    "depends" : ["purchase_requisition","gt_government_procedure",
                "purchase",],
    "init_xml" : [],
    "update_xml" : [
        "purchase_report.xml",
     ],
    "active": False,
    "installable": True,
}
