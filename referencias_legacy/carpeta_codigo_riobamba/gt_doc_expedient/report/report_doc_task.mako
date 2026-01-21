<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
    <style type="text/css">
        ${css}
    </style>
</head>

<h2>Tareas Pendientes por Usuario</h2>
<body>
    <table border=1>
	<tr>
	<th width="300" style="text-align:left">Empleado</th>
	<th width="300" style="text-align:left">Departamento</th>
	<th width="90" style="text-align:left">Cantidad</th>
	</tr>
    </table>	
%for registro in get_tareas_empleado():
	<table border=1>
		<tr>
		<td width="300" style="text-align:left">${registro[1]}</td>
		<td width="300" style="text-align:left">${registro[3]}</td>
		<td width="90" style="text-align:left">${registro[4]}</td>
		</tr>
	</table>
%endfor

%for registro in get_total_tareas(objects):
	<table border=1>
		<tr>
		<td width="300" style="text-align:left">${registro[0]}</td>
		<td width="300" style="text-align:left">${registro[1]}</td>
		<td width="90" style="text-align:left">${registro[2]}</td>
		</tr>
	</table>
%endfor
	
    </p>
    </p>
</body>
</html>
