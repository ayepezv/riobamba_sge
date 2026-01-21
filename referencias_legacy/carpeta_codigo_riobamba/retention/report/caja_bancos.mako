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
	  <td width="100%" style="font-size:14;text-align:center;">TRASLADO DEL SALDO DE CAJA BANCOS A PRESUPUESTO ${o.name.name or  ''}</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">PARTIDA:</td>
      <td style="font-size:11px" width="42%">${o.budget_id.budget_post_id.code or  ''} - ${o.budget_id.budget_post_id.name or  ''}</td>
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="15%">Nro.</th>
        <th style="font-size:11px" width="70%">CUENTA</th>
        <th style="font-size:11px" width="15%">SALDO A TRANSFERIR</th>
      </tr>
    </thead>
	<%
	   total = 0
	   a=0
	   %>
    %for line in o.line_ids:
	<%
	   total += line.monto
	   a+=1
	   %>
    <tr style="page-break-inside:avoid">
      <td width="15%" style="font-size:11px;text-align:center">${a}</td>
      <td width="70%" style="font-size:11px;text-align:left">${line.account_id.code} - ${line.account_id.name}</td>
      <td width="15%" style="font-size:11px;text-align:right">${line.monto}</td>
    </tr>
    %endfor      
    <tr style="page-break-inside:avoid">
      <td width="15%" style="font-size:11px;text-align:center"></td>
      <td width="70%" style="font-size:11px;text-align:left">TOTAL RECAUDADO</td>
      <td width="15%" style="font-size:11px;text-align:right">${total}</td>
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
      <th width="100%">Creado por</th>
 	</tr>  
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="height:35px">
      <th>________________________</th>
	</tr>
	<tr style="font-size:11px">
	  <th width="100%">${user.employee_id.complete_name or ''}</th>
	</tr>  
  </table>
  %endfor
</html>
