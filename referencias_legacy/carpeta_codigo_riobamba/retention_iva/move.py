# -*- coding: utf-8 -*-
##############################################################################
#
#    Gestion de Obras - GobERP
#    Copyright (C) 2013 Mario Chogllo
#    mariofchogllo@gmail..com
#    www.goberp.com
#
##############################################################################

from tools import ustr
from osv import osv, fields
import time
from lxml import etree
import csv
import decimal_precision as dp

class moveIva(osv.Model):
    _inherit = 'account.move'

    def onchange_cp(self, cr, uid, ids, cp,iva,iva_id2,renta_id2,inv_id,iva_srv,renta_srv, period=False, date=False,journal=False):
        result = {}
        value = []
        certificate_obj = self.pool.get('budget.certificate')
        tax_obj = self.pool.get('account.tax')
        map_obj = self.pool.get('account.tax.map')
        post_obj = self.pool.get('budget.post')
        line_obj = self.pool.get('account.move.line')
        company_obj = self.pool.get('res.company')
        move_obj = self.pool.get('account.move')
        account_obj = self.pool.get('account.account')
        certificate_obj = self.pool.get('budget.certificate')
        partner_account_obj = self.pool.get('partner.account')
        cert = certificate_obj.browse(cr, uid, cp)
        move_ids = move_obj.search(cr, uid, [('certificate_id','=',cert.id),('state','=','posted')])
        if move_ids:
            MSG = 'El documento presupuestario esta ya relacionado en otro(s) comprobante(s)'
        result['narration'] = cert.notes
        #######################
        result = {}
        value = []
        iva_id = renta_id = iva_id_srv = renta_id_srv = None
        if iva_id2:
            iva_id = tax_obj.browse(cr, uid, iva_id2)
        if renta_id2:
            renta_id = tax_obj.browse(cr, uid, renta_id2)
        if iva_srv:
            iva_id_srv = tax_obj.browse(cr, uid, iva_srv)
        if renta_srv:
            renta_id_srv = tax_obj.browse(cr, uid, renta_srv)
        if inv_id:
            inv_id = account_obj.browse(cr, uid, inv_id)
        if not period:
            MSG = 'Debe seleccionar un periodo'
            raise osv.except_osv('Error', MSG)
        if not date:
            MSG = 'Debe seleccionar una fecha'
            raise osv.except_osv('Error', MSG)
        if not journal:
            MSG = 'Debe seleccionar un diario'
            raise osv.except_osv('Error', MSG)
        account_aux = '0'
        #si hay lineas en el move elimina las lineas
        for move in self.browse(cr, uid, ids):
            if move.state=='draft':
                line_ant_ids = line_obj.search(cr, uid, [('move_id','=',move.id)])
                if line_ant_ids:
                    line_obj.unlink(cr, uid, line_ant_ids)
        partner_id = cert.partner_id.id
        compania = company_obj.browse(cr, uid, 1)
        partner_account_ids = []
        for line in cert.line_ids:
            aux_partida = line.budget_post.code[0:2]
            partner_id = cert.partner_id.id
            budget_id = line.budget_id
            account_aux_ids = account_obj.search(cr, uid, [('budget_id','=',budget_id.budget_post_id.id)])
            if not account_aux_ids:
                aux_6 = line.budget_id.budget_post_id.code[0:6]
                aux_budget_6_ids = post_obj.search(cr, uid, [('code','=',aux_6)])
                if aux_budget_6_ids:
                    account_aux_ids = account_obj.search(cr, uid, [('budget_id','=',aux_budget_6_ids[0])])
            if len(account_aux_ids)>0:
                for account_id in account_aux_ids:
                    account = account_obj.browse(cr, uid, account_id)
                    if account.account_rec_id or account.account_pay_id:
                        account_aux = account.id
                        continue
                    else:
                        aux_partida = line.budget_post.code[0:2]
                        partner_account_ids = partner_account_obj.search(cr, uid, [('name','=',aux_partida),('p_id','=',line.certificate_id.partner_id.id)])
                        if partner_account_ids:
                            account_aux = account.id
                            continue
                if account_aux=='0':
                    MSG = 'La partida %s no tiene configurada la cuenta por pagar' % (account.code)
                    raise osv.except_osv('Error', MSG)
                account = account_obj.browse(cr, uid, account_aux)
                if partner_account_ids:
                    partner_account = partner_account_obj.browse(cr, uid, partner_account_ids[0])
                    account_aux2 = partner_account.account_id.id
                elif account.account_rec_id:
                    account_aux2 = account.account_rec_id.id
                elif account.account_pay_id:
                    account_aux2 = account.account_pay_id.id
                else:
                    aux_name_cuenta = account.code + ' - ' + account.name
                    MSG = 'La cuenta %s de la partida %s no tiene configurada la cuenta por pagar' % (aux_name_cuenta,budget_id.budget_post_id.name)
                    raise osv.except_osv('Error', MSG)
            else:
                aux_msg_contra = budget_id.budget_post_id.code + ' - ' + budget_id.budget_post_id.name
                MSG = 'La partida %s no tiene configurada la contra cuenta' % (aux_msg_contra)
                raise osv.except_osv('Error', MSG)
            aux_code_budget = line.budget_post.code[0:2]
            if line.tipo_invoice in ('Bien','Servicio','Iess'):
                amount_aux = 0
                aux_band = True
                if (line.budget_accrued < line.amount_commited) or (line.certificate_id.partner_id.id==compania.iess_id.id) or (line.amount_commited<0):
                    amount_aux = line.amount_commited - line.budget_accrued
                    if line.tipo_invoice:
                        if line.tipo_invoice=='Iess':
                            partner_id = compania.iess_id.id
                        aux_name2 = line.tipo_invoice
                    else:
                        aux_name2 = 'REF'
                    if inv_id:
                        account_aux = inv_id.id
                    id_creado_pat = line_obj.create(cr, uid, {
                        'journal_id': journal,
                        'budget_id_cert':line.id,
                        'account_id':account_aux,
                        'debit':amount_aux,
                        'period_id': period,
                        'date': date,
                        'budget_accrued':True,
                        'name':aux_name2,
                        'partner_id':partner_id,
                    })
                    value.append(id_creado_pat)
                if (line.budget_paid < line.amount_commited) or (line.certificate_id.partner_id.id==compania.iess_id.id) or (line.amount_commited<0):
                    aux_iva = aux_renta = 0 
                    account_iess_3 = False
                    if line.tipo_invoice == 'Bien':
                        if iva_id:
                            aux_iva = (line.amount_commited) * (int(iva)) / (100.00)
                        if renta_id:
                            aux_renta = (line.amount_commited) * (float(renta_id.porcentaje)) /100.00
                    elif line.tipo_invoice == 'Servicio':
                        if iva_srv:
                            aux_iva = (line.amount_commited) * (int(iva)) / (100.00)
                        if renta_srv:
                            if float(renta_id_srv.porcentaje)<1:
                                aux_renta = (line.amount_commited) * (float(renta_id_srv.porcentaje)) /100.00
                            else:
                                aux_renta = (line.amount_commited) * (float(renta_id_srv.porcentaje)) /100.00
                    elif line.tipo_invoice == 'Iess':
                        if account.tercero_id:
                            account_iess_3 = account.tercero_id.id
                    amount_aux = line.amount_commited - aux_renta
                    if line.tipo_invoice:
                        aux_name2 = line.tipo_invoice
                    else:
                        aux_name2 = 'REF'
                    if account_iess_3:
                        id_creado_pp = line_obj.create(cr, uid, {
                            'journal_id': journal,
                            'period_id': period,
                            'date': date,
                            'budget_id_cert':line.id,
                            'account_id':account_aux2,
                            'account_id2':account_iess_3,
                            'credit':amount_aux,
                            'name':aux_name2,
                            'partner_id':partner_id,
                        })
                    else:
                        id_creado_pp = line_obj.create(cr, uid, {
                            'journal_id': journal,
                            'period_id': period,
                            'date': date,
                            'budget_id_cert':line.id,
                            'account_id':account_aux2,
                            'credit':amount_aux,
                            'name':aux_name2,
                            'partner_id':partner_id,
                        })
                    value.append(id_creado_pp)
                    if renta_id:
                        partner_id = compania.tax_company_id.id
                        map_ids = map_obj.search(cr, uid, [('budget','=',aux_code_budget),('tax_id','=',renta_id.id)])
                        if map_ids:
                            map = map_obj.browse(cr, uid, map_ids[0])
                            account_aux2 = map.account_id.id
                        if renta_id.account_id:
                            if aux_renta>0:
                                id_creado_pp = line_obj.create(cr, uid, {
                                    'journal_id': journal,
                                    'period_id': period,
                                    'date': date,
                                    'budget_id_cert':line.id,
                                    'account_id':account_aux2,
                                    'account_id2':renta_id.account_id.id,
                                    'credit':aux_renta,
                                    'name':aux_name2,
                                    'partner_id':partner_id,
                                })
                                value.append(id_creado_pp)
                        else:
                            if aux_renta>0:
                                id_creado_pp = line_obj.create(cr, uid, {
                                    'journal_id': journal,
                                    'period_id': period,
                                    'partner_id':partner_id,
                                    'date': date,
                                    'budget_id_cert':line.id,
                                    'account_id':account_aux2,
                                    'credit':aux_renta,
                                    'name':aux_name2,
                                })
                                value.append(id_creado_pp)
                    elif renta_id_srv:
                        partner_id = compania.tax_company_id.id
                        map_ids = map_obj.search(cr, uid, [('budget','=',aux_code_budget),('tax_id','=',renta_id_srv.id)])
                        if map_ids:
                            map = map_obj.browse(cr, uid, map_ids[0])
                            account_aux2 = map.account_id.id
                        if renta_id_srv.account_id:
                            if aux_renta>0:
                                id_creado_pp = line_obj.create(cr, uid, {
                                    'journal_id': journal,
                                    'period_id': period,
                                    'date': date,
                                    'budget_id_cert':line.id,
                                    'account_id':account_aux2,
                                    'account_id2':renta_id_srv.account_id.id,
                                    'credit':aux_renta,
                                    'name':aux_name2,
                                    'partner_id':partner_id,
                                })
                                value.append(id_creado_pp)
                        else:
                            if aux_renta>0:
                                id_creado_pp = line_obj.create(cr, uid, {
                                    'journal_id': journal,
                                    'period_id': period,
                                    'partner_id':partner_id,
                                    'date': date,
                                    'budget_id_cert':line.id,
                                    'account_id':account_aux2,
                                    'credit':aux_renta,
                                    'name':aux_name2,
                                })
                                value.append(id_creado_pp)
            else:
                if line.tipo_invoice=='SRI':
                    partner_id = compania.tax_company_id.id
                    aux_name2 = line.tipo_invoice
                else:
                    aux_name2 = 'REF'
                if inv_id:
                    account_aux = inv_id.id
                id_creado_pat = line_obj.create(cr, uid, {
                    'journal_id': journal,
                    'budget_id_cert':line.id,
                    'account_id':account_aux,
                    'debit':line.amount_commited,
                    'period_id': period,
                    'date': date,
                    'budget_accrued':True,
                    'name':aux_name2,
                    'partner_id':partner_id,
                })
                value.append(id_creado_pat)
                aux_iva_fisco = aux_iva_proveedor = aux_renta = 0
                if line.tipo_invoice=='Iva':
                    if iva_id:
                        map_ids = map_obj.search(cr, uid, [('budget','=',aux_code_budget),('tax_id','=',iva_id.id)])
                        if map_ids:
                            map = map_obj.browse(cr, uid, map_ids[0])
                            account_aux2 = map.account_id.id
                        aux_proveedor = 100 - int(iva_id.porcentaje) 
                        aux_iva_fisco = (line.amount_commited) * (int(iva_id.porcentaje)) /100.00
                        if iva_id.account_id:
                            id_creado_pp = line_obj.create(cr, uid, {
                                'journal_id': journal,
                                'period_id': period,
                                'partner_id':partner_id,
                                'date': date,
                                'budget_id_cert':line.id,
                                'account_id':account_aux2,
                                'account_id2':iva_id.account_id.id,
                                'credit':aux_iva_fisco,
                                'name':aux_name2,
                            })
                        else:
                            id_creado_pp = line_obj.create(cr, uid, {
                                'journal_id': journal,
                                'period_id': period,
                                'date': date,
                                'partner_id':partner_id,
                                'budget_id_cert':line.id,
                                'account_id':account_aux2,
                                'credit':aux_iva_fisco,
                                'name':aux_name2,
                            })
                        value.append(id_creado_pp)
                        tax_proveedor_ids = tax_obj.search(cr, uid, [('tax_group','=','other'),('porcentaje','=',str(aux_proveedor))]) 
                        if tax_proveedor_ids:
                            map_ids = map_obj.search(cr, uid, [('budget','=',aux_code_budget),('tax_id','=',tax_proveedor_ids[0])])
                            if map_ids:
                                map = map_obj.browse(cr, uid, map_ids[0])
                                account_aux2 = map.account_id.id
                        aux_iva_proveedor = line.amount_commited - aux_iva_fisco
                        if aux_iva_proveedor>0:
                            id_creado_pp = line_obj.create(cr, uid, {
                                'journal_id': journal,
                                'period_id': period,
                                'date': date,
                                'budget_id_cert':line.id,
                                'account_id':account_aux2,
                                'credit':aux_iva_proveedor,
                                'name':aux_name2,
                                'partner_id':partner_id,
                            })
                            value.append(id_creado_pp)
                    else:
                        tax_proveedor_ids = tax_obj.search(cr, uid, [('tax_group','=','other'),('porcentaje','=','100')]) 
                        if tax_proveedor_ids:
                            map_ids = map_obj.search(cr, uid, [('budget','=',aux_code_budget),('tax_id','=',tax_proveedor_ids[0])])
                            if map_ids:
                                map = map_obj.browse(cr, uid, map_ids[0])
                                account_aux2 = map.account_id.id
                        aux_iva_proveedor = line.amount_commited
                        id_creado_pp = line_obj.create(cr, uid, {
                            'journal_id': journal,
                            'period_id': period,
                            'date': date,
                            'budget_id_cert':line.id,
                            'account_id':account_aux2,
                            'credit':aux_iva_proveedor,
                            'name':aux_name2,
                            'partner_id':partner_id,
                        })
                        value.append(id_creado_pp)
                elif line.tipo_invoice=='IvaServicios':
                    if iva_id_srv:
                        map_ids = map_obj.search(cr, uid, [('budget','=',aux_code_budget),('tax_id','=',iva_id_srv.id)])
                        if map_ids:
                            map = map_obj.browse(cr, uid, map_ids[0])
                            account_aux2 = map.account_id.id
                        aux_proveedor = 100 - int(iva_id_srv.porcentaje) 
                        aux_iva_fisco = (line.amount_commited) * (int(iva_id_srv.porcentaje)) /100.00
                        if iva_id_srv.account_id:
                            id_creado_pp = line_obj.create(cr, uid, {
                                'journal_id': journal,
                                'period_id': period,
                                'partner_id':partner_id,
                                'date': date,
                                'budget_id_cert':line.id,
                                'account_id':account_aux2,
                                'account_id2':iva_id_srv.account_id.id,
                                'credit':aux_iva_fisco,
                                'name':aux_name2,
                            })
                        else:
                            id_creado_pp = line_obj.create(cr, uid, {
                                'journal_id': journal,
                                'period_id': period,
                                'date': date,
                                'partner_id':partner_id,
                                'budget_id_cert':line.id,
                                'account_id':account_aux2,
                                'credit':aux_iva_fisco,
                                'name':aux_name2,
                            })
                        value.append(id_creado_pp)
                        tax_proveedor_ids = tax_obj.search(cr, uid, [('tax_group','=','other'),('porcentaje','=',str(aux_proveedor))]) 
                        if tax_proveedor_ids:
                            map_ids = map_obj.search(cr, uid, [('budget','=',aux_code_budget),('tax_id','=',tax_proveedor_ids[0])])
                            if map_ids:
                                map = map_obj.browse(cr, uid, map_ids[0])
                                account_aux2 = map.account_id.id
                        aux_iva_proveedor = line.amount_commited - aux_iva_fisco
                        if aux_iva_proveedor>0:
                            id_creado_pp = line_obj.create(cr, uid, {
                                'journal_id': journal,
                                'period_id': period,
                                'date': date,
                                'budget_id_cert':line.id,
                                'account_id':account_aux2,
                                'credit':aux_iva_proveedor,
                                'name':aux_name2,
                                'partner_id':partner_id,
                            })
                            value.append(id_creado_pp)
                    else:
                        tax_proveedor_ids = tax_obj.search(cr, uid, [('tax_group','=','other'),('porcentaje','=','100')]) 
                        if tax_proveedor_ids:
                            map_ids = map_obj.search(cr, uid, [('budget','=',aux_code_budget),('tax_id','=',tax_proveedor_ids[0])])
                            if map_ids:
                                map = map_obj.browse(cr, uid, map_ids[0])
                                account_aux2 = map.account_id.id
                        aux_iva_proveedor = line.amount_commited
                        id_creado_pp = line_obj.create(cr, uid, {
                            'journal_id': journal,
                            'period_id': period,
                            'date': date,
                            'budget_id_cert':line.id,
                            'account_id':account_aux2,
                            'credit':aux_iva_proveedor,
                            'name':aux_name2,
                            'partner_id':partner_id,
                        })
                        value.append(id_creado_pp)
                else:
                    partner_id = line.certificate_id.partner_id.id
                    tax_ids = tax_obj.search(cr, uid, [('porcentaje','=',100),('tax_group','=','other')])
                    map_ids = map_obj.search(cr, uid, [('budget','=',aux_code_budget),('tax_id','=',tax_ids[0])])
                    if map_ids:
                        map = map_obj.browse(cr, uid, map_ids[0])
                        account_aux2 = map.account_id.id
                    id_creado_pp = line_obj.create(cr, uid, {
                        'journal_id': journal,
                        'period_id': period,
                        'partner_id':partner_id,
                        'date': date,
                        'budget_id_cert':line.id,
                        'account_id':account_aux2,
                        'credit':line.amount_commited,
                        'name':'100 Proveedor',
                    })
                    value.append(id_creado_pp)
        result['line_id'] = value
        result['narration'] = cert.notes
        result['ref'] = cert.notes
        return {'value': result}

    _columns = dict(
        iva_id = fields.many2one('account.tax','Iva Fisco Bien'),
        renta_id = fields.many2one('account.tax','Retencion Renta Bien'),
        iva_id2 = fields.many2one('account.tax','Iva Fisco Srv.'),
        renta_id2 = fields.many2one('account.tax','Retencion Renta Srv.'),
        cta_inventario = fields.many2one('account.account','Cuenta de Inventario'),
        iva = fields.selection([('12','12'),('14','14')],'IVA APLICA'),
    )
    _defaults = dict(
        iva='12',
    )
moveIva()
