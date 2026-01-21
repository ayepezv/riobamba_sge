<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
	
  %for inv in objects :
  <H1><center>GESTIÓN ADMINISTRATIVA - ADMINISTRACIÓN DE BIENES</center></H1>
  <H2><center>TRASPASO DE BIENES DE LARGA DURACION Nº ${inv.name or ''|entity} </center></H2>
  <H2><center>${inv.tipo or ''|entity} </center></H2>
  <table WIDTH="100%"  rules="none" cellpadding="2" cellspacing="0" style="font-size:12px">
    <tr WIDTH=1000>
      <td WIDTH=150 style="text-align:left;font-size:12px;page-break-inside:avoid"> Custodio que Entrega:</td>
      <td WIDTH=850 style="text-align:left;font-size:12px;page-break-inside:avoid">${inv.emp_old_id.complete_name or ''|entity}</td>	
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 style="text-align:left;font-size:12px;page-break-inside:avoid"> Custodio que Recibe:</td>
      %if inv.tipo in ('Comodato','Donacion'): 
      <td WIDTH=850 style="text-align:left;font-size:12px;page-break-inside:avoid">${inv.entidad or ''|entity}</td>	
      %else:
      <td WIDTH=850 style="text-align:left;font-size:12px;page-break-inside:avoid">${inv.emp_new_id.complete_name or ''|entity}</td>	
      %endif
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 style="text-align:left;font-size:12px;page-break-inside:avoid"> Autorizado por:</td>
      <td WIDTH=850 style="text-align:left;font-size:12px;page-break-inside:avoid">${inv.autorizado_por.complete_name or ''|entity}</td>
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 style="text-align:left;font-size:12px;page-break-inside:avoid"> Documento</td>
      <td WIDTH=850 style="text-align:left;font-size:12px;page-break-inside:avoid">${inv.document_name or ''|entity}</td>	
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 style="text-align:left;font-size:12px;page-break-inside:avoid"> Detalle</td>
      <td WIDTH=850 style="text-align:left;font-size:12px;page-break-inside:avoid">${inv.detail or ''|entity}</td>	
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=150 style="text-align:left;font-size:12px;page-break-inside:avoid"> Por un total de:</td>
      <td WIDTH=850 style="text-align:left;font-size:12px;page-break-inside:avoid">${inv.valor_total or ''|entity}</td>	
    </tr>
  </table>
  <br>
  <br>
  <table WIDTH=1000 style="font-size:14px">
    <tr WIDTH=1000>
      <td WIDTH=1000 style="font-size:14px;text-align:justify"> En el Cant&oacute;n de ${user.company_id.city or ''|entity}, Provincia del ${user.company_id.state_id.name or ''|entity}, el ${inv.date or ''|entity}, en las oficinas de ${user.context_department_id.name or ''|entity}, de el ${user.company_id.name or ''|entity}, se re&uacute;nen por una parte ${inv.emp_old_id.complete_name or ''|entity}, y por otra, 
%if inv.tipo in ('Donacion','Comodato'):
${inv.entidad or ''|entity}
%else:
${inv.emp_new_id.complete_name or ''|entity}
%endif
, con el fin de realizar la entrega recepci&oacute;n de los bienes que se detallan a continuaci&oacute;n, conforme lo indica el Art. 20 del Reglamento General para la Administración, Utilización, Manejo y Control de los Bienes e Inventarios del Sector Público.</td>		
	</table>
  <br>
  <br>
  <table WIDTH=1000 style="font-size:14px" rules="none" border="1">	
    <tr WIDTH=1000 > <b>		
	<td width="30%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">C&oacute;digo del Bien</td>
	<td width="45%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">Descripci&oacute;n</b></td>
<td width="15%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid" >N&uacute;mero Serie</td>
<td width="10%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">Valor</td>
</tr>
</table>
%for activo in inv.transfer_ids:
<table WIDTH=1000 style="font-size:14px" border="1" cellpadding="2" cellspacing="0">	
  %if activo.selected:
  <tr WIDTH=1000 style="page-break-inside:avoid" border="1" cellpadding="2" cellspacing="0"> <b>		
      <td width="30%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">${activo.asset_id.code or ''|entity}</td>
      <td width="45%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">${activo.asset_id.name or ''|entity}</b></td>
      <td width="15%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">${activo.asset_id.serial_number or ''|entity}</td>
      <td width="10%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">${activo.asset_id.purchase_value or ''|entity}</td>
</tr>
%endif
</table>	
%endfor
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
<table WIDTH=1000 style="font-size:14px">	
  <tr WIDTH=1000 style="page-break-inside:avoid"> <b>		
      <td WIDTH=250 > <center> ELABORADO POR</center></td>
      <td WIDTH=250 > <center> ENTREGUE CONFORME</center></td>
      <td WIDTH=250 > <center> RECIBI CONFORME</center></b></td>
<td WIDTH=250 > <center> AUTORIZADO</center></td>
</tr>
<tr WIDTH=1000 > <b>
    <td WIDTH=250 > <center> ${inv.created_id.employee_id.complete_name or ''|entity}</center></td>
    <td WIDTH=250 > <center> ${inv.emp_old_id.complete_name or ''|entity}</center></td>
    %if inv.tipo in ('Donacion','Comodato'):
    <td WIDTH=250 > <center> ${inv.entidad or ''|entity}</center></b></td>
%else:
<td WIDTH=250 > <center> ${inv.emp_new_id.complete_name or ''|entity}</center></b></td>
%endif
<td WIDTH=250 > <center> ${inv.autorizado_por.complete_name or ''|entity}</center></td>
</tr>
</table>
%endfor
</body>
</html>
