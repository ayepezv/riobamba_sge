# -*- coding: utf-8 -*-

from osv import osv, fields

class DocumentReportCash(osv.TransientModel):
    _inherit = 'account.common.report'
    _name = 'document.report.consolidate'
    _columns = {
        'account_invoice': fields.boolean('Facturas de Proveedores por Pagar ?',
                                          default=True),
        'doc_contract': fields.boolean('Contratos ?'),
        'doc_covenant': fields.boolean('Convenios'),
        'contract_state': fields.selection([('draft', 'Borrador'),
                                            ('legalizing', 'Abierto'),
                                            ('open', 'Distribución'),
                                            ('execution', 'Ejecución')],
                                            string='Estado de Contratos'),
        'covenant_state': fields.selection([('draft', 'Borrador'),
                                            ('legalizing', 'Abierto'),
                                            ('open', 'Distribución'),
                                            ('execution', 'Ejecución')],
                                            string='Estado de convenios'),
        }

    _defaults = {
        'filter': 'filter_period',
        'account_invoice': True,
        'doc_contract': True,
        'doc_covenant': True,
        'contract_state': 'open',
        'covenant_state': 'open'        
        }

    def action_print_report(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado
        Fechas de consulta para documentos
        contratos: fecha_inicio
        convenios: suscription_date
        facturas: date_due
        '''
        contract_obj = self.pool.get('doc_contract.contract')
        conv_obj = self.pool.get('doc_covenant.covenant')
        inv_obj = self.pool.get('account.invoice')
        line_obj = self.pool.get('contract.payment.line')
        if not context:
            context = {}
        wiz = self.browse(cr, uid, ids, context)[0]
        fini = wiz.period_from.date_start
        ffin = wiz.period_to.date_stop
        inv_ids = inv_obj.search(cr, uid, [('state','=','open'),
                                           ('type','=','in_invoice'),
                                           ('date_due','>=',fini),
                                           ('date_due','<=',ffin)])
        
        line_ids = line_obj.search(cr, uid, [('date','>=',fini),('date','<=',ffin)])
        
        cont_ids = contract_obj.search(cr, uid, [('state','=',wiz.covenant_state),
                                                 ('fecha_inicio','>=',fini),
                                                 ('fecha_inicio','<=',ffin)])
        
        conv_ids = conv_obj.search(cr, uid, [('state','=',wiz.covenant_state),
                                             ('subscription_date','>=',fini),
                                             ('subscription_date','<=',ffin)])
        datas = {'lines': line_ids,
                 'invoices': inv_ids,
                 'fiscalyear': wiz.fiscalyear_id.name}

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'document_consolidate1_report',
            'model': 'document.report.consolidate',
            'datas': datas,
            'nodestroy': True,                        
            }
