# -*- coding: utf-8 -*-
##############################################################################
#
#    Carpeta - Documentos contables
#    Copyright (C) 2013 Mario Chogllo
#    mariofchogllo@gmail..com
#    $Id$
#
##############################################################################

from osv import osv, fields
import time
from tools import ustr
from gt_tool import XLSWriter

class wizardMoveExcel(osv.TransientModel):
    _name = 'wizard.move.excel'
    _columns = dict(
        opc1 = fields.selection([('only','Solo Una cuenta'),('all','Todas las cuentas')],'Todas las cuentas'),
        opc = fields.selection([('Ingresos','Ingresos'),('Egresos','Egresos'),('Todo','Todo')],'Opcion'),
        banco_id = fields.many2one('account.account','Banco'),
        date_start = fields.date('Fecha Desde'),
        date_end = fields.date('Fecha Hasta'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def default_get(self, cr, uid, fields, context=None):
        parameter_obj = self.pool.get('ir.config_parameter')
        account_obj = self.pool.get('account.account')
        if context is None:
            context = {}
        res = {}
        banco_param_ids = parameter_obj.search(cr, uid, [('key','=','bancoCentral')],limit=1)
        if banco_param_ids:
            aux_banco = parameter_obj.browse(cr, uid, banco_param_ids[0]).value
            banco_ids = account_obj.search(cr, uid, [('code','=',aux_banco)],limit=1)
            if banco_ids:
                res.update({'banco_id':banco_ids[0],'opc':'Egresos','opc1':'all'})
        return res    

    def actionMoveExcel(self, cr,  uid, ids, context):
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        for this in self.browse(cr, uid, ids):
            str_date_ini = "'" + this.date_start + "'"
            str_date_end = "'" + this.date_end + "'"
            if this.opc=='Todo':
                aux = '''select id,cast(name as int) from account_move where name!='/' and date>=%s and state='posted' and date<=%s order by name''' % (str_date_ini,str_date_end)
                cr.execute(aux)
                writer = XLSWriter.XLSWriter()
                writer.append(['DETALLE COMPROBANTES'])
                writer.append(['DESDE',this.date_start])
                writer.append(['HASTA',this.date_end])
                writer.append(['NUMERO COMPROBANTE','FECHA','BENEFICIARIO','TOTAL COMPROBANTE','TOTAL BANCO','DETALLE'])
                for row in cr.fetchall():
                    move = move_obj.browse(cr, uid, row[0])
                    #aqui preguntar si es egreso
                    writer.append([move.name,move.date,ustr(move.partner_id.name),move.amount,move.total_banco,ustr(move.narration)])
            elif this.opc=='Egresos':
#                aux = '''select id,cast(name as int) from account_move where id in (select move_id from account_move_line where account_id in (select default_debit_account_id from account_journal) and date>=%s and state='posted' and date<=%s and credit>0) order by name''' % (str_date_ini,str_date_end)
                if this.opc1=='only':
                    aux ='''select account_move_line.id,move_id,cast(account_move.name as int),credit from account_move_line,account_move where account_id=%s
                    and account_move.date>=%s and account_move.date<=%s and credit>0 and account_move.id=account_move_line.move_id and account_move.state='posted' order by account_move.name'''  % (this.banco_id.id,str_date_ini,str_date_end)
                else:
                    journal_ids = journal_obj.search(cr, uid, [])
                    journal_ids1 = journal_obj.search(cr, uid, [('name','=','INGRESOS')])
                    if journal_ids:
                        ids_bancos = []
                        for journal_id in journal_ids:
                            journal = journal_obj.browse(cr, uid, journal_id)
                            if journal.default_debit_account_id:
                                if journal.default_debit_account_id.code[0:3]=='111':
                                    ids_bancos.append(journal.default_debit_account_id.id)
                    move_ids = move_obj.search(cr, uid, [('journal_id','!=',journal_ids1[0]),('date','>=',this.date_start),('date','<=',this.date_end),
                                                         ('state','in',('posted','anulado'))],order='name asc')
#                    aux ='''select account_move_line.id,move_id,cast(account_move.name as int),credit from account_move_line,account_move where account_move.journal_id!=%s and account_move.date>=%s and account_move.date<=%s and credit>0 and account_move.journal_id!=%s and account_move.id=account_move_line.move_id and account_move.state='posted' order by account_move.name'''  % (journal_ids1[0],str_date_ini,str_date_end,journal_ids1[0])
#                    aux ='''select account_move_line.id,move_id,cast(account_move.name as int),credit from account_move_line,account_move where account_id in %s
#                    and account_move.date>=%s and account_move.date<=%s and credit>0 and account_move.journal_id!=%s and account_move.id=account_move_line.move_id and account_move.state='posted' order by account_move.name'''  % (tuple(ids_bancos),str_date_ini,str_date_end,journal_ids1[0])
#                cr.execute(aux)
                writer = XLSWriter.XLSWriter()
                writer.append(['DETALLE COMPROBANTES'])
                writer.append(['DESDE',this.date_start])
                writer.append(['HASTA',this.date_end])
                writer.append(['NUMERO COMPROBANTE','FECHA','BENEFICIARIO','TOTAL COMPROBANTE','TOTAL BANCO','DETALLE'])
                if move_ids:
                    for move_id in move_ids:
                        move = move_obj.browse(cr, uid, move_id)
                        writer.append([move.name,move.date,ustr(move.partner_id.name),move.amount,move.total_banco,ustr(move.narration)])                
                else:
                    for row in cr.fetchall():
                        move = move_obj.browse(cr, uid, row[1])
                        #writer.append([move.name,move.date,ustr(move.partner_id.name),move.amount,row[3],ustr(move.narration)])                
        writer.save("Comprobantes.xls")
        out = open("Comprobantes.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'Comprobantes.xls'})
        return True

    _defaults = dict(
        opc = 'Egresos',
        opc1= 'all',
    )

wizardMoveExcel()

class wizardMoveFolder(osv.TransientModel):
    _name = 'wizard.move.folder'
    _columns = dict(
        move_id = fields.many2one('account.move','Numero'),
    )

    def action_move_folder(self, cr,  uid, ids, context):
        move_obj = self.pool.get('account.move')
        line_obj = self.pool.get('account.folder.line')
        for this in self.browse(cr, uid, ids):
            line_id = line_obj.create(cr, uid, {
                'f_id':context['active_id'],
                'date':this.move_id.date,
                'name':this.move_id.name,
                'partner_id':this.move_id.partner_id.id,
                'narration':this.move_id.narration,
            })
            move_obj.write(cr, uid, [this.move_id.id],{
                'archivado':True,
            })
        return {'type':'ir.actions.act_window_close' }

wizardMoveFolder()

class accountFolderLine(osv.Model):
    _name = 'account.folder.line'
    _columns = dict(
        f_id = fields.many2one('account.folder','Carpeta'),
        date = fields.date('Fecha',required=True),
        name = fields.char('Comprobante',size=32,required=True),
        partner_id = fields.many2one('res.partner','Beneficiario',required=True),
        narration = fields.text('Descripcion',required=True),
        monto = fields.float('Monto'),
    )
accountFolderLine()

class accountFolder(osv.Model):
    _description = 'Carpeta docuemntos contables'
    _name = 'account.folder'
    _columns = dict(
        name = fields.integer('Numero Carpeta'),
        move_ids = fields.one2many('account.folder.line','f_id','Comprobantes Contables'),
    )
    _sql_constraints = [('unique_numero_folder', 'unique(name)', u'El número de carpeta es único.')]
accountFolder()
