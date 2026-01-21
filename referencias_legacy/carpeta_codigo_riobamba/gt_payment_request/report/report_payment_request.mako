<!DOCTYPE HTML>
<html>
  <head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>	

  %for line in objects :	
  <table cellspacing="0" cellpadding="2" WIDTH="100%">
	  <tr>
	    
	  </tr>  
	</table>
	<table cellspacing="0" cellpadding="2" WIDTH="100%">
	  <tr>
	    <th style="font-size:19px" WIDTH="100%">SOLICITUD DE PAGO No. ${ line.name }</th>
	  </tr>  
	</table>
	<table width="100%" rules="cols" cellspacing="0" cellpadding="5" style="font-size:12px" border="1">  
		<tr>  		
			<th WIDTH="30%" align="right">  Fecha Solicitud: </th>
			<td WIDTH="70%" >${ formatLang(line.date_request,date_time=True) or ''|entity}</td>
		</tr>	
		<tr>  
			<th WIDTH="30%" align="right">  Solicitado por: </th>
			<td WIDTH="70%" >${line.emp_solicitante.complete_name or ''|entity}</td>
		</tr>
		<tr>  	
			<th WIDTH="30%" align="right">  Proveedor: </th>
			<td WIDTH="70%" >${line.partner_id.ced_ruc or ''|entity} ${line.partner_id.name or ''|entity}</td>
		</tr>			
		<tr> 	
			<th WIDTH="30%" align="right">  Fecha Emisi&oacute;n:</th>
			<td WIDTH="70%" >${line.date_request or ''|entity}</td>
		</tr>
		<tr>  	
			<th WIDTH="30%" align="right">  Monto: </th>
			<td WIDTH="70%" >USD. ${line.amount_invoice or ''|entity} ( ${ _get_letras(line.amount_invoice) or ''|entity} ) </td>
		</tr>
		<tr>  	
			<th WIDTH="30%" align="right">  Proceso: </th>
			<td WIDTH="70%" >${line.type_doc or ''|entity}</td>
		</tr>
		<tr>  	
			<th WIDTH="30%" align="right">  Concepto: </th>
			<td WIDTH="70%" >${line.concepto or ''|entity}</td>
		</tr>
	</table>	
	<table width="100%" rules="cols" cellspacing="0" cellpadding="5" style="font-size:12px" border="1">
	  <tr>  		
		<th WIDTH="50%" align="center">  Elaborado Por: </th>
		<th WIDTH="50%" align="center">  Autorizado Por: </th>
	  </tr>	
	  <tr>  		
		<th WIDTH="50%" align="center">${line.user_id.name or ''|entity}</th>
		<th WIDTH="50%" align="center">  ALCALDE: Ing. Marcos Chica </th>
	  </tr>	
	</table>	
    %endfor
<br></br>
<br></br>
  %for line in objects :	
  <table cellspacing="0" cellpadding="2" WIDTH="100%">
	  <tr>
	    
	  </tr>  
	</table>
	<table cellspacing="0" cellpadding="2" WIDTH="100%">
	  <tr>
	    <th style="font-size:19px" WIDTH="100%">SOLICITUD DE PAGO No. ${ line.name }</th>
	  </tr>  
	</table>
	<table width="100%" rules="cols" cellspacing="0" cellpadding="5" style="font-size:12px" border="1">  
		<tr>  		
			<th WIDTH="30%" align="right">  Fecha Solicitud: </th>
			<td WIDTH="70%" >${ formatLang(line.date_request,date_time=True) or ''|entity}</td>
		</tr>	
		<tr>  
			<th WIDTH="30%" align="right">  Solicitado por: </th>
			<td WIDTH="70%" >${line.emp_solicitante.complete_name or ''|entity}</td>
		</tr>
		<tr>  	
			<th WIDTH="30%" align="right">  Proveedor: </th>
			<td WIDTH="70%" >${line.partner_id.ced_ruc or ''|entity} ${line.partner_id.name or ''|entity}</td>
		</tr>			
		<tr> 	
			<th WIDTH="30%" align="right">  Fecha Emisi&oacute;n:</th>
			<td WIDTH="70%" >${line.date_request or ''|entity}</td>
		</tr>
		<tr>  	
			<th WIDTH="30%" align="right">  Monto: </th>
			<td WIDTH="70%" >USD. ${line.amount_invoice or ''|entity} ( ${ _get_letras(line.amount_invoice) or ''|entity} ) </td>
		</tr>
		<tr>  	
			<th WIDTH="30%" align="right">  Proceso: </th>
			<td WIDTH="70%" >${line.type_doc or ''|entity}</td>
		</tr>
		<tr>  	
			<th WIDTH="30%" align="right">  Concepto: </th>
			<td WIDTH="70%" >${line.concepto or ''|entity}</td>
		</tr>
	</table>	
	<table width="100%" rules="cols" cellspacing="0" cellpadding="5" style="font-size:12px" border="1">
	  <tr>  		
		<th WIDTH="50%" align="center">  Elaborado Por: </th>
		<th WIDTH="50%" align="center">  Autorizado Por: </th>
	  </tr>	
	  <tr>  		
		<th WIDTH="50%" align="center">${line.user_id.name or ''|entity}</th>
		<th WIDTH="50%" align="center">  ALCALDE: Ing. Marcos Chica </th>
	  </tr>	
	</table>	
    %endfor
    
</html>
