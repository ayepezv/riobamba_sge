<html>
<head>
</head>
%for o in objects :
<%
   total = 0
   %> 
<body WIDTH="100%">
  <H3><left>VALIDACION DE ASIENTOS</center></H3>
<H4><left></center></H4>

<table WIDTH="100%"  rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:8px">
  <tr BGCOLOR="#D8D8D8">
    <td WIDTH="10%" style="text-align:left;font-size:10px">#</td>
    <td WIDTH="90%" style="text-align:left;font-size:10px">Descripcion</td>	
  <tr/>
  %for line in o.line_ids:
  
  <tr style="border: 1px solid black; page-break-inside: avoid;" >
    <td WIDTH="10%" style="border: 1px solid black;text-align:left;font-size:8px"></td>
    <td WIDTH="90%" style="border: 1px solid black;text-align:center;font-size:8px">${line.name}</td>
  </tr>
  %endfor
</table>
%endfor
</body>
</html>
