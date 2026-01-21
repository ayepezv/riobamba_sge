# -*- coding: utf-8 -*-
###############################################################################
#                              
#    Gnuthink Cia. Ltda., Cuenca, Ecuador
#    OpenERP ready partner, open source editor.
#    www.gnuthink.com, (+593) 074092170
#     
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#
##############################################################################

import datetime

def get_day(fecha):
    time_fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
    return time_fecha.day

def get_month(fecha):
    time_fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
    return time_fecha.month

def get_year(fecha):
    time_fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
    return time_fecha.year

def today_day():
    time_fecha = datetime.datetime.today()
    return time_fecha.day

def today_month():
    time_fecha = datetime.datetime.today()
    return time_fecha.month

def today_year():
    time_fecha = datetime.datetime.today()
    return time_fecha.year

def greater_or_equal_than(fecha1,fecha2):
    resultado = -1
    time_fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d")
    time_fecha2 = datetime.datetime.strptime(fecha2, "%Y-%m-%d")
    if time_fecha1>=time_fecha2:
        resultado = 1
    else:
        resultado = 0
    return resultado

def greater_than(fecha1,fecha2):
    resultado = -1
    time_fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d")
    time_fecha2 = datetime.datetime.strptime(fecha2, "%Y-%m-%d")
    if time_fecha1>time_fecha2:
        resultado = 1
    else:
        resultado = 0
    return resultado

def lower_than(fecha1,fecha2):
    resultado = -1
    time_fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d")
    time_fecha2 = datetime.datetime.strptime(fecha2, "%Y-%m-%d")
    if time_fecha1<time_fecha2:
        resultado = 1
    else:
        resultado = 0
    return resultado

def lower_or_equal_than(fecha1,fecha2):
    resultado = -1
    time_fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d")
    time_fecha2 = datetime.datetime.strptime(fecha2, "%Y-%m-%d")
    if time_fecha1<=time_fecha2:
        resultado = 1
    else:
        resultado = 0
    return resultado