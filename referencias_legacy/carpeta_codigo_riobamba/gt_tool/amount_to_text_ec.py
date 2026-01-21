# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

#-------------------------------------------------------------
#ESPAÑOL ECUADOR
#-------------------------------------------------------------
#from tools.translate import _
UNIDADES = ('','UN ','DOS ','TRES ','CUATRO ','CINCO ','SEIS ','SIETE ','OCHO ','NUEVE ','DIEZ ','ONCE ','DOCE ','TRECE ','CATORCE ','QUINCE ',   'DIECISEIS ', 'DIECISIETE ',
	    'DIECIOCHO ', 'DIECINUEVE ', 'VEINTE ')
DECENAS = ( 'VENTI', 'TREINTA ', 'CUARENTA ', 'CINCUENTA ', 'SESENTA ', 'SETENTA ', 'OCHENTA ', 'NOVENTA ', 'CIEN ')
CENTENAS = ('CIENTO ', 'DOSCIENTOS ', 'TRESCIENTOS ', 'CUATROCIENTOS ', 'QUINIENTOS ', 'SEISCIENTOS ', 'SETECIENTOS ', 'OCHOCIENTOS ', 'NOVECIENTOS ')

def amount_to_text_ec(monto):
    f = float(monto)
    ent = int(f)
    dec = f - ent
    res1 = toWord(ent)
    return '%s con %.2f/100' % (res1.encode('utf-8'), dec*100)        

def toWord(number):

    """
    Converts a number into string representation
    """
    converted = ''

    if not (0 < number < 999999999):

        return 'No es posible convertir el numero a letras'

    number_str = str(number).zfill(9)
    millones = number_str[:3]
    miles = number_str[3:6]
    cientos = number_str[6:]

    if(millones):
        if(millones == '001'):
            converted += 'UN MILLON '
        elif(int(millones) > 0):
            converted += '%sMILLONES ' % __convertNumber(millones)

    if(miles):
        if(miles == '001'):
            converted += 'MIL '
        elif(int(miles) > 0):
            converted += '%sMIL ' % __convertNumber(miles)

    if(cientos):
        if(cientos == '001'):
            converted += 'UN '
        elif(int(cientos) > 0):
            converted += '%s ' % __convertNumber(cientos)

    converted += ''

    return converted.title()

def __convertNumber(n):
    """
    Max length must be 3 digits
    """
    output = ''

    if(n == '100'):
        output = "CIEN "
    elif(n[0] != '0'):
        output = CENTENAS[int(n[0])-1]

    k = int(n[1:])
    if(k <= 20):
        output += UNIDADES[k]
    else:
        if((k > 30) & (n[2] != '0')):
            output += '%sY %s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])
        else:
            output += '%s%s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])

    return output

if __name__=='__main__':
    from sys import argv
    f = float(argv[1])
    ent = int(f)
    dec = f - ent
    res1 = toWord(ent)
    print '%s con %.2f/100' % (res1.encode('utf-8'), dec*100)    

