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
      <td width="100%" style="font-size:14;text-align:center;">VALE DE CAJA CHICA Nro. ${o.name or  ''}</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Lugar:</td>
      <td style="font-size:11px" width="42%">${o.lugar_id.name or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha:</td>
      <td style="font-size:11px" width="42%">${o.date or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Solicitado por:</td>
      <td style="font-size:11px" width="42%">${o.solicitud_id.solicita_id.name or ''} - ${o.solicitud_id.solicita_id.complete_name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Unidad:</td>
      <td style="font-size:11px" width="42%">${o.unidad_id.name or ''}</td>
    </tr> 
  </table>
  <p></p>
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:14;text-align:center;"><b>RECIBO DEL ${user.company_id.name}</b></td>	  	  
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:left;">La cantidad de ${o.cantidad} : ${o.letras}</td>	  	  
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:left;">Por concepto de: ${o.solicitud_id.name} ${o.concepto}</td>	  	  
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:left;">Detalle ${o.detalle}</td>	  	  
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:left;">Valor ${o.cantidad}</td>	  	  
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
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
      <th width="50%">RECIBIDO POR</th>
      <th width="50%">CUSTODIO</th>
    </tr>  

  </table>
  %endfor
</html>
