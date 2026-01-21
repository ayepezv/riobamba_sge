<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h6 style="text-align:center;" align="center">DIRECCION ADMINISTRATIVA</h6>
     <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">  
     <tr>
       <td style="text-align:center;font-size:11px" align="center"><b>BAJA DE BIENES NRO. ${o.name or ''|entity}</b></td>
     </tr>
   </table>
   <%
      total_todo=total_categoria=total_todo_ac=0
      %>
   <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
     <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Documento:</td>
      <td style="font-size:11px" width="42%">${o.document or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Autorizado por:</td>
      <td style="font-size:11px" width="42%">${ o.autorizado_por.complete_name or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Detalle:</td>
      <td style="font-size:11px" width="42%">${ o.detail or  ''}</td>
    </tr>	
  </table>
  <%import time%>
  <p style="border-collapse:collapse;font-size:12px">En el canton de ${user.company_id.city or ''|entity}, Provincia del ${user.company_id.state_id.name or ''|entity}, el ${o.date or ''|entity}, en las oficinas de ${user.context_department_id.name or ''|entity}, de el ${user.company_id.name or ''|entity}, se procede con la baja de los bienes que se detallan a continuacion.</p>
  <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
    <thead style="border-collapse:collapse;font-size:12px">
      <tr>
	<th width="5%">#</th>
	<th width="25%" style="text-align:left;">Codigo</th>
	<th width="55%">Descripcion</th>
	<th width="8%">Valor Compra</th>
	<th width="7%">Valor Actual</th>
      </tr>
    </thead>
  </table>
   %for categoria in get_categories_baja(o):
  <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
   <tr>
     <th width="60%" style="text-align:left;" ><b> CATEGORIA: ${categoria.name}</b></th>
   </tr>
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
    <%
       total_categoria=total_actual=a=0
      %>
     %for activo in get_activos_categoria(o,categoria.id):
     <%
	total_categoria+=activo.purchase_value
	total_actual+=activo.valor_actual
	a+=1
	%>
       <tr style="border-collapse:collapse;font-size:12px">
	 <td width="5%" style="font-size:11px;text-align:left">${ a }</td>
	 <td width="25%" style="font-size:11px;text-align:left">${ activo.code }</td>
	 <td width="55%" style="font-size:11px;text-align:left">${ activo.name }</td>
	 <td width="8%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(activo.purchase_value) }</td>
	 <td width="7%" style="font-size:11px;text-align:right">${ '{:,.2f}'.format(activo.valor_actual) }</td>
       </tr>
     %endfor
      <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
       <tr>
	 <!--td width="35%" style="font-size:11px;text-align:left">${}</td>
	 <td width="35%" style="font-size:11px;text-align:right">${}</td>
	 <td width="7%" style="font-size:11px;text-align:right">${}</td>
	 <td width="7%" style="font-size:11px;text-align:right">${}</td-->
	 <td width="80%" style="font-size:11px;text-align:right"><b>TOTAL CATEGORIA</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${total_categoria}</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${  '{:,.2f}'.format(total_actual) }</b></td>
       </tr>
     </table>
     <%
	total_todo_ac+=total_actual
	total_todo+=total_categoria
	%>
     %endfor   
   </table>
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <!--td width="35%" style="font-size:11px;text-align:left">${}</td>
	 <td width="35%" style="font-size:11px;text-align:right">${}</td>
	 <td width="7%" style="font-size:11px;text-align:right">${}</td>
	 <td width="7%" style="font-size:11px;text-align:right">${}</td-->
	 <td width="80%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${  '{:,.2f}'.format(total_todo) }</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${ '{:,.2f}'.format(total_todo_ac) }</b></td>
       </tr>
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
	<td width="33%" style="text-align:center;font-size:10px">${o.autorizado_por.complete_name or ''|entity}</td>
      </tr>
    </table>
</body>
</html>
