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

import time
from osv import fields, osv

class bsc_formulation(osv.osv):
    _name = 'bsc.formulation'
    _description = 'BSC - Formulación'
    
    def _calculate_mision_indicador1(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            for eje in line.mision_strategies:
                contador = contador + 1
                valor = valor + eje.bsc_indicador1
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_mision_indicador2(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            for eje in line.mision_strategies:
                contador = contador + 1
                valor = valor + eje.bsc_indicador2
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_vision_indicador1(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            for eje in line.vision_strategies:
                contador = contador + 1
                valor = valor + eje.bsc_indicador1
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_vision_indicador2(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            for eje in line.vision_strategies:
                contador = contador + 1
                valor = valor + eje.bsc_indicador2
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_politica_indicador1(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            for eje in line.politica_strategies:
                contador = contador + 1
                valor = valor + eje.bsc_indicador1
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_politica_indicador2(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            for eje in line.politica_strategies:
                contador = contador + 1
                valor = valor + eje.bsc_indicador2
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_general_indicador1(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            obj_project = self.pool.get('project.project')
            project_ids = obj_project.search(cr, uid, [])
            for proyecto in obj_project.browse(cr, uid, project_ids):
                contador = contador + 1
                valor = valor + proyecto.activity_progress
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_general_indicador2(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            obj_project = self.pool.get('project.project')
            project_ids = obj_project.search(cr, uid, [])
            for proyecto in obj_project.browse(cr, uid, project_ids):
                contador = contador + 1
                valor = valor + proyecto.compliance
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    _columns = {
                'name': fields.char('Descripción',size=50,required=True),
                'fy_id': fields.many2one('account.fiscalyear', string='Ejercicio Fiscal', required=True),
                'mision': fields.text('Misión', required=True),
                'vision': fields.text('Visión', required=True),
                'politica': fields.text('Política de calidad', required=True),
                #'mision_projects':fields.many2many('project.project','bsc_mision_project','mision_id','project_id','Proyectos de misión'),
                #'vision_projects':fields.many2many('project.project','bsc_vision_project','vision_id','project_id','Proyectos de visión'),
                #'politica_projects':fields.many2many('project.project','bsc_politica_project','politica_id','project_id','Proyectos de política de calidad'),
                'mision_strategies':fields.many2many('project.estrategy','bsc_mision_strategies','mision_id','axis_id','Estrategias de misión'),
                'vision_strategies':fields.many2many('project.estrategy','bsc_vision_strategies','vision_id','axis_id','Estrategias de visión'),
                'politica_strategies':fields.many2many('project.estrategy','bsc_politica_strategies','politica_id','axis_id','Estrategias de política de calidad'),
                #'axis_ids': fields.one2many('bsc.axis','formulation_id','Ejes estratégicos'),
                'mision_indicador1': fields.function(_calculate_mision_indicador1, method=True, type='float', string='Eficacia', store=False),
                'mision_indicador2': fields.function(_calculate_mision_indicador2, method=True, type='float', string='Eficiencia', store=False),
                #eficacia es avance, y eficiencia es cumplimiento
                'vision_indicador1': fields.function(_calculate_vision_indicador1, method=True, type='float', string='Eficacia', store=False),
                'vision_indicador2': fields.function(_calculate_vision_indicador2, method=True, type='float', string='Eficiencia', store=False),
                #indicadores para las politicas de calidad
                'politica_indicador1': fields.function(_calculate_politica_indicador1, method=True, type='float', string='Eficacia', store=False),
                'politica_indicador2': fields.function(_calculate_politica_indicador2, method=True, type='float', string='Eficiencia', store=False),
                #indicadores generales
                'general_indicador1': fields.function(_calculate_general_indicador1, method=True, type='float', string='Eficacia', store=False),
                'general_indicador2': fields.function(_calculate_general_indicador2, method=True, type='float', string='Eficiencia', store=False),
                }
    
    
bsc_formulation()

class bsc_axis(osv.osv):
    _inherit = 'project.axis'
    
    def _calculate_bsc_indicador1(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        obj_project = self.pool.get('project.project')
        for line in self.browse(cr, uid, ids, context=context):
            ids_project = obj_project.search(cr, uid, [('axis_id','=',line.id)])
            contador = 0
            total_indicador1 = total_indicador2 = 0
            for proyecto in obj_project.browse(cr, uid, ids_project, context):
                total_indicador1 = total_indicador1 + proyecto.activity_progress
                contador = contador + 1
            if contador>0:
                res[line.id] = total_indicador1/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_bsc_indicador2(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        obj_project = self.pool.get('project.project')
        for line in self.browse(cr, uid, ids, context=context):
            ids_project = obj_project.search(cr, uid, [('axis_id','=',line.id)])
            contador = 0
            total_indicador1 = total_indicador2 = 0
            for proyecto in obj_project.browse(cr, uid, ids_project, context):
                total_indicador2 = total_indicador2 + proyecto.compliance
                contador = contador + 1
            if contador>0:
                res[line.id] = total_indicador2/contador
            else:
                res[line.id] = 0
        return res
    
    _columns = {
                'bsc_indicador1': fields.function(_calculate_bsc_indicador1, method=True, type='float', string='Eficacia', store=False),
                'bsc_indicador2': fields.function(_calculate_bsc_indicador2, method=True, type='float', string='Eficiencia', store=False),
                'projects': fields.one2many('project.project','axis_id','Proyectos'),
                }
    
bsc_axis()

class bsc_strategy(osv.osv):
    _inherit = 'project.estrategy'
    
    def _calculate_bsc_indicador1(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        obj_project = self.pool.get('project.project')
        for line in self.browse(cr, uid, ids, context=context):
            ids_project = obj_project.search(cr, uid, [('estrategy_id','=',line.id)])
            contador = 0
            total_indicador1 = total_indicador2 = 0
            if ids_project:
              for proyecto in obj_project.browse(cr, uid, ids_project, context):
                total_indicador1 = total_indicador1 + proyecto.activity_progress
                contador = contador + 1
            if contador>0:
                res[line.id] = total_indicador1/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_bsc_indicador2(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        obj_project = self.pool.get('project.project')
        for line in self.browse(cr, uid, ids, context=context):
            ids_project = obj_project.search(cr, uid, [('estrategy_id','=',line.id)])
            contador = 0
            total_indicador1 = total_indicador2 = 0
            if ids_project:
              for proyecto in obj_project.browse(cr, uid, ids_project, context):
                total_indicador2 = total_indicador2 + proyecto.compliance
                contador = contador + 1
            if contador>0:
                res[line.id] = total_indicador2/contador
            else:
                res[line.id] = 0
        return res
    
    _columns = {
                'bsc_indicador1': fields.function(_calculate_bsc_indicador1, method=True, type='float', string='Eficacia', store=False),
                'bsc_indicador2': fields.function(_calculate_bsc_indicador2, method=True, type='float', string='Eficiencia', store=False),
                'projects': fields.one2many('project.project','estrategy_id','Proyectos'),
                }
    
bsc_strategy()

class bsc_indicador_detalle(osv.osv):
    _name = 'bsc.indicador.detalle'
    _description ="BSC - Detalle de indicadores para perspectivas"
    
    def _validar_meta_mayor_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.valor_meta <= 0:
            return False
        return True
    
    def _validar_real_mayor_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.valor_real < 0:
            return False
        return True
    
    _columns = {
                'name': fields.char('Período', size=32, required=True),
                'valor_meta': fields.float('Valor meta'),
                'valor_real': fields.float('Valor real'),
                #'variacion': fields.float('Variación'),
                'indicador_id': fields.many2one('bsc.indicador','Línea de indicador'),
                }
    
    _constraints = [
                    (_validar_meta_mayor_cero, 'La meta debe ser mayor a cero', ['valor_meta']),
                    (_validar_real_mayor_cero, 'El real debe ser mayor o igual a cero', ['valor_meta']),
                    ]
    
bsc_indicador_detalle()

class bsc_indicador(osv.osv):
    _name = 'bsc.indicador'
    _description ="BSC - Indicadores para perspectivas"
    
    def _calculate_total(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        #obj_project = self.pool.get('project.project')
        for line in self.browse(cr, uid, ids, context=context):
            #ids_project = obj_project.search(cr, uid, [('estrategy_id','=',line.id)])
            contador = 0
            total = 0
            for detalle in line.detalle_ids:
                total = total + (detalle.valor_real*100/detalle.valor_meta)
                contador = contador + 1
            if contador>0:
                res[line.id] = total/contador
            else:
                res[line.id] = 0
        return res
    
    _columns = {
                'name': fields.char('Indicador', size=128, required=True),
                #'date_start': fields.date('Fecha inicial', required=True),
                #'date_stop': fields.date('Fecha final', required=True),
                'perspectiva1_id': fields.many2one('bsc.perspectiva', 'Perspectiva Eficacia', ondelete="cascade"),
                'perspectiva2_id': fields.many2one('bsc.perspectiva', 'Perspectiva Eficiencia', ondelete="cascade"),
                'total': fields.function(_calculate_total, method=True, type='float', string='Total', store=False),
                'detalle_ids': fields.one2many('bsc.indicador.detalle','indicador_id','Detalle'),
    }

bsc_indicador()

class bsc_perspectiva(osv.Model):
    _name = 'bsc.perspectiva'
    _description = 'BSC - Perspectiva'
    
    def _calculate_indicador1(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            valor_proyectos = 0
            valor_indicadores = 0
            for proyecto in line.projects:
                contador = contador + 1
                valor = valor + proyecto.activity_progress
            for indicador in line.indicadores1:
                contador = contador + 1
                valor = valor + indicador.total
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    def _calculate_indicador2(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            valor = 0
            contador = 0.0
            valor_proyectos = 0
            valor_indicadores = 0
            for proyecto in line.projects:
                contador = contador + 1
                valor = valor + proyecto.compliance
            for indicador in line.indicadores2:
                contador = contador + 1
                valor = valor + indicador.total
            if contador>0:
                res[line.id] = valor/contador
            else:
                res[line.id] = 0
        return res
    
    _columns = {
                'name': fields.char('Perspectiva',size=32,required=True),
                'projects':fields.many2many('project.project','bsc_perspectiva_project','perspectiva_id','project_id','Proyectos de la perspectiva'),
                'indicador1': fields.function(_calculate_indicador1, method=True, type='float', string='Eficacia', store=False),
                'indicador2': fields.function(_calculate_indicador2, method=True, type='float', string='Eficiencia', store=False),
                'indicadores1':fields.one2many('bsc.indicador','perspectiva1_id','Indicadores Eficacia'),
                'indicadores2':fields.one2many('bsc.indicador','perspectiva2_id','Indicadores Eficiencia'),
                }

    def _check_nivel(self, cr, uid, ids, context=None):
        persp_obj = self.pool.get('bsc.perspectiva')
        result = True
        for this in self.browse(cr, uid, ids):
            if this.nivel < 0:
                result=False
            perspectiva_ids =  persp_obj.search(cr, uid, [('nivel','=',this.nivel)])
            if len(perspectiva_ids)>1:
                result=False
        return result

    #_constraints = [
    #    (_check_nivel,'El nivel debe ser >= a 0 y debe ser único',[]),
    #    ] 

    #_sql_constraints = [
    #    ('name', 'unique (name)', 'No puede tener dos perspectivas con el mismo nombre!')
    #    ]

bsc_perspectiva()
