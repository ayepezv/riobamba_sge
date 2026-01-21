# -*- coding: utf-8 -*-
##############################################################################
#
# MarioChogllo
# mariofchogllo@gmail.com
#
##############################################################################
from osv import osv, fields
from tools import ustr

class spiLine(osv.Model):
    _inherit = 'spi.line'
    _columns = dict(
        
        ref = fields.related('concepto_id','code',type='char',size=6,store=True,string='Referencia BCE'),
        concepto_id = fields.many2one('spi.concepto','Concepto Egresos'),
    )
spiLine()

class spi_voucher(osv.Model):
    _inherit = 'account.spi.voucher'

    _columns = dict(
        directo = fields.boolean('Es Transf. Directa'),
        archivoDirecto = fields.binary('Archivo Transferencia Directa'),
    )

    def spi_import_normal(self,cr, uid, ids, context):
        concepto_obj = self.pool.get('spi.concepto')
        line_obj = self.pool.get('spi.line')
        partner_obj = self.pool.get('res.partner')
        journal_obj = self.pool.get('account.journal')
        no_obj = self.pool.get('hr.no.cobro')
        move_line_obj = self.pool.get('account.move.line')
        anteriores = []
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                anteriores.append(line.id)
            if this.tipo!='norol':
                line_obj.unlink(cr, uid, anteriores)
            if this.tipo=='pgeneral':
                if this.line2_ids:
                    concepto_ids = concepto_obj.search(cr, uid, [])
                    if concepto_ids:
                        concepto_id = concepto_ids[0]
                    for line in this.line2_ids:
                        if line.partner_id.bank_ids: 
                            ##carga el tipo de pago: 40102 bienes y srv,40101 sueldos,40300 inversion
                            for line_asiento in line.line_id:
                                if int(str(line_asiento.account_id.code[0:1]))>1 and  int(str(line_asiento.account_id.code[0:1]))<3:
                                    if line_asiento.debit>0:
                                        aux_ref = 0
                                        aux_code_acc = line_asiento.account_id.code
                                        aux_code_min = aux_code_acc[0:4]
                                        #if not line_asiento.account_id.budget_id:
                                        #    concepto_ids = concepto_obj.search(cr, uid, [])
                                        #    if concepto_ids:
                                        #        concepto_id = concepto_ids[0]
                                        #    break
                                        if aux_code_min == '2137': #inversion
                                            #concepto_ids = concepto_obj.search(cr, uid, [('code','like',aux_code_acc[3:5])])
                                            concepto_ids = concepto_obj.search(cr, uid, [('code','=','40300')])
                                            if concepto_ids:
                                                concepto_id = concepto_ids[0]
#                                            aux_ref = 40300
                                            break
                                        elif aux_code_min in ('1121','1120'): #anticipos
                                            concepto_ids = concepto_obj.search(cr, uid, [('code','=','40102')])
                                            if concepto_ids:
                                                concepto_id = concepto_ids[0]
#                                            aux_ref = 40101
                                            break
                                        elif aux_code_min in ('2135'):
                                            if line_asiento.budget_id:
                                                #concepto_ids = concepto_obj.search(cr, uid, [('code','like',aux_code_acc[3:5])])
                                                concepto_ids = concepto_obj.search(cr, uid, [('code','=','40100')])
                                                if concepto_ids:
                                                    concepto_id = concepto_ids[0]
                                            else:
                                                concepto_ids = concepto_obj.search(cr, uid, [])
                                                concepto_id = concepto_ids[0]
#                                            aux_ref = 40102
                                            break
                                        elif aux_code_min in ('2138'):
                                            if line_asiento.budget_id:
                                                #concepto_ids = concepto_obj.search(cr, uid, [('code','like',aux_code_acc[3:5])])
                                                concepto_ids = concepto_obj.search(cr, uid, [('code','=','40200')])
                                                if concepto_ids:
                                                    concepto_id = concepto_ids[0]
                                            else:
                                                concepto_ids = concepto_obj.search(cr, uid, [])
                                                concepto_id = concepto_ids[0]
#                                            aux_ref = 40102
                                            break
                                        else:
                                            if line_asiento.account_id.budget_id:
                                                concepto_ids = concepto_obj.search(cr, uid, [('partida_aux','=',line_asiento.account_id.budget_id.code[0:4])])
                                                if concepto_ids:
                                                    concepto_id = concepto_ids[0]
                                            else:
                                                concepto_ids = concepto_obj.search(cr, uid, [])
                                                if concepto_ids:
                                                    concepto_id = concepto_ids[0]
#                                            aux_ref = 40102
                                            break
                                else:
                                    if line_asiento.debit>0:
                                        concepto_ids = concepto_obj.search(cr, uid, [('code','=','40101')])
                                        if concepto_ids:
                                            concepto_id = concepto_ids[0]
                                #    aux_ref = 40101
                            bank_id = line.partner_id.bank_ids[0].id
                            aux_name = 'PAGO ' + line.name
                            if line.narration:
                                aux_name = 'PAGO ' + line.name + ' ' + line.narration.replace('\n',' ')
                            aux_name = aux_name[0:254]
                            #validar que solo tome el valor de la cuenta de banco
                            amount_pagar = 0
                            ba = 0
                            for line_asiento in line.line_id:
                                if line_asiento.credit>0 and line_asiento.account_id.id==this.journal_id.default_debit_account_id.id:
                                    aux_account_id = line_asiento.account_id
                                    journal_ids = journal_obj.search(cr, uid, [('type','=','bank'),('default_credit_account_id','=',line_asiento.account_id.id)])
                                    if journal_ids:
                                        if this.journal_id.id in journal_ids:
                                            move_line_obj.write(cr, uid, line_asiento.id,{'spi_numero':this.ref})
                                            ba += 1
#                                            raise osv.except_osv(('Error de usuario !'),
#                                                                 ("La cuenta de banco no corresponde con la del comprobante"))
                                        amount_pagar = line_asiento.credit
                                        #break
                            if ba<=0:
                                raise osv.except_osv(('Error de usuario !'),
                                                     ("La cuenta de banco no corresponde con la del comprobante"))
                            if amount_pagar <=0:
                                aux_cta_pagar = aux_account_id.code + ' - ' + aux_account_id.name
                                raise osv.except_osv(('Error Configuracion !'),
                                                     ("No existe cuenta de banco en el movimiento contable a pagar '%s' o el monto es menor a 1") % (aux_cta_pagar))
                            #move_line_obj.write(cr, uid, line_asiento.id,{'spi_numero':this.ref})
                            line_obj.create(cr, uid, {
                                'spi_id':this.id,
                                'partner_id':line.partner_id.id,
                                'move_id':line.id,
                                'amount':amount_pagar,#line.amount,
                                'name':aux_name,
                                'bank_id':bank_id,
                                #'ref':aux_ref,  #cambiar por la tabla se hace related
                                'concepto_id':concepto_id,
                            })
                        else:
                            raise osv.except_osv(('Error Configuracion !'),("No existe cuenta de banco de '%s'") % (line.partner_id.name,))
                else:
                            raise osv.except_osv(('Error de Usuario !'),("No ha seleccionado comprobantes contables para pago"))
                if this.directo:
                    self.spi_realizado(cr, uid, [this.id],context)
            elif this.tipo=='norol':
                line_ids = line_obj.search(cr, uid, [('no_pagado_rol','=',True)])
                if line_ids:
                    for line_id in line_ids:
                        line_obj.write(cr, uid, line_id,{'spi_id':this.id})            
            elif this.tipo=='quincena':
                if this.quincena_id:
                    for line_quincena in this.quincena_id.line_ids:
                        for line_line_quincena in line_quincena.line_ids:
                            for line_line_line in line_line_quincena.line_ids:
                                employee = line_line_line.employee_id
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
                                if not partner_ids:
                                    raise osv.except_osv(('Error'), 
                                                         ('El beneficiario %s no esta en la base de proveedores debe estar registrado') % (employee.complete_name))
                                partner = partner_obj.browse(cr, uid, partner_ids[0])
                                if partner.bank_ids:
                                    bank_id = partner.bank_ids[0].id
                                    aux_name = ustr('PAGO QUINCENA' + employee.complete_name)
                                    aux_ref = '40101'
                                    concepto_ids = concepto_obj.search(cr, uid, [('code','=','40101')])
                                    if concepto_ids:
                                        concepto_id = concepto_ids[0]
                                    else:
                                        concepto_ids = concepto_obj.search(cr, uid, [])
                                        concepto_id = concepto_ids[0]
                                    line_obj.create(cr, uid, {
                                        'spi_id':this.id,
                                        'partner_id':partner.id,
                                        'amount':line_line_line.valor,
                                        'name':aux_name,
                                        'ref':aux_ref,
                                        'concepto_id':concepto_id,
                                        'bank_id':bank_id,
                                    })
                                else:
                                    raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (employee.complete_name))
            elif this.tipo=='mensual':
                if this.payroll_id:
                    contratos_no = []
                    if this.payroll_id.normal:
                        no_cobra_ids = no_obj.search(cr, uid, [])
                    if no_cobra_ids:
                        for no_cobra_id in no_cobra_ids:
                            no_cobra = no_obj.browse(cr, uid, no_cobra_id)
                            contratos_no.append(no_cobra.contract_id.id)
                    for slip in this.payroll_id.slip_ids :
                        if slip.net>0:
                            employee = slip.employee_id
                            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
                            if not partner_ids:
                                raise osv.except_osv(('Error'), ('El beneficiario %s no esta en la base de proveedores debe estar registrado') % (employee.complete_name))
                            partner = partner_obj.browse(cr, uid, partner_ids[0])
                            if partner.bank_ids:
                                bank_id = partner.bank_ids[0].id
                                aux_name = ustr('PAGO MENSUAL ' + employee.complete_name)
                                aux_ref = '40101'
                                concepto_ids = concepto_obj.search(cr, uid, [('code','=','40101')])
                                if concepto_ids:
                                    concepto_id = concepto_ids[0]
                                if slip.net<0:
                                    raise osv.except_osv(('Error'), ('No se puede pagar un rol negativo, verificar rol de %s ') % (partner.name))
                                if slip.contract_id.id in contratos_no:
                                    line_obj.create(cr, uid, {
                                        'no_pagado_rol':True,
                                        'partner_id':partner.id,
                                        'amount':slip.net,
                                        'name':aux_name,
                                        'ref':aux_ref,
                                        'bank_id':bank_id,
                                    })
                                else:
                                    line_obj.create(cr, uid, {
                                        'spi_id':this.id,
                                        'partner_id':partner.id,
                                        'amount':slip.net,
                                        'name':aux_name,
                                        'ref':aux_ref,
                                        'concepto_id':concepto_id,
                                        'bank_id':bank_id,
                                    })
                            else:
                                if not (slip.contract_id.id in contratos_no):
                                    raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (employee.complete_name))
            elif this.tipo=='dec3':
                if this.dec3_id:
                    for decimo in this.dec3_id.line_ids:
                        if decimo.recibir>0:
                            employee = decimo.contract_id.employee_id
                            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
                            if not partner_ids:
                                raise osv.except_osv(('Error'), ('El beneficiario %s no esta en la base de proveedores debe estar registrado') % (employee.complete_name))
                            partner = partner_obj.browse(cr, uid, partner_ids[0])
                            if partner.bank_ids:
                                bank_id = partner.bank_ids[0].id
                                aux_name = ustr('PAGO DECIMO TERCERO ' + employee.complete_name)
                                aux_ref = '40101'
                                concepto_ids = concepto_obj.search(cr, uid, [('code','=','40101')])
                                if concepto_ids:
                                    concepto_id = concepto_ids[0]
                                if decimo.recibir<0:
                                    raise osv.except_osv(('Error'), ('No se puede pagar decimo negativo, verificar rol de %s ') % (partner.name))
                                line_obj.create(cr, uid, {
                                    'spi_id':this.id,
                                    'partner_id':partner.id,
                                    'amount':decimo.recibir,
                                    'name':aux_name,
                                    'concepto_id':concepto_id,
                                    'ref':aux_ref,
                                    'bank_id':bank_id,
                                })
                            else:
                                raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (employee.complete_name))
            elif this.tipo=='dec4':
                if this.dec4_id:
                    for decimo in this.dec4_id.line_ids:
                        if decimo.recibir>0:
                            #print "empleado", decimo.contract_id
                            employee = decimo.employee_id
                            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
                            if not partner_ids:
                                raise osv.except_osv(('Error'), ('El beneficiario %s no esta en la base de proveedores debe estar registrado') % (employee.complete_name))
                            partner = partner_obj.browse(cr, uid, partner_ids[0])
                            if partner.bank_ids:
                                bank_id = partner.bank_ids[0].id
                                aux_name = ustr('PAGO DECIMO CUARTO ' + employee.complete_name)
                                aux_ref = '40101'
                                concepto_ids = concepto_obj.search(cr, uid, [('code','=','40101')])
                                if concepto_ids:
                                    concepto_id = concepto_ids[0]
                                if decimo.recibir<0:
                                    raise osv.except_osv(('Error'), ('No se puede pagar decimo negativo, verificar rol de %s ') % (partner.name))
                                line_obj.create(cr, uid, {
                                    'spi_id':this.id,
                                    'partner_id':partner.id,
                                    'amount':decimo.recibir,
                                    'name':aux_name,
                                    #'ref':aux_ref,
                                    'concepto_id':concepto_id,
                                    'bank_id':bank_id,
                                })
                            else:
                                raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (employee.complete_name))
            elif this.tipo=='varios':
                if this.varios_id:
                    for line in this.varios_id.line_ids:
                        partner = line.name
                        if not partner.bank_ids:
                            raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (partner.name))
                        bank_id = partner.bank_ids[0].id
                        aux_name = ustr('PAGO: ' + this.varios_id.name)
                        aux_ref = '40101'
                        concepto_ids = concepto_obj.search(cr, uid, [('code','=','40101')])
                        if concepto_ids:
                            concepto_id = concepto_ids[0]
                        line_obj.create(cr, uid, {
                            'spi_id':this.id,
                            'partner_id':partner.id,
                            'amount':line.valor,
                            'name':aux_name,
                            'ref':aux_ref,
                            'concepto_id':concepto_id,
                            'bank_id':bank_id,
                        })
        return True
        

spi_voucher()
