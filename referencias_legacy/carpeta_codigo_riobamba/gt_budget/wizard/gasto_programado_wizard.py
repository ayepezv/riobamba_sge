# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
from osv import fields, osv
from gt_tool import XLSWriter

class resumenGastoWizard(osv.TransientModel):
   _name = 'resumen.gasto.wizard'
   _columns = dict(
      poa_id = fields.many2one('budget.poa','Presupuesto'),
      datas = fields.binary('Archivo'),
      datas_fname = fields.char('Nombre archivo', size=32),
   )

   def get_programa_name(self,cr, uid, ids,  p_id):
      program_obj = self.pool.get('project.program')
      aux = ''
      programa = program_obj.browse(cr, uid, p_id)
      aux = programa.sequence + ' - ' + programa.name
      return aux


   def get_programa_gp(self, cr, uid, ids, poa):
      programa_list = []
      sql = '''select id from project_program where id in (select program_id from project_project where type_budget='gasto') order by sequence'''
      cr.execute(sql)
      result = cr.fetchall()
      for id_p in result:
         programa_list.append(id_p[0])
      return programa_list

   def get_budget_gp(self,cr, uid,ids, program_id,text,text1):
      budget_item_obj = self.pool.get('budget.item')
      for this in self.browse(cr, uid, ids):
         poa_id = this.poa_id.id
      budget_ids_1 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
      budget_ids_2 = []
      if text1!='0':
         budget_ids_2 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
      context = {}
      total = 0 
      budget_ids = budget_ids_1 + budget_ids_2
      for budget_id in budget_ids:
         budget = budget_item_obj.browse(cr, uid, budget_id,context)
         total += budget.planned_amount
      return total

   def exporta_excel_rgw(self, cr, uid, ids, context=None):
      for this in self.browse(cr, uid, ids):
         writer = XLSWriter.XLSWriter()
         writer.append(['RESUMEN DE GASTOS PROGRAMADOS INICIAL'])
         writer.append(['GESTION FINANCIERA'])
         writer.append(['PRESUPUESTOS'])
         writer.append(['DESDE',this.poa_id.date_start,'HASTA',this.poa_id.date_end])
         writer.append(['PROGRAMA','51','53','56-57','58','SUBTOTAL','71','73','75','77','78','84','87','96','97','SUBTOTAL','TOTAL'])
         writer.append(['','PERSONAL','BIEN SERVICIOS CONSUMO','OTROS GASTOS','TRA.CORRIENTE','','PERSONAL','BIENES SERVICIOS INVERSION','OBRA PUBLICA','PROVISIONES','ACTIVOS LARGA DURACION','INV. FINANCIERAS','AMORT. DEUDA PUBLICA','APLI. FINANCIAMIENTO','',''])
         a=subtot=subtot2=total=0
         t_51 = t_53 = t_56 = t_58 = t_71 = t_73 = t_75 = t_77 = t_78 = t_84 = t_87 = t_96 = t_97 = ts = ts2 = t = 0 
         for programa_id in self.get_programa_gp(cr, uid, ids, this.poa_id):
            aux_name=self.get_programa_name(cr, uid, ids, programa_id)
            aux_51 = self.get_budget_gp(cr, uid, ids, programa_id,'51','0')
            t_51 += aux_51
            aux_53 = self.get_budget_gp(cr, uid, ids, programa_id,'53','0')
            t_53 += aux_53
            aux_56 = self.get_budget_gp(cr, uid, ids, programa_id,'56','57')
            t_56 += aux_56
            aux_58 = self.get_budget_gp(cr, uid, ids, programa_id,'58','0')
            t_58 += aux_58
            subtot = aux_51 + aux_53 + aux_56 + aux_58
            ts += subtot
            aux_71 = self.get_budget_gp(cr, uid, ids, programa_id,'71','0')
            t_71 += aux_71
            aux_73 = self.get_budget_gp(cr, uid, ids, programa_id,'73','0')
            t_73 += aux_73
            aux_75 = self.get_budget_gp(cr, uid, ids, programa_id,'75','0')
            t_75 += aux_75
            aux_77 = self.get_budget_gp(cr, uid, ids, programa_id,'77','0')
            t_77 += aux_77
            aux_78 = self.get_budget_gp(cr, uid, ids, programa_id,'78','0')
            t_78 += aux_78
            aux_84 = self.get_budget_gp(cr, uid, ids, programa_id,'84','0')
            t_84 += aux_84
            aux_87 = self.get_budget_gp(cr, uid, ids, programa_id,'87','0')
            t_87 += aux_87
            aux_96 = self.get_budget_gp(cr, uid, ids, programa_id,'96','0')
            t_96 += aux_96
            aux_97 = self.get_budget_gp(cr, uid, ids, programa_id,'97','0')
            t_97 += aux_97
            subtot2 = aux_71 + aux_73 + aux_75 + aux_77 + aux_78 + aux_84 + aux_87 + aux_96 + aux_97
            ts2 += subtot2
            total = subtot + subtot2
            t += total
            writer.append([aux_name,aux_51,aux_53,aux_56,aux_58,subtot,aux_71,aux_73,aux_75,aux_77,aux_78,aux_84,aux_87,aux_96,aux_97,subtot2,total])
         writer.append(['TOTAL',t_51,t_53,t_56,t_58,ts,t_71,t_73,t_75,t_77,t_78,t_84,t_87,t_96,t_97,ts2,t])
      writer.save("resumenGastoInicial.xls")
      out = open("resumenGastoInicial.xls","rb").read().encode("base64")
      self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'resumenGastoInicial.xls'})
      return True

   def printResumenGasto(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['poa_id'] = report.poa_id.id
        datas = {'ids': [report.id], 'model': 'resumen.gasto.wizard','form':data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'resumen_gasto',
            'model': 'resumen.gasto.wizard',
            'datas': datas,
            'nodestroy': True,                        
            }

resumenGastoWizard()

class resumenGastoFinalWizard(osv.TransientModel):
   _name = 'resumen.gasto.final.wizard'
   _columns = dict(
      poa_id = fields.many2one('budget.poa','Presupuesto'),
      date_from = fields.date('Fecha Desde'),
      date_to = fields.date('Fecha Hasta'),
      datas = fields.binary('Archivo'),
      datas_fname = fields.char('Nombre archivo', size=32),
   )

   def get_programa_name_final(self,cr, uid, ids,  p_id):
      program_obj = self.pool.get('project.program')
      aux = ''
      programa = program_obj.browse(cr, uid, p_id)
      aux = programa.sequence + ' - ' + programa.name
      return aux


   def get_programa_gp_final(self, cr, uid, ids, poa):
      programa_list = []
      sql = '''select id from project_program where id in (select program_id from project_project where type_budget='gasto') order by sequence'''
      cr.execute(sql)
      result = cr.fetchall()
      for id_p in result:
         programa_list.append(id_p[0])
      return programa_list

   def get_budget_gp_final(self,cr, uid,ids, program_id,text,text1):
      budget_item_obj = self.pool.get('budget.item')
      for this in self.browse(cr, uid, ids):
         poa_id = this.poa_id.id
      budget_ids_1 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
      budget_ids_2 = []
      for this in self.browse(cr, uid, ids):
         date_from = this.date_from
         date_to = this.date_to
         poa_id = this.poa_id.id
      if text1!='0':
         budget_ids_2 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
      context = {}
      context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
      total = 0 
      budget_ids = budget_ids_1 + budget_ids_2
      for line in budget_item_obj.browse(cr,uid,budget_ids, context=context):
         total += line.codif_amount      
      return total

   def exporta_excel_rgwf(self, cr, uid, ids, context=None):
      for this in self.browse(cr, uid, ids):
         writer = XLSWriter.XLSWriter()
         writer.append(['RESUMEN DE GASTOS PROGRAMADOS FINALx'])
         writer.append(['GESTION FINANCIERA'])
         writer.append(['PRESUPUESTOS'])
         writer.append(['DESDE',this.poa_id.date_start,'HASTA',this.poa_id.date_end])
         writer.append(['PROGRAMA','51','53','56-57','58','SUBTOTAL','71','73','75','77','78','84','87','96','97','SUBTOTAL','TOTAL'])
         writer.append(['','PERSONAL','BIEN SERVICIOS CONSUMO','OTROS GASTOS','TRA.CORRIENTE','','PERSONAL','BIENES SERVICIOS INVERSION','OBRA PUBLICA','PROVISIONES','ACTIVOS LARGA DURACION','INV. FINANCIERAS','AMORT. DEUDA PUBLICA','APLI. FINANCIAMIENTO','',''])
         a=subtot=subtot2=total=0
         t_51 = t_53 = t_56 = t_58 = t_71 = t_73 = t_75 = t_77 = t_78 = t_84 = t_87 = t_96 = t_97 = ts = ts2 = t = 0 
         for programa_id in self.get_programa_gp_final(cr, uid, ids, this.poa_id):
            aux_name=self.get_programa_name_final(cr, uid, ids, programa_id)
            aux_51 = self.get_budget_gp_final(cr, uid, ids, programa_id,'51','0')
            t_51 += aux_51
            aux_53 = self.get_budget_gp_final(cr, uid, ids, programa_id,'53','0')
            t_53 += aux_53
            aux_56 = self.get_budget_gp_final(cr, uid, ids, programa_id,'56','57')
            t_56 += aux_56
            aux_58 = self.get_budget_gp_final(cr, uid, ids, programa_id,'58','0')
            t_58 += aux_58
            subtot = aux_51 + aux_53 + aux_56 + aux_58
            ts += subtot
            aux_71 = self.get_budget_gp_final(cr, uid, ids, programa_id,'71','0')
            t_71 += aux_71
            aux_73 = self.get_budget_gp_final(cr, uid, ids, programa_id,'73','0')
            t_73 += aux_73
            aux_75 = self.get_budget_gp_final(cr, uid, ids, programa_id,'75','0')
            t_75 += aux_75
            aux_77 = self.get_budget_gp_final(cr, uid, ids, programa_id,'77','0')
            t_77 += aux_77
            aux_78 = self.get_budget_gp_final(cr, uid, ids, programa_id,'78','0')
            t_78 += aux_78
            aux_84 = self.get_budget_gp_final(cr, uid, ids, programa_id,'84','0')
            t_84 += aux_84
            aux_87 = self.get_budget_gp_final(cr, uid, ids, programa_id,'87','0')
            t_87 += aux_87
            aux_96 = self.get_budget_gp_final(cr, uid, ids, programa_id,'96','0')
            t_96 += aux_96
            aux_97 = self.get_budget_gp_final(cr, uid, ids, programa_id,'97','0')
            t_97 += aux_97
            subtot2 = aux_71 + aux_73 + aux_75 + aux_77 + aux_78 + aux_84 + aux_87 + aux_96 + aux_97
            ts2 += subtot2
            total = subtot + subtot2
            t += total
            writer.append([aux_name,aux_51,aux_53,aux_56,aux_58,subtot,aux_71,aux_73,aux_75,aux_77,aux_78,aux_84,aux_87,aux_96,aux_97,subtot2,total])
         writer.append(['TOTAL',t_51,t_53,t_56,t_58,ts,t_71,t_73,t_75,t_77,t_78,t_84,t_87,t_96,t_97,ts2,t])
      writer.save("resumenGastoFinal.xls")
      out = open("resumenGastoFinal.xls","rb").read().encode("base64")
      self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'resumenGastoFinal.xls'})
      return True

   def printResumenGastoFinal(self, cr, uid, ids, context=None):
      if not context:
         context = {}
      data = self.read(cr, uid, ids, [], context=context)[0]
      report = self.browse(cr, uid, ids, context)[0]
      data['date_from'] = report.date_from
      data['date_to'] = report.date_to
      data['poa_id'] = report.poa_id.id
      datas = {'ids': [report.id], 'model': 'resumen.gasto.final.wizard','form':data}
      return {
         'type': 'ir.actions.report.xml',
         'report_name': 'resumen_gasto_final',
         'model': 'resumen.gasto.final.wizard',
         'datas': datas,
         'nodestroy': True,                        
      }

resumenGastoFinalWizard()

class resumenGastoWizardComprometido(osv.TransientModel):
   _name = 'resumen.gasto.comprometido.wizard'
   _columns = dict(
      poa_id = fields.many2one('budget.poa','Presupuesto'),
      date_from = fields.date('Fecha Desde'),
      date_to = fields.date('Fecha Hasta'),
      datas = fields.binary('Archivo'),
      datas_fname = fields.char('Nombre archivo', size=32),
   )

   def get_programa_name_comprometido(self,cr, uid, ids,  p_id):
      program_obj = self.pool.get('project.program')
      aux = ''
      programa = program_obj.browse(cr, uid, p_id)
      aux = programa.sequence + ' - ' + programa.name
      return aux


   def get_programa_gp_comprometido(self, cr, uid, ids, poa):
      programa_list = []
      sql = '''select id from project_program where id in (select program_id from project_project where type_budget='gasto') order by sequence'''
      cr.execute(sql)
      result = cr.fetchall()
      for id_p in result:
         programa_list.append(id_p[0])
      return programa_list

   def get_budget_gp_comprometido(self,cr, uid,ids, program_id,text,text1):
      budget_item_obj = self.pool.get('budget.item')
      for this in self.browse(cr, uid, ids):
         poa_id = this.poa_id.id
      budget_ids_1 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
      budget_ids_2 = []
      for this in self.browse(cr, uid, ids):
         date_from = this.date_from
         date_to = this.date_to
         poa_id = this.poa_id.id
      if text1!='0':
         budget_ids_2 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
      context = {}
      context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
      total = 0 
      budget_ids = budget_ids_1 + budget_ids_2
      for line in budget_item_obj.browse(cr,uid,budget_ids, context=context):
         total += line.commited_amount      
      return total

   def get_budget_gp_codif(self,cr, uid,ids, program_id,text,text1):
      budget_item_obj = self.pool.get('budget.item')
      for this in self.browse(cr, uid, ids):
         poa_id = this.poa_id.id
      budget_ids_1 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
      budget_ids_2 = []
      for this in self.browse(cr, uid, ids):
         date_from = this.date_from
         date_to = this.date_to
         poa_id = this.poa_id.id
      if text1!='0':
         budget_ids_2 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
      context = {}
      context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
      total = 0 
      budget_ids = budget_ids_1 + budget_ids_2
      for line in budget_item_obj.browse(cr,uid,budget_ids, context=context):
         total += line.codif_amount      
      return total

   def exporta_excel_rgwc(self, cr, uid, ids, context=None):
      for this in self.browse(cr, uid, ids):
         writer = XLSWriter.XLSWriter()
         writer.append(['RESUMEN DE GASTOS PROGRAMADOS COMPROMETIDO'])
         writer.append(['GESTION FINANCIERA'])
         writer.append(['PRESUPUESTOS'])
         writer.append(['DESDE',this.poa_id.date_start,'HASTA',this.poa_id.date_end])
         writer.append(['PROGRAMA','51','53','56-57','58','SUBTOTAL','71','73','75','77','78','84','87','96','97','SUBTOTAL','TOTAL'])
         writer.append(['','PERSONAL','BIEN SERVICIOS CONSUMO','OTROS GASTOS','TRA.CORRIENTE','','PERSONAL','BIENES SERVICIOS INVERSION','OBRA PUBLICA','PROVISIONES','ACTIVOS LARGA DURACION','INV. FINANCIERAS','AMORT. DEUDA PUBLICA','APLI. FINANCIAMIENTO','',''])
         a=subtot=subtot2=total=0
         a=subtoti=subtot2i=totali=0
         ti_51 = ti_53 = ti_56 = ti_58 = ti_71 = ti_73 = ti_75 = ti_77 = ti_78 = ti_84 = ti_87 = ti_96 = ti_97 = tsi = ts2i = ti = 0 
         t_51 = t_53 = t_56 = t_58 = t_71 = t_73 = t_75 = t_77 = t_78 = t_84 = t_87 = t_96 = t_97 = ts = ts2 = t = 0 
         for programa_id in self.get_programa_gp_comprometido(cr, uid, ids, this.poa_id):
            aux_name=self.get_programa_name_comprometido(cr, uid, ids, programa_id)
            auxi_51 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'51','0')
            ti_51 += auxi_51
            auxi_53 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'53','0')
            ti_53 += auxi_53
            auxi_56 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'56','57')
            ti_56 += auxi_56
            auxi_58 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'58','0')
            ti_58 += auxi_58
            subtoti = auxi_51 + auxi_53 + auxi_56 + auxi_58
            tsi += subtoti
            auxi_71 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'71','0')
            ti_71 += auxi_71
            auxi_73 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'73','0')
            ti_73 += auxi_73
            auxi_75 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'75','0')
            ti_75 += auxi_75
            auxi_77 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'77','0')
            ti_77 += auxi_77
            auxi_78 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'78','0')
            ti_78 += auxi_78
            auxi_84 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'84','0')
            ti_84 += auxi_84
            auxi_87 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'87','0')
            ti_87 += auxi_87
            auxi_96 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'96','0')
            ti_96 += auxi_96
            auxi_97 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'97','0')
            ti_97 += auxi_97
            subtot2i = auxi_71 + auxi_73 + auxi_75 + auxi_77 + auxi_78 + auxi_84 + auxi_87 + auxi_96 + auxi_97
            ts2i += subtot2i
            totali = subtoti + subtot2i
            ti += totali
            ## comprometido
            aux_51 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'51','0')
            t_51 += aux_51
            aux_53 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'53','0')
            t_53 += aux_53
            aux_56 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'56','57')
            t_56 += aux_56
            aux_58 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'58','0')
            t_58 += aux_58
            subtot = aux_51 + aux_53 + aux_56 + aux_58
            ts += subtot
            aux_71 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'71','0')
            t_71 += aux_71
            aux_73 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'73','0')
            t_73 += aux_73
            aux_75 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'75','0')
            t_75 += aux_75
            aux_77 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'77','0')
            t_77 += aux_77
            aux_78 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'78','0')
            t_78 += aux_78
            aux_84 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'84','0')
            t_84 += aux_84
            aux_87 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'87','0')
            t_87 += aux_87
            aux_96 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'96','0')
            t_96 += aux_96
            aux_97 = self.get_budget_gp_comprometido(cr, uid, ids, programa_id,'97','0')
            t_97 += aux_97
            subtot2 = aux_71 + aux_73 + aux_75 + aux_77 + aux_78 + aux_84 + aux_87 + aux_96 + aux_97
            ts2 += subtot2
            total = subtot + subtot2
            t += total
            writer.append([aux_name,aux_51,aux_53,aux_56,aux_58,subtot,aux_71,aux_73,aux_75,aux_77,aux_78,aux_84,aux_87,aux_96,aux_97,subtot2,total])
         writer.append(['TOTAL',t_51,t_53,t_56,t_58,ts,t_71,t_73,t_75,t_77,t_78,t_84,t_87,t_96,t_97,ts2,t])
         writer.append(['PRESUPUESTADO',ti_51,ti_53,ti_56,ti_58,tsi,ti_71,ti_73,ti_75,ti_77,ti_78,ti_84,ti_87,ti_96,ti_97,ts2i,ti])
         writer.append(['COMPROMETIDO',t_51,t_53,t_56,t_58,ts,t_71,t_73,t_75,t_77,t_78,t_84,t_87,t_96,t_97,ts2,t])
         writer.append(['SALDO',ti_51-t_51,ti_53-t_53,ti_56-t_56,ti_58-t_58,tsi-ts,ti_71-t_71,ti_73-t_73,ti_75-t_75,ti_77-t_77,ti_78-t_78,ti_84-t_84,ti_87-t_87,ti_96-t_96,ti_97-t_97,ts2i-ts2,ti-t])
      writer.save("resumenGastoComprometido.xls")
      out = open("resumenGastoComprometido.xls","rb").read().encode("base64")
      self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'resumenGastoComprometido.xls'})
      return True

   def printResumenGastoComprometido(self, cr, uid, ids, context=None):
      if not context:
         context = {}
      data = self.read(cr, uid, ids, [], context=context)[0]
      report = self.browse(cr, uid, ids, context)[0]
      data['date_from'] = report.date_from
      data['date_to'] = report.date_to
      data['poa_id'] = report.poa_id.id
      datas = {'ids': [report.id], 'model': 'resumen.gasto.comprometido.wizard','form':data}
      return {
         'type': 'ir.actions.report.xml',
         'report_name': 'resumen_gasto_comprometido',
         'model': 'resumen.gasto.comprometido.wizard',
         'datas': datas,
         'nodestroy': True,                        
      }

resumenGastoWizardComprometido()

class resumenGastoWizardPagado(osv.TransientModel):
   _name = 'resumen.gasto.pagado.wizard'
   _columns = dict(
      poa_id = fields.many2one('budget.poa','Presupuesto'),
      date_from = fields.date('Fecha Desde'),
      date_to = fields.date('Fecha Hasta'),
      datas = fields.binary('Archivo'),
      datas_fname = fields.char('Nombre archivo', size=32),
   )

   def get_programa_name_pagado(self,cr, uid, ids,  p_id):
      program_obj = self.pool.get('project.program')
      aux = ''
      programa = program_obj.browse(cr, uid, p_id)
      aux = programa.sequence + ' - ' + programa.name
      return aux


   def get_programa_gp_pagado(self, cr, uid, ids, poa):
      programa_list = []
      sql = '''select id from project_program where id in (select program_id from project_project where type_budget='gasto') order by sequence'''
      cr.execute(sql)
      result = cr.fetchall()
      for id_p in result:
         programa_list.append(id_p[0])
      return programa_list

   def get_budget_gp_pagado(self,cr, uid,ids, program_id,text,text1):
      budget_item_obj = self.pool.get('budget.item')
      for this in self.browse(cr, uid, ids):
         poa_id = this.poa_id.id
      budget_ids_1 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
      budget_ids_2 = []
      for this in self.browse(cr, uid, ids):
         date_from = this.date_from
         date_to = this.date_to
         poa_id = this.poa_id.id
      if text1!='0':
         budget_ids_2 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
      context = {}
      context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
      total = 0 
      budget_ids = budget_ids_1 + budget_ids_2
      for line in budget_item_obj.browse(cr,uid,budget_ids, context=context):
         total += line.paid_amount      
      return total

   def get_budget_gp_codif(self,cr, uid,ids, program_id,text,text1):
      budget_item_obj = self.pool.get('budget.item')
      for this in self.browse(cr, uid, ids):
         poa_id = this.poa_id.id
      budget_ids_1 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
      budget_ids_2 = []
      for this in self.browse(cr, uid, ids):
         date_from = this.date_from
         date_to = this.date_to
         poa_id = this.poa_id.id
      if text1!='0':
         budget_ids_2 = budget_item_obj.search(cr, uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
      context = {}
      context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
      total = 0 
      budget_ids = budget_ids_1 + budget_ids_2
      for line in budget_item_obj.browse(cr,uid,budget_ids, context=context):
         total += line.codif_amount      
      return total

   def exporta_excel_rgwp(self, cr, uid, ids, context=None):
      for this in self.browse(cr, uid, ids):
         writer = XLSWriter.XLSWriter()
         writer.append(['RESUMEN DE GASTOS PROGRAMADOS PAGADO'])
         writer.append(['GESTION FINANCIERA'])
         writer.append(['PRESUPUESTOS'])
         writer.append(['DESDE',this.poa_id.date_start,'HASTA',this.poa_id.date_end])
         writer.append(['PROGRAMA','51','53','56-57','58','SUBTOTAL','71','73','75','77','78','84','87','96','97','SUBTOTAL','TOTAL'])
         writer.append(['','PERSONAL','BIEN SERVICIOS CONSUMO','OTROS GASTOS','TRA.CORRIENTE','','PERSONAL','BIENES SERVICIOS INVERSION','OBRA PUBLICA','PROVISIONES','ACTIVOS LARGA DURACION','INV. FINANCIERAS','AMORT. DEUDA PUBLICA','APLI. FINANCIAMIENTO','',''])
         a=subtot=subtot2=total=0
         a=subtoti=subtot2i=totali=0
         ti_51 = ti_53 = ti_56 = ti_58 = ti_71 = ti_73 = ti_75 = ti_77 = ti_78 = ti_84 = ti_87 = ti_96 = ti_97 = tsi = ts2i = ti = 0 
         t_51 = t_53 = t_56 = t_58 = t_71 = t_73 = t_75 = t_77 = t_78 = t_84 = t_87 = t_96 = t_97 = ts = ts2 = t = 0 
         for programa_id in self.get_programa_gp_pagado(cr, uid, ids, this.poa_id):
            aux_name=self.get_programa_name_pagado(cr, uid, ids, programa_id)
            auxi_51 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'51','0')
            ti_51 += auxi_51
            auxi_53 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'53','0')
            ti_53 += auxi_53
            auxi_56 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'56','57')
            ti_56 += auxi_56
            auxi_58 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'58','0')
            ti_58 += auxi_58
            subtoti = auxi_51 + auxi_53 + auxi_56 + auxi_58
            tsi += subtoti
            auxi_71 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'71','0')
            ti_71 += auxi_71
            auxi_73 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'73','0')
            ti_73 += auxi_73
            auxi_75 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'75','0')
            ti_75 += auxi_75
            auxi_77 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'77','0')
            ti_77 += auxi_77
            auxi_78 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'78','0')
            ti_78 += auxi_78
            auxi_84 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'84','0')
            ti_84 += auxi_84
            auxi_87 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'87','0')
            ti_87 += auxi_87
            auxi_96 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'96','0')
            ti_96 += auxi_96
            auxi_97 = self.get_budget_gp_codif(cr, uid, ids, programa_id,'97','0')
            ti_97 += auxi_97
            subtot2i = auxi_71 + auxi_73 + auxi_75 + auxi_77 + auxi_78 + auxi_84 + auxi_87 + auxi_96 + auxi_97
            ts2i += subtot2i
            totali = subtoti + subtot2i
            ti += totali
            ## pagado
            aux_51 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'51','0')
            t_51 += aux_51
            aux_53 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'53','0')
            t_53 += aux_53
            aux_56 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'56','57')
            t_56 += aux_56
            aux_58 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'58','0')
            t_58 += aux_58
            subtot = aux_51 + aux_53 + aux_56 + aux_58
            ts += subtot
            aux_71 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'71','0')
            t_71 += aux_71
            aux_73 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'73','0')
            t_73 += aux_73
            aux_75 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'75','0')
            t_75 += aux_75
            aux_77 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'77','0')
            t_77 += aux_77
            aux_78 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'78','0')
            t_78 += aux_78
            aux_84 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'84','0')
            t_84 += aux_84
            aux_87 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'87','0')
            t_87 += aux_87
            aux_96 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'96','0')
            t_96 += aux_96
            aux_97 = self.get_budget_gp_pagado(cr, uid, ids, programa_id,'97','0')
            t_97 += aux_97
            subtot2 = aux_71 + aux_73 + aux_75 + aux_77 + aux_78 + aux_84 + aux_87 + aux_96 + aux_97
            ts2 += subtot2
            total = subtot + subtot2
            t += total
            writer.append([aux_name,aux_51,aux_53,aux_56,aux_58,subtot,aux_71,aux_73,aux_75,aux_77,aux_78,aux_84,aux_87,aux_96,aux_97,subtot2,total])
         writer.append(['TOTAL',t_51,t_53,t_56,t_58,ts,t_71,t_73,t_75,t_77,t_78,t_84,t_87,t_96,t_97,ts2,t])
         writer.append(['PRESUPUESTADO',ti_51,ti_53,ti_56,ti_58,tsi,ti_71,ti_73,ti_75,ti_77,ti_78,ti_84,ti_87,ti_96,ti_97,ts2i,ti])
         writer.append(['GASTADO',t_51,t_53,t_56,t_58,ts,t_71,t_73,t_75,t_77,t_78,t_84,t_87,t_96,t_97,ts2,t])
         writer.append(['SALDO',ti_51-t_51,ti_53-t_53,ti_56-t_56,ti_58-t_58,tsi-ts,ti_71-t_71,ti_73-t_73,ti_75-t_75,ti_77-t_77,ti_78-t_78,ti_84-t_84,ti_87-t_87,ti_96-t_96,ti_97-t_97,ts2i-ts2,ti-t])
      writer.save("resumenGastoPagado.xls")
      out = open("resumenGastoPagado.xls","rb").read().encode("base64")
      self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'resumenGastoPagado.xls'})
      return True

   def printResumenGastoPagado(self, cr, uid, ids, context=None):
      if not context:
         context = {}
      data = self.read(cr, uid, ids, [], context=context)[0]
      report = self.browse(cr, uid, ids, context)[0]
      data['date_from'] = report.date_from
      data['date_to'] = report.date_to
      data['poa_id'] = report.poa_id.id
      datas = {'ids': [report.id], 'model': 'resumen.gasto.pagado.wizard','form':data}
      return {
         'type': 'ir.actions.report.xml',
         'report_name': 'resumen_gasto_pagado',
         'model': 'resumen.gasto.pagado.wizard',
         'datas': datas,
         'nodestroy': True,                        
      }

resumenGastoWizardPagado()
