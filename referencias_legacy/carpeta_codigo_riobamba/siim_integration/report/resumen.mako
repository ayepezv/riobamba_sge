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
      <td width="100%" style="font-size:14;text-align:center;">RESUMEN RECAUDACION</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">FECHA:</td>
      <td style="font-size:11px" width="42%">${o.date or ''}</td>
    </tr> 
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
    <thead>
      <tr>
        <th style="font-size:10px" width="20%">CUENTA</th>
        <th style="font-size:10px" width="20%">PARTIDA</th>
        <th style="font-size:10px" width="60%">DESCRIPCION</th>
        <th style="font-size:10px" width="8%">ANIO ANTERIOR</th>
        <th style="font-size:10px" width="8%">ACTUAL</th>
      </tr>
    </thead>
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
	<%
	   a=0
	   actual = 0
	   %>
    %for line in o.recaudacion_ids:
	<%
	   a+=1
	   actual = line.actual_value + line.dia_value
	   %>
    <tr>
      <td width="20%" style="font-size:11px;text-align:left">${line.account_id}</td>
      <td width="20%" style="font-size:11px;text-align:left">${line.partida_id}</td>
      <td width="60%" style="font-size:11px;text-align:left">${line.desc}</td>
      <td width="8%" style="font-size:11px;text-align:right">${line.anterior_value}</td>
      <td width="8%" style="font-size:11px;text-align:right">${actual}</td>
    </tr>
    %endfor      
  </table>
<table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">FORMA DE PAGO</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
      <tr>
        <th style="font-size:11px" width="70%">PAGO</th>
        <th style="font-size:11px" width="30%">VALOR</th>
      </tr>
    </thead>
	<%
	   total_rec = 0
	   %>
    %for line_rec in o.formapago_ids:
	<%
	   total_rec += line_rec.monto
	   %>
    <tr>
      <td width="70%" style="font-size:11px;text-align:left">${line_rec.journal_id.name}</td>
      <td width="30%" style="font-size:11px;text-align:right">${line_rec.monto}</td>
    </tr>
    %endfor      
  </table>
  <table width="100%">
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
      <th width="50%">Creado por</th>
 	</tr>  
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="height:35px">
      <th>__________________</th>
	</tr>
	<tr style="font-size:11px">
      <th width="33%">${user.employee_id.complete_name or ''}</th>
  	</tr>  
  </table>
  %endfor
</html>
