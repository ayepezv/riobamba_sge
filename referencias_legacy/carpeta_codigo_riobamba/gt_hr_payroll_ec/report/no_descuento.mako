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
      <td width="100%" style="font-size:14;text-align:center;">NO DESCONTADOS EN ROL</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
    %if o.no_ids:
    <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="42%" style="text-align:center;">Funcionario</th>
	 <th width="42%" style="text-align:center;">Rubro</th>
	 <th width="5%" style="text-align:center;">Inicial</th>
	 <th width="5%" style="text-align:center;">Descontado</th>
	 <th width="5%" style="text-align:center;">Saldo</th>
       </tr>
     </thead>
      %for line_line in o.no_ids:
      <tr >
	<td width="42%" style="font-size:9px;text-align:left">${line_line.employee_id.complete_name}</td>
	<td width="42%" style="font-size:9px;text-align:left">${line_line.name}</td>
	<td width="5%" style="font-size:9px;text-align:left">${line_line.inicial}</td>
	<td width="5%" style="font-size:9px;text-align:left">${line_line.descontado}</td>
	<td width="5%" style="font-size:9px;text-align:left">${line_line.saldo}</td>
      </tr>
      %endfor
    </table>
    %endif
  </table>
  %endfor
</html>
