<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h2 style="text-align:center;" align="center">DIRECCION ADMINISTRATIVA</h2>
   <h2 style="text-align:center;" align="center">BIENES POR CUSTODIO</h2>
   <%
      total=total_categoria=0
      %>
   %for categoria in get_categories_custodio(o):
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
     <thead>
       <tr>
	 <th width="60%" style="text-align:left;" > CATEGORIA: ${categoria.name}</th>
       </tr>
     </thead>
     %endfor   
   </table>
</table>
   %endfor
</body>
</html>
