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
	  <td width="100%" style="font-size:14;text-align:center;">DEPRECIACION ACUMULADA ${o.year_id.name or  ''}</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="17%">Nro.</th>
        <th style="font-size:11px" width="47%">CATEGORIA/CUENTA</th>
        <th style="font-size:11px" width="18%"># ACTIVOS</th>
        <th style="font-size:11px" width="18%">TOTAL</th>
      </tr>
    </thead>
	<%
	   a=total=0
	   %>
    %for line in o.line_ids:
	<%
	   a+=1
	   total+=line.total
	   %>
    <tr style="page-break-inside:avoid">
      <td width="17%" style="font-size:11px;text-align:center">${a}</td>
      <td width="47%" style="font-size:11px;text-align:left">${line.category_id.code} ${line.category_id.name}</td>
      <td width="18%" style="font-size:11px;text-align:right">${line.num}</td>
      <td width="18%" style="font-size:11px;text-align:right">${line.total}</td>
    </tr>
    %endfor      
    <tr style="page-break-inside:avoid">
      <td width="17%" style="font-size:11px;text-align:center">${}</td>
      <td width="47%" style="font-size:11px;text-align:left">${}</td>
      <td width="18%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
      <td width="18%" style="font-size:11px;text-align:right"><b>${'{:,.2f}'.format(total)}</b></td>
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
      <th width="33%">Creado por</th>
      <th width="33%">Autorizado</th>
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
	  <th width="33%">${user.context_department_id.coordinador_id.complete_name or ''}</th>
	</tr>  
  </table>
  %endfor
</html>
