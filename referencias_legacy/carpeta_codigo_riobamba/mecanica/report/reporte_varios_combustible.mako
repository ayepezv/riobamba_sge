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
          <FONT size= 3 >Reporte Varios de Combustibles: </FONT>
          <br>
          <i><FONT size= 3 >${ o.variosr_id.name.name }</FONT></i>
          <br>
          <FONT size= 3 >Fechas: ${ o.date_start } - ${ o.date_stop }</FONT>
        </b>
   </center>
   <h5 style="text-align:center;" align="center">VARIAS MAQUINARIAS</h5>
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
         <th width="35%" style="text-align:center;">Responsable</th>
	 <th width="10%" style="text-align:center;">Cantidad</th>
         <th width="10%" style="text-align:center;">Unidad</th>
         <th width="34%" style="text-align:center;">Actividad Asignada/Destino</th>
       </tr>
     </thead>
   </table>


      <% 
        m1 = m2 = 0
        cont = cant = 0
        vari = 0
      %>

   %for combustible_id in get_vehiculo_combustible(o):
         <%
         cant+=combustible_id.cantidad
         numero = get_numero_registros(o)
         
         %> 
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
         
         %if m1==m2:
         <%
           
         %>
             <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-  
              size:12px">
                 <tr>
	             <td width="11%" style="font-size:11px;text-align:center">${ combustible_id.date}</td>
	             <td width="35%" style="font-size:11px;text-align:center">${ combustible_id.responsable_id.complete_name }</td>
	             <td width="10%" style="font-size:11px;text-align:center">${ combustible_id.cantidad }</td>
                     <td width="10%" style="font-size:11px;text-align:center">${ combustible_id.unidad_id.name }</td>
                     <td width="34%" style="font-size:11px;text-align:center">${ combustible_id.tipo_combustible_id.name}</td>
                 </tr>
             </table>
         
         %else:
             
             %if m1>m2:
                 
                 %if vari==1:
                     <%
                       vari2 = get_mes_nom(m1)
                       vari=0
                     %>           
                     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" 
                     style="border-collapse:collapse;font-size:12px">
                     <thead>
                         <tr>
                              <th width="11%" style="text-align:center;">${ vari2}</th>
                         </tr>
                     </thead>
                     </table>      
                 %endif
                 <%
                 vari=vari+1
                 %>
             <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-
                 size:12px">
                 <tr>
	             <td width="11%" style="font-size:11px;text-align:center">${ combustible_id.date}</td>
	             <td width="35%" style="font-size:11px;text-align:center">${ combustible_id.responsable_id.complete_name }</td>
	             <td width="10%" style="font-size:11px;text-align:center">${ combustible_id.cantidad }</td>
                     <td width="10%" style="font-size:11px;text-align:center">${ combustible_id.unidad_id.name }</td>
                     <td width="34%" style="font-size:11px;text-align:center">${ combustible_id.tipo_combustible_id.name}</td>
                 </tr>
             </table>
             %else:
                 <%
                   var2 = get_mes_nom(m2)
                 %>
                 <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" 
                 style="border-collapse:collapse;font-size:12px">
                 <thead>
                 <tr>
                      <th width="11%" style="text-align:center;">${ var2}</th>
                 </tr>
                 </thead>
                 </table>
             <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-
                 size:12px">
                 <tr>
	             <td width="11%" style="font-size:11px;text-align:center">${ combustible_id.date}</td>
	             <td width="35%" style="font-size:11px;text-align:center">${ combustible_id.responsable_id.complete_name }</td>
	             <td width="10%" style="font-size:11px;text-align:center">${ combustible_id.cantidad }</td>
                     <td width="10%" style="font-size:11px;text-align:center">${ combustible_id.unidad_id.name }</td>
                     <td width="34%" style="font-size:11px;text-align:center">${ combustible_id.tipo_combustible_id.name}</td>
                 </tr>
             </table>
             %endif
         %endif
   %endfor

   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
         <th width="46%" style="text-align:center;">TOTAL</th>
         <th width="10%" style="text-align:center;">${ cant }</th>
         <th width="10%" style="text-align:center;">GALONES</th>
         <th width="34%" style="text-align:center;">${ numero } ACTIVIDADES</th>
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
