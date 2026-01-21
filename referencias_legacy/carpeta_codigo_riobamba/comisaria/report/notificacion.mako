<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
	<%
           n1 = o.notificacion1
	   n2 = o.notificacion2
	   n3 = o.notificacion3
           pred   =  o.predio_id.name
           x='X'
           y='X'
           z='X' 		
	   %>
  <table WIDTH="100%">
	<tr>
	  <td width="100%" style="font-size:14;text-align:center;">REPORTE DE NOTIFICACIONES </td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="16%">Número de Ingreso:</td>
      <td style="font-size:11px" width="42%">${o.name or  ''}</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:11px" width="16%">cliente:</td>
      <td style="font-size:11px" width="42%">${o.cliente_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="16%">Ordenanza:</td>
      <td style="font-size:11px" width="42%">${o.ordenanza_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="16%">Multa:</td>
      <td style="font-size:11px" width="42%">${o.multa_id.name or ''}</td>
    </tr> 
%if pred != None :
    <tr>
      <td style="font-weight: bold;font-size:11px" width="16%">Predio (Clave Catastral):</td>
      <td style="font-size:11px" width="42%">${o.predio_id.name or ''}</td>
    </tr>
%endif	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Dirección:</td>
      <td style="font-size:11px" width="42%">${o.direccion or ''}</td>
    </tr>
    <tr>
%if n1 == True :
      <td style="font-weight: bold;font-size:11px" width="16%">Fecha de la Primera Notificación:</td>

      <td style="font-size:11px" width="16%">${o.fecha or  ''}</td>
%endif
    </tr>

    <tr>
%if n2 == True :
      <td style="font-weight: bold;font-size:11px" width="16%">Fecha de la Segunda Notificación:</td>

      <td style="font-size:11px" width="16%">${o.fecha2 or  ''}</td>
%endif

    </tr>
    <tr>
%if n3 == True :
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha de la Tercera Notificación:</td>

      <td style="font-size:11px" width="12%">${o.fecha3 or  ''}</td>
%endif
    </tr>

    <tr>
%if n1 == True :
      <td style="font-weight: bold;font-size:11px" width="12%">Quien le notificó por primera vez:</td>
      <td style="font-size:11px" width="42%">${o.empleado_id.name or ''} - ${o.empleado_id.complete_name or ''}</td>
%endif
    </tr>

    <tr>
%if n2 == True :
      <td style="font-weight: bold;font-size:11px" width="12%">Quien le notificó por segunda vez:</td>
      <td style="font-size:11px" width="42%">${o.empleado_id2.name or ''} - ${o.empleado_id2.complete_name or ''}</td>
%endif
    </tr>
%if n3 == True :
      <td style="font-weight: bold;font-size:11px" width="12%">Quien le notificó por tercera vez:</td>
      <td style="font-size:11px" width="42%">${o.empleado_id3.name or ''} - ${o.empleado_id3.complete_name or ''}</td>
%endif
    </tr>

    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Observaciones:</td>
      <td style="font-size:11px" width="42%">${o.observaciones or ''}</td>
    </tr>

  </table>
  <table WIDTH="100%">
    <tr>
	  <td width="100%" style="font-weight: bold;font-size:14;text-align:center;">FOTOS </td>
          	  
    </tr>	
  </table>
<!-- td son columnas,   tr son filas-->

  <table WIDTH="100%"  >
    <tr>
	  <td width="50%" style="font-size:14;text-align:right;">
           PRIMERA NOTIFICACION &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
          <td width="50%" style="font-size:14;text-align:left;">
           &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;SEGUNDA NOTIFICACION </td>	  
    </tr>
    <tr>
          <td width="50%"  style="font-size:14px;text-align:right">
               ${helper.embed_image('png', o.foto,260,180) | n}  </td>	  
          <td width="50%"  style="font-size:14px;text-align:left"> 
              ${helper.embed_image('png', o.foto1,260,180) | n} </td>	  
    </tr>	

  </table>
  <table WIDTH="100%">
     <tr>
	  <td width="100%" style="font-size:14;text-align:center;">TERCERA NOTIFICACION </td>
          	  
     </tr>
     <tr> 
          <td width="10%" style="font-size:11px;text-align:center"> ${helper.embed_image('png', o.foto2,260,180) | n} 
              ${helper.embed_image('png', o.foto3,260,180) | n}</td>	  	  
    </tr>	
  </table>
 
  
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>

    <tr style="height:35px">
      <th>__________________________</th>
      <th>__________________________</th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%"></th>
    </tr>  
    <tr style="font-size:11px">
      <th width="50%">${o.supervisor_id.complete_name}</th>
      <th width="50%">${o.empleado_id3.complete_name}</th>
    </tr>  
    <tr style="font-weight: bold;font-size:11px">
      <th width="50%">SUPERVISOR MUNICIPAL</th>
      <th width="50%">POLICIA MUNICIPAL</th>
    </tr>  

  </table>
  %endfor
</html>
