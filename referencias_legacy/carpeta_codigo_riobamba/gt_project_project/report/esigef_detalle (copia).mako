<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h2 style="text-align:center;" align="center">DIRECCION FINANCIERA</h1>
   <h4 style="text-align:center;" align="center">PRESUPUESTO SIGEF DETALLADO</h4>
   <table class="table_basic table_title">
     <tr>
       <td>Desde: ${ o.date_start }</td>
       <td>Hasta: ${ o.date_stop }</td>
     </tr>
   </table>
   <h5 style="text-align:center;" align="center">INGRESOS</h5>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:14px">
     <thead>
     <tr style="border-collapse:collapse;font-size:14px">
       <th width="5%">Codigo</th>
       <th width="35%">Denominacion</th>
       <th width="7%">Inicial</th>
       <th width="7%">Reforma</th>
       <th width="7%">Codificado</th>
       <th width="7%">Comprometido</th>
       <th width="7%">Devengado</th>
       <th width="7%">Ejecutado</th>
       <th width="5%">R4</th>
       <th width="5%">R6</th>
       <th width="5%">R7</th>
       <th width="5%">R8</th>
     </tr>
    </thead>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:14px">
    <%
       ti=tr=tcodif=tcomp=td=te=0
       %>
    %for line in o.line_ids:
    <%
       ti+=line.inicial
       tr+=line.reforma
       tcodif+=line.codificado
       tcomp+=line.comprometido
       td+=line.devengado
       te+=line.ejecutado
       %>
    <tr style="border-collapse:collapse;font-size:14px">
      <td width="5%" style="font-size:14px;text-align:left">${line.code}</td>
      <td width="35%" style="font-size:14px;text-align:left">${line.post_id.name}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.inicial}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.reforma}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.codificado}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.comprometido}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.devengado}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.ejecutado}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r4}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r6}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r7}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r8}</td>
    </tr>
    %endfor   
    <tr style="border-collapse:collapse;font-size:14px">
      <td width="5%" style="font-size:14px;text-align:right"><b>${}</b></td>
      <td width="35%" style="font-size:14px;text-align:right"><b>TOTALES INGRESOS</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${ti}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${tr}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${tcodif}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${tcomp}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${td}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${te}</b></td>
    </tr>
   </table>
</table>
   <h5 style="text-align:center;" align="center">GASTOS</h5>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:14px">
     <thead>
       <tr style="border-collapse:collapse;font-size:14px">
	 <th width="5%">Codigo</th>
	 <th width="35%">Denominacion</th>
	 <th width="7%">Inicial</th>
	 <th width="7%">Reforma</th>
	 <th width="7%">Codificado</th>
	 <th width="7%">Comprometido</th>
       <th width="7%">Devengado</th>
       <th width="7%">Ejecutado</th>
       <th width="5%">R4</th>
       <th width="5%">R6</th>
       <th width="5%">R7</th>
       <th width="5%">R8</th>
     </tr>
     </thead>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:14px">
     
     <%
       ti=tr=tcodif=tcomp=td=te=0
       %>
    %for line in o.line_ids2:
    <%
       ti+=line.inicial
       tr+=line.reforma
       tcodif+=line.codificado
       tcomp+=line.comprometido
       td+=line.devengado
       te+=line.ejecutado
       %>
    <tr style="border-collapse:collapse;font-size:14px">
      <td width="5%" style="font-size:14px;text-align:left">${line.code}</td>
      <td width="35%" style="font-size:14px;text-align:left">${line.post_id.name}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.inicial}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.reforma}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.codificado}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.comprometido}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.devengado}</td>
      <td width="7%" style="font-size:14px;text-align:right">${line.ejecutado}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r4}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r6}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r7}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r8}</td>
    </tr>
    %endfor   
    <tr style="border-collapse:collapse;font-size:14px">
      <td width="5%" style="font-size:14px;text-align:right"><b>${}</b></td>
      <td width="35%" style="font-size:14px;text-align:right"><b>TOTALES GASTOS</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${ti}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${tr}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${tcodif}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${tcomp}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${td}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${te}</b></td>
    </tr>
   </table>
   %endfor
</table>
  <table width="100%">
    <tr style="height:35px">
      <th>__________________</th>
      <th>__________________</th>
      <th>__________________</th>
    </tr>
    <tr style="font-size:22px">
      <th width="33%">Maxima Autoridad</th>
      <th width="33%">Director Financiero</th>
      <th width="33%">Contador</th>
    </tr>  
  </table>
</body>
</html>
