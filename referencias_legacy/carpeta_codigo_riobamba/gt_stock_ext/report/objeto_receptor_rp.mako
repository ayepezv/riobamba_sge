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
      <td width="100%" style="font-size:14;text-align:center;">MOVIMIENTOS OBJETO RECEPTOR</td>	  	  
    </tr>	
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">Desde: ${o.date_start} - Hasta: ${o.date_end}</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">NUM</th>
        <th style="font-size:11px" width="10%">FECHA</th>
        <th style="font-size:11px" width="20%">PRODUCTO</th>
        <th style="font-size:11px" width="10%">DOCUMENTO</th>
        <th style="font-size:11px" width="25%">SOLICITADO POR</th>
        <th style="font-size:11px" width="10%">CANTIDAD</th>
        <th style="font-size:11px" width="10%">VALOR</th>
        <th style="font-size:11px" width="10%">TOTAL</th>
      </tr>
    </thead>
    <%
       total=0
       num = 0
       %>
    %for line in o.line_ids:
	<%
	   num+=1
	   total+=line.total
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${num}</td>
      <td width="10%" style="font-size:11px;text-align:left">${line.date}</td>
      <td width="20%" style="font-size:11px;text-align:left">${line.product_id.default_code} - ${line.product_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:left">${line.documento}</td>
      <td width="20%" style="font-size:11px;text-align:left">${line.solicitant_id.complete_name}</td>
      <td width="10%" style="font-size:11px;text-align:left">${ '{:,.2f}'.format(line.qty) }</td>
      <td width="10%" style="font-size:11px;text-align:left">${ '{:,.2f}'.format(line.pu) }</td>
      <td width="10%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(line.total) }</td>
    </tr>
    %endfor      
   
  </table>
  <table>
    <tr style="page-break-inside:avoid">
      <td width="30%" style="font-size:11px;text-align:left"></td>
      <td width="50%" style="font-size:11px;text-align:left">TOTAL</td>
      <td width="20%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(total) }</td>
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
      <th width="100%">ELABORADO POR</th>
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
      <th width="100%">${user.employee_id.complete_name or ''}</th>
    </tr>  
  </table>
  %endfor
</html>
