# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
##############################################################################

{
    "name": "gt_asistencia",
    "version": "1.1",
    "author": "Mario Chogllo",
    "category": "HR",
    "sequence": 12,
    'complexity': "easy",
    "website": "http://www.mariofchogllo@gmail.com",
    "description": """
Gestion de horas de ingreso y salida de empleados
=====================================
Permite manejar:
    * Gestión de horas de ingreso y salida de empleados en base a horarios.
    * Generación de sanciones.
    * Envio de correos, y notificaciones de sanciones
    """,
    'author': 'Mario Chogllo',
    'images': [],
    'depends': ['gt_hr_base','hr_attendance',],
    'init_xml': [],
    'update_xml': [        
        'report/asistencia_report.xml',
        'asistencia_view.xml',
       # 'view/gt_gpa_workflow.xml',
        'asistencia_task.xml',
        'security/asistencia_security.xml',
        'security/ir.model.access.csv',     
        'reports_view.xml',  
        'report/report_summary_assistance_view.xml',
    ],
    'demo_xml': [],
    'test': [
             ],
    'installable': True,
}

