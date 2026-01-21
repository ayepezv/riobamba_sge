<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h4 style="text-align:center;" align="center">CONTABILIDAD</h2>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <tr>
       <td style="text-align:center;" align="center">CUENTAS POR PAGAR AL SERVICIO DE RENTAS INTERNAS AL: ${o.date}</td>
     </tr>
   </table>
   <%
      total=0
      %>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="5%" style="text-align:center;">Numero</th>
	 <th width="25%" style="text-align:center;">Comprobante Contable</th>
	 <th width="25%" style="text-align:center;">Cuenta</th>
	 <th width="25%" style="text-align:center;">Partida</th>
	 <th width="10%" style="text-align:center;">Monto</th>
	 <th width="10%" style="text-align:center;">Saldo</th>
       </tr>
     </thead>
   </table>
   <%
      a=0
      %>
   %for line in o.line_ids:
   <%
      total+=line.saldo
      a+=1
      %>
     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
       <tr>
	 <td width="5%" style="font-size:10px;text-align:center">${a}</td>
	 <td width="25%" style="font-size:10px;text-align:left">${line.move_id.name} - ${line.move_id.narration}</td>
	 <td width="25%" style="font-size:10px;text-align:left">${line.move_line_id.account_id.code} - ${line.move_line_id.account_id.name}</td>
	 <td width="25%" style="font-size:10px;text-align:left">${line.move_line_id.budget_id.code} - ${line.move_line_id.budget_id.name}</td>
	 <td width="10%" style="font-size:10px;text-align:right">${line.monto}</td>
	 <td width="10%" style="font-size:10px;text-align:right">${line.saldo}</td>
       </tr>
     </table>
     %endfor
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="90%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${total}</b></td>
       </tr>
     </table>
     %endfor
 </body>
</html>
