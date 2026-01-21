# -*- coding: utf-8 -*-
#
# mario chogllo

from osv import osv, fields

class resCountryStateCanton(osv.osv):
    _name = 'res.country.state.canton'
    _description = 'Cantones'
    _order = 'state_id asc, name asc'
    _columns = dict(
        country_id =  fields.many2one('res.country', 'País', required=True),       
        state_id =  fields.many2one('res.country.state', 'Provincia/Estado', required=True),
        name =  fields.char('Cantón', size=64, required=True),
        code = fields.char('Código',size=5),
    )
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.state_id.name + ' / ' +  record.name
            res.append((record.id, name))
        return res

resCountryStateCanton()


class resCountryStateCity(osv.osv):
    _name = 'res.country.state.city'
    _description = 'Ciudades'
    _order = 'state_id asc, name asc'
    _columns = dict(
        country_id =  fields.many2one('res.country', 'País', required=True),       
        state_id =  fields.many2one('res.country.state', 'Provincia/Estado', required=True),
	    #canton_id = fields.many2one('res.country.state.canton', 'Cantón', required=True),
        name = fields.char('Ciudad', size=64, required=True),
        code = fields.char('Código',size=5),
    )
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.state_id.name + ' / ' +  record.name
            res.append((record.id, name))
        return res

resCountryStateCity()

class resCountryStateParish(osv.osv):
    _name = 'res.country.state.parish'
    _description = 'Parroquias'
    _order = 'state_id asc, canton_id asc, name asc'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            if record.code:
                name = record.code + ' / ' +  record.name
            else:
                name = record.name
            res.append((record.id, name))
        return res

    _columns = dict(
        country_id =  fields.many2one('res.country', 'País', required=True),       
        state_id =  fields.many2one('res.country.state', 'Provincia/Estado', required=True),
	canton_id = fields.many2one('res.country.state.canton', 'Cantón', required=True),
        name =  fields.char('Parroquia', size=64, required=True),
        code = fields.char('Código',size=5),
    )

resCountryStateParish()



