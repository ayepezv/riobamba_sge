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
	  <td width="100%" style="font-size:14;text-align:center;">SOLICITUD DE CAJA CHICA Nro. ${o.name or  ''}</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha:</td>
      <td style="font-size:11px" width="42%">${o.date or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Solicitado por:</td>
      <td style="font-size:11px" width="42%">${o.solicita_id.name or ''} - ${o.solicita_id.complete_name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Departamento:</td>
      <td style="font-size:11px" width="42%">${o.department_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Detalle:</td>
      <td style="font-size:11px" width="42%">${o.desc or ''}</td>
    </tr> 
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="10%">Nro.</th>
        <th style="font-size:11px" width="50%">DETALLE</th>
        <th style="font-size:11px" width="10%">CANTIDAD</th>
        <th style="font-size:11px" width="10%">UNIDAD</th>
	<th style="font-size:11px" width="10%">PRECIO UNITARIO</th>
	<th style="font-size:11px" width="10%">SUBTOTAL</th>
      </tr>
    </thead>
	<%
	   a=0
	   total = 0 
	   %>
    %for line in o.line_ids:
	<%
	   a+=1
	   total += line.subtotal
	   %>
    <tr style="page-break-inside:avoid">
      <td width="10%" style="font-size:11px;text-align:center">${a}</td>
      <td width="50%" style="font-size:11px;text-align:left">${line.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.qty}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.unidad.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.pu}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.subtotal}</td>
    </tr>
    %endfor
    <tr style="page-break-inside:avoid">
      <td width="10%" style="font-size:11px;text-align:center"></td>
      <td width="50%" style="font-size:11px;text-align:left"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${total}</b></td>
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
    <tr style="font-size:11px">
      <th width="33%">SOLICITADO POR</th>
      <th width="33%">VISTO BUENO</th>
      <th width="33%">AUTORIZADO</th>
    </tr>
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th>________________________</th>
      <th>_______________________&nbsp;&nbsp;&nbsp;&nbsp;</th>
      <th>_______________________</th>

    </tr>
    <tr style="font-size:11px">
      <th width="100%"></th>
    </tr>  
    <tr style="font-size:11px">
      <th width="33%">${o.solicita_id.complete_name}</th>
      <th width="33%">${o.aprobador_id.complete_name}</th>
      <th width="33%">DIRECTORA ADMINISTRATIVA</th>
    </tr>  

  </table>
  %endfor
</html>
