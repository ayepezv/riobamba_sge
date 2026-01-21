# -*- coding: utf-8 -*-
##############################################################################

{
    "name": "Archivos ESIGEF",
    "description": """
    Modulo de generacion de archivos ESIGEF.
    Contables:
    * Apertura Inicial
    * Balance de Comprobacion
    * Transferencias
    Presupuestarios:
    * Presupuesto Inicial
    * Cedulas presupuestarias de:
       - Ingresos
       - Gastos
    """,
    "depends": ['gt_budget'],
    "init_xml": [],
    "update_xml": ['esigef_view.xml'],
    "installable": True,
}
