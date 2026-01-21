# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import osv, fields

class pacTdr(osv.Model):
    _name = 'pac.tdr'
    _columns = dict(
        user_id = fields.many2one('res.users','Creado por:'),
        code = fields.char('Numero',size=10),
        employee_id = fields.many2one('hr.employee','Responsable',required=True),
        name = fields.char('Nombre',size=256,required=True),
        antecedentes = fields.text('Antecedentes'),
        objetivo = fields.text('Objetivo General'),
        objetivo_esp = fields.text('Objetivo Especifico'),
        alcance = fields.text('Alcance'),
        metodologia = fields.text('Metodologia de trabajo'),
        informacion = fields.text('Informacion que dispone la entidad'),
        producto = fields.text('Producto o Servicio Esperado'),
        plazo = fields.text('Plazo de ejecucion total o parcial'),
        personal = fields.text('Personal Tecnico, equipo trabajo, recursos'),
        pago = fields.text('Formas o condiciones de pago'),
        state = fields.selection([('Borrador','Borrador'),('Aprobado','Aprobado')],'Estado'),
    )

    def print_tdr(self, cr, uid, ids, context=None):
        print "print"
        return True
        
    def draft_confirmed_tdr(self, cr, uid, ids, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        aux_code = obj_sequence.get(cr, uid, 'pac.tdr')
        self.write(cr, uid, ids[0],{
            'state':'Aprobado',
            'code':aux_code,
        })
        return True

    def return_draft_tdr(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0],{
            'state':'Borrador',
        })
        return True

    def _get_user(self,cr, uid, ids,context=None):
        return uid

    _defaults = dict(
        state = 'Borrador',
        user_id = _get_user,
    )


pacTdr()

class pacType(osv.Model):
    _description = 'Tipo Proceso'
    _name = 'pac.tipo'
    _columns = dict(
        name = fields.char('Tipo Compra',size=64,required=True)
    )
pacType()

class puRequisitionTipo(osv.Model):
    _inherit = 'purchase.requisition'
    _columns = dict(
        tipo_id = fields.many2one('pac.tipo','Tipo Proceso',required=True),
    )
puRequisitionTipo()    

class pacCategoria(osv.Model):
    _description = 'Categorias de bienes catalogo sercop'
    _name = 'pac.categoria'
    _columns = dict(
        name = fields.char('Nombre',size=64,required=True),
    )
pacCategoria()

class pacUom(osv.Model):
    _description = 'Unidades de medida pac'
    _name = 'pac.uom'
    _columns = dict(
        name = fields.char('Nombre',size=16,required=True),
    )
pacUom()

class productPac(osv.Model):
    _description = 'Catalogo PAC'
    _name = 'product.pac'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.read(cr, uid, ids, ['id','code', 'name'], context):
            res.append((record['id'], '%s - %s' % (record['code'], record['name'])))
        return res

    _columns = dict(
        code = fields.char('Codigo',size=16,required=True),
        name = fields.char('Descripcion',size=256,required=True),
        categ_id = fields.many2one('pac.categoria','Categoria',required=True),
        pu = fields.float('Precio Unitario'),
        uom = fields.many2one('pac.uom','Unidad',required=True),
    )
productPac()

class purchasePacLine(osv.Model):
    _description = 'Detalle PAC'
    _name = 'purchase.pac.line'

    def _compute_pac_total(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            aux = this.qty * this.name.pu
        res[this.id] = aux
        return res

    def onchange_pac(self, cr, uid, ids, product, context={}):
        pac_obj = self.pool.get('product.pac')
        vals = {}
        product = pac_obj.browse(cr, uid, product)
        return {'value':{'pu':product.pu}}

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids):
            res.append((record.id, '%s - %s' % (record.name.code, record.name.name)))
        return res

    _columns = dict(
        budget_id = fields.many2one('budget.post','Partida'),
        tipo = fields.selection([('Bienes','Bienes'),('Servicios','Servicios'),('Consultoria','Consultoria'),('Obra','Obra')],'Tipo Compra'),
        regimen = fields.selection([('Comun','Comun'),('Especial','Especial')],'Regimen'),
        bid = fields.selection([('Si','Si'),('No','No')],'Fondo BID'),
        tipo_budget = fields.selection([('Inversion','Inversion'),('Corriente','Corriente')],'Tipo Presupuesto'),
        tipo_producto = fields.selection([('Normalizado','Normalizado'),('No Normalizado','No Normalizado')],'Tipo Producto'),
        catalogo = fields.selection([('Si','Si'),('No','No')],'Catalogo Electronico'),
        procedimiento = fields.many2one('pac.tipo','Tipo Procedimiento'),
        p1 = fields.boolean('Cuat. 1'),
        p2 = fields.boolean('Cuat. 2'),
        p3 = fields.boolean('Cuat. 3'),
        pac_id = fields.many2one('purchase.pac','PAC'),
        name = fields.many2one('product.pac','Bien/Servicio',required=True),
        qty = fields.float('Cantidad',required=True),
        #no relacionado sino campo en la tabla
        pu_ant = fields.float('PU Anterior'),
        pu = fields.float('Precio Unitario'),
        uom = fields.many2one('pac.uom','Unidad',readonly=True),        
        total = fields.function(_compute_pac_total,string='Total',type="float",store=True),
    )

    _defaults = dict(
        bid = 'No',
    )

purchasePacLine()

class purchasePac(osv.Model):
    _description = 'Plan Anual de Compras'
    _name = 'purchase.pac'
    _columns = dict(
        code = fields.char('Codigo',size=12),
        creado_id = fields.many2one('res.users','Creado por'),
        name = fields.char('Descripcion',size=128),
        department_id = fields.many2one('hr.department','Direccion/Departamento',required=True),
        year_id = fields.many2one('account.fiscalyear','Anio Fiscal',required=True),
        line_ids = fields.one2many('purchase.pac.line','pac_id','Detalle'),
        state = fields.selection([('Borrador','Borrador'),('Aprobado','Aprobado'),('Agrupado','Agrupado'),('Anulado','Anulado')],'Estado'),
    )

    def pacBorrador(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'Borrador'})

    def pacAnulado(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'Anulado'})

    def pacAprobado(self, cr, uid, ids, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        for this in self.browse(cr, uid, ids):
            if not this.code:
                aux_code = obj_sequence.get(cr, uid, 'purchase.pac')
                self.write(cr, uid, ids, {'code':aux_code,'state':'Aprobado'})
            else:
                self.write(cr, uid, ids, {'state':'Aprobado'})
        return True

    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(('Error de usuario'), ('No puede eliminar documentos de PAC'))

    def _get_user(self,cr, uid, ids,context=None):
        return uid

    _defaults = dict(
        creado_id = _get_user,
        state = 'Borrador',
    )

purchasePac()

