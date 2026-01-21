<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   <h2 style="text-align:center;" align="center">TALENTO HUMANO</h2>
   <h2 style="text-align:center;" align="center">REPORTE DE FALTAS</h2>
   <%
      total = 0
      %> 
   <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:12px;page-break-inside:avoid">
     <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
       <td WIDTH="25%" style="text-align:left;font-size:12px"> Funcionario</td>
       <td WIDTH="25%" style="text-align:left;font-size:12px">Departamento</td>	
       <td WIDTH="5%" style="text-align:left;font-size:12px">Fecha Inicio</td>
       <td WIDTH="5%" style="text-align:left;font-size:12px">Fecha Fin</td>
       <td WIDTH="5%" style="text-align:left;font-size:12px">Dias</td>
       <td WIDTH="5%" style="text-align:left;font-size:12px">Horas</td>
       <td WIDTH="25%" style="text-align:left;font-size:12px">Motivo</td>
       <td WIDTH="5%" style="text-align:left;font-size:12px">Monto</td>
     </thead>
     %for inv in objects :
     <%
	total = inv.line_id.valor
	%>
     <tr>
       <td width="25%" style="font-size:11px;text-align:left">${ inv.employee_id.complete_name }</td>
       <td width="25%" style="font-size:11px;text-align:left">${ inv.department_id.name }</td>
       <td width="5%" style="font-size:11px;text-align:left">${ inv.date_from }</td>
       <td width="5%" style="font-size:11px;text-align:left">${ inv.date_to }</td>
       <td width="5%" style="font-size:11px;text-align:left">${ inv.total_dias }</td>
       <td width="5%" style="font-size:11px;text-align:left">${ inv.horas }</td>
       <td width="25%" style="font-size:11px;text-align:left">${ inv.notes }</td>
       <td width="5%" style="font-size:11px;text-align:left">${ inv.line_id.valor }</td>
     </tr>
   %endfor
     <tr style="page-break-inside:avoid">
       <td WIDTH="25%" style="text-align:center;font-size:12px">${''}</td>
       <td WIDTH="25%" style="text-align:center;font-size:12px">${''}</td>
       <td WIDTH="5%" style="text-align:center;font-size:12px">${''}</td>
       <td WIDTH="5%" style="text-align:center;font-size:12px">${''}</td>
       <td width="5%" style="text-align:center;font-size:12px">${''}</td>
       <td width="5%" style="text-align:center;font-size:12px">${''}</td>
       <td WIDTH="25%" style="text-align:center;font-size:12px"><b>${'TOTAL USD'}</b></td>
       <td WIDTH="5%" style="text-align:center;font-size:12px"><b>${total or '0.00'|entity}</b></td>
     </tr>
   </table>
</body>
</html>
