<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h2 style="text-align:center;" align="center">TALENTO HUMANO</h2>
   %if o.tipo_id:
   <h5 style="text-align:center;" align="center">NOMINA QUINCENAL : ${o.tipo_id.name}</h5>
   %else:
   <h5 style="text-align:center;" align="center">NOMINA QUINCENAL</h5>
   %endif
   <h5 style="text-align:center;" align="center">PERIODO: ${o.period_id.name}</h5>
   <%
      total_funcionarios=total=total_departamento=0
      %>
   %for line in o.line_ids:
   <%
	total+=line.valor
	%>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="60%" style="text-align:left;" > PROGRAMA: ${line.program_id.sequence} - ${line.program_id.name}</th>
       </tr>
     </thead>
        <%
      total_departamento=0
      %>
     %for line_line in line.line_ids:
	<%

	   total_departamento+=line_line.valor
	   %>
	<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
	  <tr>
	    <td width="60%" style="text-align:left;" >DEPARTAMENTO ${line_line.department_id.name}</td>
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
	   total_funcionarios += 1
	   %>
	<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
	  <tr>
	    <td width="30%" style="font-size:11px;text-align:left">${line_line_line.employee_id.complete_name}</td>
	    <td width="30%" style="font-size:11px;text-align:right">${line_line_line.employee_id.job_id.name}</td>
	    <td width="7%" style="font-size:11px;text-align:right">15</td>
	    <td width="7%" style="font-size:11px;text-align:right">${line_line_line.valor}</td>
	    <td width="7%" style="font-size:11px;text-align:right">0</td>
	    <td width="7%" style="font-size:11px;text-align:right">${line_line_line.valor}</td>
	    <td width="17%" style="font-size:11px;text-align:right">${}</td>
	  </tr>
	</table>
	%endfor
	<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
	  <tr>
	    <!--td width="35%" style="font-size:11px;text-align:left">${}</td>
		<td width="35%" style="font-size:11px;text-align:right">${}</td>
<td width="7%" style="font-size:11px;text-align:right">${}</td>
<td width="7%" style="font-size:11px;text-align:right">${}</td-->
	    <td width="93%" style="font-size:11px;text-align:right"><b>TOTAL DEPARTAMENTO</b></td>
	    <td width="7%" style="font-size:11px;text-align:right"><b>${total_departamento}</b></td>
	  </tr>
	</table>
     <tr style="height:35px">
     </tr>  
     <tr style="height:35px">
     </tr>
     <%
	total_departamento=0
	%>
     %endfor   
     <tr style="height:35px">
     </tr>
     %endfor
   </table>
   
</table>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
<tr>
    <td width="93%" style="font-size:11px;text-align:right"><b>TOTAL FUNCIONARIOS</b></td>
    <td width="7%" style="font-size:11px;text-align:right"><b>${total_funcionarios}</b></td>
  </tr>
  <tr>
    <!--td width="7%" style="font-size:11px;text-align:left"></td>
	<td width="7%" style="font-size:11px;text-align:right"></td>
<td width="7%" style="font-size:11px;text-align:right"></td>
<td width="7%" style="font-size:11px;text-align:right"></td-->
    <td width="93%" style="font-size:11px;text-align:right"><b>TOTAL ROL A PAGAR</b></td>
    <td width="7%" style="font-size:11px;text-align:right"><b>${total}</b></td>
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
