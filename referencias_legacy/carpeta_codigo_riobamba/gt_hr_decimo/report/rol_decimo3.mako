<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>

</head>
<body style="overflow:visible;">	
    %for decimo in objects:
    <tr style="border: 1px solid black;"><h4 style="text-align:center;" align="center">ROL DECIMO TERCERO ${decimo.contract_type.name} DEL: ${decimo.period_start.name} -  ${decimo.period_end.name}</h4></tr>
    <%
       total=0
       %>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:10px" width="5%">Nro.</th>
        <th style="font-size:10px" width="40%">Funcionario</th>
        <th style="font-size:10px" width="10%">Total Ganado(+)</th>
	<th style="font-size:10px" width="10%">Total Decimo(+)</th>
        <th style="font-size:10px" width="10%">Descuento Anticipo(-)</th>        
	<th style="font-size:10px" width="10%">Descuento Ret. Judicial(-)</th>
        <th style="font-size:10px" width="10%">Neto a Recibir</th>
        <th style="font-size:10px" width="15%">Firma</th>
      </tr>
    </thead>
  </table>
    <%
       total = total_ganado = total_decimo = total_anticipo = total_judicial = 0
       %>
    %for programa_id in all_programas(decimo):
    <table WIDTH="100%">
      <tr>
	<td width="100%" style="font-size:14;text-align:center;">PROGRAMA/DIRECCION ${programa_id.sequence or  ''} - ${programa_id.name or  ''}</td>	  	  
      </tr>	
    </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
    <%
       a=0
       total_programa = total_decimo_programa = total_ganado_programa = total_anticipo_programa = total_judicial_programa = 0
       %>
    %for decimo_id in all_decimo(decimo,programa_id):
    <% 
       a+=1
       total_decimo += decimo_id.total_dec
       total_programa+=decimo_id.recibir
       total_ganado_programa+=decimo_id.total
       total_anticipo_programa+=decimo_id.descuento_anticipo
       total_judicial_programa+=decimo_id.descuento_judicial
       total+=decimo_id.recibir
       total_ganado+=decimo_id.total
       total_anticipo+=decimo_id.descuento_anticipo
       total_judicial+=decimo_id.descuento_judicial
       total_decimo_programa += decimo_id.total_dec
       %>
    <tr  style="border-collapse:collapse;font-size:10px">
      <th style="font-size:10px" width="5%">${a}</th>
      <th style="font-size:10px;text-align:left" width="40%">${decimo_id.employee_id.complete_name}</th>
      <th style="font-size:10px;text-align:right" width="10%">${decimo_id.total}</th>     
      <th style="font-size:10px;text-align:right" width="10%">${decimo_id.total_dec}</th>
      <th style="font-size:10px;text-align:right" width="10%">${decimo_id.descuento_anticipo}</th>
      <th style="font-size:10px;text-align:right" width="10%">${decimo_id.descuento_judicial}</th>
      <th style="font-size:10px;text-align:right" width="10%">${decimo_id.recibir}</th>
      <th style="font-size:10px" width="15%"></th>
    </tr>
    %endfor
    <tr  style="border-collapse:collapse;font-size:10px">
      <th style="font-size:10px" width="5%"></th>
      <th style="font-size:10px" width="40%">TOTAL PROGRAMA</th>
      <th style="font-size:10px" width="10%">${total_ganado_programa}</th>      
      <th style="font-size:10px" width="10%">${total_decimo_programa}</th>
      <th style="font-size:10px" width="10%">${total_anticipo_programa}</th>
      <th style="font-size:10px" width="10%">${total_judicial_programa}</th>
      <th style="font-size:10px" width="10%">${total}</th>
      <th style="font-size:10px" width="15%"></th>
    </tr>
  </table>
%endfor
%endfor
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
    <tr>
      <th style="font-size:10px" width="5%"></th>
      <th style="font-size:10px" width="40%">TOTAL DECIMO TERCERO</th>
      <th style="font-size:10px" width="10%">${total_ganado}</th>
      <th style="font-size:10px" width="10%">${total_decimo}</th>
      <th style="font-size:10px" width="10%">${total_anticipo}</th>
      <th style="font-size:10px" width="10%">${total_judicial}</th>
      <th style="font-size:10px" width="10%">${decimo.total}</th>
      <th style="font-size:10px" width="15%"></th>
    </tr>
  </table>
  <table width="100%" style="page-break-inside:avoid">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="font-size:10px">
      <th width="50%">Creado por</th>
      <th width="50%">Autorizado</th>
    </tr>  
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th>__________________</th>
      <th>__________________</th>
    </tr>
    <tr style="font-size:10px">
      <th width="33%">${user.employee_id.complete_name}</th>
      <th width="33%">${user.context_department_id.manager_id.complete_name}</th>
    </tr>  
  </table>
</body>
</html>
