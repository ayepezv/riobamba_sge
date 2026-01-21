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
      <td width="100%" style="font-size:14;text-align:center;">REPORTE DE ROLES DETALLE</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Periodo:</td>
      <td style="font-size:11px" width="42%">${o.period_id.name or  ''}</td>
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="40%">EMPLEADO</th>
        <th style="font-size:11px" width="15%">CARGO</th>
        <th style="font-size:11px" width="10%">RMU</th>
        <th style="font-size:11px" width="10%">INGRESOS</th>
        <th style="font-size:11px" width="10%">EGRESOS</th>
        <th style="font-size:11px" width="10%">TOTAL</th>
      </tr>
    </thead>
	<%
	   a=0
	   t_i = t_e = t_t = t_r = 0
	   %>
    %for line in o.line2_ids:
	<%
	   a+=1
	   t_i += line.ingresos
	   t_e += line.egresos
	   t_t += line.total
	   t_r += line.rmu
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="40%" style="font-size:11px;text-align:left">${line.contract_id.employee_id.complete_name}</td>
      <td width="15%" style="font-size:11px;text-align:right">${line.contract_id.employee_id.job_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.rmu}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.ingresos}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.egresos}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.total}</td>
    </tr>
    %endfor      
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center"></td>
      <td width="40%" style="font-size:11px;text-align:left"></td>
      <td width="15%" style="font-size:11px;text-align:right">TOTALES</td>
      <td width="10%" style="font-size:11px;text-align:right">${t_r}</td>
      <td width="10%" style="font-size:11px;text-align:right">${t_i}</td>
      <td width="10%" style="font-size:11px;text-align:right">${t_e}</td>
      <td width="10%" style="font-size:11px;text-align:right">${t_t}</td>
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="font-size:11px">
      <th width="33%">Elaborado por</th>
 	</tr>  
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="height:35px">
      <th>__________________</th>
	</tr>
	<tr style="font-size:11px">
	  <th width="33%">${user.employee_id.complete_name or ''}</th>
	</tr>  
  </table>
  %endfor
</html>
