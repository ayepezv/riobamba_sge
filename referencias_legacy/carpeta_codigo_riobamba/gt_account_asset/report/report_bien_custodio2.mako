<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  <H2><center>ACTA DE ENTREGA RECEPCION DE BIENES</center></H2>
  <%import time%>
  <p style="font-size:14;text-align:justify">En el Cant&oacute;n de ${user.company_id.city or ''|entity}, Provincia del ${user.company_id.state_id.name or ''|entity}, el ${time.strftime('%Y-%m-%d') or ''|entity}, en las oficinas de ${user.context_department_id.name or ''|entity}, de el ${user.company_id.name or ''|entity}, se re&uacute;nen por una parte ${user.context_department_id.coordinador_id.complete_name or ''|entity}, en calidad de ${user.context_department_id.coordinador_id.job_id.name or ''|entity}, y por otra, ${objects[0].employee_id.complete_name or ''|entity}, con el fin de realizar el acta de entrega recepci&oacute;n de los bienes que se detallan a continuaci&oacute;n, conforme lo indica el Art. 3 del Reglamento General para la Administración, Utilización y Control de los Bienes y Existencias del Sector Público.</p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
        <th style="font-size:11px;text-align:center" width="5%">Nro.</th>
        <th style="font-size:11px;text-align:center" width="20%">CODIGO</th>
        <th style="font-size:11px;text-align:center" width="45%">DESCRIPCION</th>
        <th style="font-size:11px;text-align:center" width="20%">SERIE</th>
        <th style="font-size:11px;text-align:center" width="10%">VALOR</th>
    </thead>
  <% a=valor_total=0%>
     %for acc in objects :
  <%
     a+=1
     valor_total += acc.purchase_value
     %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="20%" style="font-size:11px;text-align:left">${acc.code}</td>
      <td width="45%" style="font-size:11px;text-align:left">${acc.name}</td>
      <td width="20%" style="font-size:11px;text-align:center">${acc.serial_number}</td>
      <td width="10%" style="font-size:11px;text-align:right">${acc.purchase_value}</td>
    </tr>
    %endfor
<table WIDTH=1000 style="font-size:14px" >	
  <tr WIDTH=1000 style="page-break-inside:avoid"> <b>		
      <td  width="15%" ></td>
      <td  width="35%" ></b></td>
<td  width="10%" ></td>
<td  width="35%" >Total</td>
<td  width="10%" align="right">${valor_total}</td>
</tr>
</table>
<br>
<table width="100%" style="page-break-inside:avoid;text-align:justify">
  <p style="text-align:justify;font-size:12px">La presente acta de entrega y recepción se la suscribe y firma en  dos ejemplares del mismo tenor amparado a lo que dispone el Artículo 3 literal b) del Reglamento  General para la Administración, Utilización, Manejo y Control de los Bienes y Existencias del Sector Público, señalando además que a partir de la presente fecha dichos bienes quedan bajo su responsabilidad y velará por la buena conservación, cuidado, administración, utilización y el buen uso, según lo estipula el Articulo 3 literal c) del mismo Reglamento; hasta que sea devuelto a esta Unidad Administrativa.</p>
<br>
<br>
<br>
  <tr>
    <th width="50%" style="text-align:center;font-size:10px">________________________</th>
    <th width="50%" style="text-align:center;font-size:10px">________________________</th>
  </tr>
  <tr>
    <th width="50%" style="text-align:center;font-size:10px">RECIBI CONFORME</th>
    <th width="50%" style="text-align:center;font-size:10px">REVISADO/AUTORIZADO</th>
  </tr>
  <tr>
    <td width="50%" style="text-align:center;font-size:10px">${objects[0].employee_id.complete_name or ''|entity}</td>
    <td width="50%" style="text-align:center;font-size:10px">${user.context_department_id.coordinador_id.complete_name or ''|entity}</td>
  </tr>
</table>
</table>
</html>
