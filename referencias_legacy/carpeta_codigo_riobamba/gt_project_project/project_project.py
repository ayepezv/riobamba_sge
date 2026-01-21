# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

__author__ = 'Mario Chogllo'
import base64
import xlrd
from lxml import etree
import time
import logging
from datetime import datetime

from osv import osv, fields
from tools.translate import _
from tools import ustr

def strToDate(dt):
        if not dt:
                dt = time.strftime('%Y-%m%d')
        dt_date=datetime(int(dt[0:4]),int(dt[5:7]),int(dt[8:10]))
        return dt_date


class ProjectConfiguration(osv.Model):
    _name = 'project.configuration'
    _description = 'Project Configuration'

    def update_budget_codes(self, cr, uid, ids, context=None):
        project_obj = self.pool.get('project.project')
        cross_obj = self.pool.get('budget.item')
        for obj in self.browse(cr, uid, ids, context):
            proj_ids = project_obj.search(cr, uid, [
                ('fy_id', '=', obj.fiscalyear_plan_id.id),
                ('state', 'in', ['exec', 'replaning'])])
            for project in project_obj.browse(cr, uid, proj_ids):
                task_num = 0
                for task in project.tasks:
                    task_num += 1
                    for bud in task.budget_planned_ids:
                         res = cross_obj.search(cr, uid, [('analytic_account_id','=',bud.acc_budget_id.id),('task_id','=',task.id)])
                         code = '%s.%s.%s' % (project.code,str(task_num).zfill(3),bud.acc_budget_id.code)
                         print code, res
                         cross_obj.write(cr, uid, res, {'code': code})
        return True

    def onchange_vars(self, cr, uid, ids, scope, time, budget):
        res = {'value': {}}
        if scope+time+budget > 100:
            res = {
                'warning': {
                    'title': 'Error de Datos',
                    'message': 'Debe sumar 100 entre las variables.'
                    },
                'value': {
                    'scope': 0,
                    'time': 0,
                    'budget': 0
                    }
                }
            return res
        return res

    def _get_fy(self, cr, uid, context=None):
        fy_id = self.pool.get('account.fiscalyear').find(cr, uid)
        return fy_id

    def get_ranges(self, cr, uid):
        res = False
        fy_id = self._get_fy(cr, uid)
        res_ids = self.search(cr, uid, [('active','=',True),('fiscalyear_id','=',fy_id)])
        if res_ids:
            data = self.read(cr, uid, res_ids[0], ['red_start','red_end','yel_start','yel_end','blue_start','blue_end'])
            res = {'red': [data['red_start'],data['red_end']],
                   'orange': [data['yel_start'],data['yel_end']],
                   'blue': [data['blue_start'],data['blue_end']]}
        return res

    def action_update_projects(self, cr, uid, ids, context=None):
        project_obj = self.pool.get('project.project')
        for obj in self.browse(cr, uid, ids, context):
            project_ids = project_obj.search(cr, uid, [('fy_id','=',obj.fiscalyear_id.id),('state','=','exec')])
            if not project_ids:
                return True
            project_obj.update_projects(cr, uid, project_ids, context)
        return True
            
    _columns = {
        'scope': fields.float('Peso de Ambito (%)'),
        'time': fields.float('Peso de Tiempo  (%)'),
        'budget': fields.float('Peso de Presupuesto (%)'),
        'active': fields.boolean('Activo ?'),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Ejercicio Fiscal', required=True, select=True),
        'red_start': fields.integer('Rojo'),
        'red_end': fields.integer('Fin Rojo'),
        'yel_start': fields.integer('Naranja'),
        'yel_end': fields.integer('Fin Naranja'),
        'blue_start': fields.integer('Azul'),
        'blue_end': fields.integer('Azul'),
        'fiscalyear_exec_id': fields.many2one('account.fiscalyear', 'Año Fiscal Ejecución', required=True),
        'fiscalyear_plan_id': fields.many2one('account.fiscalyear', 'Año Fiscal Planificación', required=True),
        }

    def get_active(self, cr, uid, fy_id):
        cr.execute("select id from project_configuration where fiscalyear_id=%s" % fy_id)
        res = cr.fetchone()
        return res

    def _check_vars(self, cr, uid, ids):
        for obj in self.browse(cr, uid, ids):
            if obj.scope + obj.time + obj.budget != 100:
                return False
        return True

    def _check_active(self, cr, uid, ids):
        """
        Metodo que verifica que exista solo
        un registro activo de configuracion
        """
        count = 0
        for obj in self.browse(cr, uid, ids):
            if obj.active and count > 0:
                return False
            count += 1
        return True

    _constraints = [(_check_vars,'Las variables no suman el valor de 100.', ['Variables']),
                    (_check_active, 'Sólo debe existir un registro activo.', ['Registro activo'])]
    _sql_constraints = [('unique_vars_fy', 'unique(active,fiscalyear_id)', u'No puede ingresar más de un registro activo por ejercicio fiscal.')]

    _defaults = dict(
        scope = 30,
        time = 20,
        budget = 50,
        active = True,
        fiscalyear_id = _get_fy,
        )    


class ProjectAxis(osv.Model):

    _name = 'project.axis'
    _description = 'Ejes Estrategicos/Componentes'

    _columns = dict(
        name = fields.char('Componente', size=64, required=True),
        legal_base = fields.text('Objetivo'),
        active = fields.boolean('Activo'),
        )

    _defaults = {
        'active': True,
        }

class ProjectProgram(osv.Model):

    _name = 'project.program'
    _description = 'Buscar Programas'

    def name_search(self, cr, uid, name='', args=[], operator='ilike',
                    context=None, limit=100):
        ids = []
        ids = self.search(cr, uid,
                          [('name', operator, name)] + args,
                          context=context, limit=limit)
        if not ids:
            ids = set()
            ids.update(self.search(cr, uid,
                                   args + [('sequence', operator, name)],
                                   limit=limit, context=context))
        ids = list(ids)
        return self.name_get(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            if record.name:
                name = record.sequence + ' ' + record.name
            res.append((record.id, name))
        return res
    

    def onchange_estrategy(self, cr, uid, ids, estrategy_id):
        """
        Metodo que devuelve el eje segun la estrategia seleccionada
        """
        res = {'value': {'axis_id': ''}}
        if estrategy_id:
            estrat = self.pool.get('project.estrategy').read(cr, uid, estrategy_id, ['axis_id'])
            res['value']['axis_id'] = estrat['axis_id']
        return res
        
    def _get_codefuncion(self, cr, uid, ids, name, args, context=None):
        res = {}
        for programa in self.browse(cr, uid, ids):
            if programa.sequence:
                res[programa.id] = programa.sequence[0:1]
        return res

    _columns = dict(
        funcion = fields.function(_get_codefuncion, store=True, string='Funcion',type='char',size=1),    
        sequence = fields.char('Código', size=32, required=True),
        name = fields.char('Programa', size=128, required=True),
        estrategy_id = fields.many2one('project.estrategy',
                                  string='Política pública',
                                  required=True),
        axis_id = fields.related('estrategy_id', 'axis_id', relation='project.axis',
                                 type='many2one', string='Componente',
                                 readonly=True, store=True),
        description = fields.text('Descripción'),
        active = fields.boolean('Activo'),
        )

    _defaults = {
        'active': True,
        }


class ProjectTask(osv.Model):

    _inherit = 'project.task'
    __logger = logging.getLogger(_inherit)    

    def loadPresupuesto(self, cr, uid, ids, context=None):
        item_obj = self.pool.get('budget.item')
        post_obj = self.pool.get('budget.post')
        for this in self.browse(cr, uid, ids):
            arch = this.datas
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            for r in range(sh.nrows)[1:]:
                aux_code1 = str(sh.cell(r,0).value).replace(' ','')
                aux_code = aux_code1.replace('.','')
                aux_name = sh.cell(r,1).value
                aux_valor = sh.cell(r,2).value
                if aux_valor:
                        print "LINEAAA", r, aux_code
                        post_ids = post_obj.search(cr, uid, [('code','=',aux_code)])
                        code_parent = aux_code[0:6] 
                        parent_ids = post_obj.search(cr, uid, [('code','=',code_parent)])
                        if parent_ids:
                                parent_id = parent_ids[0]
                        else:
                                code_parent = aux_code[0:4] 
                                parent_ids = post_obj.search(cr, uid, [('code','=',code_parent)])
                                if parent_ids:
                                        parent_id = parent_ids[0]
                        if post_ids:
                                post_id = post_ids[0]
                                post_obj.write(cr, uid, post_id,{'name':aux_name})
                        else:
                                print "VRGGGGGGGGGGGGGGGGGGG", aux_code
                                post_id = post_obj.create(cr, uid, {
                                        'code':aux_code,
                                        'code_aux':aux_code,
                                        'name':aux_name,
                                        'internal_type':'gasto',
                                        'budget_type_id':7,
                                        'parent_id':parent_id,
                                })
                        item_ids = item_obj.search(cr, uid,[('budget_post_id','=',post_id),('task_id','=',this.id)])
                        if item_ids:
                                item_obj.write(cr, uid, item_ids,{'planned_amount':aux_valor})
                        else:
                                item_obj.create(cr, uid, {
                                        'budget_post_id':post_id,
                                        'task_id':this.id,
                                        'planned_amount':aux_valor,
                                })
        return True    

    def duplicate_task(self, cr, uid, map_ids, context=None):
        return True

    def create(self, cr, uid, vals, context=None):
        """
        Redefinición del metodo para asegurar los periodos de planificacion
        return: ID object created
        """
        data = self.pool.get('project.project').read(cr, uid, vals['project_id'], ['fy_id'])
        if not vals.get('expense_planned_ids'):
            vals.update(self.onchange_fy(cr, uid, [], data['fy_id'][0])['value'])
        res_id = super(ProjectTask, self).create(cr, uid, vals, context)
        return res_id

    def action_create_budget(self, cr, uid, ids, context=None):
        """
        Metodo que devuelve un asistente para crear un presupuesto
        de la actividad
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if context is None:
            context = {}
        for task in self.browse(cr, uid, ids, context):
            result = mod_obj.get_object_reference(cr, uid, 'gt_project_project', 'action_view_budget_task2')
            act_id = result and result[1]
            result = act_obj.read(cr, uid, [act_id], context=context)[0]
            result['domain'] = "[('id','=',%s)]" % task.id
            result['res_id'] = task.id
            return result

    def _amount_planned(self, cr, uid, ids, fields, arg, context):
        """
        Metodo que calcula el monto planificado de la actividad
        return: dict {id: amount, ...}
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'planned_amount': 0, 'commited_amount': 0, 'avai_amount': 0}
            for line in obj.budget_planned_ids:
                res[obj.id]['planned_amount'] += line.planned_amount
                #res[obj.id]['commited_amount'] += line.commited_amount
                #res[obj.id]['avai_amount'] += line.planned_amount - line.commited_amount
        return res

    def _get_task(self, cr, uid, ids, context=None):
        result = {}
        for work in self.pool.get('project.task.work').browse(cr, uid, ids, context=context):
            if work.task_id: result[work.task_id.id] = True
        return result.keys()

    def _get_work(self, cr, uid, ids, context=None):
        result = {}
        for work in self.pool.get('project.kpi.work').browse(cr, uid, ids, context=context):
            if work.task_id: result[work.task_id.id] = True
        return result.keys()    

    def _compute_scope(self, cr, uid, task):
        """
        Calcula el avance de ambito por tarea
        CHECK: si tienes mas de un objetivo ?
        """
        progress = 0
        kpi = False
        for work in task.avance_ids:
            if not kpi:
                kpi = work.kpi_id.id
            if work.kpi_id.id == kpi:
                progress = work.kpi_id.progress
        return progress

    def _hours_get(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        avance_obj = self.pool.get('project.task.avance')
        cr.execute("SELECT task_id, COALESCE(SUM(hours),0) FROM project_task_work WHERE task_id IN %s GROUP BY task_id",(tuple(ids),))
        hours = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = {'effective_hours': hours.get(task.id, 0.0),
                            'total_hours': (task.remaining_hours or 0.0) + hours.get(task.id, 0.0)}
            res[task.id]['delay_hours'] = res[task.id]['total_hours'] - task.planned_hours
            res[task.id]['progress'] = 0.0
            res[task.id]['progress_time'] = 0.00
            res[task.id]['delay_time'] = 0.00
            if (task.remaining_hours + hours.get(task.id, 0.0)):
                res[task.id]['progress'] = round(min(100.0 * hours.get(task.id, 0.0) / res[task.id]['total_hours'], 99.99),2)
            if task.state in ('done','cancelled'):
                res[task.id]['progress'] = 100.0
            """
            progreso: el avance de la tarea a la fecha
            desfaz de la tarea a la fecha
            avance: calculo para registro de avance dentro de los tiempos
            retraso: delay_time: dias de retraso de la fecha de cierre
            """
            av_ids = avance_obj.search(cr, uid, [('task_id','=',task.id)], order='date_done DESC, id DESC', limit=1)
            if av_ids:
                avance = avance_obj.browse(cr, uid, av_ids)[0]
                res[task.id]['progress_time'] = avance.executed
        return res

    def _compute_progress_money(self, cr, uid, ids, fields, args, context):
        res = {}
        import random
        for task in self.browse(cr, uid, ids, context):
            res[task.id] = 0
            progress = 0
#            commited_amount = sum([b.commited_amount for b in task.budget_planned_ids])
#            if task.planned_amount > 0:
#                progress = commited_amount * 100 / task.planned_amount
            res[task.id] = progress
        return res

    def _get_plan(self, cr, uid, ids, context=None):
        result = {}
        for plan in self.pool.get('budget.item').browse(cr, uid, ids, context=context):
            result[plan.task_id.id] = True
        return result.keys()

    def _get_executed(self, cr, uid, ids, context=None):
        result = {}
        for executed in self.pool.get('project.task.avance').browse(cr, uid, ids, context=context):
            result[executed.task_id.id] = True
        return result.keys()

    def check_expense_planned(self, cr, uid, ids):
        """
        Verificar si el gasto planificado es igual
        al presupuesto de la actividad
        return False or True
        """
        for task in self.browse(cr, uid, ids):
            budget = sum([p.amount for p in task.expense_planned_ids])
            if task.project_id.type_budget == 'gasto' and not round(task.planned_amount, 2) == round(budget, 2):
                return True
#                raise osv.except_osv('Error', 'El gasto planificado no es igual al presupuesto de la actividad: %s' % task.name)
        return True

    def get_budget_by_level(self, cr, uid, tasks, consolidate=False):
        """
        Metodo que devuelve el monto presupuestado
        por nivel de cuenta, se implementa dos niveles
        Gasto Corriente, y Gasto de Inversion
        @consolidate: si consolida los totales de actividades
        return res = {taskID: {'nivelID': presupuesto, 'nivelID': presupuesto}}
        """
        acc_obj = self.pool.get('account.analytic.account')
        roof_obj = self.pool.get('budget.roof.line')
        res = {}
        for task in self.browse(cr, uid, tasks):
            limits = roof_obj.get_limits(cr, uid, task.department_id.id, task.fy_id.id)
            totals = {keys_limits[0]: 0, keys_limits[1]: 0}        
            for budget in task.budget_planned_ids:
                account = budget.acc_budget_id.id
                amount = budget.planned_amount
                for k,v in limits.items():
                    if acc_obj.is_child(cr, uid, k, account):
                        totals[k] += amount
            res[task.id] = totals
        return res

    def _read_project_budget(self, cr, uid, ids, fields, args, context):
        """
        Metodo que implementa la lectura del disponible del proyecto
        en la actividad para el campo amont_avai
        return DICT
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = obj.project_id.amount_available
        return res

    def _progress_compliance(self, cr, uid, ids, fields, args, context):
        """
        Metodo que implementa el cumplimento de tiempo y presupuesto
        de las actividades
        plan: % planificado
        No se simplifica el metodo hasta que se compruebe su funcionamiento
        """
        res = {}
        plan_obj = self.pool.get('project.expense.plan')
        for obj in self.browse(cr, uid, ids, context):
            tcom = 0
            bcom = 0
            res[obj.id] = {'tcompliance': 0, 'bcompliance': 0}
            hoy = time.strftime('%Y-%m-%d')
            today = datetime.now()
            date_start = strToDate(obj.date_start)
            date_end = strToDate(obj.date_end)
            dt = (date_end - date_start).days + 1
            dc = (today - date_start).days
            plan = 100.00 * dc / dt
            dp = obj.progress_time * dt / 100
            if obj.date_end >= hoy:
                if obj.progress_time >= plan:
                    tcom = 100
                elif obj.progress_time > 0:
                    tcom = 100 - (plan - obj.progress_time)
            else:
                if obj.progress_time == 100:
                    tcom = 100
                else:
                    t = dt - dp + (today - date_end).days
                    tcom = 100.00 - (t * 100.00 / dt)
            res[obj.id]['tcompliance'] = tcom
            ### Budget compliance stuff
            planned = plan_obj.get_planned(cr, uid, hoy, obj.id)
            progress = 0#sum([b.commited_amount for b in obj.budget_planned_ids])
            p = 0
            if planned == 0 and progress == 0:
                bcom = 0
            elif progress == planned:
                bcom = 100
            elif (progress - planned) > 0:
                bcom = planned * 100.00 / progress
            else:
                p = (planned - progress) * 100.00 / planned
                bcom = 100.00 - p
            res[obj.id]['bcompliance'] = bcom    
            self.__logger.info("Cumplimiento tiempo por actividad %s" % tcom)
            self.__logger.info("Cumplimiento economico por actividad %s" % bcom)            
        return res

    def _get_plan_bud(self, cr, uid, ids, context):
        res = {}
        for obj in self.pool.get('budget.item'):
            res[obj.task_id.id] = True
        return res.keys()

    STORE_VAR = {
        'project.task': (
            lambda self, cr, uid, ids, c={}: ids,
            ['work_ids', 'remaining_hours', 'planned_hours'],
            10
            ),
        'project.task.work': (_get_task, ['hours'], 10),
        'project.task.avance': (_get_executed, ['executed'], 10),
        'budget.item': (
            _get_plan,
            [
                'planned_amount',
                'certified_amount',
                'commited_amount',
                'progress'
            ],
            10
            )
        }

    STORE_PLAN = {
        'project.task': (lambda self, cr, uid, ids, c={}: ids, ['budget_planned_ids'], 10),
        'budget.item': (_get_plan, ['planned_amount','commited_amount','progress'], 10),
        'project.task.avance': (_get_executed, ['executed'], 10)
        }

    STORE_MONEY = {
        'project.task': (lambda self, cr, uid, ids, c={}: ids, ['budget_planned_ids'], 10),
        'budget.item': (_get_plan_bud, ['certified_amount','commited_amount','progress'], 10)
        }
    
    _columns = dict(
        datas = fields.binary('Datos'),
        task_ant = fields.many2one('project.task','Actividad Anterior'),
	poa_id = fields.related('project_id', 'poa_id', type="many2one",relation="budget.poa",
                           string="POA", store=True),
        code = fields.char('Código', size=16, readonly=False),
        name = fields.char('Task Summary', size=256, required=True, select=True),
        tcompliance = fields.function(
            _progress_compliance, method=True, multi='com',
            string='Cumplimiento de Actividades', type='float', store=False
            ),
        bcompliance = fields.function(
            _progress_compliance, method=True, multi='com',
            string='Cumplimiento de Presupuesto',
            type='float', store=False
            ),
        budget_avai = fields.function(
            _read_project_budget, method=True,
            string="Disponible Coordinación/Dirección", store=False
            ),
        date_start = fields.date('Starting Date',select=True),
        date_end = fields.date('Ending Date',select=True),
#        planned_amount = fields.function(_amount_planned, string='Monto Presupuestado', digits=(16,2),
#                                         store=STORE_PLAN, method=True, multi='task'),
        planned_amount = fields.function(_amount_planned, string='Monto Presupuestado', digits=(16,2),
                                         store=True, multi='task'),
        commited_amount = fields.function(_amount_planned, string='Monto Comprometido', digits=(16,2),
                                         store=True, multi='task'),
        avai_amount = fields.function(_amount_planned, string='Disponible', digits=(16,2),
                                         store=True, multi='task'),
#        commited_amount = fields.function(_amount_planned, string='Monto Comprometido', digits=(16,2),
#                                         store=STORE_PLAN, method=True, multi='task'),
#        avai_amount = fields.function(_amount_planned, string='Disponible', digits=(16,2),
#                                         store=STORE_PLAN, method=True, multi='task'),
        budget_planned_ids = fields.one2many('budget.item', 'task_id', string='Planificación Presupuestaria'),
        expense_planned_ids = fields.one2many('project.expense.plan', 'task_id', string='Planificación de Gasto'),
        executed_ids = fields.one2many('project.task.avance', 'task_id', string='Detalle de Avance'),
        weight = fields.integer('Peso (%)', required=True),
        own_type = fields.selection([('project', 'Proyectos Propios'),
                                     ('improve', 'Imprevistos'),
                                     ('income', 'Ingresos por Reforma'),
                                     ('deleted', 'Eliminados por Reforma')],
                                    string="Tipo"),
        department_id = fields.related('project_id', 'department_id', type='many2one',
                                       relation='hr.department', store=True, string="Componente Operativo"),
        fy_id = fields.related('project_id', 'fy_id', type='many2one',
                                relation='account.fiscalyear', string='Ejercicio Fiscal'),
        effective_hours = fields.function(_hours_get, string='Hours Spent', multi='hours', help="Computed using the sum of the task work done.",
                                          store=STORE_VAR),
        total_hours = fields.function(_hours_get, string='Total Hours', multi='hours', help="Computed as: Time Spent + Remaining Time.",
                                      store=STORE_VAR),
        progress = fields.function(_hours_get, string='Progress (%)', multi='hours', group_operator="avg", help="If the task has a progress of 99.99% you should close the task if it's finished or reevaluate the time", store=STORE_VAR),
        delay_hours = fields.function(_hours_get, string='Delay Hours', multi='hours', help="Computed as difference between planned hours by the project manager and the total hours of the task.", store=STORE_VAR),
        progress_time = fields.function(_hours_get, method=True, string="Avance (%)", store=STORE_VAR, multi='hours', group_operator='avg'),
        progress_money2 = fields.function(_compute_progress_money, method=True, string='Avance ($)', store=False),
        delay_time = fields.function(_hours_get, string='Retraso (%)', store=STORE_VAR, multi='hours', group_operator='avg'),
        roof_limit_id = fields.related('project_id', 'roof_limit_id',
                                       type='many2one', relation='budget.roof.line',
                                       store=True, string='Limite presupuestario'),
        )

    def _get_budget_avai(self, cr, uid, context):
        budget = 0
#        if context.get('budget_avai') <= 0:
#            pass
            #raise osv.except_osv('Error', 'No dispone de presupuesto.')
#            raise osv.except_osv('Error', 'No dispone de presupuesto.')
        if context.get('budget_avai'):
            budget = context.get('budget_avai')
        return budget

    def _get_fy_id(self, cr, uid, context=None):
        conf_obj = self.pool.get('project.configuration')
        res = conf_obj.search(cr, uid, [('active','=',True)])
        if not res:
            return False
        data = conf_obj.read(cr, uid, res, ['fiscalyear_plan_id', 'fiscalyear_exec_id'])[0]
        return data['fiscalyear_plan_id'][0]

    def _get_planned_budgets(self, cr, uid, context=None):
        if not context.get('project_type'):
            return {}
        data = self.pool.get('project.type').read(cr, uid, context.get('project_type'), ['budget_ids'])
        vals = [(0,0,{'acc_budget_id': d, 'name': '/', 'planned_amount': 0}) for d in data['budget_ids']]
        return vals

    def _get_plan_expense(self, cr, uid, context=None):
        fy_id = context.get('fy_id')
        pids = []
        period_ids = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=',fy_id),('special','=',False)])
        for p in period_ids:
            pids.append((0,0,{'period_id': p, 'amount': 0}))
        return pids        

    _defaults = dict(
        planned_amount=0,
        own_type='project',
        budget_avai=_get_budget_avai,
        fy_id=_get_fy_id,
        budget_planned_ids = _get_planned_budgets,
        expense_planned_ids = _get_plan_expense
        )    

    def onchange_budget_lines(self, cr, uid, ids, lines, total, available, department_id, fy_id):
        """
        Metodo que implementa la varificacion de presupuestos disponible
        por nivel de partida presupuestaria, el usuario selecciona las partidas
        @lines: lineas de planificacion presupuestaria
        @total: limite presupuestario de la coordinacion
        @available: disponible consolidado de la coordinacion
        @department_id: departamento que arma el presupuesto
        @fy_id: ejercicio fiscal en planificacion
        limits: contiene los limites por cuenta analitica
        """
        acc_obj = self.pool.get('account.analytic.account')
        roof_obj = self.pool.get('budget.roof.line')
        budget_obj = self.pool.get('budget.item')
        keys_limits = roof_obj.get_parents(cr, uid, department_id, fy_id)
        ## if len(limits.keys()) > 2:
        ##     raise osv.except_osv('Error', u'Ha configurado más de dos niveles de cuentas de gasto.')
        res = {'value': {}}
        totals = {}
        not_count = []
        #CHECK totals definition
        for key in keys_limits:
            totals.update({key: 0})
        for line in lines:
            if not line[1]:
                account = line[2]['acc_budget_id']
                amount = line[2]['planned_amount']
            else:
                bud_res = budget_obj.read(cr, uid, line[1], ['planned_amount','acc_budget_id'])
                not_count.append(line[1])
                account = bud_res['acc_budget_id'][0]
                if isinstance(line[2], dict):
                    amount = line[2]['planned_amount']
                else:
                    amount = bud_res['planned_amount']
            for k in keys_limits:
                if acc_obj.is_child(cr, uid, k, account):
                    totals[k] += amount
        limits = budget_obj.get_available_by_department(cr, uid, department_id, fy_id, not_count)
        for k,v in limits.items():
            if totals[k] > v:
                data = acc_obj.read(cr, uid, k, ['code','name'])
                name = ' '.join([data['code'], data['name']])
                msg = u'El total planificado $ %s en "%s",\n supera el disponible de\n $%.2f' %(totals[k],name,v)
                res = {'warning': {'title': 'Error de Datos', 'message': msg}}
                return res
        return res

    def onchange_fy(self, cr, uid, ids, fy_id):
        """
        Metodo que devuelve segun
        el ejercicio fiscal @fy_id devuelve los periodos
        disponibles
        @fy_id: Fiscal Year ID: integer 
        """
        res = {'value': {}}
        if not fy_id:
            return res
        pids = []
        period_ids = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=',fy_id),('special','=',False)])
        for p in period_ids:
            pids.append((0,0,{'period_id': p, 'amount': 0}))
        res['value']['expense_planned_ids'] = pids
        return res        

    def _check_amount_planned(self, cr, uid, ids):
        """
        Metodo que verifica si lo presupuestado
        supera el limite por nivel de cuenta
        """
        acc_obj = self.pool.get('account.analytic.account')
        roof_obj = self.pool.get('budget.roof.line')
        budget_obj = self.pool.get('budget.item')
        for task in self.browse(cr, uid, ids):
            if not task.budget_planned_ids or task.project_id.type_budget == 'ingreso':
                return True
            keys_limits = roof_obj.get_parents(cr, uid, task.project_id.department_id.id, task.fy_id.id)
            if not task.project_id.roof_limit_id:
                raise osv.except_osv('Error', u'No se ha definido un límite para la coordinación.')
            res = {'value': {}}
            totals = {}
            not_count = []
            #CHECK totals definition
            for key in keys_limits:
                totals.update({key: 0})            
            for budget in task.budget_planned_ids:
                account = budget.acc_budget_id.id
                amount = budget.planned_amount
                not_count.append(budget.id)
                for k in keys_limits:
                    if acc_obj.is_child(cr, uid, k, account):
                        totals[k] += amount
            limits = budget_obj.get_available_by_department(cr, uid, task.department_id.id, task.fy_id.id, not_count)
            for k,v in limits.items():
                if totals[k] > v:
                    return False
        return True       

    def _check_dates_project(self, cr, uid, ids, context=None):
        """
        Revisión para que las fechas de tareas no estén fuera
        de los límites del proyecto
        """
        if context is None:
            context = {}
        for task in self.browse(cr, uid, ids, context):
                if task.date_start:
                        start = task.date_start
                        end = task.date_end
                        p_start = task.project_id.date_start
                        p_end = task.project_id.date
                        if start[:10] < p_start or end[:10] > p_end:
                                return False
        return True

    def _check_expense_plan(self, cr, uid, ids, context=None):
        """
        Revisión para que los montos de las actividades no
        sobrepasen el techo presupuestario de la actividad
        """
        total = 0
        for obj in self.browse(cr, uid, ids):
            total = sum([line.amount for line in obj.expense_planned_ids])
	    total_planeado = sum([line.planned_amount for line in obj.budget_planned_ids])
            aux_t = total - total_planeado
        return True

    _constraints = [
        (_check_dates_project, 'La tarea debe estar dentro de los tiempos del proyecto.', ['Fecha Inicio', 'Fecha Fin']),
#        (_check_amount_planned, 'Los montos por actividades no pueden superar el techo presupuestario.', [u'Presupuesto']),
        (_check_expense_plan, 'No puede gastar mas de lo planificado', ['Gasto planificado']),
        ]

    def check_status(self, cr, uid, ids):
        """
        Metodo que verifica que el status de las tareas del proyecto
        return True|False
        """
        pass

    def write(self, cr, uid, ids, fields, context=None):
        """
        Redefinición de método write para evitar modificar fechas
        fuera de planificación.
        """
        for task in self.browse(cr, uid, ids, context):
            if (fields.get('date_end',False) or fields.get('date_start')) and \
                   task.project_id.state not in ['open','plan_done', 'replaning']:
                raise osv.except_osv('Aviso', _('Sólo se puede modificar las fechas cuando el proyecto está en planificación'))
        return super(ProjectTask, self).write(cr, uid, ids, fields, context)    

    def onchange_weight(self, cr, uid, ids, weight, project_id):
        res = {}
        if not project_id:
            return {}
        task_ids = self.search(cr, uid, [('project_id','=',project_id)])
        total = 0
        for obj in self.browse(cr, uid, task_ids):
            total += obj.weight
        if total == 100 and weight>0:
            return {}
        if total > 100 or total+weight > 100:
            res = {'value': {'weight': 0},
                   'Warning': {'title': 'Error',
                               'message': 'No puede superar el 100.'}}
        return res

    def _check_scope(self, cr, uid, ids, context):
        """
        Metodo que verifica el progreso de la tarea cumpla con
        el 100%
        """
        for task in self.browse(cr, uid, ids, context):
            if not task.progress == 100.00:
                raise osv.except_osv('Datos Incompletos', 'No ha registrado el 100% de avance de la(s) actividad(s) del proyecto.')
        return True

    def do_open(self, cr, uid, ids, context={}):
        if not isinstance(ids,list): ids = [ids]
        tasks= self.browse(cr, uid, ids, context=context)
        for t in tasks:
            if not t.project_id.state in ['exec','replaning']:
                raise osv.except_osv('No Permitido', 'El proyecto aún no esta en ejecución.')
            data = {'state': 'open'}
            if not t.date_start:
                data['date_start'] = time.strftime('%Y-%m-%d %H:%M:%S')
            self.write(cr, uid, [t.id], data, context=context)
            message = _("The task '%s' is opened.") % (t.name,)
            self.log(cr, uid, t.id, message)
        return True    

    def action_close(self, cr, uid, ids, context=None):
        # This action open wizard to send email to partner or project manager after close task.
        if context == None:
            context = {}
        task_id = len(ids) and ids[0] or False
        self._check_child_task(cr, uid, ids, context=context)
        self._check_scope(cr, uid, ids, context)
        if not task_id: return False
        task = self.browse(cr, uid, task_id, context=context)
        project = task.project_id
        res = self.do_close(cr, uid, [task_id], context=context)
        if project.warn_manager or project.warn_customer:
            return {
                'name': _('Send Email after close task'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'nodestroy': True,
                'context': {'active_id': task.id,
                            'active_model': 'project.task'}
            }
        return res    


class ProjectCondition(osv.Model):
    _name = 'project.condition'
    _description = 'Condiciones de Proyecto'

    def write(self, cr, uid, ids, vals, context=None):
        """
        Redefinición de metodo para evitar la actualización del campo name
        cuando ya registra avance
        """
        data = self.read(cr, uid, ids, ['project_id'])[0]
        project_state = self.pool.get('project.project').read(cr, uid, data['project_id'][0])['state']
        if project_state not in ['plan','plan_done', 'plan_ok']:
            vals.pop('name')
        else:
            vals['done'] = False
        return super(ProjectCondition, self).write(cr, uid, ids, vals, context)

    _columns = dict(
        name = fields.char('Condición', size=64, required=True),
        done = fields.boolean('Realizado/Entregado'),
        project_id = fields.many2one('project.project', 'Proyecto'),
        state = fields.related('project_id', 'state', type='char', size=32, readonly=True, store=True),
        )


class ProjectDevelopmentPlan(osv.Model):
    _name = 'project.development.plan'
    _description = 'Plan Nacional de Desarollo'

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se representa
        en un campo many2one
        """
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            text = '%s %s: %s' % (r.type.capitalize(), r.sequence, r.name[:128])
            res.append((r.id, text))
        return res

    _columns = dict(
        sequence = fields.char('Numeral', size=5, required=True),
        name = fields.text('Descripción', required=True, select=True),
        type = fields.selection([('objetivo', 'Objetivo'),
                                 ('politica', 'Política')], string='Tipo',
                                required=True),
        )


class ProjectProject(osv.Model):

    _inherit = 'project.project'
    __logger = logging.getLogger(_inherit)
    STATES = {'open': [('readonly', False)]}
    STATES_POINTER = {
        'open': [('readonly', False)],
        'replaning': [('readonly', False)]
        }

#    def write(self, cr, uid, ids, vals, context=None):
#	    rl_obj = self.pool.get('account.budget.roof.line')#
#	    for this in self.browse(cr, uid, ids):
#		    fy = this.fy_id.id
#		    department_id = this.department_id.id
#	    rl_ids = rl_obj.search(cr, uid, [('fy_id','=',fy),
#					     ('department_id','=',department_id)])
#	    if rl_ids:
#		    total = rl_obj.read(cr, uid, rl_ids, ['amount_total'])[0]['amount_total']
#	    vals['amount_total'] = total
#	    return super(ProjectProject, self).write(cr, uid, ids, vals, context)    



    _order = 'program_id ASC'



    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se reprenta
        en un campo many2one
        """        
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            aux_programa = r.program_id.sequence    
            new_name = r.name
            anio = ' - ' + r.fy_id.name
            if r.code:
                new_name = ' '.join([aux_programa,r.code, new_name,anio])
            res.append((r.id, new_name))
        return res


    def get_projects_by_department(self, cr, uid, ids):
        projects = {}
        deps = {}
        for project in self.browse(cr, uid, ids):
            dep_id = project.department_id.id
            deps.update({dep_id: project.department_id.name})
            project_data = [project.name, project.amount_budget]
            if projects.get(dep_id):
                projects[dep_id].append(project_data)
            else:
                projects.update({dep_id: [project_data]})
        return projects, deps

    def onchange_canton(self, cr, uid, ids, canton_id):
        return {'value': {'parish_id': False}}

    def onchange_department(self, cr, uid, ids, department_id, fy_id):
        """
        Metodo que actualiza el campo de presupuesto total
        definido para el object hr.department
        """
        proj_obj = self.pool.get('project.project')
        res = {'value':{'amount_total': 0}}
        if not department_id or not fy_id:
            return {
                'warning': {
                    'title': 'Alerta',
                    'message': 'No se ha configurado un ejercicio fiscal o un departamento.'
                    }
                }
        rl_obj = self.pool.get('budget.roof.line')
        rl_ids = rl_obj.search(cr, uid, [
            ('fy_id', '=', fy_id),
            ('department_id', '=', department_id),
            ('state', '=', 'validate')]
            )
        if not rl_ids:
            res = {
                'warning': {
                    'title': 'Error de Configuración',
                    'message': u'No se ha definido techos presupuestarios para esta dirección / coordinación.'},
                'value': {
                    'department_id': department_id
                    }
                }
            return res
        total = rl_obj.read(cr, uid, rl_ids, ['limit_amount'])[0]['limit_amount']
        res['value']['amount_total'] = total
        p_ids = proj_obj.search(cr, uid, [
            ('department_id', '=', department_id),
            ('fy_id', '=', fy_id)],
            context={}
            )
        budget_all = sum([r['amount_budget'] for r in proj_obj.read(cr, uid, p_ids, ['amount_budget'])])
        res['value']['amount_available'] = res['value']['amount_total'] - budget_all
        res['value']['roof_limit_id'] = rl_ids[0]
        return res

    def onchange_program(self, cr, uid, ids, program_id):
        """
        Metodo para cargar valores por defecto segun programa
        seleccionado.
        Devuelve eje y estrategia
        """
        res = {'value': {'axis_id': False}}
        if program_id:
            program = self.pool.get('project.program').read(cr, uid, program_id, ['axis_id', 'estrategy_id'])
            res['value']['axis_id'] = program['axis_id']
            res['value']['estrategy_id'] = program['estrategy_id']
        return res

    def onchange_dates(self, cr, uid, ids, date_start, date_end, fy_id, department_id):
        """
        Metodo para cargar el ejercicios fiscal segun fecha inicio de proyecto
        Devuelve ejercicio fiscal
        """
        rl_obj = self.pool.get('budget.roof.line')
        fy = fy_id
        res = {'value': {'fy_id': fy_id, 'amount_total': 0}}
        if not date_start and not fy_id and not department_id:
            return res
        if not fy_id:
            fy_id = self.pool.get('account.fiscalyear').find(cr, uid, date_start)
        res['value']['fy_id'] = fy_id
        rl_id, limit_amount = rl_obj.get_limit(cr, uid, department_id, fy_id)
        res['value']['amount_total'] = limit_amount
        res['value']['roof_limit_id'] = rl_id
        return res

    def onchange_type(self, cr, uid, ids, type_id):
        """
        Método que devuelve las propiedades e indicadores
        del tipo de proyecto seleccionado.
        """
        res = {'value': {}}
        kpid = []
        if not type_id:
            return res
        type_data = self.pool.get('project.type').read(cr, uid, type_id, ['properties_ids', 'kpi_ids', 'show_fields'])
        res['value']['properties_ids'] = type_data['properties_ids']
        res['value']['show_fields'] = type_data['show_fields']
        return res

    def onchange_type_kpi(self, cr, uid, ids, type_kpi_id, fy_id):
        """
        Retorna los indicadores por tipo seleccionado
        """
        res = {'value': {}}
        kpis = []
        if not type_kpi_id:
            return res
        kpi_obj = self.pool.get('project.kpi.detail')
        kpi_type = self.pool.get('project.kpi.type').browse(cr, uid, type_kpi_id)
        for kpi in kpi_type.kpi_ids:
            kpi_data = {'kpi_id': kpi.id,
                        'uom_id': kpi.uom_id.id,
                        'type_kpi_id': type_kpi_id,
                        'type_internal': '3avance',
                        'fy_id': fy_id,
                        'weight': 0}
            kpi_data.update(kpi_obj.onchange_fy(cr, uid, [], fy_id)['value'])
            kpis.append((0,0,kpi_data))
        res['value']['pointer_detail_ids'] = kpis
        return res

    def name_search(self, cr, uid, name='', args=[], operator='ilike',
                    context=None, limit=100):
        ids = []
        ids = self.search(cr, uid,
                          [('name', operator, name)] + args,
                          context=context, limit=limit)
        if not ids:
            ids = set()
            ids.update(self.search(cr, uid,
                                   args + [('code', operator, name)],
                                   limit=limit, context=context))
            if len(ids) < limit:
                ids.update(self.search(cr, uid,
                                       args + [('code_aux', operator, name)],
                                       limit=(limit-len(ids)),
                                       context=context))
#                ids.update(self.search(cr, uid,
#                                       args + [('name', operator, name)],
#                                       limit=(limit-len(ids)),
#                                       context=context))
        ids = list(ids)
        return self.name_get(cr, uid, ids, context)

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        conf_obj = self.pool.get('project.configuration')
        res = conf_obj.search(cr, uid, [('active','=',True)])
        plan_id = False
        exec_id = False
        if res:
            conf = conf_obj.browse(cr, uid, res)[0]
            plan_id = conf.fiscalyear_plan_id.id
            exec_id = conf.fiscalyear_exec_id.id
        if context and context.get('planning') and plan_id:
            args += [('fy_id','=',plan_id)]
        elif context and context.get('execute') and exec_id:
            args += [('fy_id','=',exec_id)]
        res = super(ProjectProject, self).search(cr, uid, args, offset, limit, order, context, count)
        return res

    def copy_data(self, cr, uid, ids, default=None, context=None):
        data = super(ProjectProject, self).copy_data(cr, uid, ids, default, context)
        if data['user_id'] != uid:
            raise osv.except_osv('Alerta', 'Solo el responsable puede duplicar sus proyectos.')
        data['record_ids'] = False
        data['certificate_ids'] = False
#        data['tasks'] = False
        data['pointer_detail_ids'] = False
        data['crossovered_budget_line'] = False
        data['avance_ids'] = False
        return data 
        
    
    def create(self, cr, uid, vals, context=None):
        """
        Redefinición de método create par asegurar que las
        propiedades del tipo se relacionen con el proyecto
        """
        program_obj = self.pool.get('project.program')
        if context is None:
            context = {}
        type_id = vals['type_id']
        if type_id:
            prop = self.pool.get('project.type').read(cr, uid, type_id, ['properties_ids'])['properties_ids']
            if prop:
                vals['properties_ids'] = [(6,0, prop)]
        user = self.pool.get('res.users').browse(cr, uid, vals['user_id'])
        techo = self.onchange_department(cr, uid, [], user.context_department_id.id, vals['fy_id'])
        programa = program_obj.browse(cr, uid, vals['program_id'])
        vals['programa']=programa.name
        vals['codigo_programa']=programa.sequence
        return super(ProjectProject, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        """
        Metodo de borrado redefinido para evitar borrar
        proyectos que no esten en planificación
        """
        for project in self.browse(cr, uid, ids, context):
            if project.state != 'open':
                raise osv.except_osv('Error', 'No puede borrar el proyecto.')
        return super(ProjectProject, self).unlink(cr, uid, ids, context)

    def _get_projects_from_tasks(self, cr, uid, task_ids, context=None):
        tasks = self.pool.get('project.task').browse(cr, uid, task_ids, context=context)
        project_ids = [task.project_id.id for task in tasks if task.project_id]
        return self.pool.get('project.project')._get_project_and_parents(cr, uid, project_ids, context)

    def _get_tasks_budget(self, cr, uid, task_ids, context=None):
        result = {}
        tasks = self.pool.get('project.task').browse(cr, uid, task_ids, context=context)
        for t in tasks:
            result[t.project_id.id] = True
        return result.keys()

    def _get_project_and_parents(self, cr, uid, ids, context=None):
        """ return the project ids and all their parent projects """
        res = set(ids)
        while ids:
            cr.execute("""
                SELECT DISTINCT parent.id
                FROM project_project project, project_project parent, account_analytic_account account
                WHERE project.analytic_account_id = account.id
                AND parent.analytic_account_id = account.parent_id
                AND project.id IN %s
                """, (tuple(ids),))
            ids = [t[0] for t in cr.fetchall()]
            res.update(ids)
        return list(res)

    def _get_project_same_departments(self, cr, uid, ids, context=None):
        """
        return project with the same department_id
        """
        res = set(ids)
        cr.execute("""
                   SELECT DISTINCT parent.id
                   FROM project_project project, project_project parent
                   WHERE project.department_id = parent.department_id
                   AND project.id IN %s
                   """, (tuple(ids),))
        ids = [t[0] for t in cr.fetchall()]
        res.update(ids)
        return list(res)

    def _get_budget_plan(self, cr, ui, ids, context):
        res = {}
        for obj in self.pool.get('budget.item').browse(cr, ui, ids):
            res[obj.task_id.project_id.id] = True
        return res    

    def _get_project_kpi(self, cr, ui, ids, context):
        res = {}
        for obj in self.pool.get('project.kpi.detail').browse(cr, ui, ids):
            res[obj.project_id.id] = True
        return res

    def _get_project_work(self, cr, ui, ids, context):
        res = {}
        for obj in self.pool.get('project.kpi.work').browse(cr, ui, ids):
            res[obj.project_id.id] = True
        return res

    def _get_task_avance(self, cr, uid, ids, context):
        res = {}
        for obj in self.pool.get('project.task.avance').browse(cr, uid, ids):
            res[obj.task_id.project_id.id] = True
        return res

    def update_projects(self, cr, uid, ids, context):
        import random
        for project in self.browse(cr, uid, ids):
            task_ids = [task.id for task in project.tasks]
            self.pool.get('project.task').write(cr, uid, task_ids, {'remaining_hours': random.random()})
        return True

    def crear_financiamiento(self, cr, uid, ids,context=None):
        partida_financia_obj = self.pool.get('partida.financia')    
        for this in self.browse(cr, uid, ids):
            for actividad in this.tasks:
                for line in actividad.budget_planned_ids:
                    if line.financia_id:
                        partida_financia_obj.create(cr, uid, {
                                'poa_id':line.poa_id.id,
                                'project_id':line.project_id.id,
                                'budget_id':line.budget_post_id.id,
                                'financiera_id':line.financia_id.id,
                                'monto':line.planned_amount,
                        })
        return True

    def create_certingreso(self, cr, uid, ids,context=None):
        cert_obj = self.pool.get('budget.certificate')
        cert_line_obj = self.pool.get('budget.certificate.line')
        usr_obj = self.pool.get('res.users')
        user = usr_obj.browse(cr, uid, uid)
        for this in self.browse(cr, uid, ids):
                #verficar si ya esta creado solo agreagar una nueva linea
                if this.type_budget=='gasto':
                        raise osv.except_osv('Error', 'No en gasto')
                cert_ids = cert_obj.search(cr, uid, [('tipo_aux','=','ingreso'),('date_commited','=',this.date_start)],limit=1)
                if cert_ids:
                        for line in this.tasks:
                                for budget in line.budget_planned_ids:
                                        cert_line_ids = cert_line_obj.search(cr, uid, [('certificate_id','=',cert_ids[0]),
                                                                                       ('budget_id','=',budget.id)],limit=1)
                                        if not cert_line_ids:
                                                cert_line_obj.create(cr, uid, {
                                                        'certificate_id':cert_ids[0],
                                                        'project_id':this.id,
                                                        'task_id':line.id,
                                                        'budget_id':budget.id,
                                                        'amount':budget.planned_amount,
                                                        'amount_certified':budget.planned_amount,
                                                        'amount_commited':budget.planned_amount,
                                                })              
                else:
                        aux_sec = 0
                        cert_ids_aux = cert_obj.search(cr, uid, [('tipo_aux','=','ingreso')])
                        if cert_ids_aux>0:
                                aux_sec = len(cert_ids_aux)
                        nameaux = 'ING'+str(aux_sec)
                        cert_id = cert_obj.create(cr, uid, {
                                'tipo_aux':'ingreso',
                                'ref_doc':'Ingresos',
                                'name':nameaux,
                                'notes':'INGRESOS MUNICIPALES',
                                'user_id':uid,
                                'date':this.date_start,
                                'date_confirmed':this.date,
                                'date_commited':this.date_start,
                                'department_id':user.context_department_id.id,
                                'solicitant_id':user.employee_id.id,
                                'project_id':this.id})
                        for line in this.tasks:
                                for budget in line.budget_planned_ids:
                                        cert_line_obj.create(cr, uid, {
                                                'certificate_id':cert_id,
                                                'project_id':this.id,
                                                'task_id':line.id,
                                                'budget_id':budget.id,
                                                'amount':budget.planned_amount,
                                                'amount_certified':budget.planned_amount,
                                                'amount_commited':budget.planned_amount,
                                        })
        return True

    def get_progress_money(self, cr, uid, project):
        """
        Calcula el progreso economico
        """
        total = 0
        commited = 0
        p = project.amount_budget and project.amount_budget or 1
        for line in project.certificate_ids:
                commited += line.amount_commited
#        for task in project.tasks:
            #commited += sum([b.commited_amount for b in task.budget_planned_ids])
        progress = commited * 100 / p
        return progress  #mario      

    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        task_obj = self.pool.get('project.task')
        kpi_obj = self.pool.get('project.kpi')
        conf_obj = self.pool.get('project.configuration')
        conf_ids = conf_obj.search(cr, uid, [('active','=',True)], limit=1)
        child_parent = self._get_project_and_children(cr, uid, ids, context)
        # compute planned_hours, total_hours, effective_hours specific to each project
        cr.execute("""
            SELECT project_id, COALESCE(SUM(planned_hours), 0.0),
                COALESCE(SUM(total_hours), 0.0), COALESCE(SUM(effective_hours), 0.0)
            FROM project_task WHERE project_id IN %s AND state <> 'cancelled'
            GROUP BY project_id
            """, (tuple(child_parent.keys()),))
        # aggregate results into res
        res = dict([(id, {'planned_hours':0.0,'total_hours':0.0,'effective_hours':0.0}) for id in ids])
        for id, planned, total, effective in cr.fetchall():
            # add the values specific to id to all parent projects of id in the result
            while id:
                if id in ids:
                    res[id]['planned_hours'] += planned
                    res[id]['total_hours'] += total
                    res[id]['effective_hours'] += effective
                id = child_parent[id]
        # compute progress rates
        for id in ids:
            if res[id]['total_hours']:
                res[id]['progress_rate'] = round(100.0 * res[id]['effective_hours'] / res[id]['total_hours'], 2)
            else:
                res[id]['progress_rate'] = 0.0
        #Si tareas completadas, avanza el proyecto segun el peso de la tarea
        for obj in self.browse(cr, uid, ids, context):
            progress_money = 0
            res[obj.id]['activity_progress'] = 0
            #REVISAR CALCULO DE TODA LA FORMULA CON EL CAMBIO DE INDICADOR
            task_l = len(obj.tasks)>0 and len(obj.tasks) or 1
            progress_time = sum([task.weight*task.progress_time for task in obj.tasks]) / 100.00
            progress_scope = sum([kpi.weight*kpi.progress for kpi in obj.pointer_detail_ids]) / 100
            progress_money = self.get_progress_money(cr, uid, obj)
            self.__logger.info("Project %s "% obj.name)
            self.__logger.info("progreso tiempo %s"%progress_time)
            self.__logger.info("progreso ambito %s"%progress_scope)
            self.__logger.info("progreso dinero %s"%progress_money)            
            res[obj.id]['activity_progress'] = (progress_scope + progress_time + progress_money) / 3
            self.__logger.info("Progreso total: %s" % res[obj.id]['activity_progress'])
        return res

    def get_budgets(self, cr, uid, fy_id, department_id, project_id):
        if not (fy_id and department_id and project_id):
            return 0
        cr.execute("""SELECT SUM(amount_budget) as total FROM project_project
                    WHERE department_id=%s AND fy_id=%s AND id<>%s""" % (department_id, fy_id, project_id))
        amounts = cr.fetchone()
        suma = amounts and amounts[0] or 0
        return suma

    def _compute_budget(self, cr, uid, ids, fields, args, context):
        """
        Funcion para calcular el presupuesto de actividades
        TODO: el disponible de considerar todos los proyectos
        """
        res = {}
        rl_obj = self.pool.get('budget.roof.line')
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'amount_total':0,
                           'amount_budget': 0,
                           'amount_available':0,
                           'amount_projects': 0}
            budget_projects = self.get_budgets(cr, uid, obj.fy_id.id, obj.department_id.id, obj.id)            
            #Leer de los techos asignados del proyecto
            total = obj.roof_limit_id and obj.roof_limit_id.limit_amount or 0
            res[obj.id]['amount_total'] = total
            res[obj.id]['amount_budget'] = sum([task.planned_amount for task in obj.tasks])
            res[obj.id]['amount_projects'] = budget_projects
            res[obj.id]['amount_available'] = res[obj.id]['amount_total'] \
              - res[obj.id]['amount_budget'] - res[obj.id]['amount_projects']
        return res

    def _get_projects_from_tasks(self, cr, uid, task_ids, context=None):
        tasks = self.pool.get('project.task').browse(cr, uid, task_ids, context=context)
        project_ids = [task.project_id.id for task in tasks if task.project_id]
        return project_ids

    def _get_projects_from_kpis(self, cr, uid, kpi_ids, context=None):
        kpis = self.pool.get('project.kpi.detail').browse(cr, uid, kpi_ids, context=context)
        project_ids = [kpi.project_id.id for kpi in kpis if kpi.project_id]
        return project_ids

    def _progress_compliance(self, cr, uid, ids, fields, args, context):
        """
        Metodo que implementa el cumplimiento del proyecto
        """
        self.__logger.info("Calculo de cumplimiento de proyecto")
        res = {}
        conf_obj = self.pool.get('project.configuration')
        task_obj = self.pool.get('project.task')
        today = time.strftime('%Y-%m-%d')
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = 0
            if not obj.tasks:
                continue
            if obj.state != 'exec':
                continue
#            config = conf_obj.get_active(cr, uid, obj.fy_id.id)
            config = conf_obj.search(cr, uid, [])
            if not config:
                    print "NO"
                    #raise osv.except_osv('Error configuracion', 'Verifique la configuracion de proyectos para el anio fiscal del proyecto')
            w = conf_obj.browse(cr, uid, config[0])
            tasks = [task.id for task in obj.tasks]
            total_ct = 0
            tpesos = 0
            for task in obj.tasks:
                if task.date_start < today:
                    total_ct += task.weight*task.tcompliance
                tpesos += task.weight
            if tpesos == 0:
                tpesos = 1
            com_tasks = total_ct / tpesos
            com_kpi = sum([kpi.weight*kpi.compliance for kpi in obj.pointer_detail_ids]) / 100
            total_budget = 0
            tpbudget = 0
            for task in obj.tasks:
                if task.bcompliance == 0 and task.progress_money2 == 0:
                    continue
                total_budget += task.weight * task.bcompliance
                tpbudget += task.weight
            if tpbudget == 0:
                tpbudget = 1
            com_budget = total_budget / tpbudget
            compliance = ((w.time * com_tasks) + (w.scope * com_kpi) + (w.budget * com_budget)) / 100.00
            if obj.activity_progress == 0:
                res[obj.id] = 0
            else:    
                res[obj.id] = compliance>0 and compliance or 0
            self.__logger.info("Cumplimiento de Indicadores: %s" % com_kpi)
            self.__logger.info("Cumplimiento de Presupuestos: %s" % com_budget)
            self.__logger.info("Cumplimiento de Actividades: %s" % com_tasks)
        return res

    def _check_alerts(self, cr, uid, ids, fields, args, context):
        """
        Metodo que activa alertas cuando uno de los elementos
        del proyecto esta retrasado o no cumple con la planificación
        """
        res = {}
        kpi_obj = self.pool.get('project.kpi.detail')
        task_obj = self.pool.get('project.task')
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'alert_scope': False,
                           'alert_time': False,
                           'alert_budget': False}
            """revisar status de ambito"""
            kpi_ids = [kpi.id for kpi in obj.pointer_detail_ids]
            task_ids = [task.id for task in obj.tasks]
            res[obj.id]['alert_scope'] = kpi_obj.check_status(cr, uid, kpi_ids)
            res[obj.id]['alert_time'] = task_obj.check_status(cr, uid, task_ids)
        return res

    def apply_colors(self, ranges):
        values = (ranges['red'][0],ranges['red'][1],ranges['orange'][0],ranges['orange'][1],ranges['blue'][0],ranges['blue'][1])
        colors = """grey: state in ('close','cancelled');
                    red: %s<=compliance<=%s and (state=='exec');
                    orange: %s<compliance<=%s and (state=='exec');
                    blue: %s<compliance<=%s and (state=='exec');
                    blue: state=='exec';"""% values
        return colors

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
        Redefinición de metodo para aplicar los rangos de configuracion
        """
        conf_pool = self.pool.get('project.configuration')
        res = super(ProjectProject, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        if view_type == 'tree':
            ranges = conf_pool.get_ranges(cr, uid)
            if not ranges:
                return res
            colors = self.apply_colors(ranges)
            doc = etree.XML(res['arch'])
            doc.attrib.update({'colors': colors})
            res['arch'] = etree.tostring(doc)
        return res

    STORE_VAR = {'project.project': (_get_project_and_parents, ['tasks', 'parent_id', 'child_ids', 'avance_ids'], 20),
                 'project.task': (_get_projects_from_tasks, ['planned_hours', 'remaining_hours', 'state', 'executed_ids','project_id','progress_money2'], 20),
                 'project.kpi.detail': (_get_project_kpi, ['progress','planned','project_id'], 20),
                 'project.kpi.work': (_get_project_work, ['exec_done','project_id'], 20),
                 'project.task.avance': (_get_task_avance, ['executed','task_id'], 20)}

    STORE_BUDGET = {'project.project': (_get_project_same_departments,
                                        ['tasks', 'fy_id', 'department_id', 'roof_limit_id'], 20),
                    'project.task': (_get_tasks_budget, ['planned_amount', 'budget_planned_ids', 'project_id'], 20),
                    'budget.item': (_get_budget_plan, ['planned_amount','acc_budget_id', 'task_id'], 20)}

    STATES_LOG = {'done_poa': 'Cerrado por Ejercicio Fiscal',
                  'plan_done': u'Planificación Terminada',
                  'exec': u'Ejecución',
                  'exec_ok': u'Ejecución Aprobada',
                  'exec_done': u'Ejecución Terminada',
                  'plan_ok': u'Planificación Aprobada',
                  'cancelled': 'Cancelado', 'expost_done': 'ExPost Terminado',
                  'done': 'Finalizado', 'template': 'Template',
                  'done_wo_end': 'Cerrado sin Terminar',
                  'expost_ok': 'ExPost Aprobado',
                  'expost': 'ExPOST', 'open': u'Planificación',
                  'pending': 'Suspendido'}

    def _set_budget(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids):
            budget_id = False  
            if obj.tasks:
                task = obj.tasks[0]
                if task.budget_planned_ids:
                    budget_id = task.budget_planned_ids[0].budget_id.id
            result[obj.id] = budget_id
        return result
    
    _columns = dict(
        datas = fields.binary('Archivo'),
        code_aux = fields.related('program_id','sequence',type='char',size=12,store=True),
	poa_id = fields.many2one('budget.poa','POA',required=True),
        order_name = fields.char('NOMBRE PROYECTO', size=255),
        build_program_id = fields.many2one('project.build.program','Programa',
                                           states=STATES, readonly=True),
        build_type_id = fields.many2one('project.build.type','Tipo de Obra',
                                        states=STATES, readonly=True),
        build_indole_id = fields.many2one('project.build.indole','Indole de Obra',
                                          states=STATES, readonly=True),
        build_mode_id = fields.many2one('project.build.mode', 'Modalidad',
                                        states=STATES, readonly=True),
        type_budget = fields.selection([('ingreso', 'INGRESO'), ('gasto','GASTO')],
                                       string='Tipo Presupuestario',
                                       states=STATES, readonly=True),
        pointer_expost_ids = fields.one2many('project.kpi.expost', 'project_id', 'Indicadores Expost'),
        record_ids = fields.one2many('project.record.state', 'project_id', 'Historial de Estados'),
        roof_limit_id = fields.many2one('budget.roof.line', 'Techo Presupuestario de Dirección'),
        date_start = fields.date('Fecha Inicio', required=True, states=STATES, readonly=True),
        date = fields.date('Fecha Final', required=True, states=STATES, readonly=True),
        avance_ids = fields.one2many('project.kpi.work', 'project_id', 'Avance de Proyecto'),
        alert_scope = fields.function(_check_alerts, multi="alert", string='Alerta en Ambito',
                                      type='boolean', store=STORE_VAR),
        alert_time = fields.function(_check_alerts, multi="alert", string='Alerta en Tiempo',
                                     type='boolean', store=STORE_VAR),
        alert_budget = fields.function(_check_alerts, multi="alert", string='Alerta en Presupuesto',
                                       type='boolean', store=STORE_VAR),
        activity_progress =  fields.function(_progress_rate, multi="progress",
                                             string='Avance', group_operator='avg',
                                             store=False),
        planned_hours = fields.function(_progress_rate, multi="progress",
                                        string='Planned Time', help="Sum of planned hours of all tasks related to this project and its child projects.",
                                        store=STORE_VAR),
        effective_hours = fields.function(_progress_rate, multi="progress",
                                          string='Time Spent',
                                          help="Sum of spent hours of all tasks related to this project and its child projects.",
                                          store=STORE_VAR),
        total_hours = fields.function(_progress_rate, multi="progress",
                                      string='Total Time', help="Sum of total hours of all tasks related to this project and its child projects.",
                                      store=STORE_VAR),
        progress_rate = fields.function(_progress_rate, multi="progress",
                                        string='Progress', type='float',
                                        group_operator="avg", help="Percent of tasks closed according to the total of tasks todo.",
                                        store=STORE_VAR),
        compliance = fields.function(_progress_compliance, method=True, string='Cumplimiento', type='float', group_operator='avg',
                                store = {
                                        'project.task': (_get_projects_from_tasks, ['date_start', 'weight', 'tcompliance','bcompliance','progress_money2', 'state'], 20),
                                        'project.kpi.detail' : (_get_projects_from_kpis, ['weight', 'compliance'], 20),
                                }),
        background = fields.text('Antecendentes', readonly=True, states=STATES),
        justification = fields.text('Justificación', readonly=True, states=STATES),
        general_objective = fields.text('Objetivo General', readonly=True, states=STATES),
        specific_objectives = fields.text('Objetivos Específicos',  readonly=True, states=STATES),
        program_id = fields.many2one('project.program',
                                     string='Programa',
                                     required=True, readonly=True, states=STATES),
        programa = fields.char('Programa',size=64),
        codigo_programa = fields.char('Codigo Programa',size=10),
        department_id = fields.many2one('hr.department',
                                        string='Dirección / Coordinación', readonly=True, states=STATES,required=True),
        axis_id = fields.many2one('project.axis', string='Componente Estratégico',
                                  required=True, readonly=True, states=STATES),
        estrategy_id = fields.many2one('project.estrategy', string='Política pública',
                                       readonly=True, states=STATES),
        close_condition_ids = fields.one2many('project.condition',
                                              'project_id',
                                              string='Condiciones', readonly=True, states=STATES),
        stages = fields.selection([('draft','Formulación'),
                                   ('program','Programación'),
                                   ('exec', 'Ejecución'),
                                   ('close','Cierre'),
                                   ('expost', 'Evaluación Expost')],
                                  string='Etapa'),
        state = fields.selection([('open', 'Planificación'),
                                  ('plan_done', 'Plan. Terminada'),
                                  ('plan_ok', 'Planificación Aprobada'),
                                  ('exec', 'Ejecución'),
                                  ('done', 'Finalizado'),
                                  ('pending', 'Suspendido'),
                                  ('replaning', 'RePlanificacion'),
                                  ('template', 'Template'),
                                  ('cancelled', 'Cancelado'),
                                  ],
                                 string='Estado', readonly=True),
        has_project_related = fields.boolean('Proyecto Vinculado?', readonly=True, states=STATES),
        project_id = fields.many2one('project.project', 'Proyecto Vinculado'),
        plan_objective_id = fields.many2one('project.development.plan', 'Objetivo del Plan Nacional de Desarrollo',
                                            readonly=True, states=STATES),
        plan_politics_ids = fields.many2many('project.development.plan', string='Políticas del Plan Nacional de Desarrollo',
                                             readonly=True, states=STATES),
        pointer_detail_ids = fields.one2many('project.kpi.detail', 'project_id',
                                             string='Indicadores'),
        properties_ids = fields.one2many('project.property', 'project_id', string='Propiedades de Proyecto',
                                         readonly=True, states=STATES),
        amount_total = fields.function(_compute_budget, string="Techo Presupuestario de Coordinación",
                                       method=True,
                                       store=STORE_BUDGET, multi='budget'),
        amount_budget = fields.function(_compute_budget, string="Presupuesto de Proyecto",
                                        method=True,
                                        store=STORE_BUDGET, multi='budget'),
        amount_available = fields.function(_compute_budget, string='Disponible',
                                           method=True,
                                           store=STORE_BUDGET, multi='budget'),
        amount_projects = fields.function(_compute_budget, string='Presupuesto en Otros Proyectos',
                                          method=True, store=STORE_BUDGET, multi='budget'),
        fy_id = fields.many2one('account.fiscalyear', string='Ejercicio Fiscal', required=True),
        type_id = fields.many2one('project.type', 'Tipo de Proyecto', required=True, readonly=True, states=STATES),
        type_kpi_id = fields.many2one('project.kpi.type', 'Tipo de Indicador', required=False),
        user_id = fields.many2one('res.users', 'Responsable', readonly=True, states=STATES),
        canton_id = fields.many2one('res.country.state.canton', 'Cantón'),
        parish_id = fields.many2one('res.country.state.parish', 'Parroquia'),
        certificate_ids = fields.one2many('budget.certificate.line', 'project_id', 'Presupuestos Referenciales',
                                          readonly=True),
#        certificate_ids2 = fields.one2many('budget.certificate.line', 'project_id2', 'Pres. Referenciales',
#                                          readonly=True),
        #Infraestructura vial
        amount_long_obra = fields.float('Cantidad / Logitud', readonly=True,states=STATES),
        uom_id = fields.many2one('product.uom', string="UdM", readonly=True,states=STATES),
        avance_periodo_anterior = fields.float('Avance Periodo Anterior (KM)', readonly=True,states=STATES),
        ancho_obra = fields.char('Ancho Obra', size=32, readonly=True,states=STATES),
        avance_percent_anterior = fields.integer('Avance Periodo Anterior (%)', readonly=True,states=STATES),
        inversion_periodo_anterior = fields.float('Inversión Periodo Anterior ($)', readonly=True,states=STATES),
        show_fields = fields.boolean('Mostrar Campos IV'),
        budget_id = fields.function(_set_budget,type='many2one',relation="budget.budget",store=True),
        )

    def _get_department(self, cr, uid, context=None):
        """
        Metodo que cargar el departmento por defecto
        CHECK: buscar de departamentos aplica el organico de GPA?
        """
        res = self.pool.get('res.users').read(cr, uid, uid, ['context_department_id'])
        return res['context_department_id'] and res['context_department_id'][0]

    def _get_fiscalyear(self, cr, uid, context=None):
        """Return el ejercicio fiscal actual"""
        return self.pool.get('account.fiscalyear').find(cr, uid, context=context)    
    
    _defaults = dict(
        type_budget = 'gasto',
        state = 'open',
        stages = 'draft',
        department_id = _get_department,
        fy_id = _get_fiscalyear,
        )

    def onchange_programa_obra(self, cr, uid, ids, programa):
        return {'value': {'build_type_id': False}}

    def test_expost(self, cr, uid, ids):
        expost_obj = self.pool.get('project.kpi.expost')
        res = True
        for obj in self.browse(cr, uid, ids):
            kpis = [kpi.id for kpi in obj.pointer_expost_ids]
            if not expost_obj.check_executed(cr, uid, kpis):
                raise osv.except_osv('Expost Incompleto', 'No ha ingresado la evaluación de indicadores expost.')
        return res

    def test_exec(self, cr, uid, ids):
        conf_obj = self.pool.get('project.configuration')
        res = conf_obj.search(cr, uid, [('active','=',True)])
        if not res:
            raise osv.except_osv('Error', 'No ha configurado el sistema para la gestión de proyectos.')
        data = conf_obj.browse(cr, uid, res)[0]
        for obj in self.browse(cr, uid, ids):
            if not obj.fy_id.id == data.fiscalyear_exec_id.id:
                print "NO"
                #raise osv.except_osv('Error', 'Las fechas del proyecto no pertencen al año configurado como ejecución.')
        return True

    def test_planning(self, cr, uid, ids):
        """
        Metodo de verificación de condiciones para
        cerrar la planificacion de un proyecto
        """
        return True
        task_obj = self.pool.get('project.task')
        for obj in self.browse(cr, uid, ids):
            if not obj.tasks:
                raise osv.except_osv('Integridad de Datos', 'No ha planificado actividades.')
            for task in obj.tasks:
                if not task.budget_planned_ids:
                    raise osv.except_osv('Integridad de Datos', 'No ha presupuestado la actividad: %s' % task.name)
                if not task.expense_planned_ids:
                    raise osv.except_osv('Integridad de Datos', 'No ha planificado el gasto de la actividad: %s' % task.name)
                task_obj.check_expense_planned(cr, uid, [task.id])
#            if not obj.pointer_detail_ids and not obj.type_budget == 'ingreso':
#                raise osv.except_osv('Integridad de Datos', 'No ha definido indicadores.')
            self.pool.get('project.kpi.detail').check_planning(cr, uid, [k.id for k in obj.pointer_detail_ids])
        return True

    def test_close(self, cr, uid, ids):
        """
        Metodo de verificacion de las condiciones
        de cierre esten cumplidas
        """
        for obj in self.browse(cr, uid, ids):
            for cond in obj.close_condition_ids:
                if not cond.done:
                    return False
        return True

    def compute_dummy(self, cr, uid, ids, context):
        rl_obj = self.pool.get('budget.roof.line')            
        for obj in self.browse(cr, uid, ids, context):
            values = self.onchange_dates(cr, uid, [], obj.date_start, obj.date, obj.fy_id.id, obj.department_id.id)['value']
            self.write(cr, uid, obj.id, {'roof_limit_id': values['roof_limit_id']})
        self.write(cr, uid, ids, {})
        return True

    def set_replanning(self, cr, uid, ids, context):
        state_obj = self.pool.get('project.record.state')
        state_obj.create(cr, uid, {'user_id': uid, 'name': 'Cambio a Replanificación', 'project_id': ids[0]})
        self.write(cr, uid, ids, {'state': 'replaning'})
        return True
    
    def set_reopen(self, cr, uid, ids, context=None):
        state_obj = self.pool.get('project.record.state')
        state_obj.create(cr, uid, {'user_id': uid, 'name': 'Cambio a Ejecución', 'project_id': ids[0]})
        self.write(cr, uid, ids, {'state': 'exec'})
        return True

    def action_planning(self, cr, uid, ids, context=None):
        """
        Método que cambia de estado entre las opciones de planificación
        @context: recibe la llave 'new_state'
        """
        state_obj = self.pool.get('project.record.state')
        state = self.STATES_LOG[context.get('new_state')]
        state_obj.create(cr, uid, {'user_id': uid, 'name': 'Cambio a %s'%state, 'project_id': ids[0], 'hora': time.strftime('%Y-%m-%d %H:%M:%S')})
        self.write(cr, uid, ids, {'state': context.get('new_state')})
        return True

    def set_close(self, cr, uid, ids, context):
        self.write(cr, uid, ids,{
                'state':'done',
        })
        return True

    def set_re_execution(self, cr, uid, ids, context):
        state_obj = self.pool.get('project.record.state')
        state_obj.create(cr, uid, {'user_id': uid, 'name': 'Cambio a Ejecución', 'project_id': ids[0]})
        cert_obj = self.pool.get('budget.certificate')
        cert_line_obj = self.pool.get('budget.certificate.line')
        for obj in self.browse(cr, uid, ids, context):
            line_ids = [] #budgets to create
            tasks_to_open = []        
            flag = False
            for task in obj.tasks:
                if task.state == 'draft':
                    flag = True
                    tasks_to_open.append(task.id)
                    line_ids += [l.id for l in task.budget_planned_ids]
                else:
                    for l in task.budget_planned_ids:
                        if l.state == 'draft':
                            flag = True
                            line_ids.append(l.id)
            if flag:
                self.pool.get('project.project').create_budget_alone(cr, uid, obj.budget_id.id,line_ids)
                #agrega la linea de certificado si es ingreso
                cert_ids = cert_obj.search(cr, uid, [('ref_doc','=','Ingresos')])
                if not cert_ids:
                        if obj.state!='replaning':
                                raise osv.except_osv('Configuracion Incompleto', 'No ha creado presupuesto de ingreso.')
                for line_budget in obj.tasks[0].budget_planned_ids:
                        line_ids = cert_line_obj.search(cr, uid, [('budget_id','=',line_budget.id)])
                        if line_ids:
                                cert_line_obj.write(cr, uid, line_ids[0],{
                                        'amount':line_budget.planned_amount,
                                })
                        else:
                                if line_budget.type_budget=='ingreso':
                                        cert_line_obj.create(cr, uid, {
                                                'certificate_id':cert_ids[0],
                                                'project_id':obj.id,
                                                'task_id':obj.tasks[0].id,
                                                'budget_id':line_budget.id,
                                                'amount':line_budget.planned_amount,
                                        })
                self.pool.get('project.task').do_open(cr, uid, tasks_to_open)
        self.write(cr, uid, ids, {'state': 'exec'})
        return True    

    def create_budget_alone(self, cr, uid, budget_id,line_ids, context=None):
        item_obj = self.pool.get('budget.item')
        item_obj.set_codes(cr, uid, line_ids, context)
        item_obj.write(cr, uid, line_ids, {'budget_id': budget_id})
        return True

    def create_budget(self, cr, uid, ids, context=None):
        """
        Metodo para crear el presupuesto del proyecto
        TODO: relacionar presupuesto proyecto ?
        """
        budget_obj = self.pool.get('budget.budget')
        item_obj = self.pool.get('budget.item')
        project_obj = self.pool.get('project.project')
	for obj in self.browse(cr, uid, ids, context):
            line_ids = []
            aux_programa = obj.program_id.sequence
            for t in obj.tasks:
                line_ids += [b.id for b in t.budget_planned_ids]
            aux_name = ustr(aux_programa + "-Presupuesto: " + ustr(obj.name))
            budget_data = {
#                'name': aux_programa + "-Presupuesto: {name}".format(name=ustr(obj.name)),
                'name': aux_name,
                'code': obj.code,
                'date_start': obj.date_start,
                'date_end': obj.date,
                'department_id': obj.department_id.id,
		'poa_id':obj.poa_id.id,
            }
            budget_id = budget_obj.create(cr, uid, budget_data)
            item_obj.set_codes(cr, uid, line_ids, context)
            item_obj.write(cr, uid, line_ids, {'budget_id': budget_id})
            #write en proyecto budget creado
            project_obj.write(cr, uid, obj.id,{'budget_id':budget_id})
        return True

    def create_tasks_codes(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            count = 1
            for t in obj.tasks:
                self.pool.get('project.task').write(cr, uid, [t.id], {'code': str(count).zfill(3)})
                count += 1
        return True

    def set_open(self, cr, uid, ids, context=None):
        """
        CHECK: no se require el codigo base del metodo
        """
        self.write(cr, uid, ids, {'state': 'exec'})
        self.action_open_tasks(cr, uid, ids, context)
        self.create_tasks_codes(cr, uid, ids, context)
        self.create_budget(cr, uid, ids, context)   
        return True    

    def action_execution(self, cr, uid, ids, context=None):
        """
        Método que cambia de estado entre las opciones de ejecución
        @context: recibe la llave 'new_state'
        """
        self.write(cr, uid, ids, {'state': 'exec'})
        return True

    def action_open_tasks(self, cr, uid, ids, context=None):
        """
        Metodo que implementa la apertura automatica de las actividades
        del proyecto
        """
        for obj in self.browse(cr, uid, ids, context):
            task_ids = [task.id for task in obj.tasks]
            self.pool.get('project.task').do_open(cr, uid, task_ids)
        return True

    def action_close(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': context.get('new_state')})
        return True

    def action_expost(self, cr, uid, ids, context=None):
        """
        Método que cambia de estado entre las opciones de expost
        @context: recibe la llave 'new_state'
        """
        self.write(cr, uid, ids, {'state': context.get('new_state')})
        return True

    def _check_weight(self, cr, uid, ids, context=None):
        """
        Revisión para que los pesos por actividad sumen el
        100% del proyecto.
        """
        if context is None:
            context = {}
        for project in self.browse(cr, uid, ids, context):
            total = 0
            total = sum([task.weight for task in project.tasks])
            if total > 100:
                return False
            if project.state != 'open' and project.tasks and (100 - total) > 0:
                return False
        return True

    def _check_weight_kpi(self, cr, uid, ids):
        """
        Metodo que verifica que los pesos
        de los indicadores sumen 100
        """
        for obj in self.browse(cr, uid, ids):
            if not obj.pointer_detail_ids:
                return True
            totals = sum([t.weight for t in obj.pointer_detail_ids])
            if totals != 100:
                return False
        return True

    _constraints = [(
        _check_weight,
        'Los pesos de actividades deben sumar el 100% del proyecto.',
        ['Pesos de Actividades']),
        (_check_weight_kpi,
         u'Error en los pesos de indicadores', [u'Pesos de Indicadores'])]


class ProjectExpensePlan(osv.Model):
    _name = 'project.expense.plan'
    _description = 'Expense Planning'
    _rec_name = 'amount'

    def onchange_plan_amount(self, cr, uid, ids, date_start, date_end, period_id, amount):
        period_obj = self.pool.get('account.period')
        from calendar import monthrange
        from datetime import datetime
        ds = datetime.strptime(date_start, '%Y-%m-%d')
        de = datetime.strptime(date_end, '%Y-%m-%d')
        ds = datetime(ds.year,ds.month,1)
        de = datetime(de.year,de.month,monthrange(de.year,de.month)[1])        
        res = {'value':{}}
        if not date_start or not date_end:
            res = {'value': {'amount': 0}, 'warning': {'title': 'Error', 'message': 'Debe definir las fechas de la actividad.'}}
            return res
        if amount<0:
            res = {'value': {'amount': 0}, 'warning': {'title': 'Error', 'message': 'Debe ingresar un valor mayor a 0.'}}
            return res
        periods = period_obj.search(cr, uid, [('date_start','>=',ds.strftime('%Y-%m-%d')),('date_stop','<=',de.strftime('%Y-%m-%d'))])        
        if period_id not in periods:
            res = {'value': {'amount': 0}, 'warning': {'title': 'Error', 'message': 'No puede planificar en un mes fuera de las fechas de la actividad.'}}
        return res
        
    _columns = dict(
        task_id = fields.many2one('project.task', required=True, string='Actividad', ondelete='cascade'),
        period_id = fields.many2one('account.period', required=True, string='Mes', domain=[('special','=',False)]),
        amount = fields.float('Planificado', required=True),
        )

    _sql_constraints = [('unique_period_task','unique(task_id,period_id)', 'No puede repetir en mes en la actividad.')]

    def get_planned(self, cr, uid, date_to, task_id):
        """
        Devuelve registros de planificacion
        hasta una fecha limite
        """
        p_ids = self.pool.get('account.period').search(cr, uid, [('date_stop','<', date_to),('special','=',False)])
        ids = self.search(cr, uid, [('amount','>',0),('period_id.date_stop','<',date_to),('period_id.special','=',False),('task_id','=',task_id)])
        total = sum([plan.amount for plan in self.browse(cr, uid, ids)])
        return total    

    
class ProjectPropertyKey(osv.Model):
    """
    Clasificación para propiedades de proyectos
    """
    _name = 'project.property.key'
    _columns = dict(
        name = fields.char('Propiedad', size=64, required=True, select=True),
        )


class ProjectType(osv.Model):
    """
    Tipos de proyectos que definen propiedades por defecto
    """
    _name = 'project.type'
    _description = 'Tipos de Proyectos'
    _order = 'name DESC'

    _columns = dict(
        name = fields.char('Tipo de Proyecto', size=64, required=True, select=True),
        show_fields = fields.boolean('Requerir campos de Infraestructura en proyecto'),
        active = fields.boolean('Activo?', default=True),
        properties_ids = fields.one2many('project.property', 'type_id',
                                         string="Propiedades por Tipo de Proyecto"),
        kpi_ids = fields.one2many('project.kpi', 'project_type_id', string='Indicadores'),
        budget_ids = fields.many2many('budget.post', 'type_budget_rel',
                                     'type_id', 'budget_id',
                                     string="Partidas por Defecto"),        
        )

    _defaults = dict(
        active = True,
        )


class ProjectProperty(osv.Model):
    """
    Propiedades de proyectos
    """
    _name = 'project.property'
    _description = 'Propiedades de Proyecto'

    _columns = dict(
        categ_id = fields.many2one('project.property.key', string='Propiedad',
                                    required=True),
        name = fields.char('Descripción', size=128),
        project_id = fields.many2one('project.project', string='Proyecto'),
        type_id = fields.many2one('project.type', string='Tipo'),
        )


class ProjectRecordState(osv.Model):
    _name = 'project.record.state'
    _columns= dict(
        name = fields.char('Observaciones', size=64),
        user_id = fields.many2one('res.users', 'Usuario'),
        hora = fields.datetime('Hora de Registro'),
        project_id = fields.many2one('project.project', 'Proyecto'),
        )

    _defaults = dict(
        hora = time.strftime('%Y-%m-%d %H:%M:%S'),
        )
    
    
class ProjectKpiType(osv.Model):
    _name = 'project.kpi.type'
    _columns = dict(
        name = fields.char('Tipo', size=32, required=True),
        department_id = fields.many2one('hr.department', string='Dirección / Coordinación', required=True),
        kpi_ids = fields.many2many('project.kpi', 'type_kpi_rel',
                                   'type_id', 'kpi_id',
                                   string='Indicadores'),
        )

    def _get_department(self, cr, uid, context=None):
        """
        Metodo que cargar el departmento por defecto
        CHECK: buscar de departamentos aplica el organico de GPA?
        """
        res = self.pool.get('res.users').read(cr, uid, uid, ['context_department_id'])
        return res['context_department_id'] and res['context_department_id'][0]    

    _defaults = dict(
        department_id = _get_department
        )


class ProjectKpiExpost(osv.Model):
    _name = 'project.kpi.expost'    

    def onchange_kpi(self, cr, uid, ids, kpi):
        if not kpi:
            return {}
        kpi_data = self.pool.get('project.kpi').read(cr, uid, kpi)
        res = {'value': {'uom_id': kpi_data['uom_id']}}
        return res

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se representa
        en un campo many2one
        """
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            text = '%s %s (UdM)' % (r.kpi_id.name, r.uom_id.name)
            res.append((r.id, text))
        return res

    _columns = dict(
        kpi_id = fields.many2one('project.kpi', 'Indicador', required=True),
        uom_id = fields.related('kpi_id', 'uom_id', type='many2one',
                                relation='product.uom',
                                string='Unidad de Medida', readonly=True),
        plan_ids = fields.one2many('project.expost.plan', 'kpi_id', 'Planificación'),
        project_id = fields.many2one('project.project', 'Proyecto'),
        )

    def check_executed(self, cr, uid, ids):
        """
        Metodo que revisa si la informacion de ejecucion
        fue ingresada en cada meta de indicador
        """
        plan_obj = self.pool.get('project.expost.plan')
        res = True
        for obj in self.browse(cr, uid, ids):
            plans = [p.id for p in obj.plan_ids]
            if not plan_obj.check_executed(cr, uid, plans):
                res = False
                break
        return res
            


class ProjectKpiExpostPlan(osv.Model):
    _name = 'project.expost.plan'

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se representa
        en un campo many2one
        """
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            text = '%s - (PLANIFICADO: %s)' % (r.period_id.name, r.planned)
            res.append((r.id, text))
        return res

    _columns = dict(
        kpi_id = fields.many2one('project.kpi.expost', 'Indicador Expost', ondelete='cascade', required=True),
        date_limit = fields.date('Límite', required=True),
        planned = fields.float('Meta (UdM)'),
        executed = fields.float('Ejecutado (UdM)')
        )

    def check_executed(self, cr, uid, ids):
        res = False
        for obj in self.browse(cr, uid, ids):
            if not obj.executed > 0:
                res = False
                break
        return res


class ProjectKpiDetail(osv.Model):
    _name = 'project.kpi.detail'
    _rec_name = 'type_id'
    __logger = logging.getLogger(_name)

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se representa
        en un campo many2one
        """
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            text = '%s - (V. PLANIFICADO: %s %s)' % (r.kpi_id.name, r.planned, r.uom_id.name)
            res.append((r.id, text))
        return res

    def onchange_kpi(self, cr, uid, ids, kpi):
        if not kpi:
            return {}
        kpi_data = self.pool.get('project.kpi').read(cr, uid, kpi)
        res = {'value': {'uom_id': kpi_data['uom_id']}}
        return res

    def onchange_request(self, cr, uid, ids, value):
        res = {}
        if not value > 0:
            res = {
                'value': {},
                'warning': {
                    'title': 'Error',
                    'message': 'Debe ingresar un valor mayor a 0.'}
                }
        return res

    def onchange_fy(self, cr, uid, ids, fy_id):
        res = {'value': {}}
        if not fy_id:
            return res
        pids = []
        period_ids = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=',fy_id),('special','=',False)])
        for p in period_ids:
            pids.append((0,0,{'period_id': p}))
        res['value']['plan_ids'] = pids
        return res

    def _compute_progress(self, cr, uid, ids, fields, args, context):
        """
        Método que calcula el progreso del trabajo realizado
        contra el planificado
        el detalle de work_ids registra el avance de trabajo
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'progress': 0, 'remaining': 0}
            progress = 0
            w_ids = []
            work_id = self.pool.get('project.kpi.work').search(cr, uid, [('detail_id','=',obj.id)], order='date desc, id desc', limit=1)
            if work_id:
                work = self.pool.get('project.kpi.work').browse(cr, uid, work_id)[0]
                work_value = work.exec_done>obj.planned and obj.planned or work.exec_done
                res[obj.id]['progress'] = (work_value * 100.00) / obj.planned
                res[obj.id]['remaining'] = obj.planned - work_value
        return res

    def _progress_compliance(self, cr, uid, ids, fields, args, context):
        """
        Metodo para calculo del cumplimiento de indicadores
        TODO: implementar las reglas para el cumplimiento
        """
        res = {}
        w_obj = self.pool.get('project.kpi.work')
        plan_obj = self.pool.get('project.kpi.plan')
        today = time.strftime('%Y-%m-%d')
        import datetime
        d1 = datetime.date.today()
        from dateutil.relativedelta import relativedelta
        df = d1 - relativedelta(months=1)
        today2 = df.strftime("%Y-%m-%d")
        for obj in self.browse(cr, uid, ids, context):
            p = 0
            cumplimiento = 0
            res[obj.id] = 0
            progress = 0
            w_ids = w_obj.search(cr, uid, [('detail_id','=',obj.id),('date','<=',today)], order='date desc, id desc', limit=1)
            if w_ids:
                work = w_obj.browse(cr, uid, w_ids[0])
                progress = work.exec_done
            planned = plan_obj.find(cr, uid, obj.id, today2, context)
            if progress == 0 and planned == 0:
                cumplimento = 100
                continue
            elif progress == 0:
                cumplimiento = 0
                continue
            elif progress == planned:
                cumplimiento = 100
            elif (progress - planned) > 0:
                cumplimiento = planned * 100.00 / progress
            else:
                p = ((planned - progress) * 100.00) / planned
                cumplimiento = 100 - p
	    res[obj.id] = cumplimiento
        return res

    def _get_work(self, cr, uid, ids, context=None):
        result = {}
        for work in self.pool.get('project.kpi.work').browse(cr, uid, ids, context=context):
            if work.detail_id: result[work.detail_id.id] = True
        return result.keys()    

    _STORE_VAR = {
        'project.kpi.detail': (lambda self, cr, uid, ids, c={}: ids,
                                         ['work_ids'], 10),
        'project.kpi.work': (_get_work, ['exec_done'], 10)
        }

    _columns = dict(
        sequence = fields.integer('Secuencia'),
        done = fields.boolean('Terminado ?'),
        weight = fields.integer('Peso', required=True),
        type_kpi_id = fields.many2one('project.kpi.type', 'Tipo de Indicador', required=False),
        type_internal = fields.selection([('3avance','Avance'),
                                          ('2economico', 'Economico ($)'),
                                          ('1general','General')], string='Tipo', required=True),        
        kpi_id = fields.many2one('project.kpi', 'Indicador', required=True),
        uom_id = fields.related('kpi_id', 'uom_id', type='many2one',
                                relation='product.uom',
                                string='Unidad de Medida'),
        project_id = fields.many2one('project.project', string='Proyecto'),
        fy_id = fields.related('project_id', 'fy_id', relation='account.fiscalyear',
                               type='many2one', string="Ejercicio Fiscal"),
        planned = fields.float('META'),
        plan_ids = fields.one2many('project.kpi.plan', 'detail_id', string='Planificación de Avance'),
        work_ids = fields.one2many('project.kpi.work', 'detail_id', string='Detalle de Avance'),
        progress = fields.function(_compute_progress, method=True,
                                   string='Ejecutado', store=_STORE_VAR, multi='kpi'),
        compliance = fields.function(_progress_compliance, method=True, string='Cumplimiento'),
        remaining = fields.function(_compute_progress, method=True, string='Restante',
                                    store=_STORE_VAR, multi='kpi'),        
        detail = fields.char('Detalle', size=128),  
        )

    def _get_plan(self, cr, uid, context=None):
        res = False
        if context.get('fy_id', False):
            p_ids = self.pool.get('account.period').search(cr, uid, [
                ('fiscalyear_id','=',context.get('fy_id')),
                ('special', '=', False)
                ])
            res = [(0, 0, {'period_id':k}) for k in p_ids]
        return res

    def _get_fy_id(self, cr, uid, context=None):
        conf_obj = self.pool.get('project.configuration')
        res = conf_obj.search(cr, uid, [('active','=',True)])
        if not res:
            return False
        data = conf_obj.read(cr, uid, res, ['fiscalyear_plan_id', 'fiscalyear_exec_id'])[0]
        return data['fiscalyear_plan_id'][0]

    _defaults = {
        'plan_ids': _get_plan,
        'fy_id': _get_fy_id,
        'type_internal': '1general',
        }

    def check_planning(self, cr, uid, ids):
        """
        Metodo publico que verifica la planificacion
        del indicador:
        los avances planificados deben respetar el orden cronológico
        el mayor debe ser igual a la meta y no debe existir
        un avance mas alto que la meta
        """
        return self._check_plan(cr, uid, ids)

    def _check_plan(self, cr, uid, ids):
        """
        Metodo de validacion de planificacion de indicadores
        * los avances planificados deben respetar el orden cronológico
        * el mayor debe ser igual a la meta y no debe existir
          un avance mas alto que la meta
        """
        plan_obj = self.pool.get('project.kpi.plan')
        for obj in self.browse(cr, uid, ids):
            if not obj.plan_ids:
                return False
            plan_ids = [plan.id for plan in obj.plan_ids]
            valid = plan_obj.validate_plans(cr, uid, plan_ids, obj.planned)
            return valid
        return True

    def check_status(self, cr, uid, ids):
        """
        Metodo que devuelve el status de la ejecución
        del ambito, comparar si lo planificado es igual
        a lo ejecutado, los registros de avance
        de indicador tiene fecha y deberan buscar el periodo
        de registro para saber si esta dentro del planificado
        """
        plans = {}
        execs = {}
        period_obj = self.pool.get('account.period')
        for obj in self.browse(cr, uid, ids):
            for plan in obj.plan_ids:
                plans.update({plan.period_id.id: plan.planned})
            for executed in obj.work_ids:
                period_id = period_obj.find(cr, uid, executed.date)[0]
                execs.update({period_id: executed.exec_done})
            #TODO: compare plans vs execs
        return False

    _constraints = [
        (_check_plan,
         u'Error en la planificación de indicadores',
        [u'Planificación'])
        ]

     
class ProjectKpi(osv.Model):
    _name = 'project.kpi'
    _description = 'Lista de Indicadores'
    '''
    La implementación de los indicadores es para medir el cumplimiento
    que se puede dar a los objetivos que se plantean en las actividades
    % = (Ejecutado / Comprometido) * 100
    '''

    ## def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
    ##     ids = []
    ##     if context.get('pointers', False):
    ##         kpi_ids = [i[1] for i in context.get('pointers')]
    ##         ids = self.search(cr, uid, [('id','in', kpi_ids)], context=context, limit=limit)
    ##     return self.name_get(cr, uid, ids, context)
    ##     return super(ProjectKpi, self).name_search(cr, uid, name, args, operator, context, limit)
    
    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se representa
        en un campo many2one
        """
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            text = '%s: (UdM %s)' % (r.name, r.uom_id.name)
            res.append((r.id, text))
        return res

    def _get_work(self, cr, uid, ids, context=None):
        result = {}
        for work in self.pool.get('project.kpi.work').browse(cr, uid, ids, context=context):
            if work.detail_id: result[work.detail_id.id] = True
        return result.keys()    

    def _get_complete_formula(self, cr, uid, ids, fields, args, context):
        """
        Metodo que genera el campo que contiene la formula completa
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = ' '.join([obj.numerador, '/', obj.denominador])
        return res

    _STORE_VAR = {'project.kpi': (lambda self, cr, uid, ids, c={}: ids,
                                 ['work_ids', 'exec_done', 'kpi_id'], 10),
                 'project.kpi.work': (_get_work, ['exec_done'], 10)}

    _columns = dict(
        name = fields.char('Descripción', size=128, required=True),
        formula = fields.function(_get_complete_formula, method=True, string='Fórmula', type='char'),
        numerador = fields.char('Numerador', size=128, required=True),
        denominador = fields.char('Denominador', size=128, required=True),
        uom_id = fields.many2one('product.uom', 'Unidad de Medida', required=True),
        planned_value = fields.float('Solicitado', require=True),
        project_type_id = fields.many2one('project.type', 'Tipo de Proyecto'),
        to_report = fields.boolean('En reporte Consolidado?'),        
        )

    _defaults = dict(
        numerador = '**',
        denominador = '**'
        )

    def _check_progress(self, cr, uid, ids):
        """
        Validación de avances
        """
        return True
        ## work_obj = self.pool.get('project.kpi.work')
        ## for kpi in self.browse(cr, uid, ids):
        ##     work_id = work_obj.search(cr, uid, [('kpi_id','=',kpi.id)], order='date desc, id desc', limit=1)
        ##     if not work_id:
        ##         return True
        ##     work = work_obj.browse(cr, uid, work_id)[0]
        ##     if not work.exec_done < exec_done < kpi.planned_value:
        ##         return False
        ## return True

    def _check_plan(self, cr, uid, ids):
        """
        Verificar si por indicador existe un
        registro de planificación que marca el 100%
        TODO: planificaion de indicador en el proyecto
        """
        return True

    _constraints = [(_check_progress, 'El avance registrado no puede superar, lo planificado.', ['work_ids','planned_value']),
                    (_check_plan, 'No existe un mes que avance al 100%', ['Avance planificado.'])]


class ProjectKpiPlan(osv.Model):
    _name = 'project.kpi.plan'
    _description = 'Plan de Indicadores'

    def find(self, cr, uid, detail_id, date, context):
        """
        Encuentra la planificacion en la fecha enviada
        """
        sql = "SELECT p.planned FROM project_kpi_plan p, account_period ap WHERE detail_id=%s AND p.period_id=ap.id AND ap.date_start<'%s' AND p.planned>0 ORDER BY planned DESC limit 1" % (detail_id,date);
        cr.execute(sql)
        data = cr.fetchone()
        return data and data[0] or 0

    _columns = dict(
        period_id = fields.many2one('account.period', 'Mes', required=True, domain=[('special','=',False)]),
        planned = fields.float('Avance Planificado (UdM)', required=True),
        detail_id = fields.many2one('project.kpi.detail', string='Registro de Indicador'),
        date = fields.datetime('Fecha de Registro'),
        user_id = fields.many2one('res.users', string='Reportado por'),
        )

    def validate_plans(self, cr, uid, ids, goal):
        total = sum([obj.planned for obj in self.browse(cr, uid, ids)])
        if round(total,2) != round(goal, 2):
            return False
        return True

    def _get_user(self, cr, uid, context=None):
        if context is None:
            context = {}
        return uid

    def onchange_planned(self, cr, uid, ids, planned):
        if not planned:
            return {}
        if planned > 100:
            res = {'value': {'planned': 0}, 'warning': {'title': 'Error de Usuario', 'message': 'No puede ingresar un valor mayor a 100%.'}}
            return res
        return {}

    _defaults = dict(
        user_id = _get_user,
        date = time.strftime('%Y-%m-%d %H:%M:%S'),
        planned = 0
        )

    
class ProjectKpiWork(osv.Model):
    _name = 'project.kpi.work'
    _description = 'Avance de Trabajo'
    _order = 'date DESC, id DESC'

    def compute_total(self, cr, uid, ids):
        total = 0
        total = sum([obj.exec_done for obj in self.browse(cr, uid, ids)])
        return total

    def onchange_kpi(self, cr, uid, ids, kpi_id):
        if not kpi_id:
            return {}
        kpi = self.browse(cr, uid, kpi_id)
        return {'value': {'uom_id': kpi.uom_id.id}}

    def onchange_kpi(self, cr, uid, ids, kpi_id, exec_done, flag=True):
        """
        @kpi_id: Indicador: contiene la meta planificada
        @exec_done: avance registrado
        El avance registrado debe cumplir:
        ultimo registado < avance registrado < meta
        """
        work_obj = self.pool.get('project.kpi.work')
        kpi_obj = self.pool.get('project.kpi')        
        if not kpi_id:
            return {'value': {'exec_done': exec_done}}
        kpi = kpi_obj.browse(cr, uid, kpi_id)
        if exec_done == 0 and not flag:
            res = {'value': {'detail_id': kpi_id, 'uom_id': kpi.uom_id.id}}
            return res
        if exec_done > kpi.planned_value:
            res = {'value': {'detail_id': kpi_id, 'exec_done': 0}, 'warning': {'title': 'Error', 'message': 'El avance registrado es incorrecto.'}}
            return res        
        work_id = work_obj.search(cr, uid, [('detail_id','=',kpi_id)], order='date desc, id desc', limit=1)            
        if not work_id:
            return {'value': {'detail_id': kpi_id, 'exec_done': exec_done, 'uom_id': kpi.uom_id.id}}
        work = work_obj.browse(cr, uid, work_id)[0]
        if not work.exec_done < exec_done < kpi.planned_value:
            res = {'value': {'detail_id': kpi_id, 'exec_done': 0}, 'warning': {'title': 'Error', 'message': 'El avance registrado es incorrecto.'}}
            return res
        res = {'value': {'remaining': kpi.remaining, 'uom_id': kpi.uom_id.id, 'exec_done': exec_done}}
        return res

    def _get_user(self, cr, uid, context=None):
        if context is None:
            context = {}
        return uid

    _columns = dict(
        name = fields.char('Resumen de Trabajo', size=64, required=True),
        detail_id = fields.many2one('project.kpi.detail', string="Indicador", required=True),        
        remaining = fields.related('detail_id', 'remaining', store=False, type='float', string='Restante de Meta'),
        exec_done = fields.float('Ejecutado (UdM)', required=True),
        uom_id = fields.related('detail_id', 'uom_id', type='many2one', relation='product.uom', string='Unidad de Medida'),
        user_id = fields.many2one('res.users', 'Reportado por', required=True),
        date = fields.date('Fecha', required=True),
        project_id = fields.many2one('project.project', string='Proyecto', required=True),
        )

    def get_before(self, cr, uid, kpi_id, project_id):
        res = 0
        work_id = self.search(cr, uid, [('project_id','=', project_id),('detail_id','=',kpi_id)], order='date desc, id desc', limit=2)
        if work_id and len(work_id) > 1:
            w_data = self.read(cr, uid, [work_id[1]])[0]
            res = w_data['exec_done']
        return res

    def get_last(self, cr, uid, kpi_id, project_id):
        """
        Return last amount work registered
        return float
        """
        res = 0        
        work_id = self.search(cr, uid, [('project_id','=',project_id),('detail_id','=',kpi_id)], order='date desc, id desc', limit=1)
        if work_id:
            w_data = self.read(cr, uid, work_id)[0]
            res = w_data['exec_done']
        return res

    def get_last_date(self, cr, uid, kpi_id, project_id):
        """
        Return last amount work registered
        return float
        """
        res = 0        
        work_id = self.search(cr, uid, [('project_id','=',project_id),('detail_id','=',kpi_id)], order='date desc, id desc', limit=1)
        if work_id:
            w_data = self.read(cr, uid, work_id)[0]
            res = w_data['date']
        return res    

    def _check_progress(self, cr, uid, ids):
        """
        Validación de avances
        """
        kpi_obj = self.pool.get('project.kpi')
        for work in self.browse(cr, uid, ids):
            work_id = self.search(cr, uid, [('detail_id','=',work.detail_id.id)], order='date desc, id desc', limit=1)
            if not work_id:
                return True
            work = self.browse(cr, uid, work_id)[0]
            if work.exec_done == 0:
                return False
        return True

    _constraints = [(_check_progress, 'Su avance registrado es incorrecto.', ['Avance registrado.'])]
    _sql_constraints = [('unique_plan_kpi', 'unique(detail_id,exec_done)','No puede registras dos veces el mismo avance del indicador.')]    

    _defaults = dict(
        date = time.strftime('%Y-%m-%d'),
        user_id = _get_user,
        name = '/',
        exec_done = 0.00
        )

class tipoPolitica(osv.Model):
        _name = 'tipo.politica'
        _columns = dict(
                name = fields.char('Tipo Politica',size=128),
        )
tipoPolitica()


class ProjectEstrategy(osv.Model):
    _name = 'project.estrategy'
    _description = 'Lista de politicas publica'

    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        # devuelve el nombre y código del activo
        ids = []
        ids_descrip = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_descrip))
        if name:
            code = self.search(cr, uid, [('sequence', operator, name)] + args, limit=limit, context=context)           
            ids = list(set(ids + code))
        return self.name_get(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.sequence + ' - ' + record.name
            res.append((record.id, name))
        return res

    _columns = dict(
            politica_id = fields.many2one('tipo.politica','Tipo Politica'),
            tipo = fields.selection([('vista','vista'),('regular','regular')],'Tipo'),
        sequence = fields.char('Codigo', size=8, required=True),
        name = fields.char('Política pública', size=300, required=True),
        axis_id = fields.many2one('project.axis', 'Componente'),
        )

ProjectEstrategy()

class budgetEstrategy(osv.Model):
    _name = 'budget.estrategy'
    _columns = dict(
            p_id = fields.many2one('budget.politica.anual','Anual'),    
            poa_id = fields.many2one('budget.poa','Presupuesto',required=True),
            program_id = fields.many2one('project.program','Programa',required=True),
            name = fields.related('budget_id','budget_post_id',relation='budget.post',string='Partida',store=True),
            budget_id = fields.many2one('budget.item','Partida'),
            estrategy_id = fields.many2one('project.estrategy','Politica Aplica'),
            tipo = fields.many2one('tipo.politica','Tipo de Politica'),
    )
budgetEstrategy()

class budgetPoliticaAnual(osv.Model):
    _name = 'budget.politica.anual'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto',required=True),
        program_id = fields.many2one('project.program','Programa',required=True),
        project_id = fields.many2one('project.project','Proyecto'),
        line_ids = fields.one2many('budget.estrategy','p_id','Detalle'),
    )

    def loadPoliticaAnualConfirma(self, cr, uid, ids, context=None):
        print "hace"
        return True

    def loadPoliticaAnual(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('budget.estrategy')
        item_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            ids_antes = line_obj.search(cr, uid, [('p_id','=',this.id)])
            if ids_antes:
                line_obj.unlink(cr, uid, ids_antes)
            if this.project_id:
                item_ids = item_obj.search(cr, uid, [('poa_id','=',this.poa_id.id),('program_id','=',this.program_id.id),('project_id','=',this.project_id.id)])
            else:
                item_ids = item_obj.search(cr, uid, [('poa_id','=',this.poa_id.id),('program_id','=',this.program_id.id)])
            if item_ids:
                for item_id in item_ids:
                    line_obj.create(cr, uid, {
                        'p_id':this.id,
                        'poa_id':this.poa_id.id,
                        'program_id':this.program_id.id,
                        'budget_id':item_id,
                    })    
        return True
        
budgetPoliticaAnual()

class ProjectTaskAvance(osv.Model):
    _name = 'project.task.avance'
    _description = 'Avance de Actividades'
    _order = 'date_done DESC'

    def onchange_executed(self, cr, uid, ids, executed, task_id):
        res = {}
        if not executed:
            return res
        if executed > 100.00:
            res = {'warning': {'title': 'Error de Datos', 'message': 'No puede ingresar un avance mayor a 100.'},
                   'value': {'executed': 0}}            
        return res

    def get_last(self, cr, uid, task_id):
        cr.execute("SELECT executed FROM project_task_avance WHERE task_id=%s ORDER BY date_done DESC limit 1" % task_id)
        data = cr.fetchone()
        return data and data[0] or 0

    def get_last_date(self, cr, uid, task_id):
        if not task_id:
            return 0
        cr.execute("SELECT date_done FROM project_task_avance WHERE task_id=%s ORDER BY date_done DESC limit 1" % task_id)
        data = cr.fetchone()
        return data and data[0] or 0    

    def _get_user(self, cr, uid, context=None):
        return uid

    _columns = dict(
        name = fields.char('Descripcion', size=128, required=True),
        executed = fields.integer('Avance (%)'),
        user_id = fields.many2one('res.users', 'Usuario', readonly=True),
        date_done = fields.datetime('Fecha de Registro', readonly=True),
        task_id = fields.many2one('project.task', 'Actividad'),
        )

    _defaults = dict(
        executed = 0,
        user_id = _get_user,
        date_done = time.strftime('%Y-%m-%d %H:%M:%S'),
        )

    _sql_constraints = [('unique_task_exec', 'unique(task_id,executed)', u'El avance registrado está duplicado.')]





