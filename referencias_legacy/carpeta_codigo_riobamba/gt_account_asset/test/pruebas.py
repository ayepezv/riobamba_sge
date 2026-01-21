ADDONS_PATH = '/home/gnuthink003/Proyectos/GPAzuay/gpa_seguros/6.1-gpa_seguros'
from openerp.tools import config
config.options['addons_path'] = ADDONS_PATH

import unittest
from itsbroken.transaction import Transaction
from itsbroken.testing import DB_NAME, POOL, USER, CONTEXT, \
     install_module, drop_database

class gt_account_asset(unittest.TestCase):

    def setUp(self):
        install_module('gt_account_asset')

    def test_0001_create_income(self):
        """
        Test crear tipo de bein
        """
        with Transaction().start(DB_NAME, USER, CONTEXT) as txn:
            axis_obj = POOL.get('gt.account.asset.income')
            values = {
                'name': 'tipo de bien',
                'cost': '300',
                'depreciate': 'False'
                }
            id = axis_obj.create(txn.cursor, txn.user, values, txn.context)
            axis = axis_obj.browse(txn.cursor, txn.user, id)
            self.assertEqual(axis.name, values['name'])

def tearDown(self):
    drop_database()

def suite():
    _suite = unittest.TestSuite()
    _suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(gt_account_asset),
        ])
    return _suite
            
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())