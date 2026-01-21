<!DOCTYPE HTML5>
<html>
  <head>
    <style type="text/css">
      ${css}
    </style>
  </head>
  <body>	
    <H2><center>Bienes por Grupo Relacional</center></H2>
    <table BGCOLOR="#D8D8D8" WIDTH=1300>
      <tr WIDTH=1300> <b>
	  <td WIDTH=200 > C&oacute;digo</td>
	  <td WIDTH=150 > Tipo</td>
	  <td WIDTH=200 > Subtipo/Clase</td>
	  <td WIDTH=300 > Descripci&oacute;n</td>
	  <td WIDTH=200 > Custodio</td>									
	  <td WIDTH=100 > Estado</td>
	  <td WIDTH=150 > Activo Padre</td>			
</>
</table>
</p>
%for valor in get_assets(objects):
<table WIDTH=1300 style="font-size:12px">
  <tr WIDTH=1300>
    <td width="200" style="text-align:left"><b>${valor[1] or ''|entity}</b></td>
    <td width="150" style="text-align:left"><b>${valor[0] or ''|entity}</b></td>
    <td width="200" style="text-align:left"><b>${valor[3] or ''|entity}/${valor[4] or ''|entity}</b></td>
    <td width="300" style="text-align:left"><b>${valor[7] or ''|entity}</b></td>
    <td width="200" style="text-align:left"><b>${valor[2] or ''|entity}</b></td>
    
    <td width="100" style="text-align:left">${(valor[5] == 'draft') and 'Borrador' or (valor[5] == 'open') and 'Operativo' or (valor[5] == 'review') and 'En revision' or (valor[5] == 'no_depreciate') and 'Operativo ND' or 'Dado de baja'|entity}</td>
    <td width="150" style="text-align:left"></td>
    
  </tr>		
  %for componente in get_component_asset(valor[6]):
  <tr WIDTH=1300>
    <td width="200" style="text-align:left">${componente[1] or ''|entity}</td>
    <td width="150" style="text-align:left">${componente[0] or ''|entity}</td>
    <td width="200" style="text-align:left">${componente[3] or ''|entity}/${componente[4] or ''|entity}</td>
    <td width="300" style="text-align:left">${componente[7] or ''|entity}</td>
    <td width="200" style="text-align:left">${componente[2] or ''|entity}</b></td>
<td width="100" style="text-align:left">${(componente[5] == 'draft') and 'Borrador' or (componente[5] == 'open') and 'Operativo' or (componente[5] == 'review') and 'En revision' or (componente[5] == 'no_depreciate') and 'Operativo ND' or 'Dado de baja'|entity}</td>
<td width="150" style="text-align:left">${componente[8] or ''|entity}</td>			
</tr>
%endfor
</table>
%endfor
</body>
</html>
