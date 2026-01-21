# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

import netsvc

from osv import fields, osv
from tools import ustr
class wizardLoadRetention(osv.TransientModel):
    _name = 'wizard.load.retention'

    def load_retention(self, cr, uid, ids, context):
        digital_obj = self.pool.get('digital.retention')
        parameter_obj = self.pool.get('ir.config_parameter')
        carpetaRE_ids = parameter_obj.search(cr, uid, [('key','=','RE')],limit=1)
        if carpetaRE_ids:
            carpetaRE = parameter_obj.browse(cr, uid, carpetaRE_ids[0]).value
        else:
            raise osv.except_osv('Error','No ha configurado la carpeta para retenciones autorizadas.')
        data = self.read(cr, uid, ids[0])
        texto_file = open(carpetaRE+'/auxiliarXML/'+data['datas_fname'], 'r')
        texto = texto_file.read()
        #validar que corresponde a la retencion
        ##
        l = texto.find('numeroAutorizacion')
        aux_aut = texto[l+19:l+19+37]
        m = texto.find('claveAcceso')
        aux_clave = texto[m+12:m+12+49]
        aux_clave = aux_clave[0:]
        text_new = 'RECIBIDA' + '\n' + 'AUTORIZADO' + '\n' + 'PRODUCCION' + '\n' + ustr(aux_clave) + '\n' + ustr(aux_aut)
        digital_obj.write(cr, uid, context['active_id'],{
            'autorizacion':aux_aut,
            'state': 'autorizado',
            'state_email': 'enviado',
            'pdf': data['dataspdf'],
            'fnpdf': data['dataspdf_fname'],
            'xml': data['datas'],
            'fnxml': data['datas_fname'],
            'log': text_new,
        })
        return True
            

    _columns = dict(
        dataspdf = fields.binary('Archivo PDF', required=True),
        dataspdf_fname = fields.char('Nombre archivo', size=32),
        datas = fields.binary('Archivo XML', required=True),
        datas_fname = fields.char('Nombre archivo', size=32),
        name = fields.char('Load',size=32),
    )

wizardLoadRetention()

