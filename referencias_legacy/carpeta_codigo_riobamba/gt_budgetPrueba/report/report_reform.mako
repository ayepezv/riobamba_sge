<html>
<head>
</head>
<body>
  <H3><left>DIRECCION FINANCIERA</center></H3>
<H4><left>PRESUPUESTOS</center></H4>
<H5><left>REFORMAS PRESUPUESTARIOS</center></H5>
  <%
     total_aumento = total_disminucion = aux = 0
     %> 

<table WIDTH="100%"  rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:11px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
    <td WIDTH="5%" style="text-align:left;font-size:11px">Num.</td>
    <td WIDTH="25%" style="text-align:left;font-size:11px">Partida</td>
    <td WIDTH="5%" style="text-align:center;font-size:11px">Fecha</td>
    <td WIDTH="35%" style="text-align:left;font-size:11px">Descripcion</td>
    <td WIDTH="20%" style="text-align:left;font-size:11px">Tipo Reforma</td>
    <td WIDTH="10%" style="text-align:center;font-size:11px">Valor Reforma</td>
  <thead/>

%for ref in objects :
<%
   aux += 1
%>
<%
   if ref.type_transaction=='ampliacion':
       total_aumento += ref.amount
   else:
       total_disminucion += ref.amount
   %>
<tr style="border: 1px solid black;page-break-inside:avoid" >
  <td WIDTH="5%" style="border: 1px solid black;text-align:left;font-size:9px;page-break-inside:avoid">${aux}</td>
  <td WIDTH="25%" style="border: 1px solid black;text-align:left;font-size:9px;page-break-inside:avoid">${ref.budget_id.code or ''|entity}</td>
  <td WIDTH="5%" style="border: 1px solid black;text-align:left;font-size:9px;page-break-inside:avoid">${ref.date_done or ''|entity}</td>
  <td WIDTH="35%" style="border: 1px solid black;text-align:center;font-size:9px;page-break-inside:avoid">${ref.justification or ''|entity}</td>
  <td WIDTH="20%" style="border: 1px solid black;text-align:center;font-size:9px;page-break-inside:avoid">${ref.type_transaction or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:center;font-size:9px;page-break-inside:avoid">${ref.amount or ''|entity}</td>
</tr>
%endfor
<table WIDTH="100%"  rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:11px">
  <tr style="page-break-inside:avoid">
    <td WIDTH="5%" style="text-align:center;font-size:12px">${''}</td>
    <td WIDTH="5%" style="text-align:center;font-size:12px">${''}</td>
    <td width="5%" style="text-align:center;font-size:12px">${''}</td>
    <td width="15%" style="text-align:center;font-size:12px"><b>${'TOTALES'}</b></td>
    <td WIDTH="30%" style="text-align:center;font-size:12px"><b>Aumento : ${total_aumento}</b></td>
    <td WIDTH="30%" style="text-align:center;font-size:12px"><b>Disminucion : ${total_disminucion}</b></td>
  </tr>
</table>
</table>
</body>
</html>
