# -*- coding: utf-8 -*-
##############################################################################
#
# GADMLI
#
##############################################################################

from osv import osv, fields
import time
import netsvc
from gt_tool import tool
from time import strftime, strptime
from datetime import date, datetime
from tools import ustr

class cumpleanios_line(osv.TransientModel):
    _name = 'cumpleanios.line'
    _order = 'dia_c'
    _columns = dict(
        empleado_id = fields.many2one('hr.employee','Funcionario'),
        cumpleanios_id = fields.many2one('cumpleanios','Cumpleanios'),
        edad = fields.integer('Edad'),
        fecha_n = fields.date('Fecha de Nacimiento'),
        empleado = fields.char('Empleado',size=255),
        dia_c=fields.integer('Dia'),
        frase = fields.char('Cumpleaños',size=255),
        dia_semana = fields.integer('dia s'),
        anio_act = fields.integer('año actual'),# de prueba borrar
        fecha_muestra = fields.char('fecha muestra',size=255),
        
    )
cumpleanios_line()

class cumpleanios(osv.TransientModel):
   _name = 'cumpleanios'
   _columns = dict(
      name = fields.char('Nombre',size=32),
      opcion = fields.selection([('Activos','Activos'),('Todos','Todos')],'Contratos??'),
      fech = fields.date('Fecha'),
      line_ids = fields.one2many('cumpleanios.line','cumpleanios_id','Detalle'),
      mes = fields.selection([('1','Enero'),('2','Febrero'),('3','Marzo'),('4','Abril'),('5','Mayo'),('6','Junio'),('7','Julio'),('8','Agosto'),('9','Septiembre'),('10','Octubre'),('11','Noviembre'),('12','Diciembre')],'Para conocer los cumpleañer@s escoja el Mes:'),
      
   )

   def enviar_email(self, cr, uid,context=None):
       print "DO SEND EMAIL CUMPLE"
       from tools import ustr
       user = self.pool.get('res.users').browse(cr, uid, uid)
       contract_obj = self.pool.get('hr.contract')
       obj_contrato = self.pool.get('hr.contract')
       holiday_obj = self.pool.get('holidays.period')
       fecha_actual = time.strftime('%Y-%m-%d')
       from datetime import date, datetime
       time_actual = datetime.today()
       mail_message = self.pool.get('mail.message')
       parameter_obj = self.pool.get('ir.config_parameter')
       contract_ids = obj_contrato.search(cr, uid, [('activo','=',True)])
       email_from = user.company_id.email
       if contract_ids:
           for contrato in contract_obj.browse(cr, uid, contract_ids, context):
               time_contrato = datetime.strptime(contrato.employee_id.birthday, "%Y-%m-%d")
               if time_contrato.day==time_actual.day and time_contrato.month==time_actual.month and time_contrato.year!=time_actual.year and contrato.activo:
                   razonSocial = user.company_id.name
                   msg = " Estimado  %s, \n\n Hoy es un dia especial. \n\n No hay nada mas bonito que poder disfrutar de un companero de trabajo como tu. \n\n Tampoco hay nada mas bonito que felicitarlo por el dia mas esperado del anio. \n\n Que seas feliz en este nuevo anio de tu vida, muchisimas felicidades"  %(ustr(contrato.employee_id.complete_name))
                   vals_msg = {
                       'subject': 'Feliz Cumple te desea ' + razonSocial,
                       'body_text': msg,
                       'email_from': email_from,
                       #'email_bcc' : email_copy,
                       'email_to': contrato.employee_id.email,
                       'state': 'outgoing',
                   }
                   email_msg_id = mail_message.create(cr, uid, vals_msg, context)
                   a = mail_message.send(cr, uid, [email_msg_id])
       return True
   
   def notificar_cumpleanios(self, cr, uid, ids, context=None):
       for this in self.browse(cr, uid, ids):
           print "do it"
       return True
   
   def mostrar_cumpleanios(self, cr, uid, ids, context=None):
       line_cumple_obj = self.pool.get('cumpleanios.line')
       contrato_obj = self.pool.get('hr.contract')
       today = datetime.today().strftime("%Y-%m-%d")
       
       fecha_actual1 = time.strptime(today, '%Y-%m-%d')
       cont=0
       cont1=0
       cont2=0
       for h in fecha_actual1:# recorremos toda la fecha
           if cont==2: # solo ingresara en el tercer campo es para sacar el dia de la fecha actual
               dia_actual1=h
           cont+=1
       for f in fecha_actual1:# recorremos toda la fecha
           if cont1==1: # solo ingresara en el tercer campo es para sacar el dia de la fecha actual
               mes_actual=f
           cont1+=1
       for g in fecha_actual1:# recorremos toda la fecha
           if cont2==0: # solo ingresara en el tercer campo es para sacar el dia de la fecha actual
               anio_actual=g
           cont2+=1

       mes_c=""
       meses= ""
       res=0
       now = today.split('-')                  
       datenow = date( int(now[0]), int(now[1]), int(now[2]) )
       
       for this in self.browse(cr, uid, ids):# en this carga los campos del formulario
           line_ids_antes_cumple = line_cumple_obj.search(cr, uid, [('cumpleanios_id','=',this.id)])
           if line_ids_antes_cumple:
               line_cumple_obj.unlink(cr, uid, line_ids_antes_cumple)

           if this.mes:
               if this.opcion=='Activos':     
                   #contrato_ids = contrato_obj.search(cr, uid, [('activo','=',True),('date_end','>=',today)])
                   contrato_ids = contrato_obj.search(cr, uid, ['|',('date_end','=',False),('date_end','>=',today),('activo','=',True)])
                   for line_id in contrato_ids:
                   
                       contratos = contrato_obj.browse(cr, uid, line_id)
                       mes_c = time.strptime(contratos.employee_id.birthday, '%Y-%m-%d')
                       mes_s = datetime.strptime(contratos.employee_id.birthday, '%Y-%m-%d')
                       fech = contratos.employee_id.birthday
                       
                       fecha_naci = fech.split('-')
                       datebirth = date( int(fecha_naci[0]), int(fecha_naci[1]), int(fecha_naci[2]) )
                       delta = datenow - datebirth
                       edad = delta.days/365
                       cons=0
                       cons1=0
                       cons2=0
                       cons3=0


                       for i in mes_c:# recorremos toda la fecha
                           if cons==1: # solo ingresara en el segundo campo es para sacar el MES de su cumpleaños
                               mes_cumple=i
                           cons+=1  
                       for f in mes_c:# recorremos toda la fecha
                           if cons1==2: # solo ingresara en el segundo campo es para sacar el dia de su cumpĺeaños
                               dia_cumple=f
                           cons1+=1

                       fecha_m = str(anio_actual) + "-" + str(mes_cumple) + "-" + str(dia_cumple)
                       obj = datetime.strptime(fecha_m, '%Y-%m-%d')
                       obj1 = obj.date()
                       ds1 = datetime.weekday(obj1)


                       if ds1 ==0:
                           dia_s= "Lunes "
                       elif ds1 ==1:
                           dia_s= "Martes "
                       elif ds1 ==2:
                           dia_s= "Miercoles "
                       elif ds1 ==3:
                           dia_s= "Jueves "
                       elif ds1 ==4:
                           dia_s= "Viernes "
                       elif ds1 ==5:
                           dia_s= "Sabado "
                       else:
                           dia_s= "Domingo "

                       if mes_cumple == 1:
                           meses= "Enero"
                       elif mes_cumple==2:
                           meses="Febrero"
                       elif mes_cumple==3:
                           meses="Marzo"
                       elif mes_cumple==4:
                           meses="Abril"
                       elif mes_cumple==5:
                           meses="Mayo"
                       elif mes_cumple==6:
                           meses="Junio"
                       elif mes_cumple==7:
                           meses="Julio"
                       elif mes_cumple==8:
                           meses="Agosto"
                       elif mes_cumple==9:
                           meses="Septiembre"
                       elif mes_cumple==10:
                           meses="Octubre"
                       elif mes_cumple==11:
                           meses="Noviembre"
                       else:
                           meses="Diciembre"
                           
                       if str(mes_cumple)==this.mes:

                           if mes_cumple > mes_actual:
                               if dia_cumple >= dia_actual1:
                                   edad= edad+1
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplirá "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                    'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                               else:
                                   edad= edad+1
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplirá "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                           elif mes_cumple < mes_actual:
                               if dia_cumple >= dia_actual1:
                                   
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplió "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                               else:
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplió "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                           else:
                               if dia_cumple >= dia_actual1:
                                   edad= edad+1
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplirá "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                               else:
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplió "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
               else:
                
                   contrato_ids = contrato_obj.search(cr, uid, [])
                   for line_id in contrato_ids:
                   
                       contratos = contrato_obj.browse(cr, uid, line_id)
                       mes_c = time.strptime(contratos.employee_id.birthday, '%Y-%m-%d')
                       mes_s = datetime.strptime(contratos.employee_id.birthday, '%Y-%m-%d')
                       fech = contratos.employee_id.birthday
                       
                       fecha_naci = fech.split('-')
                       datebirth = date( int(fecha_naci[0]), int(fecha_naci[1]), int(fecha_naci[2]) )
                       delta = datenow - datebirth
                       edad = delta.days/365
                       cons=0
                       cons1=0
                       cons2=0
                       cons3=0


                       for i in mes_c:# recorremos toda la fecha
                           if cons==1: # solo ingresara en el segundo campo es para sacar el MES de su cumpleaños
                               mes_cumple=i
                           cons+=1  
                       for f in mes_c:# recorremos toda la fecha
                           if cons1==2: # solo ingresara en el segundo campo es para sacar el dia de su cumpĺeaños
                               dia_cumple=f
                           cons1+=1

                       fecha_m = str(anio_actual) + "-" + str(mes_cumple) + "-" + str(dia_cumple)
                       obj = datetime.strptime(fecha_m, '%Y-%m-%d')
                       obj1 = obj.date()
                       ds1 = datetime.weekday(obj1)


                       if ds1 ==0:
                           dia_s= "Lunes "
                       elif ds1 ==1:
                           dia_s= "Martes "
                       elif ds1 ==2:
                           dia_s= "Miercoles "
                       elif ds1 ==3:
                           dia_s= "Jueves "
                       elif ds1 ==4:
                           dia_s= "Viernes "
                       elif ds1 ==5:
                           dia_s= "Sabado "
                       else:
                           dia_s= "Domingo "

                       if mes_cumple == 1:
                           meses= "Enero"
                       elif mes_cumple==2:
                           meses="Febrero"
                       elif mes_cumple==3:
                           meses="Marzo"
                       elif mes_cumple==4:
                           meses="Abril"
                       elif mes_cumple==5:
                           meses="Mayo"
                       elif mes_cumple==6:
                           meses="Junio"
                       elif mes_cumple==7:
                           meses="Julio"
                       elif mes_cumple==8:
                           meses="Agosto"
                       elif mes_cumple==9:
                           meses="Septiembre"
                       elif mes_cumple==10:
                           meses="Octubre"
                       elif mes_cumple==11:
                           meses="Noviembre"
                       else:
                           meses="Diciembre"
                           
                       if str(mes_cumple)==this.mes:

                           if mes_cumple > mes_actual:
                               if dia_cumple >= dia_actual1:
                                   edad= edad+1
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplirá "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                               else:
                                   edad= edad+1
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplirá "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                           elif mes_cumple < mes_actual:
                               if dia_cumple >= dia_actual1:
                                   
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplió "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                               else:
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplió "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                           else:
                               if dia_cumple >= dia_actual1:
                                   edad= edad+1
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplirá "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id})
                               else:
                                   frase1 = "El dia "+ dia_s + str(dia_cumple) + " de " + meses + " cumplió "+ str(edad) +" años"
                                   line_cumple_obj.create(cr, uid,   
                                   {'cumpleanios_id':this.id,'empleado':contratos.employee_id.complete_name,    
                                   'fecha_n':contratos.employee_id.birthday,'dia_c':dia_cumple,'frase':frase1,'empleado_id':contratos.employee_id.id}) 
       return True
                 
   _defaults = dict(
       
       opcion = 'Activos',
    )   
cumpleanios()

