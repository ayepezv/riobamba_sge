openerp.gt_project_project = function(openerp){
    openerp.web.form.widgets.add('charbold', 'openerp.gt_project_project.FieldCharBold');
    openerp.gt_project_project.FieldCharBold = openerp.web.form.FieldChar.extend({
        template: 'charbold',
        init: function(view, code){
            console.log('construyendo field chars...');
            this._super(view, code);
        },
    });

}
