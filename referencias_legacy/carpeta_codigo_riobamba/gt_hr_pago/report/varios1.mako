<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h4 style="text-align:center;" align="center">TALENTO HUMANO</h2>
   <h4 style="text-align:center;" align="center">PAGOS: ${o.name}</h2>
   <%
      total=0
      %>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="5%" style="text-align:center;">Numero</th>
	 <th width="65%" style="text-align:center;">Beneficiario</th>
	 <th width="10%" style="text-align:center;">Subtotal</th>
	 <th width="10%" style="text-align:center;">Descuento</th>
	 <th width="10%" style="text-align:center;">Total</th>
       </tr>
     </thead>
   </table>
   <%
      a=0
      %>
   %for line in o.line_ids:
   <%
      total+=line.valor
      a+=1
      %>
     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="5%" style="font-size:11px;text-align:center">${a}</td>
	 %if line.descontado_id:
	 <td width="65%" style="font-size:11px;text-align:left">${line.name.ced_ruc} - ${line.name.name} : ${line.descontado_id.complete_name}</td>
	 %else:
	 <td width="65%" style="font-size:11px;text-align:left">${line.name.ced_ruc} - ${line.name.name}</td>
	 %endif
	 <td width="10%" style="font-size:11px;text-align:right">${line.monto}</td>
	 <td width="10%" style="font-size:11px;text-align:right">${line.descuento}</td>
	 <td width="10%" style="font-size:11px;text-align:right">${line.valor}</td>
       </tr>
     </table>
     %endfor
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <!--td width="35%" style="font-size:11px;text-align:left">${}</td>
	 <td width="35%" style="font-size:11px;text-align:right">${}</td>
	 <td width="7%" style="font-size:11px;text-align:right">${}</td>
	 <td width="7%" style="font-size:11px;text-align:right">${}</td-->
	 <td width="93%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
	 <td width="7%" style="font-size:11px;text-align:right"><b>${total}</b></td>
       </tr>
     </table>
     %endfor
  <table width="100%" style="page-break-inside:avoid">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="font-size:11px">
      <th width="50%">CREADO POR</th>
      <th width="50%">AUTORIZADO</th>
    </tr>  
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
      </tr>
    <tr style="height:35px">
      <th>______________________</th>
      <th>______________________</th>
    </tr>
    <tr style="font-size:11px">
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
    </tr>
    <tr style="font-size:11px">
      <th width="25%">REVISADO POR</th>
      <th width="25%">CONTADOR GENERAL</th>
      <th width="25%">DIRECTOR FINANCIERO</th>
    </tr>  
    <tr style="font-size:11px">
      <th width="25%"></th>
      <th width="25%"></th>
      <th width="25%">AUTORIZO TRANSFERENCIA</th>
    </tr>  
  </table>
 </body>
</html>
