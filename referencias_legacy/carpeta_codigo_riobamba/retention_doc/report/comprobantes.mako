<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:11;text-align:center;">DETALLE DE COMPROBANTES</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:9px" width="5%">Nro.</th>
        <th style="font-size:9px" width="5%">FECHA</th>
        <th style="font-size:9px" width="40%">BENEFICIARIO</th>
        <th style="font-size:9px" width="10%">MONTO</th>
        <th style="font-size:9px" width="40%">CONCEPTO</th>
      </tr>
    </thead>
	<%
	   a=0
	   %>
    %for line in objects:
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:9px;text-align:center">${line.name}</td>
      <td width="5%" style="font-size:9px;text-align:center">${line.date}</td>
      <td width="40%" style="font-size:9px;text-align:left">${line.partner_id.name}</td>
      <td width="10%" style="font-size:9px;text-align:right">${line.monto}</td>
      <td width="40%" style="font-size:9px;text-align:left">${line.narration}</td>
    </tr>
    %endfor      
  </table>
</html>
