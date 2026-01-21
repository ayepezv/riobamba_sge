<html>
  <head>
    <style type="text/css">
      ${css}
    </style>
  </head>
  <body>
    <%import time%>

    <H2><center>ACTA DE ENTREGA RECEPCION INICIAL DE BIENES</center></H2>
    <p style="font-size:12px;text-align: justify"> En el Cant&oacute;n de ${user.company_id.city or ''|entity}, Provincia del ${user.company_id.state_id.name or ''|entity}, a los ${ objects[0].date_entrega or ''}, en las oficinas de ${user.context_department_id.name or ''|entity}, de el ${user.company_id.name or ''|entity}, se re&uacute;nen por una parte ${user.context_department_id.coordinador_id.complete_name or ''|entity}, en calidad de ${user.context_department_id.coordinador_id.job_id.name or ''|entity}, y por otra, ${objects[0].employee_id.complete_name or ''|entity}, con el fin de realizar la entrega recepci&oacute;n de los bienes que se detallan a continuaci&oacute;n, conforme lo indica el Art. 3 del Reglamento General para la Administración, Utilización y Control de los Bienes y Existencias del Sector Público.</p>
    <br>
    <br>
    <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">	
      <thead style="display: table-header-group">
	<th style="font-size:11px" width="15%" align="center">C&oacute;digo</td>
<th style="font-size:10px" width="35%" align="center">Descripci&oacute;n</b></td>
<th style="font-size:10px" width="10%" align="center">N&uacute;mero Serie</td>
<th style="font-size:10px" width="25%" align="center">Categoria</td>
<th style="font-size:10px" width="8%" align="center">Fecha de Adquisici&oacute;n</td>
<th style="font-size:10px" width="8%" align="center">Valor</td>
</thead>
<%
   total = 0
   %>
%for inv in objects:
<%
   total += inv.purchase_value
%>
<tr style="page-break-inside:avoid">
  <td style="font-size:10px" width="15%">${inv.code or ''|entity}</td>
  <td style="font-size:10px" width="35%">${inv.name or ''|entity}</td>
  <td style="font-size:10px" width="10%" align="center">${inv.serial_number or ''|entity}</td>
  <td style="font-size:10px" width="20%" align="center">${inv.category_id.name or ''|entity}</td>
  <td style="font-size:10px" width="10%" align="center">${inv.purchase_date or ''|entity}</td>
  <td style="font-size:10px" width="10%" align="right">${inv.purchase_value or ''|entity}</td>
</tr>
%endfor
<tr style="page-break-inside:avoid">
      <td style="font-size:10px" width="15%"></td>
      <td style="font-size:10px" width="35%"></b></td>
<td style="font-size:10px" width="10%" align="center"></td>
<td style="font-size:10px" width="20%" align="center"></td>
<td style="font-size:10px" width="10%" align="center">TOTAL</td>
<td style="font-size:10px" width="10%" align="right">${total or ''|entity}</td>
</tr>
</table>
<br>
<table width="100%" style="page-break-inside:avoid;text-align:justify">
  <p style="text-align:justify;font-size:12px">La presente acta de entrega y recepción se la suscribe y firma en  dos ejemplares del mismo tenor amparado a lo que dispone el Artículo 3 literal b) del Reglamento  General para la Administración, Utilización, Manejo y Control de los Bienes y Existencias del Sector Público, señalando además que a partir de la presente fecha dichos bienes quedan bajo su responsabilidad y velará por la buena conservación, cuidado, administración, utilización y el buen uso, según lo estipula el Articulo 3 literal c) del mismo Reglamento; hasta que sea devuelto a esta Unidad Administrativa.</p>
</table>
<br>
<br>
<br>
<br>
<table WIDTH="100%" style="font-size:10px" >	
  <tr> <b>		
      <td WIDTH="25%"> <center> ELABORADO</center></td>
      <td WIDTH="25%" > <center> ENTREGUE CONFORME</center></td>
      <td WIDTH="25%" > <center> RECIBI CONFORME</center></b></td>
%if inv.employee_id2: 
<td WIDTH="25%" > <center> RECIBI CONFORME</center></b></td>
%endif
</tr>
<tr> <b>		
    <td WIDTH="25%"> <center> ${user.employee_id.complete_name or ''|entity} </center></td>
    <td WIDTH="25%"> <center> ${user.context_department_id.coordinador_id.complete_name or ''|entity} </center></td>
    <td WIDTH="25%"> <center> ${inv.employee_id.complete_name or ''|entity} </center></b></td>
  %if inv.employee_id2: 
    <td WIDTH="25%"> <center> ${inv.employee_id2.complete_name or ''|entity} </center></b></td>
%endif
</tr>
</table>
    
</body>
</html>
