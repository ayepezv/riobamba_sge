<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for inv in objects :
  <H2><center>BAJA DE BIENES DE LARGA DURACION Nº ${inv.name or ''|entity} </center></H2>
  <table WIDTH=1000 style="font-size:14px">
    <tr WIDTH=1000>
      <td WIDTH=150 > Documento:</td>
      <td WIDTH=850 >${inv.document or ''|entity}</td>	
    <tr WIDTH=1000>
      <td WIDTH=150 > Autorizado por:</td>
      <td WIDTH=850 >${inv.autorizado_por.complete_name or ''|entity}</td>	
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 > Detalle</td>
      <td WIDTH=850 >${inv.detail or ''|entity}</td>	
    </tr>
  </table>
  <br>
  <br>
  <table WIDTH=1000 border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">	
    <tr WIDTH=1000 align="center"> <b>		
	<td WIDTH=250 >C&oacute;digo del Bien</td>
	<td WIDTH=200 >Categoria</td>
	<td WIDTH=100 >N. Serie</td>
	<td WIDTH=50 >Valor</td>
	<td WIDTH=400 >Descripci&oacute;n</b></td>

</tr>
</table>
%for activo in inv.asset_ids:
<table WIDTH=1000 border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">	
  <tr WIDTH=1000> <b>		
      <td WIDTH=250 >${activo.asset_id.code or ''|entity}</td>
      <td WIDTH=200 >${activo.asset_id.category_id.name or ''|entity}</b></td>
<td WIDTH=100 align="right">${activo.asset_id.serial_number or ''|entity}</td>
<td WIDTH=50 align="right">${activo.asset_id.purchase_value or ''|entity}</td>
<td WIDTH=400 >${activo.asset_id.name or ''|entity}</td>
</tr>
</table>	
%endfor
<table WIDTH=1000 style="font-size:14px" >	
  <tr WIDTH=1000> <b>		
      <td WIDTH=150 ></td>
      <td WIDTH=150 ></td>
      <td WIDTH=100 align="right">Total:</td>
      <td WIDTH=100 align="right">${inv.valor_total or ''|entity}</td>
      <td WIDTH=500 ></td>
  </tr>
</table>
<br>
<br>
	<br>
	<br>
	<br>
	<br>
	<br>
	<table WIDTH=1200 style="font-size:12px" >	
		<tr WIDTH=1200 > <b>		
			<td WIDTH=1200 > <center> AUTORIZADO</center></td>
		</tr>
		<tr WIDTH=1200 > <b>		
			<td WIDTH=1200 > <center> ${inv.autorizado_por.complete_name or ''|entity}</center></td>
		</tr>
	</table>
    %endfor
</body>
</html>
