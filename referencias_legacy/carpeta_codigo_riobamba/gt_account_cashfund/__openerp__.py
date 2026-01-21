# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2014 (<http://www.gnuthink.com>).
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
    "name" : "Fund Management",
    "version" : "0.1",
    "author" : "Gnuthink Co. Ltd.",
    "category" : "Accounting & Finance",
    "website" : "http://www.gnuthink.com",
    "description": """
    Gestion de fondos rotativos, cajas chicas
    =========================================
    """,
    "depends" : ["retention", "report_webkit"],
    "init_xml" : [],
    "update_xml" : ['cashfund_view.xml', 'cashfund_data.xml',
                    'cashfund_report.xml',
                    'security/ir.model.access.csv',
                    ],
    "active": False,
    "installable": True,
}
