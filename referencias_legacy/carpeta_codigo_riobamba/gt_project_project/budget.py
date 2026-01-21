# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

import time
import logging

from osv import osv, fields
import decimal_precision as dp


class ProjectBudgetTransfer(osv.Model):
    _name = 'project.budget.transfer'
    _description = 'Trasferencia de valores entre partidas'
    __logger = logging.getLogger(_name)    
    STATES = {'draft':[('readonly',False)]}

    def onchange_amount(self, cr, uid, ids, budget_from_id, amount):
        res = {}
        plan = self.pool.get('budget.item').browse(cr, uid, budget_from_id)
        if amount < 0:
            res = {'warning': {'title': 'Error de Datos', 'message': 'El valor debe ser mayor a cero.'},
                   'value': {'amount': 0}}
        avai_amount = plan.avai_amount
        if amount > avai_amount:
            res = {'warning': {'title': 'Error', 'message': 'El valor a transferir no puede sobrepasar el disponible: $%s' % avai_amount},
                   'value': {'amount': 0}}            
        return res

    def action_transfer(self, cr, uid, ids, context=None):
        self.__logger.info('Accion de confirmar la transferencia de fondos.')
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'ok'})
        return True

    _columns = {
        'name': fields.char('Número', size=16, required=True, readonly=True),
        'project_from_id': fields.many2one(
            'project.project',
            'Proyecto Origen',
            required=True,
            states=STATES
            ),
        'project_to_id': fields.many2one(
            'project.project',
            'Proyecto Destino',
            required=True,
            states=STATES
            ),
        'activity_from_id': fields.many2one(
            'project.task',
            'Actividad Origen',
            required=True,
            states=STATES
            ),
        'activity_to_id': fields.many2one(
            'project.task',
            'Actividad Destino',
            required=True,
            states=STATES
            ),
        'budget_from_id': fields.many2one(
            'budget.item',
            string='Partida Origen',
            required=True,
            states=STATES
            ),
        'budget_to_id': fields.many2one(
            'budget.item',
            string='Partida Destino',
            required=True,
            states=STATES
            ),
        'amount': fields.float('Valor a transferir', states=STATES),
        'state': fields.selection([
            ('draft', 'Borrador'),
            ('ok', 'Aprobado')],
            string='Estado',
            readonly=True
            ),
        }

    _defaults = {
        'name': '/',
        'state': 'draft',
        }

    def check_budget_amount(self, cr, uid, ids):
        """
        Implementa la verificacion de disponibilidad en la partida
        para que se permita el transpaso de fondos.
        """
        for obj in self.browse(cr, uid, ids):
            if (obj.budget_from_id.avai_amount - obj.amount) < 0:
                raise osv.except_osv('Error',
                                     'No existe el disponible requerido en la PARTIDA ORIGEN seleccionada.')
        return True

    _constraints = [(check_budget_amount, 'No existe presupuesto disponible para la transferencia.', ['Valor a Transferir'])]

    _sql_constraints = [
        ('gt_zero_amount', 'CHECK (amount>0)', 'El VALOR A TRANSFERIR debe ser mayor a cero.'),
        ]



#class BudgetItem(osv.Model):
#    _inherit = 'budget.item'

#    _columns = {
#        'program_id': fields.related(
#            'project_id', 'program_id',
#            type='many2one', relation='project.program',
#            store=True, readonly=True, string='Programa'),
#        }
