<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>

</head>
<body style="overflow:visible;">	
  %for decimo in objects:
  <tr style="border: 1px solid black;"><h4 style="text-align:center;" align="center">ROL RETENCIONES JUDICIALES DECIMO CUARTO - SUPA ${decimo.contract_type.name} DEL: ${decimo.date_start} -  ${decimo.date_stop}</h4></tr>
  <%
     a=total=0
     %>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <td style="font-size:11px" width="5%">Nro.</td>
        <td style="font-size:11px" width="30%">Funcionario</td>
        <td style="font-size:11px" width="50%">Beneficiario</td>
	<td style="font-size:11px" width="10%">Total Retencion</td>
        <td style="font-size:11px" width="5%">Firma</td>
      </tr>
    </thead>
    %for line in decimo.line_ids:
    <%
       total_decimo = line.total_decimo
       total_decimo_origen = line.total_decimo
       total_otras = 0
       %>

    %if line.descuento_judicial>0:
    <%
       aux_sum_line_ret = 0
       a+=1
       total+=line.descuento_judicial
       %>
    %for line_benef in line.contract_id.employee_id.judicial_ids:
    %if line_benef.is_supa:
    <%
       aux_sum_line_ret += line_benef.monto
       %>
    %endif
    %endfor
    %if aux_sum_line_ret>0:
    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <td WIDTH="5%" style="font-size:12px" align="left">${a}</td>
      <td WIDTH="40%" style="font-size:12px" align="left">${line.contract_id.employee_id.complete_name}</td>
      <td WIDTH="40%" style="font-size:12px" align="left">
	<%
	   aux_line_ret = 0
	   %>
	%for line_benef in line.contract_id.employee_id.judicial_ids:
	%if line_benef.is_supa:
	<%
           aux_line_ret = 0
           if total_decimo>0:
	       if line_benef.monto<=total_decimo:
	           aux_line_ret = line_benef.monto#(line_benef.monto * line.descuento_judicial) / aux_sum_line_ret
                   total_decimo = total_decimo - line_benef.monto
	           total_otras += line_benef.monto			     
	       else:
                   aux_line_ret = abs(total_decimo_origen - total_otras)
	           total_decimo = 0			 
	   %>
	<b>${line_benef.partner_id.ced_ruc}</b> - ${line_benef.partner_id.name} - ($.)${'{:,.2f}'.format(aux_line_ret)}
	%endif
	%endfor
      </td>
      <td WIDTH="10%" style="font-size:12px" align="right">${'{:,.2f}'.format(aux_sum_line_ret)}</td>
      <!--td WIDTH="10%" style="font-size:12px" align="right">${'{:,.2f}'.format(line.descuento_judicial)}</td-->
      <td WIDTH="5%" style="font-size:12px" align="right"></td>
    </tr>
    %endif
    %endif
    %endfor
  </table>
  %endfor
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <tr style="border-collapse:collapse;font-size:12px">
      <th style="font-size:11px" width="5%"></th>
      <th style="font-size:11px" width="50%">TOTAL RETENIDO JUDICIAL DECIMO CUARTO</th>
      <th style="font-size:11px" width="10%">${total}</th>
      <th style="font-size:11px" width="15%"></th>
    </tr>
  </table>
  <table width="100%" style="page-break-inside:avoid">
    <tr style="height:35px">
      <th></th>
      <th></th>
    </tr>
    <tr style="font-size:11px">
      <th width="33%">CREADO POR</th>
      <th width="33%">REVISADO POR</th>
      <th width="33%">AUTORIZADO</th>
    </tr>  
    <tr style="height:35px">
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th>______________________</th>
      <th>______________________</th>
      <th>______________________</th>
    </tr>
    <tr style="font-size:11px">
<th width="33%">${decimo.creado_por.employee_id.complete_name}</th>
      <th width="33%">${user.employee_id.complete_name}</th>
      <th width="33%">${user.context_department_id.manager_id.complete_name}</th>
    </tr>  
  </table>
  <table width="100%" style="page-break-inside:avoid">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th>________________________</th>
      <th>________________________</th>
      <th>________________________</th>
      <th>________________________</th>
    </tr>
    <tr style="font-size:11px">
      <th width="25%">REVISADO POR</th>
      <th width="25%">CONTADOR GENERAL</th>
      <th width="25%">ESPECIALISTA DE PRESUPUESTOS</th>
      <th width="25%">DIRECTOR FINANCIERO</th>
    </tr>  
    <tr style="font-size:11px">
      <th width="25%"></th>
      <th width="25%"></th>
      <th width="25%"></th>
      <th width="25%">AUTORIZO TRANSFERENCIA</th>
    </tr>  
  </table>
</body>
</html>
