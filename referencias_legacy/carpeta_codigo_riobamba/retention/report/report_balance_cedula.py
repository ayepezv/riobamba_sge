# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################


from report import report_sxw
from osv import osv
import operator
import time
import datetime
import tools
from osv.osv import except_osv
import pdb
from datetime import date, timedelta


class BalanceCedula(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(BalanceCedula, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            'lineas': self.lineas,
         })

    def _vars(self,resumen):
        res = { }          
        begin = self.datas['date_from']
        user=str(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['date_from']
        res['date_end'] = self.datas['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['date_end']
        res['end']=end.upper()
        res['account_ids'] = self.datas['account_ids']
        res['account_ids_with_child'] = self.datas['account_ids_with_child']
        return res 

    def lineas(self, resumen):
        lineas_balance = self.pool.get('balance.line').browse(self.cr, self.uid,self.datas['lineas_balance'])
        lineas_cedula = self.pool.get('cedula.line').browse(self.cr, self.uid, self.datas['lineas_cedula'])
        moves = self.pool.get('account.move').browse(self.cr, self.uid, self.datas['moves'])
        result = {
            'lineas_balance': lineas_balance,
            'lineas_cedula': lineas_cedula,
            'moves': moves,
        }
        return result

report_sxw.report_sxw('report.BalanceCedula','balance.cedula',
                      'addons/retention/report/balance_cedula.mako',
                      parser=BalanceCedula)
