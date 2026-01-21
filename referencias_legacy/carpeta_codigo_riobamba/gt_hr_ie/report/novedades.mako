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
      <td width="100%" style="font-size:14;text-align:center;">REPORTE DE NOVEDADES</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" > 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Concepto:</td>
      <td style="font-size:11px" width="42%">${o.name.name or  ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Periodo:</td>
      <td style="font-size:11px" width="42%">${o.period_id.name or  ''}</td>
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="65%">EMPLEADO</th>
        <th style="font-size:11px" width="10%">VALOR DESCONTADO</th>
        <th style="font-size:11px" width="10%">VALOR CARGADO</th>
        <th style="font-size:11px" width="10%">SALDO</th>
      </tr>
    </thead>
	<%
	   total=totaldes=totalsaldo=a=0
	   %>
    %for line in o.line_ids:
	<%
	   a+=1
	   total += line.valor
	   aux_saldo = 0
	   if line.valor_original>0:
	       aux_saldo = line.valor_original - line.valor
	   else:
       	       totaldes += line.valor
	   endif
	   totalsaldo += aux_saldo
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="65%" style="font-size:11px;text-align:left">${line.employee_id.name} - ${line.employee_id.complete_name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.valor}</td>
      %if line.valor_original>0:
      <td width="10%" style="font-size:11px;text-align:right">${line.valor_original}</td>
      %else:
      <td width="10%" style="font-size:11px;text-align:right">${line.valor}</td>
      %endif
      <td width="10%" style="font-size:11px;text-align:right">${aux_saldo}</td>
    </tr>
    %endfor      
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%"></th>
        <th style="font-size:11px" width="65%">TOTAL</th>
        <th style="font-size:11px" width="10%">${total}</th>
        <th style="font-size:11px" width="10%">${totaldes}</th>
        <th style="font-size:11px" width="10%">${totalsaldo}</th>
      </tr>
    </thead>
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
      <th width="50%">Creado por</th>
      <th width="50%">Autorizado</th>
 	</tr>  
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="height:35px">
      <th>__________________</th>
      <th>__________________</th>
	</tr>
	<tr style="font-size:11px">
      <th width="33%">${user.employee_id.complete_name or ''}</th>
      <th width="33%">${user.context_department_id.manager_id.complete_name or ''}</th>
	</tr>  
  </table>
  %endfor
</html>
