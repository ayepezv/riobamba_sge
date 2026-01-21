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
      <td width="100%" style="font-size:14;text-align:center;">EJECUCION DE INGRESOS</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" > 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">PARTIDA : </td>
      <td style="font-size:11px" width="42%">${o.item_id.code or  ''} - ${o.item_id.name or  ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Desde : ${o.date_start or  ''}</td>
      <td style="font-weight: bold;font-size:11px" width="12%">Hasta : ${o.date_end or  ''}</td>
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="8%">FECHA</th>
        <th style="font-size:11px" width="8%">NUM.COMPROBANTE</th>
        <th style="font-size:11px" width="55%">DETALLE</th>
        <th style="font-size:11px" width="8%">ACTUAL</th>
        <th style="font-size:11px" width="8%">ANTERIOR</th>
	<th style="font-size:11px" width="8%">TOTAL</th>
      </tr>
    </thead>
	<%
	   totalant=totalact=total=a=0
	   %>
    %for line in o.line_ids:
	<%
	   a+=1
	   totalant += line.anterior
	   totalact += line.actual
	   
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="8%" style="font-size:11px;text-align:center">${line.date}</td>
      <td width="8%" style="font-size:11px;text-align:center">${line.move_id}</td>
      <td width="55%" style="font-size:11px;text-align:left">${line.desc}</td>
      <td width="8%" style="font-size:11px;text-align:right">${line.actual}</td>
      <td width="8%" style="font-size:11px;text-align:right">${line.anterior}</td>
      <td width="8%" style="font-size:11px;text-align:right">${line.total}</td>
    </tr>
    %endfor      
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <%
	 total = totalant + totalact
	 %>
      <tr>
        <th style="font-size:11px" width="5%"></th>
        <th style="font-size:11px" width="71%">TOTAL</th>
        <th style="font-size:11px" width="8%">${totalact}</th>
        <th style="font-size:11px" width="8%">${totalant}</th>
        <th style="font-size:11px" width="8%">${total}</th>
      </tr>
    </thead>
  </table>
  %endfor
</html>
