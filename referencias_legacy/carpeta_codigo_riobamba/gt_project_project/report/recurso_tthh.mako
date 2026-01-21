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
      <td width="100%" style="font-size:14;text-align:center;">RECURSOS DE PERSONAL</td>	  	  
    </tr>	
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">PROGRAMA ${o.program_id.sequence} - ${o.program_id.name}</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="60%">Cargo/Categoria</th>
        <th style="font-size:11px" width="20%">Num. Servidores</th>
        <th style="font-size:11px" width="20%">Total Anual</th>
      </tr>
    </thead>
    <%
       total_funcionarios = total_sueldo = 0
       %>
    %for line in o.line_ids:
	<%
	   total_funcionarios += line.funcionarios
	   total_sueldo += line.total
	   %>
    <tr style="page-break-inside:avoid">
      <td width="60%" style="font-size:11px;text-align:left">${line.cargo_id2}</td>
      <td width="20%" style="font-size:11px;text-align:right">${line.funcionarios}</td>
      <td width="20%" style="font-size:11px;text-align:right">${line.total}</td>
    </tr>
    %endfor
      <tr>
        <th style="font-size:11px;text-align:left" width="60%">TOTAL GENERAL</th>
        <th style="font-size:11px;text-align:right" width="20%">${total_funcionarios}</th>
        <th style="font-size:11px;text-align:right" width="20%">${total_sueldo}</th>
      </tr>
  </table>
  %endfor
</html>
