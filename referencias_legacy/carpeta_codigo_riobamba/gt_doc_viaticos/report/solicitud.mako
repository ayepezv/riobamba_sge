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
	  <td width="100%" style="font-size:14;text-align:center;">SOLICITUD DE LICENCIA CON REMUNERACION</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="42%">Nro. SOLICITUD LICENCIA CON REMUNERACION</td>
      <td style="font-size:11px" width="12%">${o.name or  ''}</td>
      <td style="font-weight: bold;font-size:11px" width="42%">FECHA SOLICITUD</td>
      <td style="font-size:11px" width="12%">${o.fecha_solicitud or  ''}</td>
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >
    <tr>
      <td style="font-weight: bold;font-size:11px" width="100%">SELECCIONE LO QUE REQUIERE SOLICITAR</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:11px" width="100%">
	%if o.is_viatico:
	VIATICOS ____X____
        %else:
	VIATICOS _________
	%endif
	%if o.is_movilizacion:
	MOVILIZACIONES ____X____
	%else:
	MOVILIZACIONES _________
	%endif
	%if o.is_subsistencia:
	SUBSISTENCIAS ____X____
	%else:
	SUBSISTENCIAS _________
	%endif
	%if o.is_alimentacion:
	ALIMENTACION ____X____   
	%else:
	ALIMENTACION _________   
	%endif
      </td>
    </tr> 
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">DATOS GENERALES</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="50%">APELLIDOS NOMBRES DEL SERVIDOR</td>
      <td style="font-weight: bold;font-size:11px" width="50%">PUESTO</td>
    </tr>
    <tr>
      <td style="font-size:11px" width="50%">${o.employee_id.complete_name or ''}</td>      
      <td style="font-size:11px" width="50%">${o.employee_id.job_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="50%">CIUDAD - PROVINCIA DE LA COMISION</td>
      <td style="font-weight: bold;font-size:11px" width="50%">NOMBRE DE LA UNIDAD DEL SERVIDOR</td>
    </tr>
    <tr>
      <td style="font-size:11px" width="50%">${o.ciudad_comision.name or ''} - ${o.ciudad_comision.state_id.name or ''}</td>
      <td style="font-size:11px" width="50%">${o.employee_id.department_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="50%">FECHA HORA SALIDA</td>
      <td style="font-weight: bold;font-size:11px" width="50%">FECHA HORA LLEGADA</td>
    </tr>
    <tr>
      <td style="font-size:11px" width="50%">${ actualizar_fecha(o.fecha_salida) }</td>
      <td style="font-size:11px" width="50%">${ actualizar_fecha(o.fecha_llegada) }</td>
    </tr> 
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">SERVIDORES QUE INTEGRAN LA COMISION</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">${o.unidad_miembros or ''}</td>
    </tr> 
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">DESCRIPCION DE LAS ACTIVIDADES A EJECUTARSE</td>	  	  
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="100%">${o.actividades_solicitud}</td>
    <tr>
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">TRANSPORTE</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="15%">TIPO TRANSPORTE</th>
        <th style="font-size:11px" width="25%">NOMBRE TRANSPORTE</th>
        <th style="font-size:11px" width="30%">RUTA</th>
        <th style="font-size:11px" width="15%">SALIDA</th>
        <th style="font-size:11px" width="15%">LLEGADA</th>
      </tr>
    </thead>
    %for line in o.destinos_solicitud:
    <tr style="page-break-inside:avoid">
      <td width="15%" style="font-size:11px;text-align:center">${line.tipo}</td>
      <td width="25%" style="font-size:11px;text-align:center">${line.tipo_nombre}</td>
      <td width="30%" style="font-size:11px;text-align:center">${line.ruta_id.name}</td>
      <td width="15%" style="font-size:11px;text-align:center">${ actualizar_fecha(line.fecha_salida) }</td>
      <td width="15%" style="font-size:11px;text-align:center">${ actualizar_fecha(line.fecha_llegada) }</td>
    </tr>
    %endfor 
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">DATOS PARA TRANSFERENCIA</td>	  	  
    </tr>
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="25%" style="font-size:14;text-align:center;">TIPO CUENTA</td>
      <td width="25%" style="font-size:14;text-align:center;">NRO. CUENTA</td>
      <td width="50%" style="font-size:14;text-align:center;">NOMBRE BANCO</td>
    </tr>
    <tr>
      <td width="25%" style="font-size:14;text-align:center;">
	%if o.bank_id.type_cta=='aho':
	AHORROS
	%else:
	CORRIENTE
	%endif
      </td>
      <td width="25%" style="font-size:14;text-align:center;">${o.bank_id.acc_number}</td>
      <td width="50%" style="font-size:14;text-align:center;">${o.bank_id.bank.name}</td>
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="font-size:11px">
      <th width="50%">FIRMA DEL SERVIDOR SOLICITANTE</th>
      <th width="50%">FIRMA RESPONSABLE UNIDAD SOLICITANTE</th>
    </tr>  
    <br>
    <br>
    <tr style="height:35px">
      <th>____________________</th>
      <th>____________________</th>
    </tr>
    <tr style="height:12px">
      <th>${o.employee_id.complete_name}</th>
      <th>${o.autorizado_id.complete_name or ''}</th>
    </tr>
    <tr style="font-size:11px">
      <th width="50%">JEFE INMEDIATO DEL RESPONSABLE DE LA UNIDAD</th>
      <th width="50%">MAXIMA AUTORIDAD O DELEGADO</th>
    </tr>  
    <br>
    <br>
    <tr style="height:35px">
      <th>____________________</th>
      <th>____________________</th>
    </tr>
    <tr style="height:12px">
      <th>${o.aprobado_id.complete_name or ''}</th>
      <th>ALCALDE</th>
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr>
      <td style="font-size:6px">NOTA: Esta solicitud debera ser presentada para su autorizacion, con por lo menos 6 dias de anticipacion a la licencia.
      <UL type = circle>
	<LI>De no existir disponibilidad presupuestaria tanto la solicitud como la autorizacion quedaran insubsistentes
	<LI>El informe de licencia con remuneracion debera presentarse dentro del termino maximo de 4 dias de cumplida la licencia
	<LI>Esta prohibido conceder licencias para el cumplimiento de servicios institucionales durante los dias de descanso obligatorio, con excepcion de las maximas autoridades o de casos excepcionales debidamente justificados por la maxima autoridad o su delegado
	<LI>Perú
      </UL>
</td>
    </tr>
  </table>
  %endfor
</html>
