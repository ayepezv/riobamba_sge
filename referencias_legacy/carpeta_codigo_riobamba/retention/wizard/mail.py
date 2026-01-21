# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

__author__ = 'Mario Chogllo'

from osv import osv, fields

class mailAttach(osv.TransientModel):
    _inherit = 'mail.compose.message'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        result = super(mailAttach, self).default_get(cr, uid, fields, context=context)
        vals = {}
        reply_mode = context.get('mail.compose.message.mode') == 'reply'
        if (not reply_mode) and context.get('active_model') and context.get('active_id'):
            # normal mode when sending an email related to any document, as specified by
            # active_model and active_id in context
            vals = self.get_value(cr, uid, context.get('active_model'), context.get('active_id'), context)
        elif reply_mode and context.get('active_id'):
            # reply mode, consider active_id is the ID of a mail.message to which we're
            # replying
            vals = self.get_message_data(cr, uid, int(context['active_id']), context)
        else:
            # default mode
            result['model'] = context.get('active_model', False)
        for field in vals:
            if field in fields:
                result.update({field : vals[field]})

        # link to model and record if not done yet
        if not result.get('model') or not result.get('res_id'):
            active_model = context.get('active_model')
            res_id = context.get('active_id')
            if active_model and active_model not in (self._name, 'mail.message'):
                result['model'] = active_model
                if res_id:
                    result['res_id'] = res_id

        # Try to provide default email_from if not specified yet
        if not result.get('email_from'):
            current_user = self.pool.get('res.users').browse(cr, uid, uid, context)
            result['email_from'] = current_user.user_email or False
        if context.get('attachment_ids'):
            result['attachment_ids']=context['attachment_ids']
        return result

mailAttach()
