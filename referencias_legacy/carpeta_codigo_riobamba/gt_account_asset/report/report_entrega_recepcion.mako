<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>

    %for inv in objects :
	<H1><center>GESTIÓN ADMINISTRATIVA - ADMINISTRACIÓN DE BIENES</center></H1>
	<H2><center>ACTA DE ENTREGA RECEPCION DE BIENES ${inv.name or ''|entity}</center></H2>
	<H2><center>${inv.tipo or ''|entity} </center></H2>
	<table WIDTH=1000 style="font-size:14px;text-align:justify">
	  <tr WIDTH=1000>
	    <td WIDTH=1000 style="font-size:14px;text-align:justify"> En el Cant&oacute;n de ${user.company_id.city or ''|entity}, Provincia del ${user.company_id.state_id.name or ''|entity}, a los ${inv.date or ''|entity}, en las oficinas de ${user.context_department_id.name or ''|entity}, de el ${user.company_id.name or ''|entity}, se re&uacute;nen por una parte ${user.context_department_id.coordinador_id.complete_name or ''|entity}, en calidad de ${user.context_department_id.coordinador_id.job_id.name or ''|entity}, y por otra,
%if inv.tipo in ('Comodato','Donacion'): 
${inv.entidad or ''|entity}
%else:
${inv.emp_new_id.complete_name or ''|entity}
%endif
, con el fin de realizar la entrega recepci&oacute;n de los bienes que se detallan a continuaci&oacute;n, conforme lo indica el Art. 20 del Reglamento General para la Administración, Utilización, Manejo y Control de los Bienes e Inventarios del Sector Público.</td>		
	</tr>
	</table>
	<br>
	<br>
	<table WIDTH=1000 style="font-size:14px" rules="none" border="1">	
		<tr WIDTH=1000 > <b>		
			<td  width="25%">C&oacute;digo</td>
			<td  width="45%">Descripci&oacute;n</b></td>
			<td  width="10%">N&uacute;mero Serie</td>
			<td  width="10%">Fecha de Adquisici&oacute;n</td>
			<td  width="10%">Valor</td>
		</tr>
	</table>
%for activo in inv.transfer_ids:
<table WIDTH=1000 style="font-size:14px" border="1" cellpadding="2" cellspacing="0">	
  <tr WIDTH=1000 style="page-break-inside:avoid"> <b>		
      <td  width="25%">${activo.asset_id.code or ''|entity}</td>
      <td  width="45%">${activo.asset_id.name or ''|entity}</b></td>
<td  width="10%" align="center">${activo.asset_id.serial_number or ''|entity}</td>
<td  width="10%">${activo.asset_id.purchase_date or ''|entity}</td>
<td  width="10%" align="right">${activo.asset_id.purchase_value or ''|entity}</td>
</tr>
</table>	
	%endfor
<table WIDTH=1000 style="font-size:14px" border="1" cellpadding="2" cellspacing="0">	
  <tr WIDTH=1000 style="page-break-inside:avoid"> <b>		
      <td  width="80%" ></td>
<td  width="10%" >Total</td>
<td  width="10%" align="right">${inv.valor_total or ''|entity}</td>
</tr>
</table>
<br>
<table WIDTH=1000 style="font-size:14px;text-align:justify">
  <tr WIDTH=1000>
    <td WIDTH=1000 style="text-align:justify">La presente acta de entrega recepción se la suscribe y firma en dos ejemplares del mismo tenor, amparado en lo que dispone el Art. 44 literal c) del Reglamento General para la  Administración, Utilización, Manejo y Control de los Bienes e Inventarios del Sector Público, señalando además que a partir de la presente fecha queda bajo la responsabilidad y cuidado de la persona que recibe los bienes entregados, hasta que los devuelva a este Subproceso.</td>
  </tr>
  <tr WIDTH=1000>
    <td WIDTH=1000 >En constancia y fe de lo actuado, firman las partes intervinientes</td>
  </tr>
</table>
<br>
<br>
<br>
	<br>
<br>
<br>
<table WIDTH=1000 style="font-size:14px" >	
  <tr WIDTH=1000 > <b>		
      <td WIDTH=200 > <center> ELABORADO</center></td>
      <td WIDTH=200 > <center> ENTREGUE CONFORME</center></td>
      <td WIDTH=200 > <center> RECIBI CONFORME</center></b></td>
<td WIDTH=200 > <center> AUTORIZADO</center></td>
</tr>
<tr WIDTH=1000 > <b>		
    <td WIDTH=200 > <center> ${user.employee_id.complete_name}</center></td>
    <td WIDTH=200 > <center> ${inv.emp_old_id.complete_name or ''|entity} </center></td>
    %if inv.tipo in ('Comodato','Donacion'): 
    <td WIDTH=200 > <center> ${inv.entidad or ''|entity} </center></b></td>
    %else:
    <td WIDTH=200 > <center> ${inv.emp_new_id.complete_name or ''|entity} </center></b></td>
    %endif
<td WIDTH=200 > <center> ${inv.autorizado_por.complete_name or ''|entity}</center></td>
</tr>
<tr WIDTH=1000 > <b>		
    <td WIDTH=200 > <center></center></b></td>									  
    <td WIDTH=200 > <center> ${inv.emp_old_id.name or ''|entity}</center></td>
    %if inv.tipo in ('Comodato','Donacion'): 
    <td WIDTH=200 > <center></center></b></td>									    
    %else:
    <td WIDTH=200 > <center> ${inv.emp_new_id.name or ''|entity}</center></b></td>
    %endif
<td WIDTH=200 > <center> ${inv.autorizado_por.name or ''|entity}</center></td>
</tr>
</table>
%endfor
</body>
</html>
