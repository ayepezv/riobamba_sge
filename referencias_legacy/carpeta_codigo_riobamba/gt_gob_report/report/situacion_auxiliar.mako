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
	  <td width="100%" style="font-size:14;text-align:center;">SITUACION FINANCIERA AUXILIAR</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha Desde:</td>
      <td style="font-size:11px" width="42%">${o.date_from or  ''}</td>
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha Hasta:</td>
      <td style="font-size:11px" width="42%">${o.date_end or  ''}</td>
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="65%">CUENTA</th>
        <th style="font-size:11px" width="15%">SALDO ACTUAL</th>
        <th style="font-size:11px" width="15%">SALDO ANTERIO</th>
      </tr>
    </thead>
	<%
	   a=0
	   %>
    %for line in o.line_ids:
	<%
	   a+=1
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="65%" style="font-size:11px;text-align:left">${line.account_id.code_aux} - ${line.account_id.name}</td>
      <td width="15%" style="font-size:11px;text-align:right">${line.actual}</td>
      <td width="15%" style="font-size:11px;text-align:right">${line.anterior}</td>
    </tr>
    %endfor      
  </table>
  %endfor
</html>
