# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

{
    "name" : "Recursos Humanos - Base para Ecuador",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa la funcionalidad base que se debe configurar para que 
   funcione para Ecuador:
       - Empleados
       - Contratos
       - IR SRI: Tipos de deducciones
                 Tabla base de retención
                 Impuesto a la renta contrato
    """,
    "category" : "Human Resources",
    "website" : "http://gnuthink.com",
    "depends" : ['country_ec','gt_tool','hr_payroll', 
                 'gt_project_project','hr_recruitment'],
    "init_xml" : [
        'data/data.xml',
        'data/base_retention.xml',],
    "demo_xml" : [],
    "update_xml" : [
        'security/hr_security.xml',
        'wizard/empleado.xml',
        'sequence.xml',
        'hr_base_view.xml',
        'users_view.xml',
        'employee_view.xml',
        'contract_view.xml',
        'hr_secuence.xml',
        'security/ir.model.access.csv',
        'data/grupo.ocupacional.csv',
        'data/hr.marital.status.csv',
        'report.xml',
        ],
    "installable": True,
}
