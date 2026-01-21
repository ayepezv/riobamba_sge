<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h2 style="text-align:center;" align="center">DIRECCION ADMINISTRATIVA</h2>
   <h2 style="text-align:center;" align="center">CUADRO GENERAL DE ACTIVOS : ${ o.opcion }</h2>
   <h2 style="text-align:center;" align="center">FECHAS: ${ o.date_start } - ${ o.date_stop }</h2>
   <%
      total_1=total_2=total_3=0
      %>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="60%" style="text-align:center;">Categor&iacute;a</th>
	 <th width="10%" style="text-align:center;">Total Art&iacute;culos</th>
	 <th width="15%" style="text-align:center;">Valor Adquisici&oacute;n</th>
	 <th width="15%" style="text-align:center;">Valor Actual</th>
       </tr>
     </thead>
   </table>
   <% 
      total_1 = total_2 = total_3 = aux = 0
      %>
   %for categ_id in get_categories_total(o):
   <% 
      aux_total_categ = get_numero_total(o,categ_id)
      aux += aux_total_categ
      %>
     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="60%" style="font-size:11px;text-align:left">${ get_name_total(categ_id) }</td>
	 <td width="10%" style="font-size:11px;text-align:right">${ aux_total_categ }</td>
	 <td width="15%" style="font-size:11px;text-align:right">${ get_adq_total(o,categ_id) }</td>
	 <td width="15%" style="font-size:11px;text-align:right">${ get_act_total(o,categ_id) }</td>
       </tr>
     </table>
     %endfor
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="60%" style="font-size:11px;text-align:right"><b>TOTALES</b></td>
	 <td width="10%" style="font-size:11px;text-align:right"><b>${ aux }</b></td>
	 <td width="15%" style="font-size:11px;text-align:right"><b>${ get_total_2(o) }</b></td>
	 <td width="15%" style="font-size:11px;text-align:right"><b>${ get_total_3(o) }</b></td>
       </tr>
     </table>
   </table>
</table>
   %endfor
</body>
</html>
