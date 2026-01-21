<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h3 style="text-align:center;" align="center">MECANICA MUNICIPAL</h3>
   <center> 
        <b>
          <FONT size= 3 >Reporte de Combustibles: ${ o.opcion }</FONT>
          <br>
          <i><FONT size= 3 >${ o.vehiculorc_id.name.name }</FONT></i>
          <br>
          <FONT size= 3 >Fechas: ${ o.date_start } - ${ o.date_stop }</FONT>
        </b>
   </center>
   <h5 style="text-align:center;" align="center">COMBUSTIBLES</h5>
             <%
               var1 = get_mes(o)
             %>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
         <th width="11%" style="text-align:center;">${ var1}</th>
       </tr>
     </thead>
   </table>

   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
         <th width="11%" style="text-align:center;">Fecha</th>
	 <th width="10%" style="text-align:center;">Cantidad</th>
         <th width="12%" style="text-align:center;">Kilometraje</th>
         <th width="12%" style="text-align:center;">Rendimiento</th>
       </tr>
     </thead>
   </table>


      <% 
      ultimo_rk = 0
      ultimo_rki = 0
      m1 = m2 = 0
      conta=0
      ren=0
      ren_pro=0
      ultimo= 0
      primero = 0
      cantidad = 0
      reg_cant = 0
      cont=0
      cant=0
      mes_igual = True
      %>
   %for combustible_id in get_vehiculo_combustible(o):


         %if cont==0:
         <%
           t1 = time.strptime(combustible_id.date, '%Y-%m-%d')
           m1=get_mes3(t1)
           cont=1
         %>
         %else:
         <%
           t2 = time.strptime(combustible_id.date, '%Y-%m-%d')
           m2=get_mes3(t2)
           cont=0
         %>
         %endif


         %if primero==0:
            <%    
              primer_rk = combustible_id.name
              cant=combustible_id.cantidad
            %>
         %else:
            %if m1==m2:
              %if mes_igual==True:
              <%
                 reg_cant += combustible_id.cantidad
              %>
              %else:
              <%
                 reg_cant = 0
              %>
              %endif
            %endif

         %endif
         
         <% 
         longitud = get_numero_registros(o)
         ultimo = ultimo +1
         primero = primero +1
         %>

         %if longitud==ultimo:
             <%    
               ultimo_rk = combustible_id.name
             %>

         %endif

         %if m1==m2:
         <%
           mes_igual=True  
           cant+=combustible_id.cantidad
           ultimo_rki = combustible_id.name
         %>
           %if ren!=0:
             <%
               ren=(combustible_id.name - ren)/(combustible_id.cantidad)
             %>
           %endif
         
         %else:
                %if m1>m2:
                  %if conta >0:

                    %if reg_cant==0:
                      <%
                        ren_pro = reg_cant
                      %>
                    %else:
                      <%
                        ren_pro = (ultimo_rki - primer_rk) / reg_cant
                      %>
                    %endif
                 
                  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-
                   collapse:collapse;font-size:12px">
                  <thead>
                   <tr>
                     <th width="11%" style="text-align:center;">Consumo Mensual</th>
                     <th width="10%" style="text-align:center;">${ cant }</th>
                     <th width="12%" style="text-align:center;">Rendimiento Promedio</th>
                     <th width="12%" style="text-align:center;">${ '{:,.2f}'.format(ren_pro) }</th>
                   </tr>
                  </thead>
                    <%
                      ren_pro = 0
                      cant=0
                      cant+=combustible_id.cantidad
                      reg_cant=combustible_id.cantidad
                      primer_rk=combustible_id.name
                    %> 
                    %if ren!=0:
                      <%
                          ren=(combustible_id.name - ren)/(combustible_id.cantidad)
                      %>
                    %endif
                         
                  </table>
                      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000"
                       style="border-collapse:collapse;font-size:12px">
                       <thead>
                        <tr>
                          <th width="11%" style="text-align:center;">${ get_mes_nom(m1)}</th>
                        </tr>
                       </thead>
                   </table>
                  %endif
                  <%
                    conta = conta + 1
                  %>
                %else:
                    %if reg_cant==0:
                      <%
                        ren_pro = reg_cant
                      %>
                    %else:
                      <%
                        ren_pro = (ultimo_rki - primer_rk) / reg_cant
                      %>
                    %endif
                    %if ren!=0:
                      <%
                          ren=(combustible_id.name - ren)/(combustible_id.cantidad)
                      %>
                    %endif                
                  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-
                   collapse:collapse;font-size:12px">
                  <thead>
                   <tr>
                     <th width="11%" style="text-align:center;">Consumo Mensual</th>
                     <th width="10%" style="text-align:center;">${ cant }</th>
                     <th width="12%" style="text-align:center;">Rendimiento Promedio</th>
                     <th width="12%" style="text-align:center;">${ '{:,.2f}'.format(ren_pro) }</th>
                     
                   </tr>
                  </thead>
                  </table>
                     
                    <%
                         reg_cant=combustible_id.cantidad
                         cant=combustible_id.cantidad
                         primer_rk=combustible_id.name
                    %>
                                     
                  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000"
                  style="border-collapse:collapse;font-size:12px">
                  <thead>
                   <tr>
                     <th width="11%" style="text-align:center;">${ get_mes_nom(m2)}</th>
                   </tr>
                  </thead>
                  </table>
                %endif
         %endif

     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="11%" style="font-size:11px;text-align:center">${ combustible_id.date}</td>
	 <td width="10%" style="font-size:11px;text-align:center">${ combustible_id.cantidad }</td>
	 <td width="12%" style="font-size:11px;text-align:center">${ combustible_id.name }</td>
         <td width="12%" style="font-size:11px;text-align:center">${ '{:,.2f}'.format(ren) }</td>
       </tr>
     </table>
   
     %if ren!=0: 
     <%
         ren = 0
         ren+=combustible_id.name
     %>
     %else:
     <%
         ren+=combustible_id.name
     %>
     %endif

   %endfor
            
       %if reg_cant==0:
       <%
         ren_pro = reg_cant
       %>
       %else:
       <%
          ren_pro = (ultimo_rk - primer_rk) / reg_cant
       %>
       %endif

   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
         <th width="11%" style="text-align:center;">Consumo Mensual</th>
         <th width="10%" style="text-align:center;">${ cant }</th>
         <th width="12%" style="text-align:center;">Rendimiento Promedio</th>
         <th width="12%" style="text-align:center;">${ '{:,.2f}'.format(ren_pro) }</th>
       </tr>
     </thead>
   </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>

    </tr>
    <tr style="height:35px">
      <th></th>

    </tr>
    <tr style="height:35px">
      <th></th>

    </tr>
    <tr style="height:35px">
      
      <th>Elaborado por:</th>
      <th>Responsable:</th>
    </tr>
    <tr style="height:20px">
      <th></th>
    </tr>
    <tr style="height:35px">
      
      <th>__________________________</th>
      <th>__________________________</th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%"></th>
    </tr>  
    <tr style="font-size:11px">
      
      <th width="50%">${user.employee_id.complete_name or ''|entity}</th>
    </tr>  

  </table>
   %endfor
</body>
</html>
