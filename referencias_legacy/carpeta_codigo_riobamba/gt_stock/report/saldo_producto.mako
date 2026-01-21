<html>
<head>
    <style type="text/css">
    ${css}
    td {
    padding:2px 4px 2px 4px;
    font-size:10px;
    }
    table th {
	padding:2px 4px 2px 4px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
    font-size:10px;
    }
    .project {
	padding:3px 12px 9px 12px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ababab), to(#ababab));
	background: -moz-linear-gradient(top,  #ededed,  #ababab);
    font-size:12px;
    }
    table_basic {
    width: 100%;
    }
    table_title {
	border-top:1px solid #ffffff;
    }
    hr {
    border: 0;
    border-bottom: 1px solid #FFFFFF;
    border-top: 1px solid #AAAAAA;
    clear: both;
    height: 0;
    margin: 12px 0 18px;
    }
    </style>
</head>
 <body>
   %for o in objects:
   <h1 style="text-align:center;" align="center">DIRECCION FINANCIERA</h1>
   <h3 style="text-align:center;" align="center">INVENTARIO</h3>
   <h4 style="text-align:center;" align="center">SALDOS</h4>
   <table class="table_basic table_title">
     <tr>
       <td>Bodega: ${ o.bodega_id.name }</td>
     </tr>
   </table>
   <%
      total=0
      %>
   %for categoria in o.line_ids:
   %if categoria.line_ids:
   <tr>
     <td><b>Categoria: ${ categoria.categ_id.code } - ${ categoria.categ_id.name }</b></td>
   </tr>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
     <tr style="page-break-inside:avoid;font-size:12px">
       <th width="10%">Codigo</th>
       <th width="45%">Producto</th>
       <th width="15%">UdM</th>
       <th width="10%">Cantidad/Saldo</th>
       <th width="10%">Precio</th>
       <th width="10%">Valor</th>
     </tr>
    </thead>
    <%
       a=0
       %>
    %for line in categoria.line_ids:
    <%
       a+=line.total
       total+=line.total
       %>
    %if line.qty>0:
    <tr style="page-break-inside:avoid;font-size:12px">
      <td width="10%" style="font-size:11px;text-align:center">${line.product_id.default_code}</td>
      <td width="45%" style="font-size:11px;text-align:left">${line.product_id.name}</td>
      <td width="15%" style="font-size:11px;text-align:left">${line.udm_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.qty}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.valor}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.total}</td>
    </tr>
    %endif
    %endfor   
    <tr style="page-break-inside:avoid;font-size:12px">
      <td width="10%" style="font-size:11px;text-align:center"></td>
      <td width="45%" style="font-size:11px;text-align:left"></td>
      <td width="15%" style="font-size:11px;text-align:left"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>TOTAL CATEGORIA</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${a}</b></td>
    </tr>
   </table>
   %endif
   %endfor
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <tr style="page-break-inside:avoid;font-size:12px">
       <td width="10%" style="font-size:11px;text-align:center"></td>
       <td width="45%" style="font-size:11px;text-align:left"></td>
       <td width="15%" style="font-size:11px;text-align:left"></td>
       <td width="10%" style="font-size:11px;text-align:right"></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>${total}</b></td>
     </tr>
   </table>
   %endfor
</table>
</body>
</html>
