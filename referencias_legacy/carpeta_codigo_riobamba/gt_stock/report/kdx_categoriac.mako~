<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h2 style="text-align:center;" align="center">DIRECCION FINANCIERA</h1>
   <h4 style="text-align:center;" align="center">INVENTARIO:SALDOS DE BODEGA POR CATEGORIA</h4>
   <table class="table_basic table_title">
     <tr>
       <td>Bodega General</td>
       <td>Desde: ${ o.date_start }</td>
       <td>Hasta: ${ o.date_end }</td>
     </tr>
   </table>
   <h5 style="text-align:center;" align="center">CORRIENTE</h5>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
     <tr>
       <th width="60%">Categoria</th>
       <th width="10%">Saldo Inicial</th>
       <th width="10%">Ingreso</th>
       <th width="10%">Egreso</th>
       <th width="10%">Saldo Final</th>
     </tr>
    </thead>
    <%
       inicial=ingreso=egreso=saldo=0
       %>
    %for line in o.line_ids:
    <%
       inicial+=line.inicial
       ingreso+=line.ingreso
       egreso+=line.egreso
       saldo+=line.saldo
       %>
    <tr>
      <td width="60%" style="font-size:11px;text-align:left">${line.categ_id.code} - ${line.categ_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.inicial}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.ingreso}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.egreso}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.saldo}</td>
    </tr>
    %endfor   
    <tr>
      <td width="60%" style="font-size:11px;text-align:right"><b>TOTAL CORRIENTE</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${inicial}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${ingreso}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${egreso}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${saldo}</b></td>
    </tr>
   </table>
<h5 style="text-align:center;" align="center">INVERSION</h5>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
     <tr>
       <th width="60%">Categoria</th>
       <th width="10%">Saldo Inicial</th>
       <th width="10%">Ingreso</th>
       <th width="10%">Egreso</th>
       <th width="10%">Saldo Final</th>
     </tr>
    </thead>
    <%
       iniciali=ingresoi=egresoi=saldoi=0
       %>
    %for line in o.line_ids2:
    <%
       iniciali+=line.inicial
       ingresoi+=line.ingreso
       egresoi+=line.egreso
       saldoi+=line.saldo
       %>
    <tr>
      <td width="60%" style="font-size:11px;text-align:left">${line.categ_id.code} - ${line.categ_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.inicial}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.ingreso}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.egreso}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.saldo}</td>
    </tr>
    %endfor   
    <tr>
      <td width="60%" style="font-size:11px;text-align:right"><b>TOTAL INVERSION</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${iniciali}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${ingresoi}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${egresoi}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${saldoi}</b></td>
    </tr>
    <tr>
      <td width="60%" style="font-size:11px;text-align:right"><b>TOTAL GENERAL</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${inicial+iniciali}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${ingreso+ingresoi}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${egreso+egresoi}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${saldo+saldoi}</b></td>
    </tr>
   </table>
   %endfor
</table>
  <table width="100%">
    <tr style="height:35px">
      <th>__________________</th>
    </tr>
    <tr style="font-size:22px">
      <th width="33%">Jefe Inventario</th>
    </tr>  
  </table>
</body>
</html>
