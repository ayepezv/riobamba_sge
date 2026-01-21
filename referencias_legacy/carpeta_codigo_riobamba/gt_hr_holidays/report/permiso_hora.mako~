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
      <td width="100%" style="font-size:14;text-align:center;">SOLICITUD DE PERMISO Nro. ${o.code or  ''}</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Funcionario Solicita:</td>
      <td style="font-size:11px" width="42%">${o.employee_id.complete_name or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Departamento:</td>
      <td style="font-size:11px" width="42%">${o.employee_id.department_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha Desde:</td>
      <td style="font-size:11px" width="42%">${o.date_from or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha Hasta:</td>
      <td style="font-size:11px" width="42%">${o.date_to or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Tipo:</td>
      <td style="font-size:11px" width="42%">${o.holiday_status_id.name or ''}</td>
    </tr> 
  </table>
  <p></p>
  <table style="page-break-inside:avoid" width="100%">
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="height:35px">
	  <th>__________________</th>
	  <th>__________________</th>
	  <th>__________________</th>
	</tr>
	<tr style="font-size:11px">
	  <th width="33%">Jefe Inmediato</th>
	  <th width="33%">Talento Humano</th>
	  <th width="33%">Maxima Autoridad</th>
 	</tr>  
  </table>
  %endfor
</html>
