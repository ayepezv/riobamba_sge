# -*- coding: utf-8 -*-
##############################################################################
#
#    
#    Copyright (C) 2013 Mario Chogllo
#    mariofchogllo@gmail..com
#    $Id$
#
##############################################################################
from gt_tool import XLSWriter
from osv import osv, fields
import xlrd
import netsvc
import time


class budgetPacLine(osv.Model):
    _name = 'budget.pac.line'
    _columns = dict(
        p_id = fields.many2one('budget.pac','Pac'),
        p2_id = fields.many2one('budget.pac','Pac'),
        name = fields.many2one('budget.post','Partida',required=True),
        catalogo = fields.char('Catalogo',size=32),
        tipo_pac = fields.selection([('Bien','Bien'),('Servicio','Servicio'),('Obra','Obra'),('Consultoria','Consultoria')],'Tipo'),
        cantidad = fields.float('Cantidad'),
        uom = fields.many2one('pac.uom','Unidad'),
        is_publicado = fields.boolean('Publicado?'),
        publicado = fields.float('Valor Publicado'),
        reforma = fields.float('Reforma'),
        final = fields.float('Final'),
    )
budgetPacLine()

class budgetPac(osv.Model):
    _name = 'budget.pac'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        date_from = fields.date('Desde'),
        date_to = fields.date('Hasta'),
        line_ids = fields.one2many('budget.pac.line','p_id','Detalle Pac Publicado'),
        line2_ids = fields.one2many('budget.pac.line','p2_id','Detalle Pac No Publicado'),
        state = fields.selection([('Borrador','Borrador'),('Aprobado','Aprobado'),('Cerrado','Cerrado')],'Estado'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def exporta_excel_pac(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            aux_anio = this.poa_id.name[3:]
            writer = XLSWriter.XLSWriter()
            writer.append(['PAC',this.poa_id.name])
            writer.append(['VALORES PUBLICADOS'])
            writer.append(['ANIO','PARTIDA','CATALOGO','TIPO','DETALLE','CANTIDAD','UNIDAD','VALOR PUBLICADO','REFORMA'])
            aux_tp = aux_rf = 0
            for line in this.line_ids:
                writer.append([aux_anio,line.name.code,line.catalogo,line.tipo_pac,line.name.name,line.cantidad,line.uom.name,line.publicado,line.reforma])
                aux_tp += line.publicado
                aux_rf += line.reforma
            writer.append(['','','','','','','TOTAL PUBLICADO',aux_tp,aux_rf])
            writer.append(['VALORES NO PUBLICADOS'])            
            writer.append(['ANIO','PARTIDA','CATALOGO','TIPO','DETALLE','CANTIDAD','UNIDAD','VALOR PUBLICADO','REFORMA'])
            aux_tp = aux_rf = 0
            for line in this.line2_ids:
                writer.append([aux_anio,line.name.code,line.catalogo,line.tipo_pac,line.name.name,line.cantidad,line.uom.name,line.publicado,line.reforma])
                aux_tp += line.publicado
                aux_rf += line.reforma
            writer.append(['','','','','','','TOTAL NO PUBLICADO',aux_tp,aux_rf])
        writer.save("pacPresupuesto.xls")
        out = open("pacPresupuesto.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'pacPresupuesto.xls'})
        return True            

    def apruebaPac(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'Aprobado'})
        
    def computePac(self, cr, uid, ids, context=None):
        item_obj = self.pool.get('budget.item')
        line_obj = self.pool.get('budget.pac.line')
        for this in self.browse(cr, uid, ids):
            context = {'by_date':True,'date_start':this.date_from, 'date_end': this.date_to,'poa_id':this.poa_id.id}
            for line in this.line_ids:
                aux_reforma = aux_final = j = 0
                item_ids = item_obj.search(cr, uid, [('code_aux','=like',line.name.code+'%'),('poa_id','=',this.poa_id.id)])
                if item_ids:
                    for item_id in item_ids:
                        item = item_obj.read(cr,uid,item_id,['reform_amount','codif_amount'], context=context)
                        aux_reforma += item['reform_amount']
                        aux_final += item.codif_amount
                line_obj.write(cr, uid, line.id,{
                    'reforma':aux_reforma,
                    'final':aux_final,
                })
        return True

    def loadPac(self, cr, uid, ids, context=None):
        post_obj = self.pool.get('budget.post')
        item_obj = self.pool.get('budget.item')
#        post_ids = post_obj.search(cr, uid, [('is_pac','=',True)])
        line_obj = self.pool.get('budget.pac.line')
        uom_obj = self.pool.get('pac.uom')
        for this in self.browse(cr, uid, ids):
            context = {'by_date':True,'date_start':this.poa_id.date_start, 'date_end': this.poa_id.date_end,'poa_id':this.poa_id.id}            
            uom_ids = uom_obj.search(cr, uid, [('name','=','Unidad')])
            line_antes = line_obj.search(cr, uid, [('p_id','=',this.id)])
            if line_antes:
                line_obj.unlink(cr, uid, line_antes)
            line2_antes = line_obj.search(cr, uid, [('p2_id','=',this.id)])
            if line2_antes:
                line_obj.unlink(cr, uid, line2_antes)
            partida = {}
            partida_no = {}
            sql_publicado = """select p.id,p.code,i.planned_amount from budget_post p, budget_item i where p.id=i.budget_post_id and poa_id=%s and p.tipo='e' and p.is_pac=True and publicado=True"""%(this.poa_id.id)
            cr.execute(sql_publicado)
            for partida_id in cr.fetchall():
                if partida_id[0] in partida:
                    partida[partida_id]+=partida_id[2]
                else:
                    partida[partida_id]=partida_id[2]
            for partida_line in partida:
                aux_reforma = aux_final = 0
                post = post_obj.browse(cr, uid, partida_line)
                line_obj.create(cr, uid, {
                    'p_id':this.id,
                    'name':partida_line[0],
                    'catalogo':post.catalogo,
                    'tipo_pac':post.tipo_pac,
                    'cantidad':1,
                    'uom':uom_ids[0],
                    'is_publicado':post.publicado,
                    'publicado':partida_line[2],
                    'reforma':aux_reforma,
                    'final':aux_final,
                })
            #################
            sql_no_publicado = """select p.id,p.code,i.planned_amount from budget_post p, budget_item i where p.id=i.budget_post_id and poa_id=%s and p.tipo='e' and p.is_pac=True and publicado=False"""%(this.poa_id.id)
            cr.execute(sql_no_publicado)
            for partida_id in cr.fetchall():
                if partida_id[0] in partida_no:
                    partida_no[partida_id]+=partida_id[2]
                else:
                    partida_no[partida_id]=partida_id[2]
            for partida_line in partida_no:
                aux_reforma = aux_final = 0
                post = post_obj.browse(cr, uid, partida_line)
                line_obj.create(cr, uid, {
                    'p2_id':this.id,
                    'name':partida_line[0],
                    'catalogo':post.catalogo,
                    'tipo_pac':post.tipo_pac,
                    'cantidad':1,
                    'uom':uom_ids[0],
                    'is_publicado':post.publicado,
                    'publicado':partida_line[2],
                    'reforma':aux_reforma,
                    'final':aux_final,
                })
        return True

    _defaults = dict(
        state = 'Borrador',
    )

budgetPac()

class certLineLineLine(osv.TransientModel):
    _name = 'cert.line.line.line'
    _columns = dict(
        ll_id = fields.many2one('cert.line.line','Cert'),
        budget_id = fields.many2one('budget.item','Programa'),
        financiera = fields.many2one('budget.financiamiento','Cta. Financiera'),
        comprometido = fields.float('Comprometido'),
        devengado = fields.float('Dvengado'),
        pagado = fields.float('Pagado'),
        date = fields.date('Fecha'),
    )
certLineLineLine()

class certLineLine(osv.TransientModel):
    _name = 'cert.line.line'
    _columns = dict(
        l_id = fields.many2one('cert.line','Cert'),
        program_id = fields.many2one('project.program','Programa'),
        comprometido = fields.float('Comprometido'),
        line_ids = fields.one2many('cert.line.line.line','ll_id','Detalle'),
    )
certLineLine()

class certLine(osv.TransientModel):
    _name = 'cert.line'
    _columns = dict(
        date = fields.date('Fecha'),
        c_id = fields.many2one('rpt.cert','Cert'),
        partner_id = fields.many2one('res.partner','Proveedor'),
        certificate_id = fields.many2one('budget.certificate','Compromiso'),
        comprometido = fields.float('Comprometido'),
        commited_total = fields.float('Comprometido Total'),
        pagado = fields.float('Pagado'),
        pagado_total = fields.float('Comprometido Total'),
        line_ids = fields.one2many('cert.line.line','l_id','Detalle'),
    )
certLine()

class rptCert(osv.TransientModel):
    _name = 'rpt.cert'

    _columns = dict(
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
        poa_id = fields.many2one('budget.poa','Año'),
        fecha_desde = fields.date('Fecha Desde'),
        fecha_hasta = fields.date('Fecha Hasta'),
        partner_id = fields.many2one('res.partner','Proveedor'),
        line_ids = fields.one2many('cert.line','c_id','Detalle'),
        certificate_id = fields.many2one('budget.certificate','Documento Presupuestario'),
    )

    _defaults = dict(
        fecha_desde = time.strftime("%Y-%m-%d"),
        fecha_hasta = time.strftime("%Y-%m-%d"),
    )

    def exporta_excel_cert(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            #writer.append(['EVALUACION PRESPUESTARIA FUENTE FINANCIAMIENTO'])
            #writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['CERTIFICADO','PROVEEDOR','PROGRAMA','COD. PARTIDA','PARTIDA','CTA. FINANCIERA','FECHA','COMPROMETIDO','PAGADO'])
            c = 0
            for line in this.line_ids:
                lineas = []
                aux_cert = line.certificate_id.name + ' ' + line.certificate_id.notes
                if line.certificate_id.partner_id:
                    if line.certificate_id.partner_id.ced_ruc:
                        aux_partner = line.certificate_id.partner_id.ced_ruc + ' - ' +  line.certificate_id.partner_id.name
                    else:
                        aux_partner = line.certificate_id.partner_id.name
                else:
                    aux_partner = "NP"
                for line_line in line.line_ids:
                    aux_programa = line_line.program_id.sequence + ' - ' + line_line.program_id.name
#                    linea.append(aux_programa)
                    linea = []#[aux_cert,aux_partner,aux_programa]
                    for line_line_line in line_line.line_ids:
                        aux_financia = line_line_line.financiera.name + ' - ' + line_line_line.financiera.desc
                        linea.append(aux_cert)
                        linea.append(aux_partner)
                        linea.append(aux_programa)
                        linea.append(line_line_line.budget_id.code)
                        linea.append(line_line_line.budget_id.name)
                        linea.append(aux_financia)
                        linea.append(line_line_line.date)
                        linea.append(line_line_line.comprometido)
                        linea.append(line_line_line.pagado)
                        writer.append(linea)
                        linea = []
                writer.append(['','','','','','','TOTAL',line.comprometido,line.pagado])
        writer.save("detalleCertificado.xls")
        out = open("detalleCertificado.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'detalleCertificado.xls'})
        return True            

    def exporta_excel_cert_(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            #writer.append(['EVALUACION PRESPUESTARIA FUENTE FINANCIAMIENTO'])
            #writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['CERTIFICADO','PROVEEDOR','PROGRAMA','PARTIDA','CTA. FINANCIERA','FECHA','COMPROMETIDO'])
            for line in this.line_ids:
                lineas = []
                aux_cert = line.certificate_id.name + ' ' + line.certificate_id.notes
                l_1 = [aux_cert,line.certificate_id.partner_id.name]
                p = 0 
                for line_line in line.line_ids:
                    if p==0:
                        l_1.append(line_line.program_id.name)
                    else:
                        l_2 = [line_line.program_id.name]
                    p+=1
                    pa = 0
                    for line_line_line in line_line.line_ids:
                        if pa==0:
                            l_1.append(line_line_line.partida_id.name)
                            lineas.append(l_1)
                            writer.append(l_1)
                        else:
                            writer.append(line_line_line.partida_id.name)
                            lineas.append(line_line_line.partida_id.name)
                        pa+=1
                
        writer.save("detalleCertificado.xls")
        out = open("detalleCertificado.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'detalleCertificado.xls'})
        return True            


    def computeCertLine(self, cr, uid, ids, context=None):
        cert_obj = self.pool.get('budget.certificate')
        cert_line_obj = self.pool.get('budget.certificate.line')
        cline_obj = self.pool.get('cert.line')
        cline_line_obj = self.pool.get('cert.line.line')
        cline_line_line_obj = self.pool.get('cert.line.line.line')
        for this in self.browse(cr, uid, ids):
            line_antes = cline_obj.search(cr, uid, [('c_id','=',this.id)])
            if line_antes:
                cline_obj.unlink(cr, uid, line_antes)
            cert_ids = []
            if this.certificate_id:
                cert_ids.append(this.certificate_id.id)
            else:
                cert_ids = cert_obj.search(cr, uid, [('date_commited','>=',this.fecha_desde),('date_commited','<=',this.fecha_hasta),
                                                     ('state','=','commited'),('tipo_aux','=','gasto')])

            for cert_id in cert_ids:
                aux_commited_total = aux_paid_total = 0
                programa_ids = {}
                partida_ids = {}
                certificate = cert_obj.browse(cr, uid, cert_id)
                cline_id = cline_obj.create(cr, uid, {
                    'c_id':this.id,
                    'date':certificate.date_commited,
                    'partner_id':certificate.partner_id.id,
                    'certificate_id':cert_id,
                })
                for cert_line in certificate.line_ids:
                    if not programa_ids.has_key(cert_line.program_id.id):
                        programa_ids[cert_line.program_id.id] = {}
                    if not cert_line.budget_id.id in programa_ids[cert_line.program_id.id]:
                        programa_ids[cert_line.program_id.id][cert_line.budget_id.id]=[cert_line.id]#cert_line.amount_commited
                    else:
                        programa_ids[cert_line.program_id.id][cert_line.budget_id.id].append(cert_line.id)#cert_line.amount_commited
#                    else:
                        
                for program_id in programa_ids:
                    cline_line_id = cline_line_obj.create(cr, uid, {
                        'l_id':cline_id,
                        'program_id':program_id,
                    })  
                    for partida_id in programa_ids[program_id]:
                        aux_commited = aux_paid = 0
                        for certificate_line_id in programa_ids[program_id][partida_id]:
                            certificate_line = cert_line_obj.browse(cr, uid, certificate_line_id)
                            aux_commited += certificate_line.amount_commited
                            aux_commited_total += certificate_line.amount_commited
                            aux_paid += certificate_line.budget_paid
                            aux_paid_total += certificate_line.budget_paid
                            if certificate_line.financia_id:
                                aux_financia = certificate_line.financia_id.id
                        cline_line_line_id = cline_line_line_obj.create(cr, uid, {
                            'll_id':cline_line_id,
                            'budget_id':partida_id,
                            'comprometido':aux_commited,
                            'pagado':aux_paid,
                            'financiera':aux_financia,
                            'date':certificate.date_commited,
                        })
                cline_obj.write(cr, uid, cline_id,{'comprometido':aux_commited_total,'pagado':aux_paid_total})
        #import pdb
        #pdb.set_trace()
        return True

    def computeCertLine_(self, cr, uid, ids, context=None):
        cert_obj = self.pool.get('budget.certificate')
        cline_obj = self.pool.get('cert.line')
        cline_line_obj = self.pool.get('cert.line.line')
        cline_line_line_obj = self.pool.get('cert.line.line.line')
        for this in self.browse(cr, uid, ids):
            cert_ids = []
            if this.certificate_id:
                cert_ids.append(this.certificate_id.id)
            else:
                cert_ids = cert_obj.search(cr, uid, [('date_commited','>=',this.fecha_desde),('date_commited','<=',this.fecha_hasta),
                                                     ('state','=','commited'),('tipo_aux','=','gasto')])
            for cert_id in cert_ids:
                programa_ids = {}
                partida_ids = {}
                certificate = cert_obj.browse(cr, uid, cert_id)
                cline_id = cline_obj.create(cr, uid, {
                    'c_id':this.id,
                    'certificate_id':cert_id,
                })
                for cert_line in certificate.line_ids:
                    if not programa_ids.has_key(cert_line.program_id.id):
                        programa_ids[cert_line.program_id.id] = {}
                        if not cert_line.budget_id.id in programa_ids[cert_line.program_id.id]:
                            programa_ids[cert_line.program_id.id][cert_line.budget_id.id]=cert_line.amount_commited
                        else:
                            programa_ids[cert_line.program_id.id][cert_line.budget_id.id]+=cert_line.amount_commited
                for program_id in programa_ids:
                    cline_line_id = cline_line_obj.create(cr, uid, {
                        'l_id':cline_id,
                        'program_id':program_id,
                    })  
                    for partida_id in programa_ids[program_id]:
                        cline_line_line_id = cline_line_line_obj.create(cr, uid, {
                            'll_id':cline_line_id,
                            'budget_id':partida_id,
                            'comprometido':programa_ids[program_id][partida_id],
                        })
        #import pdb
        #pdb.set_trace()
        return True
                        

rptCert()

class budgetCierre(osv.TransientModel):
    _inherit = 'budget.cierre'
    _columns = dict(
        opcion = fields.selection([('valor','Con Valores Anteriores'),('codificado','Codificado'),('cero','En cero')],'Pasar valores'),
    )

    def budget_cerrar(self, cr, uid, ids, context):
      # solo crea proyecto tarea los items con otro wizard el mismo que importa de excel
      wf_service = netsvc.LocalService("workflow")
      project_obj = self.pool.get('project.project')
      project_task = self.pool.get('project.task')
      item_obj = self.pool.get('budget.item')
      budget_obj = self.pool.get('budget.budget')
      parameter_obj = self.pool.get('ir.config_parameter')
      this = self.browse(cr, uid, ids[0])
      concejo_obj = self.pool.get('budget.concejo')
      concejo_line_obj = self.pool.get('budget.concejo.line')
      concejo_ids = concejo_obj.search(cr, uid, [('name','=',this.poa_id.id)])
      is_codif = False
      if concejo_ids:
          concejo_id = concejo_ids[0]
      else:
          concejo_id = concejo_obj.create(cr, uid, {
              'name':this.poa_id.id,
              'year_id':this.year_id.id,
          })
      if this.line_ids:
         codif_ids = parameter_obj.search(cr, uid, [('key','=','loadcodif')],limit=1)
         if codif_ids:
            is_codif = True
         context = {'by_date':True,'date_start': this.year_ant_id.date_start, 'date_end': this.year_ant_id.date_stop,'poa_id':this.poa_ant_id.id}
         for line_id in this.line_ids:
            project_ant = project_obj.browse(cr, uid, line_id.project_id.id)
            id_new = project_obj.create(cr, uid, {
               'fy_id':this.year_id.id,
               'code':project_ant.code,
               'name':project_ant.name,
               'poa_id':this.poa_id.id,
               #'members':project_ant.members,
               'date_start':this.poa_id.date_start,
               'date':this.poa_id.date_end,
               'department_id':project_ant.department_id.id,
               'user_id':project_ant.user_id.id,
               'axis_id':project_ant.axis_id.id,
               'estrategy_id':project_ant.estrategy_id.id,
               'program_id':project_ant.program_id.id,
               'type_id':project_ant.type_id.id,
               'type_budget':project_ant.type_budget,
               'canton_id':project_ant.canton_id.id,
               'parish_id':project_ant.parish_id.id,
               'background':project_ant.background,
               'justification':project_ant.justification,
               'general_objective':project_ant.general_objective,
               'specific_objectives':project_ant.specific_objectives,
            })
            #pasa los miembros
            miembro_ids = []
            for miembro in project_ant.members:
               miembro_ids.append(miembro.id)
            project_obj.write(cr, uid, id_new,{
               'members':[(6,0,miembro_ids)],
            })
            for activity in project_ant.tasks:
               activity_id = project_task.create(cr, uid, {
                  'name':activity.name,
                  'weight':activity.weight,
                  'date_start':this.poa_id.date_start,
                  'date_end':this.poa_id.date_end,
                  'project_id':id_new,
                  'task_ant':activity.id,
               })
               #crea budget items
               for item_line in activity.budget_planned_ids:
                  planificado = 0 
                  if line_id.opcion=='valor':
                     planificado = item_line.planned_amount
                     if is_codif:
                        item_line2 = item_obj.read(cr, uid, item_line.id,['codif_amount'],context=context)#browse(cr, uid, item_line.id,context=context)
                        planificado = item_line2['codif_amount']#.codif_amount
                  elif line_id.opcion=='codificado':
                     planificado = 0
                     if is_codif:
                        item_line2 = item_obj.browse(cr, uid, item_line.id,context=context)
                        planificado = item_line2.codif_amount
                  item_id = item_obj.create(cr, uid, {
                     'budget_post_id':item_line.budget_post_id.id,
                     'planned_amount':planificado,
                     'task_id':activity_id,
                     'suplemento':0,
                     'reduccion':0,
                     'traspaso_aumento':0,
                     'traspaso_disminucion':0,
                     'reform_amount':0,
                     'request_amount':0,
                     'codif_amount':0,
                     'commited_amount':0,
                     'reserved_amount':0,
                     'devengado_amount':0,
                     'paid_amount':0,
                     'commited_balance':0,
                     'commited_sobregiro':0,
                     'devengado_sobregiro':0,
                     'devengado_balance':0,
                     'avai_amount':0,
                  })
                  #crear el del concejo
                  if item_line.type_budget=='ingreso':
                      concejo_line_obj.create(cr, uid, {
                          'ci_id':concejo_id,
                          'budget_id':item_id,
                          'program_id':item_line.program_id.id,
                          'name':item_line.budget_post_id.id,
                          'inicial':planificado,
                      })
                  else:
                      concejo_line_obj.create(cr, uid, {
                          'c_id':concejo_id,
                          'budget_id':item_id,
                          'program_id':item_line.program_id.id,
                          'name':item_line.budget_post_id.id,
                          'inicial':planificado,
                      })
      else:
         project_ids = project_obj.search(cr, uid, [('poa_id','=',this.poa_ant_id.id)])
         if project_ids:
            for project_id in project_ids:
               project_ant = project_obj.browse(cr, uid, project_id)
               id_new = project_obj.create(cr, uid, {
                  'fy_id':this.year_id.id,
                  'code':project_ant.code,
                  'name':project_ant.name,
                  'poa_id':this.poa_id.id,
                  #'members':project_ant.members,
                  'date_start':this.poa_id.date_start,
                  'date':this.poa_id.date_end,
                  'department_id':project_ant.department_id.id,
                  'user_id':project_ant.user_id.id,
                  'axis_id':project_ant.axis_id.id,
                  'estrategy_id':project_ant.estrategy_id.id,
                  'program_id':project_ant.program_id.id,
                  'type_id':project_ant.type_id.id,
                  'type_budget':project_ant.type_budget,
                  'canton_id':project_ant.canton_id.id,
                  'parish_id':project_ant.parish_id.id,
                  'background':project_ant.background,
                  'justification':project_ant.justification,
                  'general_objective':project_ant.general_objective,
                  'specific_objectives':project_ant.specific_objectives,
               })
               #pasa los miembros
               miembro_ids = []
               for miembro in project_ant.members:
                  miembro_ids.append(miembro.id)
               project_obj.write(cr, uid, id_new,{
                  'members':[(6,0,miembro_ids)],
               })
               for activity in project_ant.tasks:
                  activity_id = project_task.create(cr, uid, {
                     'name':activity.name,
                     'weight':activity.weight,
                     'date_start':this.poa_id.date_start,
                     'date_end':this.poa_id.date_end,
                     'project_id':id_new,
                     'task_ant':activity.id,
                  })
                  #crea budget items
                  for item_line in activity.budget_planned_ids:
                     planificado = 0 
                     if this.valor=='valor':
                        planificado = item_line.planned_amount
                     item_id = item_obj.create(cr, uid, {
                        'budget_post_id':item_line.budget_post_id.id,
                        'planned_amount':planificado,
                        'task_id':activity_id,
                        'suplemento':0,
                        'reduccion':0,
                        'traspaso_aumento':0,
                        'traspaso_disminucion':0,
                        'reform_amount':0,
                        'request_amount':0,
                        'codif_amount':0,
                        'commited_amount':0,
                        'reserved_amount':0,
                        'devengado_amount':0,
                        'paid_amount':0,
                        'commited_balance':0,
                        'commited_sobregiro':0,
                        'devengado_sobregiro':0,
                        'devengado_balance':0,
                        'avai_amount':0,
                     })
                     if item_line.type_budget=='ingreso':
                         concejo_line_obj.create(cr, uid, {
                             'ci_id':concejo_id,
                             'budget_id':item_id,
                             'program_id':item_line.program_id.id,
                             'name':item_line.budget_post_id.id,
                             'inicial':planificado,
                         })
                     else:
                         concejo_line_obj.create(cr, uid, {
                             'c_id':concejo_id,
                             'budget_id':item_id,
                             'program_id':item_line.program_id.id,
                             'name':item_line.budget_post_id.id,
                             'inicial':planificado,
                         })
      return True    
    
budgetCierre()

class budgetConcejoLine(osv.Model):
    _name = 'budget.concejo.line'
    _columns = dict(
        c_id = fields.many2one('budget.concejo','Presupuesto'),
        ci_id = fields.many2one('budget.concejo','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        budget_id = fields.many2one('budget.item','Partida Item'),
        name = fields.many2one('budget.post','Partida'),
        inicial = fields.float('Asignacion Inicial'),
    )
budgetConcejoLine()

class budgetConcejo(osv.Model):
    _name = 'budget.concejo'

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name_budget'], context=context)
        res = []
        for record in reads:
            name = record['name_budget'] 
            res.append((record['id'], name))
        return res        

    _columns = dict(
        name_budget = fields.related('name','name',type='char',size=10,
                                     string='Anio',store=True),
        state = fields.selection([('Borrador','Borrador'),('Aprobado','Aprobado')],'Estado'),
        year_id = fields.many2one('account.fiscalyear','Anio'),
        name = fields.many2one('budget.poa','Presupuesto'),
        line_ids = fields.one2many('budget.concejo.line','c_id','Detalle Presupuesto Gasto'),
        line_ids2 = fields.one2many('budget.concejo.line','ci_id','Detalle Presupuesto Ingreso'),
    )

    def apruebaConcejo(self, cr, uid, ids, context=None):
        concejo_obj = self.pool.get('budget.concejo')
        concejo_obj.write(cr, uid, ids[0],{'state':'Aprobado'})
        return True

    def clonaConcejo(self, cr, uid, ids, context=None):
        concejo_line_obj = self.pool.get('budget.concejo.line')
        item_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            line_antes = concejo_line_obj.search(cr, uid, [('c_id','=',this.id)])
            if line_antes:
                concejo_line_obj.unlink(cr, uid, line_antes)
            line_antes_ = concejo_line_obj.search(cr, uid, [('ci_id','=',this.id)])
            if line_antes_:
                concejo_line_obj.unlink(cr, uid, line_antes_)
            item_ingreso_ids = item_obj.search(cr, uid, [('poa_id','=',this.name.id),('type_budget','=','ingreso')])
            if item_ingreso_ids:
                for item_ingreso_id in item_ingreso_ids:
                    item = item_obj.browse(cr, uid, item_ingreso_id)
                    concejo_line_obj.create(cr, uid, {
                        'ci_id':this.id,
                        'program_id':item.program_id.id,
                        'budget_id':item.id,
                        'name':item.budget_post_id.id,
                        'inicial':item.planned_amount,
                    })
            item_gasto_ids = item_obj.search(cr, uid, [('poa_id','=',this.name.id),('type_budget','=','gasto')])
            if item_gasto_ids:
                for item_gasto_id in item_gasto_ids:
                    item = item_obj.browse(cr, uid, item_gasto_id)
                    concejo_line_obj.create(cr, uid, {
                        'c_id':this.id,
                        'program_id':item.program_id.id,
                        'budget_id':item.id,
                        'name':item.budget_post_id.id,
                        'inicial':item.planned_amount,
                    })                    
        return True

    _defaults = dict(
        state = 'Borrador',
    )

budgetConcejo()

############EVALUACION POR FUENTE DE FINANCIAMIENTO
class evaluacionFf(osv.TransientModel):
    _name = 'evaluacion.ff'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        obra = fields.char('Fuente Financiamiento',size=32),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
        department_id = fields.char('Departamento',size=3),
#        department_id = fields.many2one('hr.department','Departamento'),
    )

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                sal_percent = aux_percent = 0
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['paid_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)

    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        context2 = {}
        result = []
        period_obj = self.pool.get('account.period')
        department_obj = self.pool.get('hr.department')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            program_id = this.program_id.id
            obra = this.obra
            department_id = this.department_id
        c_b_lines_obj = self.pool.get('budget.item')
        if program_id:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','=',program_id)])        
        else:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}    
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                    
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            if department_id:
                if not (line.budget_post_id.name[0:3]==obra and line.budget_post_id.code[8:11]==department_id):
                    continue
            else:    
                if len(obra)=='3':
                    if not line.budget_post_id.code[11:14]==obra:
                        continue
                else:
                    if not line.budget_post_id.code[11:17]==obra:
                        continue
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_rec = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.paid_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                aux_percent_sal = 100 - aux_percent_rec
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'paid_amount':line.paid_amount,     
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.paid_amount - line.codif_amount
                aux_percent_rec = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['paid_amount']+=line.paid_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'paid_amount': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'nivel':0,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['to_rec']+=line_totales['to_rec']
#                res_line['total']['percent_rec']+=line_totales['percent_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line

    def exporta_excel_evff(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA FUENTE FINANCIAMIENTO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','INICIAL','REFORMAS','FINAL','PAGADO','%','SALDO','%'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = saldo_acumulado = por_saldo = 0 
            for values in dic_ord:
                if values['code']!=0 and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if (values['nivel']==7 or values['nivel']==8):
                        writer.append([values['code'],values['general_budget_name'],values['planned_amount'],values['reform_amount'],values['codif_amount'],values['paid_amount'],values['percent_rec'],values['to_rec'],values['percent_sal']])
            por_pagado = 0
            if res['total']['codif_amount']>0:
                por_pagado = (res['total']['paid_amount']*100) / res['total']['codif_amount']
            saldo_acumulado = res['total']['codif_amount'] - res['total']['paid_amount']
            por_saldo = 100 - por_pagado
            writer.append(['','TOTALES',res['total']['planned_amount'],res['total']['reform_amount'],res['total']['codif_amount'],res['total']['paid_amount'],por_pagado,saldo_acumulado,por_saldo])
        writer.save("evGastoObra.xls")
        out = open("evGastoObra.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evGastoObra.xls'})
        return True        

    def printEvaluacionFf(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.ff','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_ff',
            'model': 'evaluacion.ff',
            'datas': datas,
            'nodestroy': True,                        
            }
evaluacionFf()

class evaluacionFfComprometido(osv.TransientModel):
    _name = 'evaluacion.ff.comprometido'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        obra = fields.char('Fuente Financiamiento',size=32),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=64),
        department_id = fields.char('Departamento',size=3),
#        department_id = fields.many2one('hr.department','Departamento'),
    )

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                sal_percent = aux_percent = 0
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['commited_amount'] += data_suma['commited_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['commited_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'commited_amount':data['commited_amount'], #pagado - recaudado
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)

    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        context2 = {}
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            program_id = this.program_id.id
            obra = this.obra
            department_id = this.department_id
        c_b_lines_obj = self.pool.get('budget.item')
        if program_id:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','=',program_id)])        
        else:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}    
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                    
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            if department_id:
                if not (line.budget_post_id.name[0:3]==obra and line.budget_post_id.code[8:11]==department_id):
                    continue
            else:    
                if len(obra)=='3':
                    if not line.budget_post_id.code[11:14]==obra:
                        continue
                else:
                    if not line.budget_post_id.code[11:17]==obra:
                        continue
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.commited_amount
                aux_percent_rec = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.commited_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.commited_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                aux_percent_sal = 100 - aux_percent_rec
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'commited_amount':line.commited_amount,     
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.commited_amount
                aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.commited_amount - line.codif_amount
                aux_percent_rec = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.commited_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['commited_amount']+=line.commited_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'commited_amount': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'nivel':0,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['commited_amount']+=line_totales['commited_amount']
                res_line['total']['to_rec']+=line_totales['to_rec']
#                res_line['total']['percent_rec']+=line_totales['percent_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line

    def _get_anio(self,cr, uid, ids,code,name):
        post_obj = self.pool.get('budget.post')
        aux = ''
        if len(code)>8:
            post_ids = post_obj.search(cr, uid, [('code','=like',code[:len(code)-4]+"%")])
            if post_ids:
                post = post_obj.browse(cr, uid, post_ids[0])
                aux = post.parent_id.name
        return aux

    def exporta_excel_evfc(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE FUENTE FINANCIAMIENTO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','INICIAL','REFORMAS','FINAL','COMPROMETIDO','%','SALDO','%','Financiamiento($)'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = saldo_acumulado = por_saldo = 0 
            for values in dic_ord:
                if values['code']!=0 and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if (values['nivel']==7 or values['nivel']==8):
                        anio = self._get_anio(cr, uid, ids, values['code'],values['general_budget_name'])
                        writer.append([values['code'],values['general_budget_name'],values['planned_amount'],values['reform_amount'],values['codif_amount'],values['commited_amount'],values['percent_rec'],values['to_rec'],values['percent_sal']],anio)
            por_pagado = 0
            if res['total']['codif_amount']>0:
                por_pagado = (res['total']['commited_amount']*100) / res['total']['codif_amount']
            saldo_acumulado = res['total']['codif_amount'] - res['total']['commited_amount']
            por_saldo = 100 - por_pagado
            writer.append(['','TOTALES',res['total']['planned_amount'],res['total']['reform_amount'],res['total']['codif_amount'],res['total']['commited_amount'],por_pagado,saldo_acumulado,por_saldo])
        writer.save("evFuenteFinanciamientoComprometido.xls")
        out = open("evFuenteFinanciamientoComprometido.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evFuenteFinanciamientoComprometido.xls'})
        return True        

    def printEvaluacionFfComprometido(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.ff.comprometido','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_ff_comprometido',
            'model': 'evaluacion.ff.comprometido',
            'datas': datas,
            'nodestroy': True,                        
            }
evaluacionFfComprometido()

###################
class evaluacionObra(osv.TransientModel):
    _name = 'evaluacion.obra'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        obra = fields.char('Obra',size=32),
        obra_mayor = fields.many2one('budget.post','Obra Superior'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                sal_percent = aux_percent = aux_percent_mes = 0
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['paid_amount_mes'] += data_suma['paid_amount_mes']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['paid_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                    aux_percent_mes = (res[data['post'].parent_id.code]['paid_amount_mes']*100)/res[data['post'].parent_id.code]['codif_amount']
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_rec_mes'] = aux_percent_mes
                res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'paid_amount_mes':data['paid_amount_mes'],
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_rec_mes':data['percent_rec_mes'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)

    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        context2 = {}
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            program_id = this.program_id.id
            obra = this.obra
            mayor_obra = this.obra_mayor
        c_b_lines_obj = self.pool.get('budget.item')
        if program_id:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','=',program_id)])        
        else:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}    
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                    
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            if mayor_obra:
                aux_tam = len(mayor_obra.code)
                if not mayor_obra.code==line.budget_post_id.code[0:aux_tam]:
                    continue
            else:
                if not line.budget_post_id.name[0:3]==obra:
                    continue
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_rec = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.paid_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                if line.codif_amount==0:
                    aux_percent_sal = 0
                else:
                    aux_percent_sal = 100 - aux_percent_rec
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'paid_amount':line.paid_amount,    
                    'paid_amount_mes':line2.paid_amount, 
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_rec_mes':aux_percent_rec_mes,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.paid_amount
                if line.codif_amount==0:
                    aux_percent_sal = 0
                else:
                    aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.paid_amount - line.codif_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['paid_amount']+=line.paid_amount
                res_line[line.budget_post_id.id]['paid_amount_mes']+=line2.paid_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'paid_amount': 0.00,
            'paid_amount_mes': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'nivel':0,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['paid_amount_mes']+=line_totales['paid_amount_mes']
                res_line['total']['to_rec']+=line_totales['to_rec']
#                res_line['total']['percent_rec']+=line_totales['percent_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line


    def _get_totales_egreso(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            #partida_id = this.budget_id.id
            #project_id = this.project_id.id
        program_obj = self.pool.get('project.program')
        #date_from = resumen.date_start#self.datas['form']['date_from']
        #date_to = self.datas['form']['date_to']
        #program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        #program_code = self.datas['form']['program_id'][1][0:1]
        program_ids = program_obj.search(cr, uid, [])
        pr_ids = []
        if program_ids:
            for program_id in program_ids:
                pr_ids.append(program_id)
                #programa = program_obj.browse(self.cr, self.uid, program_id)
                #if programa.sequence[0:1]==program_code:
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.paid_amount
            comp_corte += line.paid_amount
        saldo = final_funcion - comp_mes
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result        

    def exporta_excel_evop(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE OBRA PAGADO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','INICIAL','REFORMAS','FINAL','PAGADO MES','%','PAGADO CORTE','%','SALDO','%'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = saldo_acumulado = por_saldo = 0 
            for values in dic_ord:
                if values['code']!=0 and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if (values['nivel']==7 or values['nivel']==8):
                        writer.append([values['code'],values['general_budget_name'],values['planned_amount'],values['reform_amount'],values['codif_amount'],values['paid_amount_mes'],'{:,.2f}'.format(values['percent_rec_mes']),values['paid_amount'],values['percent_rec'],values['to_rec'],values['percent_sal']])
            por_pagado = (res['total']['paid_amount']*100) / res['total']['codif_amount']
            por_pagado_mes = (res['total']['paid_amount_mes']*100) / res['total']['codif_amount']
            saldo_acumulado = res['total']['codif_amount'] - res['total']['paid_amount']
            por_saldo = 100 - por_pagado
            aux_total_reforma = 0
            if abs(res['total']['reform_amount'])>0.01:
                aux_total_reforma = res['total']['reform_amount']
            writer.append(['','TOTALES',res['total']['planned_amount'],res['total']['reform_amount'],res['total']['codif_amount'],res['total']['paid_amount_mes'],'{:,.2f}'.format(por_pagado_mes),res['total']['paid_amount'],por_pagado,saldo_acumulado,por_saldo])
            #total egresos
            #res_e=self._get_totales_egreso(cr, uid, ids)
            #writer.append(['','TOTAL EGRESOS',res_e[0],res_e[1],res_e[2],res_e[3],res_e[4],res_e[5],res_e[6],res_e[7],res_e[8]])
        writer.save("evGastoObra.xls")
        out = open("evGastoObra.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evGastoObra.xls'})
        return True        

    def printEvaluacionObra(self, cr, uid, ids, context):
        if context is None:
            context = {}
        for this in self.browse(cr, uid, ids):
            if not (this.obra or this.obra_mayor):
                raise osv.except_osv('Error de usuario','Debe seleccionar un campo de obra u obra mayor.')
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.obra','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_obra',
            'model': 'evaluacion.obra',
            'datas': datas,
            'nodestroy': True,                        
            }
evaluacionObra()

class evaluacionObraComprometido(osv.TransientModel):
    _name = 'evaluacion.obra.comprometido'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        obra = fields.char('Obra',size=32),
        obra_mayor = fields.many2one('budget.post','Obra Superior'),
        date_from = fields.date('Fecha Desde'),
        date_to = fields.date('Fecha Hasta'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                sal_percent = aux_percent = aux_percent_mes = 0
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['commited_amount'] += data_suma['commited_amount']
                res[data['post'].parent_id.code]['commited_amount_mes'] += data_suma['commited_amount_mes']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['commited_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                    aux_percent_mes = (res[data['post'].parent_id.code]['commited_amount_mes']*100)/res[data['post'].parent_id.code]['codif_amount']
                    res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
                else:
                    res[data['post'].parent_id.code]['percent_sal'] = 0
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_sal'] = aux_percent_mes
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'commited_amount':data['commited_amount'], #pagado - recaudado
                    'commited_amount_mes':data['commited_amount_mes'],
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_rec_mes':data['percent_rec_mes'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)

    def _get_totales(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        this=self.browse(cr, uid, ids[0])
        date_from = this.date_from
        date_to = this.date_to
        program_id = this.program_id.id
        c_b_lines_obj = self.pool.get('budget.item')
        period_obj = self.pool.get('account.period')
        post_obj = self.pool.get('budget.post')
        obra = this.obra
        mayor_obra_list = this.obra_mayor
        mayor_obra = False
        if mayor_obra_list:
            mayor_obra = post_obj.browse(cr, uid, mayor_obra_list.id) 
        ids_lines = []
        aux_date_start = this.date_from
        if program_id:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',this.poa_id.id),('type_budget','=','gasto'),('program_id','=',program_id)])
        else:
            ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',this.poa_id.id),('type_budget','=','gasto')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':this.poa_id.id}      
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':this.poa_id.id}                  
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
            if mayor_obra:
                aux_tam = len(mayor_obra.code)
                if not mayor_obra.code==line.budget_post_id.code[0:aux_tam]:
                    continue
            else:
                if not line.budget_post_id.name[0:3]==obra:
                    continue
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.commited_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.commited_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.commited_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.commited_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                if line.codif_amount==0:
                    aux_percent_sal = 0
                else:
                    aux_percent_sal = 100 - aux_percent_rec
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'commited_amount':line.commited_amount,    
                    'commited_amount_mes':line2.commited_amount,
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_rec_mes':aux_percent_rec_mes,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.commited_amount
                if line.codif_amount==0:
                    aux_percent_sal = 0
                else:
                    aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.commited_amount - line.codif_amount
                aux_percent_rec = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.commited_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.commited_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.budget_post_id.id]['commited_amount']+=line.commited_amount
                res_line[line.budget_post_id.id]['commited_amount_mes']+=line2.commited_amount
                res_line[line.budget_post_id.id]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'commited_amount': 0.00,
            'commited_amount_mes': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'nivel':0,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['commited_amount']+=line_totales['commited_amount']
                res_line['total']['commited_amount_mes']+=line_totales['commited_amount_mes']
                res_line['total']['to_rec']+=line_totales['to_rec']
#                res_line['total']['percent_rec']+=line_totales['percent_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line

    def _get_totales_egreso(self,cr, uid, ids):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            date_from = this.date_from
            date_to = this.date_to
            poa_id = this.poa_id.id
            #partida_id = this.budget_id.id
            #project_id = this.project_id.id
        program_obj = self.pool.get('project.program')
        #date_from = resumen.date_start#self.datas['form']['date_from']
        #date_to = self.datas['form']['date_to']
        #program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        #program_code = self.datas['form']['program_id'][1][0:1]
        program_ids = program_obj.search(cr, uid, [])
        pr_ids = []
        if program_ids:
            for program_id in program_ids:
                pr_ids.append(program_id)
                #programa = program_obj.browse(self.cr, self.uid, program_id)
                #if programa.sequence[0:1]==program_code:
        ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(cr, uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(cr, uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':poa_id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(cr,uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.commited_amount
            comp_corte += line.commited_amount
        saldo = final_funcion - comp_mes
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result        

    def exporta_excel_evoc(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            writer.append(['EVALUACION PRESPUESTARIA DE OBRA COMPROMETIDO'])
            writer.append(['DESDE',this.date_from,'HASTA',this.date_to])
            writer.append(['PARTIDA','DENOMINACION','INICIAL','REFORMAS','FINAL','COMP. Mes','%','COMP. CORTE','%','SALDO','%'])
            res=self._get_totales(cr, uid, ids)
            result_dic=res.values()
            import operator
            dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))
            por_pagado = saldo_acumulado = por_saldo = 0 
            for values in dic_ord:
                if values['code']!=0 and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
                    if (values['nivel']==7 or values['nivel']==8):
                        writer.append([values['code'],values['general_budget_name'],values['planned_amount'],values['reform_amount'],values['codif_amount'],values['commited_amount_mes'],'{:,.2f}'.format(values['percent_rec_mes']),values['commited_amount'],values['percent_rec'],values['to_rec'],values['percent_sal']])
            por_pagado = (res['total']['commited_amount']*100) / res['total']['codif_amount']
            por_pagado_mes = (res['total']['commited_amount_mes']*100) / res['total']['codif_amount']
            saldo_acumulado = res['total']['to_rec'] #- res['total']['commited_amount']
            por_saldo = 100 - por_pagado
            aux_total_reforma = 0
            if abs(res['total']['reform_amount'])>0.01:
                aux_total_reforma = res['total']['reform_amount']
            writer.append(['','TOTALES',res['total']['planned_amount'],res['total']['reform_amount'],res['total']['codif_amount'],res['total']['commited_amount_mes'],'{:,.2f}'.format(por_pagado_mes),res['total']['commited_amount'],por_pagado,saldo_acumulado,por_saldo])
            #total egresos
            #res_e=self._get_totales_egreso(cr, uid, ids)
            #writer.append(['','TOTAL EGRESOS',res_e[0],res_e[1],res_e[2],res_e[3],res_e[4],res_e[5],res_e[6],res_e[7],res_e[8]])
        writer.save("evGastoObraComprometido.xls")
        out = open("evGastoObraComprometido.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'evGastoObraComprometido.xls'})
        return True        

    def printEvaluacionObraComprometido(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = report.date_from
        data['date_to'] = report.date_to
        datas = {'ids': [report.id], 'model': 'evaluacion.obra.comprometido','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'evaluacion_obra_comprometido',
            'model': 'evaluacion.obra.comprometido',
            'datas': datas,
            'nodestroy': True,                        
            }
evaluacionObraComprometido()

class moveLineFinanciera(osv.Model):
    _inherit = 'account.move.line'
    _columns = dict(
        financia_id = fields.related('budget_id_cert','financia_id',type='many2one',relation='budget.financiamiento',
                                     string='Cuenta Financiera',store=True),
    )
moveLineFinanciera()    

class financiaReforma(osv.Model):
    _name = 'financia.reforma'
    _columns = dict(
        f_id = fields.many2one('partida.financia','Financia'),
        fecha = fields.date('Fecha'),
        monto = fields.float('Monto'),
    )
    
financiaReforma()

class partidaFinancia(osv.Model):
    _name = 'partida.financia'
    _order = 'code_financia asc,codigo_partida asc'

    def _amount_financia(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'reforma': 0.0,
                'codificado': 0.0,
                }
            aux_reforma = aux_codif = 0
            for line_line in line.reforma_ids:
                aux_reforma += line_line.monto
            aux_codif = line.monto + aux_reforma 
            res[line.id]['reforma'] = aux_reforma
            res[line.id]['codificado'] = aux_codif
        return res        


    def _get_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('financia.reforma').browse(cr, uid, ids, context=context):
            result[line.f_id.id] = True
        return result.keys()

    _columns = dict(
        is_recauda = fields.boolean('Automatiza Recaudacion'),
        is_reform = fields.boolean('Automatiza Reforma'),
        reforma_ids = fields.one2many('financia.reforma','f_id','Detalle Reforma'),
        codigo_partida = fields.related('budget_id','code',type='char',size=32,string='Code Partida Catalogo',store=True),
        name = fields.related('budget_id','name',type='char',size=256,string='Partida Catalogo',store=True),
        h_id = fields.many2one('partida.financia.head','Prespuesto'),
        active = fields.boolean('Activo'),
        project_id = fields.related('item_id','project_id',type='many2one',relation='project.project',string='Proyecto',store=True),
        #fields.many2one('project.project','Proyecto'),
        poa_id = fields.related('item_id','poa_id',type='many2one',relation='budget.poa',string='Presupuesto',store=True),
        #fields.many2one('budget.poa','Poa'),
        budget_id = fields.related('item_id','budget_post_id',type='many2one',relation='budget.post',string='Partida Catalogo',store=True),
        partida_id = fields.many2one('budget.post','Partida aux'),
        #budget_id = fields.many2one('budget.post','Partida'),
        item_id  = fields.many2one('budget.item','Partida'),
        code_financia = fields.related('financiera_id','name',type='char',size=10,string='Code financia',store=True),
        financiera_id = fields.many2one('budget.financiamiento','Cta. Financia'),
        monto = fields.float('Monto Inicial'),
        reforma = fields.function(_amount_financia, string='Reforma', multi="tl",store={'financia.reforma': (_get_line, ['monto'], 10)}),
        codificado = fields.function(_amount_financia, string='Codificado', multi="tl",store={'financia.reforma': (_get_line, ['monto'], 10)}),
        recaudado = fields.float('Recaudado',help="Si deja vacio este campo el sistema tomara la recaudacion de los comprobantes contables"),
        porcentaje = fields.float('Porcentaje'),
    )
    _defaults = dict(
        active = True,
    )
partidaFinancia()    

class partidaFinanciaHead(osv.Model):
    _name = 'partida.financia.head'
    _columns = dict(
        name = fields.many2one('budget.poa','Presupuesto',required=True),
        line_ids = fields.one2many('partida.financia','h_id','Detalle'),
    )
    
    def actualizaFinancia(self, cr, uid, ids, context):
        project_obj = self.pool.get('project.project')
        financia_obj = self.pool.get('partida.financia')
        for this in self.browse(cr, uid, ids):
            financia_antes = financia_obj.search(cr, uid, [('poa_id','=',this.name.id)])
            if financia_antes:
                financia_obj.unlink(cr, uid, financia_antes)
            project_ids = project_obj.search(cr, uid, [('poa_id','=',this.name.id),('type_budget','=','ingreso')])
            if project_ids:
                for project in project_obj.browse(cr, uid, project_ids):
                    for actividad in project.tasks:
                        for partida in actividad.budget_planned_ids:
                            financia_previo_ids = financia_obj.search(cr, uid, [('budget_id','=',partida.budget_post_id.id)])
                            if financia_previo_ids:
                                financia_previo = financia_obj.browse(cr, uid, financia_previo_ids[0])
                                financia_id = financia_previo.financiera_id.id
                            else:
                                financia_id = 1
                            financia_obj.create(cr, uid, {
                                'h_id':this.id,
                                'item_id':partida.id,
                                'financiera_id':financia_id,
                                'monto':partida.planned_amount,
                            })
        return True

    def clonaFinanciaHead(self, cr, uid, ids, context):
        head_obj = self.pool.get('partida.financia.head')
        line_obj = self.pool.get('partida.financia')
        item_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            line_antes = line_obj.search(cr, uid, [('h_id','=',this.id)])
            if line_antes:
                line_obj.unlink(cr, uid, line_antes)
            head_ids = head_obj.search(cr, uid, [('id','!=',this.id)])
            if head_ids:
                head = head_obj.browse(cr, uid, head_ids[0])
                for line in head.line_ids:
                    item_ids = item_obj.search(cr, uid, [('poa_id','=',this.name.id),('budget_post_id','=',line.budget_id.id)])
                    if item_ids:
                        line_obj.create(cr, uid, {
                            'h_id':this.id,
                            'item_id':item_ids[0],
                            'financiera_id':line.financiera_id.id,
                            'monto':line.monto,
                        })
        return True

partidaFinanciaHead()

class itemFinanciera(osv.Model):
    _inherit = 'budget.item'
    _columns = dict(
        financiera_id = fields.many2one('budget.financiamiento','Cta. Financia'),
    )
itemFinanciera()

#class certificateLineFinancia(osv.Model):
#    _inherit = 'budget.certificate.line'
#    _columns = dict(
#        financia_id = fields.many2one('budget.financiamiento','Cuenta Financiera'),
#    )
#certificateLineFinancia()

class programaUnidadLine(osv.Model):
    _name = 'programa.unidad.line'

    def _compute_valor(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            aux_result = this.p_id.total * (this.percent/100.00)
        res[this.id] = aux_result
        return res

    _columns = dict(
        p_id = fields.many2one('programa.unidad','Programa'),
        department_id = fields.many2one('hr.department','Unidad Operativa'),
        percent = fields.float('Porcentaje Asignacion'),
        amount = fields.function(_compute_valor,string='Monto Asignacion',type="float",store=True),
    )
programaUnidadLine()
class programaUnidad(osv.Model):
    _name = 'programa.unidad'

    def _compute_total_programa(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            cr.execute("select sum(planned_amount) from budget_item where poa_id=%s and program_id=%s and type_budget='gasto'" %(this.poa_id.id,this.program_id.id))
            aux = cr.fetchall()
            for aux_value in aux:
                aux_result = aux_value[0]
        res[this.id] = aux_result
        return res

    def _compute_total_presupuesto(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            cr.execute("select sum(planned_amount) from budget_item where poa_id=%s and type_budget='gasto'" %(this.poa_id.id))
            aux = cr.fetchall()
            for aux_value in aux:
                aux_result = aux_value[0]
        res[this.id] = aux_result
        return res

    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
        total_poa = fields.function(_compute_total_presupuesto,string='Total Presupuesto',type="float",store=True),
        total = fields.function(_compute_total_programa,string='Total Programa',type="float",store=True),
        line_ids = fields.one2many('programa.unidad.line','p_id','Unidad Operativa'),
    )
programaUnidad()

class concejoIngresos(osv.TransientModel):
    _name = 'concejo.ingresos'
    _columns = dict(
        budget_id = fields.many2one('budget.concejo','Presupuesto'),
    )

    def printConcejoIngresos(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'concejo.ingresos','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'concejo_ingresos',
            'model': 'concejo.ingresos',
            'datas': datas,
            'nodestroy': True,                        
            }

concejoIngresos()


class concejoGastos(osv.TransientModel):
    _name = 'concejo.gastos'
    _columns = dict(
        budget_id = fields.many2one('budget.concejo','Presupuesto'),
        program_id = fields.many2one('project.program','Programa'),
    )

    def printConcejoGastos(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'concejo.gastos','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'concejo_gastos',
            'model': 'concejo.gastos',
            'datas': datas,
            'nodestroy': True,                        
            }

concejoGastos()
