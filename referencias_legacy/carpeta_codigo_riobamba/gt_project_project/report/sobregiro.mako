<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h2 style="text-align:center;" align="center">DIRECCION FINANCIERA</h1>
   <h4 style="text-align:center;" align="center">PARTIDAS EGRESO SOBREGIRADAS</h4>
   <table  cellspacing="0" border="0">
     <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
     <tr>
       <td>Desde: ${ o.poa_id.date_start }</td>
       <td>Hasta: ${ o.date_to }</td>
       <td></td>
       <td></td>
       <td></td>
       <td></td>
       <td></td>
       <td></td>
       <td></td>
     </tr>
     <tr style="page-break-inside:avoid;font-size:14px">
       <td width="10%">Codigo</td>
       <td width="33%">Denominacion</td>
       <td width="8%">Inicial</td>
       <td width="8%">Reforma</td>
       <td width="8%">Codificado</td>
       <td width="8%">Comprometido</td>
       <td width="8%">Sobregiro Comprometido</td>
       <td width="8%">Devengado</td>
       <td width="8%">Sobregiro Devengado</td>
     </tr>
    </thead>
    <%
       ti=tr=tcodif=tcomp=td=tsc=tsd=0
       %>
    %for line in o.line_ids:
    <%
       ti+=line.planned_amount
       tr+=line.reform_amount
       tcodif+=line.codificado_amount
       tcomp+=line.commited_amount
       td+=line.devengado_amount
       tsc+=line.sobregiro_commited
       tsd+=line.sobregiro_devengado
       %>
    <tr style="page-break-inside:avoid;font-size:14px">
      <td width="10%" style="font-size:14px;text-align:left">${line.code}</td>
      <td width="33%" style="font-size:14px;text-align:left">${line.name}</td>
      <td width="8%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.planned_amount)}</td>
      <td width="8%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.reform_amount)}</td>
      <td width="8%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.codificado_amount)}</td>
      <td width="8%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.commited_amount)}</td>
      <td width="8%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.sobregiro_commited)}</td>
      <td width="8%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.devengado_amount)}</td>
      <td width="8%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.sobregiro_devengado)}</td>
    </tr>
    %endfor   
    <tr style="page-break-inside:avoid;font-size:14px">
      <td width="10%" style="font-size:14px;text-align:right"><b>${}</b></td>
      <td width="33%" style="font-size:14px;text-align:right"><b>TOTALES</b></td>
      <td width="8%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(ti)}</b></td>
      <td width="8%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tr)}</b></td>
      <td width="8%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tcodif)}</b></td>
      <td width="8%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tcomp)}</b></td>
      <td width="8%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tsc)}</b></td>
      <td width="8%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(td)}</b></td>
      <td width="8%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tsd)}</b></td>
    </tr>
   </table>
</table>
%endfor
</body>
</html>
