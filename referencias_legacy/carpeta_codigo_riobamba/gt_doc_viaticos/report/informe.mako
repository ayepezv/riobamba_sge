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
	  <td width="100%" style="font-size:14;text-align:center;">INFORME DE LICENCIA CON REMUNERACION</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="42%">Nro. SOLICITUD LICENCIA CON REMUNERACION</td>
      <td style="font-size:11px" width="12%">${o.name or  ''}</td>
      <td style="font-weight: bold;font-size:11px" width="42%">FECHA INFORME</td>
      <td style="font-size:11px" width="12%">${ actualizar_fecha(o.fecha_informe) or  ''}</td>
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >
    <tr>
      <td style="font-weight: bold;font-size:11px" width="100%">SELECCIONE LO QUE REQUIERE SOLICITAR</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:10px" width="100%">
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
      <td width="100%" style="font-size:11;text-align:center;">DATOS GENERALES</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:10px" width="50%">APELLIDOS NOMBRES DEL SERVIDOR</td>
      <td style="font-weight: bold;font-size:10px" width="50%">PUESTO</td>
    </tr>
    <tr>
      <td style="font-size:10px" width="50%">${o.employee_id.complete_name or ''}</td>      
      <td style="font-size:10px" width="50%">${o.employee_id.job_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:10px" width="50%">CIUDAD - PROVINCIA DE LA COMISION</td>
      <td style="font-weight: bold;font-size:10px" width="50%">NOMBRE DE LA UNIDAD DEL SERVIDOR</td>
    </tr>
    <tr>
      <td style="font-size:10px" width="50%">${o.ciudad_comision.name or ''} - ${o.ciudad_comision.state_id.name or ''}</td>
      <td style="font-size:10px" width="50%">${o.employee_id.department_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:10px" width="50%">FECHA HORA SALIDA</td>
      <td style="font-weight: bold;font-size:10px" width="50%">FECHA HORA LLEGADA</td>
    </tr>
    <tr>
      <td style="font-size:10px" width="50%">${ actualizar_fecha(o.fecha_salida)}</td>
      <td style="font-size:10px" width="50%">${ actualizar_fecha(o.fecha_llegada)}</td>
    </tr> 
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">SERVIDORES QUE INTEGRAN LA COMISION</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:10px" width="12%">${o.unidad_miembros or ''}</td>
    </tr> 
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <tr>
      <td width="100%" style="font-size:11;text-align:center;">INFORME DE ACTIVIDADES Y PRODUCTOS ALCANZADOS</td>	  	  
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:10px" width="100%">${o.actividades_informe}</td>
    <tr>
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <td WIDTH="50%">
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
	<tr>
	  <td>ITINERARIO</td>
	  <td>SALIDA</td>
	  <td>LLEGADA</td>
	</tr>
	<tr>
	  <td>FECHA dd-mm-aaaa</td>
	  <td>${ get_fecha(o.fecha_salida)}</td>
	  <td>${ get_fecha(o.fecha_llegada)}</td>
	</tr>
	<tr>
	  <td>HORA hh:mm</td>
	  <td>${ get_hora(o.fecha_salida)}</td>
	  <td>${ get_hora(o.fecha_llegada)}</td>
	</tr>
	<tr>
	  <td>Hora Inicio Labores el dia de retorno</td>
	  <td>${ float_time_convert(o.hora_inicio_actividades) }</td>
	</tr>
      </table>
    </td>
    <td WIDTH="50%">
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
	<tr>
	  <p>NOTA: Estos datos se refieren al tiempo efectivamente utilizado en la comision, desde la salida del lugar de residencia o trabajo habituales o del cumplimiento de licencia segun sea el caso, hasta su llegada de estos sitios</p>
	</tr>
      </table>
    </td>
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="100%" style="font-size:11;text-align:center;">TRANSPORTE</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:10px" width="15%">TIPO TRANSPORTE</th>
        <th style="font-size:10px" width="25%">NOMBRE TRANSPORTE</th>
        <th style="font-size:10px" width="30%">RUTA</th>
        <th style="font-size:10px" width="15%">SALIDA</th>
        <th style="font-size:10px" width="15%">LLEGADA</th>
      </tr>
    </thead>
    %for line in o.destinos_solicitud:
    <tr style="page-break-inside:avoid">
      <td width="15%" style="font-size:11px;text-align:center">${line.tipo}</td>
      <td width="25%" style="font-size:11px;text-align:center">${line.tipo_nombre}</td>
      <td width="30%" style="font-size:11px;text-align:center">${line.ruta_id.name}</td>
      <td width="15%" style="font-size:11px;text-align:center">${ actualizar_fecha(line.fecha_salida)}</td>
      <td width="15%" style="font-size:11px;text-align:center">${ actualizar_fecha(line.fecha_llegada)}</td>
    </tr>
    %endfor 
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="100%" style="font-size:10;text-align:center;">NOTA: En caso de haber utilizado transporte publico aereo o terrestre, se debera adjuntar obligatoriamente los pasajes a bordo o boletos, de acuerdo a lo que establece el articulo 19 del reglamento para pago de viaticos, subsistencias y movilizacion</td>	  	  
    </tr>
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="100%" style="font-size:11;text-align:center;">OBSERVACIONES</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="100%" style="font-size:10;text-align:center;">${o.observaciones}</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="100%" style="font-size:11;text-align:center;">DATOS PARA TRANSFERENCIA</td>	  	  
    </tr>
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td width="25%" style="font-size:10;text-align:center;">TIPO CUENTA</td>
      <td width="25%" style="font-size:10;text-align:center;">NRO. CUENTA</td>
      <td width="50%" style="font-size:10;text-align:center;">NOMBRE BANCO</td>
    </tr>
    <tr>
      <td width="25%" style="font-size:10;text-align:center;">
	%if o.bank_id.type_cta=='aho':
	AHORROS
	%else:
	CORRIENTE
	%endif
      </td>
      <td width="25%" style="font-size:10;text-align:center;">${o.bank_id.acc_number}</td>
      <td width="50%" style="font-size:10;text-align:center;">${o.bank_id.bank.name}</td>
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="font-size:10px" width="50%">NOTA: El presente informe debera presentarse dentro del termino maximo de 4 dias de cumplida la licencia, caso contrario la liquidacion se demorara e incluso de no presentarlo tendria que restituir los valores pagados. Cuando la licencia sea superior al numero de horas o dias autorizados, se debera adjuntar la autorizacion por escrito de la maxima autoridad o delegado</tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="font-size:10px">
      <th width="33%">FIRMA DEL SERVIDOR COMISIONADO</th>
      <th width="33%">JEFE INMEDIATO DEL RESPONSABLE DE UNIDAD</th>
      <th width="33%">MAXIMA AUTORIDAD</th>
    </tr>  
    <tr style="height:35px">
      <th>____________________</th>
      <th>____________________</th>
      <th>____________________</th>
    </tr>
    <tr style="font-size:10px">
      <th>${o.employee_id.complete_name}</th>
      <th>${o.aprobado_id.complete_name or ''}</th>
      <th></th>
    </tr>
  </table>
  %endfor
</html>
