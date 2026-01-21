# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
import time
from time import strftime, strptime
import decimal_precision as dp
from osv import osv, fields

class accionRio(osv.Model):
    _order = 'date desc'
    _inherit = 'hr.accion.personal'
    _columns = dict(
        autoridad_id = fields.many2one('hr.employee','Autoridad Suscribe',help='Seleccione la autoridad que suscribe el acto administrativo'),
    )


    
accionRio()
