# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import fields, osv

class revertMove(osv.TransientModel):
    _name = 'revert.move'
    _columns = dict(
        year_id = fields.many2one('account.fiscalyear','Anio'),
        move_id = fields.many2one('account.move','Comprobante a reversar'),
        date = fields.date('Fecha Comprobante Nuevo'),
    )
    
    def revert_move(self, cr, uid, ids, context):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            period_ids = period_obj.find(cr, uid, this.date)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            move = this.move_id
            aux_narration = 'COMPROBANTE REVERSO' + ' - ' + move.narration
            if move.certificate_id:
                move_id = move_obj.create(cr, uid, {
                    'partner_id':move.partner_id.id,
                    'certificate_id':move.certificate_id.id,
                    'journal_id':move.journal_id.id,
                    'period_id':period_ids[0],
                    'date':this.date,
                    'afectacion':True,
                })
            else:
                move_id = move_obj.create(cr, uid, {
                    'partner_id':move.partner_id.id,
                    'journal_id':move.journal_id.id,
                    'period_id':period_ids[0],
                    'date':this.date,
                })
            for line in move.line_id:
                aux_debit = aux_credit = 0
                if line.debit:
                    aux_debit = (-1)*(line.debit)
                if line.credit:
                    aux_credit = (-1)*(line.credit)
                if line.budget_id:
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'budget_id_cert':line.budget_id_cert.id,
                        'budget_accrued':line.budget_accrued,
                        'budget_paid':line.budget_paid,
                        'debit':aux_debit,
                        'credit':aux_credit,
                        'name':line.name,
                        'account_id':line.account_id.id,
                    })
                else:
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'debit':aux_debit,
                        'credit':aux_credit,
                        'name':line.name,
                        'account_id':line.account_id.id,
                    })

        return True

revertMove()
