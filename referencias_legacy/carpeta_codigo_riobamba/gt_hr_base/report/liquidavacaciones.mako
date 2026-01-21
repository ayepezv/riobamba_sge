<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  <% import time %>
  %for o in objects:
  <table WIDTH="100%">
	<tr>
	  <td width="100%" style="font-size:14;text-align:center;">SALDO PARA LIQUIDACION DE VACACIONES</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha Corte:</td>
      <td style="font-size:11px" width="42%">${time.strftime('%Y-%m-%d') or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Funcionario:</td>
      <td style="font-size:11px" width="42%">${o.complete_name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Departamento:</td>
      <td style="font-size:11px" width="42%">${o.department_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Cargo:</td>
      <td style="font-size:11px" width="42%">${o.job_id.name or ''}</td>
    </tr> 
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="10%">Nro.</th>
        <th style="font-size:11px" width="60%">PERIODO</th>
        <th style="font-size:11px" width="10%">DIAS VACACIONES</th>
        <th style="font-size:11px" width="10%">TOMADOS</th>
        <th style="font-size:11px" width="10%">SALDO</th>
      </tr>
    </thead>
	<%
	   a=aux_saldot=0
	   %>
    %for line in o.holidays_ids:
	<%
	   a+=1
	   aux_saldo = line.days_normal - line.tomados_normal
	   aux_saldot += aux_saldo
	   %>
    <tr style="page-break-inside:avoid">
      <td width="10%" style="font-size:11px;text-align:center">${a}</td>
      <td width="60%" style="font-size:11px;text-align:left">${line.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.days_normal}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.tomados_normal}</td>
      <td width="10%" style="font-size:11px;text-align:right">${aux_saldo}</td>
    </tr>
    %endfor
    <tr style="page-break-inside:avoid">
      <td width="10%" style="font-size:11px;text-align:center"></td>
      <td width="60%" style="font-size:11px;text-align:left"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right">TOTAL DISPONIBLE</td>
      <td width="10%" style="font-size:11px;text-align:right">${aux_saldot}</td>
    </tr>
  </table>
  %endfor
</html>
