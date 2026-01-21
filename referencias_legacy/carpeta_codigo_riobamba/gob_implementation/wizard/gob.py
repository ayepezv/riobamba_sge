# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo: mariofchogllo@gmail.com
#
##############################################################################

import time

from osv import osv
from osv import fields
import base64
import pooler
from XLSWriter import XLSWriter
import StringIO
import xlrd
from tools import ustr
import netsvc
import unicodedata
import re

class writeMove(osv.TransientModel):
    _name = 'write.move'
    _columns = dict(
        name = fields.many2one('account.move','Asiento'),
    )

    def writeRecauda(self, cr, uid, ids, context):
        rec_line_obj = self.pool.get('recaudacion.line')
        for this in self.browse(cr,uid, ids):
            line_ids = rec_line_obj.search(cr, uid,[])
            if line_ids:
                for line_id in line_ids:
                    rec_line_obj.write(cr, uid, line_id,{'updated':True,})
        return True

    def writeLine(self, cr, uid, ids, context):
        move_line_obj = self.pool.get('account.move.line')
        for this in self.browse(cr,uid, ids):
            if this.name:
                for line in this.name.line_id:
                    move_line_obj.write(cr, uid, line.id,{'updated':True})
        return True
writeMove()
class ajustaInventario(osv.TransientModel):
    _name = 'ajusta.inventario'
    _columns = dict(
        categ_id = fields.many2one('product.category','Categoria'),
        monto = fields.float('Monto'),
        archivo = fields.binary('Archivo', required=True),
    )

    def corrijeInventario(self, cr, uid, ids, context):
        product_obj = self.pool.get('product.product')
        move_obj = self.pool.get('stock.move')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                aux_code = ustr(sh.cell(r,3).value)
                code_punto = aux_code[0:1] + '.' + aux_code[1:]
                product_ids = product_obj.search(cr, uid, [('categ_id','=',data['categ_id'][0]),('default_code','=',code_punto)])
                if product_ids:
                    producto = product_obj.browse(cr, uid, product_ids[0])
                    if producto.standard_price<=0:
                        aux_precio = sh.cell(r,12).value
                        product_obj.write(cr, uid, producto.id,{
                            'standard_price':aux_precio,
                        })
                        move_line_ids = move_obj.search(cr, uid, [('product_id','=',producto.id),('picking_id','=',1940),('type','=','out')])
                        if move_line_ids:
                            if len(move_line_ids)>1:
                                print "hay mas de dos", producto.default_code
                            else:
                                move = move_obj.browse(cr, uid, move_line_ids[0])
                                total_aux = float(aux_precio) * move.product_qty
                                move_obj.write(cr, uid, move_line_ids[0],{'price_unit':aux_precio,
                                                                          'total':total_aux,
                                                                          'subtot':total_aux,
                                                                          'subtotal':aux_precio,
                                                                      })
                else:
                    print "No producto"
                    import pdb
                    pdb.set_trace()
        return True

    def ajustarInventario(self, cr, uid, ids, context):
        product_obj = self.pool.get('product.product')
        for this in self.browse(cr, uid, ids):
            product_ids = product_obj.search(cr, uid, [('categ_id','=',this.categ_id.id),('qty_available','>',0)])
            if product_ids:
                total = 0
                for product_id in product_ids:
                    producto = product_obj.browse(cr, uid, product_id)
                    subtotal_producto = producto.standard_price * producto.qty_available
                    total += subtotal_producto
                factor = total / this.monto
                for product_id in product_ids:
                    producto = product_obj.browse(cr, uid, product_id)
                    product_ant = producto.standard_price
                    subtotal_producto = producto.standard_price * producto.qty_available
                    sumar_producto = subtotal_producto / factor
                    total_producto = subtotal_producto + sumar_producto
                    new_price = total_producto / producto.qty_available
                    product_obj.write(cr, uid, product_id,{'standard_price':new_price,'p_a':product_ant})
        return True

ajustaInventario()

class ajustaBudget(osv.TransientModel):
    _name = 'ajusta.budget'

    def _checkPass(self, cr, uid, ids): 
        result = False
        for this in self.browse(cr, uid, ids):
            if this.password=='m123456':
                result = True
        return result

    _constraints = [
        (_checkPass,
         ustr('No pass.'),[ustr('Pass'), 'Pass'])
    ]

    _columns = dict(
        move_id = fields.many2one('account.move','Comprobante'),
        password = fields.char('Pass',size=10),
        item_origen  = fields.many2one('budget.item','Partida O'),
        comprometido_o = fields.float('Comp. O'),
        devengado_o = fields.float('Dev. O'),
        pagado_o = fields.float('Pag. O'),
        item_destino  = fields.many2one('budget.item','Partida D'),
        comprometido_d = fields.float('Comp. D'),
        devengado_d = fields.float('Dev. D'),
        pagado_d = fields.float('Pag. D'),
        date = fields.date('Fecha'),
    )

    def ajustaComprometido(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        lista_comp = {}
        lista_dev = {}
        lista_pag = {}
        for this in self.browse(cr, uid, ids):
            if this.move_id:
                for line_certificate in this.move_id.certificate_id.line_ids:
                    if not line_certificate.budget_id.id in lista_comp:
                        lista_comp[line_certificate.budget_id.id]=line_certificate.amount_commited
                    else:
                        lista_comp[line_certificate.budget_id.id]+=line_certificate.amount_commited
                for line_asiento in this.move_id.line_id:
                    if line_asiento.budget_accrued:
                        aux_amount = 0
                        aux_amount = line_asiento.debit + line_asiento.credit
                        if not line_asiento.budget_id.id in lista_dev:
                            lista_dev[line_asiento.budget_id.id]=aux_amount
                        else:
                            lista_dev[line_asiento.budget_id.id]+=aux_amount
            for lista_comp_line in lista_comp:
                diferencia = lista_dev[lista_comp_line] - lista_comp[lista_comp_line]
                if diferencia>0:
                    certificate_line_ids = certificate_line_obj.search(cr, uid, [('certificate_id','=',this.move_id.certificate_id.id),
                                                                                 ('budget_id','=',lista_comp_line)])
                    if certificate_line_ids:
                        certificate_line = certificate_line_obj.browse(cr, uid, certificate_line_ids[0])
                        amount_ant = certificate_line.amount_commited
                        amount_new = amount_ant + diferencia
                        certificate_line_obj.write(cr, uid, certificate_line_ids[0],{
                            'amount':amount_new,
                            'amount_certified':amount_new,
                            'amount_commited':amount_new,
                        })
                elif diferencia<0:
                    print "esta menor a cero", lista_comp_line
                else:
                    print "no  hay diferencia"
        return True
                

    def cambiarPartidaAsiento(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        cert_line_obj = self.pool.get('budget.certificate.line')
        for this in self.browse(cr, uid, ids):
            move_line_ids = move_line_obj.search(cr, uid, [('move_id','=',this.move_id.id),('budget_id','=',this.item_origen.id)])
            if move_line_ids:
                for move_line_id in move_line_ids:
                    cert_line_ids = cert_line_obj.search(cr, uid, [('certificate_id','=',this.move_id.certificate_id.id),('budget_id','=',this.item_destino.id)])
                    if cert_line_ids:
                        move_line_obj.write(cr, uid, move_line_id,{
                            'budget_id_cert':cert_line_ids[0],
                            'budget_id':this.item_destino.id,
                            'budget_post':this.item_destino.budget_post_id.id,
                        })
        return True

    def ajustarItemMigrated(self, cr, uid, ids, context=None):
        item_migrated_obj = self.pool.get('budget.item.migrated')
        for this in self.browse(cr, uid, ids):
            if this.item_origen:
                if not (this.item_origen.date_start<=this.date and this.item_origen.date_end>=this.date):
                    raise osv.except_osv(('Error!'),'Verificar fechas')
                item_migrated_obj.create(cr, uid, {
                    'budget_item_id':this.item_origen.id,
                    'type_budget':this.item_origen.type_budget,
                    'code':this.item_origen.budget_post_id.code,
                    'date':this.date,
                    'name':this.item_origen.budget_post_id.name,
                    'budget_post_id':this.item_origen.budget_post_id.id,
                    'program_code':this.item_origen.program_id.sequence,
                    'commited_amount':this.comprometido_o,
                    'devengado_amount':this.devengado_o,
                    'paid_amount':this.pagado_o,
                })
            if this.item_destino:
                if not (this.item_destino.date_start<=this.date and this.item_destino.date_end>=this.date):
                    raise osv.except_osv(('Error!'),'Verificar fechas')
                item_migrated_obj.create(cr, uid, {
                    'budget_item_id':this.item_destino.id,
                    'type_budget':this.item_destino.type_budget,
                    'code':this.item_destino.budget_post_id.code,
                    'date':this.date,
                    'name':this.item_destino.budget_post_id.name,
                    'budget_post_id':this.item_destino.budget_post_id.id,
                    'program_code':this.item_destino.program_id.sequence,
                    'commited_amount':this.comprometido_d,
                    'devengado_amount':this.devengado_d,
                    'paid_amount':this.pagado_d,
                })
        return True
        
ajustaBudget()
class updateRol(osv.TransientModel):
    _name = 'update.rol'
    _columns = dict(
        desc = fields.selection([('total','total'),('recompute','recompute')],'Tipo'),
        period_id = fields.many2one('hr.work.period.line','Periodo'),
        tipo_id = fields.many2many('hr.payroll.structure','r_s_id','r_id','s_id','Tipo'),
#        tipo_id = fields.many2one('hr.payroll.structure','Tipo'),
        archivo = fields.binary('Archivo'),
    )

    def updateBudgetInd(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                aux_cedula = ustr(sh.cell(r,0).value)
                emp_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)],limit=1)
                if emp_ids:
                    contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp_ids[0])])
                    if contract_ids:
                        contract_obj.write(cr, uid, contract_ids[0],{
                            'budget_ind':ustr(sh.cell(r,5).value),
                        })
        return True
                        

    def updatePartnerName(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                if len(ustr(sh.cell(r,21).value))>0 and len(ustr(sh.cell(r,20).value))>0:
                    aux_cedula = ustr(sh.cell(r,0).value)
                    aux_num_cuenta = str(int(sh.cell(r,20).value))
                    emp_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)],limit=1)
                    if emp_ids:
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedula)])
                        if partner_ids:
                            partner = partner_obj.browse(cr, uid, partner_ids[0])
                            if partner.bank_ids:
                                for bank in partner.bank_ids:
                                    if str(int(bank.acc_number)) != aux_num_cuenta:
                                        print "CUENTA DIFERETE", aux_cedula
                            aux_name = ustr(sh.cell(r,2).value) + ' ' + ustr(sh.cell(r,3).value)
                            partner_obj.write(cr, uid, partner_ids[0],{
                                'name':aux_name,
                            })
                        else:
                            print "NO PARTNER", aux_cedula
                    else:
                        print "No empleado", aux_cedula
        return True

    def update_wage(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        hist_obj = self.pool.get('hr.hist.wage')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                aux_cedula = ustr(sh.cell(r,0).value)
                emp_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)],limit=1)
                if emp_ids:
                    contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp_ids[0])],limit=1)
                    if contract_ids:
                        contrato=contract_obj.browse(cr, uid, contract_ids[0])
                        contract_obj.write(cr, uid, contract_ids[0],{
                            'wage':sh.cell(r,1).value,
                        })
                        hist_obj.create(cr, uid, {
                            'name':time.strftime('%Y-%m-%d'),
                            'wage':contrato.wage,
                            'new_wage':sh.cell(r,1).value, 
                            'contract_wage_id':contrato.id,
                        })
                    else:
                        print "NO CONTRATO DE EMPLEADO", aux_cedula
                else:
                    print "NO EMPLEADO DE CEDULA", aux_cedula
        else:
            print "NO ARCHIVO"
        return True

    def recompute_rolgob(self, cr, uid, ids, context=None):
        rol_obj = self.pool.get('hr.payslip')
        line_obj = self.pool.get('hr.payslip.line')
        for this in self.browse(cr, uid, ids):
            for tipo_id in this.tipo_id:
                roles_ids = rol_obj.search(cr, uid, [('period_id','=',this.period_id.id),('struct_id','=',tipo_id.id)])
                if this.desc=='recompute':
                    if roles_ids:
                        print "TOATL RLE", len(roles_ids)
                        for rol_id in roles_ids:
                            rol_obj.compute_sheet(cr, uid, [rol_id],context=context)
                    else:
                        print "NO ROLES"
                elif this.desc=='total':
                    if roles_ids:
                        for rol_id in roles_ids:
                            aux_sum = aux_resta = aux_total = 0
                            total_ids = line_obj.search(cr, uid, [('slip_id','=',rol_id),('name','=','TOTAL')])
                            rol = rol_obj.browse(cr, uid, rol_id)
                            for line in rol.line_ids:
                                if line.category_id.code=='BASIC':
                                    aux_sum += line.total
                                if line.category_id.code=='EGR':
                                    aux_resta += line.total
                                if line.category_id.code in ('APT','ING'):
                                    aux_sum += line.total
                            aux_total = aux_sum - aux_resta
                            line_obj.write(cr, uid, total_ids[0],{
                                'total':aux_total,
                                'amount':aux_total,
                            })
                            print "Modif total"
        return True

updateRol()
 
class updateGob(osv.osv_memory):
    _name = 'update.gob'

    #scripts Milagro

    def loadUsers(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        employee_obj = self.pool.get('hr.employee')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                aux_ced = sh.cell(r,1).value
                employee_ids = employee_obj.search(cr, uid, [('name','=',aux_ced)])
                if employee_ids:
                    employee = employee_obj.browse(cr, uid, employee_ids[0])
                    if not employee.user_id:
                        user_ids = user_obj.search(cr, uid, [('employee_id','=',employee_ids[0])])
                        if not user_ids:
                            user_obj.create(cr, uid, {
                                'employee_id':employee_ids[0],
                                'job_id':employee.job_id.id,
                                'context_department_id':employee.department_id.id,
                                #'login':,
                            })
        return True
                

    def colocaFinancia(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        for this in self.browse(cr, uid, ids):
            move_ids = move_obj.search(cr, uid, [('date','=',this.date),('type','=','Nomina')])
            if move_ids:
                move_line_ids = move_line_obj.search(cr, uid, [('move_id','in',move_ids),('budget_accrued','=',True)])
                if move_line_ids:
                    for move_line_id in move_line_ids:
                        move_line = move_line_obj.browse(cr, uid, move_line_id)
                        move_line_obj.write(cr, uid, move_line_id,{'financia_id':move_line.budget_id_cert.financia_id.id})
        return True

    def ajustaItemRio(self, cr, uid, ids, context=None):
        item_obj = self.pool.get('budget.item')
        migrated_obj = self.pool.get('budget.item.migrated')
        for this in self.browse(cr, uid, ids):
            context = {'by_date':True,'date_start': '2017-01-01', 'date_end': this.date,'poa_id':4}            
            aux_code = '710510%'
            item_ids = item_obj.search(cr, uid, [('code_aux','=like',aux_code),('poa_id','=',4)])
            if item_ids:
                for line in item_obj.browse(cr,uid,item_ids, context=context):
                    if line.paid_amount!=line.devengado_amount:
                        aux = line.devengado_amount - line.paid_amount
                        migrated_obj.create(cr, uid, {
                            'code':line.budget_post_id.code,
                            'budget_post_id':line.budget_post_id.id,
                            'type_budget':'gasto',
                            'date':this.date,
                            'name':line.budget_post_id.name,
                            'paid_amount':aux,
                            'program_code':line.program_id.sequence,
                            'budget_item_id':line.id,
                            'is_pronto':False,
                        })
        return True

    def loadConcilia(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('mark.line')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                aux_amount = sh.cell(r,8).value
                aux_numero = sh.cell(r,4).value
                aux_partner = sh.cell(r,5).value
                line_ids = line_obj.search(cr, uid, [('comprobante','=',aux_numero),('amount','=',aux_amount)])
                aux_ref = str(sh.cell(r,12))
                aux_ref2 = sh.cell(r,12).value
                aux_date = str(sh.cell(r,7))[7:17]
                aux_date2 = aux_date[3:5]+'/'+aux_date[0:2]+'/'+aux_date[6:]
                if line_ids:
                    print "YA REGISTRADO", aux_ref
                    line_obj.write(cr, uid, line_ids[0],{
                        'name':aux_ref2,
                    })
                else:
                    line_id = line_obj.create(cr, uid, {
                        'comprobante':aux_numero,
                        'name':aux_ref2,
                        'partner_id':sh.cell(r,5).value,
                        'amount':sh.cell(r,8).value,
                        'date':aux_date2,
                    })

    def loadSpi(self, cr, uid, ids, context=None):
        account_id = 16316
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        spi_line_obj = self.pool.get('spi.line')
        date_aux = '2017-01-01'
#        move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id),('move_id.state','=','posted'),('date','>=',date_aux)])
#        if move_line_ids:
#            for move_line_id in move_line_ids:
#                move_line = move_line_obj.browse(cr, uid, move_line_id)
#                spi_line_ids = spi_line_obj.search(cr, uid, [('move_id','=',move_line.move_id.id)])
#                if spi_line_ids:
#                    spi_line = spi_line_obj.browse(cr, uid, spi_line_ids[0])
#                    move_line_obj.write(cr, uid, move_line_id,{'spi_numero':spi_line.spi_id.ref})
        spi_lines_2 = spi_line_obj.search(cr, uid, [('date','>=',date_aux)])
#        spi_lines_2 = [5380]
        if spi_lines_2:
            for spi_2 in spi_lines_2:
                spi_line = spi_line_obj.browse(cr, uid, spi_2)
                aux_move = spi_line.name[5:10]
                move_ids = move_obj.search(cr, uid, [('name','=',aux_move),('date','>=',date_aux),('journal_id','=',5)])
                if move_ids:
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id),('move_id','=',move_ids[0])])
                    if  move_line_ids:
                        move_line_obj.write(cr, uid, move_line_ids[0],{'spi_numero':spi_line.spi_id.ref})
        return True

    def recuperaDepreciacion(self, cr, uid, ids, context=None):
        log_obj = self.pool.get('log.deprecia')
        detalle_obj = self.pool.get('deprecia.activo.det')
        log_ids = log_obj.search(cr, uid, [('date','>=','2017-12-12'),('date','<=','2017-12-31')])
        categoria = {}
        if log_ids:
            for log_id in log_ids:
                log = log_obj.browse(cr, uid, log_id)
                #detalle_obj.create(cr, uid, {
                #    'asset_id':,
                #    'amount':,
                #}) 
        return True

    def recomputeFinalRiobamba(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        aux_date = '2016-01-01'
#        asset_ids = asset_obj.search(cr, uid, [('type','=','Larga Duracion'),('purchase_date','>=',aux_date)])
#        for asset_id in asset_ids:
#            asset_obj.compute_depreciation_board(cr, uid, [asset_id])
        asset_ids2 = asset_obj.search(cr, uid, [('type','=','Larga Duracion'),('category_id','in',(4,8))])
        print "ACTIVOS", len(asset_ids2)
        for asset_id in asset_ids2:
            asset_obj.compute_depreciation_board(cr, uid, [asset_id])
        return True

    def recomputeFinalRiobamba2(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        aux_date = '2016-01-01'
        asset_ids = asset_obj.search(cr, uid, [('type','=','Larga Duracion'),('purchase_date','<=',aux_date)])
        for asset_id in asset_ids:
            asset_obj.compute_depreciation_board(cr, uid, [asset_id])
        return True

    def divide2016(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        dep_line_obj = self.pool.get('account.asset.depreciation.line')
        lineas_dep_ids = dep_line_obj.search(cr, uid, [('asset_id.type','=','Larga Duracion'),
                                                       ('depreciation_date','>=','2016-01-01'),('depreciation_date','<=','2016-12-31')])
        if lineas_dep_ids:
            for lineas_dep_id in lineas_dep_ids:
                linea = dep_line_obj.browse(cr, uid, lineas_dep_id)
                asset = asset_obj.browse(cr, uid, linea.asset_id.id)
                total_2016 = asset.value_residual - asset.depreciacion
                line_despues_2016 = dep_line_obj.search(cr, uid, [('asset_id','=',asset.id),('depreciation_date','>=','2016-01-01')])
                promedio = 0
                if line_despues_2016:
                    promedio = total_2016/len(line_despues_2016)
                    dep_line_obj.write(cr, uid, line_despues_2016,{'amount':promedio,})
        return True

    def divide2015(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        dep_line_obj = self.pool.get('account.asset.depreciation.line')
        lineas_dep_ids = dep_line_obj.search(cr, uid, [('asset_id.type','=','Larga Duracion'),
                                                       ('depreciation_date','>=','2015-01-01'),('depreciation_date','<=','2015-12-31')])
        if lineas_dep_ids:
            for lineas_dep_id in lineas_dep_ids:
                linea = dep_line_obj.browse(cr, uid, lineas_dep_id)
                promedio = 0
                asset = asset_obj.browse(cr, uid, linea.asset_id.id)
                total_2015 = asset.depreciacion
                line_antes_2015 = dep_line_obj.search(cr, uid, [('asset_id','=',asset.id),('depreciation_date','<=','2016-01-01')])
                if line_antes_2015:
                    promedio = total_2015/len(line_antes_2015)
                    dep_line_obj.write(cr, uid, line_antes_2015,{'amount':promedio,})
        return True

    def recompute2015(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
#        lista_activos = [34744,32077]
#        for asset_id in lista_activos:
#            asset_obj.compute_depreciation_board(cr, uid, [asset_id])
        sql_aux = '''select id from account_asset_asset where purchase_date<='2015-12-31' and type='Larga Duracion' and depreciacion<value_residual'''
        cr.execute(sql_aux)
        result = cr.fetchall()
        for asset_id in result:
            asset_obj.compute_depreciation_board(cr, uid, [asset_id[0]])
        return True

    def regresa2015(self, cr, uid, ids, context=None):
        log_obj = self.pool.get('log.deprecia')
        asset_obj = self.pool.get('account.asset.asset')
        log_ids = log_obj.search(cr, uid, [('asset_id.type','=','Larga Duracion')])
        if log_ids:
            for log_id in log_ids:
                log = log_obj.browse(cr, uid, log_id)
                asset_obj.write(cr, uid, log.asset_id.id,{
                    'depreciacion':log.anterior,
                })
        return True

    def ajustaDepLast(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        dep_line_obj = self.pool.get('account.asset.depreciation.line')
        asset_ids = asset_obj.search(cr, uid, [('purchase_date','<=','2016-01-01'),('type','=','Larga Duracion'),
                                               ('state','=','open'),('purchase_date','>=','2000-01-01')])
        print "total activos", len(asset_ids)
#        asset_ids = [32077]
        if asset_ids:
            for asset_id in asset_ids:
                asset = asset_obj.browse(cr, uid, asset_id)
                dep_2015 = 0
                if asset.log_ids:
                    dep_2015 = asset.depreciacion - asset.log_ids[0].valor
                    line_dep_2015_ids = dep_line_obj.search(cr, uid, [('asset_id','=',asset_id),('depreciation_date','>=','2015-01-01'),
                                                                      ('depreciation_date','<=','2015-12-31')])
                    if line_dep_2015_ids:
                        dep_line_obj.write(cr, uid, line_dep_2015_ids[0],{'amount':dep_2015,})
                        
                    line_antes_2015_ids = dep_line_obj.search(cr, uid, [('asset_id','=',asset_id),('depreciation_date','<','2015-01-01')])
                    if line_antes_2015_ids:
                        dep_line_obj.unlink(cr, uid, line_antes_2015_ids)
                    #######################
                    line_2016_ids = dep_line_obj.search(cr, uid, [('asset_id','=',asset_id),('depreciation_date','>=','2016-01-01'),
                                                                          ('depreciation_date','<=','2016-12-31')])
                    if line_2016_ids:
                        dep_line_obj.write(cr, uid, line_2016_ids[0],{'amount':asset.dep_periodo})
                    saldo = saldo_pro = 0
                    line_despues_2015_ids = dep_line_obj.search(cr, uid, [('asset_id','=',asset_id),('depreciation_date','>=','2017-01-01')])
                    saldo = asset.value_residual - asset.depreciacion
                    if saldo>0:
                        if line_despues_2015_ids:
                            saldo_pro = saldo/len(line_despues_2015_ids)
                            dep_line_obj.write(cr, uid, line_despues_2015_ids,{
                                'amount':saldo_pro,
                            })
        return True

    def computePatronal(self, cr, uid, ids, context=None):
        run_obj = self.pool.get('hr.payslip.run')
        line_obj = self.pool.get('hr.payslip.line')
        ids_roles = run_obj.search(cr, uid, [('period_id','=',25)])
        id_rule = 4
        category_ids = [1,3]
        for id_rol in ids_roles:
            run = run_obj.browse(cr, uid, id_rol)
            for rol in run.slip_ids:
                ingresos = aux_patronal = 0
                line_ids_pat = line_obj.search(cr, uid, [('slip_id','=',rol.id),('salary_rule_id','=',id_rule)])
                if line_ids_pat:
                    for line in rol.line_ids:
                        if line.category_id.id in category_ids:
                            ingresos += line.amount
                        aux_patronal = ingresos * 0.1165
                    line_obj.write(cr, uid, line_ids_pat[0],{'amount':aux_patronal})
        return True

    def loadBudget2017Ingreso(self, cr, uid, ids, context=None):
        print "vele"
        data = self.read(cr, uid, ids)[0]
        if data['municipio'] == 'mil' and data['poa_id']:
            for r in range(sh.nrows)[1:]:
                aux_budget = ustr(sh.cell(r,0).value)
                post_ids = post_obj.search(cr, uid, [('code','=',aux_budget)])
                if post_ids:
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('poa_id','=',data['poa_id'])],limit=1)
                    if item_ids:
                        item_obj.write(cr, uid, item_ids[0],{
                            'planned_amount':sh.cell(r,2).value,
                        })
                    else:
                        item_id = item_obj.create(cr, uid, {
                            'budget_post_id':post_ids[0],
                            'task_id':project.tasks[0].id,
                            'planned_amount':sh.cell(r,2).value,
                        }) 
                else:
                    print "NO BUDGET", budget_str
        return True

    def loadBudget2017Gasto(self, cr, uid, ids, context=None):
        print "vele"
        return True

    def updateNumeroComp(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        obj_sequence = self.pool.get('ir.sequence')
        move_ids = move_obj.search(cr, uid, [('migrado2','!=',True),('state','=','posted')],order='numero asc')
        sql = "select id from account_move where migrado2 is null and name='/'"
        cr.execute(sql)
        j = 3763
        for move_id in move_ids:
            move = move_obj.browse(cr, uid, move_id)
            if move.numero<3000:
                j += 1
                move_obj.write(cr, uid, [move_id],{
                    'name':str(j),
                    'numero':j,
                })
        return True

    def updatePatronal(self, cr, uid, ids, context=None):
        run_obj = self.pool.get('hr.payslip.run')
        rol_obj = self.pool.get('hr.payslip')
        rol_line_obj = self.pool.get('hr.payslip.line')
        rule_obj = self.pool.get('hr.salary.rule')
        run_ids = run_obj.search(cr,uid,[])
        rule = rule_obj.browse(cr, uid, 4)
        for run_id in run_ids:
            rol_ids = rol_obj.search(cr, uid, [('payslip_run_id','=',run_id)])
            for rol_id in rol_ids:
                rol = rol_obj.browse(cr, uid, rol_id)
                aux_monto = 0
                if rol.contract_id.type_id.name=='LOSEP':
                    aux_monto = (rol.basic + rol.aportable)*(0.1165)
                else:
                    aux_monto = (rol.basic + rol.aportable)*(0.1215)
                rol_line_obj.create(cr,uid, {
                    'total':aux_monto,
                    'amount':aux_monto,
                    'salary_rule_id':4,
                    'slip_id':rol.id,
                    'name':rule.name,
                    'category_id':6,
                    'employee_id':rol.employee_id.id,
                    'contract_id':rol.contract_id.id,
                    'code':rule.code,
                    'period_id':rol.period_id.id,
                })
        return True

    def cuadraPagado(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        for this in self.browse(cr, uid, ids):
            account_ids = account_obj.search(cr, uid, [('code','=','6263002')])
            context = {'by_date':True,'date_start': this.mes_id.date_start, 'date_end':this.mes_id.date_stop ,'poa_id':1}
            line_ids = move_line_obj.search(cr, uid, [('budget_id','=',this.budget_id.id),
                                                      ('date','>=',this.mes_id.date_start),('date','<=',this.mes_id.date_stop)])
            if line_ids:
                moves = []
                for line_id in line_ids:
                    line = move_line_obj.browse(cr, uid, line_id)
                    if not line.move_id.id in moves:
                        moves.append(line.move_id.id)
            if moves:
                for move_id in moves:
                    line_quitar_ids = []
                    move = move_obj.browse(cr, uid, move_id)

                    line_quitar_ids = move_line_obj.search(cr, uid, [('move_id','=',move_id),('budget_paid','=',True),
                                                                     ('account_id','!=',account_ids[0])])
                    move_line_obj.write(cr, uid, line_quitar_ids[0],{
                        'budget_paid':False,
                    })
                    for line in move.line_id:
                        if line.account_id.code[0:3]=='213' and line.debit>0:
                            move_line_obj.write(cr, uid, line.id,{'state':'valid','budget_paid':True,'budget_id_cert':move.certificate_id.line_ids[0].id})
                            print "MOVECAMBIADO", move.name         
        return True

    def ajustaCedula(self, cr, uid, ids, context=None):
        post_obj = self.pool.get('budget.post')
        project_obj = self.pool.get('project.project')
        move_obj = self.pool.get('account.move')
        item_obj = self.pool.get('budget.item')
        certificate_obj = self.pool.get('budget.certificate')
        move_line_obj = self.pool.get('account.move.line')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        migrated_obj = self.pool.get('budget.item.migrated')
        account_obj = self.pool.get('account.account')
        item_migrated_obj = self.pool.get('budget.item.migrated')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        for this in self.browse(cr, uid, ids):
            context = {'by_date':True,'date_start': this.date_start, 'date_end':this.date_stop ,'poa_id':1}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            account_ids = account_obj.search(cr, uid, [('code','=','6263002')])
            if not account_ids:
                print "NOOOOO", '6263002'
            if data['municipio'] == 'mil':
                j = 0
                if data['mes_id']:
                    aux_comp = aux_dev = aux_pay = 0
                    for r in range(sh.nrows)[1:]:
                        aux_p = str(sh.cell(r,0).value[0:10])
                        if int(aux_p[9])>0:
                            aux_post_id = str(sh.cell(r,0).value[0:10])
                        elif int(aux_p[7])>0:
                            aux_post_id = str(sh.cell(r,0).value[0:8])
                        else:
                            aux_post_id = str(sh.cell(r,0).value[0:6])
                        aux_project = str(sh.cell(r,0).value)[10:13] + '1'
                        post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                        if not post_ids:
                            print "NO PARTIDA", aux_post_id
    #                    project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                        project_ids = project_obj.search(cr, uid, [('code','ilike',"%"+aux_project+"%")],limit=1)
                        if not project_ids:
                            aux_project = str(sh.cell(r,0).value)[10:13] + '6'
                            project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                            if not project_ids:
                                aux_project = str(sh.cell(r,0).value)[10:13] + '8'
                                project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                                print "NO PROHECTO", aux_project
                        proyecto = project_obj.browse(cr, uid, project_ids[0])
                        task_id = proyecto.tasks[0].id
                        budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                        if not budget_ids:
                            print "NO BUDGET ITEM 1", aux_post_id, proyecto.code
                            print "NO PROYECTO",proyecto.program_id.sequence
                        aux_comp = float(sh.cell(r,5).value)
                        aux_dev = float(sh.cell(r,6).value)
                        aux_pay = float(sh.cell(r,7).value)
                        item = item_obj.browse(cr, uid, budget_ids[0],context)
                        if abs(aux_comp-item.commited_amount)>0.01:
                            aux_dif = aux_comp - item.commited_amount
                            print "DIFERENCIA-COMPROMETIDO", item.code,aux_comp,item.commited_amount,aux_dif
                            item_migrated_obj.create(cr, uid, {
                                'budget_item_id':item.id,
                                'type_budget':'gasto',
                                'code':item.budget_post_id.code,
                                'date':this.date_stop,
                                'name':item.budget_post_id.name,
                                'budget_post_id':item.budget_post_id.id,
                                'program_code':item.program_id.sequence,
                                'commited_amount':aux_dif,
                            })
                        if abs(aux_dev-item.devengado_amount)>0.01:
                            aux_dif = aux_dev - item.devengado_amount
                            print "DIFERENCIA-DEVENGADO", item.code,aux_dev,item.devengado_amount,aux_dif
                            item_migrated_obj.create(cr, uid, {
                                'budget_item_id':item.id,
                                'type_budget':'gasto',
                                'code':item.budget_post_id.code,
                                'date':this.date_stop,
                                'name':item.budget_post_id.name,
                                'budget_post_id':item.budget_post_id.id,
                                'program_code':item.program_id.sequence,
                                'devengado_amount':aux_dif,
                            })
                        if abs(aux_pay-item.paid_amount)>0.01:
                            aux_dif = aux_pay - item.paid_amount
                            print "DIFERENCIA-PAGADO", item.code,aux_pay,item.paid_amount,aux_dif
                            item_migrated_obj.create(cr, uid, {
                                'budget_item_id':item.id,
                                'type_budget':'gasto',
                                'code':item.budget_post_id.code,
                                'date':this.date_stop,
                                'name':item.budget_post_id.name,
                                'budget_post_id':item.budget_post_id.id,
                                'program_code':item.program_id.sequence,
                                'paid_amount':aux_dif,
                            })
        return True


    def ajustaCedulaIngreso(self, cr, uid, ids, context=None):
        post_obj = self.pool.get('budget.post')
        project_obj = self.pool.get('project.project')
        move_obj = self.pool.get('account.move')
        item_obj = self.pool.get('budget.item')
        certificate_obj = self.pool.get('budget.certificate')
        move_line_obj = self.pool.get('account.move.line')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        migrated_obj = self.pool.get('budget.item.migrated')
        account_obj = self.pool.get('account.account')
        item_migrated_obj = self.pool.get('budget.item.migrated')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        for this in self.browse(cr, uid, ids):
            context = {'by_date':True,'date_start': this.date_start, 'date_end':this.date_stop ,'poa_id':1}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            account_ids = account_obj.search(cr, uid, [('code','=','6263002')])
            if not account_ids:
                print "NOOOOO", '6263002'
            if data['municipio'] == 'mil':
                j = 0
                if data['mes_id']:
                    aux_pay = aux_dev = 0
                    for r in range(sh.nrows)[1:]:
                        aux_pay = float(sh.cell(r,6).value)
                        aux_dev = float(sh.cell(r,5).value)
                        aux_p = str(sh.cell(r,0).value)
                        if int(aux_p[10:12])>0:
                            aux_post_id = str(sh.cell(r,0).value[0:10])
                        elif int(aux_p[6:8])>0:
                            aux_post_id = str(sh.cell(r,0).value[0:8])
                        elif int(aux_p[8:10])>0:
                            aux_post_id = str(sh.cell(r,0).value[0:10])
                        else:
                            aux_post_id = str(sh.cell(r,0).value[0:6])
                        aux_project = str(sh.cell(r,0).value)[10:13] + '1'
                        post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                        if not post_ids:
                            print "NO PARTIDA", aux_post_id
                        project_ids = project_obj.search(cr, uid, [('type_budget','=','ingreso')],limit=1)
                        proyecto = project_obj.browse(cr, uid, project_ids[0])                    
                        budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                        if budget_ids:
                            item = item_obj.browse(cr, uid, budget_ids[0],context)
                        else:
                            import pdb
                            pdb.set_trace()
                        #pregunta si hay ya alguna linea de migrado
                        migrated_ids = item_migrated_obj.search(cr, uid, [('date','=',this.date_stop),('budget_item_id','=',item.id)])
                        aux_dif = 0
                        if abs(aux_pay-item.paid_amount)>0.01:
                            aux_dif = aux_pay - item.paid_amount
                            print "DIFERENCIA-PAGADO", item.code,aux_pay,item.paid_amount,aux_dif
                            if migrated_ids:
                                item_migrated_obj.write(cr, uid,migrated_ids[0],{
                                    'paid_amount':aux_dif,
                                })
                            else:
                                item_migrated_obj.create(cr, uid, {
                                    'budget_item_id':item.id,
                                    'type_budget':'ingreso',
                                    'code':item.budget_post_id.code,
                                    'date':this.date_stop,
                                    'name':item.budget_post_id.name,
                                    'budget_post_id':item.budget_post_id.id,
                                    'program_code':item.program_id.sequence,
                                    'paid_amount':aux_dif,
                                })
                        if abs(aux_dev-item.devengado_amount)>0.01:
                            aux_dif = aux_dev - item.devengado_amount
                            print "DIFERENCIA-DEvengado", item.code,aux_dev,item.devengado_amount,aux_dif
                            if migrated_ids:
                                item_migrated_obj.write(cr, uid,migrated_ids[0],{
                                    'devengado_amount':aux_dif,
                                })
                            else:
                                item_migrated_obj.create(cr, uid, {
                                    'budget_item_id':item.id,
                                    'type_budget':'ingreso',
                                    'code':item.budget_post_id.code,
                                    'date':this.date_stop,
                                    'name':item.budget_post_id.name,
                                    'budget_post_id':item.budget_post_id.id,
                                    'program_code':item.program_id.sequence,
                                    'devengado_amount':aux_dif,
                                })
        return True

    def igualaPagado(self, cr, uid, ids, context=None):
        post_obj = self.pool.get('budget.post')
        item_obj = self.pool.get('budget.item')
        migrated_obj = self.pool.get('budget.item.migrated')
        for this in self.browse(cr, uid, ids):
            context = {'by_date':True,'date_start': this.date_start, 'date_end':this.date_stop ,'poa_id':1}
        post_ids = post_obj.search(cr, uid, [('code','like','71%'),('internal_type','!=','view')])
        print "POSTSSSSSSSS", post_ids
        if post_ids:
            for post_id in post_ids:
                post = post_obj.browse(cr, uid, post_id)
                if post.code[0:1]=='7':
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_id)])
                    if item_ids:
                        for item_id in item_ids:
                            diferencia = 0
                            item = item_obj.browse(cr, uid, item_id,context=context)
                            if item.devengado_amount>item.paid_amount:
                                diferencia = item.devengado_amount - item.paid_amount
                                migrated_obj.create(cr, uid, {
                                    'budget_post_id':post_id,
                                    'budget_item_id': item_id,
                                    'type_budget': "gasto",
                                    'program_code':item.code[7:11],
                                    'date':this.date_stop,
                                    'planned_amount':0,
                                    'reform_amount':0,
                                    'codif_amount':0,
                                    'devengado_amount':0,
                                    'paid_amount': diferencia,
                                    'devengado_balance':0,
                                })
        return True

    def cuadraCedula(self, cr, uid, ids, context=None):
        post_obj = self.pool.get('budget.post')
        project_obj = self.pool.get('project.project')
        move_obj = self.pool.get('account.move')
        item_obj = self.pool.get('budget.item')
        certificate_obj = self.pool.get('budget.certificate')
        move_line_obj = self.pool.get('account.move.line')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        migrated_obj = self.pool.get('budget.item.migrated')
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        for this in self.browse(cr, uid, ids):
            context = {'by_date':True,'date_start': this.mes_id.date_start, 'date_end':this.mes_id.date_stop ,'poa_id':1}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            account_ids = account_obj.search(cr, uid, [('code','=','6263002')])
            if not account_ids:
                print "NOOOOO", '6263002'
            if data['municipio'] == 'mil':
                j = 0
                if data['mes_id']:
                    aux_comp = aux_dev = aux_pay = 0
                    for r in range(sh.nrows)[1:]:
                        aux_p = str(sh.cell(r,0).value[0:10])
                        if int(aux_p[9])>0:
                            aux_post_id = str(sh.cell(r,0).value[0:10])
                        elif int(aux_p[7])>0:
                            aux_post_id = str(sh.cell(r,0).value[0:8])
                        else:
                            aux_post_id = str(sh.cell(r,0).value[0:6])
                        aux_project = str(sh.cell(r,0).value)[10:13] + '1'
                        post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                        if not post_ids:
                            print "NO PARTIDA", aux_post_id
    #                    project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                        project_ids = project_obj.search(cr, uid, [('code','ilike',"%"+aux_project+"%")],limit=1)
                        if not project_ids:
                            aux_project = str(sh.cell(r,0).value)[10:13] + '6'
                            project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                            if not project_ids:
                                aux_project = str(sh.cell(r,0).value)[10:13] + '8'
                                project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                                print "NO PROHECTO", aux_project
                        proyecto = project_obj.browse(cr, uid, project_ids[0])
                        task_id = proyecto.tasks[0].id
                        budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                        if not budget_ids:
                            print "NO BUDGET ITEM 1", aux_post_id, proyecto.code
                            print "NO PROYECTO",proyecto.program_id.sequence
                        aux_comp = float(sh.cell(r,5).value)
                        aux_dev = float(sh.cell(r,6).value)
                        aux_pay = float(sh.cell(r,7).value)
                        item = item_obj.browse(cr, uid, budget_ids[0],context)
                        if abs(aux_comp-item.commited_amount)>0.01:
                            aux_dif = aux_comp - item.commited_amount
                            print "DIFERENCIA-COMPROMETIDO", item.code,aux_comp,item.commited_amount,aux_dif
                            if aux_comp==0:
                                #paso a draft los cert y line de todo
                                cert_line_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',budget_ids[0]),('date_commited','>=',this.mes_id.date_start),
                                                                                      ('date_commited','<=',this.mes_id.date_stop)])
                                if cert_line_ids:
                                    certificados = []
                                    for cert_line_id in cert_line_ids:
                                        cert_line = certificate_line_obj.browse(cr, uid, cert_line_id)
                                        if not cert_line.certificate_id.id in certificados:
                                            certificados.append(cert_line.certificate_id.id)
                                if certificados:
                                    for certificado_id in certificados:
                                        certificate_obj.write(cr, uid, certificado_id,{'state':'draft'})
                            else:
                                cert_line_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',budget_ids[0]),('date_commited','>=',this.mes_id.date_start),
                                                                                      ('date_commited','<=',this.mes_id.date_stop)])
                                aux_commited = 0
                                if cert_line_ids:
                                    certificados = []
                                    for cert_line_id in cert_line_ids:
                                        cert_line = certificate_line_obj.browse(cr, uid, cert_line_id)
                                        if cert_line.budget_accrued>0:
                                            aux_commited += cert_line.budget_accrued
                                            if not cert_line.certificate_id.id in certificados:
                                                certificados.append(cert_line.certificate_id.id)
                                aux2 = 0
                                if certificados:
                                    aux2 = item.commited_amount-aux_commited 
                                    if aux2 == aux_comp:
                                        for certificado_id in certificados:
                                            certificate_obj.write(cr, uid, certificado_id,{'state':'draft'})
                        if abs(aux_dev-item.devengado_amount)>0.01:
                            aux_dif = aux_dev - item.devengado_amount
                            print "DIFERENCIA-DEVENGADO", item.code,aux_dev,item.devengado_amount,aux_dif
                        if abs(aux_pay-item.paid_amount)>0.01:
                            aux_dif = aux_pay - item.paid_amount
                            print "DIFERENCIA-PAGADO", item.code,aux_pay,item.paid_amount,aux_dif
        return True

    def updateCargoMil2(self, cr, uid, ids, context=None):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        department_obj = self.pool.get('hr.department')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:
                    aux_ced_ruc = str(sh.cell(r,0).value)
                    aux_job = ustr(sh.cell(r,5).value)
                    aux_dept = ustr(sh.cell(r,4).value)
                    dept_ids = department_obj.search(cr, uid, [('name','=',aux_dept)])
                    if dept_ids:
                        dept_id = dept_ids[0]
                    else:
                        dept_id = department_obj.create(cr, uid, {
                            'name':aux_dept,
                            'sequence':'001',
                        })
                    job_ids = job_obj.search(cr, uid, [('name','=',aux_job),('department_id','=',dept_id)])
                    if job_ids:
                        job_id = job_ids[0]
                    else:
                        job_id = job_obj.create(cr, uid, {
                            'name':aux_job,
                            'department_id':dept_id,
                        })
                    emp_ids = employee_obj.search(cr, uid, [('name','=',aux_ced_ruc)])
                    if emp_ids:
                        contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp_ids[0]),('activo','=',True)])
                        if contract_ids:
                            contract_obj.write(cr, uid, contract_ids[0],{
                                'job_id':job_id,
                                'department_id':dept_id,
                            })
                        employee_obj.write(cr, uid, emp_ids,{
                            'job_id':job_id,
                            'department_id':dept_id,
                        })
                        num+=1
        print "CONTRATOS ACTUALIZADOS", num
        return True        

    def loadPartidaAsiento(self, cr, uid, ids, context=None):
        post_obj = self.pool.get('budget.post')
        project_obj = self.pool.get('project.project')
        move_obj = self.pool.get('account.move')
        item_obj = self.pool.get('budget.item')
        certificate_obj = self.pool.get('budget.certificate')
        move_line_obj = self.pool.get('account.move.line')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}            
            if data['municipio'] == 'mil':
                j = 0
                for r in range(sh.nrows)[1:]:
                    aux_tipo = ustr(sh.cell(r,3).value)
                    if aux_tipo=='PRESUP':
                        aux_sec = int(sh.cell(r,2).value)
                        sec_cuenta = aux_sec - 1
                        aux_comp = ustr(sh.cell(r,1).value)
                        move_ids = move_obj.search(cr, uid, [('name','=',aux_comp)])
                        aux_p = str(sh.cell(r,4).value[0:10])
                        if int(aux_p[9])>0:
                            aux_post_id = str(sh.cell(r,4).value[0:10])
                        elif int(aux_p[7])>0:
                            aux_post_id = str(sh.cell(r,4).value[0:8])
                        elif int(aux_p[8])>0:
                            aux_post_id = str(sh.cell(r,4).value[0:10])
                        else:
                            aux_post_id = str(sh.cell(r,4).value[0:6])
                        aux_project = str(sh.cell(r,4).value)[10:13] + '1'
                        post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                        if not post_ids:
                            print "NO PARTIDA", aux_post_id
                        project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                        if move_ids:
                            move = move_obj.browse(cr, uid, move_ids[0])
                            certificate_id = move.certificate_id.id
                        if not project_ids:
                            aux_project = str(sh.cell(r,3).value)[10:13] + '6'
                            project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                            if not project_ids:
                                aux_project = str(sh.cell(r,3).value)[10:13] + '8'
                                project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                                if not project_ids:
                                    if int(aux_p[0:2])<50:
                                        project_ids = project_obj.search(cr, uid, [('type_budget','=','ingreso')],limit=1)
                                        certificate_id = certificate_obj.search(cr, uid, [('tipo_aux','=','ingreso')])[0]
                                        if not project_ids:
                                            print "NO PROHECTO", aux_project
                                    else:
                                        if aux_post_id=='970101':
                                            aux_project = str(sh.cell(r,4).value)[10:14]
                                            project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                                            if not project_ids:
                                                print "NO PROHECTO", aux_project, aux_p
                                            #certificate_id = certificate_obj.search(cr, uid, [('tipo_aux','=','ingreso')])[0]
                        if not project_ids:
                            if int(aux_p[0:2])<50:
                                print "ojooooooo", aux_p
                            aux_project = str(sh.cell(r,4).value)[10:14]
                            project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                            if not project_ids:
                                print "NO PROHECTO", aux_project, aux_p
                        proyecto = project_obj.browse(cr, uid, project_ids[0])                    
                        budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                        if not budget_ids:
                            print "NO BUDGET ITEM 1", aux_post_id, proyecto.code                        
                            import pdb
                            pdb.set_trace()
                        if move_ids:
                            line_cert_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',budget_ids[0]),('certificate_id','=',certificate_id)])
                            if line_cert_ids:
                                line_ids = move_line_obj.search(cr, uid, [('move_id','=',move_ids[0]),('seq','=',sec_cuenta)])
                                if line_ids:
                                    j+=1
                                    cr.execute('''update account_move_line set budget_accrued=True,budget_paid=True,budget_id_cert=%s,budget_post=%s,budget_id=%s where id=%s'''%(line_cert_ids[0],post_ids[0],budget_ids[0],line_ids[0]))    
                                else:
                                    print "NOLINEA-SEq",sec_cuenta
                            else:
                                print "NOCERT", move.name, move.certificate_id.name
                        else:
                            print "NOMOVE",  aux_comp
        print "TOTAL LINEAS", j
        return True

    def loadReformaMil(self, cr, uid, ids, context=None):
        reform_obj = self.pool.get('mass.reform')
        line_obj = self.pool.get('mass.reform.line')
        line_ing_obj = self.pool.get('mass.reform.line.ingreso')
        item_obj = self.pool.get('budget.item')
        project_obj = self.pool.get('project.project')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['municipio'] == 'mil':
                for r in range(sh.nrows)[1:]:
                    aux_reforma = sh.cell(r,1).value
                    aux_autorizacion = sh.cell(r,2).value
                    reform_ids = reform_obj.search(cr, uid, [('code','=',aux_autorizacion),('reforma','=',aux_reforma)])
                    if not reform_ids:
                        print "noreforma",aux_autorizacion
                    aut_id = reform_ids[0]
                    aux_p = str(sh.cell(r,3).value[0:10])
                    if int(aux_p[9])>0:
                        aux_post_id = str(sh.cell(r,3).value[0:10])
                    elif int(aux_p[7])>0:
                        aux_post_id = str(sh.cell(r,3).value[0:8])
                    else:
                        aux_post_id = str(sh.cell(r,3).value[0:6])
                    aux_project = str(sh.cell(r,3).value)[10:13] + '1'
                    post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                    if not post_ids:
                        print "NO PARTIDA", aux_post_id
                    project_ids = project_obj.search(cr, uid, [('code','ilike',"%"+aux_project+"%")],limit=1)
                    if not project_ids:
                        aux_project = str(sh.cell(r,3).value)[10:13] + '6'
                        project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                        if not project_ids:
                            aux_project = str(sh.cell(r,3).value)[10:13] + '8'
                            project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                            print "NO PROHECTO", aux_project
                    proyecto = project_obj.browse(cr, uid, project_ids[0])                    
                    budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                    if not budget_ids:
                        print "NO BUDGET ITEM 1", aux_post_id, proyecto.code
                        print "NO PROYECTO",proyecto.program_id.sequence
                    aux_incremento = sh.cell(r,6).value
                    aux_decremento = sh.cell(r,7).value
                    aux_suplemento = sh.cell(r,8).value
                    aux_reduccion = sh.cell(r,9).value
                    aux_monto = 0
                    if aux_incremento>0 or aux_suplemento>0:
                        aux_monto = aux_incremento + aux_suplemento
                        line_obj.create(cr, uid, {
                            'budget_id':budget_ids[0],
                            'mass_id2':aut_id,
                            'monto':aux_monto,
                        })
                    elif aux_decremento>0 or aux_reduccion>0:
                        aux_monto = aux_decremento + aux_reduccion
                        line_obj.create(cr, uid, {
                            'budget_id':budget_ids[0],
                            'mass_id':aut_id,
                            'monto':aux_monto,
                        })
        return True

    def asientosMilDetalleAnterior(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        conta = 0 
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['municipio'] == 'mil':
                context={}
                state_aux = 'draft'
                company_aux = 1
                currency_aux = 2
                for r in range(sh.nrows)[1:]:
                    print "LINEA", r
                    aux_cta = ustr(sh.cell(r,5).value)
                    account_ids = account_obj.search(cr, uid, [('code','=',aux_cta),('type','!=','view')])
                    if account_ids:
                        account_id = account_ids[0]
                    else:
                        account_ids = account_obj.search(cr, uid, [('code','=',aux_cta)])
                        if account_ids:
                            print "NOCUENTAREGULAR", aux_cta
                            account_id = account_ids[0]
                        else:
                            print "NOCUENTA", aux_cta
                            aux_cta_name = aux_cta
                            account_id = account_obj.create(cr, uid, {
                                'name':aux_cta_name,
                                'code_aux':aux_cta,
                                'type':'other',
                                'user_type':32,
                            })
                    debe = haber = 0
                    aux_comp = ustr(sh.cell(r,1).value)
                    move_ids = move_obj.search(cr, uid, [('name','=',aux_comp),('fiscalyear_id','=',data['period_id'][0])])
                    if move_ids:
                        move = move_obj.browse(cr, uid, move_ids[0])
                        aux_move_name = move.name
                        move_id = move.id
                    else:
                        print "NOMOVE", aux_comp
                    partner_id = move.partner_id.id
                    journal_id = move.journal_id.id
                    period_id = move.period_id.id
                    date = move.date
                    debe = sh.cell(r,8).value
                    haber = sh.cell(r,9).value
                    aux_sec = sh.cell(r,3).value
                    name = ustr(sh.cell(r,6).value)[0:63]
                    conta += 1
                    sql = '''
                    INSERT INTO account_move_line (
                    move_id,name,account_id,debit,credit,journal_id,period_id,date,state,company_id,currency_id,migrado,is_start,num_comp,seq,partner_id) VALUES (%s, '%s',%s,%s,%s,%s,%s,'%s','%s',%s,%s,%s,%s,%s,%s,%s)'''%(move_id,name,account_id,debe,haber,journal_id,period_id,date,state_aux,company_aux,currency_aux,True,False,aux_comp,aux_sec,partner_id)
                    cr.execute(sql)
        print "TOTAL REGiSTROS", conta
#        self.updateAll(cr, uid, [])
        return True

    def asientosMilDetalle(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['municipio'] == 'mil':
                context={}
                state_aux = 'draft'
                company_aux = 1
                currency_aux = 2
                conta = 0 
                for r in range(sh.nrows)[1:]:
                    aux_tipo = ustr(sh.cell(r,3).value)
                    if aux_tipo=='CONTABLE':
                        aux_cta = ustr(sh.cell(r,4).value)
                        account_ids = account_obj.search(cr, uid, [('code','=',aux_cta),('type','!=','view')])
                        if account_ids:
                            account_id = account_ids[0]
                        else:
                            account_ids = account_obj.search(cr, uid, [('code','=',aux_cta)])
                            if account_ids:
                                print "NOCUENTAREGULAR", aux_cta
                                account_id = account_ids[0]
                            else:
                                print "NOCUENTA", aux_cta
                                aux_cta_name = ustr(sh.cell(r,5).value)
                                account_id = account_obj.create(cr, uid, {
                                    'name':aux_cta_name,
                                    'code_aux':aux_cta,
                                    'type':'other',
                                    'user_type':32,
                                })
                        debe = haber = 0
                        aux_comp = ustr(sh.cell(r,1).value)
                        move_ids = move_obj.search(cr, uid, [('name','=',aux_comp),('fiscalyear_id','=',data['period_id'][0])])
                        if move_ids:
                            move = move_obj.browse(cr, uid, move_ids[0])
                            aux_move_name = move.name
                            move_id = move.id
                        else:
                            print "NOMOVE", aux_comp
                        partner_id = move.partner_id.id
                        journal_id = move.journal_id.id
                        period_id = move.period_id.id
                        date = move.date
                        debe = sh.cell(r,7).value
                        haber = sh.cell(r,8).value
                        aux_sec = sh.cell(r,2).value
                        name = ustr(sh.cell(r,5).value)[0:63]
                        conta += 1
                        sql = '''
                        INSERT INTO account_move_line (
                        move_id,name,account_id,debit,credit,journal_id,period_id,date,state,company_id,currency_id,migrado,is_start,num_comp,seq,partner_id) VALUES (%s, '%s',%s,%s,%s,%s,%s,'%s','%s',%s,%s,%s,%s,%s,%s,%s)'''%(move_id,name,account_id,debe,haber,journal_id,period_id,date,state_aux,company_aux,currency_aux,True,False,aux_comp,aux_sec,partner_id)
                        cr.execute(sql)
        print "TOTAL REGiSTROS", conta
#        self.updateAll(cr, uid, [])
        return True

    def asientosMilAnterior(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        partner_obj = self.pool.get('res.partner')
        period_obj = self.pool.get('account.period')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['municipio'] == 'mil':
                for r in range(sh.nrows)[1:]:
                    aux_state = ''
                    aux_tipo_comp = ustr(sh.cell(r,4).value)
                    if aux_tipo_comp == 'EGRESO':
                        journal_aux = data['journal_id'][0]
                    elif aux_tipo_comp == 'INGRESO':
                        journal_aux = data['journal_in'][0]
                    else:
                        journal_aux = data['journal_diario'][0]
                    date_aux2 = ustr(sh.cell(r,2).value)
                    period_ids = period_obj.find(cr, uid, date_aux2)
                    name_aux = ustr(sh.cell(r,1).value)
                    desc_aux = ustr(sh.cell(r,9).value)
                    aux_cedruc1 = ustr(sh.cell(r,5).value)
                    pos_guion = aux_cedruc1.find('-')
                    aux_cedruc = aux_cedruc1[0:pos_guion].replace(' ','')
                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedruc)])
                    if partner_ids:
                        partner_id = partner_ids[0]
                    else:
                        if len(aux_cedruc)>1:
                            print "NO PARTNER", aux_cedruc
                            aux_ced = aux_cedruc
                            name = aux_cedruc1[pos_guion:].replace(' ','')
                            if len(aux_ced)==13:
                                type_ced_ruc = 'ruc'
                            elif len(aux_ced)==10:
                                type_ced_ruc = 'cedula'
                            else:
                                type_ced_ruc = 'pasaporte'
                            direccion = "Milagro"
                            mail = "info@gmail.com"
                            telefono = "222222"
                            partner_id = partner_obj.create(cr, uid, {
                                'ced_ruc':aux_cedruc,
                                'type_ced_ruc':'pasaporte',
                                'tipo_persona':'6',
                                'name':ustr(sh.cell(r,6).value),
                                'direccion':direccion,
                                'email': mail,
                                'telefono':telefono,
                                'property_account_receivable':20446,
                                'property_account_payable':25391,
                                'property_account_position':2,})
                        else:
                            print "parter el GAD", name_aux
                            partner_id = 1
                    #Antes de crear el movimiento busco la relacion con la certificacion presupuestaria
                    move_id = move_obj.create(cr, uid, {
                        'partner_id':partner_id,
                        'journal_id':journal_aux,
                        'date':date_aux2,
                        'period_id':period_ids[0],
                        'name':name_aux,
                        'numero':int(name_aux),
                        'ref':desc_aux,
                        'narration':desc_aux,
                        'migrado':True,
                        'afectacion':False,
                        'state': 'draft',
                    })
        return True

    def asientosMil(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        partner_obj = self.pool.get('res.partner')
        period_obj = self.pool.get('account.period')
        certificate_obj = self.pool.get('budget.certificate')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['municipio'] == 'mil':
                for r in range(sh.nrows)[1:]:
                    aux_state = ''
                    aux_tipo_comp = ustr(sh.cell(r,4).value)
                    if aux_tipo_comp == 'EGRESO':
                        journal_aux = data['journal_id'][0]
                    elif aux_tipo_comp == 'INGRESO':
                        journal_aux = data['journal_in'][0]
                    else:
                        journal_aux = data['journal_diario'][0]
                    date_aux2 = ustr(sh.cell(r,2).value)
                    period_ids = period_obj.find(cr, uid, date_aux2)
                    name_aux = ustr(sh.cell(r,1).value)
                    desc_aux = ustr(sh.cell(r,9).value)
                    aux_cedruc1 = ustr(sh.cell(r,5).value)
                    pos_guion = aux_cedruc1.find('-')
                    aux_cedruc = aux_cedruc1[0:pos_guion].replace(' ','')
                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedruc)])
                    ##idp
                    aux_idp = ustr(sh.cell(r,3).value)
                    certificate_ids = certificate_obj.search(cr, uid, [('name','=',aux_idp)])
                    if partner_ids:
                        partner_id = partner_ids[0]
                    else:
                        if len(aux_cedruc)>1:
                            print "NO PARTNER", aux_cedruc
                            aux_ced = aux_cedruc
                            name = aux_cedruc1[pos_guion:].replace(' ','')
                            if len(aux_ced)==13:
                                type_ced_ruc = 'ruc'
                            elif len(aux_ced)==10:
                                type_ced_ruc = 'cedula'
                            else:
                                type_ced_ruc = 'pasaporte'
                            direccion = "Milagro"
                            mail = "info@gmail.com"
                            telefono = "222222"
                            partner_id = partner_obj.create(cr, uid, {
                                'ced_ruc':aux_cedruc,
                                'type_ced_ruc':'pasaporte',
                                'tipo_persona':'6',
                                'name':ustr(sh.cell(r,6).value),
                                'direccion':direccion,
                                'email': mail,
                                'telefono':telefono,
                                'property_account_receivable':20446,
                                'property_account_payable':25391,
                                'property_account_position':2,})
                        else:
                            print "parter el GAD", name_aux
                            partner_id = 1
                    #Antes de crear el movimiento busco la relacion con la certificacion presupuestaria
                    if certificate_ids:
                        certificate = certificate_obj.browse(cr, uid, certificate_ids[0])
                        if len(certificate.line_ids)>0:
                            move_id = move_obj.create(cr, uid, {
                                'partner_id':partner_id,
                                'journal_id':journal_aux,
                                'date':date_aux2,
                                'period_id':period_ids[0],
                                'name':name_aux,
                                'ref':desc_aux,
                                'narration':desc_aux,
                                'migrado':True,
                                'afectacion':True,
                                'state': 'draft',
                                'certificate_id':certificate_ids[0],
                            })
                        else:
                            move_id = move_obj.create(cr, uid, {
                                'partner_id':partner_id,
                                'journal_id':journal_aux,
                                'date':date_aux2,
                                'period_id':period_ids[0],
                                'name':name_aux,
                                'ref':desc_aux,
                                'narration':desc_aux,
                                'migrado':True,
                                'afectacion':True,
                                'state': 'draft',
                                'certificate_id':certificate_ids[0],
                                'aux_update':'1',
                            })
                    else:
                        move_id = move_obj.create(cr, uid, {
                            'partner_id':partner_id,
                            'journal_id':journal_aux,
                            'date':date_aux2,
                            'period_id':period_ids[0],
                            'name':name_aux,
                            'ref':desc_aux,
                            'narration':desc_aux,
                            'migrado':True,
                            'afectacion':False,
                            'state': 'draft',
                        })
        return True

    def loadCompromisoLineMil(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        item_obj = self.pool.get('budget.item')
        project_obj = self.pool.get('project.project')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                j = 0
                for r in range(sh.nrows)[1:]:  
                    aux_cert_id = ustr(sh.cell(r,1).value)
                    aux_p = str(sh.cell(r,2).value[0:10])
                    if int(aux_p[9])>0:
                        aux_post_id = str(sh.cell(r,2).value[0:10])
                    elif int(aux_p[7])>0:
                        aux_post_id = str(sh.cell(r,2).value[0:8])
                    else:
                        aux_post_id = str(sh.cell(r,2).value[0:6])
                    aux_project = str(sh.cell(r,2).value)[10:13] + '1'
                    post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                    if not post_ids:
                        print "NO PARTIDA", aux_post_id
#                    project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                    project_ids = project_obj.search(cr, uid, [('code','ilike',"%"+aux_project+"%")],limit=1)
                    if not project_ids:
                        aux_project = str(sh.cell(r,2).value)[10:13] + '6'
                        project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                        if not project_ids:
                            aux_project = str(sh.cell(r,2).value)[10:13] + '8'
                            project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                            print "NO PROHECTO", aux_project
                    proyecto = project_obj.browse(cr, uid, project_ids[0])
                    task_id = proyecto.tasks[0].id
                    #considerar si es bienes o servicios
                    aux_tipo = ustr(sh.cell(r,3).value)
                    aux_tp = 'Servicio'
                    if aux_tipo[1:4]=='MAT' or aux_post_id[0:1]=='8':
                        aux_tp = 'Bien'
                    #considerar si esta el iva en la misma linea
                    aux_total = sh.cell(r,7).value
                    if aux_total:
                        certificate_ids = certificate_obj.search(cr, uid, [('name','=',aux_cert_id)],limit=1)
                        if certificate_ids:
                            certificate_id = certificate_ids[0]
                        else:
                            print "NO CERTIFICADO", aux_cert_id
                            certificate_id = certificate_obj.create(cr, uid, {
                                'name':aux_cert_id,
                                'number':aux_cert_id,
                                'ref_doc':aux_cert_id,
                                'user_id':1,
                                'department_id':1,
                                'solicitant_id':1,
                                'project_id':1,
                                'date':time.strftime('%Y-%m-%d'),
                                'date_confirmed':time.strftime('%Y-%m-%d'),
                                'date_commited':time.strftime('%Y-%m-%d'),
                                'notes':"NO CP",
                                'partner_id':1,
                                'migrado':True,
                                'state':'commited',
                            })      
                        budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                        if not budget_ids:
                            print "NO BUDGET ITEM 1", aux_post_id, proyecto.code
                            print "NO PROYECTO",proyecto.program_id.sequence
                        certificate_line_obj.create(cr, uid, {
                            'certificate_id':certificate_id,
                            'migrado':'True',
                            'tipo_invoice':aux_tp,
                            'project_id':project_ids[0],
                            'task_id':task_id,
                            'budget_id':budget_ids[0],
                            'amount':aux_total,
                            'amount_certified':aux_total,
                            'amount_commited':aux_total,
                            'state':'commited',
                        })
                        j+=1
        print "TOTAL LINEAS DE CERT",j
        return True

    def loadCompromisoLineMil2(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        item_obj = self.pool.get('budget.item')
        project_obj = self.pool.get('project.project')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:  
                    aux_cert_id = ustr(sh.cell(r,1).value)
                    aux_p = str(sh.cell(r,2).value[0:10])
                    if int(aux_p[9])>0:
                        aux_post_id = str(sh.cell(r,2).value[0:10])
                    elif int(aux_p[7])>0:
                        aux_post_id = str(sh.cell(r,2).value[0:8])
                    else:
                        aux_post_id = str(sh.cell(r,2).value[0:6])
                    aux_project = str(sh.cell(r,2).value)[10:13] + '1'
                    post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                    if not post_ids:
                        print "NO PARTIDA", aux_post_id
#                    project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                    project_ids = project_obj.search(cr, uid, [('code','ilike',"%"+aux_project+"%")],limit=1)
                    if not project_ids:
                        aux_project = str(sh.cell(r,2).value)[10:13] + '6'
                        project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                        if not project_ids:
                            aux_project = str(sh.cell(r,2).value)[10:13] + '8'
                            project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                            print "NO PROHECTO", aux_project
                    proyecto = project_obj.browse(cr, uid, project_ids[0])
                    task_id = proyecto.tasks[0].id
                    #considerar si es bienes o servicios
                    aux_tipo = ustr(sh.cell(r,3).value)
                    aux_tp = 'Servicio'
                    aux_iv = 'IvaServicios'
                    if aux_tipo[1:4]=='MAT' or aux_post_id[0:1]=='8':
                        aux_tp = 'Bien'
                        aux_iv = 'Iva'
                    #considerar si esta el iva en la misma linea
                    aux_total = sh.cell(r,7).value
                    aux_base = sh.cell(r,5).value
                    aux_iva = sh.cell(r,6).value
                    if aux_base=='':
                        certificate_ids = certificate_obj.search(cr, uid, [('name','=',aux_cert_id)],limit=1)
                        if certificate_ids:
                            certificate_id = certificate_ids[0]
                        else:
                            print "NO CERTIFICADO", aux_cert_id
                            certificate_id = certificate_obj.create(cr, uid, {
                                'name':aux_cert_id,
                                'number':aux_cert_id,
                                'ref_doc':aux_cert_id,
                                'user_id':1,
                                'department_id':1,
                                'solicitant_id':1,
                                'project_id':1,
                                'date':time.strftime('%Y-%m-%d'),
                                'date_confirmed':time.strftime('%Y-%m-%d'),
                                'date_commited':time.strftime('%Y-%m-%d'),
                                'notes':"NO CP",
                                'partner_id':1,
                                'migrado':True,
                                'state':'commited',
                            })      
                        budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                        if not budget_ids:
                            print "NO BUDGET ITEM 1", aux_post_id, proyecto.code
                            print "NO PROYECTO",proyecto.program_id.sequence
                        certificate_line_obj.create(cr, uid, {
                            'certificate_id':certificate_id,
                            'migrado':'True',
                            'tipo_invoice':aux_tp,
                            'project_id':project_ids[0],
                            'task_id':task_id,
                            'budget_id':budget_ids[0],
                            'amount':aux_total,
                            'amount_certified':aux_total,
                            'amount_commited':aux_total,
                            'state':'commited',
                        })
                    else:
                        certificate_ids = certificate_obj.search(cr, uid, [('name','=',aux_cert_id)],limit=1)
                        if certificate_ids:
                            certificate_id = certificate_ids[0]
                        else:
                            print "NO CERTIFICADO", aux_cert_id
                            certificate_id = certificate_obj.create(cr, uid, {
                                'name':aux_cert_id,
                                'number':aux_cert_id,
                                'ref_doc':aux_cert_id,
                                'user_id':1,
                                'department_id':1,
                                'solicitant_id':1,
                                'project_id':1,
                                'date':time.strftime('%Y-%m-%d'),
                                'date_confirmed':time.strftime('%Y-%m-%d'),
                                'date_commited':time.strftime('%Y-%m-%d'),
                                'notes':"NO CP",
                                'partner_id':1,
                                'migrado':True,
                                'state':'commited',
                            })
                            print "NO CERTIFICADO", aux_cert_id
                        budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                        if not budget_ids:
                            print "NO BUDGET ITEM 2", aux_post_id, proyecto.code
                            print "NO PROYECTO",proyecto.program_id.sequence
                        if aux_base!=0:
                            certificate_line_obj.create(cr, uid, {
                                'certificate_id':certificate_id,
                                'migrado':'True',
                                'project_id':project_ids[0],
                                'task_id':task_id,
                                'budget_id':budget_ids[0],
                                'amount':aux_base,
                                'tipo_invoice':aux_tp,
                                'amount_certified':aux_base,
                                'amount_commited':aux_base,
                                'state':'commited',
                            })
                        if aux_iva!=0:
                            certificate_line_obj.create(cr, uid, {
                                'certificate_id':certificate_id,
                                'migrado':'True',
                                'project_id':project_ids[0],
                                'task_id':task_id,
                                'budget_id':budget_ids[0],
                                'amount':aux_iva,
                                'amount_certified':aux_iva,
                                'amount_commited':aux_iva,
                                'tipo_invoice':aux_iv,
                                'state':'commited',
                            })
        return True

    def loadCompromisoMil(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        dept_obj = self.pool.get('hr.department')
        emp_obj = self.pool.get('hr.employee')
        partner_obj = self.pool.get('res.partner')
        project_obj = self.pool.get('project.project')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:
                    if ustr(sh.cell(r,1).value)=='NULL':
                        continue
                    aux_name = ustr(sh.cell(r,1).value)
                    if len(str(sh.cell(r,7).value))>1:
                        date_solicitud = str(sh.cell(r,7).value)[3:5] + '/' + str(sh.cell(r,7).value)[0:2] + '/' + str(sh.cell(r,7).value)[6:10]
                    else:
                        date_solicitud = str(sh.cell(r,0).value)[3:5] + '/' + str(sh.cell(r,0).value)[0:2] + '/' + str(sh.cell(r,0).value)[6:10]
                    date_aux_1 = str(sh.cell(r,0).value)[3:5] + '/' + str(sh.cell(r,0).value)[0:2] + '/' + str(sh.cell(r,0).value)[6:10]
                    partner_name_aux = ustr(sh.cell(r,4).value)
                    aux_ref_doc = ustr(sh.cell(r,6).value)
                    desc_aux = ustr(sh.cell(r,3).value)
                    partner_aux = ustr(sh.cell(r,5).value)
                    aux_department = ustr(sh.cell(r,2).value)
                    department_ids = dept_obj.search(cr, uid, [('name','=',aux_department)],limit=1)
                    if department_ids:
                        department_id = department_ids[0]
                    else:
                        print "No dept", aux_department
                        department_id = dept_obj.create(cr, uid, {
                            'sequence':'1111',
                            'name':aux_department,
                            'manager_id':1,
                        })
                    departamento = dept_obj.browse(cr, uid, department_id)
                    if departamento.manager_id:
                        employee_id = departamento.manager_id.id
                    elif departamento.coordinador_id:
                        employee_id = departamento.manager_id.id
                    else:
                        employee_ids = emp_obj.search(cr, uid, [('department_id','=',department_id)])
                        if employee_ids:
                            employee_id = employee_ids[0]
                        else:
                            employee_ids = emp_obj.search(cr, uid, [])
                            employee_id = employee_ids[0]
                    project_ids = project_obj.search(cr, uid, [('type_budget','=','gasto')],limit=1)
                    ##partner
                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',partner_aux)])
                    aux_persona = '6'
                    if partner_ids:
                        partner_id = partner_ids[0]
                    else:
                        print "No partner", partner_aux
                        aux_tipo = 'cedula'
                        if len(partner_aux)>10:
                            aux_tipo = 'ruc'
                        partner_id = partner_obj.create(cr, uid, {
                            'ced_ruc':partner_aux,
                            'type_ced_ruc':aux_tipo,
                            'tipo_persona':aux_persona,
                            'name':partner_name_aux,
                            'direccion':'Milagro',
                            'telefono':'2222222',
                            'property_account_receivable':1689,
                            'property_account_payable':2823,
                            'property_account_position':2,
                            'email':'info@gmail.com',
                        })
                    cert_id = certificate_obj.create(cr, uid, {
                        'name':aux_name,
                        'number':aux_name,
                        'ref_doc':aux_ref_doc,
                        'user_id':1,
                        'department_id':department_id,
                        'solicitant_id':employee_id,
                        'project_id':project_ids[0],
                        'date':date_solicitud,
                        'date_confirmed':date_aux_1,
                        'date_commited':date_aux_1,
                        'notes':desc_aux,
                        'partner_id':partner_id,
                        'migrado':True,
                        'state':'commited',
                    })
        return True

    def updateContrato2(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:
                    aux_ced_ruc = str(sh.cell(r,1).value)
                    emp_ids = employee_obj.search(cr, uid, [('name','=',aux_ced_ruc)])
                    if emp_ids:
                        contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp_ids[0])])
                        if contract_ids:
                            if len(contract_ids)>1:
                                print "dos contratos", aux_ced_ruc
                            if sh.cell(r,11).value:
                                aux_wage = float(sh.cell(r,11).value)
                                if not aux_wage>0:
                                    aux_wage = float(sh.cell(r,12).value)
                            else:
                                aux_wage = float(sh.cell(r,12).value)
                            num += 1
                            contract_obj.write(cr, uid, contract_ids[0],{
                                'wage':aux_wage,
                            })
                        else:
                            print "NO CONTRATO", aux_ced_ruc
                    else:
                        print "NO EMPLEADO", aux_ced_ruc
        print "CONTRATOS ACTUALIZADOS", num
        return True

    def cuentaPartidaMil(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        budget_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}   
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['municipio'] == 'mil':
                for r in range(sh.nrows)[1:]:
                    code_aux = sh.cell(r,3).value
                    account_ids = account_obj.search(cr, uid, [('code','=',code_aux),('type','!=','view')])
                    if account_ids:
                        aux_code_budget = sh.cell(r,1).value
                        if int(aux_code_budget[0:1])>3:
                            aux_code_budget = aux_code_budget[0:6]
                        else:
                            if int(aux_code_budget[7])>0:
                                aux_code_budget = aux_code_budget[0:8]
                            else:
                                aux_code_budget = aux_code_budget[0:6]
                        partida_ids = budget_obj.search(cr, uid, [('code','=',aux_code_budget)])
                        if partida_ids:
                            account_obj.write(cr, uid, account_ids[0],{
                                'budget_id':partida_ids[0],
                            })
                        else:
                            print "NOPARTIDA", aux_code_budget
                    else:
                        print "NOCUENTA", code_aux
        return True

    def updatePrecioCostoMil(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        categ_obj = self.pool.get('product.category')
        subcateg_obj = self.pool.get('product.subcategory')
        uom_obj = self.pool.get('product.uom')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['municipio'] == 'mil':
                for r in range(sh.nrows)[1:]:
                    aux_cantidad = float(sh.cell(r,5).value)
                    a = True
                    if a:
                        uom_aux = ustr(sh.cell(r,4).value)
                        code_aux = sh.cell(r,0).value
                        uom_ids = uom_obj.search(cr, uid, [('name','=',uom_aux)],limit=1)
                        product_ids = product_obj.search(cr, uid, [('default_code','=',code_aux),('uom_id','=',uom_ids[0])])
                        if product_ids:
                            costo_aux = float(sh.cell(r,6).value)
                            product = product_obj.browse(cr, uid, product_ids[0])
                            product_obj.write(cr, uid, product_ids[0],{
                                'standard_price':costo_aux,
                                'loc_rack':'A',
                            })
                        else:
                            print "no Producto",ustr(sh.cell(r,0).value)
                            aux_categ = ustr(sh.cell(r,9).value)
                            subcateg_aux = ustr(sh.cell(r,2).value)
                            categ_ids = categ_obj.search(cr, uid, [('name','like',aux_categ),('budget','=','corriente')],limit=1)
                            subcateg_ids = subcateg_obj.search(cr, uid, [('name','=',subcateg_aux)])
                            if not subcateg_ids:
                                subcateg_id = subcateg_obj.create(cr, uid, {
                                    'name':subcateg_aux,
                                    'categ_id':categ_ids[0],
                                })
                            else:
                                subcateg_id = subcateg_ids[0]
                            uom_ids = uom_obj.search(cr, uid, [('name','=',uom_aux)],limit=1)
                            product_obj.create(cr, uid, {
                                'name':ustr(sh.cell(r,3).value),
                                'default_code':ustr(sh.cell(r,0).value),
                                'type':'product',
                                'cost_method':'average',
                                'standard_price':float(sh.cell(r,6).value),
                                'categ_id':categ_ids[0],
                                'subcateg_id':subcateg_id,
                                'uom_id':uom_ids[0],
                                'uom_po_id':uom_ids[0],
                                'uos_id':uom_ids[0],
                            },context=None)
        return True

    def inventarioInicialMil(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')
        location_obj = self.pool.get('stock.location')
        inicial_obj = self.pool.get('stock.inventory')
        line_obj = self.pool.get('stock.inventory.line')
        inicial_id = inicial_obj.create(cr, uid, {
            'name':'Inventario Inicial',
        })
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        location_ids = location_obj.search(cr, uid, [('name','=','Stock')])
        if location_ids:
            location_id = location_ids[0]
        else:
            print "NO LOCATION"
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                if data['municipio'] == 'mil':
                    aux_cantidad = float(sh.cell(r,5).value)
                    if aux_cantidad>0:
                        code_aux = sh.cell(r,0).value
                        aux_udm = ustr(sh.cell(r,4).value)
                        #buscar con la udm
                        uom_ids = uom_obj.search(cr, uid, [('name','=',aux_udm)])
                        product_ids = product_obj.search(cr, uid, [('default_code','=',code_aux),('uom_id','=',uom_ids[0])])
                        if product_ids:
                            costo_aux = float(sh.cell(r,6).value)
                            product = product_obj.browse(cr, uid, product_ids[0])
                            product_obj.write(cr, uid, product_ids[0],{
                                'standard_price':costo_aux,
                            })
                            line_obj.create(cr, uid, {
                                'product_id':product_ids[0],
                                'inventory_id':inicial_id,
                                'product_uom':product.uom_id.id,
                                'product_qty':aux_cantidad,
                                'location_id':location_id,
                                'category_id':product.categ_id.id,
                            })
                        else:
                            print "No producto", code_aux
                            
                    else:
                        code_aux = sh.cell(r,0).value
                        product_ids = product_obj.search(cr, uid, [('default_code','=',code_aux)])
                        if product_ids:
                            costo_aux = float(sh.cell(r,6).value)
                            product = product_obj.browse(cr, uid, product_ids[0])
                            product_obj.write(cr, uid, product_ids[0],{
                                'standard_price':costo_aux,
                            })
        return True

    def updateSujetoControlMil(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        categ_obj = self.pool.get('account.asset.category')
        subcateg_obj = self.pool.get('asset.asset.subcateg')
        department_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        job_obj = self.pool.get('hr.job')
        partner_obj = self.pool.get('res.partner')
        acc_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            j = 0
            if data['municipio'] == 'mil': 
                for r in range(sh.nrows)[1:]:
                    aux_code = str(sh.cell(r,7).value)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code),('type','=','Sujeto a Control')])
                    if asset_ids:
                        aux_code_categ = str(sh.cell(r,5).value)[0:7]
                        categ_ids = categ_obj.search(cr, uid, [('type_asset','=','sujeto_control'),('code','=',aux_code_categ)],limit=1)
                        if not categ_ids:
                            import pdb
                            pdb.set_trace()
                            categ_ids = categ_obj.search(cr, uid, [('type_asset','=','sujeto_control')],limit=1)
                            print "NO CATEG", aux_code_categ, aux_code_completo
                        aux_subcateg_name = ustr(sh.cell(r,6).value)
                        subcateg_ids = subcateg_obj.search(cr, uid, [('categ_id','=',categ_ids[0]),('name','=',aux_subcateg_name)],limit=1)
                        if subcateg_ids:
                            subcateg_id = subcateg_ids[0]
                        else:
                            subcateg_id = subcateg_obj.create(cr, uid, {
                                'categ_id':categ_ids[0],
                                'name':aux_subcateg_name,
                            },context=None)
                        dept_ids = department_obj.search(cr, uid, [('name','=',ustr(sh.cell(r,20).value))],limit=1)
                        if len(dept_ids)>0:
                            dep_id = dept_ids[0]
                        else:
                            print "nodept", ustr(sh.cell(r,20).value)
                            dep_id = department_obj.create(cr, uid, {
                                'name': ustr(sh.cell(r,20).value),
                                'sequence':'000',
                            })
                        emp_ids = employee_obj.search(cr, uid, [('name','=',str(sh.cell(r,17).value))],limit=1)
                        if len(emp_ids)>0:
                            emp_id = emp_ids[0]
                        else:
                            job_ids = job_obj.search(cr, uid, [])
                            emp_id = employee_obj.create(cr, uid, {
                                'name':ustr(sh.cell(r,17).value),
                                'id_type':'p',
                                'employee_first_lastname':ustr(sh.cell(r,18).value),
                                'employee_first_name':' ',
                                'department_id':dep_id,
                                'job_id':job_ids[0],
                                'address':'SD',
                                'house_phone':'0000000',
                            })
                        aux_ruc = sh.cell(r,12).value
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ruc)],limit=1)
                        if partner_ids:
                            partner_id = partner_ids[0]
                        else:
                            print "NOPARTNER", aux_ruc
                            partner_id = partner_obj.create(cr, uid, {
                                'ced_ruc':aux_ruc,
                                'type_ced_ruc':'otro',
                                'tipo_persona':'6',
                                'name':ustr(sh.cell(r,12).value),
                                'direccion':'SD',
                                'telefono':'SN',
                                'email':'info@gmail.com',
                            })
                        asset_obj.write(cr, uid, asset_ids[0],{
                            'categ_id':categ_ids[0],
                            'subcateg_id':subcateg_id,
                            'department_id':dep_id,
                            'employee_id':emp_id,
                            'partner_id':partner_id,
                        })
                        j+=1
        print "total activos creados", j
        return True

    def loadSujetoControlMil(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        categ_obj = self.pool.get('account.asset.category')
        subcateg_obj = self.pool.get('asset.asset.subcateg')
        department_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        job_obj = self.pool.get('hr.job')
        partner_obj = self.pool.get('res.partner')
        acc_obj = self.pool.get('account.account')
        tipotr_obj = self.pool.get('gt.account.asset.transaction')
        componente_obj = self.pool.get('gt.account.asset.componente')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            j = 0
            if data['municipio'] == 'mil': 
                subcateg_ids = subcateg_obj.search(cr, uid, [],limit=1)
                tr_ids = tipotr_obj.search(cr, uid,[],limit=1)
                dept_ids = department_obj.search(cr, uid, [],limit=1)
                emp_ids = employee_obj.search(cr, uid, [],limit=1)
                for r in range(sh.nrows)[1:]:
                    
                    aux_estado = 'open'
                    aux_c = ustr(sh.cell(r,7).value) 
                    if aux_c=='BUEN ESTAD':
                        aux_condicion = 'Bueno'
                    elif aux_c=='REGULAR':
                        aux_condicion = 'Regular'
                    elif aux_c=='MALO':
                        aux_condicion='Malo'
                    #code quitar las letras
                    aux_code_completo = sh.cell(r,0).value
                    aux_code_categ = str(sh.cell(r,8).value)[0:7]
                    categ_ids = categ_obj.search(cr, uid, [('type_asset','=','sujeto_control'),('code','=',aux_code_categ)],limit=1)
                    if not categ_ids:
                        categ_ids = categ_obj.search(cr, uid, [('type_asset','=','sujeto_control')],limit=1)
                        print "NO CATEG", aux_code_categ, aux_code_completo
                    guion = aux_code_completo.find("-")
                    aux_code = aux_code_completo[guion+1:]
                    activo_id = asset_obj.create(cr, uid, {
                        'code_ant':aux_code_completo,
                        'code':aux_code,
                        'type':'Sujeto a Control',
                        'serial_number':'',
                        'subcateg_id':subcateg_ids[0],
                        'category_id':categ_ids[0],
                        'department_id':dept_ids[0],
                        'name':ustr(sh.cell(r,2).value),
                        'purchase_value':sh.cell(r,6).value,
                        #'salvage_value':sh.cell(r,39).value,
                        'purchase_date':str(sh.cell(r,5).value),
                        'employee_id':emp_ids[0],
                        'state':aux_estado,
                        'condicion':aux_condicion,
                        'origen_fondo':'Propios',
                        'transaction_id':tr_ids[0],
                        #'residual':sh.cell(r,40).value,
                        'invoice_id':sh.cell(r,3).value,
                        'otros_accesorios':ustr(sh.cell(r,2).value),
                        'note':ustr(sh.cell(r,2).value),
                    })
                    j+=1
        print "total activos creados", j
        return True

    def loadActivosMil(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        categ_obj = self.pool.get('account.asset.category')
        subcateg_obj = self.pool.get('asset.asset.subcateg')
        department_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        job_obj = self.pool.get('hr.job')
        partner_obj = self.pool.get('res.partner')
        acc_obj = self.pool.get('account.account')
        tipotr_obj = self.pool.get('gt.account.asset.transaction')
        componente_obj = self.pool.get('gt.account.asset.componente')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            #r = 2296
            j = 0 
            for r in range(sh.nrows)[1:]:
                if data['municipio'] == 'mil':
                    if len(str(sh.cell(r,2).value))>1:
                        categ_ids = categ_obj.search(cr, uid, [('name','=',ustr(sh.cell(r,2).value))],limit=1)
                        if not categ_ids:
                            print "NO CATEG",ustr(sh.cell(r,2).value)
                        subcateg_ids = subcateg_obj.search(cr, uid, [('name','=',ustr(sh.cell(r,6).value))],limit=1)
                        if subcateg_ids:
                            subcateg_id = subcateg_ids[0]
                        else:
                            subcateg_id = subcateg_obj.create(cr, uid, {
                                'name':ustr(sh.cell(r,6).value),
                                'categ_id':categ_ids[0],
                            },context)
                        tr_ids = tipotr_obj.search(cr, uid,[],limit=1)
                        dept_ids = department_obj.search(cr, uid, [('name','=',ustr(sh.cell(r,20).value))],limit=1)
                        if len(dept_ids)>0:
                            dep_id = dept_ids[0]
                        else:
                            print "nodept", ustr(sh.cell(r,20).value)
                            dep_id = department_obj.create(cr, uid, {
                                'name': ustr(sh.cell(r,20).value),
                                'sequence':'000',
                            })
                    emp_ids = employee_obj.search(cr, uid, [('name','=',str(sh.cell(r,17).value))],limit=1)
                    if len(emp_ids)>0:
                        emp_id = emp_ids[0]
                    else:
                        job_ids = job_obj.search(cr, uid, [])
                        emp_id = employee_obj.create(cr, uid, {
                            'name':ustr(sh.cell(r,17).value),
                            'id_type':'p',
                            'employee_first_lastname':ustr(sh.cell(r,18).value),
                            'employee_first_name':' ',
                            'department_id':dep_id,
                            'job_id':job_ids[0],
                            'address':'SD',
                            'house_phone':'0000000',
                        })
                        #emp_ids = employee_obj.search(cr, uid, [('name','=','123456789')],limit=1)
                        #emp_id = emp_ids[0]
                    aux_estado = 'open'
                    aux_c = ustr(sh.cell(r,16).value) 
                    if aux_c=='BUEN ESTAD':
                        aux_condicion = 'Bueno'
                    elif aux_c=='REGULAR':
                        aux_condicion = 'Regular'
                    elif aux_c=='M/E':
                        aux_condicion='Malo'
                    aux_ruc = sh.cell(r,12).value
                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ruc)],limit=1)
                    if partner_ids:
                        partner_id = partner_ids[0]
                    else:
                        print "NOPARTNER", aux_ruc
                        partner_id = partner_obj.create(cr, uid, {
                            'ced_ruc':aux_ruc,
                            'type_ced_ruc':'otro',
                            'tipo_persona':'6',
                            'name':ustr(sh.cell(r,12).value),
                            'direccion':'SD',
                            'telefono':'SN',
                            'email':'info@gmail.com',
                        })
                    activo_id = asset_obj.create(cr, uid, {
                        'code':ustr(sh.cell(r,7).value),
                        'type':str(sh.cell(r,0).value),
                        'serial_number':ustr(sh.cell(r,4).value),
                        'subcateg_id':subcateg_id,
                        'category_id':categ_ids[0],
                        'department_id':dep_id,
                        'name':sh.cell(r,8).value,
                        'purchase_value':sh.cell(r,10).value,
                        #'salvage_value':sh.cell(r,39).value,
                        'purchase_date':str(sh.cell(r,11).value),
                        'employee_id':emp_id,
                        'state':aux_estado,
                        'condicion':aux_condicion,
                        'origen_fondo':'Propios',
                        'transaction_id':tr_ids[0],
                        #'residual':sh.cell(r,40).value,
                        'invoice_id':sh.cell(r,15).value,
                        'partner_id':partner_id,
                        'otros_accesorios':ustr(sh.cell(r,21).value),
                        'note':ustr(sh.cell(r,21).value),
                    })
                    j+=1
        print "total activos creados", j
        return True

    def loadSancionesMil(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        sancion_obj = self.pool.get('employee.sancion')
        department_obj = self.pool.get('hr.department')
        job_obj = self.pool.get('hr.job')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:
                    aux_ced_ruc = str(sh.cell(r,1).value)
                    emp_ids = employee_obj.search(cr, uid, [('name','=',aux_ced_ruc)])
                    if emp_ids:
                        aux_dept = ustr(sh.cell(r,3).value)
                        department_ids = department_obj.search(cr, uid, [('name','=',aux_dept)])
                        if department_ids:
                            department_id = department_ids[0]
                        else:
                            department_id = department_obj.create(cr, uid, {
                                'name':aux_dept,
                            })
                        aux_job = ustr(sh.cell(r,4).value)
                        cargo_ids = job_obj.search(cr, uid, [('name','=',aux_job)])
                        if cargo_ids:
                            cargo_id = cargo_ids[0]
                        else:
                            cargo_id = job_obj.create(cr, uid, {
                                'name':aux_job,
                            })
                        verbal = verbal1 = escrita = escrita1 = pecuniaria = visto_bueno = destitucion = ''
                        if sh.cell(r,6).value:
                            verbal = ustr(sh.cell(r,6).value)
                        if sh.cell(r,7).value:
                            verbal1 = ustr(sh.cell(r,7).value)
                        if sh.cell(r,8).value:
                            escrita = ustr(sh.cell(r,8).value)
                        if sh.cell(r,9).value:
                            escrita1 = ustr(sh.cell(r,9).value)
                        if sh.cell(r,10).value:
                            pecuniaria = ustr(sh.cell(r,10).value)
                        if sh.cell(r,11).value:
                            visto_bueno = ustr(sh.cell(r,11).value)
#                        if sh.cell(r,12).value:
#                            destitucion = ustr(sh.cell(r,12).value)
                        sancion_id = sancion_obj.create(cr, uid, {
                            'employee_id':emp_ids[0],
                            'name':data['hr_period_id'][0],
                            'department_id':department_id,
                            'cargo':cargo_id,
                            'fecha_ingreso':sh.cell(r,5).value,
                            'verbal':verbal,
                            'verbal1':verbal1,
                            'escrita':escrita,
                            'escrita1':escrita1,
                            'pecuniaria':pecuniaria,
                            'visto_bueno':visto_bueno,
                            'destitucion':destitucion,
                        }) 
                    else:
                        print "NO EMPLEADO", aux_ced_ruc
        return True

    def loadVacacionesMil(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        holi_obj = self.pool.get('holidays.period')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:
                    aux_ced_ruc = str(sh.cell(r,0).value)
                    emp_ids = employee_obj.search(cr, uid, [('name','=',aux_ced_ruc)])
                    if emp_ids:
                        aux_2010_11 = float(sh.cell(r,2).value)
                        if aux_2010_11!=0:
                            holi_obj.create(cr, uid, {
                                'name':'2010 - 2011',
                                'days_normal':aux_2010_11,
                                'date_start':'2010-01-01',
                                'date_stop':'2010-12-31',
                                'employee_id':emp_ids[0],
                            })
                        aux_2011_12 = float(sh.cell(r,3).value)
                        if aux_2011_12!=0:
                            holi_obj.create(cr, uid, {
                                'name':'2011 - 2012',
                                'days_normal':aux_2011_12,
                                'date_start':'2011-01-01',
                                'date_stop':'2011-12-31',
                                'employee_id':emp_ids[0],
                            })
                        aux_2012_13 = float(sh.cell(r,4).value)
                        if aux_2012_13!=0:
                            holi_obj.create(cr, uid, {
                                'name':'2012 - 2013',
                                'days_normal':aux_2012_13,
                                'date_start':'2012-01-01',
                                'date_stop':'2012-12-31',                                
                                'employee_id':emp_ids[0],
                            })
                        aux_2013_14 = float(sh.cell(r,5).value)
                        if aux_2013_14!=0:
                            holi_obj.create(cr, uid, {
                                'name':'2013 - 2014',
                                'days_normal':aux_2013_14,
                                'date_start':'2013-01-01',
                                'date_stop':'2013-12-31',
                                'employee_id':emp_ids[0],
                            })
                        aux_2014_15 = float(sh.cell(r,6).value)
                        if aux_2014_15!=0:
                            holi_obj.create(cr, uid, {
                                'name':'2014 - 2015',
                                'days_normal':aux_2014_15,
                                'date_start':'2014-01-01',
                                'date_stop':'2014-12-31',
                                'employee_id':emp_ids[0],
                            })
                        aux_2015_16 = float(sh.cell(r,7).value)
                        if aux_2015_16!=0:
                            holi_obj.create(cr, uid, {
                                'name':'2015 - 2016',
                                'days_normal':aux_2015_16,
                                'date_start':'2015-01-01',
                                'date_stop':'2015-12-31',
                                'employee_id':emp_ids[0],
                            })
                        aux_2016_17 = float(sh.cell(r,8).value)
                        if aux_2016_17!=0:
                            holi_obj.create(cr, uid, {
                                'name':'2016 - 2017',
                                'days_normal':aux_2016_17,
                                'date_start':'2016-01-01',
                                'date_stop':'2016-12-31',
                                'employee_id':emp_ids[0],
                            })
                    else:
                        print "NO EMPLEADO", aux_ced_ruc
        return True

    def updateObreroSalario(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:
                    aux_ced_ruc = str(sh.cell(r,2).value)
                    emp_ids = employee_obj.search(cr, uid, [('name','=',aux_ced_ruc)])
                    if emp_ids:
                        contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp_ids[0])])
                        if contract_ids:
                            aux_wage = float(sh.cell(r,3).value)
                            num += 1
                            contract_obj.write(cr, uid, contract_ids[0],{
                                'wage':aux_wage,
                            })
                        else:
                            print "NO CONTRATO", aux_ced_ruc
                    else:
                        print "NO EMPLEADO", aux_ced_ruc
        print "CONTRATOS ACTUALIZADOS", num
        return True


    def loadCtasBancoMil(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        b_obj = self.pool.get('res.bank')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:
                    aux_ced_ruc = str(sh.cell(r,0).value)
                    paga_cedula = False
                    if len(aux_ced_ruc)<=10:
                        partner_ids1 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                        if partner_ids1:
                            paga_cedula = True
                        partner_ids2 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc+'001')])
                    else:
                        partner_ids1 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                        partner_ids2 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc[0:10])])
                        if partner_ids2:
                            paga_cedula = True
                    partner_ids = partner_ids1 + partner_ids2
                    if partner_ids:
                        if len(partner_ids)>1:
                            print "partnerduplicado", aux_ced_ruc
#                            raise osv.except_osv(('Partner duplicado!'),'Partner con cedula/ruc'%(str(sh.cell(r,0).value)))
                        else:
                            partner_id = partner_ids[0]
                            if paga_cedula:
                                partner_obj.write(cr, uid, partner_id,{
                                    'pagar_spi':paga_cedula,
                                })
                    else:
                        print "No partner", aux_ced_ruc
                        aux_tipo = 'cedula'
                        aux_persona = '6'
                        if len(aux_ced_ruc)>10:
                            aux_tipo = 'ruc'
                        partner_id = partner_obj.create(cr, uid, {
                            'ced_ruc':aux_ced_ruc,
                            'type_ced_ruc':aux_tipo,
                            'tipo_persona':aux_persona,
                            'name':ustr(sh.cell(r,2).value),
                            'direccion':'MILAGRO',
                            'telefono':'2222222',
                            'email':'info@gmail.com',
                            'pagar_spi':paga_cedula,
                            'property_account_receivable':1689,
                            'property_account_payable':2823,
                            'property_account_position':2,
                        })
                    nom_banco = ustr(sh.cell(r,3).value)
                    bank_ids = b_obj.search(cr, uid, [('name','=',nom_banco)])
                    if not bank_ids:
                        print "NO HAY BANCO", nom_banco
                    else:
                        tipo_c = str(sh.cell(r,6).value)
                        if tipo_c=='CORRIENTE':
                            tipo_c_aux = 'cte'
                        else:
                            tipo_c_aux = 'aho'
                        #cuenta_ids = bank_obj.search(cr, uid, [('partner_id','=',partner_id),('bank','=',bank_ids[0]),('type_cta','=',tipo_c_aux),('acc_number','=',str(sh.cell(r,5).value))])
                        cuenta_ids = bank_obj.search(cr, uid, [('partner_id','=',partner_id)])
                        if not cuenta_ids:
                            bank_obj.create(cr, uid, {
                                'partner_id':partner_id,
                                'bank':bank_ids[0],
                                'type_cta':tipo_c_aux,
                                'acc_number':str(sh.cell(r,5).value),
                            })
                            num += 1
                        #    print "cuenta creada"
                        else:
                            print "no se crea cuenta"
        print num, " cuentas creadas"

    def loadCtasBancoJubiladoR(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        b_obj = self.pool.get('res.bank')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio']:
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                j = 0
                for r in range(sh.nrows)[1:]:
                    aux_ced_ruc = str(sh.cell(r,0).value)
                    paga_cedula = False
                    if len(aux_ced_ruc)<=10:
                        partner_ids1 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                        if partner_ids1:
                            paga_cedula = True
                        partner_ids2 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc+'001')])
                    else:
                        partner_ids1 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                        partner_ids2 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc[0:10])])
                        if partner_ids2:
                            paga_cedula = True
                    partner_ids = partner_ids1 + partner_ids2
                    if partner_ids:
                        if len(partner_ids)>1:
                            print "partnerduplicado", aux_ced_ruc
#                            raise osv.except_osv(('Partner duplicado!'),'Partner con cedula/ruc'%(str(sh.cell(r,0).value)))
                        else:
                            partner_id = partner_ids[0]
                            if paga_cedula:
                                partner_obj.write(cr, uid, partner_id,{
                                    'pagar_spi':paga_cedula,
                                })
                    else:
                        print "No partner", aux_ced_ruc
                        aux_tipo = 'cedula'
                        aux_persona = '6'
                        if len(aux_ced_ruc)>10:
                            aux_tipo = 'ruc'
                        partner_id = partner_obj.create(cr, uid, {
                            'ced_ruc':aux_ced_ruc,
                            'type_ced_ruc':aux_tipo,
                            'tipo_persona':aux_persona,
                            'name':ustr(sh.cell(r,2).value),
                            'direccion':'MILAGRO',
                            'telefono':'2222222',
                            'email':'info@gmail.com',
                            'pagar_spi':paga_cedula,
                            'property_account_receivable':1689,
                            'property_account_payable':2823,
                            'property_account_position':2,
                        })
                    nom_banco = ustr(sh.cell(r,2).value)
                    bank_ids = b_obj.search(cr, uid, [('bic','=',nom_banco)])
                    if not bank_ids:
                        print "NO HAY BANCO", nom_banco
                    else:
                        tipo_c_aux = 'aho'
                        cuenta_ids = bank_obj.search(cr, uid, [('partner_id','=',partner_id)])
                        if not cuenta_ids:
                            bank_obj.create(cr, uid, {
                                'partner_id':partner_id,
                                'bank':bank_ids[0],
                                'type_cta':tipo_c_aux,
                                'acc_number':str(sh.cell(r,4).value),
                            })
                            num += 1
                        #    print "cuenta creada"
                        else:
                            print "no se crea cuenta"
        print num, " cuentas creadas"

    def loadCtasBancoMilTeso(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        b_obj = self.pool.get('res.bank')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:
                    aux_ced_ruc = str(sh.cell(r,0).value)
                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                    if partner_ids:
                        if len(partner_ids)>1:
                            raise osv.except_osv(('Partner duplicado!'),'Partner con cedula/ruc'%(str(sh.cell(r,0).value)))
                        else:
                            partner_id = partner_ids[0]
                    else:
                        print "No partner", aux_ced_ruc
                        aux_tipo = 'cedula'
                        aux_persona = '6'
                        if len(aux_ced_ruc)>10:
                            aux_tipo = 'ruc'
                        partner_id = partner_obj.create(cr, uid, {
                            'ced_ruc':aux_ced_ruc,
                            'type_ced_ruc':aux_tipo,
                            'tipo_persona':aux_persona,
                            'name':ustr(sh.cell(r,1).value),
                            'direccion':'MILAGRO',
                            'telefono':'2222222',
                            'property_account_receivable':1689,
                            'property_account_payable':2823,
                            'property_account_position':2,
                        })
                    nom_banco = ustr(sh.cell(r,3).value)
                    bank_ids = b_obj.search(cr, uid, [('name','=',nom_banco)])
                    if not bank_ids:
                        print "NO HAY BANCO", nom_banco
                        banco_id = banco_obj.create(cr, uid, {
                            'name':nom_banco,
                            'bic':nom_banco,
                            'desc':nom_banco[0:4],
                        })
                        bank_ids.append(banco_id)
                    else:
                        tipo_c = str(sh.cell(r,6).value)
                        if tipo_c in ('CORRIENTE','1'):
                            tipo_c_aux = 'cte'
                        else:
                            tipo_c_aux = 'aho'
                        #cuenta_ids = bank_obj.search(cr, uid, [('partner_id','=',partner_id),('bank','=',bank_ids[0]),('type_cta','=',tipo_c_aux),('acc_number','=',str(sh.cell(r,5).value))])
                        cuenta_ids = bank_obj.search(cr, uid, [('partner_id','=',partner_id)])
                        if not cuenta_ids:
                            bank_obj.create(cr, uid, {
                                'partner_id':partner_id,
                                'bank':bank_ids[0],
                                'type_cta':tipo_c_aux,
                                'acc_number':str(sh.cell(r,5).value),
                            })
                            num += 1
                        #    print "cuenta creada"
                        else:
                            print "no se crea cuenta"
        print num, " cuentas creadas"

    def updateCargoMil(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        job_id = self.pool.get('hr.job')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                for r in range(sh.nrows)[1:]:
                    aux_cedula = ustr(sh.cell(r,0).value)
                    employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)],limit=1)
                    if employee_ids:
                        aux_cargo = ustr(sh.cell(r,3).value)
                        contract_ids = contract_obj.search(cr, uid, [('employee_id','=',employee_ids[0])])
        return True

    def loadPartidaMil(self, cr, uid, ids, context=None):
        program_obj = self.pool.get('project.program')
        item_obj = self.pool.get('budget.item')
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            if data['municipio'] == 'mil':
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                actualizados = 0
                for r in range(sh.nrows)[1:]:
                    aux_cedula = ustr(sh.cell(r,0).value)
                    employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)],limit=1)
                    if employee_ids:
                        contract_ids = contract_obj.search(cr, uid, [('employee_id','=',employee_ids[0])])
                        if contract_ids:
                            aux_program1 = ustr(sh.cell(r,1).value)[0:4]
                            program_ids = program_obj.search(cr, uid, [('sequence','=',aux_program1)],limit=1)
                            if not program_ids:
                                print "NO POGAMA", aux_program1
                                continue
                            aux_budget = ustr(sh.cell(r,3).value)[0:9].replace('.','')
                            post_ids = post_obj.search(cr, uid, [('code','=',aux_budget)],limit=1)
                            if post_ids:
                                item_ids = item_obj.search(cr, uid, [('program_id','=',program_ids[0]),('budget_post_id','=',post_ids[0])],limit=1)
                                if item_ids:
                                    actualizados += 1
                                    contract_obj.write(cr, uid, contract_ids[0],{
                                        'program_id':program_ids[0],
                                        'activo':True,
                                        'budget_id':item_ids[0],})
        
                                else:
                                    print 'NO ITEMMMSSS cedula programa budget', aux_cedula, aux_program1, aux_budget
                            else:
                                print "NO POST", aux_budget, aux_cedula
                        else:
                            print "NBO CONTrATo", aux_cedula
                    else:
                        print "NO EMPLEADO", aux_cedula
        print "TOTAL ACTUALIZADPS", actualizados
        return True
    ##
    def depuraCargos(self, cr, uid, ids, context=None):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        department_obj = self.pool.get('hr.department')
        cargos = {}
        aux = """select name,department_id from hr_job group by name, department_id order by name,department_id"""
        cr.execute(aux)
        res = cr.fetchall()
        if res:
            for cargo in res:
                cargo_elimina = []
                cargo_ids = job_obj.search(cr, uid, [('name','=',cargo[0]),('department_id','=',cargo[1])])
                cargo_id = cargo_ids[0]
                if len(cargo_ids)>1:
                    for cargo_id2 in cargo_ids:
                        if cargo_id2!=cargo_id:
                            employee_ids = employee_obj.search(cr, uid, [('job_id','=',cargo_id2),('department_id','=',cargo[1])])
                            if employee_ids:
                                employee_obj.write(cr, uid, employee_ids,{'job_id':cargo_id})
                            #job_obj.unlink(cr, uid, [cargo_id2])
        return True

    def updateActivoNull(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        asset_ids = asset_obj.search(cr, uid, [('department_id','=',False)])
        if asset_ids:
            updated = 0
            aux_total = len(asset_ids)
            for asset_id in asset_ids:
                asset = asset_obj.browse(cr, uid, asset_id)
                cr.execute('''update account_asset_asset set department_id=%s where id=%s'''%(asset.employee_id.department_id.id,asset_id))
#                asset_obj.write(cr, uid, [asset_id],{'department_id':asset.employee_id.department_id.id,})
                updated += 1 
        print "ACTUALIZADOS", aux_total, updated
        return True

    def actualizaTotalRol(self, cr, uid, ids, context=None):
        run_obj = self.pool.get('hr.payslip.run')
        run_ids = run_obj.search(cr, uid, [('date_end','<=','2016-12-31')])
        if run_ids:
            total_actualizado = 0
            for run_id in run_ids:
                run_obj.recalcular_roles(cr, uid, [run_id])
                total_actualizado += 1
        print "TOTAL ROLES",total_actualizado        
        return True

    def depuraCtasBanco(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        move_obj = self.pool.get('account.move')
        contract_obj = self.pool.get('hr.contract')
        employee_obj = self.pool.get('hr.employee')
        partner_ids = partner_obj.search(cr, uid, [])
        for partner_id in partner_ids:
            partner=partner_obj.browse(cr, uid, partner_id)
            if len(partner.bank_ids)>1:
                if partner.bank_ids[0].acc_number!=partner.bank_ids[1].acc_number:
                    if partner.bank_ids[0].acc_number!=partner.bank_ids[1].acc_number[1:]:
                        move_ids = move_obj.search(cr, uid, [('partner_id','=',partner_id)])
                        employee_ids = employee_obj.search(cr, uid, [('name','=',partner.ced_ruc)])
                        if employee_ids:
                            contract_ids = contract_obj.search(cr, uid, [('employee_id','=',employee_ids[0])])
                        if move_ids:
                            print "DIFIERE NUMEROy tiene moves", partner.ced_ruc,partner.bank_ids[0].acc_number,partner.bank_ids[1].acc_number
                        else:
                            if contract_ids:
                                print "DIFIERE NUMEROy tiene contrato", partner.ced_ruc,partner.bank_ids[0].acc_number,partner.bank_ids[1].acc_number
                            else:
                                print "DIFIERE NUMERO", partner.ced_ruc,partner.name,partner.bank_ids[0].acc_number,partner.bank_ids[1].acc_number
                else:
                    if partner.bank_ids[0].bank.id!=partner.bank_ids[1].bank.id:
                        print "DIFIERE BANCO", partner.ced_ruc,partner.name,partner.bank_ids[0].acc_number,partner.bank_ids[1].acc_number
                    else:
                        print "HDp quitada cuenta", partner.ced_ruc,partner.name,partner.bank_ids[0].acc_number,partner.bank_ids[1].acc_number
                        bank_obj.unlink(cr, uid, [partner.bank_ids[0].id])
        return True

    def asientosSinDet(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        move_ids = move_obj.search(cr, uid, [('state','=','posted')])
        lista = []
        if move_ids:
            for move_id in move_ids:
                move_line_ids = move_line_obj.search(cr, uid, [('move_id','=',move_id)])
                if not move_line_ids:
                    lista.append(move_id)
        print "LISTA DE MOVES", lista
        return True

    def loadProntoPago(self, cr, uid, ids, context=None):
        itemm_obj = self.pool.get('budget.item.migrated')
        move_line_obj = self.pool.get('account.move.line')
        for this in self.browse(cr, uid, ids):
            move_line_ids = move_line_obj.search(cr, uid, [('name','=','Cobro'),('move_id.date','>=','2017-01-01'),('debit','>',0),('account_id','=',1435)])
            if move_line_ids:
                for move_line_id in move_line_ids:
                    move_line = move_line_obj.browse(cr, uid, move_line_id)
                    aux_desc = move_line.budget_post.code + ' - ' + move_line.budget_post.name
                    itemm_id = itemm_obj.create(cr, uid, {
                        'budget_item_id':move_line.budget_id.id,
                        'budget_post_id':move_line.budget_post.id,
                        'commited_amount':move_line.debit,
                        'date':move_line.move_id.date,
                        'program_code':move_line.budget_id.program_id.sequence,
                        'type_budget':'gasto',
                        'move_id':move_line.move_id.id,
                        'is_pronto':True,
                        'desc':aux_desc,
                    })
        return True

    def recuperaAsientosDet(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids)[0]
        move_line_obj = self.pool.get('account.move.line')
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                j=0
                for r in range(sh.nrows)[1:]:
                    aux_ref = ' '
                    aux_debit = aux_credit = 0
                    aux_devengado = aux_pagado = False
                    if sh.cell(r,13).value:
                        aux_credit = sh.cell(r,13).value
                    if sh.cell(r,18).value:
                        aux_debit = sh.cell(r,18).value
                    if sh.cell(r,19).value:
                        aux_ref = sh.cell(r,19).value
                    if sh.cell(r,39).value:
                        if sh.cell(r,39).value=='t':
                            aux_devengado = True
                    if sh.cell(r,41).value:
                        if sh.cell(r,41).value=='t':
                            aux_pagado = True
                    print "NUMERO", j
                    if sh.cell(r,36).value:
                        if sh.cell(r,9).value:
                            sql = '''INSERT INTO account_move_line (
                            id,journal_id,credit,debit,account_id,period_id,date,move_id,name,ref,partner_id,budget_id_cert,budget_post,budget_accrued,budget_paid,budget_id) VALUES (%s,%s,%s,%s,%s,%s,'%s',%s,'%s','%s',%s,%s,%s,'%s','%s',%s)'''%(int(sh.cell(r,0).value),int(sh.cell(r,6).value),aux_credit,aux_debit,int(sh.cell(r,20).value),int(sh.cell(r,21).value),sh.cell(r,23).value,int(sh.cell(r,24).value),ustr(sh.cell(r,25).value),aux_ref,int(sh.cell(r,9).value),int(sh.cell(r,36).value),int(sh.cell(r,38).value),aux_devengado,aux_pagado,int(sh.cell(r,42).value))
                            cr.execute(sql)
                        else:
                            sql = '''INSERT INTO account_move_line (
                            id,journal_id,credit,debit,account_id,period_id,date,move_id,name,ref,budget_id_cert,budget_post,budget_accrued,budget_paid,budget_id) VALUES (%s,%s,%s,%s,%s,%s,'%s',%s,'%s','%s',%s,%s,'%s','%s',%s)'''%(int(sh.cell(r,0).value),int(sh.cell(r,6).value),aux_credit,aux_debit,int(sh.cell(r,20).value),int(sh.cell(r,21).value),sh.cell(r,23).value,int(sh.cell(r,24).value),ustr(sh.cell(r,25).value),aux_ref,int(sh.cell(r,36).value),int(sh.cell(r,38).value),aux_devengado,aux_pagado,int(sh.cell(r,42).value))
                            cr.execute(sql)
                    else:
                        if sh.cell(r,9).value:
                            sql = '''INSERT INTO account_move_line (
                            id,journal_id,credit,debit,account_id,period_id,date,move_id,name,ref,partner_id) VALUES (%s,%s,%s,%s,%s,%s,'%s',%s,'%s','%s',%s)'''%(int(sh.cell(r,0).value),int(sh.cell(r,6).value),aux_credit,aux_debit,int(sh.cell(r,20).value),int(sh.cell(r,21).value),sh.cell(r,23).value,int(sh.cell(r,24).value),ustr(sh.cell(r,25).value),aux_ref,int(sh.cell(r,9).value))
                            cr.execute(sql)
                        else:
                            sql = '''INSERT INTO account_move_line (
                            id,journal_id,credit,debit,account_id,period_id,date,move_id,name,ref) VALUES (%s,%s,%s,%s,%s,%s,'%s',%s,'%s','%s')'''%(int(sh.cell(r,0).value),int(sh.cell(r,6).value),aux_credit,aux_debit,int(sh.cell(r,20).value),int(sh.cell(r,21).value),sh.cell(r,23).value,int(sh.cell(r,24).value),ustr(sh.cell(r,25).value),aux_ref)
                            cr.execute(sql)
                    j+=1
                print "RECUPERADOS", j
        return True

    def updatePlaca(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        prop_obj = self.pool.get('account.asset.property')
        tipo_obj = self.pool.get('gt.tipo.properties')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                j=0
                for r in range(sh.nrows)[1:]:
                    aux_t = ustr(sh.cell(r,0).value).zfill(3)
                    aux_st = ustr(sh.cell(r,1).value).zfill(2)
                    aux_cl = ustr(sh.cell(r,2).value).zfill(3)
                    aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,3).value).zfill(4)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                    if asset_ids:
                        aux_placa = ustr(sh.cell(r,26).value)
                        t_placa = tipo_obj.search(cr, uid, [('name','=','PLACA')])
                        prop_obj.create(cr, uid, {
                            'name':t_placa[0],
                            'value':aux_placa,
                            'asset_id':asset_ids[0],
                        })
                        aux_motor = ustr(sh.cell(r,27).value)
                        t_motor = tipo_obj.search(cr, uid, [('name','=','MOTOR')])
                        prop_obj.create(cr, uid, {
                            'name':t_motor[0],
                            'value':aux_motor,
                            'asset_id':asset_ids[0],
                        })
                        aux_chasis = ustr(sh.cell(r,28).value)
                        t_chasis = tipo_obj.search(cr, uid, [('name','=','CHASIS')])
                        prop_obj.create(cr, uid, {
                            'name':t_chasis[0],
                            'value':aux_chasis,
                            'asset_id':asset_ids[0],
                        })
                        aux_clase = ustr(sh.cell(r,29).value)
                        t_clase = tipo_obj.search(cr, uid, [('name','=','CLASE')])
                        prop_obj.create(cr, uid, {
                            'name':t_clase[0],
                            'value':aux_clase,
                            'asset_id':asset_ids[0],
                        })
                        aux_tipo = ustr(sh.cell(r,30).value)
                        t_tipo = tipo_obj.search(cr, uid, [('name','=','TIPO VEHICULO')])
                        prop_obj.create(cr, uid, {
                            'name':t_tipo[0],
                            'value':aux_tipo,
                            'asset_id':asset_ids[0],
                        })
                        aux_anio = ustr(sh.cell(r,31).value)
                        t_anio = tipo_obj.search(cr, uid, [('name','=','ANIO')])
                        prop_obj.create(cr, uid, {
                            'name':t_anio[0],
                            'value':aux_anio,
                            'asset_id':asset_ids[0],
                        })
                        j+=1
        print "update", j
        return True

    def updateActividadActivo(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        activ_obj = self.pool.get('asset.actividad')
        estr_obj = self.pool.get('asset.estructura')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_t = ustr(sh.cell(r,0).value).zfill(3)
                    aux_st = ustr(sh.cell(r,1).value).zfill(2)
                    aux_cl = ustr(sh.cell(r,2).value).zfill(3)
                    aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,3).value).zfill(4)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                    aux_activ = ustr(sh.cell(r,4).value)
                    activ_ids = activ_obj.search(cr, uid, [('name','=',aux_activ)])
                    if activ_ids:
                        activ_id = activ_ids[0]
                    else:
                        activ_id = activ_obj.create(cr,uid, {
                            'name':aux_activ,
                        })
                    aux_estruc = ustr(sh.cell(r,5).value)
                    estruc_ids = estr_obj.search(cr, uid, [('name','=',aux_estruc)])
                    if estruc_ids:
                        estruc_id = estruc_ids[0]
                    else:
                        estruc_id = estr_obj.create(cr, uid, {
                            'name':aux_estruc,
                        })
                    if asset_ids:
                        asset_obj.write(cr, uid, asset_ids[0],{
                            'actividad_id':activ_id,
                            'estructura_id':estruc_id,
                        })
        return True

    def updateProveedorActivo(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        partner_obj = self.pool.get('res.partner')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_t = ustr(sh.cell(r,0).value).zfill(3)
                    aux_st = ustr(sh.cell(r,1).value).zfill(2)
                    aux_cl = ustr(sh.cell(r,2).value).zfill(3)
                    aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,3).value).zfill(4)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                    if asset_ids:
                        aux_cedula = str(sh.cell(r,7).value)
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedula)])
                        if partner_ids:
                            partner_id = partner_ids[0]
                        else:
                            print "NO proveedor",aux_cedula
                            partner_id = partner_obj.create(cr, uid, {
                                'ced_ruc':aux_cedula,
                                'name':ustr(sh.cell(r,8).value),
                                'type_ced_ruc':'otro',
                                'tipo_persona':'6',
                                'direccion':'SD',
                                'telefono':'STF',
                                'email':'info@gmail.com',
                                'property_account_position':2,
                            })
                        asset_obj.write(cr, uid, asset_ids[0],{
                            'invoice_id':str(sh.cell(r,4).value),
                            'partner_id':partner_id,
                        })
        return True

    def updateFechasActivo(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_t = ustr(sh.cell(r,2).value).zfill(3)
                    aux_st = ustr(sh.cell(r,3).value).zfill(2)
                    aux_cl = ustr(sh.cell(r,4).value).zfill(3)
                    aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,5).value).zfill(4)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                    if asset_ids:
                        asset_obj.write(cr, uid, asset_ids[0],{
                            'purchase_date':str(sh.cell(r,20).value),
                            'date_ingreso':str(sh.cell(r,10).value),
                            'date_entrega':str(sh.cell(r,10).value),
                        })
        return True

    def updateUbicacionActivo(self, cr, uid, ids, context=None):
        parroquia_obj = self.pool.get('res.country.state.parish')
        asset_obj = self.pool.get('account.asset.asset')
        area_obj = self.pool.get('asset.area')
        direccion_obj = self.pool.get('asset.direccion')
        seccion_obj = self.pool.get('asset.seccion')
        subseccion_obj = self.pool.get('asset.subseccion')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_t = ustr(sh.cell(r,0).value).zfill(3)
                    aux_st = ustr(sh.cell(r,1).value).zfill(2)
                    aux_cl = ustr(sh.cell(r,2).value).zfill(3)
                    aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,3).value).zfill(4)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                    if asset_ids:
                        aux_parroquia = ustr(sh.cell(r,6).value)
                        parroquia_ids = parroquia_obj.search(cr, uid, [('name','=',aux_parroquia)])
                        if parroquia_ids:
                            parroquia_id = parroquia_ids[0]
                        else:
                            parroquia_id = parroquia_obj.create(cr, uid, {
                                'name':aux_parroquia,
                            })
                        aux_direccion = ustr(sh.cell(r,8).value)
                        direccion_ids = direccion_obj.search(cr, uid, [('name','=',aux_direccion)])
                        if direccion_ids:
                            direccion_id = direccion_ids[0]
                        else:
                            direccion_id = direccion_obj.create(cr, uid, {
                                'name':aux_direccion,
                            })
                        aux_area = ustr(sh.cell(r,9).value)
                        area_ids = area_obj.search(cr, uid, [('name','=',aux_area)])
                        if area_ids:
                            area_id = area_ids[0]
                        else:
                            area_id = area_obj.create(cr, uid, {
                                'name':aux_area,
                            })
                        aux_seccion = ustr(sh.cell(r,10).value)
                        seccion_ids = seccion_obj.search(cr, uid, [('name','=',aux_seccion)])
                        if seccion_ids:
                            seccion_id = seccion_ids[0]
                        else:
                            seccion_id = seccion_obj.create(cr, uid, {
                                'name':aux_seccion,
                            })
                        aux_subseccion = ustr(sh.cell(r,11).value)
                        subseccion_ids = subseccion_obj.search(cr, uid, [('name','=',aux_subseccion)])
                        if subseccion_ids:
                            subseccion_id = subseccion_ids[0]
                        else:
                            subseccion_id = subseccion_obj.create(cr, uid, {
                                'name':aux_subseccion,
                            })
                        asset_obj.write(cr, uid, asset_ids[0],{
                            'direccion_id':direccion_id,
                            'area_id':area_id,
                            'seccion_id':seccion_id,
                            'subseccion_id':subseccion_id,
                            'parroquia':parroquia_id,
                        })
        return True

    def loadDepreciacion(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        log_obj = self.pool.get('log.deprecia')
        asset_ids = asset_obj.search(cr, uid, [])
        if asset_ids:
            for asset_id in asset_ids:
                asset = asset_obj.browse(cr, uid, asset_id)
                log_obj.create(cr, uid, {
                    'asset_id':asset_id,
                    'date':'2015-01-01',
                    'desc':'Migrado',
                    'valor':asset.depreciacion,
                })
        return True

    def loadCorrijeDep(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['tipo_sistema'] == 'sigame':
                updated=0
                for r in range(sh.nrows)[1:]:
                    aux_categ = ustr(sh.cell(r,2).value)
                    aux_code = aux_categ + '.' + ustr(sh.cell(r,3).value)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code),('purchase_date','<=','2016-03-30')])
                    if asset_ids:
                        if len(asset_ids)==1:
                            aux_depreciacion = aux_actual = 0
                            aux_depreciacion = float(sh.cell(r,15).value) + float(sh.cell(r,17).value)
                            aux_actual = float(sh.cell(r,12).value) - aux_depreciacion
                            asset_obj.write(cr, uid, asset_ids[0],{
                                'depreciacion':aux_depreciacion,
                                'valor_actual':aux_actual,
                                'dep_periodo':sh.cell(r,17).value,
                            })
                            updated+=1
                        else:
                            print "DUPLICADO", aux_code
                    else:
                        print "NO ACTIVO", aux_code
        print "ACTUALIZADOS", updated
        return True

    def activosNoDep(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        depline_obj = self.pool.get('account.asset.depreciation.line')
        no_dep = []
        for this in self.browse(cr, uid, ids):
            asset_ids = asset_obj.search(cr, uid, [('type','=','Larga Duracion'),('purchase_date','>=','2016-01-01')])
            if asset_ids:
                for asset_id in asset_ids:
                    dep_line_ids = depline_obj.search(cr, uid, [('asset_id','=',asset_id)])
                    if not dep_line_ids:
                        asset_obj.compute_depreciation_board(cr, uid, [asset_id])
                        no_dep.append(asset_id)
        print "NO LINEAS DEP", no_dep

    def ajustaDepMil(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        for this in self.browse(cr, uid, ids):
            calculados = 0
            if this.date:
                aux_date = this.date 
                asset_ids = asset_obj.search(cr, uid, [('type','=','Larga Duracion'),
                                                       ('purchase_date','<=',aux_date)])
                if asset_ids:
                    print "TOTAL ACTIVOS A CALCULAR", len(asset_ids)
                    for asset_id in asset_ids:
                        calculados += 1
                        asset = asset_obj.browse(cr, uid, asset_id)
                        dep_aux = 0
                        for line_dep in asset.depreciation_line_ids:
                            if line_dep.depreciation_date<='2016-01-01':
                                dep_aux += line_dep.amount
                        asset_obj.write(cr, uid, [asset_id],{'depreciacion':dep_aux})
            print "RECALCULADOS", calculados
        return True        

    def recomputeDepMil(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        for this in self.browse(cr, uid, ids):
            calculados = 0
#                asset_ids = asset_obj.search(cr, uid, [('type','=','Larga Duracion'),
#                                                       ('purchase_date','<=',aux_date)])
            asset_ids = [12093]
            if asset_ids:
                print "TOTAL ACTIVOS A CALCULAR", len(asset_ids)
                for asset_id in asset_ids:
                    calculados += 1
                    asset_obj.compute_depreciation_board(cr, uid, [asset_id])
                    #                        asset_obj.write(cr, uid, [asset_id],{'updated':True})
            print "RECALCULADOS", calculados
        return True

    def asignaDepreciacionEmp(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        line_obj = self.pool.get('account.asset.depreciation.line')
        log_obj = self.pool.get('log.deprecia')
        categ_obj = self.pool.get('account.asset.category')
        for this in self.browse(cr, uid, ids):
            calculados = 0
            categ_ids = categ_obj.search(cr, uid, [('type_asset','=','larga_duracion')])
            if categ_ids:
                for categ_id in categ_ids:
                    total_categ = 0
                    categ = categ_obj.browse(cr, uid, categ_id)
                    asset_ids = asset_obj.search(cr, uid, [('purchase_value','>',0),('type','=','Larga Duracion'),('category_id','=',categ_id)])
#                    asset_ids = [12093]
                    if asset_ids:
#                        print "TOTAL ACTIVOS A CALCULAR", len(asset_ids)
                        for asset_id in asset_ids:
                            asset = asset_obj.browse(cr, uid, asset_id)
                            depreciado = 0
                            line_ids = line_obj.search(cr, uid, [('asset_id','=',asset_id),('depreciation_date','<=','2017-01-01')])
                            if line_ids:
                                for line_id in line_ids:
                                    line = line_obj.browse(cr, uid, line_id)
                                    depreciado += line.amount
                                    total_categ += line.amount
                                    log_obj.create(cr, uid, {
                                        'asset_id':asset_id,
                                        'date':line.depreciation_date,
                                        'valor':line.amount,
                                        'desc':'Dep.Reasignada',
                                    })
                            if asset.purchase_value<=depreciado:
                                print "a"
                                #import pdb
                                #pdb.set_trace()
                            asset_obj.write(cr, uid,asset_id,{'depreciacion':depreciado})
                    print "TOTAL CATEGORIA",categ.name,categ.code,total_categ
            print "RECALCULADOS", calculados
        return True

    def updateActivoRiobamba(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                aux_id = int(sh.cell(r,0).value)
                aux_emp = int(sh.cell(r,1).value)
                asset_obj.write(cr, uid, aux_id,{'employee_id':aux_emp})
        return True

    def loadConcejo(self, cr, uid, ids, context=None):
        item_obj= self.pool.get('budget.item')
        post_obj = self.pool.get('budget.post')
        line_obj = self.pool.get('budget.concejo.line')
        program_obj = self.pool.get('project.program')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                aux_code = sh.cell(r,0).value[0:10]
                aux_inicial = sh.cell(r,3).value
                item_ids = item_obj.search(cr, uid, [('code','=',aux_code),('poa_id','=',6)])
                if item_ids:
                    item = item_obj.browse(cr, uid, item_ids[0])
                    line_obj.create(cr, uid, {
                        'name':item.budget_post_id.id,
                        'program_id':item.program_id.id,
                        'budget_id':item.id,
                        'inicial':aux_inicial,
                    })
                else:
                    aux_code_programa = aux_code[0:3]
                    program_ids = program_obj.search(cr, uid, [('sequence','=',aux_code_programa)])
                    aux_code_post = aux_code[4:]
                    post_ids = post_obj.search(cr, uid, [('code','=',aux_code_post)])
                    if post_ids and program_ids:
                        line_obj.create(cr, uid, {
                            'name':post_ids[0],
                            'program_id':program_ids[0],
                            'inicial':aux_inicial,
                        })
                    else:
                        print "NO POSR oR PROGRAMA", aux_code_post, aux_code_programa
        return True
                

    def updateRevalRio(self, cr, uid, ids, context=None):
        reval_obj = self.pool.get('account.asset.reval')
        for this in self.browse(cr, uid, ids):
            reval_ids = reval_obj.search(cr, uid, [])
            if reval_ids:
                for reval_id in reval_ids:
                    reval = reval_obj.browse(cr, uid, reval_id)
                    reval_obj.write(cr, uid, reval_id,{
                        'actual_ant':reval.asset_id.valor_actual,
                    })
        return True

    def revalorizaRiobamba(self, cr, uid, ids, context=None):
        reval_obj = self.pool.get('account.asset.reval')
        for this in self.browse(cr, uid, ids):
            reval_ids = reval_obj.search(cr, uid, [])
            if reval_ids:
                for reval_id in reval_ids:
                    reval_obj.rev_calcula(cr, uid, [reval_id])
                    reval_obj.rev_autoriza(cr, uid, [reval_id])
                    reval_obj.rev_ejecuta(cr, uid, [reval_id])
        return True

    def ejecutaDepreciaRevalorizaRiobamba(self, cr, uid, ids, context=None):
        reval_obj = self.pool.get('account.asset.reval')
        asset_obj = self.pool.get('account.asset.asset')
        for this in self.browse(cr, uid, ids):
            reval_ids = reval_obj.search(cr, uid, [])
            if reval_ids:
                for reval_id in reval_ids:
                    reval = reval_obj.browse(cr, uid, reval_id)
                    asset_obj.recompute_dep(cr, uid, [reval.asset_id.id])
        return True

    def ejecutaRevalorizaRiobamba(self, cr, uid, ids, context=None):
        reval_obj = self.pool.get('account.asset.reval')
        for this in self.browse(cr, uid, ids):
            reval_ids = reval_obj.search(cr, uid, [])
            if reval_ids:
                for reval_id in reval_ids:
                    reval_obj.rev_ejecuta(cr, uid, [reval_id])
        return True

    def computeActivoEmp(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        for this in self.browse(cr, uid, ids):
            calculados = 0
            asset_ids = asset_obj.search(cr, uid, [('type','=','Larga Duracion')])
#            asset_ids = [12093]
            if asset_ids:
                print "TOTAL ACTIVOS A CALCULAR", len(asset_ids)
                for asset_id in asset_ids:
                    calculados += 1
                    asset_obj.compute_depreciation_board(cr, uid, [asset_id])
            print "RECALCULADOS", calculados
        return True

    def recomputeDepRioAllMigrado(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        for this in self.browse(cr, uid, ids):
            if this.date and this.category_id:
                aux_date = this.date 
                #asset_ids = asset_obj.search(cr, uid, [('state','=','open'),('type','=','Larga Duracion'),('purchase_date','>=',aux_date)])
#                asset_ids = asset_obj.search(cr, uid, [('category_id','=',this.category_id.id),('type','=','Larga Duracion'),
#                                                       ('updated','=',False),('purchase_date','<',aux_date)])
#                asset_ids = asset_obj.search(cr, uid, [('category_id','=',this.category_id.id),('type','=','Larga Duracion'),('purchase_date','<',aux_date)])
                asset_ids = asset_obj.search(cr, uid, [('category_id','=',this.category_id.id),('type','=','Larga Duracion'),
                                                       ('purchase_date','<=',aux_date)])
                calculados = 0
                if asset_ids:
                    print "TOTAL ACTIVOS A CALCULAR", len(asset_ids)
                    for asset_id in asset_ids:
                        calculados += 1
                        asset_obj.compute_depreciation_board_migrado(cr, uid, [asset_id])
                        asset_obj.write(cr, uid, [asset_id],{'updated':True})
            print "RECALCULADOS", calculados
        return True

    def depRioLineaMigrada(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        dep_line_obj = self.pool.get('account.asset.depreciation.line')
        for this in self.browse(cr, uid, ids):
            asset_ids = asset_obj.search(cr, uid, [('type','=','Larga Duracion'),('purchase_date','<=',this.date)])
            calculados = 0
            if asset_ids:
                print "TOTAL ACTIVOS A CALCULAR", len(asset_ids)
                for asset_id in asset_ids:
                    calculados += 1
                    asset = asset_obj.browse(cr, uid, asset_id)
                    dep_line_obj.create(cr, uid, {
                        'asset_id':asset_id,
                        'sequence':0,
                        'depreciation_date':'2015-12-31',
                        'amount':asset.depreciacion,
                        'remaining_value':0,
                        'depreciated_value':0,
                        'name':'Migrado',
                    })
        print "RECALCULADOS", calculados
        return True

    def recomputeDepRioAll(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        for this in self.browse(cr, uid, ids):
            if this.date and this.category_id:
                aux_date = this.date 
                #asset_ids = asset_obj.search(cr, uid, [('state','=','open'),('type','=','Larga Duracion'),('purchase_date','>=',aux_date)])
                asset_ids = asset_obj.search(cr, uid, [('category_id','=',this.category_id.id),('type','=','Larga Duracion'),
                                                       ('updated','=',False),('purchase_date','<',aux_date)])
                calculados = 0
                if asset_ids:
                    print "TOTAL ACTIVOS A CALCULAR", len(asset_ids)
                    for asset_id in asset_ids:
                        calculados += 1
                        asset_obj.compute_depreciation_board(cr, uid, [asset_id])
                        asset_obj.write(cr, uid, [asset_id],{'updated':True})
                        print "HACE", calculados
            print "RECALCULADOS", calculados
        return True

    def recomputeDepRio(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        for this in self.browse(cr, uid, ids):
            if this.date:
                aux_date = this.date 
                #asset_ids = asset_obj.search(cr, uid, [('state','=','open'),('type','=','Larga Duracion'),('purchase_date','>=',aux_date)])
                asset_ids = asset_obj.search(cr, uid, [('category_id','=',5),('type','=','Larga Duracion'),('purchase_date','>=',aux_date)])
                if asset_ids:
                    calculados = 0
                    for asset_id in asset_ids:
                        calculados += 1
                        asset_obj.compute_depreciation_board(cr, uid, [asset_id])
            print "RECALCULADOS", calculados
        return True

    def recomputeDep(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        asset_ids = asset_obj.search(cr, uid, [('state','=','open')])
        if asset_ids:
            for asset_id in asset_ids:
                asset_obj.compute_depreciation_board(self, cr, uid, asset_id)
        return True

    def updateCustodioUltimo(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        employee_obj = self.pool.get('hr.employee')
        dept_obj = self.pool.get('hr.department')
        job_obj = self.pool.get('hr.job')
        tranfer_obj = self.pool.get('account.asset.transfer')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_cedula = ustr(sh.cell(r,9).value)
                    aux_t = ustr(sh.cell(r,2).value).zfill(3)
                    aux_st = ustr(sh.cell(r,3).value).zfill(2)
                    aux_cl = ustr(sh.cell(r,4).value).zfill(3)
                    aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,5).value).zfill(4)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                    if asset_ids:
                        asset = asset_obj.browse(cr, uid, asset_ids[0])
                        transferencias_ids = tranfer_obj.search(cr, uid, [('asset_id','=',asset.id),('state','=','confirmed')])
                        if not transferencias_ids:
                            employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)])
                            if employee_ids:
                                asset_obj.write(cr, uid, asset_ids[0],{'employee_id':employee_ids[0]})
                            else:
                                dept_ids = dept_obj.search(cr, uid, [])
                                job_ids = job_obj.search(cr, uid, [])
                                employee_id = employee_obj.create(cr, uid, {
                                    'name':aux_cedula,
                                    'id_type':'p',
                                    'employee_first_lastname':ustr(sh.cell(r,10).value),
                                    'employee_first_name':' ',
                                    'department_id':dept_ids[0],
                                    'job_id':job_ids[0],
                                    'address':'LIMON',
                                    'house_phone':'SN',
                                    })
                                asset_obj.write(cr, uid, asset_ids[0],{'employee_id':employee_id})
        return True                

    def updateCustodioAntes(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        employee_obj = self.pool.get('hr.employee')
        dept_obj = self.pool.get('hr.department')
        job_obj = self.pool.get('hr.job')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_cedula = ustr(sh.cell(r,8).value)
                    aux_ced = "'"+aux_cedula+"'"
                    sql = "select id from hr_employee where name=%s and employee_first_lastname is null"%(aux_ced)
                    cr.execute(sql)
                    result = cr.fetchall()
                    if result:
                        for cedula in result:
                            employee_obj.write(cr, uid, cedula[0],{
                                'employee_first_lastname':ustr(sh.cell(r,9).value),
                            })
        return True        

    def updateCustodioActualizado(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        employee_obj = self.pool.get('hr.employee')
        dept_obj = self.pool.get('hr.department')
        job_obj = self.pool.get('hr.job')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_cedula = ustr(sh.cell(r,9).value)
                    aux_ced = "'"+aux_cedula+"'"
                    sql = "select id from hr_employee where name=%s and employee_first_lastname is null"%(aux_ced)
                    cr.execute(sql)
                    result = cr.fetchall()
                    if result:
                        for cedula in result:
                            employee_obj.write(cr, uid, cedula[0],{
                                'employee_first_lastname':ustr(sh.cell(r,10).value),
                            })
        return True        
    

    def updateCustodioOlympoNoEmpCustodio(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        employee_obj = self.pool.get('hr.employee')
        dept_obj = self.pool.get('hr.department')
        job_obj = self.pool.get('hr.job')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_cedula = ustr(sh.cell(r,11).value)
                    aux_t = ustr(sh.cell(r,2).value).zfill(3)
                    aux_st = ustr(sh.cell(r,3).value).zfill(2)
                    aux_cl = ustr(sh.cell(r,4).value).zfill(3)
                    aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,5).value).zfill(4)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                    if asset_ids:
                        print "ERGA ASHEHHEHEHE"
                        asset = asset_obj.browse(cr, uid, asset_ids[0])
                        if asset.employee_id.name=='123456789':
                            employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)])
                            if employee_ids:
                                asset_obj.write(cr, uid, asset_ids[0],{'employee_id':employee_ids[0]})
                            else:
                                dept_ids = dept_obj.search(cr, uid, [])
                                job_ids = job_obj.search(cr, uid, [])
                                employee_id = employee_obj.create(cr, uid, {
                                    'name':aux_cedula,
                                    'id_type':'p',
                                    'employee_first_lastname':ustr(sh.cell(r,10).value),
                                    'employee_first_name':' ',
                                    'department_id':dept_ids[0],
                                    'job_id':job_ids[0],
                                    'address':'LIMON',
                                    'house_phone':'SN',
                                })
                                asset_obj.write(cr, uid, asset_ids[0],{'employee_id':employee_id})
        return True        

    def updateCustodioOlympoNoEmp(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        employee_obj = self.pool.get('hr.employee')
        dept_obj = self.pool.get('hr.department')
        job_obj = self.pool.get('hr.job')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_cedula = ustr(sh.cell(r,8).value)
                    aux_t = ustr(sh.cell(r,2).value).zfill(3)
                    aux_st = ustr(sh.cell(r,3).value).zfill(2)
                    aux_cl = ustr(sh.cell(r,4).value).zfill(3)
                    aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,5).value).zfill(4)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                    if asset_ids:
                        print "COdE ACTVIO", aux_code_activo
                        asset = asset_obj.browse(cr, uid, asset_ids[0])
                        if asset.employee_id.name=='123456789':
                            employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)])
                            if employee_ids:
                                asset_obj.write(cr, uid, asset_ids[0],{'employee_id':employee_ids[0]})
                            else:
                                dept_ids = dept_obj.search(cr, uid, [])
                                job_ids = job_obj.search(cr, uid, [])
                                employee_id = employee_obj.create(cr, uid, {
                                    'name':aux_cedula,
                                    'id_type':'p',
                                    'employee_first_lastaname':ustr(sh.cell(r,9).value),
                                    'employee_first_name':' ',
                                    'department_id':dept_ids[0],
                                    'job_id':job_ids[0],
                                    'address':'LIMON',
                                })
                                asset_obj.write(cr, uid, asset_ids[0],{'employee_id':employee_id})
        return True        

    def updateCustodioOlympo(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        employee_obj = self.pool.get('hr.employee')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            if data['tipo_sistema']=='olympo':
                for r in range(sh.nrows)[1:]:
                    aux_usa = ustr(sh.cell(r,12).value)
                    if aux_usa=='1':
                        aux_cedula = ustr(sh.cell(r,11).value)
                        aux_t = ustr(sh.cell(r,3).value).zfill(3)
                        aux_st = ustr(sh.cell(r,4).value).zfill(3)
                        aux_cl = ustr(sh.cell(r,5).value).zfill(3)
                        aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,6).value).zfill(4)
                        asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                        if asset_ids:
                            asset = asset_obj.browse(cr, uid, asset_ids[0])
                            new_code = asset.code[0:4] + asset.code[5:]
                            employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)])
                            if employee_ids:
                                asset_obj.write(cr, uid, asset_ids[0],{'employee_id':employee_ids[0],
                                                                       'code':new_code,})
                            else:
                                asset_obj.write(cr, uid, asset_ids[0],{
                                    'code':new_code,})
                                print "No empleado", aux_cedula, new_code
        return True
                        

    def updateProductOlympo(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        template_obj = self.pool.get('product.template')
        categ_obj = self.pool.get('product.category')
        subcateg_obj = self.pool.get('product.subcategory')
        uom_obj = self.pool.get('product.uom')
        uom_categ = self.pool.get('product.uom.categ')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            j = 0
            for r in range(sh.nrows)[1:]:
                codigo = str(sh.cell(r,0).value)
                standard_price = float(sh.cell(r,10).value)
                product_ids = product_obj.search(cr, uid, [('default_code','=',codigo)])
                if product_ids:
                    product_obj.write(cr, uid, product_ids[0],
                                      {'standard_price':standard_price})
                else:
                    j+=1
                    categ_ids = categ_obj.search(cr,uid, [('name','=',str(sh.cell(r,3).value))])
                    if categ_ids:
                        categ_id = categ_ids[0]
                    else:
                        categ_id = categ_obj.create(cr, uid, {
                            'name':str(sh.cell(r,3).value),
                            'budget':'corriente',
                        })
                    subcateg_ids = subcateg_obj.search(cr, uid, [('name','=',str(sh.cell(r,4).value))])
                    print "1"
                    if subcateg_ids:
                        subcateg_id = subcateg_ids[0]
                    else:
                        subcateg_id = subcateg_obj.create(cr, uid, {
                            'name':str(sh.cell(r,4).value),
                            'categ_id':categ_id,
                        })
                    uom_ids = uom_obj.search(cr, uid, [('name','=',str(sh.cell(r,5).value))])
                    if uom_ids:
                        uom_id = uom_ids[0]
                    else:
                        uomc_ids = uom_categ_obj.search(cr, uid, [('name','=',str(sh.cell(r,5).value))])
                        if uomc_ids:
                            uomc_id = uomc_ids[0]
                        else:
                            uomc_id = uom_categ_obj.create(cr, uid, {
                                'name':str(sh.cell(r,5).value),
                            })
                        uom_id = uom_obj.create(cr, uid, {
                            'name':str(sh.cell(r,5).value),
                            'uom_type':'reference',
                            'rounding':0.010,
                            'category_id':uomc_id,
                        })
                    p_id = product_obj.create(cr, uid,{
                        'default_code':codigo,
                        'name':ustr(sh.cell(r,1).value),
                        'type':str(sh.cell(r,2).value),
                        'categ_id':categ_id,
                        'subcateg_id':subcateg_id,
                        'uom_id':uom_id,
                        'uos_id':uom_id,
                        'uom_po_id':uom_id,
                        'procure_method':str(sh.cell(r,8).value),
                        'cost_method':str(sh.cell(r,9).value),
                        'standard_price':standard_price,
                        'valuation':'real_time',
                    })
                    print "creadooo",p_id,codigo
        return True


    def updateCuentaContable1(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            j = 0 
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,0).value)=='NULL':
                    continue
                aux_codigo = ustr(sh.cell(r,0).value)
                aux_name = ';'+ustr(sh.cell(r,2).value)
                account_ids = account_obj.search(cr, uid, [('code_aux','=',aux_codigo)])
                if not account_ids:
                    j += 1
                    print aux_codigo,aux_name
                    if j==100:
                        print "===================================================="
                        j = 0
        return True

    def updateCuentaPadre(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            j = 0
            for r in range(sh.nrows)[1:]:
                j+=1
                print "AHCEEEEE", j
                aux_codigo = ustr(sh.cell(r,2).value)
                aux_code = aux_codigo.replace('.','')
                account_ids = account_obj.search(cr, uid, [('code','=',aux_code)])
                if account_ids:
                    aux_codigop = ustr(sh.cell(r,3).value)
                    aux_codep = aux_codigop.replace('.','')
                    aux_codep1 = aux_codep + ' '
                    account_idsp = account_obj.search(cr, uid, [('code','=',aux_codep)])
                    account_idsp1 = account_obj.search(cr, uid, [('code','=',aux_codep1)])                    
                    account_idsp2 = account_idsp + account_idsp1
                    if account_idsp2:
                        parent_id = account_idsp2[0]
#                        cr.execute('''UPDATE account_account set parent_id=%s where id=%s''',(parent_id,account_ids[0]))
                        account_obj.write(cr, uid, account_ids[0],{
                            'parent_id':parent_id,
                        })
#                        account_obj._parent_store_compute(cr)
                    else:
                        print "NOPARENT", aux_codigop
                else:
                    print "NOCUENTA", aux_codigo
        return True

    def updateCuentaPartidaRio(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            j = 0
            for r in range(sh.nrows)[1:]:  
                aux_cta = str(sh.cell(r,0).value).replace('.','')
                cta_ids = account_obj.search(cr, uid, [('code','=',aux_cta)],limit=1)
                if not cta_ids:
                    aux_cta1 = aux_cta + ' '
                    cta_ids = account_obj.search(cr, uid, [('code','=',aux_cta1)],limit=1)
                if cta_ids:
                    cuenta = account_obj.browse(cr, uid, cta_ids[0])
                    if not cuenta.budget_id:
                        aux_post = str(sh.cell(r,1).value).replace('.','')
                        if len(aux_post)>15:
                            aux_post1 = aux_post + '0'
                        post_ids = post_obj.search(cr, uid, [('code','=',aux_post)])
                        if not post_ids:
                            post_ids = post_obj.search(cr, uid, [('code','=',aux_post1)])
                        if post_ids:
                            account_obj.write(cr, uid, cta_ids[0],{
                                'budget_id':post_ids[0],
                            })
                        else:
                            print "NOPOST", aux_post
                else:
                    print "NOCTA", aux_cta
        return True

    def updateCuentaContable(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            j = 0
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,0).value)=='NULL':
                    continue
                aux_name = ustr(sh.cell(r,1).value)
                aux_codigo = ustr(sh.cell(r,0).value)
                code_sin_esp = aux_codigo.replace('.','')
                if aux_codigo[:1]=='1':
                    us_aux = 6
                elif aux_codigo[:1]=='2':
                    us_aux = 19
                else:
                    us_aux = 21
                #parent
                account_ids = account_obj.search(cr, uid, [('code','=',code_sin_esp)])
                if account_ids:
                    aux_code_parent = ustr(sh.cell(r,2).value)
                    code_parent_sin = aux_code_parent.replace('.','')
                    parent_ids = account_obj.search(cr, uid, [('code','=',code_parent_sin)])
                    if parent_ids:
                        parent_id = parent_ids[0]
                    else:
                        print "NO PAPA", code_parent_sin
                    account_obj.write(cr, uid, account_ids[0],{
                                      'parent_id':parent_id,
                    })
                else:
                    print "SI CUENAT", code_sin_esp
        return True

    def updatePartidaCuenta(self, cr, uid, ids, context=None):
        #lee un archivo excel que tenga la cuenta y la partida, usado en riobamba
        account_obj = self.pool.get('account.account')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            j = 0
            for r in range(sh.nrows)[1:]:  
                aux_code = ustr(sh.cell(r,0).value).replace('.','')
                aux_code_budget = ustr(sh.cell(r,1).value).replace('.','')
                account_ids = account_obj.search(cr, uid, [('code','=',aux_code)])
                if account_ids:
                    account = account_obj.browse(cr,uid, account_ids[0])
                    if not account.budget_id:
                        post_ids = post_obj.search(cr, uid, [('code','=',aux_code_budget)],limit=1)
                        if post_ids:
                            account_obj.write(cr, uid, account.id,{
                                'budget_id':post_ids[0],
                            })
                            print "actuliza cuenta", aux_code,aux_code_budget
                        else:
                            print "cuenta pero no partida", aux_code,aux_code_budget
                else:
                    print "NO CUENTA", aux_code
        return True

    def updateCuentaContable8(self, cr, uid, ids, context=None):
        ##este coloca la papa del arvchivo migarar
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            j = 0
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,0).value)=='NULL':
                    continue
                aux_name = ustr(sh.cell(r,1).value)
                aux_codigo = ustr(sh.cell(r,0).value)
                code_sin_esp = aux_codigo.replace('.','')
                if aux_codigo[:1]=='1':
                    us_aux = 6
                elif aux_codigo[:1]=='2':
                    us_aux = 19
                else:
                    us_aux = 21
                #parent
                account_ids = account_obj.search(cr, uid, [('code','=',code_sin_esp)])
                if not account_ids:
                    aux_code_parent = ustr(sh.cell(r,2).value)
                    code_parent_sin = aux_code_parent.replace('.','')
                    parent_ids = account_obj.search(cr, uid, [('code','=',code_parent_sin)])
                    if parent_ids:
                        parent_id = parent_ids[0]
                    else:
                        print "NO PAPA", code_parent_sin
                    account_id = account_obj.create(cr, uid, {
                        'code':aux_codigo.replace('.',''),
                        'name':ustr(sh.cell(r,1).value),
                        'code_aux':aux_codigo,
                        'parent_id':parent_id,
                        'type':'other',
                        'user_type':us_aux,
                    })
                else:
                    print "SI CUENAT", code_sin_esp
        return True

    def updateCuentaContableX(self, cr, uid, ids, context=None):
        ##este metodo solo usar para sacar el listado de cuenta y luego colocar las padre y migrar ya con la padre
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            j = 0
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,0).value)=='NULL':
                    continue
                aux_name = ustr(sh.cell(r,1).value)
                aux_codigo = ustr(sh.cell(r,0).value)
                code_sin_esp = aux_codigo.replace(' ','')
                aux_code1 = aux_codigo.replace('.','')
                aux_code = aux_code1.replace(' ','')
                aux_code3 = aux_code+' '
                account_ids = account_obj.search(cr, uid, [('code','=',aux_code)])
                account_ids2 = account_obj.search(cr, uid, [('code','=',aux_code1)])
                account_ids3 = account_obj.search(cr, uid, [('code','=',aux_code3)])
                account_ids4 = account_ids + account_ids2 + account_ids3
                if not account_ids4:
                    ###parent
                    ##
                    j+=1
                    if j in (100,200,300,400,500,600):
                        import pdb
                        pdb.set_trace()
                    aux = code_sin_esp+'_'+aux_name
                    print aux,'_',"CREADO",j
        return True

    def updateCuentaContable3(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,0).value)=='NULL':
                    continue
                aux_codigo = ustr(sh.cell(r,0).value)
                account_ids = account_obj.search(cr, uid, [('code_aux','=',aux_codigo)])
                if not account_ids:
#                    print aux_codigo
                    lista = []
                    pos_inicial = -1
                    try:
                        while True:
                            pos_inicial = aux_codigo.index('.', pos_inicial+1)
                            lista.append(pos_inicial)
                    except ValueError: # cuando ya no se encuentre la letra
                        print aux_codigo
                    aux_len = len(lista)
                    code_aux_parent = aux_codigo[:lista[aux_len-1]]
                    parent_ids = account_obj.search(cr, uid, [('code_aux','=',code_aux_parent)])
                    if not parent_ids:
                        'NO PAPA', aux_codigo
                    if aux_codigo[:1]=='1':
                        us_aux = 6
                    elif aux_codigo[:1]=='2':
                        us_aux = 19
                    else:
                        us_aux = 21
                    account_id = account_obj.create(cr, uid, {
                        'code':aux_codigo.replace('.',''),
                        'name':ustr(sh.cell(r,1).value),
                        'code_aux':aux_codigo,
                        'parent_id':parent_ids[0],
                        'type':'other',
                        'user_type':us_aux,
                    })
        return True

    def rubroPartida(self, cr, uid, ids, context=None):
        post_obj = self.pool.get('budget.post')
        account_obj = self.pool.get('account.account')
        rubro_obj = self.pool.get('recaudacion.rubro')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,0).value)=='NULL':
                    continue
                aux_code_rubro = ustr(sh.cell(r,0).value)
                aux_post_code = ustr(sh.cell(r,6).value).replace('.','')
                rubro_ids = rubro_obj.search(cr, uid, [('id_ext','=',aux_code_rubro)])
                if rubro_ids:
                    budget_ids = post_obj.search(cr, uid, [('code','=',aux_post_code)])
                    if budget_ids:
                        account_ids = account_obj.search(cr, uid, [('budget_id','=',budget_ids[0])])
                        if account_ids:
                            rubro_obj.write(cr, uid, rubro_ids[0],{
                                'partida_id':budget_ids[0],
                                'account_id':account_ids[0],
                            })
                        else:
                            print "NO CONFIG CUENTA", aux_code_rubro
                            rubro_obj.write(cr, uid, rubro_ids[0],{
                                'partida_id':budget_ids[0],
                            })
                    else:
                        print "No partida", aux_code_rubro
                else:
                    print "NO RUBROOOO", aux_code_rubro
        return True

    def loadEsigef(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,0).value)=='NULL':
                    continue
                aux_code = ustr(sh.cell(r,0).value).replace('.','')
                account_ids = account_obj.search(cr, uid, [('code','=',aux_code)])
                if account_ids:
                    if len(account_ids)>1:
                        print "more one", aux_code
                    for account_id in account_ids:
                        account_obj.write(cr, uid, account_id,{
                            'esigef':True,
                        })
        return True
        

    def depurarPartner(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('account.move')
        partner_ids = partner_obj.search(cr, uid, [])
        if partner_ids:
            k =0 
            for partner_id in partner_ids:
                partner = partner_obj.browse(cr, uid, partner_id)
                if len(partner.ced_ruc)==10:
                    aux_ruc = partner.ced_ruc + '001'
                    partner_ids2 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ruc)])
                    if partner_ids2:
                        k += 1
                        move_ids = move_obj.search(cr, uid, [('partner_id','=',partner.id)])
                        print "PARTNER CON CEDuLA Y RUC", partner.name,partner.ced_ruc
                        if move_ids:
                            print "MOVE CON CEDULA"
                elif len(partner.ced_ruc)==13:
                    aux_cedula = partner.ced_ruc[0:10]
                    partner_ids2 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedula)])
                    if partner_ids2:
                        k += 1
                        move_ids = move_obj.search(cr, uid, [('partner_id','=',partner.id)])
                        print "PARTNER CON RUC Y CEDULA", partner.name,partner.ced_ruc
                        if move_ids:
                            print "MOVE CON RUC"
        print "TOTALllllllllllllll",k
        return True

    #OLYMPO MIGRACION

    def loadCertificadoOlympo(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        dept_obj = self.pool.get('hr.department')
        emp_obj = self.pool.get('hr.employee')
        partner_obj = self.pool.get('res.partner')
        project_obj = self.pool.get('project.project')
        program_obj = self.pool.get('project.program')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        item_obj = self.pool.get('budget.item')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            department_ids = dept_obj.search(cr, uid, [],limit=1)
            employee_ids = emp_obj.search(cr, uid, [],limit=1)
            project_ids = project_obj.search(cr, uid, [('type_budget','=','gasto')],limit=1)
            date_aux = data['date']
            partner_id = 1
            cert_id = certificate_obj.create(cr, uid, {
                'name':'CPEGR001',
                'number':'CPEGR001',
                'user_id':1,
                'department_id':department_ids[0],
                'solicitant_id':employee_ids[0],
                'project_id':project_ids[0],
                'date':date_aux,
                'date_confirmed':date_aux,
                'date_commited':date_aux,
                'notes':'COMPROMISO PRESUPUESTARIO MIGRADO CORTE AL' + date_aux,
                'partner_id':partner_id,
                'migrado':True,
                'state':'commited',
                })        
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,1).value)=='NULL':
                    continue
                aux_cert_id = ustr(sh.cell(r,7).value)
                if ustr(sh.cell(r,6).value)[22:25]!='000':
                    aux_post_id = ustr(sh.cell(r,6).value)[15:25]
                else:
                    aux_post_id = ustr(sh.cell(r,6).value)[15:21]
                print "aux POSSSSTTTTT", aux_post_id
                aux_project = str(sh.cell(r,4).value)
                post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                if not post_ids:
                    print "NO PARTIDA", aux_post_id
                programa_ids = program_obj.search(cr, uid, [('sequence','=',aux_project)])
                if not programa_ids:
                    print "NO POGAMA", aux_project
                project_ids = project_obj.search(cr, uid, [('program_id','=',programa_ids[0])],limit=1)
                if not project_ids:
                    print "NO PROHECTO", aux_project
                proyecto = project_obj.browse(cr, uid, project_ids[0])
                task_id = proyecto.tasks[0].id
                aux_amount = str(sh.cell(r,12).value)
                budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                if not budget_ids:
                    aux_post_id = str(sh.cell(r,6).value)[15:25]
                    print "segunda busqueda", aux_post_id, proyecto.program_id.sequence
                    post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                    if not post_ids:
                        "NO CATALOGO BUDGT", aux_post_id
                    budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                    if not budget_ids:
                        print "NO BUDGET ITEM", aux_post_id
                        print "NO PROYECTO",proyecto.program_id.sequence
                        continue
                line_in_ids = certificate_line_obj.search(cr, uid, [('certificate_id','=',cert_id),('budget_id','=',budget_ids[0])])
                monto_aux = 0
                if line_in_ids:
                    linea = certificate_line_obj.browse(cr, uid, line_in_ids[0])
                    monto_aux = linea.amount + float(aux_amount)
                    certificate_line_obj.write(cr, uid, line_in_ids,{
                        'amount':monto_aux,
                        'amount_certified':monto_aux,
                        'amount_commited':monto_aux,
                    })
                else:
                    certificate_line_obj.create(cr, uid, {
                        'certificate_id':cert_id,
                        'migrado':'True',
                        'project_id':project_ids[0],
                        'task_id':task_id,
                        'budget_id':budget_ids[0],
                        'amount':aux_amount,
                        'amount_certified':aux_amount,
                        'amount_commited':aux_amount,
                        'amount_paid':aux_amount,
                        'state':'commited',
                    })
        return True

    def loadCertificadoOlympoAux(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        dept_obj = self.pool.get('hr.department')
        emp_obj = self.pool.get('hr.employee')
        partner_obj = self.pool.get('res.partner')
        project_obj = self.pool.get('project.project')
        program_obj = self.pool.get('project.program')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,1).value)=='NULL':
                    continue
                aux_name = ustr(sh.cell(r,3).value)
                date_aux_1 = str(sh.cell(r,4).value)[0:10]
                partner_name_aux = ustr(sh.cell(r,15).value)
                desc_aux = ustr(sh.cell(r,16).value)
                partner_aux = ustr(sh.cell(r,14).value)
                department_ids = dept_obj.search(cr, uid, [],limit=1)
                employee_ids = emp_obj.search(cr, uid, [],limit=1)
                #sacar el proyecto del num_documento
                if len(ustr(sh.cell(r,10).value))>0 and ustr(sh.cell(r,10).value)!='0':
                    aux_project = ustr(sh.cell(r,10).value)[5:8]
                    programa_ids = program_obj.search(cr, uid, [('sequence','=',aux_project)])
                    if not programa_ids:
                        print "NO POGAMA", aux_project
                    project_ids = project_obj.search(cr, uid, [('program_id','=',programa_ids[0])],limit=1)
                else:
                    project_ids = project_obj.search(cr, uid, [('type_budget','=','gasto')],limit=1)
                ##partner
                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',partner_aux)])
                aux_persona = '6'
                if partner_ids:
                    partner_id = partner_ids[0]
                else:
                    partner_id = 1
#                    print "No partner", partner_aux
#                    aux_tipo = 'cedula'
#                    if len(partner_aux)>10:
#                        aux_tipo = 'ruc'
#                    partner_id = partner_obj.create(cr, uid, {
#                        'ced_ruc':partner_aux,
#                        'type_ced_ruc':aux_tipo,
#                        'tipo_persona':aux_persona,
#                        'name':partner_name_aux,
#                        'direccion':partner_name_aux,
#                        'telefono':'2222222',
#                        'property_account_receivable':1689,
#                        'property_account_payable':2823,
#                        'property_account_position':2,
#                    })
                cert_id = certificate_obj.create(cr, uid, {
                    'name':aux_name,
                    'number':aux_name,
                    'user_id':1,
                    'department_id':department_ids[0],
                    'solicitant_id':employee_ids[0],
                    'project_id':project_ids[0],
                    'date':date_aux_1,
                    'date_confirmed':date_aux_1,
                    'date_commited':date_aux_1,
                    'notes':desc_aux,
                    'partner_id':partner_id,
                    'migrado':True,
                    'state':'commited',
#                    'amount_total':,
#                    'amount_certified':,
#                    'amount_commited':,
                })

    def loadCertificadoLineOlympo(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        item_obj = self.pool.get('budget.item')
        project_obj = self.pool.get('project.project')
        program_obj = self.pool.get('project.program')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                aux_cert_id = ustr(sh.cell(r,7).value)
                if ustr(sh.cell(r,6).value)[22:25]!='000':
                    aux_post_id = ustr(sh.cell(r,6).value)[15:25]
                else:
                    aux_post_id = ustr(sh.cell(r,6).value)[15:21]
                print "aux POSSSSTTTTT", aux_post_id
                aux_project = str(sh.cell(r,4).value)
                post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                if not post_ids:
                    print "NO PARTIDA", aux_post_id
                programa_ids = program_obj.search(cr, uid, [('sequence','=',aux_project)])
                if not programa_ids:
                    print "NO POGAMA", aux_project
                project_ids = project_obj.search(cr, uid, [('program_id','=',programa_ids[0])],limit=1)
                if not project_ids:
                    print "NO PROHECTO", aux_project
                proyecto = project_obj.browse(cr, uid, project_ids[0])
                task_id = proyecto.tasks[0].id
                aux_amount = str(sh.cell(r,12).value)
                certificate_ids = certificate_obj.search(cr, uid, [('name','=',aux_cert_id)],limit=1)
                if not certificate_ids:
                    print "NO CERTIFICADO", aux_cert_id
                budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                if not budget_ids:
                    aux_post_id = str(sh.cell(r,6).value)[15:25]
                    print "segunda busqueda", aux_post_id, proyecto.program_id.sequence
                    post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                    if not post_ids:
                        "NO CATALOGO BUDGT", aux_post_id
                    budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                    if not budget_ids:
                        print "NO BUDGET ITEM", aux_post_id
                        print "NO PROYECTO",proyecto.program_id.sequence
                        continue
                certificate_line_obj.create(cr, uid, {
                    'certificate_id':certificate_ids[0],
                    'migrado':'True',
                    'project_id':project_ids[0],
                    'task_id':task_id,
                    'budget_id':budget_ids[0],
                    'amount':aux_amount,
                    'amount_certified':aux_amount,
                    'amount_commited':aux_amount,
                    'amount_paid':aux_amount,
                    'state':'commited',
                })
        return True

    ##SIGAME SCRIPT
    ##compromisos presupuestarios

    def updateFuncionario(self, cr, uid, ids, context={}):
        employee_obj = self.pool.get('hr.employee')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            j = 0
            for r in range(sh.nrows)[1:]:
                aux_cedula = ustr(sh.cell(r,0).value)
                aux_apellido = ustr(sh.cell(r,3).value)
                aux_nombre = ustr(sh.cell(r,2).value)
                employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula),('employee_first_lastname','=','Nombre')],limit=1)
                if employee_ids:
                    j+=1
                    employee_obj.write(cr, uid, employee_ids[0],{
                        'employee_first_lastname':aux_apellido,
                        'employee_first_name':aux_nombre,
                    })
        print "ACTUALIZADOS",j
        return True

    def employeeSigameR(self, cr, uid, ids, context={}):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        department_obj = self.pool.get('hr.department')
        ocupacional_obj = self.pool.get('grupo.ocupacional')
        job_obj = self.pool.get('hr.job')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                aux_cedula = ustr(sh.cell(r,0).value)
                aux_dept = ustr(sh.cell(r,6).value)
                aux_job = ustr(sh.cell(r,7).value)
                employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)],limit=1)
                department_ids = department_obj.search(cr, uid, [('name','=',aux_dept)])
                if department_ids:
                    department_id = department_ids[0]
                else:
                    department_id = department_obj.create(cr, uid, {
                        'name':aux_dept,
                        'sequence':'0000',
                    })
                job_ids = job_obj.search(cr, uid, [('name','=',aux_job)])
                if job_ids:
                    job_id = job_ids[0]
                else:
                    job_id = job_obj.create(cr,uid , {
                        'name':aux_job,
                        'department_id':department_id,
                    })
                if employee_ids:
                    employee_id = employee_ids[0]
                else:
                    employee_id = employee_obj.create(cr, uid, {
                        'name':aux_cedula,
                        'id_type':'c',
                        'employee_first_lastname':ustr(sh.cell(r,2).value),
                        'employee_first_name':ustr(sh.cell(r,3).value),
                        'department_id':department_id,
                        'job_id':job_id,
                        'birthday':str(sh.cell(r,9).value),
                        'gender':sh.cell(r,10).value,
                        'house_phone':sh.cell(r,17).value,
                        'mobile_phone':sh.cell(r,18).value,
                        'state_id':57,
                        'canton_id':43,
                        'address':'Riobamba',
                    })
                contract_ids = contract_obj.search(cr, uid, [('employee_id','=',employee_id)])
                if contract_ids:
                    contract_obj.write(cr, uid, contract_ids[0],{
                        'activo':False,
                    })
                aux_ocu = ustr(sh.cell(r,27).value)
                ocupacional_ids = ocupacional_obj.search(cr, uid, [('name','=',aux_ocu)])
                if ocupacional_ids:
                    ocupacional_id = ocupacional_ids[0]
                else:
                    ocupacional_id = ocupacional_obj.create(cr, uid, {
                        'escala':'grados_20',
                        'grado':'20',
                        'name':aux_ocu,
                    })
                contract_id = contract_obj.create(cr, uid, {
                    'name':'CTMIGRADO',
                    'employee_id':employee_id,
                    'type_id':7,
                    'subtype_id':6,
                    'ocupational_id':ocupacional_id,
                    'department_id':department_id,
                    'job_id':job_id,
                    'date_start':str(sh.cell(r,27).value),
                    'date_end':str(sh.cell(r,28).value),
                    'work_id':1,
                    'wage':sh.cell(r,29).value,
                    'struct_id':2,
                    'activo':True,
                })
        return True

    def budgetContrato(self, cr, uid, ids, context={}):
        program_obj = self.pool.get('project.program')
        item_obj = self.pool.get('budget.item')
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                aux_cedula = ustr(sh.cell(r,0).value)
                employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)],limit=1)
                if employee_ids:
                    contract_ids = contract_obj.search(cr, uid, [('employee_id','=',employee_ids[0])])
                    if contract_ids:
                        aux_i = ustr(sh.cell(r,4).value).find('.')
                        aux_ia = ustr(sh.cell(r,4).value)[:aux_i]
                        aux_j =  ustr(sh.cell(r,4).value)[aux_i+1:]
                        aux_ij = aux_j.find('.')
                        aux_ij1 = aux_j[:aux_ij]
                        aux_program1 = aux_ia + '.'+ aux_ij1
                        if len(aux_program1)<=3:
                            aux_program1 += '.1'
                        else:
#                            aux_program1 = aux_program1[0:1]+'.'+aux_program1[2:3]+'.'+aux_program1[3:4]
                            aux_program1 = aux_program1[2:3]+'.'+aux_program1[3:4] + '.1'
                        program_ids = program_obj.search(cr, uid, [('sequence','=',aux_program1)],limit=1)
                        if not program_ids:
                            print "NO POGAMA", aux_program1
                        aux_i = ustr(sh.cell(r,4).value).find('.')
                        aux_ia = ustr(sh.cell(r,4).value)[aux_i+1:]
                        aux_j =  aux_ia.find('.')
                        aux_ij = aux_ia[aux_j+1:]
                        aux_aux = aux_i + aux_j + 2
                        aux_budget = ustr(sh.cell(r,5).value)[aux_aux:].replace('.','')#+'.'+aux_program1.replace('.','')
                        if len(aux_budget)<=9:
                            aux_budget = aux_budget[0:6]
                        post_ids = post_obj.search(cr, uid, [('code','=',aux_budget)],limit=1)
                        if post_ids:
                            item_ids = item_obj.search(cr, uid, [('program_id','=',program_ids[0]),('budget_post_id','=',post_ids[0])],limit=1)
                            if item_ids:
                                contract_obj.write(cr, uid, contract_ids[0],{
                                    'program_id':program_ids[0],
                                    'budget_id':item_ids[0],})
                            else:
                                print 'NO ITEMMMSSS cedula programa budget', aux_cedula, aux_program1, aux_budget
                        else:
                            print "NO POST", aux_budget, aux_cedula
                    else:
                        print "NBO CONTrATo", aux_cedula
                else:
                    print "NO EMPLEADO", aux_cedula
        return True

    def loadPartnerSigame(self, cr, uid, ids, context={}):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        b_obj = self.pool.get('res.bank')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]: 
                if len(str(sh.cell(r,0).value))>1:
                    aux_ced_ruc = str(sh.cell(r,0).value)
                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                    if len(partner_ids)<1:
                        if len(aux_ced_ruc)<13:
                            aux_ced_ruc = aux_ced_ruc + '001' 
                        partner_ids2 = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                        if len(partner_ids2)<1:
                            partner_id = partner_obj.create(cr, uid, {
                                'ced_ruc':aux_ced_ruc,
                                'type_ced_ruc':'ruc',
                                'tipo_persona':'9',
                                'ref':ustr(sh.cell(r,1).value),
                                'name':ustr(sh.cell(r,9).value),
                                'telefono':str(sh.cell(r,3).value),
                                'direccion':ustr(sh.cell(r,2).value),
                                'mail':ustr(sh.cell(r,10).value),
                                'property_account_receivable':20196,
                                'property_account_payable':25293,
                                'property_account_position':7,
                            })
        return True

    def productosInicialSigame(self, cr, uid, ids, context={}):
        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')
        inventory_obj = self.pool.get('stock.inventory')
        location_obj = self.pool.get('stock.location')
        inv_line_obj = self.pool.get('stock.inventory.line')
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            inv_id = inventory_obj.create(cr, uid, {
                'name':'INICIAL',
                'date':time.strftime('%Y-%m-%d'),
                'date_done':time.strftime('%Y-%m-%d'),
            })
            for r in range(sh.nrows)[1:]:
                aux_name = ustr(sh.cell(r,3).value)
                aux_code = ustr(sh.cell(r,2).value)
                aux_acc = ustr(sh.cell(r,1).value)
                account_ids = account_obj.search(cr, uid, [('code_aux','=',aux_acc)],limit=1)
                product_ids = product_obj.search(cr, uid, [('name','=',aux_name),('default_code','=',aux_code)])
                if product_ids:
                    if len(product_ids)>1:
                        p1 = product_obj.browse(cr, uid, product_ids[0])
                        p2 = product_obj.browse(cr, uid, product_ids[1])
                        p_id = p2.id
                        if p1.standard_price > p2.standard_price:
                            p_id = p1.id
                        print 'PRODUCO RePETIDO', aux_name, aux_code
                else:
                    print "NO PRODUCTO", aux_name, aux_code
                producto = product_obj.browse(cr, uid, product_ids[0])
                bodega_ids = location_obj.search(cr, uid, [('name','=','Stock')],limit=1)
                if not bodega_ids:
                    print "No bodega"
                line_id = inv_line_obj.create(cr, uid, {
                    'inventory_id':inv_id,
                    'location_id':bodega_ids[0],
                    'product_id':product_ids[0],
                    'product_uom':producto.uom_id.id,
                    'product_qty':float(sh.cell(r,6).value),
                })
        return True



    def productosSigame(self, cr, uid, ids, context={}):
        product_obj = self.pool.get('product.product')
        category_obj = self.pool.get('product.category')
        subcategory_obj = self.pool.get('product.subcategory')
        account_obj = self.pool.get('account.account')
        uom_obj = self.pool.get('product.uom')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                aux_is = ustr(sh.cell(r,9).value)
                if aux_is =='M':
                    cta_ids = account_obj.search(cr, uid, [('code_aux','=',str(sh.cell(r,1).value))],limit=1)
                    if not cta_ids:
                        cta_ids = account_obj.search(cr, uid, [('type','=','other')],limit=1)
                    aux_categ_code = str(sh.cell(r,2).value)
                    tamano = len(aux_categ_code)
                    if tamano>3:
                        aux_tam = tamano - 4 
                        categ_ids = category_obj.search(cr, uid, [('code','=',aux_categ_code[0:aux_tam])])
                    if not categ_ids:
                        print "NO CATEG", aux_categ_code
                    scateg_ids = subcategory_obj.search(cr, uid, [('categ_id','=',categ_ids[0])],limit=1)
                    if scateg_ids:
                       scateg_id = scateg_ids[0]
                    else:
                        categ = category_obj.browse(cr, uid, categ_ids[0])
                        scateg_id = subcategory_obj.create(cr, uid, {
                            'name':categ.name,
                            'categ_id':categ_ids[0],
                        })
                    uom_ids = uom_obj.search(cr, uid, [('name','=',str(sh.cell(r,10).value))],limit=1)
                    if not uom_ids:
                        print "NO UDMMMM", str(sh.cell(r,10).value)
                    context['opc']=1
                    product_id = product_obj.create(cr, uid, {
                        'name':ustr(sh.cell(r,3).value),
                        'standard_price':float(sh.cell(r,8).value),
                        'default_code':str(sh.cell(r,2).value),
                        'type':'product',
                        'cost_method':'average',
                        'property_account_expense':cta_ids[0],
                        'categ_id':categ_ids[0],
                        'subcateg_id':scateg_id,
                        'uom_id':uom_ids[0],
                        'uos_id':uom_ids[0],
                        'uom_po_id':uom_ids[0],
                        'procure_method':'make_to_stock',
                        'valuation':'real_time',
                    },context)
                
                

    def bancoSigame(self, cr, uid, ids, context={}):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        b_obj = self.pool.get('res.bank')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                aux_ced_ruc = str(sh.cell(r,2).value)
                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                if partner_ids:
                    if len(partner_ids)>1:
                        raise osv.except_osv(('Partner duplicado!'),'Partner con cedula/ruc'%(str(sh.cell(r,2).value)))
                    else:
                        partner_id = partner_ids[0]
                else:
                    aux_tipo = 'cedula'
                    aux_persona = '6'
                    if len(aux_ced_ruc)>10:
                        aux_tipo = 'ruc'
                    partner_id = partner_obj.create(cr, uid, {
                        'ced_ruc':aux_ced_ruc,
                        'type_ced_ruc':aux_tipo,
                        'tipo_persona':aux_persona,
                        'name':ustr(sh.cell(r,1).value),
                        'direccion':ustr(sh.cell(r,1).value),
                        'telefono':'2222222',
                        'property_account_receivable':1689,
                        'property_account_payable':2823,
                        'property_account_position':2,
                    })
                num_banco = str(sh.cell(r,6).value)
                bank_ids = b_obj.search(cr, uid, [('bic','=',num_banco)])
                if not bank_ids:
                    print "NO HAY BANCO", num_banco
                else:
                    tipo_c = str(sh.cell(r,4).value)
                    if tipo_c=='1':
                        tipo_c_aux = 'cte'
                    else:
                        tipo_c_aux = 'aho'
                    cuenta_ids = bank_obj.search(cr, uid, [('partner_id','=',partner_id),('bank','=',bank_ids[0]),('type_cta','=',tipo_c_aux),('acc_number','=',str(sh.cell(r,3).value))])
                    if not cuenta_ids:
                        bank_obj.create(cr, uid, {
                            'partner_id':partner_id,
                            'bank':bank_ids[0],
                            'type_cta':tipo_c_aux,
                            'acc_number':str(sh.cell(r,3).value),
                        })
                        num += 1
                    else:
                        print "no se crea cuenta"
        print num, " cuentas creadas"
        return True

    def partidaParent(self, cr, uid, ids, context={}):
        post_obj = self.pool.get('budget.post')
        post_ids = post_obj.search(cr, uid, [('parent_id','=',False)])
        print "POSSSSSTTTT SIN PAPA", post_ids
        for post_id in post_ids:
            post = post_obj.browse(cr, uid, post_id)
            code = post.code
#            if code=='77029902047181035':
#                import pdb
#                pdb.set_trace()
            if len(code)==6:
                parent_ids = post_obj.search(cr, uid, [('code','=',code[0:4])],limit=1)
                if parent_ids:
                    post_obj.write(cr, uid, post_id, {
                        'parent_id':parent_ids[0],
                    })
                else:
                    "print no papa 6", code
            elif len(code)==8:
                parent_ids = post_obj.search(cr, uid, [('code','=',code[0:6])],limit=1)
                if parent_ids:
                    post_obj.write(cr, uid, post_id, {
                        'parent_id':parent_ids[0],
                    })
                else:
                    "print no papa 8", code
            elif len(code)==11:
                parent_ids = post_obj.search(cr, uid, [('code','=',code[0:8])],limit=1)
                if parent_ids:
                    post_obj.write(cr, uid, post_id, {
                        'parent_id':parent_ids[0],
                    })
                else:
                    "print no papa 11", code
            elif len(code)==14:
                parent_ids = post_obj.search(cr, uid, [('code','=',code[0:11])],limit=1)
                if parent_ids:
                    post_obj.write(cr, uid, post_id, {
                        'parent_id':parent_ids[0],
                    })
                else:
                    "print no papa 14", code                
            elif len(code)==17:
                parent_ids = post_obj.search(cr, uid, [('code','=',code[0:14])],limit=1)
                if parent_ids:
                    post_obj.write(cr, uid, post_id, {
                        'parent_id':parent_ids[0],
                    })
                else:
                    "print no papa 17", code
            else:
                "NO ENTRSSSSSSSSSSSSSSSS", code
        return True

    def partidasAdicionales(self, cr, uid, ids, context={}):
        post_obj = self.pool.get('budget.post')
        user_type = self.pool.get('budget.user.type')
        data = self.read(cr, uid, ids)[0]
        arch = data['archivo']
        arch_xls = base64.b64decode(arch)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_name(book.sheet_names()[0])
        context={}
        user_ids = user_type.search(cr, uid, [('name','=','Corriente')],limit=1)
        for r in range(sh.nrows)[1:]:
            if ustr(sh.cell(r,1).value) != '0':
                aux_code = ustr(sh.cell(r,2).value).replace('.','')
                post_ids = post_obj.search(cr, uid, [('code','=',aux_code)])
                if not post_ids:
                    post_obj.create(cr, uid, {
                        'code':aux_code,
                        'name':ustr(sh.cell(r,3).value),
                        'internal_type':'gasto',
                        'budget_type_id':user_ids[0],
                    })
        return True

    def cargarPartidaPrograma(self, cr, uid, ids, context={}):
        item_obj = self.pool.get('budget.item')
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        data = self.read(cr, uid, ids)[0]
        arch = data['archivo']
        arch_xls = base64.b64decode(arch)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_name(book.sheet_names()[0])
        context={}
        for r in range(sh.nrows)[1:]:
            cedula = ustr(sh.cell(r,0).value)
            nombre = ustr(sh.cell(r,1).value)
            #busco empleado con esta cedula
            employee_ids = employee_obj.search(cr, uid, [('name','=',cedula)])
            if employee_ids:
                employee_id = employee_ids[0]
                contract_ids = contract_obj.search(cr, uid, [('employee_id','=', employee_id)])
                if contract_ids:
                    partida = ustr(sh.cell(r,3).value)
                    programa = ustr(sh.cell(r,2).value)
                    budget_code = partida+'.000.'+programa
                    item_ids = item_obj.search(cr, uid, [('code','=',budget_code)])
                    if item_ids:
                        item_data = item_obj.read(cr, uid, item_ids[0],['id','program_id'])
                        contract_obj.write(cr, uid, contract_ids[0], {'program_id': item_data['program_id'][0], 'budget_id': item_data['id']})
                    else:
                        print "no existe la partida", budget_code, cedula, nombre, partida, programa
                else:
                    print "no existe contrato para el empleado", cedula, nombre,partida, programa
            else:
                print "no existe empleado", cedula, nombre, partida, programa
        return True

    def updateAll(self, cr, uid, ids, context={}):
        move_line_obj = self.pool.get('account.move.line')
        line_ids = move_line_obj.search(cr, uid, [('move_id.migrado','=',True),('move_id.state','=','draft')])
        move_line_obj.write(cr, uid, line_ids, {'aux_update': 'a'})
#        move_obj = self.pool.get('account.move')
#        move_ids = move_obj.search(cr, uid, [('migrado','=',True),('state','draft')])
#        move_obj.write(cr, uid, move_ids, {'aux_update': 'a'})
        return True

    def loadIngresos(self, cr, uid, ids, context=None):
        print "sube asiento"
        rucMuni = '0660000360001'
        nomMuni = 'GAD MUNICIPAL DE RIOBAMBA'
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        partner_obj = self.pool.get('res.partner')
        account_obj = self.pool.get('account.account')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        journal_obj = self.pool.get('account.journal')
        data = self.read(cr, uid, ids)[0]
        if data['journal_id']:
            if data['archivo']:
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:
                    journal_aux = data['journal_in'][0]
                    name_aux =  ustr(sh.cell(r,0).value)
                    date = ustr(sh.cell(r,1).value)
                    period_ids = period_obj.search(cr, uid, [('date_start','<=',date_aux2),
                                                             ('date_stop','>=',date_aux2)],limit=1)
                    partner_id = 1
                    desc_aux = ustr(sh.cell(r,2).value) + ' ' + ustr(sh.cell(r,4).value) 
                    move_id = move_obj.create(cr, uid, {
                        'partner_id':partner_id,
                        'journal_id':journal_aux,
                        'date':date_aux2,
                        'period_id':period_ids[0],
                        'name':name_aux,
                        'ref':desc_aux,
                        'narration':desc_aux,
                        'certificate_id': 4273,
                        'afectacion':True,
                        'state': 'draft'
                    })

    def loadAsientoDetalleAA(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        project_obj = self.pool.get('project.project')
        dept_obj = self.pool.get('hr.department')
        emp_obj = self.pool.get('hr.employee')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            for r in range(sh.nrows)[1:]:
                debe = 0.0
                haber = 0.0
                move_aux = ustr(sh.cell(r,2).value).zfill(5)
                code_cuenta = str(sh.cell(r,1).value).replace('.','')
                account_ids = account_obj.search(cr, uid, [('code','=',code_cuenta)])
                move_ids = move_obj.search(cr, uid, [('name','=',move_aux),('fiscalyear_id','=',data['period_id'][0])])
                if move_ids:
                    move = move_obj.browse(cr, uid, move_ids[0])
                    aux_move_name = move.name
                    move_id = move.id
                else:
                    print "NO MOVE", move_aux
                journal_id = move.journal_id.id
                period_id = move.period_id.id
                date = move.date
                if account_ids:
                    cuenta_id = account_ids[0]
                else:
                    print "llinea", r
                    print "cuenta creada", code_cuenta,
                    #no existe la cuenta, por lo que se debe crear
                    account_id = account_obj.create(cr, uid, {
                        'name':code_cuenta,
                        'code':code_cuenta,
                        'code_aux': ustr(sh.cell(r,1).value),
                        'type':'other',
                        'user_type':6,
                    })
                    cuenta_id = account_id
                    print "cuenta creada", code_cuenta,
                tipo = ustr(sh.cell(r,4).value)
                band=True
                if tipo == 'DEBE':
                    debe = round(float(sh.cell(r,3).value),2)
                else:
                    haber = round(float(sh.cell(r,3).value),2)
                name = ustr(sh.cell(r,12).value)
                sql = '''
                INSERT INTO account_move_line (
                move_id,name,account_id,debit,credit,journal_id,period_id,date,state,company_id,currency_id,migrado,is_start,num_comp) VALUES (%s, '%s',%s,%s,%s,%s,%s,'%s','%s',%s,%s,%s,%s,%s)'''%(move_id,name,cuenta_id,debe,haber,journal_id,period_id,date,state_aux,company_aux,currency_aux,True,False,aux_move_name)
                cr.execute(sql)
        self.updateAll(cr, uid, [])
        return True    

    def loadAsientoAA(self, cr, uid, ids, context=None):
        print "sube asiento"
        rucMuni = '0968519280001'
        nomMuni = 'GAD EL EMPALME'
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        partner_obj = self.pool.get('res.partner')
        account_obj = self.pool.get('account.account')
        certificate_obj = self.pool.get('budget.certificate')
        journal_obj = self.pool.get('account.journal')
        data = self.read(cr, uid, ids)[0]
        if data['journal_id']:
            if data['archivo']:
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                con_certificado = False
                if data['asiento_type']=='cc':
                    for r in range(sh.nrows)[1:]:
                        if ustr(sh.cell(r,1).value) == 'NULL':
                            print "HAY NULL EN", r
                            continue
                        aux_state = ''
                        aux_tipo_comp = ustr(sh.cell(r,6).value)
                        if aux_tipo_comp == 'EGRESO':
                            journal_aux = data['journal_id'][0]
                        elif aux_tipo_comp == 'INGRESO':
                            journal_aux = data['journal_in'][0]
                        else:
                            journal_aux = data['journal_diario'][0]
                        date_aux2 = ustr(sh.cell(r,1).value)
                        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_aux2),
                                                                 ('date_stop','>=',date_aux2)],limit=1)
                        name_aux = ustr(sh.cell(r,0).value).zfill(5)#numero
                        desc_aux = ustr(sh.cell(r,2).value) + ' - ' + ustr(sh.cell(r,4).value)
                        aux_cedruc = ustr(sh.cell(r,13).value)
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedruc)])
                        if partner_ids:
                            partner_id = partner_ids[0]
                        else:
                            aux_ced = aux_cedruc
                            name = ustr(sh.cell(r,6).value)
                            if len(aux_ced)==13:
                                type_ced_ruc = 'ruc'
                            elif len(aux_ced)==10:
                                type_ced_ruc = 'cedula'
                            else:
                                type_ced_ruc = 'pasaporte'
                            if ustr(sh.cell(r,6).value) == 'PROVEEDOR':
                                print "NO PARTNER ========================>", aux_cedruc, "creando partner..."
                                direccion = ustr(sh.cell(r,9).value)
                                mail = ustr(sh.cell(r,10).value)
                                telefono = ustr(sh.cell(r,11).value)
                                if direccion is None:
                                    direccion = ""
                                if mail is None:
                                    mail = ""
                                if telefono is None:
                                    telefono = ""                                
                                partner_id = partner_obj.create(cr, uid, {
                                    'ced_ruc':aux_cedruc,
                                    'type_ced_ruc':'pasaporte',
                                    'tipo_persona':'6',
                                    'name':ustr(sh.cell(r,6).value),
                                    'direccion':direccion,
                                    'email': mail,
                                    'telefono':telefono,
                                    'property_account_receivable':20446,
                                    'property_account_payable':25391,
                                    'property_account_position':2,})
                            elif ustr(sh.cell(r,6).value) == 'FUNCIONARIO':
                                aux_cedruc = rucMuni
                                partner_id = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedruc)])[0]
                            else:
                                aux_cedruc = rucMuni
                                partner_id = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedruc)])[0]
                        #Antes de crear el movimiento busco la relacion con la certificacion presupuestaria
                        move_id = move_obj.create(cr, uid, {
                            'partner_id':partner_id,
                            'journal_id':journal_aux,
                            'date':date_aux2,
                            'period_id':period_ids[0],
                            'name':name_aux,
                            'ref':desc_aux,
                            'narration':desc_aux,
                            'migrado':True,
                            'afectacion':True,
                            'state': 'draft'
                        })
                elif data['asiento_type']=='cs':
                    partner_id = 1
                    for r in range(sh.nrows)[1:]:
                        if ustr(sh.cell(r,1).value) == 'NULL':
                            print "HAY NULL EN", r
                            continue  
                        aux_tipo_comp = ustr(sh.cell(r,6).value)
                        if aux_tipo_comp == 'EGRESO':
                            journal_aux = data['journal_id'][0]
                        elif aux_tipo_comp == 'INGRESO':
                            journal_aux = data['journal_in'][0]
                        else:
                            journal_aux = data['journal_diario'][0]
                        date_aux2 = ustr(sh.cell(r,1).value)
                        name_aux = ustr(sh.cell(r,0).value).zfill(5)#numero
                        desc_aux = ustr(sh.cell(r,2).value) + ' - ' + ustr(sh.cell(r,4).value)
                        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_aux2),
                                                                 ('date_stop','>=',date_aux2)],limit=1)
                        #Antes de crear el movimiento busco la relacion con la certificacion presupuestaria
                        move_id = move_obj.create(cr, uid, {
                            'state':'draft',
                            'partner_id':partner_id,
                            'journal_id':journal_aux,
                            'date':date_aux2,
                            'period_id':period_ids[0],
                            'name':name_aux,
                            'ref':desc_aux,
                            'narration':desc_aux,
                            'migrado':True,
                            'afectacion':True,
                        })
#        self.updateAll(cr, uid, [])
        return True

    def loadPartidaRubro(self, cr, uid, ids, context=None):
        return True

    def load_asiento_sigame(self, cr, uid, ids, context=None):
        print "sube asiento"
        rucMuni = '0660000360001'
        nomMuni = 'GAD MUNICIPAL DE RIOBAMBA'
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        partner_obj = self.pool.get('res.partner')
        account_obj = self.pool.get('account.account')
        certificate_obj = self.pool.get('budget.certificate')
        journal_obj = self.pool.get('account.journal')
        data = self.read(cr, uid, ids)[0]
        if data['journal_id']:
            if data['archivo']:
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                con_certificado = False
                if data['asiento_type']=='cc':
                    for r in range(sh.nrows)[1:]:
                        if ustr(sh.cell(r,1).value) == 'NULL':
                            print "HAY NULL EN", r
                            continue
                        aux_state = ''
                        aux_tipo_comp = ustr(sh.cell(r,6).value)
                        if aux_tipo_comp == 'EGRESO':
                            journal_aux = data['journal_id'][0]
                        elif aux_tipo_comp == 'INGRESO':
                            journal_aux = data['journal_in'][0]
                        else:
                            journal_aux = data['journal_diario'][0]
                        date_aux2 = ustr(sh.cell(r,1).value)
                        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_aux2),
                                                                 ('date_stop','>=',date_aux2)],limit=1)
                        name_aux = ustr(sh.cell(r,0).value).zfill(5)#numero
                        desc_aux = ustr(sh.cell(r,2).value) + ' - ' + ustr(sh.cell(r,4).value)
                        aux_cedruc = ustr(sh.cell(r,13).value)
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedruc)])
                        if partner_ids:
                            partner_id = partner_ids[0]
                        else:
                            aux_ced = aux_cedruc
                            name = ustr(sh.cell(r,6).value)
                            if len(aux_ced)==13:
                                type_ced_ruc = 'ruc'
                            elif len(aux_ced)==10:
                                type_ced_ruc = 'cedula'
                            else:
                                type_ced_ruc = 'pasaporte'
                            if ustr(sh.cell(r,6).value) == 'PROVEEDOR':
                                print "NO PARTNER ========================>", aux_cedruc, "creando partner..."
                                direccion = ustr(sh.cell(r,9).value)
                                mail = ustr(sh.cell(r,10).value)
                                telefono = ustr(sh.cell(r,11).value)
                                if direccion is None:
                                    direccion = ""
                                if mail is None:
                                    mail = ""
                                if telefono is None:
                                    telefono = ""                                
                                partner_id = partner_obj.create(cr, uid, {
                                    'ced_ruc':aux_cedruc,
                                    'type_ced_ruc':'pasaporte',
                                    'tipo_persona':'6',
                                    'name':ustr(sh.cell(r,6).value),
                                    'direccion':direccion,
                                    'email': mail,
                                    'telefono':telefono,
                                    'property_account_receivable':20446,
                                    'property_account_payable':25391,
                                    'property_account_position':2,})
                            elif ustr(sh.cell(r,6).value) == 'FUNCIONARIO':
                                aux_cedruc = rucMuni
                                partner_id = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedruc)])[0]
                            else:
                                aux_cedruc = rucMuni
                                partner_id = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedruc)])[0]
                        #Antes de crear el movimiento busco la relacion con la certificacion presupuestaria
                        if con_certificado==False:
                            move_id = move_obj.create(cr, uid, {
                                'partner_id':partner_id,
                                'journal_id':journal_aux,
                                'date':date_aux2,
                                'period_id':period_ids[0],
                                'name':name_aux,
                                'ref':desc_aux,
                                'narration':desc_aux,
                                'migrado':True,
                                'afectacion':True,
                                'state': 'draft'
                                })
                        else:
                            campo_cert = ustr(sh.cell(r,4).value)
                            num_cert = False
                            campo_cert = unicodedata.normalize('NFKD',campo_cert).encode('ascii','ignore')
                            #print "campo_cert", campo_cert
                            pos_1 = False
                            pos_2 = False
                            if re.search("Certificacion #: ",campo_cert):
                                pos_1 = re.search("Certificacion #: ",campo_cert).span()[1]
                                if re.search("Certificacion #: \d+[\.]?\d",campo_cert):
                                    pos_2 = re.search("Certificacion #: \d+[\.]?\d",campo_cert).span()[1]
                                elif re.search("Certificacion #: \d",campo_cert):
                                    pos_2 = re.search("Certificacion #: \d",campo_cert).span()[1]
                                else:
                                    raise osv.except_osv('Error certificacion!','No se encuentra el numero de certificacion en %s'%(campo_cert))
                                num_cert = campo_cert[pos_1:pos_2]
                                #busco la certificacion
                                if pos_1 and pos_2:
                                    certificate_ids = certificate_obj.search(cr, uid, [('name','=',num_cert)])
                                    if certificate_ids:
                                        num_cert = certificate_ids[0]
                                    else:
                                        print 'No se encuentra la certificacion con numero %s'%(num_cert), "numero de asiento: ", ustr(sh.cell(r,0).value)
                                else:    
                                    print 'No se encuentra la certificacion con numero %s'%(num_cert), "numero de asiento: ", ustr(sh.cell(r,0).value)
                            move_id = move_obj.create(cr, uid, {
                                'partner_id':partner_id,
                                'journal_id':journal_aux,
                                'date':date_aux2,
                                'period_id':period_ids[0],
                                'name':name_aux,
                                'ref':desc_aux,
                                'narration':desc_aux,
                                'migrado':True,
                                'certificate_id': num_cert,
                                'afectacion':True,
                                'state': 'draft'
                                })
                elif data['asiento_type']=='cs':
                    partner_id = 1
                    for r in range(sh.nrows)[1:]:
                        if ustr(sh.cell(r,1).value) == 'NULL':
                            print "HAY NULL EN", r
                            continue  
                        aux_tipo_comp = ustr(sh.cell(r,6).value)
                        if aux_tipo_comp == 'EGRESO':
                            journal_aux = data['journal_id'][0]
                        elif aux_tipo_comp == 'INGRESO':
                            journal_aux = data['journal_in'][0]
                        else:
                            journal_aux = data['journal_diario'][0]
                        date_aux2 = ustr(sh.cell(r,1).value)
                        name_aux = ustr(sh.cell(r,0).value).zfill(5)#numero
                        desc_aux = ustr(sh.cell(r,2).value) + ' - ' + ustr(sh.cell(r,4).value)
                        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_aux2),
                                                                 ('date_stop','>=',date_aux2)],limit=1)
                        #Antes de crear el movimiento busco la relacion con la certificacion presupuestaria
                        if con_certificado==False:
                            move_id = move_obj.create(cr, uid, {
                                'state':'draft',
                                'partner_id':partner_id,
                                'journal_id':journal_aux,
                                'date':date_aux2,
                                'period_id':period_ids[0],
                                'name':name_aux,
                                'ref':desc_aux,
                                'narration':desc_aux,
                                'migrado':True,
                                'afectacion':True,
                            })
                        else:    
                            campo_cert = ustr(sh.cell(r,3).value)
                            num_cert = False
                            campo_cert = unicodedata.normalize('NFKD',campo_cert).encode('ascii','ignore')
                            #print "campo cert", campo_cert
                            pos_1 = False
                            pos_2 = False
                            if re.search("Certificacion #: ",campo_cert):
                                pos_1 = re.search("Certificacion #: ",campo_cert).span()[1]
                                if re.search("Certificacion #: \d+[\.]?\d",campo_cert):
                                    pos_2 = re.search("Certificacion #: \d+[\.]?\d",campo_cert).span()[1]
                                elif re.search("Certificacion #: \d",campo_cert):
                                    pos_2 = re.search("Certificacion #: \d",campo_cert).span()[1]
                                num_cert = campo_cert[pos_1:pos_2]
                                #busco la certificacion
                                if pos_1 and pos_2:
                                    certificate_ids = certificate_obj.search(cr, uid, [('name','=',num_cert)])
                                    if certificate_ids:
                                        num_cert = certificate_ids[0]
                                else:
                                    print 'No se encuentra la certificacion con numero %s'%(num_cert), "numero de asiento: ", ustr(sh.cell(r,0).value)
                            move_id = move_obj.create(cr, uid, {
                                'state':'draft',
                                'partner_id':partner_id,
                                'journal_id':journal_aux,
                                'date':date_aux2,
                                'period_id':period_ids[0],
                                'name':name_aux,
                                'ref':desc_aux,
                                'narration':desc_aux,
                                'migrado':True,
                                'certificate_id': num_cert,
                                'afectacion':True,

                            })
        self.updateAll(cr, uid, [])
        return True

    def updateDatePicking(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        pick_ids = pick_obj.search(cr, uid,[])
        if pick_ids:
            for pick_id in pick_ids:
                picking = pick_obj.browse(cr, uid, pick_id)
                if picking.date_done:
                    aux_date = picking.date_done
                    move_ids = move_obj.search(cr, uid, [('picking_id','=',pick_id)])
                    if move_ids:
                        if len(move_ids)>1:
                            move_ids_aux = tuple(move_ids)
                            operator = 'in'
                        else:
                            move_ids_aux = (move_ids[0])
                            operator = '='
                        aux_date_2 = "'" + aux_date + "'"
                        sql = "UPDATE stock_move set date=%s where id %s %s" % (aux_date_2,operator,move_ids_aux)
                        cr.execute(sql)
#                        for move_id in move_ids:
#                            move_obj.write(cr, uid, move_id,{
#                                'date':aux_date,
#                            })
        return True

    def load_inicial_olympo(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['asiento_type']=='inicial' and data['tipo_sistema']=='sigame':
            #busco asiento con numero CERO
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            move_ids = move_obj.search(cr, uid, [('name','=','0')])
            if move_ids:
                move_id = move_ids[0]
                move = move_obj.browse(cr, uid, move_ids[0])
                journal_id = move.journal_id.id
                period_id = move.period_id.id
                date = move.date
            else:
                'No move de inicio'
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                code_cta = str(sh.cell(r,0).value)[0:15].replace('.','')
                account_ids = account_obj.search(cr, uid, [('code','=',code_cta)])
                debe = float(sh.cell(r,1).value)
                haber = float(sh.cell(r,2).value)
                name = 'Inicial'
                if not account_ids:
                    print "No cuenta", code_cta
                    cuenta_id = account_obj.create(cr, uid, {
                        'code':code_cta,
                        'code_aux':str(sh.cell(r,0).value),
                        'name':ustr(sh.cell(r,2).value),
                        'type':'other',
                        'user_type':6,
                    })
                else:
                    cuenta_id = account_ids[0]
                sql = '''
                INSERT INTO account_move_line (
                move_id,name,account_id,debit,credit,journal_id,period_id,date,state,company_id,currency_id,migrado) VALUES (%s,'%s',%s,%s,%s,%s,%s,'%s','%s',%s,%s,%s)'''%(move_id,name,cuenta_id,debe,haber,journal_id,period_id,date,state_aux,company_aux,currency_aux,True)
                cr.execute(sql)
        self.updateAll(cr, uid, [])
        return True


    def load_inicial_sigame(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['asiento_type']=='inicial' and data['tipo_sistema']=='sigame':
            #busco asiento con numero CERO
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            move_ids = move_obj.search(cr, uid, [('name','=','0')])
            if move_ids:
                move_id = move_ids[0]
                move = move_obj.browse(cr, uid, move_ids[0])
                journal_id = move.journal_id.id
                period_id = move.period_id.id
                date = move.date
            else:
                'No move de inicio'
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                code_cta = str(sh.cell(r,0).value).replace('.','')
                debe = float(sh.cell(r,5).value)
                haber = float(sh.cell(r,6).value)
                name = 'Inicial'
                if debe!=0 or haber!=0:
                    account_ids = account_obj.search(cr, uid, [('code','=',code_cta)])    
                    if not account_ids:
                        print "No cuenta", code_cta
                        cuenta_id = account_obj.create(cr, uid, {
                            'code':code_cta,
                            'code_aux':str(sh.cell(r,0).value),
                            'name':ustr(sh.cell(r,2).value),
                            'type':'other',
                            'user_type':6,
                        })
                    else:
                        cuenta_id = account_ids[0]
                    sql = '''
                    INSERT INTO account_move_line (
                    move_id,name,account_id,debit,credit,journal_id,period_id,date,state,company_id,currency_id,migrado) VALUES (%s,'%s',%s,%s,%s,%s,%s,'%s','%s',%s,%s,%s)'''%(move_id,name,cuenta_id,debe,haber,journal_id,period_id,date,state_aux,company_aux,currency_aux,True)
                    cr.execute(sql)
        self.updateAll(cr, uid, [])
        return True


    def load_asiento_detalle_sigame_concp(self, cr, uid, ids, context=None):
        cert_nuevo = {}
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        cert_obj = self.pool.get('budget.certificate')
        cert_line_obj = self.pool.get('budget.certificate.line')
        project_obj = self.pool.get('project.project')
        dept_obj = self.pool.get('hr.department')
        emp_obj = self.pool.get('hr.employee')
        item_obj = self.pool.get('budget.item')
        data = self.read(cr, uid, ids)[0]
        cert_dict = {}
        cert_dict_aux = {}
        cert_ids = cert_obj.search(cr, uid, [('migrado','=',True)])
        cert_ids2 = cert_obj.search(cr, uid, [('name','=','ING001')])
        cert_ids = cert_ids + cert_ids2
        cert_data = cert_obj.read(cr, uid, cert_ids, ['id','name'])
        budget_item_obj = self.pool.get('budget.item')
        budget_item_ids = budget_item_obj.search(cr, uid, [])
        budget_item_data = budget_item_obj.read(cr, uid, budget_item_ids,['id','code'])
        budget_dict = {}
        move_dict = {}
        cuenta_dict = {}
        cuenta_ids = account_obj.search(cr, uid, [])
        cuenta_data = account_obj.read(cr, uid, cuenta_ids, ['id','code_aux','code'])
        for cuenta in cuenta_data:
            cuenta_dict[cuenta['code']] = cuenta['id']
        move_ids = move_obj.search(cr, uid, [('migrado','=',True)])
        move_data = move_obj.read(cr, uid, move_ids, ['id','name','certificate_id','journal_id','date','period_id'])
        for move in move_data:
            move_dict[move['name']] = [move['id'],
                                       move['certificate_id'] and move['certificate_id'][0] or False,
                                       move['name'],
                                       move['journal_id'] and move['journal_id'][0] or False,
                                       move['date'],
                                       move['period_id'] and move['period_id'][0] or False]
        for budget in budget_item_data:
            budget_dict[budget['id']] = budget['code']
        for cert in cert_data:
            cert_dict[cert['name']] = {}
            cert_dict_aux[cert['id']] = cert['name']
        #armo un diccionario con todas las lineas de certificacion creadas en el sistema
        #para no realizar una busqueda con cada linea de asiento
        cert_line_ids = cert_line_obj.search(cr, uid, [('migrado','=',True)])
        cert_line_ids2 = cert_line_obj.search(cr, uid, [('certificate_id','=',cert_ids2[0])])
        cert_line_ids = cert_line_ids + cert_line_ids2
        cert_line_data = cert_line_obj.read(cr, uid, cert_line_ids, ['id','certificate_id','budget_id'])
        for line in cert_line_data:
            num_cert = cert_dict_aux[line['certificate_id'][0]]
            budget_id_aux = line['budget_id'][0]
            code_aux = budget_dict[budget_id_aux]
            code = code_aux[0:10]
            cert_dict[num_cert].update({code:line})
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            aux_value_debit = 0
            for r in range(sh.nrows)[1:]:
                debe = 0.0
                haber = 0.0
                partida = True
                budget_accrued =False
                budget_paid = False
                budget_cert_line_id = 'Null'
                move_id = move_dict[ustr(sh.cell(r,2).value)][0]
                name = move_dict[ustr(sh.cell(r,2).value)][2]
                journal_id = move_dict[ustr(sh.cell(r,2).value)][3]
                date = move_dict[ustr(sh.cell(r,2).value)][4]
                period_id = move_dict[ustr(sh.cell(r,2).value)][5]
                code_cuenta = ustr(sh.cell(r,1).value).replace('.','')
                if cuenta_dict.get(code_cuenta,False):
                    cuenta_id = cuenta_dict[code_cuenta]
                else:
                    #no existe la cuenta, por lo que se debe crear
                    account_id = account_obj.create(cr, uid, {
                        'name':code_cuenta,
                        'code':code_cuenta,
                        'code_aux': ustr(sh.cell(r,1).value),
                        'type':'other',
                        'user_type':6,
                    })
                    cuenta_dict.update({code_cuenta: account_id})
                    cuenta_id = account_id
                    print "cuenta creada", code_cuenta,
                tipo = ustr(sh.cell(r,4).value)
                band=True
                if tipo == 'DEBE':
                    debe = round(float(sh.cell(r,3).value),2)
                else:
                    haber = round(float(sh.cell(r,3).value),2)
                code_budget_post = ustr(sh.cell(r,5).value).replace('.','')
                if code_budget_post == '0&0':
                    partida = False
                else:
                    cert_aux = move_dict[ustr(sh.cell(r,2).value)][1]
                    partida = code_budget_post[0:6]
                    proyecto_aux = ustr(sh.cell(r,6).value)
                    if proyecto_aux == "0":
                        proyecto = "000"
                    else:
                        proyecto = proyecto_aux.replace('.','')
                    tipo_pre = ustr(sh.cell(r,7).value)
                    if tipo_pre == 'D':
                        budget_accrued = True
                    elif tipo_pre == 'E':
                        budget_paid = True
                    if proyecto=="000" and partida!=False:
                        if cert_dict['ING001'].get(partida+'.'+proyecto,False):
                            budget_cert_line_id = cert_dict['ING001'][partida+'.'+proyecto]['id']
                        else:
                            print "no existe la partida", partida+'.'+proyecto, "en el certificado de ingreso: ING001", " - ", r+1
                    else:
                        if cert_aux!=False:
                            if cert_dict[cert_dict_aux[cert_aux]].get(partida+'.'+proyecto,False):
                                budget_cert_line_id = cert_dict[cert_dict_aux[cert_aux]][partida+'.'+proyecto]['id']
                            else:
                                # busco certificate_line para ese budget_item
                                item_ids = item_obj.search(cr, uid, [('code','=',partida+'.'+proyecto+'1.'+proyecto[0:2])])
                                if item_ids:
                                    certificate_line_ids = cert_line_obj.search(cr, uid, [('budget_id','=',item_ids[0])])
                                    budget_cert_line_id = certificate_line_ids[0]
                                else:
                                    print "no existe la partida", partida+'.'+proyecto, "en el certificado ", cert_aux, " - ", r+1
                        else:
                            #                            band=False
                            item_ids = item_obj.search(cr, uid, [('code','=',partida+'.'+proyecto+'1.'+proyecto[0:2])])
                            if item_ids:
                                certificate_line_ids = cert_line_obj.search(cr, uid, [('budget_id','=',item_ids[0])])
                                budget_cert_line_id = certificate_line_ids[0]
                            else:
                                print "no existe certificacion presupuestaria para el movimiento", ustr(sh.cell(r,2).value), " - ", r+1
                if band==True:
                    sql = '''
                    INSERT INTO account_move_line (
                    move_id,name,account_id,debit,credit,journal_id,period_id,date,state,company_id,currency_id,migrado,budget_id_cert,budget_accrued,budget_paid) VALUES (%s, '%s',%s,%s,%s,%s,%s,'%s','%s',%s,%s,%s,%s,%s,%s)'''%(move_id,name,cuenta_id,debe,haber,journal_id,period_id,date,state_aux,company_aux,currency_aux,True,budget_cert_line_id,budget_accrued,budget_paid)
                    cr.execute(sql)
        self.updateAll(cr, uid, [])
        return True    

    def load_asiento_detalle_sigame(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        cert_obj = self.pool.get('budget.certificate')
        cert_line_obj = self.pool.get('budget.certificate.line')
        project_obj = self.pool.get('project.project')
        dept_obj = self.pool.get('hr.department')
        emp_obj = self.pool.get('hr.employee')
        item_obj = self.pool.get('budget.item')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            total = 0
            #quitar espacios
            aux_coso = "'" + '% ' + "'"
            aux_acc = '''select id from account_account where code like %s order by code''' %(aux_coso)
            cr.execute(aux_acc)
            for cuenta_id in cr.fetchall():
                account_con_espacio = account_obj.browse(cr, uid, cuenta_id[0])
                code = account_con_espacio.code
                code_new = code.replace(' ','')
                account_ids = account_obj.search(cr, uid, [('code','=',code_new)])
                if account_ids:
                    move_ids = move_line_obj.search(cr, uid, [('account_id','=',account_ids[0])])
                    move_ids2= move_line_obj.search(cr, uid, [('account_id','=',cuenta_id[0])])
                    if move_ids and not move_ids2:
                        account_obj.unlink(cr, uid, [cuenta_id[0]])
                    elif move_ids2 and not move_ids:
                        account_obj.unlink(cr, uid, account_ids[0])
                        account_obj.write(cr, uid, cuenta_id[0],{
                            'code':code_new,
                        })  
                    else:
                        if not move_ids and not move_ids2:
                            print "NI UNO NI OTRO"
                        else:
                            print "A LA VER"
                else:
                    account_obj.write(cr, uid, cuenta_id[0],{
                        'code':code_new,
                    })
            for r in range(sh.nrows)[1:]:
                account_id = ''
                account_ids = []
                debe = 0.0
                haber = 0.0
                partida = False
                budget_accrued =False
                budget_paid = False
                budget_cert_line_id = 'Null'
                move_aux = ustr(sh.cell(r,2).value).zfill(5)
                code_cuenta = str(sh.cell(r,1).value).replace('.','')
                account_ids = account_obj.search(cr, uid, [('code','=',code_cuenta)])
                move_ids = move_obj.search(cr, uid, [('name','=',move_aux)])
                if move_ids:
                    move = move_obj.browse(cr, uid, move_ids[0])
                    aux_move_name = move.name
                    move_id = move.id
                else:
                    print "NOMOVE", move_aux
                journal_id = move.journal_id.id
                period_id = move.period_id.id
                date = move.date
                if account_ids:
                    cuenta_id = account_ids[0]
                else:
                    code_cuenta = code_cuenta + ' '
                    account_ids = account_obj.search(cr, uid, [('code','=',code_cuenta)])
                    if account_ids:
                        account_id = account_ids[0]
                    else:
                        code_cuenta = code_cuenta + ' '
                        account_ids = account_obj.search(cr, uid, [('code','=',code_cuenta)])
                        if account_ids:
                            account_id = account_ids[0]
                        else:
                            account_id = account_obj.create(cr, uid, {
                                'name':code_cuenta,
                                'code':code_cuenta,
                                'code_aux': ustr(sh.cell(r,1).value),
                                'type':'other',
                                'user_type':6,
                            })
                            cuenta_id = account_id
                            print "cuentacreadaLinea", code_cuenta
                tipo = ustr(sh.cell(r,4).value)
                band=True
                if tipo == 'DEBE':
                    debe = round(float(sh.cell(r,3).value),2)
                else:
                    haber = round(float(sh.cell(r,3).value),2)
                code_budget_post = ustr(sh.cell(r,5).value).replace('.','')
                name = ustr(sh.cell(r,12).value)
                if code_budget_post == '0&0':
                    partida = False
                else:
                    proyecto_aux = ustr(sh.cell(r,6).value)[0:4]
                    if proyecto_aux == "0":
                        proyecto = "000"
                    else:
                        proyecto = proyecto_aux.replace('.','')
                    tipo_pre = ustr(sh.cell(r,7).value)
                    if tipo_pre == 'D':
                        budget_accrued = True
                    elif tipo_pre == 'E':
                        budget_paid = True
                    #ojo pasar el budget_id y el budget_post
                    if proyecto=="000":
                        #es ingreso
                        if len(code_budget_post)>11:
                            code_budget_post = code_budget_post + '0'
                        item_ids = item_obj.search(cr, uid, [('code_aux','=',code_budget_post),('poa_id','=',1)])
                        if item_ids:
                            cert_line_ids = cert_line_obj.search(cr,uid, [('budget_id','=',item_ids[0])])
                            if cert_line_ids:
                                budget_cert_line_id = cert_line_ids[0]
                                linea_certificado = cert_line_obj.browse(cr, uid, cert_line_ids[0])
                                b_id = linea_certificado.budget_id.id
                                p_id = linea_certificado.budget_post.id
                                partida = True
                            else:
                                print "NOBUDGETINGRESO", code_budget_post
                        else:
                            print "ERGA"
                    else:
                        if len(code_budget_post)>11:
                            code_budget_post = code_budget_post + '0'
                        code_budget_post = proyecto_aux + code_budget_post
                        item_ids = item_obj.search(cr, uid, [('code','=',code_budget_post),('poa_id','=',1)])
                        if item_ids:
                            item = item_obj.browse(cr, uid, item_ids[0])
                            budget_cert_line_id =  cert_line_obj.create(cr, uid, {
                                'project_id':item.project_id.id,
                                'task_id':item.project_id.tasks[0].id,
                                'budget_id':item_ids[0],
                                'migrado':True,
                            })
                            linea_certificado = cert_line_obj.browse(cr, uid, budget_cert_line_id)
                            b_id = linea_certificado.budget_id.id
                            p_id = linea_certificado.budget_post.id
                            partida = True
                        else:
                            print "NOPARTIDAlinea", code_budget_post, r
                if partida:
                    total+=1
                    sql = '''
                    INSERT INTO account_move_line (
                    move_id,name,account_id,debit,credit,journal_id,period_id,date,state,company_id,currency_id,migrado,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,is_start,num_comp) VALUES (%s, '%s',%s,%s,%s,%s,%s,'%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''%(move_id,name,cuenta_id,debe,haber,journal_id,period_id,date,state_aux,company_aux,currency_aux,True,budget_cert_line_id,b_id,p_id,budget_accrued,budget_paid,False,aux_move_name)
                    cr.execute(sql)
                else:
                    total+=1
                    sql = '''
                    INSERT INTO account_move_line (
                    move_id,name,account_id,debit,credit,journal_id,period_id,date,state,company_id,currency_id,migrado,is_start,num_comp) VALUES (%s, '%s',%s,%s,%s,%s,%s,'%s','%s',%s,%s,%s,%s,%s)'''%(move_id,name,cuenta_id,debe,haber,journal_id,period_id,date,state_aux,company_aux,currency_aux,True,False,aux_move_name)
                    cr.execute(sql)
        print "TOTAL LINEAS", total
#        self.updateAll(cr, uid, [])
        return True    

    def load_asiento_detalle_sigame_aux(self, cr, uid, ids, context=None):
        a = False
        import pdb
        pdb.set_trace()
        if a:
            self.load_asiento_detalle_sigame_concp
        else:
            self.load_asiento_detalle_sigame_sincp
        

    def procesoCertificado(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        certificate_ids = certificate_obj.search(cr, uid, [('migrado','=',True),('state','=','draft')])
        for certificate_id in certificate_ids:
            certificate_obj.action_request(cr, uid, [certificate_id])
            certificate_obj.action_certified(cr, uid, [certificate_id])
            certificate_obj.action_commited(cr, uid, [certificate_id])
        return True

    def loadCertificateLine(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        item_obj = self.pool.get('budget.item')
        project_obj = self.pool.get('project.project')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                aux_cert_id = ustr(sh.cell(r,1).value)
                aux_post_id = str(sh.cell(r,3).value).replace('.','')#[0:6]
                aux_project = str(sh.cell(r,2).value).replace('.','')#+'1'
                post_ids = post_obj.search(cr, uid, [('code','=',aux_post_id)],limit=1)
                if not post_ids:
                    continue #OJO CON ESTO validar
                    print "NO PARTIDA", aux_post_id
                    continue
                project_ids = project_obj.search(cr, uid, [('code','=',aux_project)],limit=1)
                if not project_ids:
                    print "NO PROHECTO", aux_project
                proyecto = project_obj.browse(cr, uid, project_ids[0])
                task_id = proyecto.tasks[0].id
                aux_amount = str(sh.cell(r,8).value)
                certificate_ids = certificate_obj.search(cr, uid, [('name','=',aux_cert_id)],limit=1)
                if not certificate_ids:
                    print "NO CERTIFICADO", aux_cert_id
                budget_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('project_id','=',proyecto.id)])
                if not budget_ids:
                    print "NO BUDGET ITEM", aux_post_id
                    print "NO PROYECTO",proyecto.program_id.sequence
                    continue
                certificate_line_obj.create(cr, uid, {
                    'certificate_id':certificate_ids[0],
                    'migrado':'True',
                    'project_id':project_ids[0],
                    'task_id':task_id,
                    'budget_id':budget_ids[0],
                    'amount':aux_amount,
                    'amount_certified':aux_amount,
                    'amount_commited':aux_amount,
                    'amount_paid':aux_amount,
                    'state':'commited',
                })
        return True

    def loadReforma(self, cr, uid, ids, context=None):
        reform_obj = self.pool.get('budget.reform')
        item_obj = self.pool.get('budget.item')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                item_code = ustr(sh.cell(r,0).value)
                cantidad = sh.cell(r,1).value
                transaccion = 'ampliacion'
                if cantidad < 0:
                    cantidad = cantidad * (-1)
                    transaccion = 'disminucion'
                budget_item_ids = item_obj.search(cr, uid, [('code','=',item_code)])
                if budget_item_ids:
                    item = item_obj.browse(cr, uid, budget_item_ids[0])
                    reform_id = reform_obj.create(cr, uid, {
                        'project_id': item.project_id.id,
                        'task_id': item.task_id.id,
                        'budget_id': item.id,
                        'amount': cantidad,
                        'type_transaction': transaccion,
                        'justification': "Reforma migrada.",
                        'state': 'done',
                        'date_done':'30/06/2015',
                    })
        return True
    
    def loadCertificate(self, cr, uid, ids, context=None):
        certificate_obj = self.pool.get('budget.certificate')
        dept_obj = self.pool.get('hr.department')
        emp_obj = self.pool.get('hr.employee')
        partner_obj = self.pool.get('res.partner')
        project_obj = self.pool.get('project.project')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                if ustr(sh.cell(r,1).value)=='NULL':
                    continue
                aux_name = ustr(sh.cell(r,0).value)
                date_aux_1 = str(sh.cell(r,1).value)[0:10]
                partner_name_aux = ustr(sh.cell(r,2).value)
                desc_aux = ustr(sh.cell(r,3).value)
                partner_aux = ustr(sh.cell(r,5).value)
                department_ids = dept_obj.search(cr, uid, [],limit=1)
                employee_ids = emp_obj.search(cr, uid, [],limit=1)
                project_ids = project_obj.search(cr, uid, [('type_budget','=','gasto')],limit=1)
                ##partner
                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',partner_aux)])
                aux_persona = '6'
                if partner_ids:
                    partner_id = partner_ids[0]
                else:
                    partner_id = 1
#                    print "No partner", partner_aux
#                    aux_tipo = 'cedula'
#                    if len(partner_aux)>10:
#                        aux_tipo = 'ruc'
#                    partner_id = partner_obj.create(cr, uid, {
#                        'ced_ruc':partner_aux,
#                        'type_ced_ruc':aux_tipo,
#                        'tipo_persona':aux_persona,
#                        'name':partner_name_aux,
#                        'direccion':partner_name_aux,
#                        'telefono':'2222222',
#                        'property_account_receivable':1689,
#                        'property_account_payable':2823,
#                        'property_account_position':2,
#                    })
                cert_id = certificate_obj.create(cr, uid, {
                    'name':aux_name,
                    'number':aux_name,
                    'user_id':1,
                    'department_id':department_ids[0],
                    'solicitant_id':employee_ids[0],
                    'project_id':project_ids[0],
                    'date':date_aux_1,
                    'date_confirmed':date_aux_1,
                    'date_commited':date_aux_1,
                    'notes':desc_aux,
                    'partner_id':partner_id,
                    'migrado':True,
                    'state':'commited',
#                    'amount_total':,
#                    'amount_certified':,
#                    'amount_commited':,
                })

    def writeAccount(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        account_ids = account_obj.search(cr, uid, [])
        account_obj.write(cr, uid, account_ids,{
            'note':'EMPALME',
        })
        account_obj._parent_store_compute(cr)
        return True

    def parentAccount(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        type_obj = self.pool.get('account.account.type')
        data = self.read(cr, uid, ids)[0]
        #if len de code quitado puntos es mayor a 3 quito dos y busco el papa, else quito 1
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            s = 0
            for r in range(sh.nrows)[1:]:  
                print "RRRRRRRRRRRRRRRRRR", r
                aux_code = ustr(sh.cell(r,0).value)
                aux_code_punto = aux_code.replace(".",'')
#                account_ids = account_obj.search(cr, uid, [('code','=',aux_code_punto)],limit=1)
                sql1 =  "select id from account_account where code='%s'" % (aux_code_punto)
                print "SQL", sql1
                cr.execute(sql1)
                ids_sql = cr.fetchone()
                if ids_sql:
                    id_account = ids_sql[0]
                    if len(aux_code_punto)>3:
                        aux_indice = int(len(aux_code_punto)-2)
                        aux_parent_code = aux_code_punto[0:aux_indice]
                        cr.execute("select id from account_account where code='%s'"%(aux_parent_code))
                        ids_parent = cr.fetchone()
                        #parent_ids = account_obj.search(cr, uid, [('code','=',aux_parent_code)],limit=1)
                        if ids_parent:#parent_ids:
                            cr.execute("update account_account set parent_id=%s where id=%s"%(ids_parent[0],id_account))
                            #account_obj.write(cr, uid, account_ids[0],{
                            #    'parent_id':parent_ids[0],
                             #   })
                        else:
                            print "NO PAPA", aux_code
                    else:
                        aux_indice = int(len(aux_code_punto)-1)
                        aux_parent_code = aux_code_punto[0:aux_indice]
                        cr.execute("select id from account_account where code='%s'"%(aux_parent_code))
                        ids_parent = cr.fetchone()
                        #parent_ids = account_obj.search(cr, uid, [('code','=',aux_parent_code)],limit=1)
                        if ids_parent:#parent_ids:
                            cr.execute("update account_account set parent_id=%s where id=%s"%(ids_parent[0],id_account))
                else:
                    s +=1
                    type_ids = type_obj.search(cr, uid, [])
                    print "NO CUENTA EN MIGRADO", s 
                    aux_name = ustr(sh.cell(r,2).value)
                    account_id = account_obj.create(cr, uid, {
                        'code':aux_code,
                        'name':aux_name,
                        'type':'other',
                        'user_type':type_ids[0],
                        'code_aux':aux_code_punto,
                    })
                    aux_code_punto = aux_code.replace(".",'')
                    if len(aux_code_punto)>3:
                        aux_indice = int(len(aux_code_punto)-2)
                        aux_parent_code = aux_code_punto[0:aux_indice]
                        parent_ids = account_obj.search(cr, uid, [('code','=',aux_parent_code)],limit=1)
                        if parent_ids:
                            account_obj.write(cr, uid, account_id,{
                                'parent_id':parent_ids[0],
                            })
                        else:
                            print "NO PAPA", aux_code
        return True

    def cuentaCxp(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        budget_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        cxp_lista = []
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            sigame = olimpo = False
            if data['tipo_sistema']=='olympo':
                olimpo = True
            else:
                sigame = True
            if olimpo:
                for r in range(sh.nrows)[1:]:  
                    aux_code = str(sh.cell(r,0).value)
                    aux_init = aux_code[0:1]
                    aux_init_gasto = aux_code[0:3].replace(".",'')
                    aux_budget = str(sh.cell(r,2).value)[0:7].replace(".",'')
                    budget_ids = budget_obj.search(cr, uid, [('code','=',aux_budget)])
                    if budget_ids:
                        #preguntar si es patrimonial colocar la cxp o cxc else solo la partida
                        if aux_init in ('6') or aux_init_gasto not in ('11','21'): #2
                            #atarle a la patrimonial
                            budget = budget_obj.browse(cr, uid, budget_ids[0])
                            if not aux_budget in cxp_lista:
                                patrimonial_ids = account_obj.search(cr, uid, [('budget_id','=',budget_ids[0])])
                                if patrimonial_ids:
                                    for patrimonial_id in patrimonial_ids:
                                        patrimonial = account_obj.browse(cr, uid, patrimonial_id)
                                        if patrimonial.code[0:2] not in ('11','21'):
                                            #aqui sacar la cxp
                                            account_ids = account_obj.search(cr, uid, [('budget_id','=',budget_ids[0])],limit=1)
                                            if account_ids[0]==patrimonial_id:
                                                account_ids = account_obj.search(cr, uid, [('budget_id','=',budget_ids[0])])                            
                                                for account_id in account_ids:
                                                    if account_id!=patrimonial_id:
                                                        account_aux = account_obj.browse(cr, uid, account_id)
                                                        if account_aux.code[0:2] in ('11','21'):
                                                            account_id_cxp = account_aux.id
                                                            account_obj.write(cr, uid, patrimonial_id,{
                                                                'account_rec_id':account_id_cxp,
                                                            })

                                            else:
                                                account_aux = account_obj.browse(cr, uid, account_ids[0])
                                                if account_aux.code[0:2] in ('11','21'):
                                                    account_id_cxp = account_aux.id
                                                    account_obj.write(cr, uid, patrimonial_id,{
                                                        'account_rec_id':account_id_cxp,
                                                    })
                                                else:
                                                    print "No cxp por el else"
                                            cxp_lista.append(aux_budget)
                                else:
                                    print "no partida cta", aux_code, aux_budget
            if sigame:
                for r in range(sh.nrows)[1:]:
                    aux_code = str(sh.cell(r,0).value)
                    account_id_cxp=0
                    aux_init = aux_code[0:1]
                    aux_init_gasto = aux_code[0:3].replace(".",'')
                    aux_budget = str(sh.cell(r,1).value)[0:9].replace(".",'')
                    budget_ids = budget_obj.search(cr, uid, [('code','=',aux_budget)])
                    if budget_ids:
                        #preguntar si es patrimonial colocar la cxp o cxc else solo la partida
                        if aux_init in ('6','1') or aux_init_gasto not in ('11','21'): #2
                            #atarle a la patrimonial
                            if not aux_budget in cxp_lista:
                                patrimonial_ids = account_obj.search(cr, uid, [('budget_id','=',budget_ids[0])])
                                if patrimonial_ids:
                                    for patrimonial_id in patrimonial_ids:
                                        patrimonial = account_obj.browse(cr, uid, patrimonial_id)
                                        if patrimonial.code[0:2] not in ('11','21'):
                                            #aqui sacar la cxp
                                            account_ids = account_obj.search(cr, uid, [('budget_id','=',budget_ids[0])],limit=1)
                                            if account_ids[0]==patrimonial_id:
                                                account_ids = account_obj.search(cr, uid, [('budget_id','=',budget_ids[0])])                            
                                                for account_id in account_ids:
                                                    if account_id!=patrimonial_id:
                                                        account_aux = account_obj.browse(cr, uid, account_id)
                                                        if account_aux.code[0:2] in ('11','21'):
                                                            account_id_cxp = account_aux.id
                                            else:
                                                account_aux = account_obj.browse(cr, uid, account_ids[0])
                                                if account_aux.code[0:2] in ('11','21'):
                                                    account_id_cxp = account_aux.id
                                            if account_id_cxp!=0:
                                                account_obj.write(cr, uid, patrimonial_id,{
                                                    'account_rec_id':account_id_cxp,
                                                })
                                            else:
                                                print aux_code
                                            cxp_lista.append(aux_budget)
        return True

    def cxpOlympo(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['type_olympo']=='ingreso':
                for r in range(sh.nrows)[1:]:
                    if len(str(sh.cell(r,4).value))>4:
                        aux_code_gasto = str(sh.cell(r,4).value).replace(".",'')
                        account_gasto_ids = account_obj.search(cr, uid, [('code','=',aux_code_gasto)],limit=1)
                        if account_gasto_ids:
                            account = account_obj.browse(cr, uid, account_gasto_ids[0])
                            if account.account_rec_id:
                                continue
                            aux_code_cxp = str(sh.cell(r,2).value).replace(".",'')
                            account_cxp_ids = account_obj.search(cr, uid, [('code','=',aux_code_cxp)],limit=1)
                            if account_cxp_ids:
                                account_obj.write(cr, uid, account_gasto_ids[0],{
                                    'account_rec_id':account_cxp_ids[0],
                                })
                    elif len(str(sh.cell(r,20).value))>4:
                        aux_code_inv = str(sh.cell(r,20).value).replace(".",'')
                        account_inv_ids = account_obj.search(cr, uid, [('code','=',aux_code_inv)],limit=1)
                        if account_inv_ids:
                            account = account_obj.browse(cr, uid, account_inv_ids[0])
                            if account.account_rec_id:
                                continue
                            aux_code_cxp = str(sh.cell(r,18).value).replace(".",'')
                            account_cxp_ids = account_obj.search(cr, uid, [('code','=',aux_code_cxp)],limit=1)
                            if account_cxp_ids:
                                account_obj.write(cr, uid, account_inv_ids[0],{
                                    'account_rec_id':account_cxp_ids[0],
                                })
        
        return True

    def partidaCuenta(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        budget_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        account_list = []
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            olimpo = sigame = False
            if data['tipo_sistema']=='olympo':
                olimpo = True
            else:
                sigame = True
            if olimpo:
                for r in range(sh.nrows)[1:]:                    
                    aux_code = str(sh.cell(r,0).value).replace(".",'')
                    account_ids = account_obj.search(cr, uid, [('code','=',aux_code)],limit=1)
                    aux_budget = str(sh.cell(r,2).value)[0:7].replace(".",'')
                    budget_ids = budget_obj.search(cr, uid, [('code','=',aux_budget)])
                    if account_ids:
                        if budget_ids:
                            if not account_ids[0] in account_list:
                                account_hijas_ids = account_obj.search(cr, uid, [('parent_id','=',account_ids[0])])
                                if account_hijas_ids:
                                    account_obj.write(cr, uid, account_hijas_ids,{
                                        'budget_id':budget_ids[0],
                                    })
                                account_obj.write(cr, uid, account_ids[0],{
                                    'budget_id':budget_ids[0],
                                })
                            account_list.append(account_ids[0])
                        else:
                            print "NO PARTIDA", aux_budget
                    else:
                        print "NO CTA", aux_code
            if sigame:
                for r in range(sh.nrows)[1:]:
                    aux_code = str(sh.cell(r,0).value)
                    aux_init = aux_code[0:1]
                    account_ids = account_obj.search(cr, uid, [('code_aux','=',aux_code)],limit=1)
                    #hasta el amperstand
                    l = str(sh.cell(r,1).value).find('&')
                    aux_budget = str(sh.cell(r,1).value)[0:l].replace(".",'')
                    budget_ids = budget_obj.search(cr, uid, [('code','=',aux_budget)])
                    if account_ids:
                        if budget_ids:
                            if not account_ids[0] in account_list:
                                account_obj.write(cr, uid, account_ids[0],{
                                    'budget_id':budget_ids[0],
                                })
                            account_list.append(account_ids[0])
                        else:
                            print "NO PARTIDA", aux_budget
                    else:
                        print aux_code
        return True

######################SIGAME


    def computeStd(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        k_obj = self.pool.get('aux.cardex')
        product_ids = product_obj.search(cr, uid, [('qty_available','>',0)])
        for product_id in product_ids:
            product = product_obj.browse(cr, uid, product_ids[0])
            qty_available = product.qty_available
            move_ids = k_obj.search(cr, uid, [('name','=',product_id),('tipo_move','=','i')])
            if len(move_ids)==1:
                move1 = k_obj.browse(cr, uid, move_ids[0])
                aux_std = move1.pu
            elif len(move_ids)>1:
                move1 = k_obj.browse(cr, uid, move_ids[0])
                move2 = k_obj.browse(cr, uid, move_ids[1])
                if move1.qty>=qty_available:
                    aux_std = move1.pu
                else:
                    aux_qty = move1.qty + move2.qty
                    total = move1.total + move2.total
                    aux_std = total/aux_qty
            else:
                aux_std = 1
            product_obj.write(cr, uid, product_id,{
                'standard_price':aux_std,
            })

    def loadKdx(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        k_obj = self.pool.get('aux.cardex')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                product_ids = product_obj.search(cr, uid, [('default_code','=',ustr(sh.cell(r,1).value))],limit=1)
                if product_ids:
                    product_id = product_ids[0]
                else:
                    print "NO PRODUCTO"
                if sh.cell(r,5).value>0:
                    tipo_aux = 'i'
                    qty_aux = sh.cell(r,5).value
                    pu_aux = sh.cell(r,6).value
                    tot_aux =sh.cell(r,7).value
                else:
                    tipo_aux = 'e'
                    qty_aux = sh.cell(r,8).value
                    pu_aux = sh.cell(r,9).value
                    tot_aux =sh.cell(r,10).value
                k_id = k_obj.create(cr, uid, {
                    'code':ustr(sh.cell(r,1).value),
                    'name':product_id,
                    'tipo_move':tipo_aux,
                    'qty':qty_aux,
                    'pu':pu_aux,
                    'total':tot_aux,
                    'seq':int(sh.cell(r,2).value),
                })
        return True

    def mayusculasUsr(self,cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        user_ids = user_obj.search(cr, uid, [])
        for user_id in user_ids:
            user = user_obj.browse(cr, uid, user_id)
            login_ant = user.login
            new_login = login_ant.upper()
            user_obj.write(cr, uid, user_id,{
                'login':new_login,
            })
        return True

    def updateRUC(self,cr, uid, ids, context=None):
        part_obj = self.pool.get('res.partner')
        part_obj.write(cr, uid, 1, {
            'ced_ruc':'0968532700001',
        })
        return True

    def updateActivoMarca(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                aux_cod = ustr(sh.cell(r,1).value)
                asset_ids = asset_obj.search(cr, uid, [('code','=',aux_cod)])
                if asset_ids:
                    asset_obj.write(cr, uid, asset_ids[0],{
                        'marca':ustr(sh.cell(r,2).value),
                        'modelo':ustr(sh.cell(r,3).value),
                        'color':ustr(sh.cell(r,5).value),
                    })
                else:
                    print "NO ACTIVO ===", sh.cell(r,1).value
        return True

    def updateRec(self, cr, uid, ids, context=None):
        rec_obj = self.pool.get('account.recaudacion')
        rec_ids = rec_obj.search(cr, uid, [])
        j = 0
        for rec_id in rec_ids:
            j += 1
            rec_obj.cargar_recaudado(cr, uid, [rec_id],context=context)
            rec_obj.contabilizar_recaudado(cr, uid, [rec_id],context=context)
            rec_date = rec_obj.read(cr, uid,rec_id,['date'])
            print rec_id, rec_date['date']
        return True
        
    def updateRol(self, cr, uid, ids, context=None):
        rol_obj = self.pool.get('hr.payslip')
        rol_ids = rol_obj.search(cr, uid, [])
        j = 0
        for rol_id in rol_ids:
            j += 1
            rol_obj.compute_sheet(cr, uid, [rol_id],context=context)
            print "HECHO", j
        return True

    def updateAccAnticipo(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                aux_ced = ustr(sh.cell(r,0).value)
                aux_cc = ustr(sh.cell(r,1).value)
                p_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced)])
                if p_ids:
                    account_ids = account_obj.search(cr, uid, [('code','=',aux_cc)],limit=1)
                    if account_ids:
                        partner_obj.write(cr, uid, p_ids[0],{
                            'anticipo_id':account_ids[0],
                        })
                    else:
                        print "NO ACc ===", aux_cc
                else:
                    print "No PART", aux_ced
        return True

    def updateDepreciation(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                if len(ustr(sh.cell(r,1).value))>5:
                    aux_cod = ustr(sh.cell(r,1).value)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_cod)])
                    if asset_ids:
                        asset = asset_obj.browse(cr, uid, asset_ids[0])
                        asset_obj.write(cr, uid, asset.id,{
                            'depreciacion':float(sh.cell(r,7).value),
                        })
                    else:
                        print "NO ACTIVO ===", sh.cell(r,1).value
        return True

    def updateRunId(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.payslip.line')
        line_ids = line_obj.search(cr, uid, [])
        for line_id in line_ids:
            line = line_obj.browse(cr, uid, line_id)
            line_obj.write(cr, uid, line_id,{
                'run_id':line.slip_id.payslip_run_id.id,
            })
        return True

    def updateBudgetContract(self, cr, uid, ids, context=None):
        rol_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        employee_obj = self.pool.get('hr.employee')
        item_obj = self.pool.get('budget.item')
        post_obj = self.pool.get('budget.post')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            k = m = p= q = s =0
            for r in range(sh.nrows)[1:]:  
                if len(ustr(sh.cell(r,2).value))>5:
                    aux_ced = ustr(sh.cell(r,1).value)
                    empleado_ids = employee_obj.search(cr, uid, [('name','=',aux_ced)],limit=1)
                    if empleado_ids:
                        empleado = employee_obj.browse(cr, uid, empleado_ids[0])
                        contract_ids = contract_obj.search(cr, uid, [('employee_id','=',empleado_ids[0])])
                        if contract_ids:
                            #update el contrato con la partida e imprimir el numero de rol
                            contrato = contract_obj.browse(cr, uid, contract_ids[0])
                            rol_ids = rol_obj.search(cr, uid, [('contract_id','=',contract_ids[0])])
                            if rol_ids:
                                rol_obj.write(cr, uid, rol_ids[0],{
                                    'rev':True,
                                })
                                rol = rol_obj.browse(cr, uid, rol_ids[0])
                                m += 1
                                aux_post = ustr(sh.cell(r,2).value)
                                aux_post1 = aux_post[0:6]
                                post_ids = post_obj.search(cr, uid, [('code','=',aux_post1)],limit=1)
                                if post_ids:
                                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),('program_id','=',contrato.program_id.id)],limit=1)
                                    if item_ids:
                                        p += 1
                                        contract_obj.write(cr, uid, contrato.id,{
                                            'budget_id':item_ids[0],
                                        })
                                    else:
                                        #cambia el programa en el contrato OJO
                                        q += 1
#                                        print "NO OARTIDA EN PROGRAMA DE CONTRATO", contrato.employee_id.complete_name
                                else:
                                    print "NO PARTIDA POST"#, aux_post1
                            else:
                                print "NO ROL DE PAGOS"#, contrato.employee_id.complete_name
                        else:
                            print "NO CONTRATO DE "#, empleado.complete_name
                    else:
                        k += 1
                        print "NO EMPLEADO"#, ustr(sh.cell(r,1).value), r
#        print "KKKKKKKKKKKKKKKKKKKKKKKKKK", k
#        print "TOTAL ROLES", m
#        print "CONTRATOS UDATEDEE", p
#        print "NO PROGRAMA PARTIDA REVISAR", q
#        print "NO ROLES", r
        return True

    def updatePrograma(self, cr, uid, ids, context=None):
        item_obj = self.pool.get('budget.item')
        item_ids = item_obj.search(cr, uid, [])
        for item_id in item_ids:
            item = item_obj.browse(cr, uid, item_id)
            item_obj.write(cr, uid, item_id,{
                'program_id':item.project_id.program_id.id,
            })
        return True

    def updateBajas(self, cr, uid, ids, context=None):
        activo_obj = self.pool.get('account.asset.asset')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                if len(str(sh.cell(r,15).value))>1:
                    aux_code = ustr(sh.cell(r,15).value)
                    activo_ids = activo_obj.search(cr, uid, [('code','ilike',aux_code)],limit=1)
                    if activo_ids:
                        activo = activo_obj.browse(cr, uid, activo_ids[0])
                        if activo.state=='close':
                            date_aux = str(sh.cell(r,17).value)
                            activo_obj.write(cr, uid, activo_ids[0],{
                                'baja_date':date_aux,
                            })
                    else:
                        print "NO HAY EL ACTIVO", aux_code
        return True

    def relatedBudget(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('account.move.line')
        cert_line = self.pool.get('budget.certificate.line')
        line_ids = line_obj.search(cr, uid, [])
        for line in line_ids:
            line = line_obj.browse(cr, uid, line)
            if line.budget_id_cert:
                cert = cert_line.browse(cr, uid, line.budget_id_cert.id)
                line_obj.write(cr, uid, line.id, {
                    'budget_id':cert.budget_id.id,
                    'budget_post':cert.budget_id.budget_post_id.id,
                })
        cert_ids = cert_line.search(cr, uid, [])
        for cert_id in cert_ids:
            cert = cert_line.browse(cr, uid, cert_id)
            cert_line.write(cr, uid, cert_id,{
                'budget_post':cert.budget_id.budget_post_id.id,
            })

    def loadResBank(self,cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        b_obj = self.pool.get('res.bank')
        data = self.read(cr, uid, ids)[0]
        num = 0
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                aux_ced_ruc = str(sh.cell(r,0).value)
                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                if partner_ids:
                    if len(partner_ids)>1:
                        raise osv.except_osv(('Partner duplicado!'),'Partner con cedula/ruc'%(str(sh.cell(r,0).value)))
                    else:
                        partner_id = partner_ids[0]
                else:
                    print "No partner", aux_ced_ruc
                    aux_tipo = 'cedula'
                    aux_persona = '6'
                    if len(aux_ced_ruc)>10:
                        aux_tipo = 'ruc'
                    partner_id = partner_obj.create(cr, uid, {
                        'ced_ruc':aux_ced_ruc,
                        'type_ced_ruc':aux_tipo,
                        'tipo_persona':aux_persona,
                        'name':ustr(sh.cell(r,1).value),
                        'direccion':ustr(sh.cell(r,1).value),
                        'telefono':'2222222',
                        'property_account_receivable':1689,
                        'property_account_payable':2823,
                        'property_account_position':2,
                    })
                num_banco = str(sh.cell(r,2).value)
                bank_ids = b_obj.search(cr, uid, [('bic','=',num_banco)])
                if not bank_ids:
                    print "NO HAY BANCO", num_banco
                else:
                    tipo_c = str(sh.cell(r,4).value)
                    if tipo_c=='CORRIENTE':
                        tipo_c_aux = 'cte'
                    else:
                        tipo_c_aux = 'aho'
                    cuenta_ids = bank_obj.search(cr, uid, [('partner_id','=',partner_id),('bank','=',bank_ids[0]),('type_cta','=',tipo_c_aux),('acc_number','=',str(sh.cell(r,3).value))])
                    if not cuenta_ids:
                        bank_obj.create(cr, uid, {
                            'partner_id':partner_id,
                            'bank':bank_ids[0],
                            'type_cta':tipo_c_aux,
                            'acc_number':str(sh.cell(r,3).value),
                        })
                        num += 1
                        print "cuenta creada"
                    else:
                        print "no se crea cuenta"
        print num, " cuentas creadas"
        return True
            
    def updatePartner(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        b_obj = self.pool.get('res.bank')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]: 
                if data['municipio'] == 'emp':
                    print "EMPLAME"
                    if len(str(sh.cell(r,0).value))>1:
                        aux_ced_ruc = str(sh.cell(r,0).value)
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                        if len(partner_ids)<1:
                            if len(aux_ced_ruc)<13:
                                aux_ced_ruc = aux_ced_ruc + '001' 
                            partner_id = partner_obj.create(cr, uid, {
                                'ced_ruc':aux_ced_ruc,
                                'type_ced_ruc':'ruc',
                                'tipo_persona':'9',
                                'name':ustr(sh.cell(r,6).value),
                                'telefono':str(sh.cell(r,4).value),
                                'direccion':ustr(sh.cell(r,3).value),
                                #    'property_account_receivable':'1689',
                                #    'property_account_payable':'2823',
                                #    'property_account_position':'2',
                            })
                else:
                    if len(str(sh.cell(r,9).value))>1:
                        aux_ced_ruc = str(sh.cell(r,1).value)
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)])
                        if len(partner_ids)<1:
                            partner_id = partner_obj.create(cr, uid, {
                                'ced_ruc':aux_ced_ruc,
                                'type_ced_ruc':'pasaporte',
                                'tipo_persona':'6',
                                'name':ustr(sh.cell(r,6).value),
                                'telefono':str(sh.cell(r,4).value),
                                'direccion':ustr(sh.cell(r,3).value),
                                #    'property_account_receivable':'1689',
                                #    'property_account_payable':'2823',
                                #    'property_account_position':'2',
                            })
                        num_banco = str(sh.cell(r,12).value)
                        bank_ids = b_obj.search(cr, uid, [('bic','=',num_banco)])
                        if len(bank_ids)<1:
                            print "NO HAY BANCOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",str(sh.cell(r,11).value), num_banco
                            tipo_c = str(sh.cell(r,10).value)
                            if tipo_c=='CORRIENTE':
                                tipo_c_aux = 'cte'
                            else:
                                tipo_c_aux = 'aho'
                                bank_obj.create(cr, uid, {
                                    'partner_id':partner_id,
                                    'bank':bank_ids[0],
                                    'type_cta':tipo_c_aux,
                                    'acc_number':str(sh.cell(r,9).value),
                                })
                    else:
                        if len(ustr(sh.cell(r,11).value))>1:
                            tipo_c = str(sh.cell(r,10).value)
                            if tipo_c=='CORRIENTE':
                                tipo_c_aux = 'cte'
                            else:
                                tipo_c_aux = 'aho'
                                num_banco = str(sh.cell(r,12).value)
                                bank_ids = b_obj.search(cr, uid, [('bic','=',num_banco)])
                                if len(bank_ids)<1:
                                    print "NO HAY BANCOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",str(sh.cell(r,11).value), num_banco
                                    bank_obj.create(cr, uid, {
                                        'partner_id':partner_ids[0],
                                        'bank':bank_ids[0],
                                        'type_cta':tipo_c_aux,
                                        'acc_number':str(sh.cell(r,9).value),
                                    })
        return True

    def projectExec(self, cr, uid, ids, context=None):
        project_obj = self.pool.get('project.project')
        project_ids = project_obj.search(cr, uid, [])
        wf_service = netsvc.LocalService("workflow")
        for project_id in project_ids:
            wf_service.trg_validate(uid, 'project.project', project_id, 'signal_planning', cr)
            
    def projectExec2(self, cr, uid, ids, context=None):
        project_obj = self.pool.get('project.project')
        project_ids = project_obj.search(cr, uid, [])
        wf_service = netsvc.LocalService("workflow")
        for project_id in project_ids:
            wf_service.trg_validate(uid, 'project.project', project_id, 'signal_execution', cr)

    def quitarDuplicado(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        line_obj = self.pool.get('account.asset.depreciation.line')
        transfer_obj = self.pool.get('account.asset.transfer')
        asset_ids = asset_obj.search(cr, uid, [])
        asset_duplicado = []
        j = 0
        for asset_id in asset_ids:
            asset = asset_obj.browse(cr, uid, asset_id)
            code_aux = asset.code
            asset_ids_aux = asset_obj.search(cr, uid, [('code','=',code_aux)])
            if len(asset_ids_aux)>1:
                j += 1
                #bbuscar si hay transfer pone el otro
                transfer_ids = transfer_obj.search(cr, uid, [('asset_id','=',asset_ids_aux[1])])
                if transfer_ids:
                    asset_duplicado.append(asset_ids_aux[0])
                else:
                    asset_duplicado.append(asset_ids_aux[1])
                print "ESTE ES DUPLICADO", asset.code, asset.id, asset.state
        print "DUPLIVCADOS", asset_duplicado
        print "TOTAL DUPLICADOS", j
        for duplicado_id in asset_duplicado:
            line_ids = line_obj.search(cr, uid, [('asset_id','=',duplicado_id)])
            line_obj.unlink(cr, uid, line_ids)
            asset_obj.unlink(cr, uid, duplicado_id)
        return True
        
    def loadCustodioActivosSigame(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        employee_obj = self.pool.get('hr.employee')
        job_obj = self.pool.get('hr.job')
        department_obj = self.pool.get('hr.department')
        job_ids = job_obj.search(cr, uid, [])
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            department_ids = department_obj.search(cr, uid, [])
            department_id = department_ids[0]
            if data['tipo_sistema'] == 'sigame':
                for r in range(sh.nrows)[1:]:
                    aux_code_activo = ustr(sh.cell(r,1).value) + '.' + ustr(sh.cell(r,2).value)
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                    if asset_ids:
                        aux_asignado = ustr(sh.cell(r,7).value)
                        if aux_asignado=='N':
                            aux_ced = ustr(sh.cell(r,5).value)
                        else:
                            aux_ced = ustr(sh.cell(r,9).value)
                        employee_ids = employee_obj.search(cr, uid, [('name','=',aux_ced)],limit=1)
                        if employee_ids:
                            employee_id = employee_ids[0]
                        else:
                            if aux_ced in ('0','bodega'):
                                employee_ids = employee_obj.search(cr, uid, [('name','=','1234567890')],limit=1)
                                if employee_ids:
                                    employee_id = employee_ids[0]
                                else:
                                    "OJOOOOO falta crear el aux de act fijo empleado con CI 1234567890"
                            else:
                                print "NO EMPLEADO=================", aux_ced
                                employee_id = employee_obj.create(cr, uid, {
                                    'name':aux_ced,
                                    'id_type':'p',
                                    'employee_first_lastname':'Nombre',
                                    'employee_first_name':'Apellido',
                                    'department_id':department_id,
                                    'job_id':job_ids[0],
                                    'address':'AUX',
                                    'house_phone':'000000',
                                })
                        empleado = employee_obj.browse(cr, uid, employee_id)
                        asset_obj.write(cr, uid, asset_ids[0],{
                            'department_id':empleado.department_id.id,
                            'employee_id':empleado.id,
                        })
                        aux_texto = empleado.name + ' - ' + 'Migrado Custodio'
                        move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, 
                                                                               {'type':'transferencia',
                                                                                'cause':aux_texto,
                                                                                'name':aux_code_activo}, context=None)
                        self.pool.get('gt.account.asset.moves.relation').create(cr, uid, 
                                                                                {'asset_id': asset_ids[0],
                                                                                 'move_id':move_id,
                                                                                 'date_create':sh.cell(r,6).value,}, context=None)
                    else:
                        print "NO ACTIVO-------------", aux_code_activo
        return True

    def updateDepreciacionOlympo(self, cr, uid, ids, context=None):
        log_obj = self.pool.get('log.deprecia')
        asset_obj = self.pool.get('account.asset.asset')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                aux_t = ustr(sh.cell(r,0).value).zfill(3)
                aux_st = ustr(sh.cell(r,1).value).zfill(3)
                aux_cl = ustr(sh.cell(r,2).value).zfill(3)
                aux_code_activo = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,3).value).zfill(4)
                asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code_activo)])
                anio = str(sh.cell(r,5).value) + '-' + '12' + '-' + '31' 
                aux_valor = float(str(sh.cell(r,9).value).replace(',','.'))
                if asset_ids:
                    log_obj.create(cr, uid, {
                        'asset_id':asset_ids[0],
                        'date':anio,
                        'desc':'Migrado',
                        'valor':aux_valor,
                    })
                    asset = asset_obj.browse(cr, uid, asset_ids[0])
                    dep_ant = asset.depreciacion
                    new = dep_ant + aux_valor
                    asset_obj.write(cr, uid, [asset.id],{
                        'depreciacion':new,
                    })
                else:
                    print "NO ACTIVO", aux_code_activo
        return True

    def loadActivoOlympo(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        categ_obj = self.pool.get('account.asset.category')
        subcateg_obj = self.pool.get('asset.asset.subcateg')
        department_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        acc_obj = self.pool.get('account.account')
        tipotr_obj = self.pool.get('gt.account.asset.transaction')
        componente_obj = self.pool.get('gt.account.asset.componente')
        partner_obj = self.pool.get('res.partner')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                aux_tipoactivo = ustr(sh.cell(r,0).value)
                aux_categ = ustr(sh.cell(r,1).value)
                categ_ids = categ_obj.search(cr, uid, [('name','=',aux_categ)],limit=1)
                if not categ_ids:
                    raise osv.except_osv(('Error datos!'),'No cateoria %s'%(aux_categ))
                aux_vidautil = int(sh.cell(r,17).value)
                if aux_vidautil<=0:
                    categoria = categ_obj.browse(cr, uid, categ_ids[0])
                    aux_vidautil = categoria.method_number
                aux_t = ustr(sh.cell(r,2).value).zfill(3)
                aux_st = ustr(sh.cell(r,3).value).zfill(3)
                aux_cl = ustr(sh.cell(r,4).value).zfill(3)
                aux_subcateg = aux_t + aux_st + aux_cl
                subcateg_ids = subcateg_obj.search(cr, uid, [('code','=',aux_subcateg)],limit=1)
                if not subcateg_ids:
                    raise osv.except_osv(('Error datos!'),'No subcateoria %s'%(aux_subcateg))
                aux_code = aux_t + '.' + aux_st + '.' + aux_cl + '.' + ustr(sh.cell(r,5).value).zfill(4)
                aux_tipocompra = ustr(sh.cell(r,8).value)
                aux_estado = 'open'
                if aux_tipocompra=='BAJA':
                    aux_estado = 'close'
                tr_ids = tipotr_obj.search(cr, uid,[('name','=',aux_tipocompra)],limit=1)
                if not tr_ids:
                    print 'No tipo transaccion', aux_tipocompra
                #custodio
                aux_ced_ruc = ustr(sh.cell(r,40).value) #AO
                emp_ids = employee_obj.search(cr, uid, [('name','=',aux_ced_ruc)],limit=1)
                if emp_ids:
                    emp_id = emp_ids[0]
                else:
                    emp_ids = employee_obj.search(cr, uid, [('name','=','9999999')],limit=1)
                    emp_id = emp_ids[0]
                empleado = employee_obj.browse(cr, uid, emp_id)
                dept_id = empleado.department_id.id
                aux_estado1 = str(sh.cell(r,22).value) #celda W
                if aux_estado1=='BUENO':
                    aux_estado1 = 'Bueno'
                elif aux_estado1=='MALO':
                    aux_estado1 = 'Malo'
                else:
                    aux_estado1 = 'Regular'
                partner_id = 1
                aux_pv = str(sh.cell(r,13).value).replace(',','.') #O
                aux_salvaguarda = (float(aux_pv) * 0.10)
                aux_residual = float(aux_pv) - aux_salvaguarda
                aux_dp = str(sh.cell(r,13).value).replace(',','.') #
                aux_valor_actual = float(aux_pv) - float(aux_dp) 
#                aux_valor_actual = float(sh.cell(r,13).value) - float(sh.cell(r,63).value) 
                aux_note = ustr(sh.cell(r,11).value) + ' - ' + ustr(sh.cell(r,12).value) 
                activo_id = asset_obj.create(cr, uid, {
                    'code':aux_code,
                    'type':aux_tipoactivo,
                    'serial_number':sh.cell(r,28).value,
                    'subcateg_id':subcateg_ids[0],
                    'category_id':categ_ids[0],
                    'department_id':dept_id,
                    'name':sh.cell(r,11).value,
                    'purchase_value':aux_pv,
                    'depreciacion':0,
                    'valor_actual':aux_valor_actual,
                    'salvage_value':aux_salvaguarda,
                    'value_residual':aux_residual,
                    'purchase_date':str(sh.cell(r,10).value),
                    'employee_id':emp_id,
                    'state':aux_estado,
                    'condicion':aux_estado1,
                    'transaction_id':tr_ids[0],
                    'marca':sh.cell(r,26).value,
                    'modelo':sh.cell(r,27).value,
                    'color':sh.cell(r,24).value,
                    'otros_accesorios':ustr(sh.cell(r,12).value),
                    'note':aux_note,
                    'partner_id':partner_id,
                    'method_number':aux_vidautil,
                    })
                print "activo creado", activo_id
        return True

    def loadComponentes(self, cr, uid, ids, context=None):
        componente_obj = self.pool.get('gt.account.asset.componente')
        asset_obj = self.pool.get('account.asset.asset')
        employee_obj = self.pool.get('hr.employee')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['tipo_sistema'] == 'sigame':
                for r in range(sh.nrows)[1:]:
                    aux_cedula = ustr(sh.cell(r,0).value)
                    aux_activo = ustr(sh.cell(r,1).value)
                    emp_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)])
                    if emp_ids:
                        emp_id = emp_ids[0]
                    else:
                        print "NO EMPLEADO", aux_cedula
                        emp_id = 1
                    activo_ids = asset_obj.search(cr, uid, [('name','ilike',aux_activo),('category_id','=',5)])
                    aux_value = 'Vel. ' + ustr(sh.cell(r,6).value) + ' Cap. ' + ustr(sh.cell(r,7).value) + ' Mem. ' + ustr(sh.cell(r,8).value)   
                    if activo_ids:
                        componente_obj.create(cr, uid, {
                            'name':ustr(sh.cell(r,2).value),
                            'value': aux_value,
                            'cantidad':1,
                            'serie':ustr(sh.cell(r,3).value),
                            'marca':ustr(sh.cell(r,4).value),
                            'modelo':ustr(sh.cell(r,5).value),
                            'state':'Operativo',
                            'employee_id':emp_id,
                            'empleado':aux_cedula,
                            'activo':ustr(sh.cell(r,1).value),
                        })
                    else:
                        componente_obj.create(cr, uid, {
                            'name':ustr(sh.cell(r,2).value),
                            'value': aux_value,
                            'cantidad':1,
                            'serie':ustr(sh.cell(r,3).value),
                            'marca':ustr(sh.cell(r,4).value),
                            'modelo':ustr(sh.cell(r,5).value),
                            'state':'Operativo',
                            'employee_id':emp_id,
                            'empleado':aux_cedula,
                            'activo':ustr(sh.cell(r,1).value),
                        })
        return True

    def updateCategStock(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        move_ids = move_obj.search(cr, uid, [('type_id','=','out')])
        if move_ids:
            for move_id in move_ids:
                move = move_obj.browse(cr, uid, move_id)
                aux_categ_id = move.product_id.categ_id.id
                move_obj.write(cr, uid, move_id,{
                    'categ_id':aux_categ_id,
                })
        return True

    def recomputePartidaNivel(self, cr, uid, ids, context=None):
        budget_obj = self.pool.get('budget.post')
        post_ids = budget_obj.search(cr, uid, [])
        if post_ids:
            for post_id in post_ids:
                post = budget_obj.browse(cr, uid, post_id)
                aux_name = post.name
                aux_name_2 = aux_name + ' '
                budget_obj.write(cr, uid, post_id,{'name':aux_name_2})
        return True

    def updateCategActivo(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        categ_obj = self.pool.get('asset.asset.subcateg')
        asset_ids = asset_obj.search(cr, uid, [])
        if asset_ids:
            for asset_id in asset_ids:
                asset = asset_obj.browse(cr, uid, asset_id)
                code = asset.code
                code_cuenta = code[0:11]
                len_total = len(code)
                aux_code_subcateg = code[12:len_total-4]
                if len(aux_code_subcateg)>=1:
                    if aux_code_subcateg[len(aux_code_subcateg)-1]=='.':
                        aux_code_subcateg = code[12:len_total-5]
                subcateg_ids = categ_obj.search(cr, uid, [('cuenta_contable','=',code_cuenta),('code','=',aux_code_subcateg)],limit=1)
                if subcateg_ids:
                    asset_obj.write(cr, uid, asset_id,{'subcateg_id':subcateg_ids[0]})
        return True

    def updateInicioCateg(self, cr, uid, ids, context=None):
        categ_obj = self.pool.get('product.category')
        subcateg_obj = self.pool.get('product.subcategory')
        product_obj = self.pool.get('product.product')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['tipo_sistema'] == 'sigame':
                for r in range(sh.nrows)[1:]:
                    aux_code = ustr(sh.cell(r,2).value)
                    aux_name = ustr(sh.cell(r,3).value)
                    aux_code_categ = ustr(sh.cell(r,1).value)
                    aux_code_c = aux_code_categ[0:11]
                    categ_ids = categ_obj.search(cr, uid, [('code','=',aux_code_c)])
                    if not categ_ids:
                        import pdb
                        pdb.set_trace()
                    product_ids = product_obj.search(cr, uid, [('name','=',aux_name),('default_code','=',aux_code)])
                    if product_ids:
                        product_obj.write(cr, uid, product_ids[0],{
                            'categ_id':categ_ids[0],
                        })
                    else:
                        print "NO PRODUCTOS", aux_code, aux_name
        return True

    def updateCategProducto(self, cr, uid, ids, context=None):
        categ_obj = self.pool.get('product.category')
        subcateg_obj = self.pool.get('product.subcategory')
        product_obj = self.pool.get('product.product')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['tipo_sistema'] == 'sigame':
                for r in range(sh.nrows)[1:]:
                    aux_code = ustr(sh.cell(r,2).value)
                    aux_name = ustr(sh.cell(r,3).value)
                    aux_code_categ = ustr(sh.cell(r,1).value)
                    aux_code_c = aux_code_categ[0:11]
                    categ_ids = categ_obj.search(cr, uid, [('code','=',aux_code_c)])
                    if not categ_ids:
                        import pdb
                        pdb.set_trace()
                    product_ids = product_obj.search(cr, uid, [('name','=',aux_name),('default_code','=',aux_code),('categ_id','=',categ_ids[0])])
                    if product_ids:
                        aux = len(aux_code)
                        if len(aux_code)>3:
                            aux_code_p = aux_code[0:aux-4]
                        else:
                            aux_code_p = aux_code
                        subcateg_ids = subcateg_obj.search(cr, uid, [('account_code','=',aux_code_categ),('code','=',aux_code_p)])
                        if not subcateg_ids:
                            subcateg_ids = subcateg_obj.search(cr, uid, [('code','=',aux_code_p)])
                        if not subcateg_ids:
                            import pdb
                            pdb.set_trace()
                        if categ_ids:
                            product_obj.write(cr, uid, product_ids[0],{
                                'categ_id':categ_ids[0],
                                'subcateg_id':subcateg_ids[0],
                            })
                        else:
                            product_obj.write(cr, uid, product_ids[0],{
                                'subcateg_id':subcateg_ids[0],
                            })
                    else:
                        print "NO PRODUCTO", aux_code_c, aux_code, aux_name
        return True


    def updateCategoria(self, cr, uid, ids, context=None):
        categ_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        categ_ids = categ_obj.search(cr, uid, [])
        if categ_ids:
            for categ_id in categ_ids:
                categ = categ_obj.browse(cr, uid, categ_id)
                if categ.parent_id:
                    categ_aux_id = categ.parent_id.id 
                    product_ids = product_obj.search(cr, uid, [('categ_id','=',categ_id)])
                    if product_ids:
                        for product_id in product_ids:
                            product_obj.write(cr, uid, product_id,{
                                'categ_id':categ_aux_id,
                            })
        return True

    def updateValor(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                aux_code = ustr(sh.cell(r,1).value) + '.' + ustr(sh.cell(r,2).value) 
                asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code),('state','=','open')])
                if asset_ids:
                    asset_obj.write(cr, uid, asset_ids,{'purchase_value':sh.cell(r,0).value})
                else:
                    "print NO ACTIVO FLE MADSOO", aux_code
        return True

    def loadActivoSigame(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        categ_obj = self.pool.get('account.asset.category')
        subcateg_obj = self.pool.get('asset.asset.subcateg')
        department_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        acc_obj = self.pool.get('account.account')
        tipotr_obj = self.pool.get('gt.account.asset.transaction')
        componente_obj = self.pool.get('gt.account.asset.componente')
        partner_obj = self.pool.get('res.partner')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['tipo_sistema'] == 'sigame':
                for r in range(sh.nrows)[1:]:
                    aux_tipoactivo = ustr(sh.cell(r,1).value)
                    aux_categ = ustr(sh.cell(r,2).value)
                    categ_ids = categ_obj.search(cr, uid, [('code','=',aux_categ)],limit=1)
                    if not categ_ids:
                        raise osv.except_osv(('Error datos!'),'No cateoria %s'%(aux_categ))
                    #quitar lo ultimo hasta el .
                    aux_subcateg = ustr(sh.cell(r,3).value)
                    lista = []
                    pos_inicial = -1
                    try:
                        while True:
                            pos_inicial = aux_subcateg.index('.', pos_inicial+1)
                            lista.append(pos_inicial)
                    except ValueError: # cuando ya no se encuentre la letra
                        print aux_subcateg
                    if len(lista)>0:
                        aux_len = len(lista)
                        aux_subcateg = aux_subcateg[:lista[aux_len-1]]
                    subcateg_ids = subcateg_obj.search(cr, uid, [('code','=',aux_subcateg)],limit=1)
                    if not subcateg_ids:
                        raise osv.except_osv(('Error datos!'),'No subcateoria %s'%(aux_subcateg))
                    aux_code = aux_categ + '.' + ustr(sh.cell(r,3).value)
                    #busco activo si esta solo actualizo el valor de compra
                    asset_ids = asset_obj.search(cr, uid, [('code','=',aux_code)])
                    if asset_ids:
                        continue
                    aux_tipocompra = ustr(sh.cell(r,21).value) 
                    tr_ids = tipotr_obj.search(cr, uid,[('name','=',aux_tipocompra)],limit=1)
                    emp_ids = employee_obj.search(cr, uid, [('name','=','1234567890')],limit=1)
                    emp_id = emp_ids[0]
                    dept_ids = department_obj.search(cr, uid,[])
                    aux_asignado = ustr(sh.cell(r,25).value)
                    bandera = False
                    if aux_asignado == 'S':
                        bandera = True
                    aux_estado1 = str(sh.cell(r,20).value)
                    if aux_estado1 in ('Bueno','Malo','Regular'):
                        aux_estado = 'open'
                    else:
                        aux_estado = 'close'
                    aux_proveedor = str(sh.cell(r,22).value)
                    partner_id = 1
                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_proveedor)],limit=1)
                    if partner_ids:
                        partner_id = partner_ids[0]
                    aux_valor_actual = float(sh.cell(r,12).value) - float(sh.cell(r,15).value) 
                    activo_id = asset_obj.create(cr, uid, {
                        'code':aux_code,
                        'noemp':bandera,
                        'type':aux_tipoactivo,
                        'serial_number':sh.cell(r,9).value,
                        'subcateg_id':subcateg_ids[0],
                        'category_id':categ_ids[0],
                        'department_id':dept_ids[0],
                        'name':sh.cell(r,4).value,
                        'purchase_value':sh.cell(r,12).value,
                        'depreciacion':sh.cell(r,15).value,
                        'valor_actual':aux_valor_actual,
                        'salvage_value':sh.cell(r,17).value,
                        'purchase_date':str(sh.cell(r,13).value),
                        'employee_id':emp_ids[0],
                        'state':aux_estado,
                        'condicion':aux_estado1,
                        'transaction_id':tr_ids[0],
                        'residual':sh.cell(r,15).value,
                        'invoice_id':sh.cell(r,26).value,
                        'marca':sh.cell(r,7).value,
                        'modelo':sh.cell(r,8).value,
                        'color':sh.cell(r,10).value,
                        'otros_accesorios':sh.cell(r,11).value,
                        'note':sh.cell(r,23).value,
                        'partner_id':partner_id,
                        'method_number':sh.cell(r,14).value,
                        })
                    print "activo creado", activo_id
        return True

    def actualizaActivoEmpalme(self, cr, uid, ids, context=None):
        print "vele"
        asset_obj = self.pool.get('account.asset.asset')
        categ_obj = self.pool.get('account.asset.category')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                if data['municipio'] == 'emp':
                    if len(ustr(sh.cell(r,0).value))>1 and len(ustr(sh.cell(r,4).value))>1:
                        code_aux = str(sh.cell(r,4).value)
                        code = code_aux.replace(',','.')
                        code = code.replace(' ','')
                        asset_ids = asset_obj.search(cr, uid, [('code','=',code)])
                        if asset_ids:
                            aux_final = len(code)
                            code_aux_categ = str(sh.cell(r,1).value)
                            categ_ids = categ_obj.search(cr, uid, [('code','=',code_aux_categ)])
                            if categ_ids:
                                asset_obj.write(cr, uid, asset_ids[0], {
                                    'category_id':categ_ids[0],
                                })
                            else:
                                print 'NO VCATEG', code_aux_categ
                        else:
                            print "NO ASSET", code
        return True
                            


    def load_activo(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        categ_obj = self.pool.get('account.asset.category')
        subcateg_obj = self.pool.get('asset.asset.subcateg')
        department_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        acc_obj = self.pool.get('account.account')
        tipotr_obj = self.pool.get('gt.account.asset.transaction')
        componente_obj = self.pool.get('gt.account.asset.componente')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            r = 2296
            for r in range(sh.nrows)[1:]:
                if data['municipio'] == 'emp':
                    if len(ustr(sh.cell(r,0).value))>1 and len(ustr(sh.cell(r,4).value))>1:
                        code_aux = str(sh.cell(r,4).value)
                        aux_tipo = code_aux[0:3]
                        code = code_aux.replace(',','.')
                        code_aux_categ = code[12:14]
                        aux_cta_contable_1 = code[0:6] + code[12:14]
                        if len(code)==16:
                            aux_cta_contable = code[0:1] + '.' + code[1:2] + '.' + code[2:3] + '.' + code[4:6] +'.' + code[10:12]
                        elif len(code)==17:
                            aux_cta_contable = code[0:1] + '.' + code[1:2] + '.' + code[2:3] + '.' + code[4:6] +'.' + code[13:15]
                        elif len(code)==19:
                            aux_cta_contable = code[0:1] + '.' + code[1:2] + '.' + code[2:3] + '.' + code[4:6] +'.' + code[10:12]
                        elif len(code)==20:
                            aux_cta_contable = code[0:1] + '.' + code[1:2] + '.' + code[2:3] + '.' + code[4:6] +'.' + code[12:14]
                        else:
                            aux_cta_contable = code[0:1] + '.' + code[1:2] + '.' + code[2:3] + '.' + code[4:6] +'.' + code[12:14]
                        cta_contable_ids = acc_obj.search(cr, uid, [('code','=',aux_cta_contable)],limit=1)
                        if cta_contable_ids:
                            account_id = cta_contable_ids[0]
                        else:
                            cta_contable_ids = acc_obj.search(cr, uid, [('code','ilike',aux_cta_contable)],limit=1)
                            if cta_contable_ids:
                                account_id = cta_contable_ids[0]
                            else:
                                account_id=5869
                        #tipo
                        if aux_tipo=='141':
                            tipo_aux = 'larga_duracion'
                            tipo_aux_as = 'Larga Duracion'
                        else:
                            tipo_aux = 'sujeto_control'
                            tipo_aux_as = 'Sujeto a Control'
                        categ_ids = categ_obj.search(cr, uid, [('cuenta_baja','=',account_id)],limit=1)
                        if categ_ids:
                            categ_id = categ_ids[0]
                            categ = categ_obj.browse(cr, uid, categ_id)
                            subcateg_ids = subcateg_obj.search(cr, uid, [('categ_id','=',categ.id)],limit=1)
                            subcateg_id = subcateg_ids[0]
                        else:
                            categ_id = categ_obj.create(cr, uid, {
                                'type_asset':tipo_aux,
                                'name':ustr(sh.cell(r,1).value),
                                'code':code_aux_categ,
                                'cuenta_ingreso':account_id,
                                'cuenta_baja':account_id,
                                'account_asset_id':account_id,
                                'account_depreciation_id':account_id,
                                'account_expense_depreciation_id':account_id,
                                'journal_id':22,
                            })
                            subcateg_id = subcateg_obj.create(cr, uid, {
                                'name':ustr(sh.cell(r,1).value),
                                'categ_id':categ_id,
                            })
                        tr_ids = tipotr_obj.search(cr, uid,[],limit=1)
                        emp_ids = employee_obj.search(cr, uid, [('name','=',ustr(sh.cell(r,15).value).replace(' ',''))],limit=1)
                        if emp_ids:
                            empleado = employee_obj.browse(cr, uid, emp_ids[0])
                            emp_id = emp_ids[0]
                        else:
                            emp_id = 1
                        dept_ids = department_obj.search(cr, uid, [('name','ilike',ustr(sh.cell(r,12).value))],limit=1)
                        if dept_ids:
                            dept_id = dept_ids[0]
                        else:
                            dept_id = empleado.department_id.id
                        bandera = False
                        if str(sh.cell(r,13).value)=='11111':
                            bandera=True
                        if str(sh.cell(r,11).value):
                            if len(str(sh.cell(r,11).value))==4:
                                aux_date = '01/01/'+str(sh.cell(r,11).value)
                            else:
                                aux_date = str(sh.cell(r,11).value)
                            activo_id = asset_obj.create(cr, uid, {
                                'code':code,
                                'noemp':bandera,
                                'type':tipo_aux_as,
                                'serial_number':sh.cell(r,8).value,
                                'subcateg_id':subcateg_id,
                                'category_id':categ_id,
                                'department_id':dept_id,
                                'name':ustr(sh.cell(r,5).value),
                                'purchase_value':sh.cell(r,10).value,
                                'salvage_value':0,
                                'purchase_date':aux_date,
                                'employee_id':emp_id,
                                'state':'open',
                                'transaction_id':tr_ids[0],
                                'residual':0,
                                'marca':ustr(sh.cell(r,6).value),
                                'modelo':ustr(sh.cell(r,7).value),
                                'color':ustr(sh.cell(r,9).value),
                            })
                        else:
                            activo_id = asset_obj.create(cr, uid, {
                                'code':code,
                                'noemp':bandera,
                                'type':tipo_aux_as,
                                'serial_number':sh.cell(r,8).value,
                                'subcateg_id':subcateg_id,
                                'category_id':categ_id,
                                'department_id':dept_id,
                                'name':ustr(sh.cell(r,5).value),
                                'purchase_value':sh.cell(r,10).value,
                                'salvage_value':0,
                                'employee_id':emp_id,
                                'state':'open',
                                'transaction_id':tr_ids[0],
                                'residual':0,
                                'marca':ustr(sh.cell(r,6).value),
                                'modelo':ustr(sh.cell(r,7).value),
                                'color':ustr(sh.cell(r,9).value),
                            })
                    else:
                        #crea componente y pone al activo anterior
                        componente_obj.create(cr, uid, {
                            'name':ustr(sh.cell(r,5).value),
                            'value':ustr(sh.cell(r,7).value),
                            'marca':ustr(sh.cell(r,6).value),
                            'serie':ustr(sh.cell(r,8).value),
                            'asset_id':activo_id,
                        })
                elif data['municipio'] == 'nr':
                    if len(str(sh.cell(r,4).value))>1:
                        categ_ids = categ_obj.search(cr, uid, [('name','=',ustr(sh.cell(r,4).value))],limit=1)
                        subcateg_ids = subcateg_obj.search(cr, uid, [('name','=',ustr(sh.cell(r,2).value))],limit=1)
                        tr_ids = tipotr_obj.search(cr, uid,[],limit=1)
                        dept_ids = department_obj.search(cr, uid, [('name','=',ustr(sh.cell(r,11).value))],limit=1)
                        print "departamentpo", ustr(sh.cell(r,11).value), ustr(sh.cell(r,23).value)
                        if len(dept_ids)>0:
                            dep_id = dept_ids[0]
                        else:
                            dep_id = department_obj.create(cr, uid, {
                                'name': ustr(sh.cell(r,11).value),
                            })
                    emp_ids = employee_obj.search(cr, uid, [('name','ilike',str(sh.cell(r,23).value))],limit=1)
                    if len(emp_ids)>0:
                        emp_id = emp_ids[0]
                        bandera = False
                    else:
                        emp_ids = employee_obj.search(cr, uid, [('name','=','000001111')],limit=1)
                        emp_id = emp_ids[0]
                        bandera = True
                        aux_estado = str(sh.cell(r,21).value)
                        activo_id = asset_obj.create(cr, uid, {
                            'code':ustr(sh.cell(r,25).value),
                            'noemp':bandera,
                            'type':'Larga Duracion',
                            'serial_number':sh.cell(r,0).value,
                            'subcateg_id':subcateg_ids[0],
                            'category_id':categ_ids[0],
                            'department_id':dep_id,
                            'name':sh.cell(r,41).value,
                            'purchase_value':sh.cell(r,37).value,
                            'salvage_value':sh.cell(r,39).value,
                            'purchase_date':str(sh.cell(r,26).value),
                            'employee_id':emp_ids[0],
                            'state':sh.cell(r,21).value,
                            'transaction_id':tr_ids[0],
                            'residual':sh.cell(r,40).value,
                            'invoice_id':sh.cell(r,28).value,
                        })
                    print "activo creado", activo_id

    def load_presupuesto(self, cr, uid, ids, context=None):
        item_obj = self.pool.get('budget.item')
        data = self.read(cr, uid, ids)[0]
        if data['journal_id']:
            if data['archivo']:
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                for r in range(sh.nrows)[1:]:  
                    if sh.cell(r,5).value:
                        aux_tipo_comp = ustr(sh.cell(r,27).value)
        return True

    def asiento_partner(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        account_obj = self.pool.get('account.account')
        position_obj = self.pool.get('account.fiscal.position')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:  
                if sh.cell(r,8).value:
                    aux_comp = ustr(sh.cell(r,1).value)
                    aux_ced_ruc = ustr(sh.cell(r,4).value)
                    partner_id = partner_obj.search(cr, uid, [('ced_ruc','=',aux_ced_ruc)],limit=1)
                    aux_name = ustr(sh.cell(r,6).value) + ' ' + ustr(sh.cell(r,5).value)
                    if not partner_id:
                        partner_id = partner_obj.create(cr, uid, {
                            'ced_ruc':aux_ced_ruc,
                            'type_ced_ruc':'pasaporte',
                            'tipo_persona':'6',
                            'name':aux_name,
                            'direccion':'NARANJAL',
                            'telefono':'00000',
                            'property_account_receivable':'1689',
                            'property_account_payable':'2823',
                            'property_account_position':'2',
                        })
                    
        
    def validate_asiento(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        line_obj = self.pool.get('account.move.line')
        move_ids = move_obj.search(cr, uid, [])
        for move_id in move_ids:
            move = move_obj.browse(cr, uid, move_id)
            if move.state == 'draft':
                move_obj.button_validate(cr, uid, [move.id], context)
        return True

    def load_budget(self, cr, uid, ids, context=None):
        item_obj = self.pool.get('budget.item')
        budget_obj = self.pool.get('budget.post')
        program_obj = self.pool.get('project.program')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            migrated_obj = self.pool.get('budget.item.migrated')
            if data['budget_type']=='ingreso':
                for r in range(sh.nrows)[1:]:
                    aux_partida = ustr(sh.cell(r,0).value)
                    if len(aux_partida)>8:
                        budget_aux = aux_partida.replace('.','')
                        budget_ids = budget_obj.search(cr, uid, [('code','=',budget_aux)],limit=1)
                        if not budget_ids:
                            print "no hay partida presupuestaria de catalogo de ingreso", budget_aux
                        else:
                            budget_item_ids = item_obj.search(cr, uid, [('budget_post_id','=',budget_ids[0])],limit=1)
                            if not budget_item_ids:
                                print "no hay budget item con partida", budget_aux
                            else:
                                migrated_obj.create(cr, uid, {
                                    'budget_post_id':budget_ids[0],
                                    'budget_item_id': budget_item_ids[0],
                                    'type_budget': "ingreso",
                                    'date':sh.cell(r,8).value,
                                    'planned_amount':float(sh.cell(r,2).value.replace(" ","")),
                                    'reform_amount': float(sh.cell(r,3).value.replace(" ","")),
                                    'codif_amount': float(sh.cell(r,4).value.replace(" ","")),
                                    'devengado_amount': float(sh.cell(r,5).value.replace(" ","")),
                                    'paid_amount': float(sh.cell(r,6).value.replace(" ","")),
                                    'devengado_balance': float(sh.cell(r,7).value.replace(" ",""))
                                })
                print "terminada importacion de ingresos"            
            elif data['budget_type']=='egreso':
                for r in range(sh.nrows)[1:]:
                    aux_partida = ustr(sh.cell(r,0).value)
                    if len(aux_partida)>12:
                        budget_aux_sin_punto = aux_partida.replace('.','')
                        budget_aux = budget_aux_sin_punto[0:6]
                        budget_ids = budget_obj.search(cr, uid, [('code','=',budget_aux)],limit=1)
                        if not budget_ids:
                            print "no hay partida presupuestaria", budget_aux
                        programa_aux = budget_aux_sin_punto[10:15]
                        programa_ids = program_obj.search(cr, uid, [('sequence','=',programa_aux)])
                        aux_concatenado = budget_aux + '.' + '0000' + '.' + programa_aux
                        if not budget_ids:
                            print "no hay partida presupuestaria de egreso", budget_aux
                        else:
                            budget_item_ids = item_obj.search(cr, uid, [('code','=',aux_concatenado)],limit=1)
                            if not budget_item_ids:
                                print "no hay budget item con partida", aux_concatenado
                            else:
                                migrated_obj.create(cr, uid, {
                                    'budget_item_id': budget_item_ids[0],
                                    'budget_post_id':budget_ids[0],
                                    'program_code': programa_aux,
                                    'type_budget': "gasto",
                                    'date':sh.cell(r,10).value,
                                    'planned_amount':float(sh.cell(r,2).value.replace(" ","")),
                                    'reform_amount': float(sh.cell(r,3).value.replace(" ","")),
                                    'codif_amount': float(sh.cell(r,4).value.replace(" ","")),
                                    'commited_amount': float(sh.cell(r,5).value.replace(" ","")),
                                    'devengado_amount': float(sh.cell(r,6).value.replace(" ","")),
                                    'paid_amount': float(sh.cell(r,7).value.replace(" ","")),
                                    'commited_balance': float(sh.cell(r,8).value.replace(" ","")),
                                    'devengado_balance': float(sh.cell(r,9).value.replace(" ","")),
                                })
                print "terminada importacion de egresos"            
            else:
                print "No  hacer nada"
        return True

    def cuentas_no(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                if ustr(sh.cell(r,5).value)=='C':
                    aux_code = ustr(sh.cell(r,7).value)
                    account_ids = account_obj.search(cr, uid, [('code','=',aux_code)],limit=1)
                    if not account_ids:
                        print "NO EXISTE LA CTA ==============================", aux_code
        return True

    def load_asiento_detalle(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        cert_line_obj = self.pool.get('budget.certificate.line')
        project_obj = self.pool.get('project.project')
        item_obj = self.pool.get('budget.item')
        data = self.read(cr, uid, ids)[0]
        if data['archivo'] and data['as_det']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            if data['as_det'] =='P':
                aux_value_debit = 0
                for r in range(sh.nrows)[1:]:
                    if ustr(sh.cell(r,5).value)=='P':
                        name_aux = ustr(sh.cell(r,2).value)
                        aux_budget = str(sh.cell(r,7).value)
                        aux_b = aux_budget[0:6] + '.' + '0000' + '.' + aux_budget[10:16]
                        move_ids = move_obj.search(cr, uid, [('name','=',name_aux)],limit=1)
                        aux_value_debit = sh.cell(r,11).value
                        if move_ids:
                            move = move_obj.browse(cr, uid, move_ids[0])
                            move_line_ids = move_line_obj.search(cr, uid, [('move_id','=',move_ids[0]),('debit','=',aux_value_debit)])
    #                        project_ids = project_obj.search(cr, uid, [])
    #                        project = project_obj.browse(cr, uid, project_ids[0])
                            #buscar el budget item
                            item_ids = item_obj.search(cr, uid, [('code','=',aux_b)])
                            if item_ids:
                                item_id = item_ids[0]
                                item = item_obj.browse(cr, uid, item_ids[0])
                            else:
                                if int(aux_budget[7:15])<=0:
                                    aux_b_ingreso = aux_budget[0:6] + '.01.9999'
                                    item_ids = item_obj.search(cr, uid, [('code','=',aux_b_ingreso)])
                                    if item_ids:
                                        item = item_obj.browse(cr, uid, item_ids[0])
                                        item_id = item_ids[0]
                                else:
                                    print "NO BUDGET ITEM", aux_b 
                            if move_line_ids:
                                #busco 
                                cert_line_id = cert_line_obj.create(cr, uid, {
                                    'project_id':item.project_id.id,
                                    'task_id':item.project_id.tasks[0].id,
                                    'budget_id':item_id,
                                    'amount':sh.cell(r,11).value,
                                    'amount_certified':sh.cell(r,11).value,
                                    'amount_commited':sh.cell(r,11).value,
                                    'period_id':move.period_id.id,
                                })
                                cr.execute('''UPDATE account_move_line set budget_id_cert=%s where id=%s''' % (cert_line_id,move_line_ids[0]))
                                #busco que coincida al debe
#                                move_line_obj.write(cr, uid, move_line_ids[0],{
#                                    'budget_id_cert':cert_line_id,
#                                })
            else:
                for r in range(sh.nrows)[1:]:
                    if ustr(sh.cell(r,5).value)=='C':
                        name_aux = ustr(sh.cell(r,2).value)
                        aux_code = ustr(sh.cell(r,6).value)
                        aux_debe = ustr(sh.cell(r,8).value)
                        aux_value_debit = aux_value_credit = 0
                        if aux_debe == 'D':
                            aux_value_debit = float(sh.cell(r,10).value)
                        else:
                            aux_value_credit = float(sh.cell(r,10 ).value)
                        move_ids = move_obj.search(cr, uid, [('name','=',name_aux)],limit=1)
                        if move_ids:
                            move = move_obj.browse(cr, uid, move_ids[0])
                            date_aux = move.date
                            journal_aux = move.journal_id.id
                            period_aux = move.period_id.id
                            account_ids = account_obj.search(cr, uid, [('code','=',aux_code)],limit=1)
                            if account_ids:
                                account_id = account_ids[0]
                            else:
                                account_id = account_obj.create(cr, uid, {
                                    'name':aux_code,
                                    'code':aux_code,
                                    'code_aux': aux_code,
                                    'type':'other',
                                    'user_type':6,
                                })
                                print "cuenta creada", aux_code,
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,name,account_id,debit,credit,journal_id,period_id,date,state,company_id,currency_id,migrado) VALUES (%s, %s, %s,%s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_ids[0],name_aux,account_id,aux_value_debit,aux_value_credit,journal_aux,period_aux,date_aux,state_aux,company_aux,currency_aux,True))
#                            print "ACUMULDADOR=========================", r
        return True

    def load_asiento(self, cr, uid, ids, context=None):
        print "sube asiento"
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        partner_obj = self.pool.get('res.partner')
        account_obj = self.pool.get('account.account')
        journal_obj = self.pool.get('account.journal')
        data = self.read(cr, uid, ids)[0]
        if data['journal_id']:
            if data['archivo']:
                arch = data['archivo']
                arch_xls = base64.b64decode(arch)
                book = xlrd.open_workbook(file_contents=arch_xls)
                sh = book.sheet_by_name(book.sheet_names()[0])
                context={}
                if data['asiento_type']=='cc':
                    for r in range(sh.nrows)[1:]:
                        aux_state = ''
                        aux_doc = ustr(sh.cell(r,17).value)   
                        if sh.cell(r,8).value:
                            if aux_doc=='3':
                                aux_tipo_comp = ustr(sh.cell(r,16).value)
                                if aux_tipo_comp == 'EGRESOS':
                                    journal_aux = data['journal_id'][0]
                                elif aux_tipo_comp == 'INGRESOS':
                                    journal_aux = data['journal_in'][0]
                                else:
                                    journal_aux = data['journal_diario'][0]
                                date_aux = ustr(sh.cell(r,2).value)
                                date_aux2 = date_aux[6:10] + '-' + date_aux[3:5] + '-' + date_aux[0:2]
                                name_aux = ustr(sh.cell(r,1).value)#numero
                                desc_aux = ustr(sh.cell(r,10).value)
                                aux_cedruc = ustr(sh.cell(r,4).value)
                                period_ids = period_obj.search(cr, uid, [('date_start','<=',date_aux2),
                                                                         ('date_stop','>=',date_aux2)],limit=1)
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',aux_cedruc)])
                                if partner_ids:
                                    partner_id = partner_ids[0]
                                else:
                                    print "NO PARTNER", aux_cedruc
                                    partner_id = partner_obj.create(cr, uid, {
                                        'ced_ruc':aux_cedruc,
                                        'type_ced_ruc':'pasaporte',
                                        'tipo_persona':'6',
                                        'name':ustr(sh.cell(r,6).value),
                                        'direccion':'Naranjal',
                                        'telefono':'SN',
                                        'property_account_receivable':1689,
                                        'property_account_payable':2823,
                                        'property_account_position':2,})
                                move_id = move_obj.create(cr, uid, {
                                    'partner_id':partner_id,
                                    'journal_id':journal_aux,
                                    'date':date_aux2,
                                    'period_id':period_ids[0],
                                    'name':name_aux,
                                    'ref':desc_aux,
                                    'narration':desc_aux,
                                    'migrado':True,
                                })
                            else:
                                print "HJYHJGJG============", name_aux
                elif data['asiento_type']=='cs':
                    partner_id = 1
                    for r in range(sh.nrows)[1:]:  
                        if sh.cell(r,5).value:
                            aux_tipo_comp = ustr(sh.cell(r,13).value)
                            if aux_tipo_comp == 'EGRESOS':
                                journal_aux = data['journal_id'][0]
                            elif aux_tipo_comp == 'INGRESOS':
                                journal_aux = data['journal_in'][0]
                            else:
                                journal_aux = data['journal_diario'][0]
                            date_aux = ustr(sh.cell(r,2).value)
                            date_aux2 = date_aux[6:10] + '-' + date_aux[3:5] + '-' + date_aux[0:2]
                            name_aux = ustr(sh.cell(r,1).value)#numero
                            desc_aux = ustr(sh.cell(r,7).value)
                            period_ids = period_obj.search(cr, uid, [('date_start','<=',date_aux2),
                                                                     ('date_stop','>=',date_aux2)],limit=1)
                            aux_state = ''
                            aux_state_aux =ustr(sh.cell(r,4).value)
                            if aux_state_aux=='AN':
                                aux_state='anulado'
                            else:
                                aux_state='draft'
                            move_id = move_obj.create(cr, uid, {
                                'state':aux_state,
                                'partner_id':partner_id,
                                'journal_id':journal_aux,
                                'date':date_aux2,
                                'period_id':period_ids[0],
                                'name':name_aux,
                                'ref':desc_aux,
                                'narration':desc_aux,
                                'migrado':True,
                            })
                else:
                    print "Ninguno"
        return True
                    
    def updateCodeProduct(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:   
                name_aux = ustr(sh.cell(r,0).value)
                product_ids = product_obj.search(cr, uid, [('name','=',name_aux)])
                if product_ids:
                    if len(product_ids)==2:
                        print "HAY DOS DE UN ORJLKJLKJJLKJJK+++++++++", name_aux
                        product_obj.unlink(cr, uid, [product_ids[1]])
                    if len(product_ids)==3:
                        print "HAY TREsS DE UN ORJLKJLKJJLKJJK+++++++++", name_aux
                        product_obj.unlink(cr, uid, [product_ids[1]])
                        product_obj.unlink(cr, uid, [product_ids[2]])
                    product_obj.write(cr, uid, product_ids[0],{
                        'default_code':ustr(sh.cell(r,1).value),
                    })
                else:
                    print "No productos"
        return True
                
  
    def load_product(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')
        categ_obj = self.pool.get('product.category')
        subcateg_obj = self.pool.get('product.subcategory')
        acc_obj = self.pool.get('account.account')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if data['municipio']=='emp':
                print "empalme"
                for r in range(sh.nrows)[1:]:   
                    categ_name = ustr(sh.cell(r,3).value)
                    categ_ids = categ_obj.search(cr, uid, [('name','=',categ_name)],limit=1)
                    if not categ_ids:
                        print "No existe la categoria", categ_name
                    categ = categ_obj.browse(cr, uid, categ_ids[0])
                    subcateg_name = ustr(sh.cell(r,4).value)
                    subcateg_ids = subcateg_obj.search(cr, uid, [('name','=',subcateg_name)],limit=1)
                    if not subcateg_ids:
                        print "No existe la subcategoria", subcateg_name
                    subcateg = subcateg_obj.browse(cr, uid, subcateg_ids[0])
                    uom_name = ustr(sh.cell(r,6).value)
                    uom_ids = uom_obj.search(cr, uid, [('name','=',uom_name)],limit=1)
                    if not uom_ids:
                        print "No existe la u medida", uom_name
                    uom = uom_obj.browse(cr, uid, uom_ids[0])
                    id_creado = product_obj.create(cr, uid, {
                        'name':ustr(sh.cell(r,0).value),
                        'default_code':ustr(sh.cell(r,1).value),
                        'type':'product',
                        'categ_id':categ.id,
                        'uom_id':uom.id,
                        'uos_id':uom.id,
                        'uom_po_id':uom.id,
                        'subcateg_id':subcateg.id,
                        'cost_method':'average',
                        'valuation':'real_time',
#                        'standard_price':sh.cell(r,8).value,
                    })
            else:
                for r in range(sh.nrows)[1:]:   
                    categ_name = ustr(sh.cell(r,4).value)
                    categ_ids = categ_obj.search(cr, uid, [('name','=',categ_name)],limit=1)
                    if not categ_ids:
                        print "No existe la categoria", categ_name
                    categ = categ_obj.browse(cr, uid, categ_ids[0])
                    subcateg_name = ustr(sh.cell(r,5).value)
                    subcateg_ids = subcateg_obj.search(cr, uid, [('name','=',subcateg_name)],limit=1)
                    if not subcateg_ids:
                        print "No existe la subcategoria", subcateg_name
                    subcateg = subcateg_obj.browse(cr, uid, subcateg_ids[0])
                    uom_name = ustr(sh.cell(r,6).value)
                    uom_ids = uom_obj.search(cr, uid, [('name','=',uom_name)],limit=1)
                    if not uom_ids:
                        print "No existe la u medida", uom_name
                    uom = uom_obj.browse(cr, uid, uom_ids[0])
                    acc_name = ustr(sh.cell(r,7).value)
                    acc_ids = acc_obj.search(cr, uid, [('code','=',acc_name)],limit=1)
                    if not acc_ids:
                        print "No existe la cuenta", acc_name
                        acc_ids = acc_obj.search(cr, uid, [],limit=1)
                    acc = acc_obj.browse(cr, uid, acc_ids[0])
                    code_familia_aux = str(sh.cell(r,1).value)
                    if len(code_familia_aux)==1:
                        code_familia = code_familia_aux + '00'
                    elif len(code_familia_aux)==2:
                        code_familia = code_familia_aux + '0'
                    else:
                        code_familia = code_familia_aux
                    code_subfamilia_aux = str(sh.cell(r,2).value).zfill(3)
                    code_product_aux = str(sh.cell(r,3).value).zfill(3)
                    code_completo = code_familia + code_subfamilia_aux + code_product_aux
                    id_creado = product_obj.create(cr, uid, {
                        'name':ustr(sh.cell(r,0).value),
                        'default_code':code_completo,
                        'type':'product',
                        'categ_id':categ.id,
                        'uom_id':uom.id,
                        'uos_id':uom.id,
                        'uom_po_id':uom.id,
                        'subcateg_id':subcateg.id,
                        'cost_method':'average',
                        'standard_price':sh.cell(r,8).value,
                        'property_account_expense':acc.id,
                    })
                    print "creado", id_creado, ustr(sh.cell(r,0).value)
        
    def load_partner_inicial(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        b_obj = self.pool.get('res.bank')
        bank_obj = self.pool.get('res.partner.bank')
        account_obj = self.pool.get('account.account')
        fiscal_obj = self.pool.get('account.fiscal.position')
        data = self.read(cr, uid, ids)[0]                        
        account_ids = account_obj.search(cr, uid, [('code','=','1131301001')],limit=1)
        account_ids2 = account_obj.search(cr, uid, [('code','=','213530100101')],limit=1)
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:    
                ced_name = sh.cell(r,1).value
                partner_name = ustr(sh.cell(r,2).value)
                a = True
                if a:#len(ced_name)>9:
                    partner_ids = partner_obj.search(cr, uid, [('name','=',partner_name)])
                    if partner_ids:
                        bank_ids = b_obj.search(cr, uid, [('name','ilike',str(sh.cell(r,8).value))],limit=1)
                        if str(sh.cell(r,11).value)=='AHORROS':
                            aux_t_cta = 'aho'
                        else:
                            aux_t_cta = 'cte'
                        partner = partner_obj.browse(cr, uid, partner_ids[0])
                        if bank_ids:
                            bank_id = bank_obj.create(cr, uid, {
                                'partner_id':partner_ids[0],
                                'bank':bank_ids[0],
                                'type_cta':aux_t_cta,
                                'acc_number':sh.cell(r,9).value,
                            })
                        else:
                            "NO BANCO", sh.cell(r,8).value
                    #    partner_obj.write(cr, uid, partner_ids[0],{
                    #        'ced_ruc':ustr(sh.cell(r,1).value),
                     #   })
#                                            'property_account_position':fiscal_ids[0],
#                                        })
#                        fiscal_ids = fiscal_obj.search(cr, uid, [('name','=','PROFESIONALES - PERSONA NATURAL - HONORARIOS')],limit=1)
#                        partner_obj.write(cr, uid, partner_ids[0], 
#                                        {
#                                            'property_account_position':fiscal_ids[0],
#                                        })
                        print "partner ya existe", partner_name
                    else:
                        #busca por cedula
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',ced_name)])
                        if partner_ids:
                            print "partner ya existe", partner_name
                        else:
                            fiscal_name = str(sh.cell(r,6).value)
                            fiscal_ids = fiscal_obj.search(cr, uid, [('name','=',fiscal_name)],limit=1)
                            partner_id = partner_obj.create(cr, uid, {
                                'name':partner_name,
                                'ced_ruc':ced_name,
                                'type_ced_ruc':'ruc',#sh.cell(r,6).value,
                                'tipo_persona':str(sh.cell(r,5).value),
                                'direccion':ustr(sh.cell(r,3).value),
                                'telefono':ustr(sh.cell(r,4).value),
                                'property_account_receivable':5233,
                                'property_account_payable':6617,
                                'property_account_position':fiscal_ids[0],
                                'customer':False,
                                'supplier':True,
                                'active':True,
                            })
                            bank_ids = bank_obj.search(cr, uid, [('name','ilike',sh.cell(r,1).value)],limit=1)
                            if sh.cell(r,1).value=='AHORROS':
                                aux_t_cta = 'aho'
                            else:
                                aux_t_cta = 'cte'
                            if bank_ids:
                                bank_id = bank_obj.create(cr, uid, {
                                    'partner_id':partner_id,
                                    'bank':bank_ids[0],
                                    'type_cta':aux_t_cta,
                                    'acc_number':sh.cell(r,10).value,
                                })
                else:
                    print "partner no migrado cedula incorrecta", partner_name
        return True

    def load_file_partner(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                partner_name = ustr(sh.cell(r,0).value)
                partner_ids = partner_obj.search(cr, uid, [('name','=',partner_name)])
                for partner_id in partner_ids:
                    partner = partner_obj.browse(cr, uid, partner_id)
                    bank_id = bank_obj.search(cr, uid, [('partner_id','=',partner_id)],limit=1)
                    if bank_id:
                        partner_obj.write(cr, uid, partner_id,{
                                'ced_ruc':ustr(sh.cell(r,1).value),
                                'type_ced_ruc':'cedula',
                                'tipo_persona':'6',
                                })
                    else:
                        partner_obj.unlink(cr, uid, [partner_id])
        return True

    def load_file(self, cr, uid, ids, context=None):
        acc_obj = self.pool.get('account.account')
        acc_type = self.pool.get('account.account.type')
        data = self.read(cr, uid, ids)[0]
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                parent_code = str(sh.cell(r,4).value)
                user_type_aux = sh.cell(r,6).value
                user_type = acc_type.search(cr, uid, [('name','ilike',user_type_aux)],limit=1)
                name_aux = ustr(sh.cell(r,1).value)
                if len(parent_code) > 0:
                    parent_id = acc_obj.search(cr, uid, [('code','=',parent_code)],limit=1)
                    if len(parent_id)>0:
                        acc_id = acc_obj.create(cr, uid, {
                                'code':str(sh.cell(r,0).value),
                                'name':name_aux,
                                'parent_id':parent_id[0],
                                'type':str(sh.cell(r,5).value),
                                'user_type':user_type[0],
                            })
                    else:
                        aux = str(sh.cell(r,1).value)
                        aux_code = str(sh.cell(r,0).value)
                        print "cta que no tiene papa", aux,aux_code
                        acc_id = acc_obj.create(cr, uid, {
                                'code':str(sh.cell(r,0).value),
                                'name':name_aux,
                                'type':str(sh.cell(r,5).value),
                                'user_type':user_type[0]})
                else:
                    aux = str(sh.cell(r,1).value)
                    aux_code = str(sh.cell(r,0).value)
                    print "cta que no tiene papa", aux,aux_code
                    acc_id = acc_obj.create(cr, uid, {
                            'code':str(sh.cell(r,0).value),
                            'name':name_aux,
                            'type':str(sh.cell(r,5).value),
                            'user_type':user_type[0]})
        return True

    def validate_esigef(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        moves = move_obj.search(cr, uid, [('state','=','posted'),('migrado','=',False),('date','>=','2015-04-01'),('date','<=','2015-04-30')])
        message = move_obj.check_esigef_msg(cr, uid, moves)
        self.write(cr, uid, ids, {'messages': message})
    
    def updateNameUser(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        user_ids = user_obj.search(cr, uid, [])
        for user_id in user_ids:
            user = user_obj.browse(cr, uid, user_id)
            user_obj.write(cr, uid, user_id, {
                    'name':user.job_id.name + ' : ' + user.employee_id.complete_name,
                    })

    def _checkPass(self, cr, uid, ids): 
        result = False
        for this in self.browse(cr, uid, ids):
            if this.password=='m123456':
                result = True
        return result

    _constraints = [
        (_checkPass,
         ustr('No pass.'),[ustr('Pass'), 'Pass'])
    ]

    _columns = dict(
        password = fields.char('Pass',size=10),
        category_id = fields.many2one('account.asset.category','Categoria'),
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        hr_period_id = fields.many2one('hr.work.period','Periodo TTHH'),
        date_start = fields.date('Fecha Desde'),
        date_stop = fields.date('Fecha Hasta'),
        budget_id = fields.many2one('budget.item','Partida'),
        mes_id = fields.many2one('account.period','Mes'),
        period_id = fields.many2one('account.fiscalyear','Anio Fiscal'),
        date = fields.date('Fecha corte'),
        type_olympo = fields.selection([('tabla','tabla'),('ingreso','ingreso')],'Tipo CXP'),
        as_det = fields.selection([('C','C'),('P','P')],'Asiento detalle tipo'),
        name = fields.char('Desc',size=2),
        municipio = fields.selection([('emp','Empalme'),('nr','Naranjal'),('mil','Milagro')],'Municipio'),
        archivo = fields.binary('Archivo', required=True),
        journal_id = fields.many2one('account.journal','Diario Egreso'),
        journal_in = fields.many2one('account.journal','Diario Ingreso'),
        journal_diario = fields.many2one('account.journal','Diario Diario'),
        asiento_type = fields.selection([('inicial','inicial'),('cc','CaberaConBenef'),('cs','CabeceraSinBenef'),('up','Update')],'Tipo'),
        tipo_sistema = fields.selection([('sigame','sigame'),('olympo','olympo')],'SISTEMA'),
        budget_type = fields.selection([('ingreso','ingreso'),('egreso','egreso')],'Tipo Budget'),
        messages = fields.text('Mensajes', readonly=True),
        )
    _defaults = dict(
        name = 'AA',
        municipio = 'emp' ,
        type_olympo = 'ingreso',
        )
updateGob()
class import_stock(osv.osv_memory):

    _name='import.stock'
    
    _columns={
        'name':fields.char('Observaciones',size=128),
        'archivo':fields.binary('Archivo', required=True),
        }

    def _bad_archivo(self, cr, uid, ids, arch,context=None):
        result=True
        acc_obj=self.pool.get('account.account')
        arch_xls = base64.b64decode(arch)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_name(book.sheet_names()[0])
        j=i=0
        for r in range(sh.nrows)[1:]:
            i+=1
            if sh.cell(r,0).value and sh.cell(r,1).value:
 #               import pdb
 #               pdb.set_trace()
                cta_id = acc_obj.search(cr, uid, [('code','=',sh.cell(r,0).value)])
                cta_comp_id=acc_obj.search(cr, uid, [('code','=',sh.cell(r,1).value)])
                if not len(cta_id)>0: 
                    raise osv.except_osv(('Error de archivo!'),'La cta %s , en la linea numero %d no corresponde a nigun empleado'%((str(sh.cell(r,1).value)),i+1))
                if not len(cta_comp_id)>0: 
                    raise osv.except_osv(('Error de archivo!'),'La cta %s comp, en la linea numero %d no corresponde a nigun empleado'%((str(sh.cell(r,1).value)),i+1))
            else:
                raise osv.except_osv(('Error de archivo!'),'Existe un campo que esta vacio en la linea %s '%(r))
#        if j==sh.nrows:
#            result=False
        return result

    def import_stock(self, cr, uid, ids, context=None):
        inv_obj=self.pool.get('stock.inventory')
        inv_line_obj=self.pool.get('stock.inventory.line')
        p_obj = self.pool.get('product.product')
        data = self.read(cr, uid, ids)[0]
#        self._bad_archivo(cr, uid, ids, data['archivo'],context=context)
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            inv_id = inv_obj.create(cr, uid, {'name':data['name']})
            for r in range(sh.nrows)[1:]:
                product_id = p_obj.search(cr, uid, [('default_code','=',sh.cell(r,0).value)])
                qty = sh.cell(r,1).value
                if product_id:
                    product = p_obj.browse(cr, uid, product_id[0])
                    inv_line_obj.create(cr,uid,{
                            'inventory_id':inv_id,
                            'location_id':product.location_id.id,
                            'product_id':product_id[0],
                            'product_uom':product.uom_id.id,
                            'product_qty':sh.cell(r,1).value,
                            })
                else:
                    print "No hay el product", sh.cell(r,0).value
        return {'type':'ir.actions.act_window_close' }

import_stock()


