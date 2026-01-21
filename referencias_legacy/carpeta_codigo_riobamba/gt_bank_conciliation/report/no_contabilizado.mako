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
	  <td width="100%" style="font-size:14;text-align:center;">DETALLE NO CONTABILIZADO ${o.period_id.name or  ''}</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="5%">FECHA</th>
        <th style="font-size:11px" width="5%">TIPO</th>
        <th style="font-size:11px" width="55%">DETALLE</th>
        <th style="font-size:11px" width="20%">REFERENCIA</th>
        <th style="font-size:11px" width="10%">MONTO</th>
      </tr>
    </thead>
	<%
	   a=0
	   %>
    %for line in o.no_ids:
	<%
	   a+=1
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="5%" style="font-size:11px;text-align:center">${line.date}</td>
      <td width="5%" style="font-size:11px;text-align:center">${line.tipo}</td>
      <td width="55%" style="font-size:11px;text-align:left">${line.descripcion}</td>
      <td width="20%" style="font-size:11px;text-align:right">${line.ref}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.monto}</td>
    </tr>
    %endfor      
  </table>
  %endfor
</html>
