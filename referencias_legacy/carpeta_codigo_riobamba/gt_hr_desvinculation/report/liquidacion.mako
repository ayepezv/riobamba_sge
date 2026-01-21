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
	  <td width="100%" style="font-size:14;text-align:center;">LIQUIDACION Nro. ${o.name or  ''}</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Fecha Liquidacion:</td>
      <td style="font-size:11px" width="42%">${o.date or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Funcionario:</td>
      <td style="font-size:11px" width="42%">${o.contract_id.employee_id.name or ''} - ${o.contract_id.employee_id.complete_name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Motivo Salida:</td>
      <td style="font-size:11px" width="42%">${o.salida_id.name or  ''} - ${o.description or  ''}</td>
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="70%">RUBRO</th>
        <th style="font-size:11px" width="25%">VALOR</th>
      </tr>
    </thead>
	<%
	   a=0
	   total=0
	   %>
    %for line in o.line_ids:
	<%
	   a+=1
	   total+=line.amount
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="70%" style="font-size:11px;text-align:left">${line.salary_rule_id.name}</td>
      <td width="25%" style="font-size:11px;text-align:right">${line.amount}</td>
    </tr>
    %endfor      
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center"></td>
      <td width="70%" style="font-size:11px;text-align:right"><b>TOTAL LIQUIDACION</b></td>
      <td width="25%" style="font-size:11px;text-align:right"><b>${total}</b></td>
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="font-size:11px">
      <th width="33%">Creado por:</th>
      <th width="33%">Autorizado Por:</th>
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
	  <th width="33%">${o.create_user_id.employee_id.complete_name or ''}</th>
	  <th width="33%">${o.create_user_id.context_department_id.manager_id.complete_name or ''}</th>
	</tr>  
  </table>
  %endfor
</html>
