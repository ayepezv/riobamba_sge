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
      <td width="100%" style="font-size:14;text-align:center;">DETALLE DE PAGOS - NUMERO ${ o.ref } : ${ o.name }</td>	  	  
    </tr>	
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">INSTITUCION: ${ user.company_id.name } </td>	  	  
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">FECHA REPORTE: ${ o.date_done } </td>	  	  
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">REFERENCIA: ${ o.date_done } </td>	  	  
    </tr>
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="10%">CEDULA</th>
        <th style="font-size:11px" width="30%">NOMBRE</th>
        <th style="font-size:11px" width="10%">CUENTA</th>
	<th style="font-size:11px" width="40%">DETALLE</th>
	<th style="font-size:11px" width="10%">VALOR</th>
      </tr>
    </thead>
    <% total=0 
       %>
    %for line in o.line_ids:
    <% 
       total += line.amount
       %>
    <tr style="page-break-inside:avoid">
      <td width="10%" style="font-size:11px;text-align:left">${line.partner_id.ced_ruc}</td>
      <td width="30%" style="font-size:11px;text-align:right">${line.partner_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.bank_id.acc_number}</td>
      <td width="40%" style="font-size:11px;text-align:right">${line.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.amount}</td>
    </tr>
    %endfor      
    <tr style="page-break-inside:avoid">
      <td width="10%" style="font-size:11px;text-align:left"></td>
      <td width="30%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="40%" style="font-size:11px;text-align:right"><b>TOTAL $</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${total}</b></td>
    </tr>
  </table>
  <tr>
    <tfoot>
      <tr>
	<td>PARA USO INTERNO DE LA ENTIDAD PUBLICA<td>
      </tr>
    </tfoot>
  %endfor
</html>
