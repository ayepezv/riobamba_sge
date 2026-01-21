# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
import time
from report import report_sxw
from osv import fields, osv
from gt_tool import XLSWriter
import re

total_todo = []
cabecera_todo = []

class activo_valorado(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(activo_valorado, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'generate_dict_valorado': self.generate_dict_valorado,
        })

    def generate_dict_valorado(self, this):
        dept_obj = self.pool.get('hr.department')
        categ_obj = self.pool.get('account.asset.category')
        asset_obj = self.pool.get('account.asset.asset')
        categ_valor = {}
        if this.tipo=='Todos':
            dept_ids = []
#            categ_ids = []
#            dept_ids = dept_obj.search(self.cr, self.uid, [])
            dept_ids2 = dept_obj.search(self.cr, self.uid, [])
            categ_ids = categ_obj.search(self.cr, self.uid, [])
            if dept_ids2:
                for dep_id in dept_ids2:
                    asset_aux_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dep_id)])
                    if asset_aux_ids:
                        dept_ids.append(dep_id)
        else:
            dept_ids = []
            categ_ids = []
            for dept_id in this.dept_ids:
                dept_ids.append(dept_id.id)
            for categ_id in this.categ_ids:
                categ_ids.append(categ_id.id)
        if categ_ids:
            result = []
            cabecera = ['DEPARTAMENTO']
            for categ_id in categ_ids:
                categoria = categ_obj.browse(self.cr, self.uid, categ_id)
                cabecera.append(categoria.name)
            result.append(cabecera)
            result.append([''])
            if this.valor=='Adquisicion':
                for dept_id in dept_ids:
                    linea = []
                    departamento = dept_obj.browse(self.cr, self.uid, dept_id)
                    linea = [departamento.name]
                    for categ_id in categ_ids:
                        aux_valor = 0
                        #entre fechas
                        if this.opc:
                            if this.date_start:
                                if this.opc2=='Operativos':
                                    asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                     ('purchase_date','>=',this.date_start),('purchase_date','<=',this.date_stop),
                                                                                     ('state','in',('open','close'))])
                                else:
                                    asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                     ('purchase_date','>=',this.date_start),('purchase_date','<=',this.date_stop)])
                            else:
                                if this.opc2=='Operativos':
                                    asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                     ('purchase_date','<=',this.date_stop),('state','in',('open','close'))])
                                else:
                                    asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                 ('purchase_date','<=',this.date_stop)])
                        else:
                            if this.opc2=='Operativos':
                                asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                 ('state','in',('open','close'))])
                            else:
                                asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id)])
                        if asset_ids:
                            for asset_id in asset_ids:
                                asset = asset_obj.browse(self.cr, self.uid, asset_id)
                                if this.opc2=='Operativos':
                                    if asset.state=='open':
                                        aux_valor += asset.purchase_value
                                    elif asset.state=='close':
                                        if asset.baja_date:
                                            if asset.baja_date>this.date_stop:
                                                aux_valor += asset.purchase_value
                                else:
                                    aux_valor += asset.purchase_value
                        linea.append(aux_valor)
                        if categ_id in categ_valor:
                            categ_valor[categ_id] += aux_valor
                        else:
                            categ_valor[categ_id] = aux_valor#0
                    result.append(linea)
                    result.append([''])
            else:
                for dept_id in dept_ids:
                    linea = []
                    departamento = dept_obj.browse(self.cr, self.uid, dept_id)
                    linea = [departamento.name]
                    for categ_id in categ_ids:
                        aux_valor = 0
                        if this.opc:
                            if this.date_start:
                                if this.opc2=='Operativos':
                                    asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                     ('purchase_date','>=',this.date_start),('purchase_date','<=',this.date_stop),
                                                                                     ('state','in',('open','close'))])
                                else:
                                    asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                     ('purchase_date','>=',this.date_start),('purchase_date','<=',this.date_stop)])
                            else:
                                if this.opc2=='Operativos':
                                    asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                     ('purchase_date','<=',this.date_stop),('state','in',('open','close'))
                                                                                 ])
                                else:
                                    asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                     ('purchase_date','<=',this.date_stop)])
                        else:
                            if this.opc2=='Operativos':
                                asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id),
                                                                                 ('state','in',('open','close'))])
                            else:
                                asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','=',dept_id),('category_id','=',categ_id)])
                        if asset_ids:
                            for asset_id in asset_ids:
                                asset = asset_obj.browse(self.cr, self.uid, asset_id)
                                if this.opc2=='Operativos':
                                    if asset.state=='open':
                                        aux_valor += asset.purchase_value
                                    elif asset.state=='close':
                                        if asset.baja_date:
                                            if asset.baja_date>this.date_stop:
                                                aux_valor += asset.purchase_value
                                else:
                                    aux_valor += asset.purchase_value
                        linea.append(aux_valor)
                        if categ_id in categ_valor:
                            categ_valor[categ_id] += aux_valor
                        else:
                            categ_valor[categ_id] = aux_valor#0
                    result.append(linea)
                    result.append([''])
            total = ['TOTAL']
            for c_v in categ_valor:
                total.append(categ_valor[c_v])
            result.append(total)
        return result

       
report_sxw.report_sxw('report.activo_valorado',
                       'departamento.valor', 
                       'addons/gt_account_asset/report/activo_valorado.mako',
                       parser=activo_valorado,
                       header=False)

