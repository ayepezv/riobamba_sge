# -*- coding: utf-8 -*-
##############################################################################
#    Autor
#    Mario Chogllo
#
##############################################################################

from osv import osv, fields

class partnerSiim(osv.Model):
    _inherit = 'res.partner'

    def create(self, cr, uid, vals, context=None):
        partner_obj = self.pool.get('res.partner')
        direccion_obj = self.pool.get('res.partner.address')
        if vals.has_key('direccion'):
            direccion = vals['direccion']
        else:
            direccion = ''
        if vals.has_key('telefono'):
            phone = vals['telefono']
        else:
            phone = ''
        if vals.has_key('email'):
            mail = vals['email']
        else:
            mail = ""
        id_creado = super(partnerSiim, self).create(cr, uid, vals, context=None)
        id_dir = direccion_obj.create(cr, uid, {
            'type':'default',
            'active':True,
            'partner_id':id_creado,
            'street':direccion,
            'phone':phone,
            'email': mail,
        })
        return id_creado
    
    _columns = dict(
        direccion = fields.char('Direccion',size=256,required=True),
        telefono = fields.char('Telefono',size=10,required=True),
        pagar_spi = fields.boolean('Pagar SPI con cedula?',help="Marcar este campo si el SPI genera con la cedula como identificador"),
        nombre_comercial = fields.char('Nombre Comercial',size=128),
        email2 = fields.char('Email',size=128),
        )
    _defaults = dict(
        supplier = True,
        email = 'info@gmail.com',
    )
partnerSiim()

