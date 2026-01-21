ADDONS_PATH = '/home/ovnicraft/dev/openerp/61/project-addons'
from openerp.tools import config
config.options['addons_path'] = ADDONS_PATH

import unittest

from itsbroken.transaction import Transaction
from itsbroken.testing import DB_NAME, POOL, USER, CONTEXT, \
     install_module, drop_database

class TestProjectProject(unittest.TestCase):

    def setUp(self):
        install_module('gt_project_project')

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

    def test_0020_create_strategy(self):
        with Transaction().start(DB_NAME, USER, CONTEXT) as txn:
            estr_obj = POOL.get('project.estrategy')
            axis_obj = POOL.get('project.axis')
            values_ax = {
                'name': 'test_axis',
                'legal_base': 'data_test_legal_base'
                }
            axid = axis_obj.create(txn.cursor, txn.user, values_ax, txn.context)            
            values = {'sequence': 1, 'name': 'mi estategia', 'axis_id': axid}
            obj_id = estr_obj.create(txn.cursor, txn.user, values, txn.context)
            estategy = estr_obj.browse(txn.cursor, txn.user, obj_id, txn.context)
            self.assertEqual(estategy.name, values['name'])

    def test_0030_create_program(self):
        with Transaction().start(DB_NAME, USER, CONTEXT) as txn:
            estr_obj = POOL.get('project.estrategy')
            axis_obj = POOL.get('project.axis')
            prog_obj = POOL.get('project.program')
            values_ax = {'name': 'test_axis', 'legal_base': 'data_test_legal_base'}
            values = {'sequence': 1, 'name': 'mi estategia', 'axis_id': axid}
            prog_data = {'sequence': '5555',
                         'name': 'Mi programa del plan nacional de desarrollo',
                         'axis_id': axid, 'estrategy_id': obj_id}            
            axid = axis_obj.create(txn.cursor, txn.user, values_ax, txn.context)            
            obj_id = estr_obj.create(txn.cursor, txn.user, values, txn.context)
            estategy = estr_obj.browse(txn.cursor, txn.user, obj_id, txn.context)
            pr_id = prog_obj.create(txn.cursor, txn.user, prog_data, txn.context)
            program = prog_obj.browse(txn.cursor, txn.user, pr_id, txn.context)
            self.assertEqual(program.name, prog_data['name'])

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
