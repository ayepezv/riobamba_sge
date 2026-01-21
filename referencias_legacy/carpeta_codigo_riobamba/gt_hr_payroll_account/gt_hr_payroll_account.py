# -*- coding: utf-8 -*-
##############################################################################

# Mario Chogllo
# mariofchogllo@gmail.com
##############################################################################
import base64
from osv import fields, osv
import time
from tools import ustr
from gt_tool import XLSWriter
import xlrd
import decimal_precision as dp

class wizardPagaCxp(osv.TransientModel):
    _name = 'wizard.paga.cxp'
    _columns = dict(
        move_id = fields.many2one('account.move','Comprobante'),
        opc = fields.selection([('ComprobanteE','Comprobante Existente'),('ComprobanteN','Comprobante Nuevo')],'Opcion'),
    )
wizardPagaCxp()

class pagarIessDetalle(osv.TransientModel):
    _name = 'pagar.iess.detalle'
    _columns = dict(
        move_line_id = fields.many2one('account.move.line','Movimiento'),
        move_id = fields.many2one('account.move','Comprobante Contable'),
        beneficiario = fields.many2one('res.partner','Beneficiario'),
        valor = fields.float('Monto'),
        l_id = fields.many2one('pagar.iess.line','CxP'),
    )
pagarIessDetalle()

class pagarIessLine(osv.TransientModel):
    _name = 'pagar.iess.line'
    _order = 'code asc'
    _columns = dict(
        account_id = fields.many2one('account.account','Cuenta'),
        budget_id = fields.many2one('budget.item','Partida'),
        code = fields.char('Code',size=64),
        certificate_line_id = fields.many2one('budget.certificate.line','Certificado linea'),
        monto = fields.float('Monto'),
        saldo = fields.float('Saldo por pagar'),
        monto_pago = fields.float('Monto a pagar'),
        pagar = fields.boolean('Pagar'),
        i_id = fields.many2one('pagar.iess','Pagar'),
        desc = fields.char('Descripcion',size=64),
        line_cxp_ids = fields.one2many('pagar.iess.detalle','l_id','Detalle'),
        move_id = fields.many2one('account.move','Comprobante Contable'),
        move_line_id = fields.many2one('account.move.line','Cuenta por pagar'),
    )

    def agregaComprobante(self, cr, uid, ids, context=None):
        print "agrega"
        return True

pagarIessLine()
class pagarIess(osv.TransientModel):
    _name = 'pagar.iess'
    _columns = dict(
        cp_id = fields.many2one('budget.certificate','Documento Prespuestario'),
        bank_id = fields.many2one('account.journal','Banco'),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        date = fields.date('Fecha Corte'),
        date_start = fields.date('Fecha Inicio'),
        line_ids = fields.one2many('pagar.iess.line','i_id','Detalle'),
        opc = fields.selection([('ComprobanteExistente','Comprobante Existente'),('NuevoComprobante','Nuevo Comprobante')],'Opcion'),
        move_id = fields.many2one('account.move','Comprobante Contable'),
    )

    def default_get(self, cr, uid, fields, context=None):
        company_obj = self.pool.get('res.company')
        if context is None:
            context = {}
        res = {}
        compania = company_obj.browse(cr, uid, 1)
        partner_id = compania.iess_id.id
        res.update({'opc':'NuevoComprobante','partner_id':partner_id})
        return res

    def print_iess(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        pagar = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [pagar.id], 'model': 'pagar.iess'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pagar.iess',
            'model': 'pagar.iess',
            'datas': datas,
            'nodestroy': True,                        
            }            

    def pagarIess(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        cert_line_obj = self.pool.get('budget.certificate.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            if not this.bank_id:
                raise osv.except_osv('Error de usuario', 'Debe seleccionar el banco')
            if this.opc=='ComprobanteExistente' and this.move_id:
                move_id = this.move_id.id
            else:
                journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
                if not journal_ids:
                    raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
                period_ids = period_obj.find(cr, uid, this.date)
                if not period_ids:
                    raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
                aux_name = "PAGO " + this.partner_id.name
                if this.cp_id:
                    move_id = move_obj.create(cr, uid, {
                        'ref': aux_name,
                        'narration':aux_name,
                        'journal_id': journal_ids[0],
                        'date': this.date,
                        'period_id':period_ids[0],
                        'state':'draft',
                        'afectacion':True,
                        'partner_id':this.partner_id.id,
                        'type':'Nomina',
                        'no_cp':False,
                        'validar_cp':True,
                        'certificate_id':this.cp_id.id,
                    })
                else:
                    move_id = move_obj.create(cr, uid, {
                        'ref': aux_name,
                        'narration':aux_name,
                        'journal_id': journal_ids[0],
                        'date': this.date,
                        'period_id':period_ids[0],
                        'state':'draft',
                        'afectacion':True,
                        'partner_id':this.partner_id.id,
                        'type':'Nomina',
                        'no_cp':True,
                        'validar_cp':True,
                    })
            aux_banco = 0
            lineas_pagar  = 0
            for line in this.line_ids:
                if line.pagar and line.monto_pago>0 and line.monto_pago<=line.monto:
                    lineas_pagar += 1
                    aux_banco += line.monto_pago
                    if line.account_id.code[0:3]=='224':
                        if not this.cp_id:
                            raise osv.except_osv('Error de usuario', 'Es pago de anio anterior debe seleccionar el compromiso presupuestario')
                    if this.cp_id:
                        move_line_id = move_line_obj.create(cr, uid, {
                            'partner_id':this.partner_id.id,
                            'move_id':move_id,
                            'move_line_cxp':line.move_line_id.id,
                            'debit':line.monto_pago,
                            'budget_paid':True,
                            'budget_accrued':True,
                            'account_id':line.account_id.id,
                            'budget_id_cert':this.cp_id.line_ids[0].id,
                        })
                    else:
                        move_line_id = move_line_obj.create(cr, uid, {
                            'partner_id':this.partner_id.id,
                            'move_id':move_id,
                            'move_line_cxp':line.move_line_id.id,
                            'debit':line.monto_pago,
                            'budget_paid':True,
                            'account_id':line.account_id.id,
                            'budget_id_cert':line.certificate_line_id.id,
                        })
            if lineas_pagar==0:
                raise osv.except_osv('Error de usuario', 'No ha marcado lineas a pagar')
            move_line_id = move_line_obj.create(cr, uid, {
                'partner_id':this.partner_id.id,
                'move_id':move_id,
                'credit':aux_banco,
                'account_id':this.bank_id.default_debit_account_id.id,
            })
        return {'type':'ir.actions.act_window_close' }

    def loadPagarIess(self, cr, uid, ids, context=None):
        iess_line_obj = self.pool.get('pagar.iess.line')
        move_line_obj = self.pool.get('account.move.line')
        company_obj = self.pool.get('res.company')
        compania = company_obj.browse(cr, uid, 1)
        partner_id = compania.iess_id.id
        aux_date = '2017-01-01'
        for this in self.browse(cr, uid, ids):
            lineas_antes = iess_line_obj.search(cr, uid, [('i_id','=',this.id)])
            if lineas_antes:
                iess_line_obj.unlink(cr, uid, lineas_antes)
            move_line_ids = move_line_obj.search(cr, uid, [('partner_id','=',partner_id),('date','>=',aux_date),
                                                            ('date','<=',this.date),('move_id.state','=','posted'),('saldo','>',0)])
            if move_line_ids:
                for move_line_id in move_line_ids:
                    move_line = move_line_obj.browse(cr, uid, move_line_id)
                    pagos_ids = move_line_obj.search(cr, uid, [('move_line_cxp','=',move_line_id),('move_id.state','=','posted')])
                    pagado = 0
                    if pagos_ids:
                        for pago_id in pagos_ids:
                            pago = move_line_obj.browse(cr, uid, pago_id)
                            pagado += pago.debit
                    if (move_line.account_id.code[0:3] in ('213','224') and (move_line.credit>pagado)):
                        iess_line_obj.create(cr, uid, {
                            'i_id':this.id,
                            'budget_id':move_line.budget_id.id,
                            'account_id':move_line.account_id.id,
                            'monto':move_line.credit,
                            'pagar':True,
                            'saldo':(move_line.credit-pagado),
                            'move_id':move_line.move_id.id,
                            'move_line_id':move_line.id,
                            'monto_pago':move_line.saldo,
                            'certificate_line_id':move_line.budget_id_cert.id,
                        })
        return True

    def loadPagarIess2(self, cr, uid, ids, context=None):
        tercero_obj = self.pool.get('hr.pago.terceros')
        move_obj = self.pool.get('account.move')
        iess_line_obj = self.pool.get('pagar.iess.line')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        company_obj = self.pool.get('res.company')
        item_obj = self.pool.get('budget.item')
        compania = company_obj.browse(cr, uid, 1)
        partner_id = compania.iess_id.id
        for this in self.browse(cr, uid, ids):
            lineas_antes = iess_line_obj.search(cr, uid, [('i_id','=',this.id)])
            if lineas_antes:
                iess_line_obj.unlink(cr, uid, lineas_antes)
            move_line_ids1 = move_line_obj.search(cr, uid, [('partner_id','=',partner_id),('date','>=',this.date_start),
                                                           ('date','<=',this.date),('move_id.state','=','posted')])
            if move_line_ids1:
                if len(move_line_ids1)>1:
                    tuple_ids = tuple(move_line_ids1)
                    operador = 'in'
                else:
                    tuple_ids = (move_line_ids1[0])
                    operador = '='
                sql = '''select account_id from account_move_line where id %s %s group by account_id''' % (operador,tuple_ids)
                cr.execute(sql)
                res = cr.fetchall()
                if res:
                    debe_mayor = haber_mayor = 0
                    for account_id in res:
                        partida_dic = {}
                        account = account_obj.browse(cr, uid, account_id[0])
                        if account.code[0:3] in ('213','224'):
                            debe = haber = 0
                            move_line_ids = move_line_obj.search(cr, uid, [('partner_id','=',partner_id),('account_id','=',account_id[0]),
                                                                           ('date','>=',this.date_start),
                                                                           ('move_id.state','=','posted'),('date','<=',this.date)])
                            for move_line_id in move_line_ids:
                                move_line = move_line_obj.browse(cr, uid, move_line_id)
                                if not move_line.budget_id.id in partida_dic:
                                    partida_dic[move_line.budget_id.id] = []
                                    partida_dic[move_line.budget_id.id].append(move_line.debit)
                                    partida_dic[move_line.budget_id.id].append(move_line.credit)
                                else:
                                    partida_dic[move_line.budget_id.id][0] += move_line.debit
                                    partida_dic[move_line.budget_id.id][1] += move_line.credit
                                debe += move_line.debit
                                haber += move_line.credit
                            if haber>debe:
                                for partida in partida_dic:
                                    aux_monto = 0
                                    if partida_dic[partida][1]>partida_dic[partida][0]:
                                        aux_monto = partida_dic[partida][1]-partida_dic[partida][0]
                                        partida_ = item_obj.browse(cr, uid, partida)
                                        iess_line_obj.create(cr, uid, {
                                            'i_id':this.id,
                                            'budget_id':partida,
                                            'account_id':account_id,
                                            'monto':aux_monto,
                                            'code':partida_.code,
                                        })
            else:
                raise osv.except_osv('Aviso', 'No hay movimientos del IESS en el periodo seleccionado')
        return True
        

    def loadPagarIess1(self, cr, uid, ids, context=None):
        tercero_obj = self.pool.get('hr.pago.terceros')
        move_obj = self.pool.get('account.move')
        iess_line_obj = self.pool.get('pagar.iess.line')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        company_obj = self.pool.get('res.company')
        item_obj = self.pool.get('budget.item')
        compania = company_obj.browse(cr, uid, 1)
        partner_id = compania.iess_id.id
        for this in self.browse(cr, uid, ids):
            lineas_antes = iess_line_obj.search(cr, uid, [('i_id','=',this.id)])
            if lineas_antes:
                iess_line_obj.unlink(cr, uid, lineas_antes)
            move_ids = move_obj.search(cr, uid, [('partner_id','=',partner_id),('date','>=',this.date_start),('date','<=',this.date),('state','=','posted')])
            if len(move_ids)>1:
                tuple_ids = tuple(move_ids)
                operador = 'in'
            else:
                tuple_ids = (move_ids[0])
                operador = '='
            if move_ids:
                sql = '''select account_id from account_move_line where move_id %s %s group by account_id''' % (operador,tuple_ids)
                cr.execute(sql)
                res = cr.fetchall()
                if res:
                    debe_mayor = haber_mayor = 0
                    for account_id in res:
                        partida_dic = {}
                        account = account_obj.browse(cr, uid, account_id[0])
                        if account.code[0:3]=='213':
                            debe = haber = 0
                            move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id[0]),('move_id','in',move_ids),('date','>=',this.date_start),
                                                                           ('move_id.state','=','posted'),('date','<=',this.date)])
                            for move_line_id in move_line_ids:
                                move_line = move_line_obj.browse(cr, uid, move_line_id)
                                if not move_line.budget_id.id in partida_dic:
                                    partida_dic[move_line.budget_id.id] = []
                                    partida_dic[move_line.budget_id.id].append(move_line.debit)
                                    partida_dic[move_line.budget_id.id].append(move_line.credit)
                                else:
                                    partida_dic[move_line.budget_id.id][0] += move_line.debit
                                    partida_dic[move_line.budget_id.id][1] += move_line.credit
                                debe += move_line.debit
                                haber += move_line.credit
                            if haber>debe:
                                for partida in partida_dic:
                                    aux_monto = 0
                                    if partida_dic[partida][1]>partida_dic[partida][0]:
                                        aux_monto = partida_dic[partida][1]-partida_dic[partida][0]
                                        iess_line_obj.create(cr, uid, {
                                            'i_id':this.id,
                                            'budget_id':partida,
                                            'account_id':account_id,
                                            'monto':aux_monto,
                                        })
        return True

pagarIess()
##reporte de descuentos
class rolDescuentosLine(osv.TransientModel):
    _name = 'rol.descuentos.line'
    _order = 'name'
    _columns = dict(
        d_id = fields.many2one('rol.descuentos','Reporte'),
        name = fields.char('Funcionario',size=256),
        ingresos = fields.float('Ingresos'),
        subrogacion = fields.float('Aportables Subrogacion'),
        total_ingresos = fields.float('Total Ingresos'),
        iess = fields.float('Iess'),
        total = fields.float('Total'),
        employee_id = fields.many2one('hr.employee','Funcionario'),
        monto = fields.float('Monto', digits_compute=dp.get_precision('Account')),
    )
rolDescuentosLine()

class pagoJudicial(osv.TransientModel):
    _name = 'pago.judicial'
    _columns = dict(
        period_id = fields.many2one('hr.work.period.line','Periodo'),
        period_id2 = fields.many2one('account.period','Periodo'),
    )

    def generarPagoJudicial(self, cr, uid, ids, context=None):
        pago_obj = self.pool.get('hr.varios')
        pago_line_obj = self.pool.get('hr.varios.line')
        contract_obj = self.pool.get('hr.contract')
        for this in self.browse(cr, uid, ids):
            aux_desc = 'PAGO RETENCIONES JUDICIALES: ' + this.period_id2.name
            pago_id = pago_obj.create(cr, uid, {
                'name':aux_desc,
                'period_id':this.period_id2.id,
            })
            pago_id_2 = pago_obj.create(cr, uid, {
                'name':aux_desc + ' - SUPA',
                'period_id':this.period_id2.id,
            })
            contract_ids = contract_obj.search(cr, uid, [('activo','=',True)])
            k = l = 0
            if contract_ids:
                for contract_id in contract_ids:
                    contrato = contract_obj.browse(cr, uid, contract_id)
                    if contrato.employee_id.judicial_ids and contrato.subtype_id.name not in ('JUBILADO'):
                        aux_monto = 0
                        for judicial in contrato.employee_id.judicial_ids:
                            aux_monto += judicial.monto
                            if judicial.is_supa:
                                if judicial.monto>0:
                                    line_id = pago_line_obj.create(cr, uid, {
                                        'name':judicial.partner_id.id,
                                        'varios_id':pago_id_2,
                                        'monto':judicial.monto,
                                        'valor':judicial.monto,
                                        'descontado_id':contrato.employee_id.id,
                                    })
                                    l += 1 
                            else:
                                if judicial.monto>0:
                                    line_id = pago_line_obj.create(cr, uid, {
                                        'name':judicial.partner_id.id,
                                        'varios_id':pago_id,
                                        'monto':judicial.monto,
                                        'valor':judicial.monto,
                                        'descontado_id':contrato.employee_id.id,
                                    })
                                    k += 1
            if l==0:
                pago_obj.unlink(cr, uid, [pago_id_2])
            if k==0:
                pago_obj.unlink(cr, uid, [pago_id])
        return {'type':'ir.actions.act_window_close' }
    
pagoJudicial()

class rolDescuentos(osv.TransientModel):
    _name = 'rol.descuentos'

    def print_rol_descuento(self, cr, uid, ids, context):
        obj = self.pool.get('rol.descuentos')
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        obj.load_rol_descuento(cr, uid, ids, context)
        datas = {'ids': [report.id], 'model': 'report.rol.descuentos'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'descuento_rol',
            'model': 'rol.descuentos',
            'datas': datas,
            'nodestroy': True,                        
        }    

    def print_rol_descuento_detalle(self, cr, uid, ids, context):
        obj = self.pool.get('rol.descuentos')
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        obj.load_rol_descuento(cr, uid, ids, context)
        datas = {'ids': [report.id], 'model': 'report.rol.descuentos'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'descuento_rold',
            'model': 'rol.descuentos',
            'datas': datas,
            'nodestroy': True,                        
        }    

    def load_rol_descuento(self, cr, uid, ids, context=None):
        payslip_obj = self.pool.get('hr.payslip')
        line_rol_obj = self.pool.get('hr.payslip.line')
        line_obj = self.pool.get('rol.descuentos.line')
        empleados_ids = []
        for this in self.browse(cr, uid, ids):
            lines_antes = line_obj.search(cr, uid, [('d_id','=',this.id)])
            if lines_antes:
                line_obj.unlink(cr, uid, lines_antes)
            if this.rol_id:
                line_ids = line_rol_obj.search(cr, uid, [('salary_rule_id','=',this.rubro_id.id),('run_id','=',this.rol_id.id)])
            else:
                line_ids = line_rol_obj.search(cr, uid, [('period_id','=',this.period_id.id),('salary_rule_id','=',this.rubro_id.id)])
            if line_ids:
                for line_id in line_ids:
                    linea = line_rol_obj.browse(cr, uid, line_id)
                    empleados_ids.append(linea.employee_id.id)
                    aux_iess = 0
                    iess_line_ids = line_rol_obj.search(cr, uid, [('slip_id','=',linea.slip_id.id),('code','=','IESS_PERSONAL')])
                    if iess_line_ids:
                        linea_iess = line_rol_obj.browse(cr, uid, iess_line_ids[0])
                        aux_iess = linea_iess.total
                    line_obj.create(cr, uid, {
                        'd_id':this.id,
                        'ingresos':linea.slip_id.allowance+linea.slip_id.basic,
                        'subrogacion':linea.slip_id.aportable,
                        'total_ingresos':linea.slip_id.allowance+linea.slip_id.aportable+linea.slip_id.basic,
                        'iess':aux_iess,
                        'total':linea.slip_id.net,
                        'employee_id':linea.employee_id.id,
                        'name':linea.employee_id.complete_name,
                        'monto':linea.total,
                    })
            if this.rol_id and this.is_renta:
                roles_extra_ids = payslip_obj.search(cr, uid, [('payslip_run_id','=',this.rol_id.id),('employee_id','not in',empleados_ids)])
                if roles_extra_ids:
                    for rol_extra_id in roles_extra_ids:
                        rol_extra = payslip_obj.browse(cr, uid, rol_extra_id)
                        aux_iess = 0
                        iess_line_ids = line_rol_obj.search(cr, uid, [('slip_id','=',rol_extra_id),('code','=','IESS_PERSONAL')])
                        if iess_line_ids:
                            linea_iess = line_rol_obj.browse(cr, uid, iess_line_ids[0])
                            aux_iess = linea_iess.total
                        line_obj.create(cr, uid, {
                            'd_id':this.id,
                            'ingresos':rol_extra.allowance+rol_extra.basic,
                            'subrogacion':rol_extra.aportable,
                            'total_ingresos':rol_extra.allowance+rol_extra.aportable+rol_extra.basic,
                            'iess':aux_iess,
                            'total':rol_extra.net,
                            'employee_id':rol_extra.employee_id.id,
                            'name':rol_extra.employee_id.complete_name,
                            'monto':0,
                        })  
        return True

    def exportaExcelRpDesc(self, cr, uid, ids, name, context={}):
        total = 0
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            cabecera_all = ['REPORTE DESCUENTOS',this.rubro_id.name]
            writer.append(cabecera_all)
            cabecera_all = ['PERIODO',this.period_id.name]
            writer.append(cabecera_all)
            total_certificado = total_comprometido = total_devengado = total_pagado = 0
            writer.append(['Funcionario','Monto'])
            for line in this.line_ids:
                writer.append([line.name,line.monto])
                total += line.monto
        final = ['TOTALES',total]
        writer.append(final)
        writer.save("DescuentoRubro.xls")
        out = open("DescuentoRubro.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'DescuentoRubro.xls'})
        return True

    _columns = dict(
        is_renta = fields.boolean('Reporte Renta'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
        line_ids = fields.one2many('rol.descuentos.line','d_id','Detalle'),
        period_id = fields.many2one('hr.work.period.line','Periodo'),
        rol_id = fields.many2one('hr.payslip.run','Rol'),
        rubro_id = fields.many2one('hr.salary.rule','Rubro'),
    )
rolDescuentos()
#pago de rol
class pagoRolLine(osv.Model):
    _name = 'hr.pago.rol.line'
    _columns = dict(
        to_pay = fields.boolean('Pagar?'),
        move_id = fields.many2one('account.move','Comprobante Contable'),
        move_line_id = fields.many2one('account.move.line','Ref. Asiento'),
        p_id = fields.many2one('hr.pago.rol','Rol'),
        cxp_id = fields.many2one('account.account'),
        cert_line = fields.many2one('budget.certificate.line','Partida'),
        partida_id = fields.many2one('budget.item','Partida'),
        monto = fields.float('Valor'),
        monto_pay = fields.float('Monto A Pagar'),
    )
    _defaults = dict(
        to_pay = True,
    )
pagoRolLine()
class pagoRol(osv.Model):
    _name = 'hr.pago.rol'
    _columns = dict(
        line_ids = fields.one2many('hr.pago.rol.line','p_id','Lineas'),
        rol_id = fields.many2one('hr.payslip.run','Rol'),
        name = fields.related('rol_id', 'name', type='char',size=64,string='Descripcion', store=True),
        contract_type_id = fields.related('rol_id', 'contract_type_id', type='many2one', relation='hr.contract.type.type', string='Contrato', store=True),
        period_id = fields.related('rol_id', 'period_id', type='many2one', relation='hr.work.period.line', string='Periodo', store=True),
        bank_id = fields.many2one('account.journal','Banco'),
        move_id = fields.many2one('account.move','Asiento Contable'),
        state = fields.selection([('Borrador','Borrador'),('Pagado','Pagado')],'Estado'),
    )

    def finalizar_cxprol(self,cr, uid,ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                if line.to_pay:
                    move_line_obj.write(cr, uid, line.move_line_id.id,{'monto_pagado':line.monto_pay})
        self.write(cr, uid, ids, {'state':'Pagado'})
        return True

    def load_cxprol(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        line_obj = self.pool.get('hr.pago.rol.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        state_aux = 'draft'
        company_aux = 1
        currency_aux = 2
        for this in self.browse(cr, uid, ids):
            line_antes = line_obj.search(cr, uid, [('p_id','=',this.id)])
            if line_antes:
                line_obj.unlink(cr, uid, line_antes)
            #sacar diario de egreso
            journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
            period_ids = period_obj.find(cr, uid, this.rol_id.date_end)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            lines_ant = line_obj.search(cr, uid, [('p_id','=',this.id)])
            if lines_ant:
                line_obj.unlink(cr, uid, lines_ant)
            move_rol = this.rol_id.move_id
            aux_name = "PAGO ROL " + this.rol_id.name + 'DE: ' + this.rol_id.period_id.name
            aux_monto = 0
            date_aux = this.rol_id.date_end
            if not this.rol_id.move_id:
                raise osv.except_osv('Error de usuario','No a generado el registro contable(devengado) del rol.')
            for line in this.rol_id.move_id.line_id:
#                if line.credit>0 and line.budget_id:
                if line.budget_id and line.account_id.code[0:1]=='2':
                    #cargar cuentas por pagar
                    if line.name in ('neto','ingreso','Neto','Ingreso') or line.ref in ('neto','ingreso','Neto','Ingreso'):
                        #mejora buscar las lineas pagadas de la linea y solo colocar el saldo pendiente
                        linea_pagada_ids = line_obj.search(cr, uid, [('move_line_id','=',line.id)])
                        if linea_pagada_ids:
                            aux_pagado = 0
                            for linea_pagada_id in linea_pagada_ids:
                                linea_pagada = line_obj.browse(cr, uid, linea_pagada_id)
                                aux_pagado += linea_pagada.monto_pay
                            aux_saldo = line.credit - aux_pagado
                        else:
                            aux_saldo = line.credit
                        line_obj.create(cr, uid, {
                            'to_pay':True,
                            'p_id':this.id,
                            'cxp_id':line.account_id.id,
                            'partida_id':line.budget_id.id,
                            'monto':line.credit,
                            'monto_pay':line.credit,
                            'move_id':this.rol_id.move_id.id,
                            'move_line_id':line.id,
#                            'monto_pay':aux_saldo,
                            'cert_line':line.budget_id_cert.id,
                        })
        return True

    def paid_cxprol(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        line_obj = self.pool.get('hr.pago.rol.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        state_aux = 'draft'
        company_aux = 1
        currency_aux = 2
        for this in self.browse(cr, uid, ids):
            #sacar diario de egreso
            journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
            period_ids = period_obj.find(cr, uid, this.rol_id.date_end)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            move_rol = this.rol_id.move_id
            aux_name = "PAGO ROL " + this.rol_id.name + 'DE: ' + this.rol_id.period_id.name
            aux_monto = 0
            date_aux = this.rol_id.date_end
            if this.move_id:
                if this.move_id.state=='draft' and this.move_id.name=='/':
                    move_obj.unlink(cr, uid, [this.move_id.id],aux=1)
                    move_id = move_obj.create(cr, uid, {
                        'ref': aux_name,
                        'narration':aux_name,
                        'journal_id': journal_ids[0],
                        'date': this.rol_id.date_end,
                        'period_id':period_ids[0],
                        'state':'draft',
                        'certificate_id':this.rol_id.certificate_id.id,
                        'afectacion':True,
                        'partner_id':1,
                        'type':'Nomina',
                        'no_cp':True,
                        'validar_cp':True,
                    })
                    move = move_obj.browse(cr, uid, move_id)
                    date_aux = move.date
                    for line in this.line_ids:
                        if line.monto_pay!=0: #>
                            aux_monto += line.monto_pay
                            b_id = line.cert_line.budget_id.id
                            p_id = line.cert_line.budget_post.id
                            #SQL
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,line.cxp_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.cert_line.id,b_id,p_id,'Pago',False,True))
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_accrued) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)''',(move_id,this.bank_id.default_credit_account_id.id,aux_monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Banco',False,False))                    
                    self.write(cr, uid, this.id,{
                        'move_id':move_id,
                    })
                else:
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                    move_id = this.move_id.id
                    move = this.move_id
                    for line in this.line_ids:
                        if line.monto_pay!=0: #>
                            aux_monto += line.monto_pay
                            b_id = line.cert_line.budget_id.id
                            p_id = line.cert_line.budget_post.id
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,line.cxp_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.cert_line.id,b_id,p_id,'Pago',False,True))
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_accrued) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)''',(move_id,this.bank_id.default_credit_account_id.id,aux_monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Banco',False,False))                    
            else:
                move_id = move_obj.create(cr, uid, {
                    'ref': aux_name,
                    'narration':aux_name,
                    'journal_id': journal_ids[0],
                    'date': this.rol_id.date_end,
                    'period_id':period_ids[0],
                    'state':'draft',
                    'afectacion':True,
                    'partner_id':1,
                    'no_cp':True,
                    'certificate_id':this.rol_id.certificate_id.id,
                    'type':'Nomina',
                    'validar_cp':True,
                    })
                move = move_obj.browse(cr, uid, move_id)
                for line in this.line_ids:
                    if line.to_pay:
                        if line.monto_pay!=0: #>
                            aux_monto += line.monto_pay
                            b_id = line.cert_line.budget_id.id
                            p_id = line.cert_line.budget_post.id
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,line.cxp_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.cert_line.id,b_id,p_id,'Pago',False,True))
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_accrued) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)''',(move_id,this.bank_id.default_credit_account_id.id,aux_monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Banco',False,False))                    
                self.write(cr, uid, this.id,{
                    'move_id':move_id,
                })

    _defaults = dict(
        state = 'Borrador',
    )
pagoRol()

#pagos a terceros
class beneficiarioTercero(osv.Model):
    _name = 'beneficiario.tercero'

    def _get_estado(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 'Pendiente'
        for this in self.browse(cr, uid, ids):
            if this.move_id.state=='posted':
                aux = 'Pagado'
            res[this.id] = aux
        return res

    _columns = dict(
        t_id = fields.many2one('hr.pago.terceros.line','Detalle'),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        monto = fields.float('Monto'),
        move_id = fields.many2one('account.move','Comprobante'),
        state = fields.function(_get_estado,string='ESTADO',type="char",size=10,store=True),
    )
beneficiarioTercero()
class pagoTercerosLine(osv.Model):
    _name = 'hr.pago.terceros.line'

    _columns = dict(
        ref_exp = fields.integer('Referencia Exporta'),
        move_line_id = fields.many2one('account.move.line','Linea Asiento'),
        to_pay = fields.boolean('Pagar'),
        line_ids = fields.one2many('beneficiario.tercero','t_id','Beneficiarios'),
        name=fields.char('Ref.',size=32),
        ref = fields.char('Ref/Comprobante',size=32),
        date = fields.date('Fecha'),
        t_id = fields.many2one('hr.pago.terceros','Pago'),
        account_id = fields.many2one('account.account','Cuenta por pagar'),
        budget_id = fields.many2one('budget.item','Partida',required=True),
        monto_inicial = fields.float('Cuenta por pagar'),
        monto = fields.float('Monto Pago'),
        program_id = fields.many2one('project.program','Programa'),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        move_line_cxp = fields.many2one('account.move.line','Linea Asiento Paga'),
    )

    def _check_total_tercero(self, cr, uid, ids):
        band = True
        aux = 0
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                aux += line.monto
        if aux>this.monto:
            band = False
        return band

    _constraints = [
        (_check_total_tercero,
         ustr('El total a pagar debe ser igual al valor descontado.'),
         [ustr('Fondos terceros'), 'Total']),
    ]

    _defaults = dict(
        to_pay = True,
    )

pagoTercerosLine()

class terceroMove(osv.Model):
    _name = 'tercero.move'
    _columns = dict(
        t_id = fields.many2one('hr.pago.terceros','Pago'),
        move_id = fields.many2one('account.move','Comprobante'),
        monto = fields.float('Valor'),
    )
terceroMove()

class pagoTerceros(osv.Model):
    _name = 'hr.pago.terceros'
    _columns = dict(
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
 #       name = fields.many2one('hr.salary.rule','Rubro',required=True),
        is_iess = fields.boolean('Es IESS'),
        new_comp = fields.boolean('Otro Comprobante'),
        varios_benef = fields.boolean('Varios Beneficiarios'),
        name = fields.char('Desc',size=256),
        name_ids = fields.many2many('hr.salary.rule','t_r_id_rel','t_id','r_id','Rubros'),
        partner_id = fields.many2one('res.partner','Proveedor',required=True),
        period_id = fields.many2one('hr.work.period.line','Periodo',required=True),
        period_id2 = fields.many2one('hr.work.period.line','Periodo Extra'),
        date = fields.date('Fecha Pago',required=True),
        bank_id = fields.many2one('account.journal','Banco'),
        line_ids = fields.one2many('hr.pago.terceros.line','t_id','Detalle Pago'),
        move_id = fields.many2one('account.move','Asiento Pago'),
        pago_ids = fields.one2many('tercero.move','t_id','Detalle Pagos'),
        certificate_id = fields.many2one('budget.certificate'),
        total_pago = fields.float('TOTAL PAGO'),
    )

    def imp_cxp3(self, cr, uid, ids, context=None):    
        line_obj = self.pool.get('hr.pago.terceros.line')
        for this in self.browse(cr, uid, ids):
            lines_antes = line_obj.search(cr, uid, [('t_id','=',this.id)])
            if lines_antes:
                line_obj.write(cr,uid, lines_antes,{'to_pay':False})
            arch = this.datas
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            aux_total = 0
            for r in range(sh.nrows)[1:]: 
                aux_ref = ''
                if sh.cell(r,0).value:
                    aux_ref = int(sh.cell(r,0).value)
                aux_monto_pago = sh.cell(r,6).value
                aux_paga = ustr(sh.cell(r,7).value)
                if aux_ref:
                    if aux_paga in ('SI','si','Si','1'):
                        line_ids = line_obj.search(cr, uid, [('ref_exp','=',aux_ref),('t_id','=',this.id)])
                        if line_ids:
                            aux_total += aux_monto_pago
                            line_obj.write(cr,uid, line_ids[0],{'to_pay':True,'monto':aux_monto_pago})
            self.write(cr, uid, this.id,{'total_pago':aux_total})            
        return True

    def exp_cxp3(self, cr, uid, ids, context=None):    
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            cabecera_all = ['Ref. Interna(NO MODIFICAR)','Ref/Comprobante','Fecha','Cuenta por pagar','Partida','Monto Cuenta por pagar','Monto Pago','Pagar']
            writer.append(cabecera_all)
            total = total_1 = 0
            for line in this.line_ids:
                total += line.monto_inicial
                total_1 += line.monto
                aux_cta = line.account_id.code + ' - ' + line.account_id.name
                linea_pago = [line.ref_exp,line.ref,line.date,aux_cta,line.budget_id.code,line.monto_inicial,line.monto,line.to_pay]
                writer.append(linea_pago)
            writer.append(['','','','','TOTAL',total,total_1])
        writer.save("PagoTercero.xls")
        out = open("PagoTercero.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'PagoTercero.xls'})
        return True

    def onchange_rubro_3(self, cr, uid, ids, rubro, context={}):
        rule_obj = self.pool.get('hr.salary.rule')
        rule = rule_obj.browse(cr, uid, rubro)
        vals = {}
        return {'value':{'partner_id':rule.partner_id.id}}

    def computeTotalCxp3(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            aux_pago = 0
            for line in this.line_ids:
                if line.to_pay:
                    aux_pago += line.monto
            self.write(cr, uid, this.id,{
                'total_pago':aux_pago,
            })
        return True

    def marca_cxp3(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.pago.terceros.line')
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                if line.to_pay:
                    line_obj.write(cr, uid, line.id,{
                        'to_pay':False,
                    })
                else:
                    line_obj.write(cr, uid, line.id,{
                        'to_pay':True,
                    })
        return True

    def paid_cxp3(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.varios_benef:
                self.paid_cxp3Var(cr, uid, ids, context)
            else:
                self.paid_cxp3Ind(cr, uid, ids, context)
        return True

    def paid_cxp3Var(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        move_line_obj = self.pool.get('account.move.line')
        cert_line_obj = self.pool.get('budget.certificate.line')
        for this in self.browse(cr, uid, ids):
            if this.certificate_id:
                if not this.certificate_id.state=='commited':
                    raise osv.except_osv('Error de usuario', 'El documento presupuestario del rol debe estar comprometido, por favor verifique')
            journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
            period_ids = period_obj.find(cr, uid, this.date)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            aux_monto = 0
            for line in this.line_ids:
                for line_benef in line.line_ids:
                    if line_benef.move_id:
                        move_line_ids = move_line_obj.search(cr, uid, [('move_id','=',line_benef.move_id.id)])
                        if move_line_ids:
                            move_line_obj.unlink(cr, uid, move_line_ids)
                        move_id = line_benef.move_id.id
                    else:
                        aux_name = "PAGO A FAVOR DE " + line_benef.partner_id.name + " POR CONCEPTO DE CUOTAS CORRESPONDIENTES A " + this.period_id.name
                        move_id = move_obj.create(cr, uid, {
                            'ref': aux_name,
                            'narration':aux_name,
                            'journal_id': journal_ids[0],
                            'date': this.period_id.date_stop,
                            'period_id':period_ids[0],
                            'state':'draft',
                            'afectacion':True,
                            'partner_id':line_benef.partner_id.id,
                            'type':'Nomina',
                            'no_cp':True,
                            'certificate_id':this.certificate_id.id,
                            'validar_cp':True,
                        })
                    cert_line_id = cert_line_obj.create(cr, uid, {
                        'project_id':this.certificate_id.project_id.id,
                        'task_id':this.certificate_id.project_id.tasks[0].id,
                        'budget_id':line.budget_id.id,
                    })
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':line.account_id.id,
                        'debit':line_benef.monto,
                        'name':'Pago',
                        'budget_id_cert':cert_line_id,
                        'budget_paid':True,
                    })
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':this.bank_id.default_credit_account_id.id,
                        'credit':line_benef.monto,
                        'name':'Banco',
                    })
        return True

    def paid_cxp3Ind(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        cert_line_obj = self.pool.get('budget.certificate.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        tercero_move_obj = self.pool.get('tercero.move')
        for this in self.browse(cr, uid, ids):
            if this.certificate_id:
                if not this.certificate_id.state=='commited':
                    raise osv.except_osv('Error de usuario', 'El documento presupuestario del rol debe estar comprometido, por favor verifique')
            #sacar diario de egreso
            journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
            period_ids = period_obj.find(cr, uid, this.date)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            aux_name = "PAGO A FAVOR DE " + this.partner_id.name + " POR CONCEPTO DE CUOTAS CORRESPONDIENTES A " + this.period_id.name + " DE LOS EMPLEADOS DEL MUNICIPIO"
            aux_monto = 0
            if this.move_id:
                if this.move_id.state =='draft' and this.move_id.name=='/':
                    move_obj.unlink(cr, uid, [this.move_id.id],aux=1)
                    move_id = move_obj.create(cr, uid, {
                        'ref': aux_name,
                        'narration':aux_name,
                        'journal_id': journal_ids[0],
                       #'date': this.period_id.date_stop,
                        'date': this.date,
                        'period_id':period_ids[0],
                        'state':'draft',
                        'afectacion':True,
                        'partner_id':this.partner_id.id,
                        'type':'Nomina',
                        'no_cp':True,
                        'certificate_id':this.certificate_id.id,
                        'validar_cp':True,
                    })
                    tercero_move_obj.create(cr, uid, {
                        't_id':this.id,
                        'move_id':move_id,
                    })
                else:
                    move_id = this.move_id.id
                    move_obj.write(cr, uid, [this.move_id.id],{
                        'state':'draft',
                    })
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                for line in this.line_ids:
                    if line.to_pay:
                        aux_monto += line.monto
                        cert_line_id = cert_line_obj.create(cr, uid, {
                            'project_id':this.certificate_id.project_id.id,
                            'task_id':this.certificate_id.project_id.tasks[0].id,
                            'budget_id':line.budget_id.id,
                        })
                        move_line_obj.create(cr, uid, {
                            'move_id':move_id,
                            'account_id':line.account_id.id,
                            'debit':line.monto,
                            'name':'Pago',
                            'budget_id_cert':cert_line_id,
                            'budget_paid':True,
                            'move_line_cxp':line.move_line_id.id,
                            'partner_id':line.partner_id.id,
                        })
                if aux_monto>0:
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':this.bank_id.default_credit_account_id.id,
                        'credit':aux_monto,
                        'name':'Banco',
                    })
                #    move_obj.post(cr, uid, [this.move_id.id],context)
                    self.write(cr, uid, this.id,{
                        'move_id':move_id,
                    })
            else:
                move_id = move_obj.create(cr, uid, {
                    'ref': aux_name,
                    'narration':aux_name,
                    'journal_id': journal_ids[0],
                    #'date': this.period_id.date_stop,
                    'date': this.date,
                    'period_id':period_ids[0],
                    'state':'draft',
                    'afectacion':True,
                    'no_cp':True,
                    'partner_id':this.partner_id.id,
                    'type':'Nomina',
                    'certificate_id':this.certificate_id.id,
                    'validar_cp':True,
                    })
                tercero_move_obj.create(cr, uid, {
                    't_id':this.id,
                    'move_id':move_id,
                })
                for line in this.line_ids:
                    if line.to_pay:
                        aux_monto += line.monto
                        cert_line_id = cert_line_obj.create(cr, uid, {
                            'project_id':this.certificate_id.project_id.id,
                            'task_id':this.certificate_id.project_id.tasks[0].id,
                            'budget_id':line.budget_id.id,
                        })
                        move_line_obj.create(cr, uid, {
                            'move_id':move_id,
                            'account_id':line.account_id.id,
                            'debit':line.monto,
                            'name':'Pago',
                            'budget_id_cert':cert_line_id,
                            'budget_paid':True,
                            'move_line_cxp':line.move_line_id.id,
                            'partner_id':line.partner_id.id,
                        })
                        if line.move_line_id:
                            move_line_obj.write(cr, uid, line.move_line_id.id,{
                                'to_pay':True,
                            })
                if aux_monto>0:
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':this.bank_id.default_credit_account_id.id,
                        'credit':aux_monto,
                        'name':'Banco',
                    })
                    self.write(cr, uid, this.id,{
                        'move_id':move_id,
                    })
            #si es otro pago del mismo
            if this.new_comp:
                move_id = move_obj.create(cr, uid, {
                    'ref': aux_name,
                    'narration':aux_name,
                    'journal_id': journal_ids[0],
                    'date': this.period_id.date_stop,
                    'period_id':period_ids[0],
                    'state':'draft',
                    'afectacion':True,
                    'no_cp':True,
                    'partner_id':this.partner_id.id,
                    'type':'Nomina',
                    'certificate_id':this.certificate_id.id,
                    'validar_cp':True,
                    })
                print "MOBVE CRADO", move_id
                tercero_move_obj.create(cr, uid, {
                    't_id':this.id,
                    'move_id':move_id,
                })
                for line in this.line_ids:
                    if line.to_pay:
                        aux_monto += line.monto
                        cert_line_id = cert_line_obj.create(cr, uid, {
                            'project_id':this.certificate_id.project_id.id,
                            'task_id':this.certificate_id.project_id.tasks[0].id,
                            'budget_id':line.budget_id.id,
                        })
                        move_line_obj.create(cr, uid, {
                            'move_id':move_id,
                            'account_id':line.account_id.id,
                            'debit':line.monto,
                            'name':'Pago',
                            'budget_id_cert':cert_line_id,
                            'budget_paid':True,
                            'move_line_cxp':line.move_line_id.id,
                            'partner_id':line.parner_id.id,
                        })
                if aux_monto>0:
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':this.bank_id.default_credit_account_id.id,
                        'credit':aux_monto,
                        'name':'Banco',
                    })
        return True

    def corrige_cxp3(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        for this in self.browse(cr, uid, ids):
            lista_moves = []
            for line in this.line_ids:
                move_line_ids = move_line_obj.search(cr, uid, [('id','not in',lista_moves),('move_id','=',this.move_id.id),('budget_id','=',False),('debit','=',line.monto)])
                if move_line_ids:
                    aux_id = move_line_ids[0]
                    lista_moves.append(aux_id)
                    sql_ = """update account_move_line set budget_id=%s where id=%s"""%(line.budget_id,aux_id)
                    cr.execute(sql_)
                    cr.commit
        return True

    def load_cxp3(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        line_obj = self.pool.get('hr.pago.terceros.line')
        run_obj = self.pool.get('hr.payslip.run')
        config_obj = self.pool.get('hr.account.configuration')
        cert_line_obj = self.pool.get('budget.certificate.line')
        move_line_obj = self.pool.get('account.move.line')
        rule_obj = self.pool.get('hr.salary.rule')
        slip_line_obj = self.pool.get('hr.payslip.line')
        line_detalle_obj = self.pool.get('run.programa.detalle')
        period_id2 = []
        for this in self.browse(cr, uid, ids):
            antes_ids = line_obj.search(cr, uid, [('t_id','=',this.id)])
            line_obj.unlink(cr, uid, antes_ids)
#            run_ids = run_obj.search(cr, uid, [('period_id','=',this.period_id.id)])
            if this.period_id2:
                period_id2.append(this.period_id.id)
                period_id2.append(this.period_id2.id)
                run_ids = run_obj.search(cr, uid, [('period_id','in',period_id2)])
            else:
                run_ids = run_obj.search(cr, uid, [('period_id','=',this.period_id.id)])
            if not run_ids:
                raise osv.except_osv(('Error de usuario !'),
                                     ("No existen roles en el periodo seleccionado %s") % (this.period_id.name))
            #mandamos un cert_id de un rol
#            run = run_obj.browse(cr, uid, run_ids[0])
            move_ids = []
            aux_exp = 0
            for rubro_id in this.name_ids:
                line_ids = line_detalle_obj.search(cr, uid, [('run_id','in',run_ids),('rubro_id','=',rubro_id.id)])
                for line_id in line_ids:
                    line = line_detalle_obj.browse(cr, uid, line_id)
                    budget_id = line.partida_id.budget_post_id
                    #busca la cuenta del rubro
                    config_ids = config_obj.search(cr, uid, [('rule_id','=',line.rubro_id.id),('budget_id','=',budget_id.id)],limit=1)
                    if config_ids:
                        aux_exp += 1
                        config = config_obj.browse(cr, uid, config_ids[0])
                        aux_ref = line.run_id.move_id.name
                        aux_date = line.run_id.move_id.date
                        if not line.run_id.move_id.id in move_ids:
                            move_ids.append(line.run_id.move_id.id)
                        move_line_ids = move_line_obj.search(cr, uid, [('move_id','=',line.run_id.move_id.id),('account_id','=',config.pay_account_id.id),
                                                                       ('credit','=',line.monto),('budget_id','=',line.partida_id.id)])
                        if move_line_ids:
                            line_obj.create(cr, uid, {
                                'ref':aux_ref,
                                'date':aux_date,
                                'move_line_id':move_line_ids[0],
                                't_id':this.id,
                                'name':'Pago',
                                'budget_id':line.partida_id.id,
                                'monto':line.monto,
                                'monto_inicial':line.monto,
                                'programa_id':line.programa_id.id,
                                'account_id':config.pay_account_id.id,
                                'ref_exp':aux_exp,
                                'partner_id':this.partner_id.id,
                                'move_line_cxp':move_line_ids[0],
                            })
                    else:
                        #import pdb
                        #pdb.set_trace()
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("El rubro %s de tercero '%s' para la partida %s no tiene parametrizado la cuenta por pagar") % (line.rubro_id.name,this.partner_id.name,budget_id.code))
            #es iess
            if not this.period_id2:
                date_start = this.period_id.date_start
                date_stop = this.period_id.date_stop
            else:
                date_start = this.period_id.date_start
                date_stop = this.period_id2.date_stop
            if this.is_iess:
                cert_line_ids = cert_line_obj.search(cr, uid, [('tipo_invoice','=','Iess'),('date_commited','>=',date_start),('date_commited','<=',date_stop)])
                if cert_line_ids:
                    move_line_ids = move_line_obj.search(cr, uid, [('budget_id_cert','in',cert_line_ids),('credit','>',0),('move_id.state','=','posted')])
                    if move_line_ids:
                        for move_line_id in move_line_ids:
                            move_line = move_line_obj.browse(cr, uid, move_line_id)
                            if move_line.account_id.code[0:5]!='21398':
                                aux_exp+=1
                                line_obj.create(cr, uid, {
                                    'move_line_id':move_line.id,
                                    'ref':move_line.move_id.name,
                                    'date':move_line.move_id.date,
                                    't_id':this.id,
                                    'name':'Pago IESS',
                                    'budget_id':move_line.budget_id.id,
                                    'monto':move_line.credit,
                                    'move_line_id':move_line.id,
                                    'monto_inicial':move_line.credit,
                                    'programa_id':move_line.budget_id.program_id.id,
                                    'account_id':move_line.account_id.id,
                                    'ref_exp':aux_exp,
                                    'partner_id':this.partner_id.id,
                                    'move_line_cxp':move_line_ids[0],
                                })
            for run_id in run_ids:
                run = run_obj.browse(cr, uid, run_id)
                if run.move_id.certificate_id:
                    self.write(cr, uid,  this.id,{
                        'certificate_id':run.move_id.certificate_id.id,
                    })
                    break
        return True
pagoTerceros()

class partnerCtaAnticipo(osv.Model):
    _inherit = 'res.partner'
    _columns = dict(
        anticipo_id = fields.many2one('account.account','Cuenta Anticipo'),
        rendir_id = fields.many2one('account.account','Cuenta reposicion o rendicion'),
    )
partnerCtaAnticipo()    


class hr_payslip_account(osv.osv):
    _name = 'hr.payslip.account'
    _description = 'Rol de pagos - Aplicacion Contable'
    _columns = {
                'payslip_id': fields.many2one('hr.payslip.run','Rol'),
                #'code': fields.char('Codigo',size=20),
                'description': fields.many2one('account.account','Descripcion'),
                #'parcial': fields.float('Parcial'),
             #   'budget_id': fields.many2one('crossovered.budget.certificate.line', 'Partida Presupuestaria'),
                'project_id': fields.many2one('account.analytic.account', 'Centro de costo'),
                'debe': fields.float('Debe'),
                'haber': fields.float('Haber'),
                }
    _defaults = {
                 'debe': 0,
                 'haber': 0,
                 }
hr_payslip_account()

class hr_payslip_budget(osv.osv):
    _name = 'hr.payslip.account.budget'
    _description = 'Rol de pagos - Aplicacion Presupuestaria'
    _columns = {
                'payslip_id': fields.many2one('hr.payslip.account','Aplicacion contable de rol'),
                #'code': fields.char('Codigo',size=20),
            #    'description': fields.many2one('crossovered.budget.lines','Partida Presupuestaria'),
                #'parcial': fields.float('Parcial'),
                'compromiso': fields.float('Comprometido'),
                'devengado': fields.float('Devengado'),
                'pago': fields.float('Pago'),
                }
    _defaults = {
                 'compromiso': 0,
                 'devengado': 0,
                 'pago': 0,
                 }
hr_payslip_budget()

class hr_payslip_account_direct(osv.osv):
    _name = 'hr.payslip.account.direct'
    _description = 'Rol de pagos - Aplicacion General'
    _columns = {
                'payslip_id': fields.many2one('hr.payslip.account','Aplicacion contable de rol'),
                #'code': fields.char('Codigo',size=20),
           #     'description': fields.many2one('crossovered.budget.lines','Partida Presupuestaria'),
                #'parcial': fields.float('Parcial'),
                'compromiso': fields.float('Comprometido'),
                'devengado': fields.float('Devengado'),
                'pago': fields.float('Pago'),
                }
    _defaults = {
                 'compromiso': 0,
                 'devengado': 0,
                 'pago': 0,
                 }
hr_payslip_account_direct()

class runProgramaDetalle(osv.Model):
    _name = 'run.programa.detalle'
    _order = 'rubro_id asc,program_code asc'
    _columns = dict(
        config_id = fields.many2one('hr.account.configuration','LInea config'),
        run_id = fields.many2one('hr.payslip.run','Rol',ondelete='cascade'),
        program_code = fields.related('programa_id','sequence',type='char',size=10,store=True),
        programa_id = fields.many2one('project.program','Programa'),
        code_programa = fields.related('programa_id', 'sequence', type='char',size=64,string='Programa', store=True),
        rubro_id = fields.many2one('hr.salary.rule','Rubro'),
        partida_id = fields.many2one('budget.item','Partida'),
        monto = fields.float('Valor'),
        partner_id = fields.many2one('res.partner','Funcionario'),
    )
runProgramaDetalle()

class hr_inherit_payslip_account(osv.osv):
    _inherit = 'hr.payslip.run'
    _columns = {
        'log_configuracion':fields.text('Log Errores'),
        'verificado':fields.boolean('Verificado Configuracion'),
        'state':fields.selection([('draft','Borrador'),('Aprobado','Aprobado'),('Autorizado','Autorizado'),
                                  ('Pagado','Pagado'),('Contabilizado','Contabilizado')],'Estado',readonly=True),
        'payslip_account_ids': fields.one2many('hr.payslip.account','payslip_id','Aplicacion Contable'),
        'journal_id': fields.many2one('account.journal', 'Diario'),
        'detalle_ids':fields.one2many('run.programa.detalle','run_id','Detalle Rubro Programa'),
        'move_id': fields.many2one('account.move', 'Asiento Contable'),
        'move_id2': fields.many2one('account.move', 'Asiento Contable Patronal'),
        'certificate_id': fields.many2one('budget.certificate','Certificacion Presupuestaria'),
        'certificate_id2': fields.many2one('budget.certificate','Certificacion Presupuestaria Patronal'),
        #'payslip_budget_ids': fields.one2many('hr.payslip.budget','payslip_id','Aplicacion Presupuestaria'),
    }

    def verificarConfiguracion(self, cr, uid, ids, context=None):
        config_obj = self.pool.get('hr.account.configuration')
        for this in self.browse(cr, uid, ids):
            aux_log = ""
            for rol in this.slip_ids:
                partida_contrato = rol.contract_id.budget_id.budget_post_id
                for rol_line in rol.line_ids:
                    if rol_line.salary_rule_id.category_id.code in ('BASIC','EGR'):
                        config_ids = config_obj.search(cr, uid, [('budget_id','=',partida_contrato.id),('rule_id','=',rol_line.salary_rule_id.id)])
                        if not config_ids:
                            aux_linea = 'No hay parametro para el rubro: '+rol_line.salary_rule_id.name + ' Partida: ' + partida_contrato.code + ' Empleado: '+rol.employee_id.complete_name+'\r\n'
                            aux_log += aux_linea
                    elif rol_line.salary_rule_id.category_id.code in ('APT','ING','COMP'):
                        band=False
                        for line_config in rol.contract_id.config_rubro_ids:
                            if line_config.rule_id.id==rol_line.salary_rule_id.id:
                                band=True
                        if not band:
                            aux_linea = 'No hay parametro para el rubro: '+rol_line.salary_rule_id.name + ' Empleado: '+rol.employee_id.complete_name+'\r\n'
                            aux_log += aux_linea
        self.write(cr, uid, ids, {'log_configuracion':aux_log})
        return True

    def _create_move_tthh(self, cr, uid, ids, context=None):
        '''EN ESTE METODO SERIA MAS OPIMO USAR SQL DIRECTO PARA OPTIMIZAR EL TIEMPO'''
        item_obj = self.pool.get('budget.item')
        move_obj = self.pool.get('account.move')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        partner_obj = self.pool.get('res.partner')
        journal_obj = self.pool.get('account.journal')
        config_obj = self.pool.get('hr.account.configuration')
        period_obj = self.pool.get('account.period')
        pay_line = self.pool.get('hr.payslip.line')
        slip_obj = self.pool.get('hr.payslip')
        run_obj = self.pool.get('hr.payslip.run')
        certificate_obj = self.pool.get('budget.certificate')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        project_obj = self.pool.get('project.project')
        user_obj = self.pool.get('res.users')
        acc_rule = self.pool.get('rule.account')
        post_obj = self.pool.get('budget.post')
        cxp_obj = self.pool.get('rubro.cxp')
        rule_obj = self.pool.get('hr.salary.rule')
        parameter_obj = self.pool.get('ir.config_parameter')
        poa_obj = self.pool.get('budget.poa')
        total_aux = deduction_aux = basic_aux = s_o_ing = 0
        state_aux = 'draft'
        company_aux = 1
        currency_aux = 2
        band = False
        anticipo_aux = {}
        programa_anticipo_aux = []
        anticipo_aux_egr = []
        anticipo_quin_egr = []
        anticipo_budget_quin_egr = {}
        rendicion_aux = []
        vaca_aux = []
        quincena_aux = []
        #verificar si separa el aporte patronal
        patronal = False
        separa_patronal_ids = parameter_obj.search(cr, uid, [('key','=','separaPatronal')],limit=1)
        if separa_patronal_ids:
            separa_patronal = parameter_obj.browse(cr, uid, separa_patronal_ids[0]).value
            patronal = True
        for this in self.browse(cr, uid, ids):
            rule_base_ids = rule_obj.search(cr, uid, [('category_id.code','=','BASIC')])
            poa_ids = poa_obj.search(cr, uid,[('date_start','<=',this.period_id.date_start),('date_end','>=',this.period_id.date_start)])
            #certificacion presupuestaria
            aux_name = 'ASIENTO - ' + ustr(this.name) + ' DEL:  ' + ustr(this.period_id.name)
            aux_name2 = 'ASIENTO - APORTE PATRONAL ' + ustr(this.name) + ' DEL:  ' + ustr(this.period_id.name)
            usuario = user_obj.browse(cr, uid, uid)
            #debe tomar del mismo anio
            project_ids = project_obj.search(cr, uid, [('date_start','<=',this.date_end),('date','>=',this.date_end)])
            notes_aux = 'CERTIFICACION PRESUPUESTARIA DE NOMINA: ' + ustr(this.name) + ' DEL:  ' + ustr(this.period_id.name)
            notes_aux2 = 'CERTIFICACION PRESUPUESTARIA DE NOMINA APORTE PATRONAL: ' + ustr(this.name) + ' DEL:  ' + ustr(this.period_id.name)
            if this.certificate_id:
                if this.certificate_id.name=='/':
                    cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id.id))
                    certificate_obj.unlink(cr, uid, [this.certificate_id.id],context)
                    cp_id = certificate_obj.create(cr, uid, {
                        'department_id':usuario.context_department_id.id,
                        'solicitant_id':usuario.employee_id.id,
                        'project_id':project_ids[0],
                        'partner_id':1,
                        'notes':notes_aux,
                        'date':this.date_end,
                        'date_confirmed':this.date_end,
                        'date_commited':this.date_end,
                    })
                else:
                    cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id.id))
                    cp_id = this.certificate_id.id
            else:
                cp_id = certificate_obj.create(cr, uid, {
                    'department_id':usuario.context_department_id.id,
                    'solicitant_id':usuario.employee_id.id,
                    'project_id':project_ids[0],
                    'partner_id':1,
                    'notes':notes_aux,
                    'date':this.date_end,
                    'date_confirmed':this.date_end,
                    'date_commited':this.date_end,
                })
#            run_obj.write(cr, uid, this.id,{'certificate_id':cp_id})
            #compromiso de patronal
            if patronal:
                if this.certificate_id2:
                    if this.certificate_id2.name=='/':
                        cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id2.id))
                        certificate_obj.unlink(cr, uid, [this.certificate_id2.id],context)
                        cp_id2 = certificate_obj.create(cr, uid, {
                            'department_id':usuario.context_department_id.id,
                            'solicitant_id':usuario.employee_id.id,
                            'project_id':project_ids[0],
                            'partner_id':1,
                            'notes':notes_aux2,
                            'date':this.date_end,
                            'date_confirmed':this.date_end,
                            'date_commited':this.date_end,
                        })
                    else:
                        cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id2.id))
                        cp_id2 = this.certificate_id2.id
                else:
                    cp_id2 = certificate_obj.create(cr, uid, {
                        'department_id':usuario.context_department_id.id,
                        'solicitant_id':usuario.employee_id.id,
                        'project_id':project_ids[0],
                        'partner_id':1,
                        'notes':notes_aux2,
                        'date':this.date_end,
                        'date_confirmed':this.date_end,
                        'date_commited':this.date_end,
                    })
            journal_ids = journal_obj.search(cr, uid, [('name','=','ROLES')],limit=1)
            if not journal_ids:
                raise osv.except_osv(('Error de Configuracion !'),
                                     ("No existe diario de ROLES, cree uno por favor"))
            period_ids = period_obj.search(cr, uid, [('date_start','<=',this.date_end),('date_stop','>=',this.date_end)])
            if not period_ids:
                raise osv.except_osv(('Error de Configuracion !'),
                                     ("No existe periodo contable para la fecha de rol"))
            move_id2 = False
            if this.move_id:
                if this.move_id.migrado:
                    return True
                if this.move_id.state=='draft' and this.move_id.name=='/':
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                    move_obj.unlink(cr, uid, [this.move_id.id],aux=1)
                    move_id = move_obj.create(cr, uid, {
                        'ref': aux_name,
                        'narration':aux_name,
                        'journal_id': journal_ids[0],
                        'date': this.date_end,
                        'state':'draft',
                        'period_id':period_ids[0],
                        'afectacion':True,
                        'partner_id':1,
                        'certificate_id':cp_id,
                        'type':'Nomina',
                        'validar_cp':True,
                    })
                else:
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                    move_id = this.move_id.id
            else:
                move_id = move_obj.create(cr, uid, {
                    'ref': aux_name,
                    'narration':aux_name,
                    'journal_id': journal_ids[0],
                    'date': this.date_end,
                    'state':'draft',
                    'afectacion':True,
                    'period_id':period_ids[0],
                    'partner_id':1,
                    'certificate_id':cp_id,
                    'type':'Nomina',
                    'validar_cp':True,
                })
            #asiento de patronal si es separado
            if patronal:
                if this.move_id2:
                    if this.move_id2.migrado:
                        return True
                    if this.move_id2.state=='draft' and this.move_id2.name=='/':
                        cr.execute("delete from account_move_line where move_id=%s"%(this.move_id2.id))
                        move_obj.unlink(cr, uid, [this.move_id2.id],aux=1)
                        move_id2 = move_obj.create(cr, uid, {
                            'ref': aux_name2,
                            'narration':aux_name2,
                            'journal_id': journal_ids[0],
                            'date': this.date_end,
                            'state':'draft',
                            'period_id':period_ids[0],
                            'afectacion':True,
                            'partner_id':1,
                            'certificate_id':cp_id2,
                            'type':'Nomina',
                            'validar_cp':True,
                        })
                    else:
                        cr.execute("delete from account_move_line where move_id=%s"%(this.move_id2.id))
                        move_id2 = this.move_id2.id
                else:
                    move_id2 = move_obj.create(cr, uid, {
                        'ref': aux_name2,
                        'narration':aux_name2,
                        'journal_id': journal_ids[0],
                        'date': this.date_end,
                        'state':'draft',
                        'afectacion':True,
                        'period_id':period_ids[0],
                        'partner_id':1,
                        'certificate_id':cp_id2,
                        'type':'Nomina',
                        'validar_cp':True,
                    })
            for rol in this.slip_ids:
                deduction_aux += rol.deduction
                basic_aux += rol.basic
            total_aux = basic_aux - deduction_aux
            #asiento
            move_obj.write(cr, uid, [move_id],{
                'certificate_id':cp_id,
            })
            move = move_obj.browse(cr, uid, move_id)
            date_aux = move.date
            name_aux = 'ROL'
            tipo_rol_id = this.contract_type_id.id
            dict_partida = {}
            for line in this.detalle_ids:
                if not line.partida_id:
                    aux_msg_1 = line.rubro_id.name
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("La linea de rubro '%s' no tiene parametrizado la partida") % (aux_msg_1))
                line_id = certificate_line_obj.create(cr, uid, {
                    #'certificate_id':cp_id,
                    'project_id':line.partida_id.project_id.id,
                    'task_id':line.partida_id.project_id.tasks[0].id,
                    'budget_id':line.partida_id.id,
                    'amount':line.monto,
                    'amount_certified':line.monto,
                    'amount_commited':line.monto,
                })
                linea_aux_rol = certificate_line_obj.browse(cr, uid, line_id)
                b_id = linea_aux_rol.budget_id.id
                p_id = linea_aux_rol.budget_post.id
                post_code_aux = linea_aux_rol.budget_post.code
                #lo que suma y el extra rol van a debe
                #primero el sueldo basico y el a pagar de sueldo
                partner_id = 1
                if line.rubro_id.partner_id:
                    partner_id = line.rubro_id.partner_id.id
                if line.rubro_id.category_id.code=='BASIC':
                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
                    dict_partida[line.partida_id.id]=line_id
                    #sacar los roles del programa y aqui por cada uno sacar los totales
                    s_basic_aux = eg_aux = aux_total_det = 0
                    #ojo aqui tambien debe ser no con la partida sino con el post
#                    roles_aux = slip_obj.search(cr, uid, [('program_id','=',line.programa_id.id),('payslip_run_id','=',this.id),('budget_id','=',line.partida_id.id)])
                    roles_aux = slip_obj.search(cr, uid, [('program_id','=',line.programa_id.id),('payslip_run_id','=',this.id),('budget_id2','=',line.partida_id.budget_post_id.id)])
                    aux_total_det = s_basic_aux = s_o_ing = eg_aux = aux_3 = aux_neto = 0 
                    for rol_aux_id in roles_aux:
                        rol_aux = slip_obj.browse(cr, uid, rol_aux_id)
                        s_basic_aux += rol_aux.basic
                        s_o_ing += rol_aux.allowance
                        eg_aux += rol_aux.deduction
                        aux_neto += rol_aux.net
                    #sacar el neto y cambiar en las lineas de partida
                    #certificate_line_obj.write(cr, uid, line_id,{'amount':aux_neto,'amount_certified':aux_neto,'amount_commited':aux_neto})
                    aux_3 = s_basic_aux + s_o_ing
                    aux_total_det = s_basic_aux - eg_aux #+ aux_aa
                    account_ids_1 = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id),('type','!=','view')])
                    account_ids_2 = account_obj.search(cr, uid, [('budget_haber_id','=',line.partida_id.budget_post_id.id),('type','!=','view')])
                    account_ids = account_ids_1 + account_ids_2
                    if not account_ids:
                        #aqui considerar las cuentas patrimonio de la partida de mayor
                        post_ids = post_obj.search(cr, uid, [('code','=',line.partida_id.budget_post_id.code[0:6])])
                        if post_ids:
                            account_ids = account_obj.search(cr, uid, [('budget_id','in',post_ids),('type','!=','view')])
                            if not account_ids:
                                aux_msg_1 = line.partida_id.budget_post_id.code
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("La partida '%s' no tiene parametrizado la cuenta") % (aux_msg_1))
                    for account_id in account_ids:
                        account = account_obj.browse(cr, uid, account_id)
                        if account.account_pay_id:
                            break#continue
                    #SQL
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,s_basic_aux,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'Sueldo',False,False,partner_id))
                    if account.account_rec_id:
                        if account.code[0:3]=='151' and post_code_aux[0:1]=='5':
                            print "MALLLLLLLL"
                        if account.code[0:3]=='633' and post_code_aux[0:1]=='7':
                            print "MALLLLLLLL"
                        if account.code[0:5]=='21371' and post_code_aux[0:1]=='5':
                            print "MALLLLLLLL"
                        if account.code[0:5]=='21351' and post_code_aux[0:1]=='7':
                            print "MALLLLLLLL"
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.account_rec_id.id,aux_total_det,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'neto',False,True,partner_id))
                    elif account.account_pay_id:
                        if account.code[0:3]=='151' and post_code_aux[0:1]=='5':
                            print "MALLLLLLLL"
                        if account.code[0:3]=='633' and post_code_aux[0:1]=='7':
                            print "MALLLLLLLL"
                        if account.code[0:5]=='21371' and post_code_aux[0:1]=='5':
                            print "MALLLLLLLL"
                        if account.code[0:5]=='21351' and post_code_aux[0:1]=='7':
                            print "MALLLLLLLL"
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.account_pay_id.id,aux_total_det,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'neto',False,True,partner_id))
                    else:
                        aux_msg_1 = account.code + ' - ' + account.name
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
                #extra rol apt patronal
                elif line.rubro_id.category_id.code=='COMP':
                    if patronal:
                        certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id2,})
                    else:
                        certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                    if not account_ids:
                        #busco por el codigo papa
                        post_ids_aux = post_obj.search(cr, uid, [('code','=',line.partida_id.budget_post_id.code[0:6])])
                        if post_ids_aux:
                            account_ids = account_obj.search(cr, uid, [('budget_id','in',post_ids_aux)])
                            if not account_ids:
                                aux_msg_1 = line.rubro_id.name + ' - ' + line.partida_id.budget_post_id.code
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("La partida '%s' no esta asociada a alguna cuenta contable") % (aux_msg_1))
                    account = account_obj.browse(cr, uid, account_ids[0])
                    for account_id in account_ids:
                        account = account_obj.browse(cr, uid, account_id)
                        if account.account_rec_id:
                            account_comp = account.account_rec_id.id
                            band_comp = True
                            break
                        elif account.account_pay_id:
                            account_comp = account.account_pay_id.id
                            band_comp=True
                            break
                    if account.code[0:3]=='151' and post_code_aux[0:1]=='5':
                        print "MALLLLLLLL"
                    if account.code[0:3]=='633' and post_code_aux[0:1]=='7':
                        print "MALLLLLLLL"
                    if account.code[0:5]=='21371' and post_code_aux[0:1]=='5':
                        print "MALLLLLLLL"
                    if account.code[0:5]=='21351' and post_code_aux[0:1]=='7':
                        print "MALLLLLLLL"
                    aux_move_id = move_id
                    if patronal:
                        aux_move_id = move_id2
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(aux_move_id,account.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'Patronal',False,False,partner_id))
                    #aqui preguntar si tiene el rubro la 212 y si tiene buscar en las lineas por tipo rol
                    aux_tercero_id = False
                    if line.rubro_id.tercero_id:
                        lines_ids = acc_rule.search(cr, uid, [('rc_id','=',line.rubro_id.id),('tipo_id','=',tipo_rol_id)])
                        if lines_ids:
                            line_acc = acc_rule.browse(cr, uid, lines_ids[0])
                            aux_tercero_id = line_acc.account_id.id
                    else:
                        aux_tercero_id = line.rubro_id.tercero_id.id
                    if account.code[0:3]=='151' and post_code_aux[0:1]=='5':
                        print "MALLLLLLLL"
                    if account.code[0:3]=='633' and post_code_aux[0:1]=='7':
                        print "MALLLLLLLL"
                    if account.code[0:5]=='21371' and post_code_aux[0:1]=='5':
                        print "MALLLLLLLL"
                    if account.code[0:5]=='21351' and post_code_aux[0:1]=='7':
                        print "MALLLLLLLL"
                    if account.account_rec_id:
                        if aux_tercero_id:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id,account_id2) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(aux_move_id,account.account_rec_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'patronal',False,True,partner_id,aux_tercero_id))
                        elif account.account_rec_id.tercero_id:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id,account_id2) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(aux_move_id,account.account_rec_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'patronal',False,True,partner_id,account.account_rec_id.tercero_id.id))
                        else:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(aux_move_id,account.account_rec_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'patronal',False,True,partner_id))
                    elif account.account_pay_id:
                        if aux_tercero_id:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id,account_id2) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(aux_move_id,account.account_pay_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'patronal',False,True,partner_id,aux_tercero_id))
                        elif account.account_pay_id.tercero_id:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id,account_id2) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(aux_move_id,account.account_pay_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'patronal',False,True,partner_id,account.account_pay_id.tercero_id.id))
                        else:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(aux_move_id,account.account_pay_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'patronal',False,True,partner_id))
                    else:
                        aux_msg_1 = account.code + ' - ' + account.name
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
                #Ingresos
                elif line.rubro_id.category_id.code in ('ING','APT'):
                    if line.rubro_id.is_ingreso_anticipo:
                        if line.programa_id.id in vaca_aux:
                            continue
                        name_aux = line.rubro_id.name
                        anticipo_ids = pay_line.search(cr, uid, [('run_id','=',this.id),('salary_rule_id','=',line.rubro_id.id),
                                                                 ('program_id','=',line.programa_id.id)])
                        if anticipo_ids:
                            no_cta = []
                            for anticipo_id in anticipo_ids:
                                anticipo = pay_line.browse(cr, uid, anticipo_id)
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',anticipo.employee_id.name)],limit=1)
                                if partner_ids:
                                    partner= partner_obj.browse(cr, uid, partner_ids[0])
                                else:
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("El funcionario '%s' no tiene proveedor") % (anticipo.employee_id.complete_name))
                                if partner.anticipo_id:
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_paid,migrado,partner_id,is_ingreso_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,partner.anticipo_id.id,anticipo.total,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,False,partner.id,True))
                                else:
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("El proveedor %s no tiene cuenta de anticipo configurada") % (anticipo.employee_id.complete_name))
                        vaca_aux.append(line.programa_id.id)
                    else:
                        aux_desc = line.rubro_id.name
                        aux_ref = 'ingreso'
                        certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
                        account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id),('type','!=','view')])
                        if not account_ids:
                            if line.config_id:
                                account_ids.append(line.config_id.expense_account_id.id)
                            else:
                                if not account_ids:
                                    post_ids = post_obj.search(cr, uid, [('code','=',line.partida_id.budget_post_id.code[0:6])])
                                    if post_ids:
                                        account_ids = account_obj.search(cr, uid, [('budget_id','in',post_ids),('type','!=','view')])
                                    if not account_ids:
                                        aux_msg_1 = line.partida_id.budget_post_id.code + ' - ' + line.partida_id.budget_post_id.name
                                        raise osv.except_osv(('Error de Configuracion !'),
                                                             ("La partida '%s' no tiene parametrizado la relacion con cuenta patrimonial de gasto") % (aux_msg_1))
                        if len(account_ids)>1:
                            for acc_id in account_ids:
                                account_aux = account_obj.browse(cr, uid, acc_id)
                                if account_aux.account_rec_id.id or account_aux.account_pay_id.id:
                                    account = account_obj.browse(cr, uid, acc_id)
                        else:
                            if not account_ids:
                                print "RAOSE DE NO CUNETA PARTIDA CONFIGURACON"
                            account = account_obj.browse(cr, uid, account_ids[0])
                        if not account:
                            print "RAISE DE BO  HAY CONFIGURADOIN DE LA CUENTA"
                        if account.code[0:3]=='151' and post_code_aux[0:1]=='5':
                            print "MALLLLLLLL"
                        if account.code[0:3]=='633' and post_code_aux[0:1]=='7':
                            print "MALLLLLLLL"
                        if account.code[0:5]=='21371' and post_code_aux[0:1]=='5':
                            print "MALLLLLLLL"
                        if account.code[0:5]=='21351' and post_code_aux[0:1]=='7':
                            print "MALLLLLLLL"
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,ref,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,aux_desc,False,False,'ingreso',partner_id))
                        if account.account_rec_id:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,ref,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.account_rec_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,aux_desc,False,True,'ingreso',partner_id))
                        elif account.account_pay_id:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,ref,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.account_pay_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,aux_desc,False,True,'ingreso',partner_id))
                        else:
                            aux_msg_1 = account.code + ' - ' + account.name
                            raise osv.except_osv(('Error de Configuracion !'),
                                                 ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
                elif line.rubro_id.category_id.code == 'EGR':
#                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
#                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,
#                                                                 'amount':0,
#                                                                 'amount_certified':0,
#                                                                'amount_commited':0,
#                                                             })
                    if dict_partida.has_key(line.partida_id.id):
                        aux_certA = dict_partida[line.partida_id.id]
                    else:
                        dict_partida[line.partida_id.id]=line_id
                        aux_certA = line_id
                    #Anticipos de salario tiene 3 lineas
                    #hacer sql para insertar directo seria mucho mas rapido
                    #separar la primera quincena
                    #consideracion si es tipo vacaciones anticipo
                    
#                    if "Anticipo" in line.rubro_id.name:

#                    if "Anticipo" or "ANTICIPO" in line.rubro_id.name:
                    #aqui se debe considerar otros rubros q tambien son anticipo pero otro, no lista sino diccionario rubro id:programa id

                    if ("Anticipo" in line.rubro_id.name) or ("ANTICIPO" in line.rubro_id.name) and (line.rubro_id.name!='ANTICIPO QUINCENA'):  
                        #print "RIBROORRR", line.rubro_id.name
                        if not line.rubro_id.id in anticipo_aux:
                            anticipo_aux[line.rubro_id.id] = [] 
                        if line.programa_id.id in anticipo_aux[line.rubro_id.id]:
                            continue
                        #saco los anticipos de los empleados del rol
                        else:
                            anticipo_ids = pay_line.search(cr, uid, [('run_id','=',this.id),('salary_rule_id','=',line.rubro_id.id),
                                                                     ('program_id','=',line.programa_id.id)])
                        if anticipo_ids:
                            no_cta = []
                            for anticipo_id in anticipo_ids:
                                anticipo = pay_line.browse(cr, uid, anticipo_id)
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',anticipo.employee_id.name)],limit=1)
                                if partner_ids:
                                    partner= partner_obj.browse(cr, uid, partner_ids[0])
                                else:
                                    aux_msg_1 = anticipo.employee_id.complete_name
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("El funcionario'%s' no esta relacionada a un proveedor") % (aux_msg_1))
                                if not partner.anticipo_id:
                                    no_cta.append(partner.name)
                                if no_cta:
                                    str_empleados = ''
                                    for n_cta in no_cta:
                                        str_empleados += n_cta + ' - '
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("Los funcionarios '%s' no tiene parametrizado la cuenta de anticipo") % (str_empleados))
                            for anticipo_id in anticipo_ids:
                                anticipo = pay_line.browse(cr, uid, anticipo_id)
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',anticipo.employee_id.name)],limit=1)
                                if partner_ids:
                                    partner= partner_obj.browse(cr, uid, partner_ids[0])
                                else:
                                    aux_msg_1 = anticipo.employee_id.complete_name
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("El funcionario'%s' no esta relacionada a un proveedor") % (aux_msg_1))
                                account_id_ant = False
                                if partner.anticipo_id or line.rubro_id.account_id:
                                    account_ids = account_obj.search(cr, uid, ['|',('budget_id','=',line.partida_id.budget_post_id.id),
                                                                               ('budget_haber_id','=',line.partida_id.budget_post_id.id)])
                                    no_2 = False
                                    if not account_ids:
                                        ##cojo la cxp del rmu
                                        config_ant_ids = config_obj.search(cr, uid, [('rule_id','in',rule_base_ids),('budget_id','=',line.partida_id.budget_post_id.id)])
                                        if config_ant_ids:
                                            config_ant = config_obj.browse(cr, uid, config_ant_ids[0])
                                            account = config_ant.pay_account_id
                                            account_id_ant = account.id
                                            account_ids = [config_ant.pay_account_id.id]
                                            no_2 = True
                                    if not account_ids and not no_2:
                                        aux_msg_1 = line.partida_id.budget_post_id.code + ' - ' + line.partida_id.budget_post_id.name
                                        raise osv.except_osv(('Error de Configuracion !'),
                                                             ("La partida '%s' no esta relacionada con cuenta contable") % (aux_msg_1))
                                    if not no_2:
                                        for account_id in account_ids:
                                            account = account_obj.browse(cr, uid, account_id)
                                            if account.account_rec_id:
                                                account_id_ant = account.account_rec_id.id
                                                break
                                            elif account.account_pay_id:
                                                account_id_ant = account.account_pay_id.id
                                                break
                                            else:
                                                #aux_msg_1 = account.code + ' - ' + account.name
                                                #raise osv.except_osv(('Error de Configuracion !'),
                                                #                     ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
                                                account_id_ant = account_obj.browse(cr, uid, account_ids[0]).id
                                    if not account_id_ant:
                                        aux_msg_ant = anticipo.employee_id.complete_name
                                        raise osv.except_osv(('Error de Configuracion !'),
                                                             ("No hay cuenta de anticipo para '%s'") % (aux_msg_ant))
                                    #hacer con sqls para optimizar
                                    anticipo_acc_id = partner.anticipo_id.id
                                    if not partner.anticipo_id:
                                        aux_msg_ant = anticipo.employee_id.complete_name
                                        raise osv.except_osv(('Error de Configuracion !'),
                                                             ("No hay cuenta de anticipo para '%s'") % (aux_msg_ant))
                                    si_cta = False
                                    #solo para R
                                    riobamba = False
                                    anticipos_r_ids = parameter_obj.search(cr, uid, [('key','=','anticipoR')],limit=1)
                                    if anticipos_r_ids:
                                        anticipo_r_opc = parameter_obj.browse(cr, uid, anticipos_r_ids[0]).value
                                        riobamba = True
                                    if riobamba==False:
                                        if line.rubro_id.account_id and not anticipo_acc_id:
                                            anticipo_acc_id = line.rubro_id.account_id.id
                                            si_cta = True
                                    #riobamba cambiar la 213 con la cta
                                    if riobamba:
#                                        item_ids_anticipo = item_obj.search(cr, uid,[('budget_post_id','=',anticipo.contract_id.budget_id.budget_post_id.id),
#                                                                                     ('program_id','=',anticipo.contract_id.program_id.id),('poa_id','=',poa_ids[0])])
                                        if line.rubro_id.account_id:
                                            #busco si es inversion o corriente
                                            aux_code_cxc = '213' + anticipo.contract_id.budget_id.budget_post_id.code[0:2]
                                            cxp_ids = cxp_obj.search(cr, uid, [('name','=',aux_code_cxc)])
                                            if cxp_ids:
                                                cxp = cxp_obj.browse(cr, uid, cxp_ids[0])
                                                account_id_ant = cxp.account_id.id
                                            else:
                                                account_id_ant = line.rubro_id.account_id.id
                                            si_cta = True
                                    name_aux = line.rubro_id.name
                                    account_ant_aux_2 = account_obj.browse(cr, uid, account_id_ant)
                                    if account_ant_aux_2.code[0:3]=='151' and post_code_aux[0:1]=='5':
                                        print "MALLLLLLLL"
                                    if account_ant_aux_2.code[0:3]=='633' and post_code_aux[0:1]=='7':
                                        print "MALLLLLLLL"
                                    if account_ant_aux_2.code[0:5]=='21371' and post_code_aux[0:1]=='5':
                                        print "MALLLLLLLL"
                                    if account_ant_aux_2.code[0:5]=='21351' and post_code_aux[0:1]=='7':
                                        print "MALLLLLLLL"
                                    if anticipo.amount>0:
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,partner_id,is_anticipo) VALUES (%s,%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,anticipo_acc_id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,partner.id,True))
                                        #cta 213
                                        item_ids_anticipo = item_obj.search(cr, uid,[('budget_post_id','=',anticipo.contract_id.budget_id.budget_post_id.id),
                                                                                     ('program_id','=',anticipo.contract_id.program_id.id),('poa_id','=',poa_ids[0])])
                                        if not poa_ids:
                                            raise osv.except_osv(('Error de Configuracion !'),
                                                                 ("No hay poa para la fecha de rol"))
                                        if not item_ids_anticipo:
                                            raise osv.except_osv(('Error de Configuracion !'),
                                                                 ("No hay partida presupuestaria '%s' de anticipo para el programa '%s'") % (anticipo.contract_id.budget_id.budget_post_id.name,anticipo.contract_id.program_id.code))
                                        certificateA_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',item_ids_anticipo[0]),
                                                                                                 ('certificate_id','=',cp_id)]) #this.certifictae_id.id
                                        if not dict_partida.has_key(item_ids_anticipo[0]):
                                            raise osv.except_osv(('Error de Configuracion !'),
                                                                 ("No hay partida presupuestaria configurada '%s' de anticipo para el contrato '%s'") % (anticipo.contract_id.budget_id.budget_post_id.name,anticipo.contract_id.employee_id.complete_name))
                                        aux_certA = dict_partida[item_ids_anticipo[0]]
                                        #if not certificateA_ids:
                                        #    raise osv.except_osv(('Error de Configuracion !'),
                                        #                         ("No hay partida en el compromiso '%s', '%s'") % (anticipo.contract_id.budget_id.budget_post_id.code,anticipo.contract_id.program_id.sequence))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,partner_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,aux_certA,True,True,False,anticipo.contract_id.budget_id.budget_post_id.id,item_ids_anticipo[0],partner.id,True))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,migrado,budget_post,budget_id,partner_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,aux_certA,False,anticipo.contract_id.budget_id.budget_post_id.id,item_ids_anticipo[0],partner.id,True))
#                                        cr.execute('''
#                                        INSERT INTO account_move_line (
#                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,partner_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,True,True,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner.id,True))
#                                        cr.execute('''
#                                        INSERT INTO account_move_line (
#                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,migrado,budget_post,budget_id,partner_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner.id,True))
                                else:
                                    no_cta.append(partner.name)
                            if no_cta:
                                str_empleados = ''
                                for n_cta in no_cta:
                                    str_empleados += n_cta + ' - '
                                if not si_cta:
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("Los funcionarios '%s' no tiene parametrizado la cuenta de anticipo") % (str_empleados))
                            #no considerar esto en limon
                            varios_opcion = 'No'
                            parameter_obj = self.pool.get('ir.config_parameter')
                            varios_anticipos_programa_ids = parameter_obj.search(cr, uid, [('key','=','anticipoPrograma')],limit=1)
                            if varios_anticipos_programa_ids:
                                varios_opcion = parameter_obj.browse(cr, uid, varios_anticipos_programa_ids[0]).value
                            if varios_opcion=='No':
                                #anticipo_aux.append(line.programa_id.id)
                                anticipo_aux[line.rubro_id.id].append(line.programa_id.id)
                            band = True
                    #anticipo egreso
                    elif "ANTICIPO EGRESO" in line.rubro_id.name:
                        print "ANT EGRESO"
                        if line.programa_id.id in anticipo_aux_egr:
                            continue
                        #saco los anticipos de los empleados del rol
                        else:
                            anticipo_ids = pay_line.search(cr, uid, [('run_id','=',this.id),('salary_rule_id','=',line.rubro_id.id),
                                                                     ('program_id','=',line.programa_id.id)])
                        if anticipo_ids:
                            no_cta = []
                            for anticipo_id in anticipo_ids:
                                anticipo = pay_line.browse(cr, uid, anticipo_id)
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',anticipo.employee_id.name)],limit=1)
                                if partner_ids:
                                    partner= partner_obj.browse(cr, uid, partner_ids[0])
                                else:
                                    print "NO partner de empleado"
                                if partner.anticipo_id:
                                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                                    if not account_ids:
                                        print "No partida cuenta"
                                    for account_id in account_ids:
                                        account = account_obj.browse(cr, uid, account_id)
                                        if account.account_rec_id:
                                            account_id_ant = account.account_rec_id.id
                                            break
                                        elif account.account_pay_id:
                                            account_id_ant = account.account_pay_id.id
                                            break
                                        else:
                                            #aux_msg_1 = account.code + ' - ' + account.name
                                            #raise osv.except_osv(('Error de Configuracion !'),
                                            #                     ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
                                            account_id_ant = account_obj.browse(cr, uid, account_ids[0]).id
#                                    if not account_id_ant:
#                                        aux_msg_ant = anticipo.employee_id.complete_name
#                                        raise osv.except_osv(('Error de Configuracion !'),
#                                                             ("No hay cuenta de anticipo para '%s'") % (aux_msg_ant))
                                    #hacer con sqls para optimizar
                                    si_cta = False
                                    anticipo_acc_id = partner.anticipo_id.id 
                                    if line.rubro_id.account_id:
                                        anticipo_acc_id = line.rubro_id.account_id.id
                                        si_cta = True
                                    name_aux = line.rubro_id.name
                                    if account_id_ant.code[0:3]=='151' and post_code_aux[0:1]=='5':
                                        print "MALLLLLLLL"
                                    if account_id_ant.code[0:3]=='633' and post_code_aux[0:1]=='7':
                                        print "MALLLLLLLL"
                                    if account_id_ant.code[0:5]=='21371' and post_code_aux[0:1]=='5':
                                        print "MALLLLLLLL"
                                    if account_id_ant.code[0:5]=='21351' and post_code_aux[0:1]=='7':
                                        print "MALLLLLLLL"
                                    if anticipo.amount>0:
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,partner_id,is_anticipo) VALUES (%s,%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,anticipo_acc_id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,partner.id,True))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,partner_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,True,True,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner.id,True))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,migrado,budget_post,budget_id,partner_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner.id,True))
                                else:
                                    no_cta.append(partner.name)
                            if no_cta:
                                str_empleados = ''
                                for n_cta in no_cta:
                                    str_empleados += n_cta + ' - '  
                                if not si_cta:
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("Los funcionarios '%s' no tiene parametrizado la cuenta de anticipo") % (str_empleados))
                            anticipo_aux_egr.append(line.programa_id.id)
                    #egresos en general
                    elif line.rubro_id.name in ('PRIMERA QUINCENA'):
                        if line.programa_id.id in quincena_aux:
                            continue
                        #saco los anticipos de los empleados del rol
                        else:
                            anticipo_ids = pay_line.search(cr, uid, [('run_id','=',this.id),('salary_rule_id','=',line.rubro_id.id),
                                                                     ('program_id','=',line.programa_id.id)])
                        if anticipo_ids:
                            for anticipo_id in anticipo_ids:
                                anticipo = pay_line.browse(cr, uid, anticipo_id)
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',anticipo.employee_id.name)],limit=1)
                                if partner_ids:
                                    partner= partner_obj.browse(cr, uid, partner_ids[0])
                                else:
                                    print "NO partner de empleado"
                                if partner.anticipo_id:
                                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                                    if not account_ids:
                                        print "No partida cuenta"
                                    for account_id in account_ids:
                                        account = account_obj.browse(cr, uid, account_id)
                                        if account.account_rec_id:
                                            account_quin_id = account.account_rec_id.id
                                            break
                                        elif account.account_pay_id:
                                            account_quin_id = account.account_pay_id.id
                                            break
                                        else:
                                            account_quin_id = account_obj.browse(cr, uid, account_ids[0]).id
                                    #hacer con sqls para optimizar
                                    if anticipo.amount>0:
                                        name_aux = 'Antic. 1er Quincena'
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,is_anticipo) VALUES (%s,%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s)''',(move_id,partner.anticipo_id.id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,True))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_quin_id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,True,True,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,True))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,migrado,budget_post,budget_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_quin_id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,True))
                                else:
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("El proveedor '%s' no tiene parametrizado la cuenta de anticipo") % (partner.name))
                            quincena_aux.append(line.programa_id.id)
                            band = True
                    else:
                        name_aux = line.rubro_id.name
                        if line.rubro_id.is_rendicion:
                            if line.programa_id.id in rendicion_aux:
                                continue
                            #saco los anticipos de los empleados del rol
                            else:
                                rendicion_ids = pay_line.search(cr, uid, [('run_id','=',this.id),('salary_rule_id','=',line.rubro_id.id),
                                                                         ('program_id','=',line.programa_id.id)])
                            if rendicion_ids:
                                no_cta_fondo = []
                                for rendicion_id in rendicion_ids:
                                    rendicion = pay_line.browse(cr, uid, rendicion_id)
                                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',rendicion.employee_id.name)],limit=1)
                                    if partner_ids:
                                        partner= partner_obj.browse(cr, uid, partner_ids[0])
                                    else:
                                        raise osv.except_osv(('Error de Configuracion !'),
                                                             ("El empleado '%s' no tiene proveedor") % (rendicion.employee_id.complete_name))
                                    if partner.rendir_id:
                                        name_aux = line.rubro_id.name
                                        if rendicion.amount>0:
                                            account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                                            if not account_ids:
                                                print "No partida cuenta"
                                            for account_id in account_ids:
                                                account = account_obj.browse(cr, uid, account_id)
                                                if account.account_rec_id:
                                                    account_rendicion = account.account_rec_id.id
                                                    break
                                                elif account.account_pay_id:
                                                    account_rendicion = account.account_pay_id.id
                                                    break
                                                else:
                                                    print "NOne"
                                            cr.execute('''
                                            INSERT INTO account_move_line (
                                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_rendicion,rendicion.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,True,True,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,True))
                                            cr.execute('''
                                            INSERT INTO account_move_line (
                                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,migrado,budget_post,budget_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_rendicion,rendicion.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,True))
                                            cr.execute('''
                                            INSERT INTO account_move_line (
                                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,partner_id,is_anticipo) VALUES (%s,%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,partner.rendir_id.id,rendicion.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,partner.id,True))
                                    else:
                                        no_cta_fondo.append(partner.name)
                                if no_cta_fondo:
                                    str_empleados = ''
                                    for n_cta in no_cta_fondo:
                                        str_empleados += n_cta + ' - '  
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("Los funcionarios '%s' no tiene parametrizado la cuenta de fondos a rendir cuentas") % (str_empleados))
                                #no considerar esto en limon
                            rendicion_aux.append(line.programa_id.id)
                        elif line.rubro_id.name=='ANTICIPO QUINCENA':
                            if this.contract_type_id.account_id:
                                aux_account_type_id = this.contract_type_id.account_id.id
                            elif line.rubro_id.account_id:
                                aux_account_type_id = line.rubro_id.account_id.id
                            else:
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("El anticipo quincena necesita configuracion de cuenta"))

                            if not line.programa_id.id in anticipo_budget_quin_egr:
                                anticipo_budget_quin_egr[line.programa_id.id] = [] 
                            if line.partida_id.budget_post_id.id in anticipo_budget_quin_egr[line.programa_id.id]:
                                continue
                                #saco los anticipos de los empleados del rol
                            else:
                                anticipo_quin_ids = pay_line.search(cr, uid, [('run_id','=',this.id),('salary_rule_id','=',line.rubro_id.id),
                                                                              ('program_id','=',line.programa_id.id),
                                                                              ('budget_id2','=',line.partida_id.budget_post_id.id)])
                            if anticipo_quin_ids:
                                for anticipo_id in anticipo_quin_ids:
                                    anticipo = pay_line.browse(cr, uid, anticipo_id)
                                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',anticipo.employee_id.name)],limit=1)
                                    if partner_ids:
                                        partner= partner_obj.browse(cr, uid, partner_ids[0])
                                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                                    if not account_ids:
                                        print "No partida cuenta"
                                    for account_id in account_ids:
                                        account = account_obj.browse(cr, uid, account_id)
                                        if account.account_rec_id:
                                            account_quin1_ant = account.account_rec_id.id
                                            break
                                        elif account.account_pay_id:
                                            account_quin1_ant = account.account_pay_id.id
                                            break
                                        else:
                                            print "NOne"
                                    if anticipo.amount>0:
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_quin1_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,True,True,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,True))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,migrado,budget_post,budget_id,is_anticipo) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_quin1_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,True))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,partner_id,is_anticipo) VALUES (%s,%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,aux_account_type_id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,partner.id,True))
                                band=True
                                anticipo_budget_quin_egr[line.programa_id.id].append(line.partida_id.budget_post_id.id)
                        else:
                            #aqui preguntar si tiene el rubro la 212 y si tiene buscar en las lineas por tipo rol
                            aux_tercero_id = False
                            if line.rubro_id.tercero_id:
                                lines_ids = acc_rule.search(cr, uid, [('rc_id','=',line.rubro_id.id),('tipo_id','=',tipo_rol_id)])
                                if lines_ids:
                                    line_acc = acc_rule.browse(cr, uid, lines_ids[0])
                                    aux_tercero_id = line_acc.account_id.id
                            else:
                                aux_tercero_id = line.rubro_id.tercero_id.id
                            budget_item = line.partida_id
                            config_ids = config_obj.search(cr, uid, [('rule_id','=',line.rubro_id.id),('budget_id','=',budget_item.budget_post_id.id)])
                            if not config_ids:
                                aux_bd = budget_item.budget_post_id.code + ' - ' + budget_item.budget_post_id.name  
                                config_ids = config_obj.search(cr, uid, [('rule_id','=',line.rubro_id.id)])
                                if not config_ids:
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("El rubro '%s' no tiene parametrizado para la partida") % (ustr(line.rubro_id.name)))
                            config = config_obj.browse(cr, uid, config_ids[0])
                            if not config.pay_account_id:
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("El rubro '%s' no tiene parametrizado para la cuenta por pagar") % (ustr(line.rubro_id.name)))
                            account_id = config.pay_account_id.id
                            if config.pay_account_id.code[0:3]=='151' and post_code_aux[0:1]=='5':
                                print "MALLLLLLLL"
                            if config.pay_account_id.code[0:3]=='633' and post_code_aux[0:1]=='7':
                                print "MALLLLLLLL"
                            if config.pay_account_id.code[0:5]=='21371' and post_code_aux[0:1]=='5':
                                print "MALLLLLLLL"
                            if config.pay_account_id.code[0:5]=='21351' and post_code_aux[0:1]=='7':
                                print "MALLLLLLLL"
                            if line.rubro_id.tercero_id:
                                if aux_tercero_id:
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,partner_id,account_id2,is_ingreso_gad) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,aux_certA,True,False,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner_id,aux_tercero_id,line.rubro_id.is_ingreso_gad))
                                else:
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,partner_id,account_id2,is_ingreso_gad) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,aux_certA,True,False,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner_id,line.rubro_id.tercero_id.id,line.rubro_id.is_ingreso_gad))
                            elif config.pay_account_id.tercero_id:
                                cr.execute('''
                                INSERT INTO account_move_line (
                                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,partner_id,account_id2,is_ingreso_gad) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,aux_certA,True,False,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner_id,config.pay_account_id.tercero_id.id,line.rubro_id.is_ingreso_gad))
                            else:
                                cr.execute('''
                                INSERT INTO account_move_line (
                                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_accrued,budget_paid,migrado,budget_post,budget_id,partner_id,is_ingreso_gad) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,aux_certA,True,False,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner_id,line.rubro_id.is_ingreso_gad))                  
                else:
                    print "fds"
#            certificate_obj.action_request(cr, uid, [cp_id], context)
#            certificate_obj.action_certified(cr, uid, [cp_id], context)
#            certificate_obj.action_commited(cr, uid, [cp_id], context)
            self.write(cr, uid, this.id,{
                'move_id':move_id,
                'move_id2':move_id2 or '',
                'certificate_id':cp_id,
                'contabilizado':True,
            })
        return True

    def contabilizar_payslip_run2(self, cr, uid, ids, context=None):
        self._create_move_tthh(cr, uid, ids)
        return True

    def reversaconta_payslip_run(self, cr, uid, ids, context=None):    
        run_obj = self.pool.get('hr.payslip.run')
        for this in self.browse(cr, uid, ids):
            if this.move_id:
                if this.move_id.state=='posted':
                    raise osv.except_osv(('Error de usuario'),('El registro contable numero %s de el rol esta contabilizado,debe regresar a borrador.') %(this.move_id.name))
            if this.certificate_id:
                if this.certificate_id.state!='draft':
                    raise osv.except_osv(('Error de usuario'), ('El documento presupuestario numero %s de este rol debe estar en borrador')%(this.certificate_id.name))
            run_obj.write(cr, uid, this.id, {'contabilizado':False})
        return True

    def contabilizar_payslip_run(self, cr, uid, ids, context=None):
        payslip_line_obj = self.pool.get('hr.payslip.line')
        detalle_obj = self.pool.get('run.programa.detalle')
        budget_item_obj=self.pool.get('budget.item')
        rule_obj = self.pool.get('hr.salary.rule')
        payslip_obj = self.pool.get('hr.payslip')
        program_obj = self.pool.get('project.program')
        project_obj = self.pool.get('project.project')
        config_obj = self.pool.get('hr.account.configuration')
        year_obj = self.pool.get('account.fiscalyear')
        programas = []
        rubros = []
        contratos = []
        detalle = []
        for this in self.browse(cr, uid, ids):
            if this.contabilizado:
                raise osv.except_osv('Error de usuario', 'El rol ya esta contabilizado, debe reversar esta contabilizacion.')
            year_ids = year_obj.search(cr, uid, [('date_start','<=',this.date_end),('date_stop','>=',this.date_end)],limit=1)
            if year_ids:
                year = year_obj.browse(cr, uid, year_ids[0])
            else:
                raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha de compromiso.')
            id_this = this.id
            detalle_antes = detalle_obj.search(cr, uid, [('run_id','=',id_this)])
            detalle_obj.unlink(cr, uid, detalle_antes)
            slip_aux = []
            for line in this.slip_ids:#roles individuales
                slip_aux.append(line.id)
                aux_id_1 = line.contract_id.budget_id.id
                aux_id_2 = line.contract_id.budget_id.budget_post_id.id
                #si cambio la partida en el contrato cambiar en el rol
                if line.budget_id2.id!=line.contract_id.budget_id.budget_post_id.id:
                    aux_id_1 = line.contract_id.budget_id.id
                    aux_id_2 = line.contract_id.budget_id.budget_post_id.id
                    payslip_obj.write(cr, uid, line.id,{
                        'budget_id':aux_id_1,
                        'budget_id2':aux_id_2,
                    })
                    lineas_rol = payslip_line_obj.search(cr, uid, [('slip_id','=',line.id)])
                    if len(lineas_rol)>1:
                        tuple_ids = tuple(lineas_rol)
                        operador = 'in'
                    else:
                        tuple_ids = (lineas_rol[0])
                        operador = '='
                    if lineas_rol:
                        sql_update_1 = "UPDATE hr_payslip_line set budget_id=%s,budget_id2=%s where id %s %s"%(aux_id_1,aux_id_2,operador,tuple_ids)
                        cr.execute(sql_update_1)
                lineas_rol = payslip_line_obj.search(cr, uid, [('slip_id','=',line.id)])
                if not lineas_rol:
                    continue
                    raise osv.except_osv(('Error de configuracion !'),
                                         ("No existen detalle rol de %s") % (line.contract_id.employee_id.complete_name))
                if len(lineas_rol)>1:
                    tuple_ids = tuple(lineas_rol)
                    operador = 'in'
                else:
                    tuple_ids = (lineas_rol[0])
                    operador = '='
                if lineas_rol:
#                    sql_update = "UPDATE hr_payslip_line set budget_id2=%s where id %s %s"%(line.budget_id2.id,operador,tuple_ids)
                    sql_update = "UPDATE hr_payslip_line set budget_id=%s,budget_id2=%s where id %s %s"%(aux_id_1,aux_id_2,operador,tuple_ids)
                    cr.execute(sql_update)
                if not line.program_id.id in programas:
                    programas.append(line.program_id.id)
                for rubro in line.line_ids:#payslip line
                    if rubro.salary_rule_id.category_id.code not in ('NET'):
                        if not rubro.salary_rule_id.id in rubros:
                            rubros.append(rubro.salary_rule_id.id)
                if not line.contract_id.budget_id.id in contratos:
                    #aqui deberia tambien buscar entre fechas para colocar
                    item_idsc = budget_item_obj.search(cr, uid, [('budget_post_id','=',line.contract_id.budget_id.budget_post_id.id),
                                                                 ('year_id','=',year_ids[0]),
                                                                 #cambio mario 31 oct 2017
                                                                 #('date_start','<=',this.date_start),('date_end','>=',this.date_start),
                                                                 ('program_id','=',line.contract_id.program_id.id)],limit=1)
                    if not item_idsc:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existen planificacion de partida en el contrato %s para el anio en curso %s") % (line.contract_id.employee_id.complete_name,this.date_start))
                    if not item_idsc[0] in contratos:
                        contratos.append(item_idsc[0])
                    #contratos.append(line.contract_id.budget_id.id)
            #poner el budget_id2 de cada rol en las lineas de rol
#        for programa_id in programas:
            for rubro_id in rubros:
                #if rubro_id==4:
                #    import pdb
                #    pdb.set_trace()
                for contrato_budget_id in contratos:
                    item_contrato = budget_item_obj.browse(cr, uid, contrato_budget_id)
                    rubro = rule_obj.browse(cr, uid, rubro_id)
                    programa_id = item_contrato.program_id.id
                    payslip_line_ids = payslip_line_obj.search(cr, uid, [('program_id','=',programa_id),('budget_id2','=',item_contrato.budget_post_id.id),
                                                                         ('slip_id','in',slip_aux),('salary_rule_id','=',rubro_id)])
#                    if not payslip_line_ids:
#                        payslip_line_ids = payslip_line_obj.search(cr, uid, [('program_id','=',programa_id),('budget_id','=',item_contrato.id),
#                                                                             ('slip_id','in',slip_aux),('salary_rule_id','=',rubro_id)])
                    monto = 0 
                    if payslip_line_ids:
                        config_line = False
                        for line_id in payslip_line_ids:
                            payslip_line = payslip_line_obj.browse(cr, uid, line_id)
                            monto += payslip_line.amount
                        config_ids = config_obj.search(cr, uid, [('rule_id','=',rubro_id)])
#                        config_ids = config_obj.search(cr, uid, [('rule_id','=',rubro_id),('budget_id','=',item_contrato.budget_post_id.id)])
                        budget_id = ''
                        config_line_aux = False
                        if config_ids:
                            for config_line in config_ids:
                                config_aux = config_obj.browse(cr, uid, config_line)
                                if config_aux.budget_id.id == item_contrato.budget_post_id.id:
                                    #print "ENCONTRO EN EL PRIMERO",rubro.name,config_aux.budget_id.code
                                    budget_id = item_contrato.id
                                    config_line_aux = config_line
                                    break
                            #aqui busco ahora con la misma partida
                            #if rubro_id==4:
                            #    import pdb
                            #    pdb.set_trace()
  
                            if not budget_id:
                                conf_1 = config_obj.browse(cr, uid, config_ids[0])
                                aux_code = item_contrato.budget_post_id.code[0] + conf_1.budget_id.code[1:6] + item_contrato.budget_post_id.code[6:]
#                                import pdb
#                                pdb.set_trace()
                                for config_line in config_ids:
                                    conf_aux = config_obj.browse(cr, uid, config_line)#config_ids[0]
                                    item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('budget_post_id.code','=',aux_code),
                                                                                ('aux_tipo','=',item_contrato.budget_post_id.code[0:1]),
                                                                                ('year_id','=',year_ids[0])],limit=1)
                                    if item_ids:
                                        budget_id = item_ids[0]
                                        config_line_aux = config_line
                                        break
                            if not budget_id and rubro.category_id.name=='Egresos':
                                item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('budget_post_id.code','=',item_contrato.budget_post_id.code[6:]),
                                                                            ('aux_tipo','=',item_contrato.budget_post_id.code[0:1]),
                                                                            ('year_id','=',year_ids[0])],limit=1)
                                if item_ids:
                                    budget_id = item_ids[0]
                            if not budget_id:
                                for config_line in config_ids:
                                    conf_aux = config_obj.browse(cr, uid, config_line)#config_ids[0]
                                    partida_name = conf_aux.budget_id.name
                                    partida_name_upper = conf_aux.budget_id.name.upper()
                                    item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('name','in',(partida_name,partida_name_upper)),
                                                                                ('aux_tipo','=',item_contrato.budget_post_id.code[0:1]),
                                                                                ('year_id','=',year_ids[0])],limit=1)
                                                                                #('date_start','<=',this.date_end),('date_end','>=',this.date_end),
                                    if item_ids:
                                        #print "NO ES DE RMU Y TOMA LA PRIMERA Q ENCUENTRA", rubro.name, item_ids
                                        budget_id = item_ids[0]
                                        config_line_aux = config_line
                                        break
                                    else:
                                        item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('code_aux','=',conf_aux.budget_id.code),
                                                                                    ('aux_tipo','=',item_contrato.budget_post_id.code[0:1]),
                                                                                    ('year_id','=',year_ids[0])],limit=1)
                                                                                    #          ('date_start','<=',this.date_end),('date_end','>=',this.date_end)],
                                        if item_ids:
                                            budget_id = item_ids[0]
                                            config_line_aux = config_line
                                            break
                                        else:
                                            #riobamba:
                                            aux_code_proyecto = item_contrato.code[10:] #me da el proyecto
                                            aux_code_ext = item_contrato.budget_post_id.code[0:1]+conf_aux.budget_id.code[1:]+aux_code_proyecto
                                            item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('code_aux','=',aux_code_ext),
                                                                                        ('aux_tipo','=',item_contrato.budget_post_id.code[0:1]),
                                                                                        ('year_id','=',year_ids[0])],limit=1)
                                                                                        #('date_start','<=',this.date_end),('date_end','>=',this.date_end)],
                                            if item_ids:
                                                budget_id = item_ids[0]
                                                config_line_aux = config_line
                                                break
                            if not budget_id:        
                                raise osv.except_osv(('Error de configuracion !'),
                                                     ("No existe partida %s del programa %s en el presupuesto del anio, para el rubro %s") % 
                                                     (item_contrato.budget_post_id.code,item_contrato.program_id.sequence,rubro.name))
                                            #else:
#                                                raise osv.except_osv(('Error de configuracion !'),
#                                                                     ("No existe partida %s del programa %s en el presupuesto del anio, para el rubro %s") % (item_contrato.budget_post_id.code,item_contrato.program_id.sequence,rubro.name))
                            project_ids = project_obj.search(cr, uid, [('program_id','=',programa_id)],limit=1)
                        else:
                            budget_id = contrato_budget_id
                        programa = program_obj.browse(cr, uid, programa_id)
                        aux_pr = programa.sequence + ' - ' + programa.name
                        #cambiar el anio del budget_id
                        budget_actual = budget_item_obj.browse(cr, uid, budget_id)
                        if budget_actual.year_id.id!=year_ids[0]:
                            budget_ids = budget_item_obj.search(cr, uid, [('year_id','=',year_ids[0]),('program_id','=',programa_id),
                                                                   ('budget_post_id','=',budget_actual.budget_post_id.id)])
                            if budget_ids:
                                budget_id=budget_ids[0]
                        detalle_id = detalle_obj.create(cr, uid, {
                            'run_id':id_this,
                            'programa_id':programa_id,
                            'rubro_id':rubro_id,
                            'partida_id':budget_id,
                            'monto':monto,
#                            'config_id':config_line_aux,
                        })
                        budget_id = False
            self._create_move_tthh(cr, uid, ids)
        return True

    def asiento_payslip_run(self, cr, uid, ids, context={}):
        self._create_move_tthh(cr, uid, ids)
        return True

    def calcular_asiento(self, cr, uid, ids, context={}):
        obj_configuration = self.pool.get('hr.account.configuration')
        obj_account = self.pool.get('hr.payslip.account')
        detalle = {}
        for rol_general in self.browse(cr, uid, ids, context):
            #procedemos a eliminar la antigua informacion de este registro
            detalle_ids = obj_account.search(cr, uid, [('payslip_id','=',rol_general.id)])
            if detalle_ids:
                obj_account.unlink(cr, uid, detalle_ids, context)
            #procedemos a la creacion de la nueva informacion contable
            for rol_individual in rol_general.slip_ids:
                for linea_rol in rol_individual.line_ids:
                    if linea_rol.category_id.code in ('BASIC','ING','GROSS','EGR','NET'):
                        configuration_id = obj_configuration.search(cr, uid, [('rule_id','=',linea_rol.salary_rule_id.id),
                                                                              ('project_id','=',linea_rol.contract_id.project_id.id)])
                        if configuration_id:
                            configuration = obj_configuration.browse(cr, uid, configuration_id[0], context)
                            if linea_rol.category_id.code in ('BASIC','ING','GROSS'):
                                obj_account.create(cr, uid, {'payslip_id': rol_general.id,
                                                             #'code': item['description'].code,
                                                             'description': configuration.expense_account_id.id,
                                                             'budget_id': configuration.budget_line_id.id,
                                                             'project_id': configuration.project_id.id,
                                                             'debe': linea_rol.total,
                                                             'haber': 0,}, context)
                                if configuration.expense_account_id.account_comp_id:
                                    if configuration.expense_account_id.account_comp_id.account_comp_id:
                                        obj_account.create(cr, uid, {'payslip_id': rol_general.id,
                                                                     'description': configuration.expense_account_id.account_comp_id.id,
                                                                     'debe': 0,
                                                                     'haber': linea_rol.total,}, context)
                                        obj_account.create(cr, uid, {'payslip_id': rol_general.id,
                                                                     'description': configuration.expense_account_id.account_comp_id.account_comp_id.id,
                                                                     'debe': linea_rol.total,
                                                                     'haber': 0,}, context)
                            if linea_rol.category_id.code in ('EGR','NET'):
                                obj_account.create(cr, uid, {'payslip_id': rol_general.id,
                                                             #'code': item['description'].code,
                                                             'description': configuration.expense_account_id.id,
                                                             #'budget_id': configuration.budget_line_id.id,
                                                             #'project_id': configuration.project_id.id,
                                                             'debe': 0,
                                                             'haber': linea_rol.total,}, context)
                        else:
                            raise osv.except_osv("Error !", "No se encuentra configurada la seccion contable para el rubro '" + str(linea_rol.salary_rule_id.name) + "' y el proyecto '" + str(linea_rol.contract_id.project_id.name) + "'")
        return True
                        
    
    def calcular_asiento_anterior(self, cr, uid, ids, context=None):
        obj_configuration = self.pool.get('hr.account.configuration')
        obj_account = self.pool.get('hr.payslip.account')
        #'rule_id': fields.many2one('hr.salary.rule', 'Rubro'),
        #'project_id': fields.many2one('project.project', 'Proyecto'),
        detalle = {}
        for rol_general in self.browse(cr, uid, ids, context):
            #procedemos a eliminar la antigua informacion de este registro
            detalle_ids = obj_account.search(cr, uid, [('payslip_id','=',rol_general.id)])
            if detalle_ids:
                obj_account.unlink(cr, uid, detalle_ids, context)
            #procedemos a la creacion de la nueva informacion contable
            for rol_individual in rol_general.slip_ids:
                for linea_rol in rol_individual.line_ids:
                    if linea_rol.category_id.code in ('BASIC','ING','GROSS','EGR','NET'):
                        configuration_id = obj_configuration.search(cr, uid, [('rule_id','=',linea_rol.salary_rule_id.id),
                                                                              ('project_id','=',linea_rol.contract_id.project_id.id)])
                        if configuration_id:
                            configuration = obj_configuration.browse(cr, uid, configuration_id[0], context)
                            if linea_rol.category_id.code in ('BASIC','ING','GROSS'):
                                if detalle.has_key(configuration.pay_account_id.id):
                                    detalle[configuration.pay_account_id.id]={'description':configuration.pay_account_id,
                                                                              'debe':detalle[configuration.pay_account_id.id]['debe']+linea_rol.total,
                                                                              'haber':detalle[configuration.pay_account_id.id]['haber']+0}
                                else:
                                    detalle[configuration.pay_account_id.id]={'description':configuration.pay_account_id,
                                                                              'debe':linea_rol.total,
                                                                              'haber':0}
                            if linea_rol.category_id.code in ('EGR','NET'):
                                if detalle.has_key(configuration.expense_account_id.id):
                                    detalle[configuration.expense_account_id.id]={'description':configuration.expense_account_id,
                                                                                  'debe':detalle[configuration.expense_account_id.id]['debe']+0,
                                                                                  'haber':detalle[configuration.expense_account_id.id]['haber']+linea_rol.total}
                                else:
                                    detalle[configuration.expense_account_id.id]={'description':configuration.expense_account_id,
                                                                                  'debe':0,
                                                                                  'haber':linea_rol.total}
                        else:
                            raise osv.except_osv("Error !", "No se encuentra configurada la seccion contable para el rubro '" + str(linea_rol.salary_rule_id.name) + "' y el proyecto '" + str(linea_rol.contract_id.project_id.name) + "'")
            if detalle:
                for item in detalle.values():
                    obj_account.create(cr, uid, {'payslip_id': rol_general.id,
                                                 #'code': item['description'].code,
                                                 'description': item['description'].id,
                                                 'debe': item['debe'],
                                                 'haber': item['haber'],}, context)
        return True
    
    def crear_asiento(self, cr, uid, ids, context={}):
        obj_account_move = self.pool.get("account.move")
        obj_account_move_line = self.pool.get("account.move.line")
        for rol_general in self.browse(cr, uid, ids, context):
            move_id = obj_account_move.create(cr, uid, {'ref': rol_general.name,
                                                        'journal_id': rol_general.journal_id.id,
                                                        'date': time.strftime("%Y-%m-%d"),
                                                        'state':'draft'}, context=context)
            for asiento_calculado in rol_general.payslip_account_ids:
                
                move_line_id = obj_account_move_line.create(cr, uid, {'name': rol_general.name,
                                                                      'move_id': move_id,
                                                                      'account_id': asiento_calculado.description.id,
                                                                      'analytic_account_id': asiento_calculado.project_id.id,
                                                                      'budget_id': asiento_calculado.budget_id.id,
                                                                      'debit': asiento_calculado.debe,
                                                                      'credit': asiento_calculado.haber,
                                                                      'state':'draft'})
            self.write(cr, uid, [rol_general.id], {'account_move_id':move_id}, context=context)
            return True
        return True
    
    
hr_inherit_payslip_account()

class clonaRubro(osv.TransientModel):
    _name = 'clona.rubro'
    _columns = dict(
        rubro_o = fields.many2one('hr.salary.rule','Rubro a clonar'),
        rubro_d = fields.many2one('hr.salary.rule','Rubro nuevo'),
    )

    def clonaRubro(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.account.configuration')
        contract_obj = self.pool.get('hr.contract')
        for this in self.browse(cr, uid, ids):
            contract_ids = contract_obj.search(cr, uid, [('activo','=',True)])
            if contract_ids:
                for contract_id in contract_ids:
                    lineas_contrato = []
                    contract = contract_obj.browse(cr, uid, contract_id)
                    for config_line in contract.config_rubro_ids:
                        lineas_contrato.append(config_line.id)
                        if config_line.rule_id.id==this.rubro_o.id:
                            line_creada_id = line_obj.create(cr, uid, {
                                'rule_id':this.rubro_d.id,
                                'pay_account_id':config_line.pay_account_id.id,
                                'expense_account_id':config_line.expense_account_id.id,
                                'budget_id':config_line.budget_id.id,
                            })
                            lineas_contrato.append(line_creada_id)
                    contract_obj.write(cr, uid, contract_id,{'config_rubro_ids':[(6,0,lineas_contrato)]})
#            line_ids = line_obj.search(cr, uid, [('rule_id','=',this.rubro_o.id)])
##            line_d_ids = line_obj.search(cr, uid, [('rule_id','=',this.rubro_d.id)])
#            if line_ids and not line_d_ids:
#                for line_id in line_ids:
#                    linea = line_obj.browse(cr, uid, line_id)
#                    line_creada_id = line_obj.create(cr, uid, {
#                        'rule_id':this.rubro_d.id,
#                        'pay_account_id':linea.pay_account_id.id,
#                        'expense_account_id':linea.expense_account_id.id,
#                        'budget_id':linea.budget_id.id,
#                    })
        return {'type': 'ir.actions.act_window_close'}

clonaRubro()


class clonaContrato(osv.TransientModel):
    _name = 'clona.contrato'
    _columns = dict(
        contract_id = fields.many2one('hr.contract','Contrato A Clonar'),
        contract_nuevo_id = fields.many2one('hr.contract','Contrato Nuevo'),
    )

    def clonaContrato(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.account.configuration')
        contract_obj = self.pool.get('hr.contract')
        post_obj = self.pool.get('budget.post')
        for this in self.browse(cr, uid, ids):
            lineas_contrato = []
            if not this.contract_id.config_rubro_ids:
                raise osv.except_osv('Error de usuario', 'El contrato a clonar no tiene configuradas cuentas')
            for line_id in this.contract_id.config_rubro_ids:
                budget_clona_code = this.contract_id.budget_id.budget_post_id.code[0:6]
                if budget_clona_code==this.contract_nuevo_id.budget_id.budget_post_id.code[0:6]:
                    budget_id = this.contract_nuevo_id.budget_id.budget_post_id.id
                else:
                    budget_clona_code = line.budget_id.code[0:6] + this.contract_nuevo_id.budget_id.budget_post_id.code[6:]
                    post_ids = post_obj.search(cr, uid, [('code','=',budget_clona_code)])
                    if post_ids:
                        budget_id = post_ids[0]
                    else:
                        raise osv.except_osv('Error de usuario', 'El rubro no tiene partida')
                line_creada_id = line_obj.create(cr, uid, {
                    'rule_id':line_id.rule_id.id,
                    'pay_account_id':line_id.pay_account_id.id,
                    'expense_account_id':line_id.expense_account_id,
                    'budget_id':budget_id,
                })
                lineas_contrato.append(line_creada_id)
                contract_obj.write(cr, uid, contract_nuevo_id,{'config_rubro_ids':[(6,0,lineas_contrato)]})
        return {'type': 'ir.actions.act_window_close'}

clonaContrato()

class paramRubro(osv.TransientModel):
    _name = 'param.rubro'
    _columns = dict(
        cgasto = fields.many2one('account.account','Cuenta Gasto'),
        cxc = fields.many2one('account.account','Cuenta Pagar'),
        rubro_ids = fields.many2many('hr.salary.rule','p_r_id','p_id','r_id','Rubros'),
        otro = fields.char('Otra Partida',size=6),
        tipo = fields.selection([('5','5'),('7','7')],'Tipo'),
        opc_pat = fields.boolean('Opcion Patrimonial'),
        rol_id = fields.many2one('hr.payslip.run','Rol'),
    )

    def paramRubro(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.account.configuration')
        contract_obj = self.pool.get('hr.contract')
        post_obj = self.pool.get('budget.post')
        account_obj = self.pool.get('account.account')
        rol_id = self.pool.get('hr.payslip')
        for this in self.browse(cr, uid, ids):
            rubro_ids = this.rubro_ids
            if this.rol_id:
                contract_ids = []
                for rol_ind_id in this.rol_id.slip_ids:
                    contract_ids.append(rol_ind_id.contract_id.id)
                    if not this.rubro_ids:
                        rubro_ids = []
                        for rol_line in rol_ind_id.line_ids:
                            if not rol_line.salary_rule_id in rubro_ids and rol_line.salary_rule_id.category_id.code!='NET':
                                rubro_ids.append(rol_line.salary_rule_id)
            else:
                contract_ids = contract_obj.search(cr, uid, [('activo','=',True)])
            if not rubro_ids:
                raise osv.except_osv('Error de usuario', 'Debe seleccionar el rol o los rubros a configurar')
            if contract_ids:
                for contract_id in contract_ids:
                    lineas_contrato = []
                    contrato = contract_obj.browse(cr, uid, contract_id)
                    for line_ant in contrato.config_rubro_ids:
                        lineas_contrato.append(line_ant.id)
                    if not contrato.budget_id.budget_post_id.code[0]==this.tipo:
                        continue
                    for rubro in rubro_ids:
                        if this.otro:
                            aux_code = this.otro+contrato.budget_id.budget_post_id.code.replace('.','')[6:]
                            budget_ids = post_obj.search(cr, uid, [('code','=',aux_code)])
                            if budget_ids:
                                budget_id = budget_ids[0]
                            else:
                                print "NOOOOOOOOOOOOOOOOOOOOO",contrato.employee_id.complete_name,rubro.name
                        else:
                            budget_id = contrato.budget_id.budget_post_id.id
#                        line_ids = line_obj.search(cr, uid, [('rule_id','=',rubro.id),('pay_account_id','=',this.cxc.id),('expense_account_id','=',this.cgasto.id),
#                                                             ('budget_id','=',budget_id)])
                        line_ids = line_obj.search(cr, uid, [('rule_id','=',rubro.id),('budget_id','=',budget_id)])
                        #if line_ids:
                        #    line_obj.unlink(cr, uid, line_ids)
                        aux_gasto = this.cgasto.id
                        if not this.cgasto:
                            acc_expense_ids = account_obj.search(cr, uid, [('budget_id','=',budget_id)])
                            if acc_expense_ids:
                                aux_gasto = acc_expense_ids[0]
                        #if this.opc_pat:
                        #    account_gasto_ids = account_obj.search(cr, uid, [('','',)])
                        if not line_ids:
                            line_creada_id = line_obj.create(cr, uid, {
                                'rule_id':rubro.id,
                                'pay_account_id':this.cxc.id,
                                'expense_account_id':aux_gasto,
                                'budget_id':budget_id,
                            })
                            lineas_contrato.append(line_creada_id)
                        else:
                            line_obj.write(cr, uid, line_ids,{
                                'rule_id':rubro.id,
                                'pay_account_id':this.cxc.id,
                                'expense_account_id':aux_gasto,
                                'budget_id':budget_id,
                            })
                            band_c = False
                            for line_contrato in contrato.config_rubro_ids:
                                if line_contrato.rule_id.id==rubro.id:
                                    band_c=True
                            if not band_c:
                                lineas_contrato.append(line_ids[0])
                            #line_creada_id = line_ids[0]
                        if not this.cgasto.account_rec_id:
                            account_obj.write(cr, uid, this.cgasto.id,{'account_rec_id':this.cxc.id,})
                    if lineas_contrato:
                        contract_obj.write(cr, uid, contract_id,{'config_rubro_ids':[(6,0,lineas_contrato)]})
                                
        return {'type': 'ir.actions.act_window_close'}

paramRubro()
