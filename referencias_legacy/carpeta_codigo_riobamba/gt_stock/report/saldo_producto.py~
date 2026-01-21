import time
from report import report_sxw

class ReportKdxBodega(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportKdxBodega, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_bodega_kdx':self.get_bodega_kdx,
            'get_location_kdx':self.get_location_kdx,
            'browse_group': self.browse_group,
#            'convert_date': self.convert_date,
        })

    def get_location_kdx(self,objects):
        print "vele"
        return True

    def get_bodega_kdx(self,objects):
        line = ''
        bodega_obj = self.pool.get('stock.location')
        if objects.optionbg[0]=='Todas':
            return 'Todas'
        else:
            for bodega in objects.bodega_ids:
                line += "<th>%s</th>" % bodega.name
        return line

    def browse_group(self, objects):
        """
        return: []
        """
        data = []
        data2 = {}
        line_obj = self.pool.get('report.move.head')
#        objects.sort(key=lambda x: x.date)
        for p in objects[0].line_ids:
            if not data3.get(p.location_dest_id.id):
                data3.update({p.location_dest_id.id: {
                                                   'name': p.location_dest_id.name,
                                                   'qty': 0, 'ct': 0, }})
            data3[p.location_dest_id.id]['qty'] += p.qty
            data3[p.location_dest_id.id]['ct'] += p.ct
            if not data2.get(p.product_id.categ_id.id):
                data2.update({p.product_id.categ_id.id: {'line_ids':[],
                                                   'name': p.product_id.categ_id.name,
                                                   'qty': 0, 'ct': 0, }})
            data2[p.product_id.categ_id.id]['line_ids'].append(p)
            data2[p.product_id.categ_id.id]['qty'] += p.qty
            data2[p.product_id.categ_id.id]['ct'] += p.ct
        for k,v in data2.items():
            data.append(v)
#        for d in data:
#            d[''] = sum([p.activity_progress for p in d['project_ids']]) / len(d['project_ids'])
        return data

report_sxw.report_sxw('report.kdx.bodega',
                       'report.move.head', 
                       'addons/gt_stock_gpa/report/kdx_by_bodega.mako',
                       parser=ReportKdxBodega)
