# -*- coding: utf-8 -*-
##############################################################################
#
# Mario chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import osv, fields

class resBank(osv.Model):
    _inherit = 'res.bank'

#    def write(self, cr, uid, ids, vals, context=None):
#        raise osv.except_osv(('Aviso !'), 'No puede editar la informacion de bancos, el catalogo es normado por el banco central y unico')

    _columns = dict(
        bic = fields.char('Codigo de identificador bancario',size=8,required=True),
        desc = fields.char('Desc. Corta',size=5,required=True),
        )

#    _sql_constraints = [('unique_number', 'unique(bic)', u'El codigo de banco es unico.')]

resBank()

class resBankAccount(osv.osv):
    _inherit = 'res.partner.bank'
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            name = record.bank.name + ' : ' + record.acc_number
            res.append((record.id, name))
        return res
    
    def _check_numero_cta(self, cr, uid, ids):
        for cuenta in self.browse(cr, uid, ids):
            if cuenta.acc_number.isdigit():
                aux_int = int(cuenta.acc_number)
                if aux_int>0:
                    return True
                else:
                    return False
            else:
                return False

    def _check_numero_cta_unico(self, cr, uid, ids):
        return True
        bank_obj = self.pool.get('res.partner.bank')
        for cuenta in self.browse(cr, uid, ids):
            partner_ids = bank_obj.search(cr, uid, [('partner_id','=',cuenta.partner_id.id)])
            if len(partner_ids)>1:
#                print "cuenta repetida", cuenta.partner_id.ced_ruc
                raise osv.except_osv(('Aviso !'), 'Cuenta de banco es unica')
            else:
                return True
            
    _constraints = [
        (_check_numero_cta,'El numero de cuenta debe ser numerico sin caracteres',['Numero Cuenta']),
        (_check_numero_cta_unico,'El numero de cuenta debe ser unico',['Numero Cuenta']),
    ]

    _TIPO = [('aho','Cta. Ahorros'),('cte','Cta. Corriente'),
             ('vir','Cta. Virtual'),('esp','Especial')]
    _columns = {
        'spi_pay':fields.related('partner_id', 'pagar_spi', type='boolean',
                                     string='Pagar Con cedula',store=True,
                                     readonly=True),
        'type_cta': fields.selection(_TIPO , 'Tipo de cuenta', required=True),
        'bank': fields.many2one('res.bank', 'Bank', required=True),
        'partner_id':fields.many2one('res.partner','Propietario Cuenta'),
        }
    
    _defaults = dict(
        type_cta = 'aho',
        state = 'bank',
        )
resBankAccount()
