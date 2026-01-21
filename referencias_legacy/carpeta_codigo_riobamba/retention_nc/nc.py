# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from time import strftime, strptime
from osv import osv, fields

class accountNc(osv.Model):
    _name = 'account.nc'
    _columns = dict(
        partner_id = fields.many2one('res.partner','Proveedor',required=True),
        name = fields.char('Numero',size=15),
        fecha = fields.date('Fecha'),
        base = fields.float('Base imponible'),
        iva = fields.float('Iva'),
        total = fields.float('Total'),
    )
accountNc()

class ncPayLine(osv.TransientModel):
    _name = 'nc.pay.line'
    _columns = dict(
        n_id = fields.many2one('nc.pay','Nota Credito'),
        move_line_id = fields.many2one('account.move.line','Movimiento'),
        account_id = fields.many2one('account.account','Cuenta'),
        debe = fields.float('Debe'),
        haber = fields.float('Haber'),
        disminuye = fields.boolean('Disminuir'),
        debe_d = fields.float('Disminuye Debe'),
        haber_d = fields.float('Disminuye Haber'),
    )
ncPayLine()

class ncPay(osv.TransientModel):
    _name = 'nc.pay'
    _columns = dict(
        partner_id = fields.many2one('res.partner','Proveedor'),
        nc_id = fields.many2one('account.nc','Nota de credito'),
        line_ids = fields.one2many('nc.pay.line','n_id','Detalle'),
    )

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        record_id = context and context.get('active_id', False) or False
        move = self.pool.get('account.move').browse(cr, uid, record_id, context=context)
        res.update({'partner_id':move.partner_id.id,
                })
        return res

    def loadNc(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('nc.pay.line')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        move = move_obj.browse(cr, uid, context['active_id'])
        for this in self.browse(cr, uid, ids):
            for move_line in move.line_id:
                line_obj.create(cr, uid, {
                    'n_id':this.id,
                    'move_line_id':move_line.id,
                    'account_id':move_line.account_id.id,
                    'debe':move_line.debit,
                    'haber':move_line.credit,
                })
        return True

    def disminuyeNc(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                if line.disminuye:
                    move_line_obj.create(cr, uid, {
                        'move_id':context['active_id'],
                        'account_id':line.account_id.id,
                        'debit':line.debe_d,
                        'credit':line.haber_d,
                        'budget_id_cert':line.move_line_id.budget_id_cert.id,
                        'budget_accrued':line.move_line_id.budget_accrued,
                        'budget_paid':line.move_line_id.budget_paid,
                        'move_line_cxp':line.move_line_id.id,
                    })
        return {'type':'ir.actions.act_window_close' }

ncPay()
