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
      <td width="100%" style="font-size:14;text-align:center;">REPORTE DE CONTROL ***TRASNFERENCIAS SPI-SP***</td>	  	  
    </tr>	
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">INSTITUCION: ${ user.company_id.name } </td>	  	  
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">FECHA REPORTE: ${ o.date_done } </td>	  	  
    </tr>
<tr>
      <td width="100%" style="font-size:14;text-align:center;">FECHA AFECTACION: ${ o.date_done } </td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="60%">INSTITUCION PAGADORA</th>
        <th style="font-size:11px" width="20%">#PAGOS</th>
        <th style="font-size:11px" width="20%">MONTO</th>
      </tr>
    </thead>
	<%
	   total=qty=0
	   %>
	%for line in o.resumen_ids:
	<%
	   total+=line.amount
	   qty+=line.qty
	   %>
    <tr style="page-break-inside:avoid">
      <td width="60%" style="font-size:11px;text-align:left">${line.name}</td>
      <td width="20%" style="font-size:11px;text-align:right">${line.qty}</td>
      <td width="20%" style="font-size:11px;text-align:right">${line.amount}</td>
    </tr>
    %endfor      
    <tr>
      <td width="60%" style="font-size:11px;text-align:left">TOTALES</td>
      <td width="20%" style="font-size:11px;text-align:right">${qty}</td>
      <td width="20%" style="font-size:11px;text-align:right">${total}</td>
    </tr>

  </table>

  <tr>
    <td width="20%" style="font-size:11px;text-align:left">NUMERO DE CONTROL</td>
    <td width="80%" style="font-size:11px;text-align:right">${o.dig}</td>
  </tr>
    <tfoot>
      </br>
      <tr>
	<td>PARA USO INTERNO DE LA ENTIDAD PUBLICA<td>
      </tr>
    </tfoot>
  %endfor
</html>
