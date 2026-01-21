<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h4 style="text-align:center;" align="center">DIRECCION FINANCIERA</h4>
   <h6 style="text-align:center;" align="center">INVENTARIO : INGRESOS DE BODEGA</h6>
   <table class="table_basic table_title">
     <tr>
       <td>Bodega: ${ o.bodega_id.name }</td>
       <td>Desde: ${ o.date_start }</td>
       <td>Hasta: ${ o.date_end }</td>
     </tr>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
     <tr>
       <th width="20%">Proveedor</th>
       <th width="10%">Codigo</th>
       <th width="45%">Producto</th>
       <th width="15%">UdM</th>
       <th width="10%">Num. Doc. Ingreso</th>
       <th width="10%">Fecha Ingreso</th>
       <th width="10%">Cantidad</th>
       <th width="10%">Precio Unitario</th>
       <th width="10%">Subtotal</th>
       <th width="10%">Impuestos</th>
       <th width="10%">Total</th>
     </tr>
    </thead>
    <%
       a=0
       %>
    %for line in o.line_ids:
    <%
       a+=line.move_id.total
       %>
    <tr style="page-break-inside:avoid">
      <td width="10%" style="font-size:11px;text-align:center">${line.picking_id.partner_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:center">${line.move_id.product_id.default_code}</td>
      <td width="45%" style="font-size:11px;text-align:left">${line.move_id.product_id.name}</td>
      <td width="15%" style="font-size:11px;text-align:left">${line.move_id.product_uom.name}</td>
      <td width="15%" style="font-size:11px;text-align:left">${line.picking_id.name}</td>
      <td width="15%" style="font-size:11px;text-align:left">${line.picking_id.date}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.move_id.product_qty}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.move_id.price_unit}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.move_id.subtot}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.move_id.amount_tax}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.move_id.total}</td>
    </tr>
    %endfor   
    <tr style="page-break-inside:avoid">
      <td width="10%" style="font-size:11px;text-align:center">''</td>
      <td width="10%" style="font-size:11px;text-align:center">''</td>
      <td width="45%" style="font-size:11px;text-align:left">''</td>
      <td width="15%" style="font-size:11px;text-align:left">''</td>
      <td width="15%" style="font-size:11px;text-align:left">''</td>
      <td width="15%" style="font-size:11px;text-align:left">''</td>
      <td width="10%" style="font-size:11px;text-align:right">''</td>
      <td width="10%" style="font-size:11px;text-align:right">''</td>
      <td width="10%" style="font-size:11px;text-align:right">''</td>
      <td width="10%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${a}</b></td>
    </tr>
   </table>
   %endfor
</table>
</body>
</html>
