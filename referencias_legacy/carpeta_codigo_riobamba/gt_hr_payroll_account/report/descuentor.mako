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
       <td style="text-align:center;" align="center">DESCUENTOS RUBRO: ${o.rubro_id.name}</td>
       <td style="text-align:center;" align="center">PERIODO: ${o.period_id.name}</td>
       %if o.rol_id:
       <td style="text-align:center;" align="center">ROL: ${o.rol_id.name}</td>
       %endif
     </tr>
   </table>
   <%
      total=0
      %>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="5%" style="text-align:center;">Numero</th>
	 <th width="85%" style="text-align:center;">Funcionario</th>
	 <th width="10%" style="text-align:center;">Total</th>
       </tr>
     </thead>
   </table>
   <%
      a=0
      %>
   %for line in o.line_ids:
   <%
      total+=line.monto
      a+=1
      %>
     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="5%" style="font-size:11px;text-align:center">${a}</td>
	 <td width="85%" style="font-size:11px;text-align:left">${line.name}</td>
	 <td width="10%" style="font-size:11px;text-align:right">${line.monto}</td>
       </tr>
     </table>
     %endfor
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="90%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${total}</b></td>
       </tr>
     </table>
      <br>
      <br>
      <br>
     <table width="100%" style="page-break-inside:avoid">
      <tr>
	<th width="50%" style="text-align:center;font-size:10px">________________________</th>
	<th width="50%" style="text-align:center;font-size:10px">________________________</th>
      </tr>
      <tr>
	<th width="50%" style="text-align:center;font-size:10px">CREADO POR</th>
	<th width="50%" style="text-align:center;font-size:10px">REVISADO POR</th>
      </tr>
      <tr>
	<td width="50%" style="text-align:center;font-size:10px">${user.employee_id.complete_name or ''|entity}</td>
	<td width="50%" style="text-align:center;font-size:10px">SOFIA ROSA CASTILLO HEREDIA</td>
      </tr>
    </table>
     %endfor
 </body>
</html>
