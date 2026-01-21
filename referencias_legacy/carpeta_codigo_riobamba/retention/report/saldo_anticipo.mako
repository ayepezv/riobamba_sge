<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <% import time %>
   <h4 style="text-align:center;" align="center">CONTABILIDAD</h2>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <tr>
       <td style="text-align:center;" align="center">CUENTAS POR COBRAR AL PERSONAL ANTICIPOS AL: ${time.strftime('%Y-%m-%d')}</td>
     </tr>
   </table>
   <%
      totala = totald = totals = 0
      %>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="5%" style="text-align:center;">Numero</th>
	 <th width="65%" style="text-align:center;">Funcionario</th>
	 <th width="10%" style="text-align:center;">Total Anticipo</th>
	 <th width="10%" style="text-align:center;">Devengado</th>
	 <th width="10%" style="text-align:center;">Saldo</th>
       </tr>
     </thead>
   </table>
   <%
      a=0
      %>
   %for line in o.line_ids:
   <%
      totala+=line.total_anticipos
      totald+=line.total_devengado
      totals+=line.saldo
      a+=1
      %>
   %if line.saldo>0:
     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
       <tr>
	 <td width="5%" style="font-size:10px;text-align:center">${a}</td>
	 <td width="65%" style="font-size:10px;text-align:left">${line.empleado_name}</td>
	 <td width="10%" style="font-size:10px;text-align:right">${line.total_anticipos}</td>
	 <td width="10%" style="font-size:10px;text-align:right">${line.total_devengado}</td>
	 <td width="10%" style="font-size:10px;text-align:right">${line.saldo}</td>
       </tr>
     </table>
     %endif
     %endfor
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="70%" style="font-size:11px;text-align:right"><b>TOTALES</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${totala}</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${totald}</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${totals}</b></td>
       </tr>
     </table>
     %endfor
 </body>
</html>
