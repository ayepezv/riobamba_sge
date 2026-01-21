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
      <td width="100%" style="font-size:14;text-align:center;">DISTRIBUTIVO</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="15%">Partida General</th>
        <th style="font-size:11px" width="25%">Partida Individual</th>
        <th style="font-size:11px" width="10%">Funcionario</th>
        <th style="font-size:11px" width="10%">Cargo</th>
        <th style="font-size:11px" width="10%">Sueldo</th>
      </tr>
    </thead>
    %for line_programa in o.line_ids:
    <p>PROGRAMA : ${line_programa.program_id.sequence} - ${line_programa.program_id.name}</p>	  	  
    %for line_departamento in line_programa.line_ids:
    <p>DEPARTAMENTO : ${line_departamento.department_id.name}</p>
    %for line_contract in line_departamento.line_ids:
    <p>CCCC</p>
    %endfor
    %endfor
    %endfor      
  </table>
  %endfor
</html>
