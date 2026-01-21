# -*- coding: utf-8 -*-
##############################################################################
#
# GADMLI
# SISTEMAS
#
##############################################################################
import time
from report import report_sxw
from osv import fields, osv
from gt_tool import XLSWriter
import re

class reporte_notificacion_multa(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(reporte_notificacion_multa, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_mes':self.get_mes,
            'get_genero':self.get_genero,
            'get_genero_emp':self.get_genero_emp,
        })

    def get_mes(self,t1):
        cont=0
        cont2=0
        cont3=0

        for i in t1:
            if cont==2: 
                dia=i
            cont+=1  

        for i in t1:
            if cont2==1: 
                mes=i
            cont2+=1 

        for i in t1:
            if cont3==0: 
                anio=i
            cont3+=1

        if mes==1:
            mes1="Enero"
        elif mes==2:
            mes1="Febrero"
        elif mes==3:
            mes1="Marzo"
        elif mes==4:
            mes1="Abril"
        elif mes==5:
            mes1="Mayo"
        elif mes==6:
            mes1="Junio"
        elif mes==7:
            mes1="Julio"
        elif mes==8:
            mes1="Agosto"
        elif mes==9:
            mes1="Septiembre"
        elif mes==10:
            mes1="Octubre"
        elif mes==11:
            mes1="Noviembre"
        else:
            mes1="Diciembre"   
        
        fecha_m = str(dia) + " de " + str(mes1) + " del " + str(anio)

        return fecha_m

    def get_genero(self,genero):
        gen=""
        if genero=="F":
            gen = "a la Sra."
        else:
            gen = "al Sr."

        return gen

    def get_genero_emp(self,genero1):
        gen1=""
        if genero1=="female":
            gen1 = "la"
        else:
            gen1 = "el"
        return gen1

      
report_sxw.report_sxw('report.reporte_notificacion_multa',
                       'reporte.notificacion.multa', 
                       'addonsgob/comisaria/report/reporte_notificacion_multa.mako',
                       parser=reporte_notificacion_multa,
                       header=False)


