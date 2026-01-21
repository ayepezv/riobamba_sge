<html>
  <head>
    <style type="text/css">
      ${css}
    </style>
  </head>
  <body>
    <H1><center>LISTADO DE ACTIVOS Y COMPONENTES</center></H1>
    <table BGCOLOR="#D8D8D8" WIDTH=820 style="text-align:left;font-size:9px">
      <tr WIDTH=820> <b>	
			<td WIDTH=100 > C&oacute;digo</td>	
			<td WIDTH=170 > Descripci&oacute;n</td>					
			<td WIDTH=100 > Categoria de bien/</td>
			<td WIDTH=100 > Transacci&oacute;n</td>
			<td WIDTH=50 > Costo hist&oacute;rico</td>					
			<td WIDTH=100 > Estado</td>
		</>
	</table>
	</p>
    %for inv in objects :
	<table WIDTH=820 rules="none" style="text-align:left;font-size:8px">
		<tr WIDTH=820>
			<td WIDTH=100 >${inv.code or ''|entity}</td>
			<td WIDTH=170 >${inv.name or ''|entity}</td>
			<td WIDTH=100 >${inv.category_id.name or ''|entity}</td>
			<td WIDTH=100 >${inv.transaction_id.name or ''|entity}</td>
			<td WIDTH=50 >${inv.purchase_value or ''|entity}</td>			
			<td width=100 >${(inv.state == 'draft') and 'Borrador' or (inv.state == 'open') and 'Operativo' or (inv.state == 'review') and 'En revision' or (inv.state == 'no_depreciate') and 'Operativo' or 'Dado de baja'|entity}</td>
		</tr>
	</table>
	%if len(inv.componentes_ids) > 0 :
	<table WIDTH=820   rules="none" style="text-align:left;font-size:8px">
	  <tr WIDTH=820>		
	    <td WIDTH=100 ></td>
	    <td WIDTH=170 BGCOLOR="#D8D8D8">Nombre</td>
	    <td WIDTH=200 BGCOLOR="#D8D8D8">Descripci&oacute;n</td>
	    <td WIDTH=150 BGCOLOR="#D8D8D8">Marca</b></td>
<td WIDTH=150 BGCOLOR="#D8D8D8">No. Serie</td>
<td WIDTH=50 BGCOLOR="#D8D8D8">Cantidad</td>
</tr>

</table>
<table WIDTH=820 rules="none" style="text-align:left;font-size:8px">
  %for componente in inv.componentes_ids:		
  <tr WIDTH=820> <b>		
      <td WIDTH=100 ></td>
      <td WIDTH=170 >${componente.name or ''|entity}</td>
				<td WIDTH=200 >${componente.value or ''|entity}</td>
				<td WIDTH=150 >${componente.marca or ''|entity}</b></td>
				<td WIDTH=150 >${componente.serie or ''|entity}</td>
				<td WIDTH=50 >${componente.cantidad or ''|entity}</td>
			</tr>
		%endfor
		</table>
	%endif
    %endfor
</body>
</html>
