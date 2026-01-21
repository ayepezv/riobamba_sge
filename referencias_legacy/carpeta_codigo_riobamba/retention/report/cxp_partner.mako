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
	  <td width="100%" style="font-size:14;text-align:center;">CUENTAS POR PAGAR</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="80%">BENEFICIARIO</th>
        <th style="font-size:11px" width="15%">MONTO</th>
      </tr>
    </thead>
	<%
	   a=0
	   total=0
	   %>
    %for line in o.line_ids:
	<%
	   a+=1
	   total+=line.monto
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="80%" style="font-size:11px;text-align:right">${line.partner_id.ced_ruc} - ${line.partner_id.name}</td>
      <td width="15%" style="font-size:11px;text-align:right">${line.monto}</td>
    </tr>
    %endfor      
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center"></td>
      <td width="80%" style="font-size:11px;text-align:left">TOTAL</td>
      <td width="15%" style="font-size:11px;text-align:right">${total}</td>
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%">Contador(a)</th>
    </tr>  
    <tr style="height:35px">
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th>__________________</th>
    </tr>
  </table>
  %endfor
</html>
