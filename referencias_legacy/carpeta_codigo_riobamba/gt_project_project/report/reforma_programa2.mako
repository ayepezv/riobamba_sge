<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>

</head>
<body style="overflow:visible;">	
    %for obj in objects:
    <tr style="border: 1px solid black;"><h2 style="text-align:center;" align="center">REFORMA PRESUPUESTARIA DE EGRESO</h1></tr>
<!-- COLUMNA 1 -->
%for program_id in all_programas(obj):
    <%
       first=0
       %>
    <table cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px;border: 1px solid black"  width="100%" border="1" rules="none">
      <tr style="border: 1px solid black;"><h2 style="text-align:center;" align="center">PROGRAMA : ${program_id.sequence} - ${program_id.name}</h1></tr>
     %for linea in generate_dict(obj,program_id):

    </table>
<!-- FIN COLUMNA 1 -->
    %endfor
</table>
%endfor
  <table width="100%" style="page-break-inside:avoid">
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
	<tr style="font-size:11px">
      <th width="50%">Creado por</th>
      <th width="50%">Autorizado</th>
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
	<tr style="font-size:11px">
      <th width="33%">${user.employee_id.complete_name}</th>
      <th width="33%">${user.context_department_id.manager_id.complete_name}</th>
	</tr>  
  </table>
</body>
</html>
