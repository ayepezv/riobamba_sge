<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%">
    %if o.tipo2:
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">SOLICITUD DE ${o.tipo2 or  ''} Nro. ${o.code or  ''}</td>
    </tr>
    %else:
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">SOLICITUD DE PERMISO Nro. ${o.code or  ''}</td>
    </tr>
    %endif
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">FECHA SOLICITUD ${o.date_permiso or  ''}</td>
    </tr>
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Funcionario Solicita:</td>
      <td style="font-size:11px" width="42%">${o.employee_id.complete_name or  ''}</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Departamento:</td>
      <td style="font-size:11px" width="42%">${o.employee_id.department_id.name or ''}</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Denominacion/Cargo:</td>
      <td style="font-size:11px" width="42%">${o.employee_id.job_id.name or ''}</td>
    </tr>
    %if o.tipo=='Dias':
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha:</td>
      <td style="font-size:11px" width="42%">Desde: ${o.date or ''} - Hasta: ${o.date_end or ''}</td>
    </tr>
    %else:
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Dia/Hora:</td>
      <td style="font-size:11px" width="42%">
        ${o.date or ''} -
        ${str(o.hora_inicio).split(',')[0]+':'+str(int(str(o.hora_inicio).split(',')[1])*60/100).zfill(2) or ''} -
        ${str(o.hora_fin).split(',')[0]+':'+str(int(str(o.hora_fin).split(',')[1])*60/100).zfill(2) or ''}</td>
    </tr>
    %endif
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Justificacion:</td>
      <td style="font-size:11px" width="42%">${o.name or ''}</td>
    </tr>
    %if o.tipo=='Dias':
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Total Dias</td>
      <td style="font-size:11px" width="42%">${o.total_dias or ''}</td>
    </tr>
    %else:
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Total Horas</td>
      <td style="font-size:11px" width="42%">
        ${str(o.total_horas).split(',')[0]+':'+str(int(str(o.total_horas).split(',')[1])*60/100).zfill(2) or ''}
      </td>
    </tr>
    %endif
  </table>
  <p>
  </p>
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
	  <th>__________________</th>
	  <th>__________________</th>
	  <th>__________________</th>
	  <th>__________________</th>
	</tr>
	<tr style="font-size:11px">
	  <th width="25%">${o.employee_id.complete_name or  ''}</th>
	  <th width="25%">${o.jefe_id.complete_name or  ''}</th>
	  <th width="25%"></th>
	  <th width="25%"></th>
 	</tr>
	<tr style="font-size:11px">
	  <th width="25%">FUNCIONARIO</th>
	  <th width="25%">Director o Jefe de Seccion</th>
	  <th width="25%">Administrador de Gestion de Talento Humano</th>
	  <th width="25%">Alcalde</th>
 	</tr>
  </table>
  %endfor
</html>
