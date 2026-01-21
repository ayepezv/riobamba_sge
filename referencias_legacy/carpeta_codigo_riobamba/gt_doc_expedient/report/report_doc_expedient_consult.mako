<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>	
    %for expedient in objects:
    <table style="text-align:left;font-size:10px">
    	<tr>
    	<th width="50"><b>Asunto:</b></th>
    	<td width="500">${expedient.name}</td>
    	<th width="70"><b>Núm.Trámite:</b></th>
    	<td width="100">${expedient.code}</td>
    	</tr>
    	
    </table>
    <table style="text-align:left;font-size:10px">
    	<tr>
    	<th width="50"><b>Creado por:</b></th>
    	<td width="300">${expedient.user_id.name}</td>
    	<th width="70"><b>Fecha Creación:</b></th>
    	<td width="200">${expedient.creation_date}</td>
    	</tr>
    </table>
    
    <p><b>Resumen:</b> ${expedient.resumen}</br></p>
	<p><b>TAREAS DEL TRÁMITE<b><p>
	<table rules="all" border="1" style="text-align:left;font-size:10px">
		<tr>
		<th width="40">Núm.</th>
		<th width="250">Tarea</th>
		<th width="100">Fecha Creación</th>
		<th width="150">Enviado por</th>
		<th width="150">Asignado a</th>
		<th width="70">Prioridad</th>
		<th width="70">Estado</th>
		</tr>
	</table>
	%for t in get_tasks_expedient(objects):
	<table rules="all" border="1" style="text-align:left;font-size:10px">
		<tr>
		<td width="40">${t.task_sequence}</td>
		<td width="250">${(t.other_action_chk == True) and (t.other_action) or (t.action_id.name)}</td>
		<td width="100">${t.date_task}</td>
		<td width="150">${t.user_id.name}</td>
		<td width="150">${t.employee_id.name}</td>
		<td width="70">${(t.priority == 'normal') and 'normal' or (t.priority == 'urgent') and 'urgente' or 'media'}</td>
		<td width="70">${(t.state == 'draft') and 'borrador' or (t.state == 'progress') and 'pendiente' or (t.state == 'done') and 'realizado' or 'anulado'}</td>
		</tr>

	</table>
        %endfor
	<p><b>REFERENCIAS</b></p>
	<table rules="all" border="1" style="text-align:left;font-size:10px">
		<tr>
		<th width="120">Núm.Trámite</th>
		<th width="630">Asunto</th>
		</tr>
	</table>
	%for r in expedient.references:
	<table rules="all" border="1" style="text-align:left;font-size:8px">
		<tr>
		<td width="120">${r.code}</td>
		<td width="630">${r.name}</td>
		</tr>
	</table>
	
	%endfor
	<p><b>DOCUMENTOS</b></p>
	<table rules="all" border="1" style="text-align:left;font-size:10px">
		<tr>
		<th width="50">Tarea</th>
		<th width="160">Descripción</th>
		<th width="200">Nombre del Archivo</th>
		<th width="170">Subido por</th>
		<th width="150">Fecha Adjunto</th>
		</tr>
	</table>
	%for d in expedient.documents:
	<table rules="all" border="1" style="text-align:left;font-size:8px">
		<tr>
		<td width="50">${d.document_id.name}</td>
		<td width="160">${d.name}</td>
		<td width="200">${d.datas_fname}</td>
		<td width="170">${d.create_uid.name}</td>
		<td width="150">${d.create_date}</td>
		</tr>
	</table>
	
	%endfor
			   
    %endfor
	
    </p>
    </p>
</body>
</html>
