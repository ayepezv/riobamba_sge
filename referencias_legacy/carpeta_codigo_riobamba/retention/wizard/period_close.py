# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class account_period_close(osv.osv_memory):
    """
        close period
    """
    _inherit = "account.period.close"
    _description = "period close"
    _columns = dict(
        sure = fields.boolean('Check this box'),
        data_balance = fields.binary('Archivo de Balance', filters="*.txt"),
        data_cedulas = fields.binary('Archivo de Cedulas', filters="*.txt"),
        data_transferencias = fields.binary('Archivo de Transferencias', filters="*.txt"),
    )

    def data_save(self, cr, uid, ids, context=None):
        """
        This function close period
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: account period close’s ID or list of IDs
         """
        period_pool = self.pool.get('account.period')
        account_move_obj = self.pool.get('account.move')
        obj_acc_move_line = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        mode = 'done'
        for form in self.read(cr, uid, ids, context=context):
            #guarda los archivos de txt
            period = period_pool.browse(cr, uid, context['active_id'])
            if period.total_cierre == 0:
                if not form['data_balance']:
                    raise osv.except_osv('Error de usuario','Debe seleccionar el archivo texto del balance validado en el esigef para el periodo')
                if not form['data_cedulas']:
                    raise osv.except_osv('Error de usuario','Debe seleccionar el archivo texto de la cedula validado en el esigef para el periodo')
                if not form['data_transferencias']:
                    raise osv.except_osv('Error de usuario','Debe seleccionar el archivo texto de transferencias validado en el esigef para el periodo')
                period_pool.write(cr, uid, context['active_id'],{
                    'data_balance':form['data_balance'],
                    'data_cedulas':form['data_cedulas'],
                    'data_transferencias':form['data_transferencias'],
                    'total_cierre':1,
                })
            else:
                aux_cierre = period.total_cierre + 1
                period_pool.write(cr, uid, context['active_id'],{
                    'total_cierre':aux_cierre,
                })
            if form['sure']:
                for id in context['active_ids']:
                    cr.execute('update account_journal_period set state=%s where period_id=%s', (mode, id))
                    cr.execute('update account_period set state=%s where id=%s', (mode, id))
                    # Log message for Period
                    for period_id, name in period_pool.name_get(cr, uid, [id]):
                        period_pool.log(cr, uid, period_id, "Period '%s' is closed, no more modification allowed for this period." % (name))
        return {'type': 'ir.actions.act_window_close'}

account_period_close()
