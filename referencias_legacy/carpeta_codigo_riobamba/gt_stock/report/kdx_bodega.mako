<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <table WIDTH="100%">
     <tr WIDTH="100%"><td style="text-align:center;font-size:12px" align="center"><b>DIRECCION FINANCIERA</b></td></tr>
     <tr WIDTH="100%"><td style="text-align:center;font-size:12px" align="center"><b>INVENTARIO</b></td></tr>
     <tr WIDTH="100%"><td style="text-align:center;font-size:12px" align="center"><b>KARDEX DE PRODUCTO</b></td></tr>
   </table>
   <table>
     <tr>
       <td style="border-collapse:collapse;font-size:10px">Bodega: ${ o.bodega_id.name or '' }</td>
     </tr>
     <tr>
       <td style="border-collapse:collapse;font-size:10px">Producto: ${ o.product_id.default_code or '' } - ${ o.product_id.name or '' } Unidad Medida:${ o.product_id.uom_id.name or '' }</td>
     </tr>
     <tr>
       <td style="border-collapse:collapse;font-size:10px">Desde: ${ o.date_start }</td>
     </tr>
     <tr>
       <td style="border-collapse:collapse;font-size:10px">Hasta: ${ o.date_end }</td>
     </tr>
     <tr>
       <td style="border-collapse:collapse;font-size:10px">Saldo Inicial: ${ o.qty_inicial }</td>
     </tr>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group"> 
     <tr>
       <th width="44%">Documento</th>
       <th width="8%">Fecha</th>
       <th width="8%">Cantidad</th>
       <th width="8%">Precio</th>
       <th width="8%">Total</th>
       <th width="8%"><b>STOCK</b></th>
       <th width="8%">Prec.Unitario Existencia</th>
       <th width="8%"><b>TOTAL EXISTENCIA</b></th>
     </tr>
    </thead>
    %for line in o.line_ids:
    	<%
	   usd=0
	   %>
    	<%
	   usd=line.saldo * o.product_id.standard_price
	   %>
    <tr style="page-break-inside:avoid;font-size:9px">
      <td width="44%" style="font-size:9px;text-align:left">${line.documento} - ${line.tipo}</td>
      <td width="8%" style="font-size:9px;text-align:left">${formatLang(line.date,date=True)}</td>
      <td width="8%" style="font-size:9px;text-align:right">${line.qty}</td>
      <td width="8%" style="font-size:9px;text-align:right">${line.cu}</td>
      <td width="8%" style="font-size:9px;text-align:right">${line.tot_cu}</td>
      <td width="8%" style="font-size:9px;text-align:right">${line.saldo}</td>
      <td width="8%" style="font-size:9px;text-align:right">${'{:,.2f}'.format(o.product_id.standard_price)}</td>
      <td width="8%" style="font-size:9px;text-align:right">${usd}</td>
    </tr>
    %endfor
   </table>
   <table width="100%" style="page-break-inside:avoid">
     <tr style="page-break-inside:avoid">
       <td width="92%" style="font-size:11px;text-align:right"><b>TOTAL INGRESOS CANTIDAD</b></td>
       <td width="8%" style="font-size:11px;text-align:right"><b>${o.total_in}</b></td>
     </tr>
     <tr style="page-break-inside:avoid">
       <td width="92%" style="font-size:11px;text-align:right"><b>TOTAL EGRESOS CANTIDAD</b></td>
       <td width="8%" style="font-size:11px;text-align:right"><b>${o.total_out}</b></td>
     </tr>
     <tr style="page-break-inside:avoid">
       <td width="92%" style="font-size:11px;text-align:right"><b>TOTAL INGRESOS DINERO</b></td>
       <td width="8%" style="font-size:11px;text-align:right"><b>${o.total_in_usd}</b></td>
     </tr>
     <tr style="page-break-inside:avoid">
       <td width="92%" style="font-size:11px;text-align:right"><b>TOTAL EGRESOS DINERO</b></td>
       <td width="8%" style="font-size:11px;text-align:right"><b>${o.total_out_usd}</b></td>
     </tr>
   </table>
   %endfor
</table>
</body>
</html>
