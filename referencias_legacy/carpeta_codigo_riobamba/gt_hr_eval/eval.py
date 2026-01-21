# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from time import strftime, strptime
from osv import osv, fields
import netsvc
import addons
from random import choice
import os
import socket

class surveySendInvitation(osv.osv_memory):
    _inherit = 'survey.send.invitation'
    _columns = dict(
        user_ids = fields.many2many('res.users','survey_res_user','user_id',\
                                        'survey_id', "Usuarios", required=1),
        partner_ids = fields.many2many('res.partner','survey_res_partner','partner_id',\
                                'survey_id', "Answer"),
    )
    
    def action_send(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        employee_obj = self.pool.get('hr.employee')
        record = self.read(cr, uid, ids, [],context=context)
        survey_ids =  context.get('active_ids', [])
        record = record and record[0]
        partner_ids = record['partner_ids']
        user_ref= self.pool.get('res.users')
        survey_ref= self.pool.get('survey')
        mail_message = self.pool.get('mail.message')

        model_data_obj = self.pool.get('ir.model.data')
        group_id = model_data_obj._get_id(cr, uid, 'base', 'group_survey_user')
        group_id = model_data_obj.browse(cr, uid, group_id, context=context).res_id

        act_id = self.pool.get('ir.actions.act_window')
        act_id = act_id.search(cr, uid, [('res_model', '=' , 'survey.name.wiz'), \
                        ('view_type', '=', 'form')])
        out = "login,password\n"
        skipped = 0
        existing = ""
        created = ""
        error = ""
        user_exists = False
        new_user = []
        attachments = {}
        current_sur = survey_ref.browse(cr, uid, context.get('active_id'), context=context)
        exist_user = current_sur.invited_user_ids
        if exist_user:
            for use in exist_user:
                new_user.append(use.id)
        for id in survey_ref.browse(cr, uid, survey_ids):
            report = self.create_report(cr, uid, [id.id], 'report.survey.form', id.title)
            file = open(addons.get_module_resource('survey', 'report') + id.title +".pdf")
            file_data = ""
            while 1:
                line = file.readline()
                file_data += line
                if not line:
                    break
            file.close()
            attachments[id.title +".pdf"] = file_data
            os.remove(addons.get_module_resource('survey', 'report') + id.title +".pdf")
        
        if partner_ids:
            for partner in self.pool.get('res.partner').browse(cr, uid, partner_ids):
                if not partner.email:
                    skipped+= 1
                    continue
                user = user_ref.search(cr, uid, [('login', "=", partner.email)])
                if user:
                    if user[0] not in new_user:
                        new_user.append(user[0])
                    user = user_ref.browse(cr, uid, user[0])
                    user_ref.write(cr, uid, user.id, {'survey_id':[[6, 0, survey_ids]]})
                    mail = record['mail']%{'login':addr.email, 'passwd':user.password, \
                                                'name' : addr.name}
                    if record['send_mail_existing']:
                        mail_message.schedule_with_attach(cr, uid, record['mail_from'], [addr.email] , \
                                         record['mail_subject_existing'] , mail, context=context)
                        existing+= "- %s (Login: %s,  Password: %s)\n" % (user.name, addr.email, \
                                                                          user.password)
                    continue

                passwd= self.genpasswd()
                out+= partner.email + ',' + passwd + '\n'
                mail= record['mail'] % {'login' : partner.email, 'passwd' : passwd, 'name' : partner.name}
                if record['send_mail']:
                    ans = mail_message.schedule_with_attach(cr, uid, record['mail_from'], [partner.email], \
                                           record['mail_subject'], mail, attachments=attachments, context=context)
                    if ans:
                        res_data = {'name': partner.name or 'Unknown',
                                    'login': partner.email,
                                    'password': passwd,
                                    #'address_id': addr.id,
                                    'groups_id': [[6, 0, [group_id]]],
                                    'action_id': act_id[0],
                                    'survey_id': [[6, 0, survey_ids]]
                                   }
                        user = user_ref.create(cr, uid, res_data)
                        if user not in new_user:
                            new_user.append(user)
                        created+= "- %s (Login: %s,  Password: %s)\n" % (partner.name or 'Unknown',\
                                                                          partner.email, passwd)
                    else:
                        error+= "- %s (Login: %s,  Password: %s)\n" % (partner.name or 'Unknown',\
                                                                        partner.email, passwd)
        user_ids = record['user_ids']
        new_vals = {}
        new_vals.update({'invited_user_ids':[[6,0,new_user]]})
        if record['send_mail']:
            if user_ids:
                for user_id in user_ids:
                    user = user_ref.browse(cr, uid, user_id)
                    employee_ids = employee_obj.search(cr, uid, [('user_id','=',user_id)])
                    if employee_ids:
                        employee = employee_obj.browse(cr, uid, employee_ids[0])
                        if employee.work_email:
                            mail = record['mail']%{'login':user.login, 'passwd':user.password, \
                                                   'name' : user.name}
                            ans = mail_message.schedule_with_attach(cr, uid, record['mail_from'], [employee.work_email], \
                                                                    record['mail_subject'], mail, attachments=attachments, context=context)
        new_vals.update({'invited_user_ids':[[6,0,user_ids]]})
        survey_ref.write(cr, uid, context.get('active_id'),new_vals)
        note= ""
        if created:
            note += 'Created users:\n%s\n\n' % (created)
        if existing:
            note +='Already existing users:\n%s\n\n' % (existing)
        if skipped:
            note += "%d contacts where ignored (an email address is missing).\n\n" % (skipped)
        if error:
            note += 'E-Mail not send successfully:\n====================\n%s\n' % (error)
        context.update({'note' : note})
        return {
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'survey.send.invitation.log',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

surveySendInvitation()
