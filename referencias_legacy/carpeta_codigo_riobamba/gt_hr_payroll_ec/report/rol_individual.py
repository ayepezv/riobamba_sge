# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from report import report_sxw
from tools import amount_to_text_en
from gt_tool import amount_to_text_ec

class rol_individual(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(rol_individual, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_details_by_rule_category': self.get_details_by_rule_category,
            'get_cta_rol': self.get_cta_rol,
            'get_banco': self.get_banco,
            'get_letras_rol': self.get_letras_rol,
        })

    def get_letras_rol(self, valor):
        letra = amount_to_text_ec.amount_to_text_ec(valor)
        return letra

    def get_cta_rol(self, cedula):
        partner_obj = self.pool.get('res.partner')
        partner_ids = partner_obj.search(self.cr, self.uid, [('ced_ruc','=',cedula)])
        aux = ''
        if partner_ids:
            partner = partner_obj.browse(self.cr, self.uid, partner_ids[0])
            if partner.bank_ids:
                aux = partner.bank_ids[0].acc_number
        return aux

    def get_banco(self, cedula):
        partner_obj = self.pool.get('res.partner')
        partner_ids = partner_obj.search(self.cr, self.uid, [('ced_ruc','=',cedula)])
        aux = ''
        if partner_ids:
            partner = partner_obj.browse(self.cr, self.uid, partner_ids[0])
            if partner.bank_ids:
                aux = partner.bank_ids[0].bank.name
        return aux

    def get_details_by_rule_category(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        rule_cate_obj = self.pool.get('hr.salary.rule.category')

        def get_recursive_parent(rule_categories):
            if not rule_categories:
                return []
            if rule_categories[0].parent_id:
                rule_categories.insert(0, rule_categories[0].parent_id)
                get_recursive_parent(rule_categories)
            return rule_categories

        res = []
        result = {}
        ids = []

        for id in range(len(obj)):
            ids.append(obj[id].id)
        if ids:
            self.cr.execute('''SELECT pl.id, pl.category_id FROM hr_payslip_line as pl \
                LEFT JOIN hr_salary_rule_category AS rc on (pl.category_id = rc.id) \
                WHERE pl.id in %s and rc.code<>'PROV' and rc.name!='Extra Rol' \
                GROUP BY rc.parent_id, pl.sequence, pl.id, pl.category_id \
                ORDER BY pl.sequence, rc.parent_id''',(tuple(ids),))
            for x in self.cr.fetchall():
                result.setdefault(x[1], [])
                result[x[1]].append(x[0])
            for key, value in result.iteritems():
                rule_categories = rule_cate_obj.browse(self.cr, self.uid, [key])
                parents = get_recursive_parent(rule_categories)
                category_total = 0
                for line in payslip_line.browse(self.cr, self.uid, value):
                    category_total += line.total
                level = 0
                for parent in parents:
                    res.append({
                        'rule_category': parent.name,
                        'name': parent.name,
                        'code': parent.code,
                        'level': level,
                        'total': category_total,
                    })
                    level += 1
                for line in payslip_line.browse(self.cr, self.uid, value):
                    res.append({
                        'rule_category': line.name,
                        'name': line.name,
                        'code': line.code,
                        'total': line.total,
                        'level': level
                    })
        return res

report_sxw.report_sxw('report.rol_individual', 'hr.payslip', 'gt_hr_payroll_ec/report/rol_individual.rml', parser=rol_individual, header=True)
