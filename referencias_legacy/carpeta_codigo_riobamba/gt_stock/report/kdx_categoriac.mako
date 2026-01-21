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
       <th width="80%">Categoria</th>
       <th width="10%">Saldo Inventario</th>
       <th width="10%">Saldo Contabilidad</th>
     </tr>
    </thead>
    <%
       inventario=contable=0
       %>
    %for line in o.line_ids:
    <%
       inventario+=line.saldo
       contable+=line.saldoc
       %>
    <tr style="border-collapse:collapse;font-size:12px">
      <td width="80%" style="font-size:11px;text-align:left">${line.categ_id.code} - ${line.categ_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.saldo}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.saldoc}</td>
    </tr>
    %endfor   
    <tr style="border-collapse:collapse;font-size:12px">
      <td width="80%" style="font-size:11px;text-align:right"><b>TOTAL CORRIENTE</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${inventario}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${contable}</b></td>
    </tr>
   </table>
   <h5 style="text-align:center;" align="center">INVERSION</h5>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
     <tr>
       <th width="80%">Categoria</th>
       <th width="10%">Saldo Inventario</th>
       <th width="10%">Saldo Contable</th>
     </tr>
    </thead>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <%
       inventarioi=contablei=0
       %>
    %for line in o.line_ids2:
    <%
       inventarioi+=line.saldo
       contablei+=line.saldoc
       %>
    <tr style="border-collapse:collapse;font-size:12px">
      <td width="80%" style="font-size:11px;text-align:left">${line.categ_id.code} - ${line.categ_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.saldo}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.saldoc}</td>
    </tr>
    %endfor   
    <tr style="border-collapse:collapse;font-size:12px">
      <td width="80%" style="font-size:11px;text-align:right"><b>TOTAL INVERSION</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${inventarioi}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${contablei}</b></td>
    </tr>
    <tr style="border-collapse:collapse;font-size:12px">
      <td width="80%" style="font-size:11px;text-align:right"><b>TOTAL GENERAL</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${inventario+inventarioi}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${contable+contablei}</b></td>
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
