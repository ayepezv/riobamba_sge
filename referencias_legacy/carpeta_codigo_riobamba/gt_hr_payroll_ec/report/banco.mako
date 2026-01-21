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
      <td width="100%" style="font-size:14;text-align:center;">DETALLE CUENTAS BANCO PAGO</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
    <thead>
      <tr>
        <th style="font-size:9px" width="5%">#</th>
        <th style="font-size:9px" width="40%">FUNCIONARIO</th>
        <th style="font-size:9px" width="35%">BANCO</th>
        <th style="font-size:9px" width="15%">CUENTA</th>
        <th style="font-size:9px" width="5%">MONTO</th>
      </tr>
    </thead>
    <% a=total=0
       %>
    %for line in o.slip_ids:
    <% 
       a+=1
       total += line.net
       %>
    <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
      <tr >
	<td width="5%" style="font-size:9px;text-align:left">${ a }</td>
	<td width="40%" style="font-size:9px;text-align:left">${line.employee_id.name} - ${line.employee_id.complete_name}</td>
	<td width="35%" style="font-size:9px;text-align:left">${get_banco(line)}</td>
	<td width="15%" style="font-size:9px;text-align:right">${get_cuenta(line)}</td>
	<td width="5%" style="font-size:9px;text-align:right">${line.net}</td>
    </tr>
      </table>
    %endfor      
  </table>
  <table WIDTH="100%">
    <tr>
      <td width="90%" style="font-size:14;text-align:center;"><b>TOTAL</b></td>
      <td width="10%" style="font-size:14;text-align:center;"><b>${total}</b></td>
    </tr>	
  </table>
  %endfor
</html>
