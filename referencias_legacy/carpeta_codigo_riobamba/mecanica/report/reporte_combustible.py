# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
import time
from report import report_sxw
from osv import fields, osv
from gt_tool import XLSWriter
import re

class reporte_combustible(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(reporte_combustible, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_vehiculo_combustible': self.get_vehiculo_combustible,
            'get_consumo_mensual':self.get_consumo_mensual,
            'get_numero_registros':self.get_numero_registros,
            'get_mes':self.get_mes,
            'get_mes3':self.get_mes3,
            'get_mes_nom':self.get_mes_nom,
        })


    def get_mes(self,this):
        
        combus_obj = self.pool.get('vehiculo.combustible') 
        combus_ids = [this.vehiculorc_id.id]
        for vehiculorc_id in combus_ids:
            if this.opc:
                if this.date_start:
                    combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id),('date','>=',this.date_start),  
                    ('date','<=',this.date_stop)])
                else:
                    combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id),('date','<=',this.date_stop)])
            else:
                combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id)])
       
        cons=0   
        mes=""
        res=0
        
        
        for combus_id in combus_ids:
            combus = combus_obj.browse(self.cr, self.uid, combus_id)
            mes = time.strptime(combus.date, '%Y-%m-%d')#escogemos la fecha campo date y le pasamos la variable mes campo string
            for i in mes:# recorremos toda la fecha
                if cons==1: # solo ingresara en el segundo campo es para sacar el MES pero solo del primer registro date.
                    res=i
                cons+=1         


        if res==1:
            mes1="Enero"
        elif res==2:
            mes1="Febrero"
        elif res==3:
            mes1="Marzo"
        elif res==4:
            mes1="Abril"
        elif res==5:
            mes1="Mayo"
        elif res==6:
            mes1="Junio"
        elif res==7:
            mes1="Julio"
        elif res==8:
            mes1="Agosto"
        elif res==9:
            mes1="Septiembre"
        elif res==10:
            mes1="Octubre"
        elif res==11:
            mes1="Noviembre"
        else:
            mes1="Diciembre"   
        return mes1


    def get_mes3(self,t1):
        cont2=0
        for i in t1:
            if cont2==1: 
                res=i
            cont2+=1  


        if res==1:
            mes1="Enero"
        elif res==2:
            mes1="Febrero"
        elif res==3:
            mes1="Marzo"
        elif res==4:
            mes1="Abril"
        elif res==5:
            mes1="Mayo"
        elif res==6:
            mes1="Junio"
        elif res==7:
            mes1="Julio"
        elif res==8:
            mes1="Agosto"
        elif res==9:
            mes1="Septiembre"
        elif res==10:
            mes1="Octubre"
        elif res==11:
            mes1="Noviembre"
        else:
            mes1="Diciembre"   
        return res

    def get_mes_nom(self,res):

        if res==1:
            mes1="Enero"
        elif res==2:
            mes1="Febrero"
        elif res==3:
            mes1="Marzo"
        elif res==4:
            mes1="Abril"
        elif res==5:
            mes1="Mayo"
        elif res==6:
            mes1="Junio"
        elif res==7:
            mes1="Julio"
        elif res==8:
            mes1="Agosto"
        elif res==9:
            mes1="Septiembre"
        elif res==10:
            mes1="Octubre"
        elif res==11:
            mes1="Noviembre"
        else:
            mes1="Diciembre"   
        return mes1

    def get_vehiculo_combustible(self,this):
       
        combus_obj = self.pool.get('vehiculo.combustible') 
        combus_ids = [this.vehiculorc_id.id]
        for vehiculorc_id in combus_ids:
            if this.opc:
                if this.date_start:
                    combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id),('date','>=',this.date_start),  
                    ('date','<=',this.date_stop)])
                else:
                    combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id),('date','<=',this.date_stop)])
            else:
                combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id)])
                    
        return combus_obj.browse(self.cr, self.uid,combus_ids)
       


    def get_numero_registros(self,this):
        
        combus_obj = self.pool.get('vehiculo.combustible') 
        combus_ids = [this.vehiculorc_id.id]
        for vehiculorc_id in combus_ids:
            if this.opc:
                if this.date_start:
                    combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id),('date','>=',this.date_start),  
                    ('date','<=',this.date_stop)])
                else:
                    combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id),('date','<=',this.date_stop)])
            else:
                combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id)])
                    
        return len(combus_ids)

    def get_consumo_mensual(self,this):
        
        combus_obj = self.pool.get('vehiculo.combustible') 
        combus_ids = [this.vehiculorc_id.id]
        for vehiculorc_id in combus_ids:
            if this.opc:
                if this.date_start:
                    combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id),('date','>=',this.date_start),  
                    ('date','<=',this.date_stop)])
                else:
                    combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id),('date','<=',this.date_stop)])
            else:
                combus_ids = combus_obj.search(self.cr, self.uid, [('vehiculoc_id','=',vehiculorc_id)])
                    
        aux  = 0
        for combus_id in combus_ids:
            combus = combus_obj.browse(self.cr, self.uid, combus_id)
            aux += combus.cantidad
        return aux

 


      
report_sxw.report_sxw('report.reporte_combustible',
                       'reporte.combustible', 
                       'addonsgob/mecanica/report/reporte_combustible.mako',
                       parser=reporte_combustible,
                       header=False)


