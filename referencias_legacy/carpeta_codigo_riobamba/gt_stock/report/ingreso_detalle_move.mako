<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h4 style="text-align:center;" align="center">DIRECCION FINANCIERA</h4>
   <h4 style="text-align:center;" align="center">INVENTARIO</h4>
   <h4 style="text-align:center;" align="center">INGRESOS A BODEGA POR CATEGORIA</h4>
   <table class="table_basic table_title">
     <tr>
       <td>Bodega General</td>
       <td>Desde: ${ o.date_start }</td>
       <td>Hasta: ${ o.date_end }</td>
     </tr>
   </table>
    <%
       total_all=0
       %>
   %for line in o.line_ids:
   <table class="table_basic table_title">
     <tr>
       <td>CATEGORIA: ${line.categ_id.code} - ${line.categ_id.name}</td>
     </tr>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
    <thead style="display: table-header-group">
     <tr style="border-collapse:collapse;font-size:10px">
       <th width="8%">Fecha</th>
       <th width="10%">Ingreso</th>
       <th width="50%">Producto</th>
       <th width="8%">Cant.</th>
       <th width="8%">P.Unit.</th>
       <th width="10%">Subtotal</th>
       <th width="8%">IVA</th>
       <th width="10%">Total</th>
     </tr>
    </thead>
    <%
       total=0
       %>
    %for line_line in line.line_ids:
    <%
       total+=line_line.subtotal
       total_all+=line_line.subtotal
       %>
    <tr style="page-break-inside:avoid;font-size:10px">
      <td width="8%" style="font-size:10px;text-align:left">${line_line.move_id.date_done}</td>
      <td width="10%" style="font-size:10px;text-align:left">${line_line.numero}</td>
      <td width="40%" style="font-size:10px;text-align:left">${line_line.product_id.name}</td>
      <td width="8%" style="font-size:10px;text-align:right">${line_line.cantidad}</td>
      <td width="8%" style="font-size:10px;text-align:right">${line_line.move_id2.price_unit}</td>
      <td width="10%" style="font-size:10px;text-align:right">${line_line.move_id2.subtot}</td>
      <td width="8%" style="font-size:10px;text-align:right">${line_line.move_id2.imp_iva}</td>
      <td width="10%" style="font-size:10px;text-align:right">${line_line.subtotal}</td>
    </tr>
    %endfor   
    <tr style="page-break-inside:avoid">
      <td width="8%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="10%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="40%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="8%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="8%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="10%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="8%" style="font-size:10px;text-align:right"><b>TOTAL CATEGORIA</b></td>
      <td width="10%" style="font-size:10px;text-align:right"><b>${total}</b></td>
    </tr>
   </table>
   %endfor
    <tr style="page-break-inside:avoid">
    <tr style="page-break-inside:avoid">
      <td width="8%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="10%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="40%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="8%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="8%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="10%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="8%" style="font-size:10px;text-align:right"><b>TOTAL</b></td>
      <td width="10%" style="font-size:10px;text-align:right"><b>${total_all}</b></td>
    </tr>
    </tr>
   %endfor
</table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:12px">
      <th>__________________</th>
    </tr>
    <tr style="font-size:12px">
      <th width="33%">Jefe Inventario</th>
    </tr>  
  </table>
</body>
</html>
