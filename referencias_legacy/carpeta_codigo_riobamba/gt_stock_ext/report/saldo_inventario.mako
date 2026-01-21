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
	  <td width="100%" style="font-size:14;text-align:center;">SALDO DE INVENTARIO ${o.date or  ''}</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="30%">CODIGO</th>
        <th style="font-size:11px" width="50%">DESCRIPCION</th>
        <th style="font-size:11px" width="20%">VALOR</th>
      </tr>
    </thead>
    <%
	   total=0
	   %>
    %for line in o.linec_ids:
	<%
	   total+=line.total
	   %>
    <tr style="page-break-inside:avoid">
      <td width="30%" style="font-size:11px;text-align:left">${line.category_id.code}</td>
      <td width="50%" style="font-size:11px;text-align:left">${line.category_id.name}</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(line.total) }</td>
    </tr>
    %endfor      
    <tr style="page-break-inside:avoid">
      <td width="30%" style="font-size:11px;text-align:left"></td>
      <td width="50%" style="font-size:11px;text-align:left">TOTAL EXISTENCIAS CONSUMO</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(total) }</td>
    </tr>
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="30%">CODIGO</th>
        <th style="font-size:11px" width="50%">DESCRIPCION</th>
        <th style="font-size:11px" width="20%">VALOR</th>
      </tr>
    </thead>
    <%
	   total_i=0
	   %>
    %for linei in o.linei_ids:
	<%
	   total_i+=linei.total
	   %>
    <tr style="page-break-inside:avoid">
      <td width="30%" style="font-size:11px;text-align:left">${linei.category_id.code}</td>
      <td width="50%" style="font-size:11px;text-align:left">${linei.category_id.name}</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(linei.total) }</td>
    </tr>
    %endfor
    <tr style="page-break-inside:avoid">
      <td width="30%" style="font-size:11px;text-align:left"></td>
      <td width="50%" style="font-size:11px;text-align:left">TOTAL EXISTENCIAS INVERSION</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(total_i) }</td>
    </tr>      
  </table>
	<%
	   total_all=total_i + total
	   %>
  <tr style="page-break-inside:avoid">
    <td width="30%" style="font-size:11px;text-align:left"></td>
    <td width="50%" style="font-size:11px;text-align:left">TOTAL EXISTENCIAS</td>
    <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(total_all) }</td>
  </tr>      
  %endfor
</html>
