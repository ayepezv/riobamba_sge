<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h2 style="text-align:center;" align="center">TALENTO HUMANO</h2>
   <h2 style="text-align:center;" align="center">NOMINA QUINCENAL</h2>
   <h2 style="text-align:center;" align="center">PERIODO: ${o.period_id.name}</h2>
   <%
      total=total_rol=total_aux=0
      %>
   %for line in o.line_ids:
   <%
	total_aux+=line.valor
	%>
   %endfor
   %for line in o.line_ids2:
   <%
      empleados=0
      %>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="60%" style="text-align:center;" ><b> ROL: ${line.tipo_id.name}</b></th>
       </tr>
     </thead>
        <%
      total_rol=0
      %>
     %for line_line in line.line_ids:
     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="60%" style="text-align:left;" >PROGRAMA : ${line_line.program_id.sequence} - ${line_line.program_id.name}</td>
       </tr>
       <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
	 <thead>
	   <tr>
	     <th width="30%" style="text-align:left;">Empleado</th>
	     <th width="30%">Cargo</th>
	     <th width="7%">Dias Laborados</th>
	     <th width="7%">Ingresos</th>
	     <th width="7%">Egresos</th>
	     <th width="7%">Neto a recibir</th>
	     <th width="17%">Firma</th>
	   </tr>
	 </thead>
       </table>
     </table>
     %for line_line_line in line_line.line_ids:
     <%
	total_rol+=line_line_line.valor
	total+=line_line_line.valor
	empleados += 1
	%>
     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="30%" style="font-size:11px;text-align:left">${line_line_line.contract_id.employee_id.complete_name}</td>
	 <td width="30%" style="font-size:11px;text-align:right">${line_line_line.contract_id.employee_id.job_id.name}</td>
	 <td width="7%" style="font-size:11px;text-align:right">15</td>
	 <td width="7%" style="font-size:11px;text-align:right">${line_line_line.valor}</td>
	 <td width="7%" style="font-size:11px;text-align:right">0</td>
	 <td width="7%" style="font-size:11px;text-align:right">${line_line_line.valor}</td>
	 <td width="17%" style="font-size:11px;text-align:right">${}</td>
       </tr>
     </table>

     %endfor
     <tr style="height:35px">
	 <th>___________________________________________________________________________</th>
     </tr>
     <tr style="height:35px">
     </tr>  
     <tr style="height:35px">
     </tr>
        <%
      total_departamento=0
      %>
     %endfor   
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <!--td width="35%" style="font-size:11px;text-align:left">${}</td>
	 <td width="35%" style="font-size:11px;text-align:right">${}</td-->
	 <td width="30%" style="font-size:11px;text-align:right"><b>TOTAL EMPLEADOS</b></td>
	 <td width="7%" style="font-size:11px;text-align:right"><b>${empleados}</b></td>
	 <td width="30%" style="font-size:11px;text-align:right"><b>TOTAL TIPO ROL</b></td>
	 <td width="7%" style="font-size:11px;text-align:right"><b>${total_rol}</b></td>
       </tr>
     </table>

     <tr style="height:35px">
     </tr>
   </table>
   
</table>
%endfor
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
  <tr>
    <!--td width="7%" style="font-size:11px;text-align:left"></td>
    <td width="7%" style="font-size:11px;text-align:right"></td>
    <td width="7%" style="font-size:11px;text-align:right"></td>
    <td width="7%" style="font-size:11px;text-align:right"></td-->
    <td width="93%" style="font-size:11px;text-align:right"><b>TOTAL ROL A PAGAR</b></td>
    <td width="7%" style="font-size:11px;text-align:right"><b>${total_aux}</b></td>
  </tr>
</table>
<table width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
    <th>__________________</th>
    <th>__________________</th>
  </tr>
  <tr style="font-size:18px">
    <th width="33%">Jefe Talento Humano</th>
    <th width="33%">${user.employee_id.complete_name or ''}</th>
  </tr>  
</table>
   %endfor
</body>
</html>
