<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%">
	<tr>
	  <td style="font-size:18;text-align:center;"><b>CERTIFICADO DE NO TENER BIENES</b></td>	  	  
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
   <table WIDTH="100%" border="0" cellpadding="2" bordercolor="#000000" style="font-size:14px;text-align:justify;">
     <tr>
       <td WIDTH=1000 >Quien suscribe, luego de revisar los inventarios de bienes de larga duraci&oacute;n y bienes de control administrativo que se encuentran bajo mi responsabilidad.
	 <b>CERTIFICA</b> 
	 Que el/la servidor(a) <b>${o.employee_id.complete_name or ''|entity}</b> con cedula de identidad Nro. <b>${o.employee_id.name or ''|entity}</b>, cargo <b>${o.employee_id.job_id.name or ''|entity}</b> del departamento <b>${o.employee_id.department_id.name or ''|entity}</b>, No tiene bienes pendientes de entrega al subproceso ${user.employee_id.department_id.name or ''}.</td>
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
    <tr>
      <td>
	<%
	   import time
	   aux = time.strftime('%Y-%m-%d')
	   %>
	${user.company_id.city or ''|entity} - ${aux} 
      </td>
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
	<tr style="height:35px">
	  <th></th>
	  <th></th>
	  <th></th>
	</tr>
	<tr style="height:35px">
	  <th>_____________________________</th>
	</tr>
	<tr style="font-size:11px">
	  <th width="33%">${user.context_department_id.coordinador_id.complete_name or ''}</th>
	</tr>  
	<tr style="font-size:11px">
	  <th width="33%">${user.context_department_id.coordinador_id.job_id.name or ''}</th>
	</tr>  
  </table>
  %endfor
</html>
