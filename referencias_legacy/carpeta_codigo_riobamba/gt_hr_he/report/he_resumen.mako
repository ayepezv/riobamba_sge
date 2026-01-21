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
	  <td width="100%" style="font-size:14;text-align:center;">RESUMEN DE HORAS EXTRAS ${o.period_id.name or  ''}</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
      <tr>
        <th style="font-size:11px" width="50%">EMPLEADO</th>
        <th style="font-size:11px" width="10%">USD 25%</th>
        <th style="font-size:11px" width="10%">USD 50%</th>
        <th style="font-size:11px" width="10%">USD 60%</th>
        <th style="font-size:11px" width="10%">USD 100%</th>
        <th style="font-size:11px" width="10%">TOTAL USD</th
      </tr>
    </thead>
    %for line in o.line_ids:
    <tr>
      <td width="50%" style="font-size:11px;text-align:center">${line.contract_id.employee_id.complete_name or ''}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.total_25}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.total_50}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.total_60}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.total_100}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.total}</td>
    </tr>
    %endfor      
  </table>
  <table width="100%">
	<tr style="height:35px">
      <th></th>
      <th></th>
   	</tr>
	<tr style="height:35px">
      <th></th>
      <th></th>
   	</tr>
	<tr style="font-size:11px">
      <th width="33%">Talento Humano</th>
      <th width="33%">Funcionario</th>
	</tr>  
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="height:35px">
      <th>__________________</th>
      <th>__________________</th>
	</tr>
  </table>
  %endfor
</html>
