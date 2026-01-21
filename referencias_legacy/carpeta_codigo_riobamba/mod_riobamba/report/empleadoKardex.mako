<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <table  cellspacing=0 width="100%">
     <tr>
       <td width="15%"><center><b>${helper.embed_logo_by_name('invoice_logo',width=50,height=50)|n}</b></center></td>
       <td width="70%"><center><b>${company.name}</b><br>KARDEX FUNCIONARIOS</center></td>
     </tr>
   </table>
   <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
     <tr>
       <td style="font-weight: bold;font-size:11px" width="20%">Fecha Desde:</td>
       <td style="font-size:11px" width="30%">${o.fecha or  ''}</td>
    </tr>
  </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
     <tr style="page-break-inside:avoid">
       <th width="60%">Funcionario</th>
       <th width="10%">Contrato</th>
       <th width="10%">Departamento</th>
       <th width="10%">Cargo</th>
       <th width="10%">RMU</th>
       <th width="10%">Fecha desde</th>
       <th width="10%">Fecha hasta</th>
       <th width="10%">activo</th>
     </tr>
    </thead>
    <%
       %>
    %for line in o.line_ids:
    <%
       %>
    <tr BGCOLOR="#A4A4A4" style="page-break-inside:avoid">
      <td width="60%" style="font-size:11px;text-align:left"><b>${line.employee_id.name} - ${line.employee_id.complete_name}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
      <td width="10%" style="font-size:11px;text-align:right"></td>
    </tr>
    %for line_line in line.line_ids:
    <tr style="page-break-inside:avoid">
      <td width="60%" style="font-size:11px;text-align:left"></td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.contract_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.contract_id.department_id.name or line_line.contract_id.employee_id.department_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.contract_id.job_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.contract_id.wage}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.contract_id.date_start}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.contract_id.date_end}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line_line.estado}</td>
    </tr>
    %endfor
    %endfor   
   </table>
   %endfor
  <table width="100%">
    <tr style="height:35px">
      <th>__________________</th>
    </tr>
  </table>
</body>
</html>
