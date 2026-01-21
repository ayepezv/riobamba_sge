# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2013 Consultoria YarosLab (<http://www.yaroslab.com> - info@yaroslab.com).
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


import time
import calendar
import re

from report import report_sxw

class balance_comprobacion_wizard(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(balance_comprobacion_wizard, self).__init__(cr, uid, name, context=context)
        self.cursor = cr
        self.localcontext.update({
            'time': time,
            'get_cabecera': self.get_cabecera,
            'get_detalle': self.get_detalle,
        })
        self.cr = cr
        self.uid = uid
        self.context = context

    def get_cabecera(self, form):
        result = []
        periodo = form['anio']
        cr = self.cursor

        sql = "SELECT rc.name FROM res_company rc WHERE id=1"

        cr.execute(sql)
        recordset = self.cr.dictfetchall()

        if (len(recordset)>=1):
            for row in recordset:
                result.append({
                    'periodo': periodo,
                    'nombres': row['name'],
                })
        return result

    def get_detalle(self, form):
        cr = self.cursor
        anio = form['anio']

        periodo_anual = "%s" % str(anio)
        anio_fiscal_anterior = int(periodo_anual) - 1


        sql_balance_comprobacion = """
        SELECT c.id AS "account_id",
            c.code AS "codigo",
            c.name AS "nombre_cuenta",
            sum(aml.debit) AS "balance_comprobacion_debe",
            sum(aml.credit) AS "balance_comprobacion_haber"
        FROM account_account AS c
            LEFT JOIN account_move_line AS aml ON (c.id = aml.account_id)
            LEFT JOIN account_fiscalyear AS af ON (c.create_uid = af.create_uid)
        WHERE af.name = '%s' AND c.id != '%s' AND c.code NOT LIKE '%s'
        GROUP BY c.id
        ORDER BY c.code
        """

        sql_balance_saldo_inicial = """
        SELECT c.id AS "account_id",
            c.code AS "codigo",
            c.name AS "nombre_cuenta",
            sum(aml.debit) AS "periodo_anterior_debe",
            sum(aml.credit) AS "periodo_anterior_haber"
        FROM account_account AS c
            INNER JOIN account_move_line AS aml ON (c.id = aml.account_id)
            INNER JOIN account_fiscalyear AS af ON (c.create_uid = af.create_uid)
        WHERE af.name = '%s' AND c.id != '%s' AND c.code NOT LIKE '%s'
        GROUP BY c.id
        ORDER BY c.code
        """

        # Obtención de Datos - Balance de Comprobación
        cr.execute(sql_balance_comprobacion % (periodo_anual, '1', '0%'))
        recordset_balance_comprobacion = self.cr.dictfetchall()

        # Obtención de Datos - Saldo Inicial
        cr.execute(sql_balance_saldo_inicial % (anio_fiscal_anterior, '1', '0%'))
        recordset_balance_saldo_inicial = self.cr.dictfetchall()


        result_balance_comprobacion = []
        result_balance_comprobacion_totales = []

        campos_balance_debe = campos_balance_haber = 0.0
        saldo_inicial_debe = saldo_inicial_haber = 0.0

        for campo in recordset_balance_comprobacion:

            if campo.has_key('account_id') and campo['account_id'] != '-':

                campos_balance_debe = campo['balance_comprobacion_debe']
                campos_balance_haber = campo['balance_comprobacion_haber']

                if campos_balance_haber is None:
                    campos_balance_haber = 0.0

                if campos_balance_debe is None:
                    campos_balance_debe = 0.0

                for campo_inicial in recordset_balance_saldo_inicial:
                    if campo_inicial['account_id'] == campo['account_id']:
                        saldo_inicial_debe = float(campo_inicial['periodo_anterior_debe'])

                    if campo_inicial['account_id'] == campo['account_id']:
                        saldo_inicial_haber = float(campo_inicial['periodo_anterior_haber'])


                if re.match("6.", campo['codigo']):
                    saldo_inicial_debe = saldo_inicial_haber = 0.0



                suma_mayor_debe = saldo_inicial_debe + campos_balance_debe
                suma_mayor_haber = saldo_inicial_haber + campos_balance_haber


                saldos_mayor_debe = saldos_mayor_haber = 0.0
                resultados_naturaleza_debe = resultados_naturaleza_haber = 0.0
                cuentas_balance_debe = cuentas_balance_haber = 0.0
                
                
                if (suma_mayor_debe - suma_mayor_haber) >= 0:
                    saldos_mayor_debe = suma_mayor_debe - suma_mayor_haber
                else:
                    saldos_mayor_haber = -(suma_mayor_debe) + suma_mayor_haber

                transferencia_cancelaciones_debe = transferencia_cancelaciones_haber = 0.0

                if re.match("6.", campo['codigo']):

                    if ((saldos_mayor_debe - saldos_mayor_haber) + (transferencia_cancelaciones_debe - transferencia_cancelaciones_haber)) >= 0:
                        resultados_naturaleza_debe = (saldos_mayor_debe - saldos_mayor_haber) + (transferencia_cancelaciones_debe - transferencia_cancelaciones_haber)
                    else:
                        resultados_naturaleza_haber = -((saldos_mayor_debe - saldos_mayor_haber) + (transferencia_cancelaciones_debe - transferencia_cancelaciones_haber))

                else:
                    if ((saldos_mayor_debe - saldos_mayor_haber) + (transferencia_cancelaciones_debe - transferencia_cancelaciones_haber)) >= 0:
                        cuentas_balance_debe = (saldos_mayor_debe - saldos_mayor_haber) + (transferencia_cancelaciones_debe - transferencia_cancelaciones_haber)
                    else:
                        cuentas_balance_haber = -((saldos_mayor_debe - saldos_mayor_haber) + (transferencia_cancelaciones_debe - transferencia_cancelaciones_haber))



            result_balance_comprobacion.append({
                'account_id': (campo['account_id']) if campo.has_key('account_id') else '-',
                'codigo': (campo['codigo']) if campo.has_key('codigo') else '-',
                'nombre_cuenta': (campo['nombre_cuenta']) if campo.has_key('nombre_cuenta') else '-',
                'saldo_inicial_debe': saldo_inicial_debe,
                'saldo_inicial_haber': saldo_inicial_haber,
                'campos_balance_debe': campos_balance_debe if campos_balance_debe else '0.0',
                'campos_balance_haber': campos_balance_haber if campos_balance_haber else '0.0',
                'suma_mayor_debe': suma_mayor_debe,
                'suma_mayor_haber': suma_mayor_haber,
                'saldos_mayor_debe': saldos_mayor_debe,
                'saldos_mayor_haber': saldos_mayor_haber,
                'transferencia_cancelaciones_debe': transferencia_cancelaciones_debe,
                'transferencia_cancelaciones_haber': transferencia_cancelaciones_haber,
                'cuentas_balance_debe': cuentas_balance_debe,
                'cuentas_balance_haber': cuentas_balance_haber,
                'resultados_naturaleza_debe': resultados_naturaleza_debe,
                'resultados_naturaleza_haber': resultados_naturaleza_haber,
                })

        total_saldo_inicial_debe = total_saldo_inicial_haber = 0.0
        total_campos_balance_debe = total_campos_balance_haber = 0.0
        total_suma_mayor_debe = total_suma_mayor_haber = 0.0
        total_saldos_mayor_debe =  total_saldos_mayor_haber = 0.0
        total_transferencia_cancelaciones_debe = total_transferencia_cancelaciones_haber = 0.0
        total_cuentas_balance_debe = total_cuentas_balance_haber = 0.0
        total_resultados_naturaleza_debe = total_resultados_naturaleza_haber = 0.0


        for campos in result_balance_comprobacion:
            total_saldo_inicial_debe += float(campos['saldo_inicial_debe'])
            total_saldo_inicial_haber += float(campos['saldo_inicial_haber'])
            total_campos_balance_debe += float(campos['campos_balance_debe'])
            total_campos_balance_haber += float(campos['campos_balance_haber'])
            total_suma_mayor_debe += float(campos['suma_mayor_debe'])
            total_suma_mayor_haber += float(campos['suma_mayor_haber'])
            total_saldos_mayor_debe += float(campos['saldos_mayor_debe'])
            total_saldos_mayor_haber += float(campos['saldos_mayor_haber'])
            total_transferencia_cancelaciones_debe += float(campos['transferencia_cancelaciones_debe'])
            total_transferencia_cancelaciones_haber += float(campos['transferencia_cancelaciones_haber'])
            total_cuentas_balance_debe += float(campos['cuentas_balance_debe'])
            total_cuentas_balance_haber += float(campos['cuentas_balance_haber'])
            total_resultados_naturaleza_debe += float(campos['resultados_naturaleza_debe'])
            total_resultados_naturaleza_haber += float(campos['resultados_naturaleza_haber'])

        result_balance_comprobacion_totales.append({
            'detalle': result_balance_comprobacion,
            'total_saldo_inicial_debe': total_saldo_inicial_debe,
            'total_saldo_inicial_haber': total_saldo_inicial_haber,
            'total_campos_balance_debe': total_campos_balance_debe,
            'total_campos_balance_haber': total_campos_balance_haber,
            'total_suma_mayor_debe': total_suma_mayor_debe,
            'total_suma_mayor_haber': total_suma_mayor_haber,
            'total_saldos_mayor_debe': total_saldos_mayor_debe,
            'total_saldos_mayor_haber': total_saldos_mayor_haber,
            'total_transferencia_cancelaciones_debe': total_transferencia_cancelaciones_debe,
            'total_transferencia_cancelaciones_haber': total_transferencia_cancelaciones_haber,
            'total_cuentas_balance_debe': total_cuentas_balance_debe,
            'total_cuentas_balance_haber': total_cuentas_balance_haber,
            'total_resultados_naturaleza_debe': total_resultados_naturaleza_debe,
            'total_resultados_naturaleza_haber': total_resultados_naturaleza_haber,
            })


        return result_balance_comprobacion_totales


report_sxw.report_sxw('report.BalanceComprobacion', 'balance.comprobacion', 'addons/gt_account_report/balance_comprobacion/report/balance_comprobacion.rml', parser=balance_comprobacion_wizard, header=False)
