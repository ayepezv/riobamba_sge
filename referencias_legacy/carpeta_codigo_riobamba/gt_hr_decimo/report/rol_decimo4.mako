<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>

</head>
<body style="overflow:visible;">	
    %for decimo in objects:
    <tr style="border: 1px solid black;"><h4 style="text-align:center;" align="center">ROL DECIMO CUARTO ${decimo.contract_type.name} DEL: ${decimo.date_start} -  ${decimo.date_stop}</h4></tr>
    <%
       total_descuento_all=total=total_recibe=0
       %>
%for programa_id in all_programas(decimo):
<table WIDTH="100%">
  <tr>
    <td width="100%" style="font-size:14;text-align:center;">PROGRAMA/DIRECCION ${programa_id.sequence or  ''} - ${programa_id.name or  ''}</td>	  	  
  </tr>	
</table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:11px" width="5%">Nro.</th>
        <th style="font-size:11px" width="35%">Funcionario</th>
	<th style="font-size:11px" width="5%">Total Dias</th>
	<th style="font-size:11px" width="10%">Tot. Decimo</th>
	<th style="font-size:11px" width="10%">Desc. Judicial</th>
        <th style="font-size:11px" width="10%">Neto Recibir</th>
        <th style="font-size:11px" width="15%">Partida</th>
       <!--  <th style="font-size:11px" width="10%">Firma</th> -->
      </tr>
    </thead>
    <%
       a=0
       total_programa=subtotal_programa=0
       total_descuento=0
       %>
    %for decimo_id in all_decimo(decimo,programa_id):
    <% 
       aux_subtotal = 0
       a+=1 
       total_programa+=decimo_id.recibir
       total_descuento+=decimo_id.descuento_judicial
       aux_subtotal = decimo_id.recibir + decimo_id.descuento_judicial
       total+=aux_subtotal
       subtotal_programa+=aux_subtotal
       total_descuento_all+=decimo_id.descuento_judicial
       aux_partida = decimo_id.code_partida
       %>
    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <th style="font-size:11px" width="5%">${a}</th>
      <th style="font-size:11px;text-align:left" width="35%">${decimo_id.employee_id.complete_name}</th>
      <th style="font-size:11px;text-align:center" width="5%">${decimo_id.dias_lab}</th>
      <th style="font-size:11px;text-align:right" width="10%">${ '{:,.2f}'.format(aux_subtotal)}</th>
      <th style="font-size:11px;text-align:right" width="10%">${ '{:,.2f}'.format(decimo_id.descuento_judicial)}</th>
      <th style="font-size:11px;text-align:right" width="10%">${ '{:,.2f}'.format(decimo_id.recibir)}</th>
      <th style="font-size:11px" width="15%">${aux_partida}</th>
      <!-- <th style="font-size:11px;text-align:right" width="10%"></th> -->
    </tr>
    %endfor
    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <th style="font-size:11px" width="5%"></th>
      <th style="font-size:11px" width="35%">TOTAL PROGRAMA</th>
      <th style="font-size:11px" width="5%"></th>
      <th style="font-size:11px" width="10%">${ '{:,.2f}'.format(subtotal_programa)}</th>
      <th style="font-size:11px" width="10%">${ '{:,.2f}'.format(total_descuento)}</th>
      <th style="font-size:11px" width="10%">${ '{:,.2f}'.format(total_programa)}</th>
      <th style="font-size:11px" width="15%"></th>
     <!-- <th style="font-size:11px" width="10%"></th> -->
    </tr>

%endfor
%endfor
  <%
     total_recibe = total - total_descuento_all
     %>

    <tr style="border-collapse:collapse;font-size:12px">
      <th style="font-size:11px" width="5%"></th>
      <th style="font-size:11px" width="35%">TOTAL DECIMO CUARTO</th>
      <th style="font-size:11px" width="5%"></th>
      <th style="font-size:11px" width="10%">${ '{:,.2f}'.format(total)}</th>
      <th style="font-size:11px" width="10%">${ '{:,.2f}'.format(total_descuento_all)}</th>
      <th style="font-size:11px" width="10%">${ '{:,.2f}'.format(total_recibe)}</th>
      <th style="font-size:11px" width="10%"></th>
    </tr>
  </table>
<table width="100%" style="page-break-inside:avoid">
  <tr style="font-size:11px">
    <th width="33%">CREADO POR</th>
    <th width="33%">REVISADO POR</th>
    <th width="33%">AUTORIZADO</th>
  </tr>  
  <br>
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
  <br>
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
