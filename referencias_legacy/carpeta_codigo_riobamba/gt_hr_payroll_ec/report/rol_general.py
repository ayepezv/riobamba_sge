# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-now Gnuthink Software Labs Co. Ltd. (<http://www.gnuthink.com>).
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

from osv import fields, osv
from gt_tool import XLSWriter

class hr_payroll_export(osv.osv_memory):
    _name='hr.payroll.export'
    _columns = {
                'datas':fields.binary('Archivo'),
                'datas_fname':fields.char('Nombre archivo', size=32),
                'payroll_id': fields.many2one('hr.payslip.run','Rol'),
                }
    
    def rol_padre(self, cr, uid, context={}):
        return context.get('active_id')
    
    _defaults = {
                 'payroll_id': rol_padre,
                 }

    def generar_archivo_rol(self, cr, uid, ids, context={}):
        #diccionario.values() devuelve los valores del diccionario
        #diccionario.keys() devuelve las claves o cabeceras del diccionario
        #diccionario.items() devuelve el par (clave,valor) de cada registro del diccionario
        diccionario = {}
        diccionario_totales = {}
        #La estructura de diccionario es, por ejemplo:
        #diccionario = {
        #               'id_departamento': {
        #                                   'nombre_empleado': {
        #                                                       'cedula': cedula_empleado,
        #                                                       'id_rubro': valor,
        #                                                       },
        #                                   },
        #               }
        departamentos = []
        rubros = []
        for registro in self.browse(cr, uid, ids, context):
            for rol_individual in registro.payroll_id.slip_ids:
                for rubro in rol_individual.line_ids:
                    #rubro tiene la informacion (id,secuencia,name)
                    rubros.append([rubro.salary_rule_id.id,rubro.salary_rule_id.sequence,rubro.salary_rule_id.name])
                    #departamentos tiene el par (id,name)
                    departamentos.append([rol_individual.department_id.id,rol_individual.department_id.name])
                    if diccionario.has_key(rol_individual.department_id.id):
                        if diccionario[rol_individual.department_id.id].has_key(rol_individual.employee_id.complete_name):
                            if diccionario[rol_individual.department_id.id][rol_individual.employee_id.complete_name].has_key(rubro.salary_rule_id.id):
                                diccionario[rol_individual.department_id.id][rol_individual.employee_id.complete_name][rubro.salary_rule_id.id] += rubro.amount
                            else:
                                diccionario[rol_individual.department_id.id][rol_individual.employee_id.complete_name][rubro.salary_rule_id.id] = rubro.amount
                        else:
                            diccionario[rol_individual.department_id.id][rol_individual.employee_id.complete_name] = {'cedula': rol_individual.employee_id.name,
                                                                                                                      rubro.salary_rule_id.id: rubro.amount}
                    else:
                        diccionario[rol_individual.department_id.id] = {rol_individual.employee_id.complete_name: {'cedula': rol_individual.employee_id.name,
                                                                                                                   rubro.salary_rule_id.id: rubro.amount}
                                                                        }
        departamentos_clean = []
        for key in departamentos:
            if key not in departamentos_clean:
                departamentos_clean.append(key)
        rubros_clean = []
        for key in rubros:
            if key not in rubros_clean:
                rubros_clean.append(key)
        #resultado = list(resultado.values())
        #resultado.sort()
        departamentos_clean.sort(key=lambda x: x[0])
        rubros_clean.sort(key=lambda x: x[1])
        print departamentos_clean
        print rubros_clean
        print diccionario
        
        #creamos la variable para la escritura en el archivo xls
        writer = XLSWriter.XLSWriter()
        
        cabecera = ['Funcionario']
        pie = {}
        for rubro in rubros_clean:
            cabecera.append(rubro[2])
        writer.append(cabecera)
        #
        for departamento in departamentos_clean:
            linea = [departamento[1]]
            writer.append([''])
            writer.append(linea)
            pie = {}
            for empleado in diccionario[departamento[0]].keys():
                linea = [empleado]
                for rubro in rubros_clean:
                    if not pie.has_key(rubro[0]):
                        pie.update({rubro[0]:0.00})
                    if diccionario[departamento[0]][empleado].has_key(rubro[0]):
                        linea.append(diccionario[departamento[0]][empleado][rubro[0]])
                        pie[rubro[0]] = pie[rubro[0]] + diccionario[departamento[0]][empleado][rubro[0]]
                    else:
                        linea.append(0.00)
                writer.append(linea)
            linea = ['TOTAL']
            for rubro in rubros_clean:
                linea.append(pie[rubro[0]])
            writer.append(linea)
        writer.save("resumen_rol.xls")
        out = open("resumen_rol.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'resumen_rol.xls'})
            
            

hr_payroll_export()
