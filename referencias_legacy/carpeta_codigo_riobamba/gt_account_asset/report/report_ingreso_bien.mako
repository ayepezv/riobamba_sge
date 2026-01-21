<!DOCTYPE HTML>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>

  %for inv in objects :
  <H2><center>INGRESO DE BIENES ${inv.secuencia or ''|entity}</center></H2>
  <H2><center>${inv.type or ''|entity}</center></H2>
  <table WIDTH=1000 style="font-size:12px">
    <tr WIDTH=1000>
      <td WIDTH=150 > TIPO DE TRANSACCION:</td>
      <td WIDTH=850 >${inv.transaction_id.name or ''|entity}</td>	
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 > DETALLE DE TRANSACCION:</td>
      <td WIDTH=850 >${inv.note or ''|entity}</td>	
    </tr>
  </table>
  <table WIDTH=1000 style="font-size:12px" rules="none" border="1">
    <tr WIDTH=1000>
      <td WIDTH=150 align="right">Categoria:  </td>
      <td WIDTH=850 >${inv.category_id.name or ''|entity}</td>	
    </tr>		
    <tr WIDTH=1000>
      <td WIDTH=150 align="right">Sub Categoria:  </td>
      <td WIDTH=850 >${inv.subcateg_id.name or ''|entity}</td>	
    </tr>		
    <tr WIDTH=1000>
      <td WIDTH=150 align="right">Cuenta Contable:  </td>
      <td WIDTH=850 >${inv.cuenta_contable or inv.category_id.cuenta_ingreso.code_aux or ''|entity}</td>	
    </tr>		
    <tr WIDTH=1000>
      <td WIDTH=150 align="right">C&oacute;digo:  </td>
      <td WIDTH=850 >${inv.code or ''|entity}</td>	
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 align="right">Descripci&oacute;n:  </td>					
      <td WIDTH=850 >${inv.name or ''|entity}</td>	
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 align="right">Observaciones:  </td>					
      <td WIDTH=850 >${inv.note or ''|entity} ${inv.otros_accesorios or ''|entity}</td>	
    </tr>
  </table>
  <table WIDTH=1000 style="font-size:12px" rules="none" border="1">
    <tr WIDTH=1000>
      <td WIDTH=150 align="center">CARACTERISTICAS</td>
    </tr>		
  </table>
  <table WIDTH=1000 style="font-size:12px" rules="none" border="1">
    <tr WIDTH=1000>
      <td WIDTH=150 align="right">Estado:  </td>
      <td WIDTH=350 >${inv.condicion or ''|entity}</td>		
      <td WIDTH=150 align="right">Estado Externo:  </td>
      <td WIDTH=350 >${inv.state2 or ''|entity}</td>	
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 align="right">Marca:  </td>
      <td WIDTH=350 >${inv.marca or ''|entity}</td>		
      <td WIDTH=150 align="right">Modelo:  </td>
      <td WIDTH=350 >${inv.modelo or ''|entity}</td>	
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 align="right">Color:  </td>
      <td WIDTH=350 >${inv.color or ''|entity}</td>		
      <td WIDTH=150 align="right">Num. Serie:  </td>
      <td WIDTH=350 >${inv.serial_number or ''|entity}</td>	
    </tr>
    
  </table>
  <table WIDTH=1000 style="font-size:12px" rules="none" border="1">	
    %for activo in inv.asset_property_ids:
    <tr WIDTH=1000> <b>		
	<td WIDTH=150 align="right">${activo.name.name or ''|entity}: </td>
	<td WIDTH=850 >${activo.value or ''|entity}</b></td>
</tr>
%endfor
</table>	

<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000>
    <td WIDTH=150 align="center">FECHAS Y VALORACION</td>
  </tr>		
</table>
<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000>
    <td WIDTH=150 align="right">Fecha Adquisici&oacute;n:  </td>
    <td WIDTH=350 >${inv.purchase_date or ''|entity}</td>
    %if inv.type=='Larga Duracion':		
    <td WIDTH=150 align="right">Vida Util:  </td>
    <td WIDTH=350 >${inv.method_number or ''|entity}</td>	
    %endif
  </tr>
  <tr WIDTH=1000>
    <td WIDTH=150 align="right">Valor:  </td>
    <td WIDTH=350 >${inv.purchase_value or ''|entity}</td>
    %if inv.type=='Larga Duracion':	
    <td WIDTH=150 align="right">Dep Mensual:  </td>
    <td WIDTH=350 >${get_dep_mensual(inv.id)}</td>	
    %endif
  </tr>
  <tr WIDTH=1000>
    %if inv.type=='Larga Duracion':
    <td WIDTH=150 align="right">Dep. Acumulada:  </td>
    <td WIDTH=350 >${inv.depreciacion}</td>
    %endif
    <td WIDTH=150 align="right">Valor en Libros:  </td>
    <td WIDTH=350 >${inv.purchase_value or ''|entity}</td>	
  </tr>
  <tr WIDTH=1000>
    %if inv.type=='Larga Duracion':
    <td WIDTH=150 align="right">Saldo x Depreciar:  </td>
    <td WIDTH=350 >${inv.value_residual or ''|entity}</td>		
    <td WIDTH=150 align="right">Fecha Aplicaci&oacute;n Dep:  </td>
    <td WIDTH=350 >${inv.purchase_date or ''|entity}</td>	
    %endif
  </tr>
  %if inv.type=='Larga Duracion':
  <tr WIDTH=1000>
    <td WIDTH=150 align="right"></td>
    <td WIDTH=350 ></td>		
    <td WIDTH=150 align="right">Valor Residual:  </td>
    <td WIDTH=350 >${inv.salvage_value or ''|entity}</td>	
  </tr>
  %endif
</table>
<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000>
    <td WIDTH=150 align="center">CUSTODIO</td>
  </tr>		
</table>
<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000 > <b>		
      <td WIDTH=800 align="left">Nombre</td>
      <td WIDTH=200>Usa</td>
  </tr>
  <tr WIDTH=1000>
    <td WIDTH=800 align="left">${inv.employee_id.complete_name or ''|entity} </td>
    <td WIDTH=200 >x</td>
  </tr>		
  %for activo in inv.transfer_ids:
  <tr WIDTH=1000> <b>		
      <td WIDTH=800 align="left">${activo.emp_old_id.complete_name or ''|entity}</td>
      <td WIDTH=200 ></b></td>
</tr>
%endfor
</table>	
<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000>
    <td WIDTH=150 align="center">UBICACION</td>
  </tr>		
</table>
<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000 > <b>		
      <td WIDTH=250 align="left">Provincia</td>
      <td WIDTH=250>${inv.state_id.name  or ''|entity}</td>
      <td WIDTH=250>Area</td>
      <td WIDTH=250>${inv.area_id.name  or ''|entity}</td>
  </tr>
  <tr WIDTH=1000 > <b>		
      <td WIDTH=250 align="left">Cant&oacute;n</td>
      <td WIDTH=250>${inv.canton_id.name  or ''|entity}</td>
      <td WIDTH=250>Secci&oacute;n</td>
      <td WIDTH=250>${inv.seccion_id.name  or ''|entity}</td>			
      
  </tr>
  <tr WIDTH=1000 > <b>		
      <td WIDTH=250 align="left">Parroquia</td>
      <td WIDTH=250>${inv.parroquia.name  or ''|entity}</td>
      <td WIDTH=250>SubSecci&oacute;n</td>
      <td WIDTH=250>${inv.subseccion_id.name  or ''|entity}</td>			
  </tr>
    <tr WIDTH=1000 > <b>		
      <td WIDTH=250 align="left">Direcci&oacute;n</td>
      <td WIDTH=250>${inv.direccion_id.name  or ''|entity}</td>
      <td WIDTH=250></td>
      <td WIDTH=250></td>			
  </tr>
</table>
<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000>
    <td WIDTH=150 align="center">DOCUMENTO DE REFERENCIA</td>
  </tr>		
</table>
<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000 > <b>		
      <td WIDTH=800 align="left">Proveedor</td>
      <td WIDTH=200>Documento</td>
      <td WIDTH=200>Fecha</td>
      
  </tr>
  
  <tr WIDTH=1000 >
    <td WIDTH=800 align="left">${inv.partner_id.name  or ''|entity} </td>
    <td WIDTH=200>${inv.invoice_id  or ''|entity}</td>
    <td WIDTH=200>${inv.purchase_date  or ''|entity}</td>
  </tr>
</table>
<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000>
    <td WIDTH=150 align="center">COMPONENTES</td>
  </tr>		
</table>
<table WIDTH=1000 style="font-size:12px" rules="none" border="1">
  <tr WIDTH=1000 > <b>		
      <td WIDTH=200 align="left">Nombre</td>
      <td WIDTH=500>Descripci&oacute;n</td>
      <td WIDTH=100>Serie</td>
      <td WIDTH=100>Marca</td>
      <td WIDTH=100>Cantidad</td>
  </tr>		
  %for componente in inv.componentes_ids:
  <tr WIDTH=1000> <b>		
      <td WIDTH=200 align="left">${componente.name  or ''|entity}</td>
      <td WIDTH=500>${componente.value  or ''|entity}</td>
      <td WIDTH=100>${componente.serie or ''|entity}</td>
      <td WIDTH=100>${componente.marca or ''|entity}</td>
      <td WIDTH=100>${componente.cantidad or ''|entity}</td>
  </tr>
  %endfor
</table>
	<br>
	<br>
	<br>
	<br>
	<br>
	<br>
	<br>
	<table WIDTH=1000 style="font-size:12px" >	
		<tr WIDTH=1000 > <b>		
			<td WIDTH=400 > <center> RESPONSABLE</center></td>
		</tr>
		<tr WIDTH=1000 > <b>		
			<td WIDTH=400 > <center> ${ user.name or ''|entity} </center></td>
		</tr>
	</table>
    %endfor
</body>
</html>
