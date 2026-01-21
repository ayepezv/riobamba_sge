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
      <td width="100%" style="font-size:14;text-align:center;">RESUMEN RUBRO PROGRAMA</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
      <tr>
        <th style="font-size:11px" width="35%">PROGRAMA</th>
        <th style="font-size:11px" width="22%">RUBRO</th>
        <th style="font-size:11px" width="36%">PARTIDA</th>
        <th style="font-size:11px" width="8%">VALOR</th>
      </tr>
    </thead>
    %for line in o.detalle_ids:
    <tr>
      <td width="35%" style="font-size:11px;text-align:left">${line.programa_id.sequence} - ${line.programa_id.name}</td>
      <td width="22%" style="font-size:11px;text-align:left">${line.rubro_id.name}</td>
      <td width="36%" style="font-size:11px;text-align:left">${line.partida_id.code} - ${line.partida_id.name}</td>
      <td width="8%" style="font-size:11px;text-align:right">${line.monto}</td>
    </tr>
    %endfor      
  </table>
  %endfor
</html>
