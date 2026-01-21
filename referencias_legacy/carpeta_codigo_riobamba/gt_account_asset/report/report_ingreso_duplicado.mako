<!DOCTYPE HTML>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>

    %for inv in objects :
	<H2><center>INGRESO DE BIENES</center></H2>
	<table WIDTH=1000 style="font-size:10px">
		<tr WIDTH=1000>
			<td WIDTH=150 > TIPO DE TRANSACCION:</td>
			<td WIDTH=850 >${inv.transaction_id.name or ''|entity}</td>	
		</tr>
		<tr WIDTH=1000>
			<td WIDTH=150 > DETALLE DE TRANSACCION:</td>
			<td WIDTH=850 >${inv.detail or ''|entity}</td>	
		</tr>
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
	  <tr WIDTH=1000>
			<td WIDTH=150 align="right">Categoria:  </td>
			<td WIDTH=850 >${inv.category_id.name or ''|entity}</td>	
		</tr>
		<tr WIDTH=1000>
			<td WIDTH=150 align="right">C&oacute;digo:  </td>
			<td WIDTH=850 >
			${inv.asset_id.code or ''|entity} 
			%for activo_cod in inv.asset_ids:
				-- ${activo_cod.code or ''|entity} 
			%endfor
			</td>	
		</tr>
	  <tr WIDTH=1000>
			<td WIDTH=150 align="right">Descripci&oacute;n:  </td>					
			<td WIDTH=850 >${inv.name or ''|entity}</td>	
		</tr>
		<tr WIDTH=1000>
			<td WIDTH=150 align="right">Observaciones:  </td>					
			<td WIDTH=850 >${inv.asset_id.note or ''|entity}</td>	
		</tr>
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000>
			<td WIDTH=150 align="center">CARACTERISTICAS</td>
		</tr>		
	</table>
	<table WIDTH=1000 style="font-size:8px" rules="none" border="1">	
		%for activo in inv.asset_id.asset_property_ids:
		<tr WIDTH=1000> <b>		
			<td WIDTH=150 align="right">${activo.name.name or ''|entity}: </td>
			<td WIDTH=850 >${activo.value or ''|entity}</b></td>
		</tr>
		%endfor
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000>
			<td WIDTH=150 align="center">FECHAS Y VALORACION</td>
		</tr>		
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000>
			<td WIDTH=150 align="right">Fecha Adquisici&oacute;n:  </td>
			<td WIDTH=350 >${inv.asset_id.purchase_date or ''|entity}</td>		
			<td WIDTH=150 align="right">Vida Util:  </td>
			<td WIDTH=350 >${inv.asset_id.method_number or ''|entity}</td>	
		</tr>
		<tr WIDTH=1000>
			<td WIDTH=150 align="right">Valor:  </td>
			<td WIDTH=350 >${inv.asset_id.purchase_value or ''|entity}</td>	
			<td WIDTH=150 align="right">Dep Mensual:  </td>
			<td WIDTH=350 >${get_dep_mensual(inv.asset_id.id)}</td>	

		</tr>
		<tr WIDTH=1000>
			<td WIDTH=150 align="right">Dep. Acumulada:  </td>
			<td WIDTH=350 >${get_dep_acumulada(inv.asset_id.id)}</td>		
			<td WIDTH=150 align="right">Valor en Libros:  </td>
			<td WIDTH=350 >${inv.asset_id.purchase_value or ''|entity}</td>	
		</tr>
		<tr WIDTH=1000>
			<td WIDTH=150 align="right">Saldo x Depreciar:  </td>
			<td WIDTH=350 >${inv.asset_id.value_residual or ''|entity}</td>		
			<td WIDTH=150 align="right">Fecha Aplicaci&oacute;n Dep:  </td>
			<td WIDTH=350 >${inv.asset_id.purchase_date or ''|entity}</td>	
		</tr>

		<tr WIDTH=1000>
			<td WIDTH=150 align="right"></td>
			<td WIDTH=350 ></td>		
			<td WIDTH=150 align="right">Valor Residual:  </td>
			<td WIDTH=350 >${inv.asset_id.salvage_value or ''|entity}</td>	
		</tr>
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000>
			<td WIDTH=150 align="center">CUSTODIOS</td>
		</tr>		
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000> 		
			<td WIDTH=200 align="center">Activo</td>
			<td WIDTH=800 align="left">Custodio</b></td>
		</tr>
		<tr WIDTH=1000> 		
			<td WIDTH=200 align="center">${inv.asset_id.code or ''|entity}:</td>
			<td WIDTH=800 align="left">${inv.asset_id.employee_id.complete_name or ''|entity}:</b></td>
		</tr>

	%for activo_det in inv.asset_ids:
		<tr WIDTH=1000> 		
			<td WIDTH=200 align="center">${activo_det.code or ''|entity}: </td>
			<td WIDTH=800 align="left">${activo_det.employee_id.complete_name or ''|entity}</b></td>
		</tr>
	%endfor
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000>
			<td WIDTH=150 align="center">UBICACION</td>
		</tr>		
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000 > <b>		
			<td WIDTH=250 align="left">Provincia</td>
			% if inv.asset_id.state_id:
				<td WIDTH=250>${inv.asset_id.state_id.name  or ''|entity}</td>
			% else:
				<td WIDTH=250></td>
			% endif
			<td WIDTH=250>Area</td>
			% if inv.asset_id.department_id:
				<td WIDTH=250>${inv.asset_id.department_id.name  or ''|entity}</td>
			% endif
			
		</tr>
		<tr WIDTH=1000 > <b>		
			<td WIDTH=250 align="left">Cant&oacute;n</td>
			<td WIDTH=250>${inv.asset_id.canton_id.name  or ''|entity}</td>
			<td WIDTH=250>Secci&oacute;n</td>
			% if inv.asset_id.department_id:
				<td WIDTH=250>${inv.asset_id.department_id.parent_id.name  or ''|entity}</td>			
			% endif
		</tr>
		<tr WIDTH=1000 > <b>		
			<td WIDTH=250 align="left">Parroquia</td>
			<td WIDTH=250>${inv.asset_id.parroquia.name  or ''|entity}</td>
			<td WIDTH=250></td>
			<td WIDTH=250></td>			
		</tr>
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000>
			<td WIDTH=150 align="center">DOCUMENTO DE REFERENCIA</td>
		</tr>		
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000 > <b>		
			<td WIDTH=800 align="left">Proveedor</td>
			<td WIDTH=200>Documento</td>
			<td WIDTH=200>Fecha</td>			
		</tr>
		<tr WIDTH=1000 >
			% if inv.asset_id.invoice_id:
				<td WIDTH=800 align="left">${inv.asset_id.invoice_id.partner_id.name  or ''|entity} </td>
				<td WIDTH=200>${inv.asset_id.invoice_id.number  or ''|entity}</td>
				<td WIDTH=200>${inv.asset_id.invoice_id.date_invoice  or ''|entity}</td>
			% else:
				<td WIDTH=800 align="left"></td>
				<td WIDTH=200></td>
				<td WIDTH=200></td>
			% endif
		</tr>
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000>
			<td WIDTH=150 align="center">COMPONENTES</td>
		</tr>		
	</table>
	<table WIDTH=1000 style="font-size:10px" rules="none" border="1">
		<tr WIDTH=1000 > <b>		
			<td WIDTH=200 align="left">Nombre</td>
			<td WIDTH=500>Descripci&oacute;n</td>
			<td WIDTH=100>Serie</td>
			<td WIDTH=100>Marca</td>
			<td WIDTH=100>Cantidad</td>
		</tr>		
		%for componente in inv.asset_id.componentes_ids:
			<tr WIDTH=1000> <b>		
				<td WIDTH=200 align="left">${componente.name  or ''|entity}</td>
				<td WIDTH=500>${componente.value  or ''|entity}</td>
				<td WIDTH=100>${componente.serie or ''|entity}</td>
				<td WIDTH=100>${componente.marca or ''|entity}</td>
				<td WIDTH=100>${componente.cantidad or ''|entity}</td>
			</tr>
		%endfor
	</table>
    %endfor
</body>
</html>
