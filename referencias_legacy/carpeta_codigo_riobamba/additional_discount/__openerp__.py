{
    "name": "Additional discount",
    "version": "0.1",
    "depends": ["base","purchase","account"],
    "author": "E-nova tecnologies Pvt. Ltd.",
    "category": "Sales",
    "description": """
    This module provide : additional discount at total sales order, purchase order and invoices instead of per order line,
    but there is no changes in existing discount on per order lines.
    Additional discount is fully integrated between sales, purchase and invoices.
    """,
    "init_xml": [],
    'update_xml': ['additional_discount_view.xml'],
    'demo_xml': [],
    'test': [
        'test/scenario1.yml',
        'test/scenario2.yml',
    ],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
