# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Numérigraphe SARL.
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
    'name': 'Search Stock Locations and Products by stock quantity',
    'version': '1.0',
    "category" : "Generic Modules/Inventory Control",
    'description': '''This allows searches on available quantities.
It lets user define custom search filters, and adds the following quick-filter buttons:
Lists of products:
- available products (stock > 0)
- products out of stock (stock = 0)
- products with negative stock (stock < 0)
Lists of locations:
- used locations (stock > 0)
- empty locations (stock = 0)
- locations with negative stock (stock < 0)
The search filters are context-sensitive: i.e. when examining a product's stock 
by Location, an "empty" Location is one that does not contain this
specific product (but may contain others).
''',
    'author' : u'Numérigraphe SARL',
    'depends': ['stock'],
    'update_xml': [
    	'product_view.xml',
    	'stock_view.xml'
    ],
    'test': [
        'test/stock_qty_search.yml',
    ],
    'installable': True,
    # XXX In v6.1+, we could add this to have this module automatically installed along with stock:
    #'active': True,
}

