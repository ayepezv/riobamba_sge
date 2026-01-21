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
      <h2 width="100%" style="font-size:14;text-align:center;">DISTRIBUTIVO</h2>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="15%">Partida General</th>
        <th style="font-size:11px" width="20%">Partida Individual</th>
        <th style="font-size:11px" width="25%">Funcionario</th>
        <th style="font-size:11px" width="35%">Cargo</th>
        <th style="font-size:11px" width="5%">Sueldo</th>
      </tr>
    </thead>
    %for line_programa in o.line_ids:
    <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
      <p><b>PROGRAMA : ${line_programa.program_id.sequence} - ${line_programa.program_id.name}</b></p>	  	  
      %for line_departamento in line_programa.line_ids:
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
      <p><b>DEPARTAMENTO : ${line_departamento.department_id.name}</b></p>
      %for line_contract in line_departamento.line_ids:
      <tr>
        <td style="font-size:11px" width="15%">${line_contract.contract_id.budget_id.code}</th>
        <td style="font-size:11px" width="20%">${line_contract.contract_id.budget_ind}</th>
        <td style="font-size:11px" width="25%">${line_contract.contract_id.employee_id.complete_name}</th>
        <td style="font-size:11px" width="35%">${line_contract.contract_id.employee_id.job_id.name}</th>
        <td style="font-size:11px;text-align:right" width="5%">${line_contract.contract_id.wage}</th>
      </tr>
      %endfor
</table>
      %endfor      
</table>
%endfor     
</table>
%endfor     
</html>
