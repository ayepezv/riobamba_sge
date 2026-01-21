<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr>
      <td width="100%" style="font-size:38;text-align:center;"><b>CERTIFICADO DE TRABAJO</b></td>	  	  
    </tr>	

    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
	<tr>
	  <td width="100%" style="font-size:28;text-align:center;"><b>A QUIEN INTERESE:</b></td>	  	  
	</tr>	
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </table>
  <table WIDTH=1000 style="font-size:20px;text-align:justify">
    <tr WIDTH=1000>
      <td WIDTH=1000 >El suscrito, ${user.context_department_id.coordinador_id.complete_name or ''} - ${user.context_department_id.coordinador_id.job_id.name or ''} del ${user.company_id.name or ''|entity}
<b>CERTIFICA</b> 
Que el/la funcionario(a) <b>${o.employee_id.complete_name or ''|entity}</b> portador de la c&eacute;dula de ciudadan&iacute;a Nro. <b>${o.employee_id.name or ''|entity}</b>, 
%if o.activo:
labora
%else:
labor&oacute;
%endif
en esta instituci&oacute;n municipal desde el <b>${o.date_start or ''|entity}</b> 
%if not o.activo:
hasta <b>${o.date_end or ''|entity}</b> 
%endif
con el cargo de <b>${o.job_id.name or ''|entity}</b> percibiendo una remuneraci&oacute;n mensual unificada de <b>${o.wage or ''|entity}</b> d&oacute;lares americanos.</td>
    </tr>
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr WIDTH=1000>
      <td WIDTH=1000 > Es todo cuanto puedo certificar en honor a la verdad y me remito a los archivos en caso necesario.</td>
    </tr>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </table>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
	<tr style="height:35px">
	  <th></th>
	  <th></th>
	  <th></th>
	</tr>
	<tr style="height:35px">
	  <th>_____________________________</th>
	</tr>
	<tr style="font-size:16px">
	  <th width="100%">${user.context_department_id.coordinador_id.complete_name or ''}</th>
	</tr>  
	<tr style="font-size:16px">
	  <th width="100%">${user.context_department_id.coordinador_id.job_id.name or ''}</th>
	</tr>  
  </table>
  %endfor
</html>
