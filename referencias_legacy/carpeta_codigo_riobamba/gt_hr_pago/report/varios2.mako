<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h4 style="text-align:center;" align="center">GESTIÓN DE TALENTO HUMANO</h2>
   <h4 style="text-align:center;" align="center">PAGOS: ${o.name}</h2>
   <h4 style="text-align:center;" align="center">PERIODO: ${o.period_id.name}</h2>
   <%
      total=0
      %>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="5%" style="text-align:center;">Numero</th>
	 <th width="65%" style="text-align:center;">Descontado/Beneficiario</th>
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
	 <td width="65%" style="font-size:11px;text-align:left">${line.descontado_id.complete_name}: ${line.name.ced_ruc} - ${line.name.name}</td>
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
     <tr style="height:35px">
	 <th>___________________________________________________________________________</th>
     </tr>
     <tr style="height:35px">
     </tr>  
     <tr style="height:35px">
     </tr>
     <table width="100%">
       <tr style="height:35px">
       </tr>
       <tr style="height:35px">
	 <th>__________________</th>
	 <th>__________________</th>
       </tr>
       <tr style="font-size:12px">
	   
	 <th width="50%">${user.context_department_id.coordinador_id.complete_name or ''}</th>
	  <th width="50%">${user.employee_id.complete_name or ''}</th>
	 <th width="50%"></th>
       </tr>  
       <tr style="font-size:12px">
	 <th width="50%">Autorizado</th>
	  <th width="50%">Realizado por:</th>
	 
       </tr>  
	    
 
     </table>
     %endfor
 </body>
</html>
