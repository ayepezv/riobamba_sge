<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <% import time %>
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">CONTABILIDAD</td>	  	  
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">DETALLE DE SALDO PENDIENTES CUENTAS POR COBRAR AL ${time.strftime('%Y-%m-%d')} </td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="65%">BENEFICIARIO</th>
        <th style="font-size:11px" width="10%">MONTO ANTICIPADO</th>
        <th style="font-size:11px" width="10%">ANTICIPO DEVENGADO</th>
        <th style="font-size:11px" width="10%">SALDO X DEVENGAR</th>
      </tr>
    </thead>
	<%
	   a=0
	   totala = totald = totalpd = 0
	   %>
    %for line in o.line_ids:
	<%
	   a+=1
	   totala+=line.monto
	   totald+=line.devengado
	   totalpd+=line.saldo
	   %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="65%" style="font-size:11px;text-align:left">${line.partner_id.ced_ruc} - ${line.partner_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.monto}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.devengado}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.saldo}</td>
    </tr>
    %for line_line in line.line_ids:
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${}</td>
      <td width="65%" style="font-size:11px;text-align:left">${line_line.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.monto}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.devengado}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.saldo}</td>
    </tr>
    %endfor
    %endfor
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <tr style="page-break-inside:avoid">
      <td width="70%" style="font-size:11px;text-align:left"><b>TOTAL</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${totala}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${totald}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${totalpd}</b></td>
    </tr>
  </table>
  %endfor
</html>
