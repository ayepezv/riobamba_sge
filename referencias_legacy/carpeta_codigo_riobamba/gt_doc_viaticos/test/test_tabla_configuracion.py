ADDONS_PATH = 'openerp6.1/addons/gpa_viaticos'
from openerp.tools import config
config.options['addons_path'] = ADDONS_PATH
 
import unittest
 
from itsbroken.transaction import Transaction
from itsbroken.testing import DB_NAME, POOL, USER, CONTEXT, \
     install_module, drop_database
 
class TestProjectProject(unittest.TestCase):
 
    def setUp(self):
        install_module('gt_doc_viaticos')
 
    def test_0010_create_axis(self):
        """
        Test creating project.axis
        """
        with Transaction().start(DB_NAME, USER, CONTEXT) as txn:
            axis_obj = POOL.get('project.axis')
            values = {
                'name': 'test_axis',
                'legal_base': 'data_test_legal_base'
                }
            id = axis_obj.create(txn.cursor, txn.user, values, txn.context)
            axis = axis_obj.browse(txn.cursor, txn.user, id)
            self.assertEqual(axis.name, values['name'])
 
def tearDown(self):
    drop_database()
 
def suite():
    _suite = unittest.TestSuite()
    _suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(TestProjectProject),
        ])
    return _suite
            
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())