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

class baja_categoria(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(baja_categoria, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_categories_baja': self.get_categories_baja,
            'get_activos_categoria':self.get_activos_categoria,
        })

    def get_activos_categoria(self, this, categ_id):
        asset_ids = []
        asset_obj = self.pool.get('account.asset.asset')
        for line in this.asset_ids:
            if line.asset_id.category_id.id == categ_id:
                asset_ids.append(line.asset_id.id)
        return asset_obj.browse(self.cr, self.uid,asset_ids)

    def get_categories_baja(self,this):
        categ_ids1 = []
        asset_obj = self.pool.get('account.asset.asset')
        categ_obj = self.pool.get('account.asset.category')
        for line in this.asset_ids:
            if not line.asset_id.category_id.id in categ_ids1:
                categ_ids1.append(line.asset_id.category_id.id)
        return categ_obj.browse(self.cr, self.uid,categ_ids1)
       
report_sxw.report_sxw('report.baja_categoria',
                       'gt.account.asset.baja.masiva', 
                       'addons/gt_account_asset/report/baja_categoria.mako',
                       parser=baja_categoria,
                       header=True)

