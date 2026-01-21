# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time

from osv import osv
from osv import fields
import base64
import pooler
#from XLSWriter import XLSWriter
import StringIO
import xlrd
from gt_tool import XLSWriter
import netsvc

class userPermiso(osv.TransientModel):
    _name = 'user.permiso'
    _columns = dict(
        activos = fields.boolean('Solo activos'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=128),
    )

    def computeUserRoles(self, cr, uid, ids, context=None):
        writer = XLSWriter.XLSWriter()
        group_obj = self.pool.get('res.groups')
        user_obj = self.pool.get('res.users')
        for this in self.browse(cr, uid, ids):
            lista_grupo = {}
            writer.append(['USUARIOS GRUPOS'])
            group_ids = group_obj.search(cr, uid, [])
            if group_ids:
                lista_aux=['USUARIO']
                for group_id in group_ids:
                    group = group_obj.browse(cr, uid, group_id)
                    lista_grupo[group] = group.name
                    lista_aux.append(group.name)
            writer.append(lista_aux)
            if this.activos:
                user_ids = user_obj.search(cr, uid, [('active','=',True)])
            else:
                user_ids = user_obj.search(cr, uid, [])
            for user_id in user_ids:
                lista_funcionario = lista_grupo
                user = user_obj.browse(cr, uid, user_id)
                lista_aux=[user.login]
                for grupo in lista_grupo:
                    if user in grupo.users:
                        lista_aux.append('SI')
                        lista_funcionario[grupo]='SI'
                    else:
                        lista_aux.append('NO')
                        lista_funcionario[grupo]='NO'
                writer.append(lista_aux)
                #print "SIIIIII", user.name,lista_funcionario
        writer.save("usuariosGrupos.xls")
        out = open("usuariosGrupos.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'usuariosGrupos.xls'})
        #print lista_grupo
        return True
        
    
userPermiso()
    
