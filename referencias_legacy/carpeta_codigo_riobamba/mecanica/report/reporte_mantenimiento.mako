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
          <FONT size= 3 >Reporte de Mantenimiento: ${ o.opcion }</FONT>
          <br>
          <i><FONT size= 3 >${ o.vehiculor_id.name.name }</FONT></i>
          <br>
          <FONT size= 3 >Fechas: ${ o.date_start } - ${ o.date_stop }</FONT>
        </b>
   </center>
   <h5 style="text-align:center;" align="center">LUBRICANTES</h5>
   <%
      
      %>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
         <th width="11%" style="text-align:center;">Fecha</th>
	 <th width="20%" style="text-align:center;">Lubricante</th>
	 <th width="10%" style="text-align:center;">Cantidad</th>
         <th width="11%" style="text-align:center;">Unidad</th>
         <th width="11%" style="text-align:center;">Kilometraje</th>
	 <th width="11%" style="text-align:center;">Pr&oacute;ximo Cambio</th>
   <th width="10%" style="text-align:center;">Reque. - C. Chica</th>
	 <th width="20%" style="text-align:center;">Observaciones</th>
       </tr>
     </thead>
   </table>
   <% 
      
      %>
   %for lubricant_id in get_vehiculo_lubricante(o):

     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="11%" style="font-size:11px;text-align:center">${ lubricant_id.fecha}</td>
         <td width="20%" style="font-size:11px;text-align:center">${ lubricant_id.descripcion_lubricante}</td>
	 <td width="10%" style="font-size:11px;text-align:center">${ lubricant_id.cantidad }</td>
	 <td width="11%" style="font-size:11px;text-align:center">${ lubricant_id.unidad_id.name }</td>
	 <td width="11%" style="font-size:11px;text-align:center">${ lubricant_id.name }</td>
         <td width="11%" style="font-size:11px;text-align:center">${ lubricant_id.proximo_cambio_kilometraje }</td>
         <td width="10%" style="font-size:11px;text-align:center">${ lubricant_id.requerimiento_quitar_lubri }</td>
         <td width="20%" style="font-size:11px;text-align:center">${ lubricant_id.tipo_cambio_id.name }</td>
       </tr>
     </table>
     %endfor
   <br><br>
   <h5 style="text-align:center;" align="center">REPUESTOS, REPARACION Y MANTENIMIENTOS</h5>

   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
         <th width="11%" style="text-align:center;">Fecha</th>
	 <th width="27%" style="text-align:center;">Descripción del Repuesto</th>
	 <th width="10%" style="text-align:center;">Cantidad</th>
         <th width="11%" style="text-align:center;">Unidad</th>
         <th width="12%" style="text-align:center;">Kilometraje</th>
	 <th width="10%" style="text-align:center;">Reque. - C. Chica</th>
	 <th width="20%" style="text-align:center;">Observaciones</th>
       </tr>
     </thead>
   </table>  
    %for mante_id in get_vehiculo_mantenimiento(o):

     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="11%" style="font-size:11px;text-align:center">${ mante_id.date}</td>
         <td width="27%" style="font-size:11px;text-align:center">${ mante_id.name}</td>
	 <td width="10%" style="font-size:11px;text-align:center">${ mante_id.cantidad }</td>
	 <td width="11%" style="font-size:11px;text-align:center">${ mante_id.unidad_id.name }</td>
	 <td width="12%" style="font-size:11px;text-align:center">${ mante_id.kilometraje }</td>
         <td width="10%" style="font-size:11px;text-align:center">${ mante_id.requerimiento_cajachica }</td>
         <td width="20%" style="font-size:11px;text-align:center">${ mante_id.observaciones }</td>
       </tr>
     </table>
     %endfor
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
      
    </tr>
    <tr style="height:20px">
      <th></th>
    </tr>
    <tr style="height:35px">
      
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
