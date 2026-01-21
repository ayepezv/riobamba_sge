<html>
<head>
</head>
<body>
  <H3><left>DIRECCION FINANCIERA</center></H3>
<H4><left>PRSUPUESTOS</center></H4>
<H5><left>DOCUMENTOS PRESUPUESTARIOS</center></H5>
  <%
     total_certificado = aux = 0
     %> 

<table WIDTH="100%"  rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:11px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
    <td WIDTH="5%" style="text-align:left;font-size:11px">Num.</td>
    <td WIDTH="10%" style="text-align:left;font-size:11px">Documento</td>
    <td WIDTH="25%" style="text-align:left;font-size:11px">Beneficiario</td>
    <td WIDTH="15%" style="text-align:center;font-size:11px">Solicitante</td>
    <td WIDTH="5%" style="text-align:center;font-size:11px">Fecha</td>
    <td WIDTH="30%" style="text-align:center;font-size:11px">Descripcion</td>
    <td WIDTH="10%" style="text-align:center;font-size:11px">Monto</td>
  <thead/>

%for cp in objects :
<%
   aux += 1
   total_certificado += cp.amount_commited
   %>
<tr style="border: 1px solid black;page-break-inside:avoid" >
  <td WIDTH="5%" style="border: 1px solid black;text-align:left;font-size:9px;page-break-inside:avoid">${aux}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:left;font-size:9px;page-break-inside:avoid">${cp.name or ''|entity}</td>
  <td WIDTH="25%" style="border: 1px solid black;text-align:left;font-size:9px;page-break-inside:avoid">${cp.partner_id.name or ''|entity}</td>
  <td WIDTH="15%" style="border: 1px solid black;text-align:center;font-size:9px;page-break-inside:avoid">${cp.solicitant_id.complete_name or ''|entity}</td>
  <td WIDTH="5%" style="border: 1px solid black;text-align:center;font-size:9px;page-break-inside:avoid">${cp.date_commited or ''|entity}</td>
  <td WIDTH="30%" style="border: 1px solid black;text-align:center;font-size:9px;page-break-inside:avoid">${cp.notes or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:center;font-size:9px;page-break-inside:avoid">${cp.amount_commited or ''|entity}</td>
</tr>
%endfor
  <tr style="page-break-inside:avoid">
      <td WIDTH="5%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="10%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="25%" style="text-align:center;font-size:12px">${''}</td>
      <td width="15%" style="text-align:center;font-size:12px">${''}</td>
      <td width="5%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="30%" style="text-align:center;font-size:12px"><b>${'TOTAL USD'}</b></td>
      <td WIDTH="10%" style="text-align:center;font-size:12px"><b>${total_certificado}</b></td>
  </tr>
</table>
</body>
</html>
