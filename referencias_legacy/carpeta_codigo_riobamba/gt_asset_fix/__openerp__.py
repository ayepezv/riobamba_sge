# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
{
    "name": "gt_asset_fix",
    "version": "1.1",
    "author": "Mario Chogllo",
    "category": "Asset",
    "sequence": 12,
    'complexity': "easy",
    "website": "www.planerp.ec",
    "description": """
Modulo para mantenimiento de activos fijos.
=====================================
    """,    
    'images': [],
    'depends': ['gt_account_asset'],
    'init_xml': [],
    'update_xml': [        
        'security/gt_asset_fix_security.xml',
        'security/ir.model.access.csv',
        'fix_view.xml',    
    ],
    'demo_xml': [],
    #'test': ['test/gt_insurance.yml'],
    'installable': True,
}

