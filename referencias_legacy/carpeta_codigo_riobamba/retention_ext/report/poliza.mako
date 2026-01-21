<!DOCTYPE HTML>
<html>
<head>
  <style type="text/css">
    .line {
    border-bottom:1pt solid black;
    }
  </style>
</head>
<body>
%for o in objects:
  <%import time%>
  <thead>
    <h4 colspan="2" style="text-align:right">OFICION NRO. ${ o.oficio }</h3>
    <h4 colspan="2" style="text-align:right">${user.company_id.city or ''|entity} , ${time.strftime('%d-%m-%Y') or ''|entity}</h3>
  </thead>
  <tbody>
    <br>
    <br>
  <p>
    Se&ntilde;ores.
    <br>
    ${ o.aseguradora_id.name }
    <br>
    Presente.-
  </p>  
  <br>
  <br>
    <p style="text-align:justify">Para los fines pertinentes comunico a usted que el/la ${ o.partner_id.ced_ruc } - ${ o.partner_id.name }, hasta la presente fecha no ha procedido a hacer la entrega y recepci&oacute;n del contrato suscrito <b>${ o.obra_id.name } </b>, compromiso adquirido con el ${user.company_id.partner_id.name or ''|entity}, por lo tanto solicito hacer la renovaci&oacute;n de la <b>poliza Nro. ${o.numero}</b> de ${o.name.name}, por un per&iacute;odo de ${o.dias_renova} d&iacute;as calendario a partir de la fecha que caduca la p&oacute;liza <b>${o.fecha_fin}</b></p>
    <br>
<br>
<p>Por la favorable acogida que sabr&aacute; dar al presente, anticipo mis agradecimientos</p>
<br>
<br>
<p>Atentamente</p>
<br>
<br>
<p>
    _______________________________
  <br>
   ${ user.employee_id.complete_name }

%endfor
</body>
</html>
