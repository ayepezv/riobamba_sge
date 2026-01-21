<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h2 style="text-align:center;" align="center">DIRECCION ADMINISTRATIVA</h2>
   <h2 style="text-align:center;" align="center">CUADRO GENERAL DEPRECIACION ACTIVOS</h2>
   <h2 style="text-align:center;" align="center">FECHAS: ${ o.date_start } - ${ o.date_stop }</h2>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="80%" style="text-align:center;">Categoria</th>
	 <th width="20%" style="text-align:center;">Total Depreciacion</th>
       </tr>
     </thead>
   </table>
   %for categ_id in get_categories_total_dep(o):
     <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="80%" style="font-size:11px;text-align:left">${ get_name_total_dep(categ_id) }</td>
	 <td width="20%" style="font-size:11px;text-align:right">${ get_act_total_dep(o,categ_id) }</td>
       </tr>
     </table>
     %endfor
      <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr>
	 <td width="80%" style="font-size:11px;text-align:right"><b>TOTALES</b></td>
	 <td width="20%" style="font-size:11px;text-align:right"><b>${ get_total_dep(o) }</b></td>
       </tr>
     </table>
   </table>
</table>
   %endfor
</body>
</html>
