<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>	
%for inv in objects :
<body>	

  <H1><center>MOVIMIENTO DE ACTIVOS</center></H1>
  
  <table WIDTH=1000 style="text-align:left;font-size:13px" >
    <tr WIDTH=1000> <b>		
	<td WIDTH=50 style="font-size:11px;text-align:left"> <b>Activo</b></td>
	<td WIDTH=200 style="font-size:11px;text-align:left">${inv.name or ''|entity}</td>
	<td WIDTH=50 style="font-size:11px;text-align:left"> <b>C&oacute;digo</b></td>
	<td WIDTH=200 style="font-size:11px;text-align:left">${inv.code or ''|entity}</td>
	<td WIDTH=100 style="font-size:11px;text-align:left"> <b>Categoria de Bien</b></td>
	<td WIDTH=400 style="font-size:11px;text-align:left">${inv.category_id.name or ''|entity}</td>
    </tr>		
  </table>
  <br>
  <br>
  <table WIDTH=1000 >
    <tr WIDTH=1000> <b>		
	<td WIDTH=1000 style="text-align:left;font-size:13px"> <b>Detalle de Movimientos</b></td>
    </tr>
  </table>
  <table WIDTH=1000 style="text-align:left;font-size:13px" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
    <tr WIDTH=1000 BGCOLOR="#D8D8D8"> <b>		
	<td WIDTH=100 > <b>C&oacute;digo</b></td>
	<td WIDTH=200 > <b>Movimiento</b></td>
	<td WIDTH=150 > <b>Realizado por</b></td>
	<td WIDTH=550 > <b>Justificaci&oacute;n</b></td>
    </tr>
    %for componente in inv.asset_moves_ids:
    
    <tr WIDTH=1000> <b>		
	<td WIDTH=100 >${componente.name or ''|entity}</td>
	<td WIDTH=200 >${(componente.type == 'ingreso') and 'Registro' or (componente.type == 'secuencial_ingreso') and 'Secuencial de Ingreso' or (componente.type == 'modificacion') and 'Modificacion' or (componente.type == 'transferencia') and 'Transferencia' or 'Dado de baja'|entity}</td>
	      <td WIDTH=150 >${componente.created_id.name or ''|entity}</b></td>
<td WIDTH=550 >${componente.justificacion or ''|entity}</td>
</tr>
%endfor
	</table>

</body>
%endfor
</html>
