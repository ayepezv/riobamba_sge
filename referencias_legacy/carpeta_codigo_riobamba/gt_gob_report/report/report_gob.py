
# -*- coding: utf-8 -*-
##############################################################################
#    
# mariofchogllo@gmail.com
#
##############################################################################


from report import report_sxw
from osv import osv
import operator
import time
import datetime
import tools
from osv.osv import except_osv
import pdb
from tools import ustr
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from more_itertools import chunked

class BalanceComprobacion(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(BalanceComprobacion, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            'lineas': self.lineas,
            'get_firmas':self.get_firmas,
         })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_end'] = self.datas['form']['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_end']
        res['end']=end.upper()
        res['nivel'] = self.datas['form']['nivel']
        res['all_accounts'] = self.datas['form']['all_accounts']
        return res 

    def lineas(self, resumen):
        cr = self.cr
        uid = self.uid
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        result = {}
        fiscalyear_id = self.datas['form']['fiscalyear']
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        fiscal_obj = self.pool.get('account.fiscalyear')
        #account_ids = account_obj.search(cr, uid, [('type','!=','view')])
        #Buscar lineas de asientos de asiento de inicio
        sql_move_inicio = """
        select account_move.id,date from account_move,account_period
        where account_move.period_id=account_period.id and account_period.fiscalyear_id=%s and is_start=True """%(fiscalyear_id[0],)
        cr.execute(sql_move_inicio)
        move_inicial = cr.fetchall()
        if move_inicial:
            move_id_inicio = move_inicial[0][0]
            fecha_inicio = move_inicial[0][1]
        else:
            texto = tools.ustr("No se ha marcado un asiento como de inicio para el periodo fiscal ") + tools.ustr(fiscalyear_id[1])
            raise osv.except_osv('Error', texto)

        if fecha_inicio == date_inicial_reporte:
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_aux = date_aux + timedelta(days=1)
            date_inicial_reporte_aux = date_inicial_reporte
            date_inicial_reporte = date_aux.strftime('%Y-%m-%d')
            #cambiar la fecha de final si es sin cierre
            if self.datas['form']['cierre']:
                fiscal = fiscal_obj.browse(cr, uid, self.datas['form']['fiscalyear'][0])
                if fiscal.date_stop == self.datas['form']['date_end']:
                    final_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
                    final_aux = final_aux - timedelta(days=1)
                    date_final_reporte = final_aux.strftime('%Y-%m-%d')
        else:
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_aux = date_aux - timedelta(days=1)
            date_inicial_reporte_aux = date_aux.strftime('%Y-%m-%d')
        #sacar nivel >7
        account_ids = account_obj.search(cr, uid, [('level','<=', self.datas['form']['nivel']),('level','>',0)])
#        if self.datas['form']['nivel']<=6:
#            account_ids = account_obj.search(cr, uid, [('level','<=', self.datas['form']['nivel']),('level','>',0)])
#        else:
#            account_ids = account_obj.search(cr, uid, [('level','=', self.datas['form']['nivel']),('level','>',0)])
    #   account_ids = account_obj.search(cr, uid, [('level','<',6)])
        ctx = {}
        ctx.update({'fiscalyear': fiscalyear_id[0]})
        ctx.update({'state': 'posted'})
        ctx.update({'date_from': fecha_inicio,
                    'date_to': date_inicial_reporte_aux})
        account_ids = list(chunked(account_ids, 1000))
        accounts_inicial = []
        for accounts in account_ids:
            accounts_inicial += account_obj.read(cr, uid, accounts, ['code','code_aux','name','debit','credit', 'balance','level','child_id'], ctx)

        ctx2 = {}
        ctx2.update({'fiscalyear': fiscalyear_id[0]})
        ctx2.update({'state': 'posted'})
        ctx2.update({'date_from': date_inicial_reporte,
                    'date_to': date_final_reporte})
        accounts_flujo = []
        for accounts in account_ids:
            accounts_flujo += account_obj.read(cr, uid, accounts, ['code','code_aux','name','debit','credit', 'balance','level'], ctx2)

        accounts_inicial_dict = {}
        for account_data in accounts_inicial:
            debe_inicial = 0
            haber_inicial = 0
            debe_inicial = account_data['debit']
            haber_inicial = account_data['credit']
            if account_data['child_id']:
                final=False
            else:
                final=True
            accounts_inicial_dict[account_data['code']] = {
                'code_aux': account_data['code_aux'],
                'code': account_data['code'],
                'desc': account_data['name'],
                'nivel': account_data['level'],
                'debit': debe_inicial,
                'credit': haber_inicial,
                'final': final,
            }

        accounts_flujo_dict = {}
        for account_data in accounts_flujo:
            accounts_flujo_dict[account_data['code']] = {
                'debit': account_data['debit'],
                'credit': account_data['credit']
            }

        accounts_final_dict = {}
        for code in accounts_inicial_dict:
            debe_final = 0
            haber_final = 0
            saldo = (accounts_inicial_dict[code]['debit'] + accounts_flujo_dict[code]['debit']) - (accounts_inicial_dict[code]['credit'] + accounts_flujo_dict[code]['credit'])
            if saldo >= 0:
                debe_final = saldo
            else:
                haber_final = saldo * - 1
            accounts_final_dict[code] = {
                'code_aux': accounts_inicial_dict[code]['code_aux'],
                'code': accounts_inicial_dict[code]['code'],
                'final': accounts_inicial_dict[code]['final'],
                'desc': accounts_inicial_dict[code]['desc'],
                'nivel': accounts_inicial_dict[code]['nivel'],
                'debe_inicial': accounts_inicial_dict[code]['debit'],
                'haber_inicial': accounts_inicial_dict[code]['credit'],
                'debe_flujo': accounts_flujo_dict[code]['debit'],
                'haber_flujo': accounts_flujo_dict[code]['credit'],
                'debe_suma': accounts_inicial_dict[code]['debit'] + accounts_flujo_dict[code]['debit'],
                'haber_suma': accounts_inicial_dict[code]['credit'] + accounts_flujo_dict[code]['credit'],
                'debe_final': debe_final,
                'haber_final': haber_final
            }
        #antes del return quitar o restar lo de la depreciacion
#q        aux_dep = 0
#q        if accounts_final_dict.has_key('14199'):
#q            aux_dep = accounts_final_dict['14199']['haber_inicial']#accounts_final_dict['1']['haber_inicial']
#q        aux_debe_activo = accounts_final_dict['1']['debe_inicial']-aux_dep#accounts_final_dict['1']['haber_inicial']
#q        accounts_final_dict['1']['haber_inicial']=accounts_final_dict['1']['haber_inicial']-aux_dep#0
#q        accounts_final_dict['1']['debe_inicial']=aux_debe_activo
        #bajar tambien en la 141
#q        aux_debe_activo_141 = 0
#q        if accounts_final_dict.has_key('141'):
#q            aux_debe_activo_141 = accounts_final_dict['141']['debe_inicial']-aux_dep
#q            accounts_final_dict['141']['debe_inicial']=aux_debe_activo_141
#q        aux_debe_activo_14 = 0
#q        if accounts_final_dict.has_key('14'):
#q            aux_debe_activo_14 = accounts_final_dict['14']['debe_inicial']-aux_dep
#q            accounts_final_dict['14']['debe_inicial']=aux_debe_activo_14
        #6 cero en el debe
#        accounts_final_dict['6']['debe_inicial']=0
        #en la 9 cero
        #q quitado despues de apertura riobamba
#q        accounts_final_dict['9']['debe_inicial']=0
#q        accounts_final_dict['9']['haber_inicial']=0
        #resta 619 deudor a 61 y a 6
#        debe_619 = 0
#        if accounts_final_dict.has_key('619'):
#            debe_619 = accounts_final_dict['619']['debe_inicial']
#        aux_haber_61 = 0
#        if accounts_final_dict.has_key('61'):
#            aux_haber_61 = accounts_final_dict['61']['haber_inicial']
#        accounts_final_dict['61']['haber_inicial']= aux_haber_61 - debe_619
#        aux_haber_6 = accounts_final_dict['6']['haber_inicial']
#        accounts_final_dict['6']['haber_inicial']= aux_haber_6 - debe_619 - accounts_final_dict['61']['debe_inicial'] + debe_619 
        #rio 92123
        #lista_aux = ['92123','91123']
        #for lista_a in lista_aux:
##        for cuenta_aux in accounts_final_dict:
##            saldo_92123 = 0
#            if accounts_final_dict.has_key(lista_a):
##            aux_92123 = accounts_final_dict[cuenta_aux]['haber_inicial']
##            aux_debe_92123 = accounts_final_dict[cuenta_aux]['debe_inicial']
##            saldo_92123 = abs(accounts_final_dict[cuenta_aux]['haber_inicial'] - accounts_final_dict[cuenta_aux]['debe_inicial'])
##            if aux_92123 > aux_debe_92123:
##                accounts_final_dict[cuenta_aux]['haber_inicial']=saldo_92123
##                accounts_final_dict[cuenta_aux]['debe_inicial'] = 0
##            else:
##                accounts_final_dict[cuenta_aux]['debe_inicial']=saldo_92123
##               accounts_final_dict[cuenta_aux]['haber_inicial']=0
        return accounts_final_dict

report_sxw.report_sxw('report.BalanceComprobacion','account.account',
                      'addons/gt_gob_report/report/report_balance_comprobacion.mako',
                      parser=BalanceComprobacion)

class EstadoResultados(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(EstadoResultados, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            'lineas': self.lineas,
            'get_firmas':self.get_firmas,
         })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux
        
    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_end'] = self.datas['form']['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_end']
        res['end']=end.upper()
        return res



    def lineas(self, resumen):
        result = {}
        result['act'] = self.lineas_individual(resumen,'act')
        result['ant'] = self.lineas_individual(resumen,'ant')
        return result

    def lineas_individual(self, resumen, tipo):
        context = {}
        cr = self.cr
        uid = self.uid
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        if tipo!='act':
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_inicial_aux = date_aux - relativedelta(years=1)
            date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
            date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux = date_aux - relativedelta(years=1)
            date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
        result = {}
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        if tipo=='ant':
            fiscalyear_ids = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
            if fiscalyear_ids:
                fiscalyear_id = fiscalyear_ids[0]
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        ctx = context.copy()
        c62401 = ['62401','62402','62403','62404']
        c63801 = ['63801','63802','63803','63804']
        c62435  = ['62435','63835']
        c621 =  ['621','623','631','633','634']
        c63501 = ['63501','63504']
        c626 = ['626','636']
        c62501 = ['62501','62502','62503','62504']
        c63502 = ['63502','63503','63507']
        c62421 = ['62421','62422','62423','62424','62425','62426','62427']
        c63821 = ['63821','63822','63823','63824','63825','63826','63827']
        c62521 = ['62521','62522','62523','62524']
        c63851 = ['63851','63852','63853','63854','63855','63856','63857','63858','63859','63860',
                 '63861','63862','63863','63864','63865','63866','63867','63868','63869','63870',
                 '63871','63872','63873','63874','63875','63876','63877','63878','63879','63880',
                 '63881','63882','63883','63884','63885','63886','63887','63888','63889','63890',
                 '63891','63892','63893']
        c629 =  ['629','639','61803']
        codes = c62401 + c63801 + c62435 + c621 + c63501 + c626 + c62501 + c63502 + c62421 + c63821 + c62521 + c63851 + c629
        account_ids = account_obj.search(cr, uid, [('code','in', codes)])
        ctx.update({'fiscalyear': fiscalyear_id})
        ctx.update({'state': 'posted'})
        ctx.update({'date_from': date_inicial_reporte,
                    'date_to': date_final_reporte})
        accounts = account_obj.read(cr, uid, account_ids, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        accounts_by_id = {}
        for account in accounts:
            accounts_by_id[account['code']] = account
        for code in codes:
            if accounts_by_id.get(code,False) == False:
                accounts_by_id.update({code: {'code': code, 'balance': 0} })
        #####################
        sum_aux = 0
        for code_aux in c62401:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62401/04': {'62401/04': '62401/04', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c63801:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'63801/04': {'63801/04': '63801/04', 'balance': sum_aux}})
        #####################
        accounts_by_id.update({'63501-04': {'63501-04': '63501-04', 'balance': accounts_by_id['63501']['balance']+accounts_by_id['63504']['balance']}})
        #####################
        sum_aux = 0
        for code_aux in c62501:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62501/04': {'62501/04': '62501/04', 'balance': sum_aux}})
        #####################
        accounts_by_id.update({'63502/03-07': {'63502/03-07': '63502/03-07', 'balance': accounts_by_id['63502']['balance']+accounts_by_id['63503']['balance']+accounts_by_id['63507']['balance']}})
        #####################
        sum_aux = 0
        for code_aux in c62421:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62421/27': {'62421/27': '62421/27', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c63821:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'63821/27': {'63821/27': '63821/27', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c62521:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62521/24': {'62521/24': '62521/24', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c62521:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62521/24': {'62521/24': '62521/24', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c63851:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'63851/93': {'63851/93': '63851/93', 'balance': sum_aux}})
        ####################
        resultado_explotacion = (accounts_by_id['62401/04']['balance']+accounts_by_id['63801/04']['balance'])*(-1)
        accounts_by_id.update({'resultado_explotacion': {'resultado_explotacion': 'resultado_explotacion', 'balance': resultado_explotacion}})
        ####################
        resultado_operacion = (accounts_by_id['621']['balance']+accounts_by_id['623']['balance']+accounts_by_id['631']['balance']+accounts_by_id['633']['balance']+accounts_by_id['634']['balance']+accounts_by_id['63501-04']['balance'])*(-1)
        accounts_by_id.update({'resultado_operacion': {'resultado_operacion': 'resultado_operacion', 'balance': resultado_operacion}})
        ####################
        transferencias_netas = (accounts_by_id['626']['balance']+accounts_by_id['636']['balance'])*(-1)
        accounts_by_id.update({'transferencias_netas': {'transferencias_netas': 'transferencias_netas', 'balance': transferencias_netas}})
        ####################
        resultado_financiero = (accounts_by_id['62501/04']['balance']+accounts_by_id['63502/03-07']['balance'])*(-1)
        accounts_by_id.update({'resultado_financiero': {'resultado_financiero': 'resultado_financiero', 'balance': resultado_financiero}})
        otros_ingresos_gastos = (accounts_by_id['62421/27']['balance']+accounts_by_id['63821/27']['balance']+accounts_by_id['62521/24']['balance']+accounts_by_id['63851/93']['balance']+accounts_by_id['629']['balance']+accounts_by_id['639']['balance'])*(-1)
        accounts_by_id.update({'otros_ingresos_gastos': {'otros_ingresos_gastos': 'otros_ingresos_gastos', 'balance': otros_ingresos_gastos}})
        resultado_ejercicio = resultado_explotacion + resultado_operacion + transferencias_netas + resultado_financiero + otros_ingresos_gastos
        accounts_by_id.update({'resultado_ejercicio': {'resultado_ejercicio': 'resultado_ejercicio', 'balance': resultado_ejercicio}})    
        return accounts_by_id
 
report_sxw.report_sxw('report.EstadoResultados','account.account',
                      'addons/gt_gob_report/report/report_estado_resultados.mako',
                      parser=EstadoResultados)

class EstadoResultadosAuxiliar(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(EstadoResultadosAuxiliar, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            'lineas': self.lineas,
            'get_saldo_resultados':self.get_saldo_resultados,
            'get_firmas':self.get_firmas,
         })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux
        
    def get_saldo_resultados(self, code,desde,hasta,lista):
        fiscal_obj = self.pool.get('account.fiscalyear')
        account_obj = self.pool.get('account.account')
        account_parent_ids = account_obj.search(self.cr, self.uid, [('code','=',code)])
        res= []
        ctx = {}
        ctx_ant = {}
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        fiscal = fiscal_obj.browse(self.cr, self.uid, fiscalyear_id)
        if date_final_reporte==fiscal.date_stop:
            date_aux_f = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux_f = date_aux_f - timedelta(days=1)
            date_final_reporte = date_final_aux_f.strftime('%Y-%m-%d')
        ctx['fiscalyear'] = fiscalyear_id
        ctx['state'] = 'posted'
        ctx['date_from'] = date_inicial_reporte
        ctx['date_to'] = date_final_reporte
        #armo anio anterior
        date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
        date_inicial_aux = date_aux - relativedelta(years=1)
        date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
        date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
        date_final_aux = date_aux - relativedelta(years=1)
        date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
        fiscalyear_ids = self.pool.get('account.fiscalyear').search(self.cr, self.uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
        if fiscalyear_ids:
            fiscalyear_id = fiscalyear_ids[0]
        ctx_ant['fiscalyear'] = fiscalyear_id
        ctx_ant['state'] = 'posted'
        ctx_ant['date_from'] = date_inicial_reporte
        ctx_ant['date_to'] = date_final_reporte
        if account_parent_ids and len(lista)==0:
            aux_parent = []
            account_parent = account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx)
            account_parent_ant = account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx_ant)
            if abs(account_parent[0]['balance'])>0:
                aux_parent.append(account_parent[0]['code_aux'])
                aux_parent.append(account_parent[0]['name'])
                aux_parent.append(abs(account_parent[0]['balance']))
                aux_parent.append(abs(account_parent_ant[0]['balance']))
                res.append(aux_parent)
                account_hijas_ids = account_obj.search(self.cr, self.uid, [('parent_id','=',account_parent_ids[0]),('code','>=',desde),('code','<=',hasta)])
                if account_hijas_ids:
                    for account_hija in account_obj.read(self.cr, self.uid, account_hijas_ids,['id','code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx):
                        if abs(account_hija['balance'])>0:
                            account_hija_ant = account_obj.read(self.cr, self.uid, account_hija['id'],['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx_ant)
                            aux_hija = []
                            aux_hija.append(account_hija['code_aux'])
                            aux_hija.append(account_hija['name'])
                            aux_hija.append(abs(account_hija['balance']))
                            aux_hija.append(abs(account_hija_ant['balance']))
                            #aux_hija.append(abs(account_hija_ant['balance']))
                            res.append(aux_hija)
        else:
            if account_parent_ids:
                account_parent = account_obj.read(self.cr, self.uid, account_parent_ids[0],['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx)
                account_parent_ant = account_obj.read(self.cr, self.uid, account_parent_ids[0],['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx_ant)
                aux_parent = []
                aux_parent.append(account_parent['code_aux'])
                aux_parent.append(account_parent['name'])
                aux_parent.append(abs(account_parent['balance']))
                aux_parent.append(abs(account_parent_ant['balance']))
                res.append(aux_parent)
                parent_aux = 0
                for account_id in lista:
                    account_hija_ids = account_obj.search(self.cr, self.uid, [('code','=',account_id)])
                    if account_hija_ids:
                        account_hija = account_obj.read(self.cr, self.uid, account_hija_ids[0],['id','code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx)
                        if abs(account_hija['balance'])>0:
                            account_hija_ant = account_obj.read(self.cr, self.uid, account_hija['id'],['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx_ant)    
                            aux_hija = []
                            aux_hija.append(account_hija['code_aux'])
                            aux_hija.append(account_hija['name'])
                            aux_hija.append(abs(account_hija['balance']))
                            aux_hija.append(abs(account_hija_ant['balance']))
                            res.append(aux_hija)
                            parent_aux += abs(account_hija['balance'])
                res[0][2] = parent_aux
                res[0][3] = parent_aux
        return res

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_end'] = self.datas['form']['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_end']
        res['end']=end.upper()
        return res

    def lineas(self, resumen):
        result = {}
        result['act'] = self.lineas_individual(resumen,'act')
        result['ant'] = self.lineas_individual(resumen,'ant')
        return result

    def lineas_individual(self, resumen, tipo):
        fiscal_obj = self.pool.get('account.fiscalyear')
        context = {}
        cr = self.cr
        uid = self.uid
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        if tipo!='act':
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_inicial_aux = date_aux - relativedelta(years=1)
            date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
            date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux = date_aux - relativedelta(years=1)
            date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
        result = {}
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        fiscal = fiscal_obj.browse(self.cr, self.uid, fiscalyear_id)
        if date_final_reporte==fiscal.date_stop:
            date_aux_f = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux_f = date_aux_f - timedelta(days=1)
            date_final_reporte = date_final_aux_f.strftime('%Y-%m-%d')
        if tipo=='ant':
            fiscalyear_ids = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
            if fiscalyear_ids:
                fiscalyear_id = fiscalyear_ids[0]
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        ctx = context.copy()
        c62401 = ['62401','62402','62403','62404']
        c63801 = ['63801','63802','63803','63804','63807']
        c62435  = ['62435','63835']
        c621 =  ['621','623','631','633','634']
        c63501 = ['63501','63504']
        c626 = ['626','636']
        c62501 = ['62501','62502','62503','62504']
        c63502 = ['63502','63503','63507']
        c62421 = ['62421','62422','62423','62424','62425','62426','62427']
        c63821 = ['63821','63822','63823','63824','63825','63826','63827']
        c62521 = ['62521','62522','62523','62524']
        c63851 = ['63851','63852','63853','63854','63855','63856','63857','63858','63859','63860',
                 '63861','63862','63863','63864','63865','63866','63867','63868','63869','63870',
                 '63871','63872','63873','63874','63875','63876','63877','63878','63879','63880',
                 '63881','63882','63883','63884','63885','63886','63887','63888','63889','63890',
                 '63891','63892','63893']
        c629 =  ['629','639','61803']
        codes = c62401 + c63801 + c62435 + c621 + c63501 + c626 + c62501 + c63502 + c62421 + c63821 + c62521 + c63851 + c629
        account_ids = account_obj.search(cr, uid, [('code','in', codes)])
        ctx.update({'fiscalyear': fiscalyear_id})
        ctx.update({'state': 'posted'})
        ctx.update({'date_from': date_inicial_reporte,
                    'date_to': date_final_reporte})
        accounts = account_obj.read(cr, uid, account_ids, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        accounts_by_id = {}
        for account in accounts:
            accounts_by_id[account['code']] = account
        for code in codes:
            if accounts_by_id.get(code,False) == False:
                accounts_by_id.update({code: {'code': code, 'balance': 0} })
        #####################
        sum_aux = 0
        for code_aux in c62401:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62401/04': {'62401/04': '62401/04', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c63801:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'63801/04': {'63801/04': '63801/04', 'balance': sum_aux}})
        #####################
        accounts_by_id.update({'63501-04': {'63501-04': '63501-04', 'balance': accounts_by_id['63501']['balance']+accounts_by_id['63504']['balance']}})
        #####################
        sum_aux = 0
        for code_aux in c62501:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62501/04': {'62501/04': '62501/04', 'balance': sum_aux}})
        #####################
        accounts_by_id.update({'63502/03-07': {'63502/03-07': '63502/03-07', 'balance': accounts_by_id['63502']['balance']+accounts_by_id['63503']['balance']+accounts_by_id['63507']['balance']}})
        #####################
        sum_aux = 0
        for code_aux in c62421:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62421/27': {'62421/27': '62421/27', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c63821:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'63821/27': {'63821/27': '63821/27', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c62521:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62521/24': {'62521/24': '62521/24', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c62521:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'62521/24': {'62521/24': '62521/24', 'balance': sum_aux}})
        #####################
        sum_aux = 0
        for code_aux in c63851:
            sum_aux+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'63851/93': {'63851/93': '63851/93', 'balance': sum_aux}})
        ####################
        resultado_explotacion = (accounts_by_id['62401/04']['balance']+accounts_by_id['63801/04']['balance'])*(-1)
        accounts_by_id.update({'resultado_explotacion': {'resultado_explotacion': 'resultado_explotacion', 'balance': resultado_explotacion}})
        ####################
        resultado_operacion = (accounts_by_id['621']['balance']+accounts_by_id['623']['balance']+accounts_by_id['631']['balance']+accounts_by_id['633']['balance']+accounts_by_id['634']['balance']+accounts_by_id['63501-04']['balance'])*(-1)
        accounts_by_id.update({'resultado_operacion': {'resultado_operacion': 'resultado_operacion', 'balance': resultado_operacion}})
        ####################
        transferencias_netas = (accounts_by_id['626']['balance']+accounts_by_id['636']['balance'])*(-1)
        accounts_by_id.update({'transferencias_netas': {'transferencias_netas': 'transferencias_netas', 'balance': transferencias_netas}})
        ####################
        resultado_financiero = (accounts_by_id['62501/04']['balance']+accounts_by_id['63502/03-07']['balance'])*(-1)
        accounts_by_id.update({'resultado_financiero': {'resultado_financiero': 'resultado_financiero', 'balance': resultado_financiero}})
        otros_ingresos_gastos = (accounts_by_id['62421/27']['balance']+accounts_by_id['63821/27']['balance']+accounts_by_id['62521/24']['balance']+accounts_by_id['63851/93']['balance']+accounts_by_id['629']['balance']+accounts_by_id['639']['balance'])*(-1)
        accounts_by_id.update({'otros_ingresos_gastos': {'otros_ingresos_gastos': 'otros_ingresos_gastos', 'balance': otros_ingresos_gastos}})
        resultado_ejercicio = resultado_explotacion + resultado_operacion + transferencias_netas + resultado_financiero + otros_ingresos_gastos
        accounts_by_id.update({'resultado_ejercicio': {'resultado_ejercicio': 'resultado_ejercicio', 'balance': resultado_ejercicio}})    
        return accounts_by_id
 
report_sxw.report_sxw('report.EstadoResultadosAuxiliar','account.account',
                      'addons/gt_gob_report/report/report_estado_resultados_auxiliar.mako',
                      parser=EstadoResultadosAuxiliar)

class EstadoSituacion(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(EstadoSituacion, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            'lineas': self.lineas,
         })

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_end'] = self.datas['form']['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_end']
        res['end']=end.upper()
        return res

    def lineas(self, resumen):
        result = {}
        result['act'] = self.lineas_individual(resumen,'act')
        result['ant'] = self.lineas_individual(resumen,'ant')
        return result

    def lineas_individual(self, resumen, tipo):
        context = {}
        cr = self.cr
        uid = self.uid
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        if tipo!='act':
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_inicial_aux = date_aux - relativedelta(years=1)
            date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
            date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux = date_aux - relativedelta(years=1)
            date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
        result = {}
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        if tipo=='ant':
            fiscalyear_ids = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
            if fiscalyear_ids:
                fiscalyear_id = fiscalyear_ids[0]
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        ctx = context.copy()
        codes = ['111','112','113','121','122','123','124','132','134','135','141','14199','142','14299','144','14499','145','14599','151','15198',
                 '152','15298','125','12599','126','12699','131','133','212','213','221','222','223','224','225','226','611','612','61801','619','618','911',
                 '921','62','63']
        account_ids = account_obj.search(cr, uid, [('code','in', codes)])
        ctx.update({'fiscalyear': fiscalyear_id})
        ctx.update({'state': 'posted'})
        ctx.update({'date_from': date_inicial_reporte,
                    'date_to': date_final_reporte})
        accounts = account_obj.read(cr, uid, account_ids, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        accounts_by_id = {}
        for account in accounts:
            accounts_by_id[account['code']] = account
        for code in codes:
            if accounts_by_id.get(code,False) == False:
                accounts_by_id.update({code: {'code': code, 'balance': 0} })
        ######################33
        corriente = accounts_by_id['111']['balance']+accounts_by_id['112']['balance']+accounts_by_id['113']['balance']+accounts_by_id['121']['balance']+accounts_by_id['122']['balance']+accounts_by_id['123']['balance']+accounts_by_id['124']['balance']+accounts_by_id['132']['balance']+accounts_by_id['134']['balance']+accounts_by_id['135']['balance']
        accounts_by_id.update({'corriente': {'corriente': 'corriente', 'balance': corriente}})
        largo_plazo = 0#accounts_by_id['122']['balance']+accounts_by_id['123']['balance']+accounts_by_id['124']['balance']
        accounts_by_id.update({'largo_plazo': {'largo_plazo': 'largo_plazo', 'balance': largo_plazo}})
#        activos_fijos = accounts_by_id['141']['balance']+accounts_by_id['14199']['balance']+accounts_by_id['142']['balance']+accounts_by_id['14299']['balance']+accounts_by_id['144']['balance']+accounts_by_id['14499']['balance']+accounts_by_id['145']['balance']+accounts_by_id['14599']['balance']
        activos_fijos = accounts_by_id['141']['balance']+accounts_by_id['142']['balance']+accounts_by_id['144']['balance']+accounts_by_id['145']['balance']
        accounts_by_id.update({'activos_fijos': {'activos_fijos': 'activos_fijos', 'balance': activos_fijos}})
#        inversiones = accounts_by_id['151']['balance']+accounts_by_id['15198']['balance']+accounts_by_id['152']['balance']+accounts_by_id['15298']['balance']
        inversiones = accounts_by_id['151']['balance']+accounts_by_id['152']['balance']
        accounts_by_id.update({'inversiones': {'inversiones': 'inversiones', 'balance': inversiones}})
        otros = accounts_by_id['125']['balance']+accounts_by_id['12599']['balance']+accounts_by_id['126']['balance']+accounts_by_id['12699']['balance']+accounts_by_id['131']['balance']+accounts_by_id['133']['balance']
        accounts_by_id.update({'otros': {'otros': 'otros', 'balance': otros}})
        activo = corriente + largo_plazo + activos_fijos + inversiones + otros
        accounts_by_id.update({'activo': {'activo': 'activo', 'balance': activo}})
        #####################
        pcorrientes = accounts_by_id['212']['balance']+accounts_by_id['213']['balance']
        accounts_by_id.update({'pcorrientes': {'pcorrientes': 'pcorrientes', 'balance': pcorrientes}})
        plargo_plazo = accounts_by_id['222']['balance']+accounts_by_id['223']['balance']+accounts_by_id['224']['balance']
        accounts_by_id.update({'plargo_plazo': {'plargo_plazo': 'plargo_plazo', 'balance': plargo_plazo}})
        potros = accounts_by_id['225']['balance']+accounts_by_id['226']['balance']
        accounts_by_id.update({'potros': {'potros': 'potros', 'balance': potros}})
        pasivo = pcorrientes + plargo_plazo + potros
        accounts_by_id.update({'pasivo': {'pasivo': 'pasivo', 'balance': pasivo}})
        ######################
        aux_vigente = (abs(accounts_by_id['62']['balance'])-abs(accounts_by_id['63']['balance'])) * (-1)
        patrimonio = accounts_by_id['611']['balance']+accounts_by_id['612']['balance']+aux_vigente+accounts_by_id['619']['balance']+accounts_by_id['61801']['balance']
#        patrimonio = accounts_by_id['611']['balance']+accounts_by_id['612']['balance']+accounts_by_id['618']['balance']+accounts_by_id['61801']['balance']+accounts_by_id['619']['balance']
        accounts_by_id.update({'patrimonio': {'patrimonio': 'patrimonio', 'balance': patrimonio}})
        accounts_by_id.update({'pasivo_patrimonio': {'pasivo_patrimonio': 'pasivo_patrimonio', 'balance': patrimonio + pasivo}})
        return accounts_by_id
        
 
report_sxw.report_sxw('report.EstadoSituacion','account.account',
                      'addons/gt_gob_report/report/report_estado_situacion.mako',
                      parser=EstadoSituacion)

class EstadoSituacionAux(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(EstadoSituacionAux, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            'lineas': self.lineas,
            'get_saldo_situacion':self.get_saldo_situacion,
            'get_firmas':self.get_firmas,
         })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux

    def get_saldo_situacion(self, code,desde,hasta):
        account_obj = self.pool.get('account.account')
        account_parent_ids = account_obj.search(self.cr, self.uid, [('code','=',code)])
        res= []
        ctx = {}
        ctx_ant = {}
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        ctx['fiscalyear'] = fiscalyear_id
        ctx['state'] = 'posted'
        ctx['date_from'] = date_inicial_reporte
        ctx['date_to'] = date_final_reporte
        #sacar anio anterior
        date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
        date_inicial_aux = date_aux - relativedelta(years=1)
        date_inicial_reporte_ant = date_inicial_aux.strftime('%Y-%m-%d')
        date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
        date_final_aux = date_aux - relativedelta(years=1)
        date_final_reporte_ant = date_final_aux.strftime('%Y-%m-%d')
        fiscalyear_ids = self.pool.get('account.fiscalyear').search(self.cr, self.uid, [('date_start','<=', date_inicial_reporte_ant),('date_stop','>=',date_final_reporte_ant)])
        if fiscalyear_ids:
            fiscalyear_id_ant = fiscalyear_ids[0]
        ctx_ant['fiscalyear'] = fiscalyear_id_ant
        ctx_ant['state'] = 'posted'
        ctx_ant['date_from'] = date_inicial_reporte_ant
        ctx_ant['date_to'] = date_final_reporte_ant
        if account_parent_ids:
            aux_parent = []
            account_parent = account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx)
            account_parent_ant = account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx_ant)
            if abs(account_parent[0]['balance'])!=0:
                aux_parent.append(account_parent[0]['code_aux'])
                aux_parent.append(account_parent[0]['name'])
                aux_parent.append(abs(account_parent[0]['balance']))
                aux_parent.append(abs(account_parent_ant[0]['balance']))
                res.append(aux_parent)
                account_hijas_ids = account_obj.search(self.cr, self.uid, [('parent_id','=',account_parent_ids[0]),('code','>=',desde),('code','<=',hasta)])
                if account_hijas_ids:
                    for account_hija in account_obj.read(self.cr, self.uid, account_hijas_ids,['id','code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx):
                        account_hija_ant = account_obj.read(self.cr, self.uid, account_hija['id'],['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx_ant)
                        if abs(account_hija['balance'])!=0:
                            aux_hija = []
                            aux_hija.append(account_hija['code_aux'])
                            aux_hija.append(account_hija['name'])
                            aux_hija.append(abs(account_hija['balance']))
                            aux_hija.append(abs(account_hija_ant['balance']))
                            res.append(aux_hija)
        return res

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_end'] = self.datas['form']['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_end']
        res['end']=end.upper()
        return res

    def lineas(self, resumen):
        result = {}
        result['act'] = self.lineas_individual(resumen,'act')
        result['ant'] = self.lineas_individual(resumen,'ant')
        return result

    def lineas_individual(self, resumen, tipo):
        context = {}
        cr = self.cr
        uid = self.uid
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        if tipo!='act':
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_inicial_aux = date_aux - relativedelta(years=1)
            date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
            date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux = date_aux - relativedelta(years=1)
            date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
        result = {}
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        if tipo=='ant':
            fiscalyear_ids = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
            if fiscalyear_ids:
                fiscalyear_id = fiscalyear_ids[0]
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        ctx = context.copy()
        codes = ['1','111','112','113','121','122','123','124','132','134','135','141','14199','142','14299','143','14399','144','14499','145','14599','151','15198',
                 '152','15298','125','12599','126','12699','131','133','212','213','221','222','223','224','225','226','611','612','61801','619','618','911',
                 '921','62','63','6']
        account_ids = account_obj.search(cr, uid, [('code','in', codes)])
        ctx.update({'fiscalyear': fiscalyear_id})
        ctx.update({'state': 'posted'})
        ctx.update({'date_from': date_inicial_reporte,
                    'date_to': date_final_reporte})
        accounts = account_obj.read(cr, uid, account_ids, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        accounts_by_id = {}
        for account in accounts:
            accounts_by_id[account['code']] = account
        for code in codes:
            if accounts_by_id.get(code,False) == False:
                accounts_by_id.update({code: {'code': code, 'balance': 0} })
        ######################33
        corriente = accounts_by_id['111']['balance']+accounts_by_id['112']['balance']+accounts_by_id['113']['balance']+accounts_by_id['121']['balance']+accounts_by_id['122']['balance']+accounts_by_id['123']['balance']+accounts_by_id['124']['balance']+accounts_by_id['131']['balance']+accounts_by_id['132']['balance']+accounts_by_id['134']['balance']+accounts_by_id['135']['balance']
        accounts_by_id.update({'corriente': {'corriente': 'corriente', 'balance': corriente}})
        largo_plazo = accounts_by_id['122']['balance']+accounts_by_id['123']['balance']+accounts_by_id['124']['balance']
        accounts_by_id.update({'largo_plazo': {'largo_plazo': 'largo_plazo', 'balance': largo_plazo}})
#        activos_fijos = accounts_by_id['141']['balance']+accounts_by_id['14199']['balance']+accounts_by_id['142']['balance']+accounts_by_id['14299']['balance']+accounts_by_id['144']['balance']+accounts_by_id['14499']['balance']+accounts_by_id['145']['balance']+accounts_by_id['14599']['balance']
        activos_fijos = accounts_by_id['141']['balance']+accounts_by_id['142']['balance']+accounts_by_id['143']['balance']+accounts_by_id['144']['balance']+accounts_by_id['145']['balance']
        accounts_by_id.update({'activos_fijos': {'activos_fijos': 'activos_fijos', 'balance': activos_fijos}})
#        inversiones = accounts_by_id['151']['balance']+accounts_by_id['15198']['balance']+accounts_by_id['152']['balance']+accounts_by_id['15298']['balance']
        inversiones = accounts_by_id['151']['balance']+accounts_by_id['152']['balance']
        accounts_by_id.update({'inversiones': {'inversiones': 'inversiones', 'balance': inversiones}})
        otros = accounts_by_id['125']['balance']+accounts_by_id['12599']['balance']+accounts_by_id['126']['balance']+accounts_by_id['12699']['balance']+accounts_by_id['131']['balance']+accounts_by_id['133']['balance']
        accounts_by_id.update({'otros': {'otros': 'otros', 'balance': otros}})
        activo = accounts_by_id['1']['balance']#corriente + largo_plazo + activos_fijos + inversiones + otros
        accounts_by_id.update({'activo': {'activo': 'activo', 'balance': activo}})
        #####################
        pcorrientes = accounts_by_id['212']['balance']+accounts_by_id['213']['balance']
        accounts_by_id.update({'pcorrientes': {'pcorrientes': 'pcorrientes', 'balance': pcorrientes}})
        plargo_plazo = accounts_by_id['222']['balance']+accounts_by_id['223']['balance']+accounts_by_id['224']['balance']
        accounts_by_id.update({'plargo_plazo': {'plargo_plazo': 'plargo_plazo', 'balance': plargo_plazo}})
        potros = accounts_by_id['225']['balance']+accounts_by_id['226']['balance']
        accounts_by_id.update({'potros': {'potros': 'potros', 'balance': potros}})
        pasivo = pcorrientes + plargo_plazo + potros
        accounts_by_id.update({'pasivo': {'pasivo': 'pasivo', 'balance': pasivo}})
        ######################
        aux_vigente = (abs(accounts_by_id['62']['balance'])-abs(accounts_by_id['63']['balance'])) * (-1)
        patrimonio = accounts_by_id['6']['balance']
#        patrimonio = accounts_by_id['611']['balance']+accounts_by_id['612']['balance']+aux_vigente+accounts_by_id['619']['balance']
#        patrimonio = accounts_by_id['611']['balance']+accounts_by_id['612']['balance']+accounts_by_id['618']['balance']+accounts_by_id['61801']['balance']+accounts_by_id['619']['balance']
        accounts_by_id.update({'patrimonio': {'patrimonio': 'patrimonio', 'balance': patrimonio}})
        accounts_by_id.update({'pasivo_patrimonio': {'pasivo_patrimonio': 'pasivo_patrimonio', 'balance': patrimonio + pasivo}})
        return accounts_by_id
        
 
report_sxw.report_sxw('report.EstadoSituacionAux','account.account',
                      'addons/gt_gob_report/report/report_estado_situacion_aux.mako',
                      parser=EstadoSituacionAux)

class EstadoSituacionAuxiliar(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(EstadoSituacionAuxiliar, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            'lineas': self.lineas,
            'get_firmas':self.get_firmas,
         })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_end'] = self.datas['form']['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_end']
        res['end']=end.upper()
        return res

    def lineas(self, resumen):
        result = {}
        result['act'] = self.lineas_individual(resumen,'act')
        result['ant'] = self.lineas_individual(resumen,'ant')
        return result

    def lineas_individual(self, resumen, tipo):
        context = {}
        cr = self.cr
        uid = self.uid
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        if tipo!='act':
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_inicial_aux = date_aux - relativedelta(years=1)
            date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
            date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux = date_aux - relativedelta(years=1)
            date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
        result = {}
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        if tipo=='ant':
            fiscalyear_ids = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
            if fiscalyear_ids:
                fiscalyear_id = fiscalyear_ids[0]
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        ctx = context.copy()
        codes = ['111','112','113','121','122','123','124','132','134','135','141','14199','142','14299','144','14499','145','14599','151','15198',
                 '152','15298','125','12599','126','12699','131','133','212','213','221','222','223','224','225','226','611','612','61801','619','618','911',
                 '921']
        account_ids = account_obj.search(cr, uid, [('code','in', codes)])
        ctx.update({'fiscalyear': fiscalyear_id})
        ctx.update({'state': 'posted'})
        ctx.update({'date_from': date_inicial_reporte,
                    'date_to': date_final_reporte})
        accounts = account_obj.read(cr, uid, account_ids, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        accounts_by_id = {}
        for account in accounts:
            accounts_by_id[account['code']] = account
        for code in codes:
            if accounts_by_id.get(code,False) == False:
                accounts_by_id.update({code: {'code': code, 'balance': 0} })
        ######################33
        corriente = accounts_by_id['111']['balance']+accounts_by_id['112']['balance']+accounts_by_id['113']['balance']+accounts_by_id['121']['balance']+accounts_by_id['122']['balance']+accounts_by_id['123']['balance']+accounts_by_id['124']['balance']+accounts_by_id['131']['balance']+accounts_by_id['132']['balance']+accounts_by_id['134']['balance']+accounts_by_id['135']['balance']
        accounts_by_id.update({'corriente': {'corriente': 'corriente', 'balance': corriente}})
        largo_plazo = accounts_by_id['122']['balance']+accounts_by_id['123']['balance']+accounts_by_id['124']['balance']
        accounts_by_id.update({'largo_plazo': {'largo_plazo': 'largo_plazo', 'balance': largo_plazo}})
        activos_fijos = accounts_by_id['141']['balance']+accounts_by_id['14199']['balance']+accounts_by_id['142']['balance']+accounts_by_id['14299']['balance']+accounts_by_id['144']['balance']+accounts_by_id['14499']['balance']+accounts_by_id['145']['balance']+accounts_by_id['14599']['balance']+accounts_by_id['143']['balance']+accounts_by_id['14399']['balance']
        accounts_by_id.update({'activos_fijos': {'activos_fijos': 'activos_fijos', 'balance': activos_fijos}})
        inversiones = accounts_by_id['151']['balance']+accounts_by_id['15198']['balance']+accounts_by_id['152']['balance']+accounts_by_id['15298']['balance']
        accounts_by_id.update({'inversiones': {'inversiones': 'inversiones', 'balance': inversiones}})
        otros = accounts_by_id['125']['balance']+accounts_by_id['12599']['balance']+accounts_by_id['126']['balance']+accounts_by_id['12699']['balance']+accounts_by_id['131']['balance']+accounts_by_id['133']['balance']
        accounts_by_id.update({'otros': {'otros': 'otros', 'balance': otros}})
        activo = corriente + largo_plazo + activos_fijos + inversiones + otros
        accounts_by_id.update({'activo': {'activo': 'activo', 'balance': activo}})
        #####################
        pcorrientes = accounts_by_id['212']['balance']+accounts_by_id['213']['balance']
        accounts_by_id.update({'pcorrientes': {'pcorrientes': 'pcorrientes', 'balance': pcorrientes}})
        plargo_plazo = accounts_by_id['222']['balance']+accounts_by_id['223']['balance']+accounts_by_id['224']['balance']
        accounts_by_id.update({'plargo_plazo': {'plargo_plazo': 'plargo_plazo', 'balance': plargo_plazo}})
        potros = accounts_by_id['225']['balance']+accounts_by_id['226']['balance']
        accounts_by_id.update({'potros': {'potros': 'potros', 'balance': potros}})
        pasivo = pcorrientes + plargo_plazo + potros
        accounts_by_id.update({'pasivo': {'pasivo': 'pasivo', 'balance': pasivo}})
        ######################
        patrimonio = accounts_by_id['611']['balance']+accounts_by_id['612']['balance']+accounts_by_id['618']['balance']+accounts_by_id['61801']['balance']+accounts_by_id['619']['balance']
        accounts_by_id.update({'patrimonio': {'patrimonio': 'patrimonio', 'balance': patrimonio}})
        accounts_by_id.update({'pasivo_patrimonio': {'pasivo_patrimonio': 'pasivo_patrimonio', 'balance': patrimonio + pasivo}})
        return accounts_by_id
        
 
report_sxw.report_sxw('report.EstadoSituacionAuxiliar','account.account',
                      'addons/gt_gob_report/report/report_estado_situacion_auxiliar.mako',
                      parser=EstadoSituacionAuxiliar)


class FlujoEfectivo(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(FlujoEfectivo, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars':self._vars,
            'lineas': self.lineas,
            'get_firmas':self.get_firmas,
         })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux
    
    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_end'] = self.datas['form']['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_end']
        res['end']=end.upper()
        return res

    def lineas(self, resumen):
        result = {}
        result['act'] = self.lineas_individual(resumen,'act')
        result['ant'] = self.lineas_individual(resumen,'ant')
        return result

    def lineas_individual(self, resumen, tipo):
        fiscal_obj = self.pool.get('account.fiscalyear')
        context = {}
        cr = self.cr
        uid = self.uid
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        result = {}
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        if tipo!='act':
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_inicial_aux = date_aux - relativedelta(years=1)
            date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
            date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux = date_aux - relativedelta(years=1)
            date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
            fiscalyear_ids = fiscal_obj.search(cr, uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
            if fiscalyear_ids:
                fiscalyear_id = fiscalyear_ids[0]
                fiscal_anterior = fiscal_obj.browse(cr, uid, fiscalyear_id)
#                date_inicial_reporte = fiscal_anterior.date_start
#                date_final_reporte = fiscal_anterior.date_stop
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        ctx = context.copy()
        ctx2 = context.copy()
        fuentes_corrientes = ['11311','11313','11314','11317','11318','11319']
        usos_corrientes = ['21351','21352','21353','21355','21356','21357','21358']
        fuentes_capital = ['11324','11328']
        usos_produccion = ['21361','21363','21367','21371','21373','21375','21377','21378','21384','21385','21387','11327','21388']

        fuentes_financiamiento = ['11336','11397','11398']
        usos_financiamiento = ['21396','21397','21398']
        flujos_no_presupuestariosc = ['11340','11381','11382','11383']  #11381
        flujos_no_presupuestariosd = ['21315','21340','21381','21382','21383','21395']
        variaciones = ['111','112','61991','212']
        codes = fuentes_corrientes + usos_corrientes + fuentes_capital + usos_produccion
        codes = codes + fuentes_financiamiento + usos_financiamiento + flujos_no_presupuestariosc + flujos_no_presupuestariosd + variaciones
        account_ids = account_obj.search(cr, uid, [('code','in', codes)])
        ctx.update({'fiscalyear': fiscalyear_id})
        ctx.update({'state': 'posted'})
        ctx.update({'date_from': date_inicial_reporte,
                    'date_to': date_final_reporte})
        accounts = account_obj.read(cr, uid, account_ids, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        accounts_by_id = {}
        for account in accounts:
            accounts_by_id[account['code']] = account
        for code in codes:
            if accounts_by_id.get(code,False) == False:
                accounts_by_id.update({code: {'code': code, 'balance': 0, 'credit':0 , 'debit': 0} })
        print "3", accounts_by_id['11381']
        #######################
        sum_fuentes_corrientes = 0
        for code_aux in fuentes_corrientes:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['credit'] #aqui se hace versa
            sum_fuentes_corrientes+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'fuentes_corrientes': {'fuentes_corrientes': 'fuentes_corrientes', 'balance': sum_fuentes_corrientes}})
        #######################
        sum_usos_corrientes = 0
        for code_aux in usos_corrientes:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['debit']
            sum_usos_corrientes+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'usos_corrientes': {'usos_corrientes': 'usos_corrientes', 'balance': sum_usos_corrientes}})
        ######################
        sd_corriente = sum_fuentes_corrientes - sum_usos_corrientes
        accounts_by_id.update({'sd_corriente': {'sd_corriente': 'sd_corriente', 'balance': sd_corriente}})
        #####################
        sum_fuentes_capital = 0
        for code_aux in fuentes_capital:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['credit']
            sum_fuentes_capital+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'fuentes_capital': {'fuentes_capital': 'fuentes_capital', 'balance': sum_fuentes_capital}})
        #####################
        sum_usos_produccion = 0
        for code_aux in usos_produccion:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['debit']
            sum_usos_produccion+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'usos_produccion': {'usos_produccion': 'usos_produccion', 'balance': sum_usos_produccion}})
        #####################
        sd_capital = sum_fuentes_capital - sum_usos_produccion
        accounts_by_id.update({'sd_capital': {'sd_capital': 'sd_capital', 'balance': sd_capital}})
        #####################
        sd_bruto = sd_corriente + sd_capital
        accounts_by_id.update({'sd_bruto': {'sd_bruto': 'sd_bruto', 'balance': sd_bruto}})

        #######################
        sum_fuentes_financiamiento = 0
        for code_aux in fuentes_financiamiento:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['credit']
            sum_fuentes_financiamiento+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'fuentes_financiamiento': {'fuentes_financiamiento': 'fuentes_financiamiento', 'balance': sum_fuentes_financiamiento}})
        #######################
        sum_usos_financiamiento = 0
        for code_aux in usos_financiamiento:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['debit']
            sum_usos_financiamiento+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'usos_financiamiento': {'usos_financiamiento': 'usos_financiamiento', 'balance': sum_usos_financiamiento}})
        ######################

        sd_financiamiento = sum_fuentes_financiamiento - sum_usos_financiamiento
        accounts_by_id.update({'sd_financiamiento': {'sd_financiamiento': 'sd_financiamiento', 'balance': sd_financiamiento}})
                
        sum_flujos_no_presupuestariosc = 0
        for code_aux in flujos_no_presupuestariosc:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['debit']#accounts_by_id[code_aux]['credit']  # debit deberia ser comentando esta linea
            sum_flujos_no_presupuestariosc+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'flujos_no_presupuestariosc': {'flujos_no_presupuestariosc': 'flujos_no_presupuestariosc', 'balance': sum_flujos_no_presupuestariosc}})
        ######################
        sum_flujos_no_presupuestariosd = 0
        for code_aux in flujos_no_presupuestariosd:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['debit']
            sum_flujos_no_presupuestariosd+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'flujos_no_presupuestariosd': {'flujos_no_presupuestariosd': 'flujos_no_presupuestariosd', 'balance': sum_flujos_no_presupuestariosd}})
        ######################
        flujos_netos = sum_flujos_no_presupuestariosc - sum_flujos_no_presupuestariosd
        accounts_by_id.update({'flujos_netos': {'flujos_netos': 'flujos_netos', 'balance': flujos_netos}})
        print "4", accounts_by_id['11381']
        #VARIACIONES NO PRESUPUESTARIAS
        accounts_by_id_inicial = {}
        accounts_by_id_final = {}
        account_move_obj = self.pool.get('account.move') 
        asiento_inicial = account_move_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear_id),('is_start','=',True)])
        codes2 = ['111','112','61991','212']
        account_ids2 = account_obj.search(cr, uid, [('code','in', codes2)])
        nuevo_contexto = {'move_ids': asiento_inicial} # contexto agregado en modulo base account, en archivo account_move_line.py
        ctx2.update({'fiscalyear': fiscalyear_id})
        ctx2.update({'state': 'posted'})
        ctx2.update({'date_from': date_inicial_reporte,
                     'date_to': date_inicial_reporte})
#        cuentas2_inicial = account_obj.read(cr, uid, account_ids2, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx2)
        cuentas2_inicial = account_obj.read(cr, uid, account_ids2, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], nuevo_contexto)
        cuentas2_final = account_obj.read(cr, uid, account_ids2, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        for account in cuentas2_inicial:
            accounts_by_id_inicial[account['code']] = account
        for account in cuentas2_final:
            accounts_by_id_final[account['code']] = account            
        for code in codes2:
            if accounts_by_id_inicial.get(code,False) == False:
                accounts_by_id_inicial.update({code: {'code': code, 'balance': 0} })
            if accounts_by_id_final.get(code,False) == False:
                accounts_by_id_final.update({code: {'code': code, 'balance': 0} })
        print "5", accounts_by_id['11381']
        accounts_by_id.update({'111': {'111': '111', 'balance': accounts_by_id_inicial['111']['balance'] - accounts_by_id_final['111']['balance']}})
        accounts_by_id.update({'112': {'112': '112', 'balance': accounts_by_id_inicial['112']['balance'] - accounts_by_id_final['112']['balance']}})
        accounts_by_id.update({'61991': {'61991': '61991', 'balance': accounts_by_id_inicial['61991']['balance'] - accounts_by_id_final['61991']['balance']}})
        accounts_by_id.update({'212': {'212': '212', 'balance': abs(accounts_by_id_final['212']['balance']) - abs(accounts_by_id_inicial['212']['balance'])}})
        variaciones_netas = accounts_by_id['111']['balance'] + accounts_by_id['112']['balance'] + accounts_by_id['61991']['balance'] + accounts_by_id['212']['balance']
        accounts_by_id.update({'variaciones_netas': {'variaciones_netas': 'variaciones_netas', 'balance': variaciones_netas}})

        sd_bruto2 = sd_financiamiento + flujos_netos + variaciones_netas
        accounts_by_id.update({'sd_bruto2': {'sd_bruto2': 'sd_bruto2', 'balance': sd_bruto2}})
        print "ACCOUTS", accounts_by_id['11381']
        return accounts_by_id
 
report_sxw.report_sxw('report.FlujoEfectivo','account.account',
                      'addons/gt_gob_report/report/report_flujo_efectivo.mako',
                      parser=FlujoEfectivo)

class FlujoEfectivoAuxiliar(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(FlujoEfectivoAuxiliar, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars':self._vars,
            'lineas': self.lineas,
            'get_saldo_flujo':self.get_saldo_flujo,
            'get_saldo_resta':self.get_saldo_resta,
            'get_firmas':self.get_firmas,
         })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux

    def get_saldo_flujo(self, code,desde,hasta,tipo):
        account_obj = self.pool.get('account.account')
        account_parent_ids = account_obj.search(self.cr, self.uid, [('code','=',code)])
        res= []
        ctx = {}
        ctx2 = {}
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        ctx['fiscalyear'] = fiscalyear_id
        ctx['state'] = 'posted'
        ctx['date_from'] = date_inicial_reporte
        ctx['date_to'] = date_final_reporte
        #anio anterior
        date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
        date_inicial_aux = date_aux - relativedelta(years=1)
        date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
        date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
        date_final_aux = date_aux - relativedelta(years=1)
        date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
        fiscalyear_ids = self.pool.get('account.fiscalyear').search(self.cr, self.uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
        if fiscalyear_ids:
            fiscalyear_id2 = fiscalyear_ids[0]
        ctx2['fiscalyear'] = fiscalyear_id2
        ctx2['state'] = 'posted'
        ctx2['date_from'] = date_inicial_reporte
        ctx2['date_to'] = date_final_reporte
        if account_parent_ids:
            aux_parent = []
            account_parent = account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx)
            account_parent2 = account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx2)
            if abs(account_parent[0][tipo])>0:
                aux_parent.append(account_parent[0]['code_aux'])
                aux_parent.append(account_parent[0]['name'])
                aux_parent.append(abs(account_parent[0][tipo]))
                aux_parent.append(abs(account_parent2[0][tipo]))
                res.append(aux_parent)
                account_hijas_ids = account_obj.search(self.cr, self.uid, [('parent_id','=',account_parent_ids[0]),('code','>=',desde),('code','<=',hasta)])
                if account_hijas_ids:
                    for account_hija in account_obj.read(self.cr, self.uid, account_hijas_ids,['id','code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx):
                        account_hijaa = account_obj.read(self.cr, self.uid, account_hijas['id'],['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx2)
                        if abs(account_hija[tipo])>0:
                            aux_hija = []
                            aux_hija.append(account_hija['code_aux'])
                            aux_hija.append(account_hija['name'])
                            aux_hija.append(abs(account_hija[tipo]))
                            aux_hija.append(abs(account_hijaa[tipo]))
                            res.append(aux_hija)
        return res

    #aqui se debe pasar si es actual o anterios
    def get_saldo_resta(self, code,desde,hasta,lista):
        year_obj = self.pool.get('account.fiscalyear')
        account_obj = self.pool.get('account.account')
        account_parent_ids = account_obj.search(self.cr, self.uid, [('code','=',code)])
        res= []
        ctx = {}
        ctx2 = {}
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        year = year_obj.browse(self.cr, self.uid, fiscalyear_id)
        ctx['fiscalyear'] = fiscalyear_id
        ctx['state'] = 'posted'
        ctx['date_from'] = date_inicial_reporte
        ctx['date_to'] = date_final_reporte
        ctx2['fiscalyear'] = fiscalyear_id
        ctx2['state'] = 'posted'
        ctx2['date_from'] = year.date_start
        ctx2['date_to'] = year.date_start
        if account_parent_ids:
            aux_parent = []
            account_parent=account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx)
            if abs(account_parent[0]['balance'])>0:
                aux_parent.append(account_parent[0]['code_aux'])
                aux_parent.append(account_parent[0]['name'])
            account_parent_i=account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx2)
            aux_resta = 0
            if lista[0]=='final': #inicial - final
                aux_resta = account_parent[0]['balance'] - account_parent_i[0]['balance']
            else:
                aux_resta = account_parent_i[0]['balance'] - account_parent[0]['balance']
            aux_parent.append(aux_resta)
            #aqui se debe sacar de anio anterior es la columna 4
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_inicial_aux = date_aux - relativedelta(years=1)
            date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
            date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux = date_aux - relativedelta(years=1)
            date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
            fiscalyear_ids = self.pool.get('account.fiscalyear').search(self.cr, self.uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
            year = year_obj.browse(self.cr, self.uid, fiscalyear_ids[0])
            ctx['fiscalyear'] = year.id
            ctx['state'] = 'posted'
            ctx['date_from'] = date_inicial_reporte
            ctx['date_to'] = date_final_reporte
            ctx2['fiscalyear'] = year.id
            ctx2['state'] = 'posted'
            ctx2['date_from'] = year.date_start
            ctx2['date_to'] = year.date_start
#            import pdb
#            pdb.set_trace()
            if account_parent_ids:
                account_parent=account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx)
                account_parent_i=account_obj.read(self.cr, self.uid, account_parent_ids,['code','code_aux','name','debit','credit', 'balance', 'parent_id','level'], ctx2)
                aux_resta = 0
                if lista[0]=='final': #inicial - final
                    aux_resta = account_parent[0]['balance'] - account_parent_i[0]['balance']
                else:
                    aux_resta = account_parent_i[0]['balance'] - account_parent[0]['balance']
                aux_parent.append(aux_resta)
            res.append(aux_parent)
        return res

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_end'] = self.datas['form']['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_end']
        res['end']=end.upper()
        return res

    def lineas(self, resumen):
        result = {}
        result['act'] = self.lineas_individual(resumen,'act')
        result['ant'] = self.lineas_individual(resumen,'ant')
        return result

    def lineas_individual(self, resumen, tipo):
        context = {}
        cr = self.cr
        uid = self.uid
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        result = {}
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        if tipo!='act':
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_inicial_aux = date_aux - relativedelta(years=1)
            date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
            date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux = date_aux - relativedelta(years=1)
            date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
            fiscalyear_ids = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
            if fiscalyear_ids:
                fiscalyear_id = fiscalyear_ids[0]        
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        ctx = context.copy()
        #fuentes_corrientes = ['11311','11313','11314','11317','','11318','11319','11381']
        fuentes_corrientes = ['11311','11313','11314','11317','','11318','11319']
        usos_corrientes = ['21351','21352','21353','21355','21356','21357','21358']
        fuentes_capital = ['11324','11328']
        usos_produccion = ['21361','21363','21367','21371','21373','21375','21377','21378','21384','21387','11327','21388']

        fuentes_financiamiento = ['11336','11397','11398']
        usos_financiamiento = ['21396','21397','21398']
        flujos_no_presupuestariosc = ['11340','11381','11382','11383']
        flujos_no_presupuestariosd = ['21315','21340','21381','21382','21383','21385','21386','21395']
        variaciones = ['111','112','61991','212']
        codes = fuentes_corrientes + usos_corrientes + fuentes_capital + usos_produccion
        codes = codes + fuentes_financiamiento + usos_financiamiento + flujos_no_presupuestariosc + flujos_no_presupuestariosd + variaciones
        account_ids = account_obj.search(cr, uid, [('code','in', codes)])
        ctx.update({'fiscalyear': fiscalyear_id})
        ctx.update({'state': 'posted'})
        ctx.update({'date_from': date_inicial_reporte,
                    'date_to': date_final_reporte})
        nuevo_contexto = ctx.copy()
        accounts = account_obj.read(cr, uid, account_ids, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        accounts_by_id = {}
        for account in accounts:
            accounts_by_id[account['code']] = account
        for code in codes:
            if accounts_by_id.get(code,False) == False:
                accounts_by_id.update({code: {'code': code, 'balance': 0, 'credit':0 , 'debit': 0} })
        #######################
        sum_fuentes_corrientes = 0
        for code_aux in fuentes_corrientes:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['credit']
            sum_fuentes_corrientes+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'fuentes_corrientes': {'fuentes_corrientes': 'fuentes_corrientes', 'balance': sum_fuentes_corrientes}})
        #######################
        sum_usos_corrientes = 0
        for code_aux in usos_corrientes:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['debit']
            sum_usos_corrientes+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'usos_corrientes': {'usos_corrientes': 'usos_corrientes', 'balance': sum_usos_corrientes}})
        ######################
        sd_corriente = sum_fuentes_corrientes - sum_usos_corrientes
        accounts_by_id.update({'sd_corriente': {'sd_corriente': 'sd_corriente', 'balance': sd_corriente}})
        #####################
        sum_fuentes_capital = 0
        for code_aux in fuentes_capital:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['credit']
            sum_fuentes_capital+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'fuentes_capital': {'fuentes_capital': 'fuentes_capital', 'balance': sum_fuentes_capital}})
        #####################
        sum_usos_produccion = 0
        for code_aux in usos_produccion:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['debit']
            if code_aux=='11327':
                sum_usos_produccion-=accounts_by_id[code_aux]['balance']
            else:
                sum_usos_produccion+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'usos_produccion': {'usos_produccion': 'usos_produccion', 'balance': sum_usos_produccion}})
        #####################
        sd_capital = sum_fuentes_capital - sum_usos_produccion
        accounts_by_id.update({'sd_capital': {'sd_capital': 'sd_capital', 'balance': sd_capital}})
        #####################
        sd_bruto = sd_corriente + sd_capital
        accounts_by_id.update({'sd_bruto': {'sd_bruto': 'sd_bruto', 'balance': sd_bruto}})

        #######################
        sum_fuentes_financiamiento = 0
        for code_aux in fuentes_financiamiento:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['credit']
            sum_fuentes_financiamiento+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'fuentes_financiamiento': {'fuentes_financiamiento': 'fuentes_financiamiento', 'balance': sum_fuentes_financiamiento}})
        #######################
        sum_usos_financiamiento = 0
        for code_aux in usos_financiamiento:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['debit']
            sum_usos_financiamiento+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'usos_financiamiento': {'usos_financiamiento': 'usos_financiamiento', 'balance': sum_usos_financiamiento}})
        ######################

        sd_financiamiento = sum_fuentes_financiamiento - sum_usos_financiamiento
        accounts_by_id.update({'sd_financiamiento': {'sd_financiamiento': 'sd_financiamiento', 'balance': sd_financiamiento}})
                
        sum_flujos_no_presupuestariosc = 0
        for code_aux in flujos_no_presupuestariosc:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['credit']
            sum_flujos_no_presupuestariosc+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'flujos_no_presupuestariosc': {'flujos_no_presupuestariosc': 'flujos_no_presupuestariosc', 'balance': sum_flujos_no_presupuestariosc}})
        ######################
        sum_flujos_no_presupuestariosd = 0
        for code_aux in flujos_no_presupuestariosd:
            accounts_by_id[code_aux]['balance'] = accounts_by_id[code_aux]['debit']
            sum_flujos_no_presupuestariosd+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'flujos_no_presupuestariosd': {'flujos_no_presupuestariosd': 'flujos_no_presupuestariosd', 'balance': sum_flujos_no_presupuestariosd}})
        ######################
        flujos_netos = sum_flujos_no_presupuestariosc - sum_flujos_no_presupuestariosd
        accounts_by_id.update({'flujos_netos': {'flujos_netos': 'flujos_netos', 'balance': flujos_netos}})
        
        #VARIACIONES NO PRESUPUESTARIAS
        accounts_by_id_inicial = {}
        accounts_by_id_final = {}
        account_move_obj = self.pool.get('account.move') 
        asiento_inicial = account_move_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear_id),('is_start','=',True),('state','=','posted')])
        codes2 = ['111','112','61991','212']
        account_ids2 = account_obj.search(cr, uid, [('code','in', codes2)])
        if asiento_inicial:
            nuevo_contexto['move_ids'] = asiento_inicial # contexto agregado en modulo base account, en archivo account_move_line.py
        cuentas2_inicial = account_obj.read(cr, uid, account_ids2, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], nuevo_contexto)
        cuentas2_final = account_obj.read(cr, uid, account_ids2, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        for account in cuentas2_inicial:
            accounts_by_id_inicial[account['code']] = account
        for account in cuentas2_final:
            accounts_by_id_final[account['code']] = account            
        for code in codes2:
            if accounts_by_id_inicial.get(code,False) == False:
                accounts_by_id_inicial.update({code: {'code': code, 'balance': 0} })
            if accounts_by_id_final.get(code,False) == False:
                accounts_by_id_final.update({code: {'code': code, 'balance': 0} })
        #segun el reglamento del ESIGEF son los saldos finales menos los iniciales (SI-SF)
        accounts_by_id.update({'111': {'111': '111', 'balance': accounts_by_id_inicial['111']['balance'] - accounts_by_id_final['111']['balance']}})
        accounts_by_id.update({'112': {'112': '112', 'balance': accounts_by_id_inicial['112']['balance'] - accounts_by_id_final['112']['balance']}})
        accounts_by_id.update({'61991': {'61991': '61991', 'balance': accounts_by_id_inicial['61991']['balance'] - accounts_by_id_final['61991']['balance']}})
        accounts_by_id.update({'212': {'212': '212', 'balance': abs(accounts_by_id_final['212']['balance']) - abs(accounts_by_id_inicial['212']['balance'])}})
        variaciones_netas = accounts_by_id['111']['balance'] + accounts_by_id['112']['balance'] + accounts_by_id['61991']['balance'] + accounts_by_id['212']['balance']
        accounts_by_id.update({'variaciones_netas': {'variaciones_netas': 'variaciones_netas', 'balance': variaciones_netas}})

        sd_bruto2 = sd_financiamiento + flujos_netos + variaciones_netas
        accounts_by_id.update({'sd_bruto2': {'sd_bruto2': 'sd_bruto2', 'balance': sd_bruto2}})
        return accounts_by_id
 
report_sxw.report_sxw('report.FlujoEfectivoAuxiliar','account.account',
                      'addons/gt_gob_report/report/report_flujo_efectivo_auxiliar.mako',
                      parser=FlujoEfectivoAuxiliar)


class Superavit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(Superavit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars':self._vars,
            'lineas': self.lineas,
         })

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_end'] = self.datas['form']['date_end']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_end']
        res['end']=end.upper()
        return res

    def lineas(self, resumen):
        result = {}
        result['act'] = self.lineas_individual(resumen,'act')
        result['ant'] = self.lineas_individual(resumen,'ant')
        return result

    def lineas_individual(self, resumen, tipo):
        context = {}
        cr = self.cr
        uid = self.uid
        date_inicial_reporte = self.datas['form']['date_from']
        date_final_reporte = self.datas['form']['date_end']
        if tipo!='act':
            date_aux = datetime.datetime.strptime(date_inicial_reporte, '%Y-%m-%d').date()
            date_inicial_aux = date_aux - relativedelta(years=1)
            date_inicial_reporte = date_inicial_aux.strftime('%Y-%m-%d')
            date_aux = datetime.datetime.strptime(date_final_reporte, '%Y-%m-%d').date()
            date_final_aux = date_aux - relativedelta(years=1)
            date_final_reporte = date_final_aux.strftime('%Y-%m-%d')
        result = {}
        fiscalyear_id = self.datas['form']['fiscalyear'][0]
        if tipo=='ant':
            fiscalyear_ids = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start','<=', date_inicial_reporte),('date_stop','>=',date_final_reporte)])
            if fiscalyear_ids:
                fiscalyear_id = fiscalyear_ids[0]        
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        ctx = context.copy()

        fuentes_financiamiento = ['11336','11397','11398']
        usos_financiamiento = ['21396','21397','21398']
        flujos_no_presupuestariosc = ['11340','11381','11382','11383']
        flujos_no_presupuestariosd = ['21340','21381','21382','21383','21395']
        variaciones = ['111','112','61991','212']
        
        codes = fuentes_financiamiento + usos_financiamiento + flujos_no_presupuestariosc + flujos_no_presupuestariosd + variaciones
        account_ids = account_obj.search(cr, uid, [('code','in', codes)])
        ctx.update({'fiscalyear': fiscalyear_id})
        ctx.update({'state': 'posted'})
        ctx.update({'date_from': date_inicial_reporte,
                    'date_to': date_final_reporte})
        accounts = account_obj.read(cr, uid, account_ids, ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)
        accounts_by_id = {}
        for account in accounts:
            accounts_by_id[account['code']] = account
        for code in codes:
            if accounts_by_id.get(code,False) == False:
                accounts_by_id.update({code: {'code': code, 'balance': 0} })
        #######################
        sum_fuentes_financiamiento = 0
        for code_aux in fuentes_financiamiento:
            sum_fuentes_financiamiento+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'fuentes_financiamiento': {'fuentes_financiamiento': 'fuentes_financiamiento', 'balance': sum_fuentes_financiamiento}})
        #######################
        sum_usos_financiamiento = 0
        for code_aux in usos_financiamiento:
            sum_usos_financiamiento+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'usos_financiamiento': {'usos_financiamiento': 'usos_financiamiento', 'balance': sum_usos_financiamiento}})
        ######################
        sum_flujos_no_presupuestariosc = 0
        for code_aux in flujos_no_presupuestariosc:
            sum_flujos_no_presupuestariosc+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'flujos_no_presupuestariosc': {'flujos_no_presupuestariosc': 'flujos_no_presupuestariosc', 'balance': sum_flujos_no_presupuestariosc}})
        ######################
        sum_flujos_no_presupuestariosd = 0
        for code_aux in flujos_no_presupuestariosd:
            sum_flujos_no_presupuestariosd+=accounts_by_id[code_aux]['balance']
        accounts_by_id.update({'flujos_no_presupuestariosd': {'flujos_no_presupuestariosd': 'flujos_no_presupuestariosd', 'balance': sum_flujos_no_presupuestariosd}})
        ######################
        flujos_netos = sum_flujos_no_presupuestariosc + sum_flujos_no_presupuestariosd
        accounts_by_id.update({'flujos_netos': {'flujos_netos': 'flujos_netos', 'balance': flujos_netos}})
        return accounts_by_id
 
report_sxw.report_sxw('report.Superavit','account.account',
                      'addons/gt_gob_report/report/report_superavit.mako',
                      parser=Superavit)
