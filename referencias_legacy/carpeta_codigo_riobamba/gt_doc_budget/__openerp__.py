# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 Gnuthink Software Cia. Ltda. (<http://gnuthink.com>).
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
    "name" : "Budget Request",
    "version" : "0.1",
    "author" : "Gnuthink Co. Ltd.",
    "category" : "Generic Project",
    "website" : "http://www.gnuthink.com",
    "description": """
    Document for Request Budget in Government
    """,
    "depends" : ["gt_project_project"],
    "init_xml" : [],
    "update_xml" : [
                    "gt_doc_budget_view.xml",
                    #"gt_doc_budget_sequence.xml",
     ],
    "active": False,
    "installable": True,
}
