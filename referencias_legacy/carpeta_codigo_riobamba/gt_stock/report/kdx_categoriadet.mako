<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">SALDO DE INVENTARIO: Desde ${o.date_start or  ''} - Hasta ${o.date_end or  ''}</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">CORRIENTE</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr style="page-break-inside:avoid">
        <th style="font-size:11px" width="65%">PRODUCTO</th>
        <th style="font-size:11px" width="10%">CANTIDAD</th>
        <th style="font-size:11px" width="10%">PRECIO</th>
        <th style="font-size:11px" width="15%">TOTAL</th>
      </tr>
    </thead>
    <%
       total_all=0
       %>
    %for line in o.line_ids:
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">${line.categ_id.code} - ${line.categ_id.name}</td>	  	  
    </tr>	
    <%
       total_categ=0
       %>
    %for line_line in line.line_ids:
    <%
       aux_total = 0
       aux_total = line_line.name.standard_price * line_line.cantidad
       total_categ=line.saldo
       %>
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:left">${line_line.name.default_code} - ${line_line.name.name}</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(line_line.cantidad) }</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(line_line.precio) }</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(line_line.total) }</td>
    </tr>
    %endfor      
    <%
       total_all+=total_categ
       %>
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:left"></td>
      <td width="20%" style="font-size:11px;text-align:right"></td>
      <td width="20%" style="font-size:11px;text-align:right">TOTAL CATEGORIA</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(total_categ) }</td>
    </tr>
    %endfor
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:left"></td>
      <td width="20%" style="font-size:11px;text-align:right"></td>
      <td width="20%" style="font-size:11px;text-align:right">TOTAL CORRIENTE</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(total_all) }</td>
    </tr>
  </table>
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">INVERSION</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr style="page-break-inside:avoid">
        <th style="font-size:11px" width="80%">PRODUCTO</th>
        <th style="font-size:11px" width="20%">CANTIDAD</th>
	<th style="font-size:11px" width="10%">PRECIO</th>
        <th style="font-size:11px" width="15%">TOTAL</th>
      </tr>
    </thead>
    <%
       total_all=0
       %>
    %for linei in o.line_ids2:
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">${linei.categ_id.code} - ${linei.categ_id.name}</td>	  	  
    </tr>
    <%
       total_categ=0
       %>
    %for line_line in linei.line_ids:
    <%
       aux_total = 0
       aux_total = line_line.name.standard_price * line_line.cantidad
       total_categ=linei.saldo
       %>
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:left">${line_line.name.default_code} - ${line_line.name.name}</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(line_line.cantidad) }</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(line_line.precio) }</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(line_line.total) }</td>
    </tr>
    %endfor
    <%
       total_all+=total_categ
       %>
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:left"></td>
      <td width="20%" style="font-size:11px;text-align:right"></td>
      <td width="20%" style="font-size:11px;text-align:right">TOTAL CATEGORIA</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(total_categ) }</td>
    </tr>
    %endfor
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:left"></td>
      <td width="20%" style="font-size:11px;text-align:right"></td>
      <td width="20%" style="font-size:11px;text-align:right">TOTAL INVERSION</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(total_all) }</td>
    </tr>
  </table>
  %endfor
</html>
