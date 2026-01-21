<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
	<H2><center> Activos Fijos por Custodio</center></H2>	
    %for employee in objects :    		
    	%if len(employee.account_asset_ids_) > 0 :
    		</br>
			</br>
	    	<span class="title">${_("Custodio:   ")} ${employee.name or ''|entity}</span>
	    	<table BGCOLOR="#D8D8D8" WIDTH=1250>
				<tr WIDTH=1250> <b>
					<td WIDTH=150 > C&oacute;digo</td>
					<td WIDTH=150 > Descripci&oacute;n</td>
					<td WIDTH=300 > Tipo/Subtipo/Clase</td>				
					<td WIDTH=100 > Estado</td>
				</>
			</table>
	    	%for inv in employee.account_asset_ids_ :
				<table WIDTH=1250 rules="all" style="text-align:left;font-size:10px">
					<tr WIDTH=1250>
						<td WIDTH=150 >${inv.code or ''|entity}</td>
						<td WIDTH=150 >${inv.name or ''|entity}</td>
						<td WIDTH=300 >${inv.tipo_id.name or ''|entity}/${inv.subtipo_id.name or ''|entity}${inv.class_id.name or ''|entity}</td>
						<td WIDTH=100 >${(inv.state == 'draft') and 'Borrador' or (inv.state == 'open') and 'Operativo' or (inv.state == 'review') and 'En revision' or (inv.state == 'no_depreciate') and 'Operativo' or 'Dado de baja'|entity}</td>
					</tr>
				</table>
			%endfor
		%endif
    %endfor
    </p>
    </p>
</body>
</html>
