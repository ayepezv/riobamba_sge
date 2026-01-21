<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
	<H1><center>ACTIVOS SINIESTRADOS</center></H1>
	<table BGCOLOR="#D8D8D8" WIDTH=900 style="text-align:left;font-size:9px">
		<tr WIDTH=900> <b>	
			<td WIDTH=200 > Activo</td>	
			<td WIDTH=350 align="left"> Tipo/Subtipo/Clase</td>
			<td WIDTH=100 align="left"> Estado del Activo</td>
			<td WIDTH=150 align="left"> Siniestro</td>								
			<td WIDTH=100 align="left"> Estado de Siniestro</td>
		</>
	</table>
	</p>
    %for inv in objects :
	%if len(inv.sinister_ids) > 0 :
		%for siniestro in inv.sinister_ids:			
				<table WIDTH=900 rules="none" style="text-align:left;font-size:8px">
					<tr WIDTH=900>
						<td WIDTH=200 align="left">${inv.code or ''|entity}/${inv.name or ''|entity}</td>
						<td WIDTH=350 align="left">${inv.tipo_id.name or ''|entity}/${inv.subtipo_id.name or ''|entity}/${inv.class_id.name or ''|entity}</td>
						<td width=100 align="left">${(inv.state == 'draft') and 'Borrador' or (inv.state == 'open') and 'Operativo' or (inv.state == 'review') and 'En revision' or (inv.state == 'no_depreciate') and 'Operativo' or 'Dado de baja'|entity}</td>
			
						<td WIDTH=150 align="left">${siniestro.name.name or ''|entity} </td>
						<td width=100 align="left">${(siniestro.state == 'draft') and 'Borrador' or (siniestro.state == 'open') and 'Abierto' or (siniestro.state == 'cancel') and 'Cancelado' or 'Finalizado'|entity}</td>
					</tr>			
						
				</table>
		%endfor	
	%endif
    %endfor
</body>
</html>
