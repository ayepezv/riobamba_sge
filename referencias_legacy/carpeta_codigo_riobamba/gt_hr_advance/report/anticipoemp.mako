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
      <td width="100%" style="font-size:14;text-align:center;">REPORTE DE ANTICIPOS Y SALDOS DE EMPLEADOS</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="10%">Nro.</th>
        <th style="font-size:11px" width="50%">EMPLEADO</th>
        <th style="font-size:11px" width="10%">MONTO ANTICIPO</th>
        <th style="font-size:11px" width="10%">PAGADO</th>
        <th style="font-size:11px" width="10%">SALDO</th>
      </tr>
    </thead>
	<%
	   total=totalp=totals=a=0
	   %>
    %for line in o.line_ids:
	<%
	   a+=1
	   total += line.monto
	   totalp += line.pagado
	   totals += line.saldo
	   %>
    <tr style="page-break-inside:avoid">
      <td width="10%" style="font-size:11px;text-align:center">${a}</td>
      <td width="50%" style="font-size:11px;text-align:left">${line.employee_id.name} - ${line.employee_id.complete_name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.monto}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.pagado}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.saldo}</td>
    </tr>
    %endfor      
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="10%"></th>
        <th style="font-size:11px" width="50%">TOTAL</th>
        <th style="font-size:11px" width="10%">${total}</th>
	<th style="font-size:11px" width="10%">${totalp}</th>
	<th style="font-size:11px" width="10%">${totals}</th>
      </tr>
    </thead>
  </table>
  %endfor
</html>
