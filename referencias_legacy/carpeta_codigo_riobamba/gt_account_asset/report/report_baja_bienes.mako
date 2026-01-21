<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for inv in objects:
   <h6 style="text-align:center;" align="center">DIRECCION ADMINISTRATIVA - ACTIVOS FIJOS</h6>
   <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">  
     <tr>
       <td style="text-align:center;font-size:11px" align="center"><b>BAJA DE BIENES NRO. ${inv.name or ''|entity}</b></td>
     </tr>
   </table>
   <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
     <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Documento:</td>
      <td style="font-size:11px" width="42%">${inv.document or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Autorizado por:</td>
      <td style="font-size:11px" width="42%">${ inv.autorizado_por.complete_name or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Detalle:</td>
      <td style="font-size:11px" width="42%">${ inv.detail or  ''}</td>
    </tr>	
  </table>
  <%import time%>
  <p style="border-collapse:collapse;font-size:12px">En el canton de ${user.company_id.city or ''|entity}, Provincia del ${user.company_id.state_id.name or ''|entity}, el ${inv.date or ''|entity}, en las oficinas de ${user.context_department_id.name or ''|entity}, de el ${user.company_id.name or ''|entity}, se procede con la baja de los bienes que se detallan a continuacion.</p>
  <%
     total=total2=0
     %>
  <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
      <tr>
	<th width="20%" style="text-align:left;">C&oacute;digo del Bien</th>
	<th width="40%">Descripci&oacute;n</th>
	<th width="30%">Categoria</th>
	<th width="5%">Valor Compra</th>
	<th width="5%">Valor</th>
      </tr>
    %for activo in inv.asset_ids:
    
    <%
       total+=activo.asset_id.purchase_value
       total2 +=activo.asset_id.valor_actual
       %>	 
    <tr>
      <td width="20%" style="font-size:11px;text-align:left">${ activo.asset_id.code }</td>
      <td width="40%" style="font-size:11px;text-align:left">${ activo.asset_id.name or ''|entity}</td>
      <td width="30%" style="font-size:11px;text-align:right">${ activo.asset_id.category_id.name or ''|entity }</td>
      <td width="5%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(activo.asset_id.purchase_value) }</td>
      <td width="5%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(activo.asset_id.valor_actual) }</td>
    </tr>
    %endfor
  </table>
</table>
%endfor
<br>
<br>
<table width="100%" style="page-break-inside:avoid">
  <tr>
    <th width="33%" style="text-align:center;font-size:10px">________________________</th>
    <th width="33%" style="text-align:center;font-size:10px">________________________</th>
    <th width="33%" style="text-align:center;font-size:10px">________________________</th>
      </tr>
      <tr>
	<th width="33%" style="text-align:center;font-size:10px">ELABORADO</th>
	<th width="33%" style="text-align:center;font-size:10px">REVISADO</th>
	<th width="33%" style="text-align:center;font-size:10px">AUTORIZADO</th>
      </tr>
      <tr>
	<td width="33%" style="text-align:center;font-size:10px">${user.employee_id.complete_name or ''|entity}</td>
	<td width="33%" style="text-align:center;font-size:10px">${user.context_department_id.coordinador_id.complete_name or ''|entity}</td>
    <td width="33%" style="text-align:center;font-size:10px">${inv.autorizado_por.complete_name or ''|entity}</td>	
      </tr>
    </table>
</body>
</html>
