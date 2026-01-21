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
      <td width="100%" style="font-size:14;text-align:center;">PLAN ANUAL DE COMPRAS</td>	  	  
    </tr>	
    <tr>
      <td width="100%" style="font-size:14;text-align:left;">DIRECCION/DEPARTAMENTO: ${o.department_id.name or  ''}</td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="10%">CODIGO</th>
        <th style="font-size:11px" width="40%">BIEN/SERVICIO</th>
        <th style="font-size:11px" width="10%">CANTIDAD</th>
        <th style="font-size:11px" width="15%">UNIDAD</th>
        <th style="font-size:11px" width="10%">PRECIO UNITARIO</th>
        <th style="font-size:11px" width="10%">TOTAL</th>
      </tr>
    </thead>
	<%
	   a=total=0
	   %>
    %for line in o.line_ids:
	<%
	   total += line.total
	   a+=1
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="10%" style="font-size:11px;text-align:left">${line.name.code}</td>
      <td width="40%" style="font-size:11px;text-align:left">${line.name.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.qty}</td>
      <td width="15%" style="font-size:11px;text-align:right">${line.name.uom.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.name.pu}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.total}</td>
    </tr>
    %endfor
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${}</td>
      <td width="10%" style="font-size:11px;text-align:center">${}</td>
      <td width="40%" style="font-size:11px;text-align:left">${}</td>
      <td width="10%" style="font-size:11px;text-align:right">${}</td>
      <td width="15%" style="font-size:11px;text-align:right">${}</td>
      <td width="10%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${total}</b></td>
    </tr>      
  </table>
    <table width="100%">
      <tr>
	<th width="50%" style="text-align:center;font-size:10px">________________________</th>
      </tr>
      <tr>
	<th width="50%" style="text-align:center;font-size:10px">DIRECTOR</th>
      </tr>
    </table>
  %endfor
</html>
