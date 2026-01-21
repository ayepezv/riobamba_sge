<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <%import time%>
   <H2><center>ACTA DE REVALORIZACION DE ACTIVOS FIJOS</center></H2>
   <p style="font-size:12px;text-align: justify"> En el Cant&oacute;n de ${user.company_id.city or ''|entity}, Provincia del ${user.company_id.state_id.name or ''|entity}, a los ${ o.date_start or ''}, en las oficinas de ${user.context_department_id.name or ''|entity}, de el ${user.company_id.name or ''|entity}, se re&uacute;nen la comisi&oacute;n para la actualizacion de los registros de inventarios al valor actual de mercado de los siguientes bienes institucionales. Conforme lo indica el Reglamento General para la Administración, Utilización y Control de los Bienes y Existencias del Sector Público.</p>
   <br>
   <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
</table>
  <%
     totala=totaln=totald=0
     %>

%for categoria in o.line_ids:
<table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
  <tr>
    <th width="60%" style="text-align:left;" ><b> CATEGORIA: ${categoria.categ_id.name}</b></th>
  </tr>
</table>
<table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
  <%
     totalac=totalnc=totaldc=a=0
     %>
     <thead style="border-collapse:collapse;page-break-inside:avoid;font-size:12px">
       <tr>
	 <th style="font-size:11px" width="5%" align="center">Num.</td>
	 <th style="font-size:11px" width="15%" align="center">C&oacute;digo</td>
         <th style="font-size:10px" width="30%" align="center">Descripci&oacute;n</b></td>
         <th style="font-size:10px" width="10%" align="center">N&uacute;mero Serie</td>
         <th style="font-size:10px" width="10%" align="center">Fecha de Adquisici&oacute;n</td>
         <th style="font-size:10px" width="10%" align="center">Valor Anterior</td>
         <th style="font-size:10px" width="10%" align="center">Nuevo Valor </td>
         <th style="font-size:10px" width="10%" align="center">Diferencia </td>
</tr>
</thead>

  %for activo in categoria.line_ids:
  <%
     totalac+=activo.rev_id.valor_ant
     totalnc+=activo.rev_id.valor
     totaldc+=activo.rev_id.diferencia
     totala+=activo.rev_id.valor_ant
     totaln+=activo.rev_id.valor
     totald+=activo.rev_id.diferencia
     a+=1
     %>
  <tr style="border-collapse:collapse;font-size:12px;page-break-inside:avoid">
    <td style="font-size:10px" width="5%">${a}</td>
    <td style="font-size:10px" width="15%">${activo.rev_id.asset_id.code or ''|entity}</td>
    <td style="font-size:10px" width="30%">${activo.rev_id.asset_id.name or ''|entity}</td>
    <td style="font-size:10px" width="10%" align="center">${activo.rev_id.asset_id.serial_number or ''|entity}</td>  
    <td style="font-size:10px" width="10%" align="center">${activo.rev_id.asset_id.purchase_date or ''|entity}</td>
    <td style="font-size:10px" width="10%" align="center">${activo.rev_id.valor_ant or ''|entity}</td>
    <td style="font-size:10px" width="10%" align="right">${activo.rev_id.valor or ''|entity}</td>
    <td style="font-size:10px" width="10%" align="right">${activo.rev_id.diferencia or ''|entity}</td>
  </tr>
  %endfor
  <tr style="page-break-inside:avoid">
  <td style="font-size:10px" width="5%"></td>
  <td style="font-size:10px" width="15%"></td>
  <td style="font-size:10px" width="30%"></b></td>
<td style="font-size:10px" width="10%" align="center"></td>
<td style="font-size:10px" width="10%" align="center"><b>TOTAL CATEGORIA</b></td>
<td style="font-size:10px" width="10%" align="right">${totalac or ''|entity}</td>
<td style="font-size:10px" width="10%" align="right">${totalnc or ''|entity}</td>
<td style="font-size:10px" width="10%" align="right">${totaldc or ''|entity}</td>
</tr>
  %endfor   
  <tr style="page-break-inside:avoid">
  <td style="font-size:10px" width="5%"></td>
  <td style="font-size:10px" width="15%"></td>
  <td style="font-size:10px" width="35%"></b></td>
<td style="font-size:10px" width="10%" align="center"></td>
<td style="font-size:10px" width="10%" align="center"><b>TOTAL GENERAL</b></td>
<td style="font-size:10px" width="10%" align="right">${totala or ''|entity}</td>
<td style="font-size:10px" width="10%" align="right">${totaln or ''|entity}</td>
<td style="font-size:10px" width="10%" align="right">${totald or ''|entity}</td>
</tr>
</table>

%endfor
<br>
<table width="100%" style="page-break-inside:avoid;text-align:justify">
  <p style="text-align:justify;font-size:12px">La presente acta se la suscribe y firma en  dos ejemplares por parte de la comisión, amparado a lo que dispone el Artículo 3 literal b) del Reglamento  General para la Administración, Utilización, Manejo y Control de los Bienes y Existencias del Sector Público.</p>
</table>
<br>
<br>
<br>
<br>
<table WIDTH="100%" style="font-size:10px" >	
  <tr> 
    <td WIDTH="33%"><center>__________________________</center></td>
    <td WIDTH="33%"><center>__________________________</center></td>
    <td WIDTH="33%"><center>__________________________</center></td>
</tr>
  <tr> 
    <td WIDTH="33%"><center>ADMINISTRADOR DE BIENES</center></td>
    <td WIDTH="33%"><center>DIRECTOR ADMINISTRATIVO</center></td>
    <td WIDTH="33%"><center>DIRECTOR FINANCIERO</center></td>
</tr>
</table>
</body>
</html>
