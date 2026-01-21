<html>
  <head>
    <style type="text/css">
      ${css}
    </style>
  </head>
  <body>
    <%import time%>

    <H2><center>ACTA DE REVALORIZACION DE ACTIVOS FIJOS</center></H2>
    <p style="font-size:12px;text-align: justify"> En el Cant&oacute;n de ${user.company_id.city or ''|entity}, Provincia del ${user.company_id.state_id.name or ''|entity}, a los ${ objects[0].date or ''}, en las oficinas de ${user.context_department_id.name or ''|entity}, de el ${user.company_id.name or ''|entity}, se re&uacute;nen la comisi&oacute;n para la actualizacion de los registros de inventarios al valor actual de mercado de los siguientes bienes institucionales. Conforme lo indica el Reglamento General para la Administración, Utilización y Control de los Bienes y Existencias del Sector Público.</p>
    <br>
    <br>
    <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">	
      <thead style="display: table-header-group">
	<th style="font-size:11px" width="15%" align="center">C&oacute;digo</td>
<th style="font-size:10px" width="35%" align="center">Descripci&oacute;n</b></td>
<th style="font-size:10px" width="10%" align="center">N&uacute;mero Serie</td>
<th style="font-size:10px" width="25%" align="center">Categoria</td>
<th style="font-size:10px" width="8%" align="center">Fecha de Adquisici&oacute;n</td>
<th style="font-size:10px" width="8%" align="center">Valor Anterior</td>
<th style="font-size:10px" width="8%" align="center">Nuevo Valor </td>

</thead>
<%
   total_anterior = total_nuevo = 0
   %>
%for inv in objects:
<%
   total_anterior += inv.valor_ant   
   total_nuevo += inv.valor
%>
<tr style="page-break-inside:avoid">
  <td style="font-size:10px" width="15%">${inv.asset_id.code or ''|entity}</td>
  <td style="font-size:10px" width="35%">${inv.asset_id.name or ''|entity}</td>
  <td style="font-size:10px" width="10%" align="center">${inv.asset_id.serial_number or ''|entity}</td>  
  <td style="font-size:10px" width="20%" align="center">${inv.asset_id.category_id.name or ''|entity}</td>
  <td style="font-size:10px" width="10%" align="center">${inv.asset_id.purchase_date or ''|entity}</td>
  <td style="font-size:10px" width="10%" align="center">${inv.valor_ant or ''|entity}</td>
  <td style="font-size:10px" width="10%" align="right">${inv.valor or ''|entity}</td>
</tr>
%endfor
<tr style="page-break-inside:avoid">
  <td style="font-size:10px" width="15%"></td>
  <td style="font-size:10px" width="35%"></b></td>
<td style="font-size:10px" width="10%" align="center"></td>
<td style="font-size:10px" width="20%" align="center"></td>
<td style="font-size:10px" width="10%" align="center">TOTALES</td>
<td style="font-size:10px" width="10%" align="right">${total_anterior or ''|entity}</td>
<td style="font-size:10px" width="10%" align="right">${total_nuevo or ''|entity}</td>
</tr>
</table>
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
