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
       <td style="text-align:center;" align="center">DESCUENTOS RUBRO DETALLE: ${o.rubro_id.name}</td>
       <td style="text-align:center;" align="center">PERIODO: ${o.period_id.name}</td>
       %if o.rol_id:
       <td style="text-align:center;" align="center">ROL: ${o.rol_id.name}</td>
       %endif
     </tr>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="5%" style="text-align:center;">Numero</th>
	 <th width="35%" style="text-align:center;">Funcionario</th>
	 <th width="10%" style="text-align:center;">Ingresos</th>
	 <th width="10%" style="text-align:center;">Apt.(Subrogacion)</th>
	 <th width="10%" style="text-align:center;">Total Ingresos</th>
	 <th width="10%" style="text-align:center;">Iess</th>
	 <th width="10%" style="text-align:center;">Total Rol</th>
	 <th width="10%" style="text-align:center;">Total Descontado</th>
       </tr>
     </thead>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
   <%
      a=t_i=t_s=t_ii=t_iess=t_sub=total=0
      %>
   %for line in o.line_ids:
   <%
      total+=line.monto
      t_i+=line.ingresos
      t_s+=line.subrogacion
      t_ii+=line.total_ingresos
      t_iess+=line.iess
      t_sub+=line.total
      a+=1
      %>
       <tr>
	 <td width="5%" style="font-size:11px;text-align:center">${a}</td>
	 <td width="35%" style="font-size:11px;text-align:left">${line.employee_id.name} - ${line.name}</td>
	 <td width="10%" style="font-size:11px;text-align:left">${line.ingresos}</td>
	 <td width="10%" style="font-size:11px;text-align:left">${line.subrogacion}</td>
	 <td width="10%" style="font-size:11px;text-align:left">${line.total_ingresos}</td>
	 <td width="10%" style="font-size:11px;text-align:left">${line.iess}</td>
	 <td width="10%" style="font-size:11px;text-align:left">${line.total}</td>
	 <td width="10%" style="font-size:11px;text-align:right">${line.monto}</td>
       </tr>
     %endfor
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <tr>
       <td width="40%" style="font-size:11px;text-align:right"><b>TOTALES</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>${t_i}</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>${t_s}</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>${t_ii}</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>${t_iess}</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>${t_sub}</b></td>
       <td width="10%" style="font-size:11px;text-align:right"><b>${total}</b></td>
     </tr>
   </table>
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
       <td width="50%" style="text-align:center;font-size:10px">SOFIA CASTILLO</td>
     </tr>
   </table>
   %endfor
 </body>
</html>
