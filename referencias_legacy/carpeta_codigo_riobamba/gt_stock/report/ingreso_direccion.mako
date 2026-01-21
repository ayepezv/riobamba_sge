<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   <%
      total_all=0
      %>
   %for o in objects:
   <h2 style="text-align:center;" align="center">DIRECCION FINANCIERA</h2>
   <h2 style="text-align:center;" align="center">INVENTARIO</h2>
   <h2 style="text-align:center;" align="center">INGRESOS A BODEGA POR DIRECCION Y CATEGORIA</h2>
   <table class="table_basic table_title">
     <tr>
       <td>Bodega General</td>
       <td>Desde: ${ o.date_start }</td>
       <td>Hasta: ${ o.date_end }</td>
     </tr>
   </table>
   <%
      total_direccion=0
      %>
   %for line in o.line_ids:
   <%
      total_direccion+=line.total
       %>
   <!--h3 style="text-align:center;" align="center">DIRECCION: ${line.direccion_id.name}</h3-->
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead style="display: table-header-group">
       <tr>
	 <th width="60%" style="text-align:left;" > ${line.direccion_id.name}</th>
	 <th width="10%"></th>
	 <th width="10%"></th>
       </tr>
       <tr>
	 <th width="60%" style="text-align:left;">Categoria</th>
	 <th width="10%">Cantidad</th>
	 <th width="10%">Subtotal</th>
       </tr>
     </thead>
     <%
	total=0
	%>
     %for line_line in line.line_ids:
     <%
	total+=line_line.subtotal
	%>
     <tr style="page-break-inside:avoid">
       <td width="80%" style="font-size:11px;text-align:left">${line_line.categ_id.name}</td>
       <td width="10%" style="font-size:11px;text-align:right">${line_line.cantidad}</td>
       <td width="10%" style="font-size:11px;text-align:right">${line_line.subtotal}</td>
     </tr>
     %endfor   
     <tr style="page-break-inside:avoid">
       <td width="80%" style="font-size:11px;text-align:right"><b>${}</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>${total}</b></td>
     </tr>
     %endfor
   </table>
   %endfor
   <tr style="page-break-inside:avoid">
       <td width="80%" style="font-size:11px;text-align:right"><b>${}</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>TOTAL DIRECCIONES</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>${total_direccion}</b></td>
     </tr>
</table>
<table style="page-break-inside:avoid" width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
    <th>__________________</th>
  </tr>
  <tr style="font-size:22px">
    <th width="33%">Jefe Inventario</th>
  </tr>  
  <tr style="height:35px">
  </tr>
</table>
</body>
</html>
