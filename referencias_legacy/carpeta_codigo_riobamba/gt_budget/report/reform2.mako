<html>
  <head>
    <style type="text/css">
      ${css}
    </style>
  </head>
  <body>
    %for o in objects:
    <H3><left>REFORMA PRESUPUESTARIA : ${o.name} de el: ${o.date}</center></H3>
<H4><left>ORDENANZA REFORMATORIA</center></H4>
<H5><left>ASIGANCION SEGUN EL OBJETO DEL GASTO</center></H5>
%if o.line_ids:
<H6><left>PARTIDAS ORIGEN o DISMINUCION</center></H6>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:8px">
  <thead style="display: table-header-group">
    <tr>
      <th style="font-size:8px" width="52%"></th>
      <th style="font-size:8px" width="17%">TRASPASO DE CREDITO</th>
      <th style="font-size:8px" width="27%"></th>
    </tr>
  </thead>
</table>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:8px">
  <thead style="display: table-header-group">
    <tr>
      <th style="font-size:8px" width="15%">PARTIDA</th>
      <th style="font-size:8px" width="31%">CONCEPTO</th>
      <th style="font-size:8px" width="9%">PRESUPUESTO INICIAL</th>
      <th style="font-size:8px" width="9%">AUMENTO</th>
      <th style="font-size:8px" width="9%">DISMINUCION</th>
      <th style="font-size:8px" width="9%">SUPLEMENTOS</th>
      <th style="font-size:8px" width="9%">REDUCCIONES</th>
      <th style="font-size:8px" width="9%">PRESUPUESTO FINAL</th>
    </tr>
  </thead>
  <% final =  0 
     %>
  %for line in o.line_ids:
  <% 
     final = line.budget_id.planned_amount - line.monto
     %>
     <tr style="page-break-inside:avoid">
       <td width="15%" style="font-size:8px;text-align:center">${line.budget_id.code}</td>
       <td width="31%" style="font-size:8px;text-align:left">${line.budget_id.name}</td>
       <td width="9%" style="font-size:8px;text-align:right">${line.budget_id.planned_amount}</td>
       %if line.traspaso:
       <td width="9%" style="font-size:8px;text-align:right">${line.monto}</td>
       %endif
       <td width="9%" style="font-size:8px;text-align:right">${0}</td>
       <td width="9%" style="font-size:8px;text-align:right">${0}</td>
       <td width="9%" style="font-size:8px;text-align:right">${0}</td>
       %if not line.traspaso:
       <td width="9%" style="font-size:8px;text-align:right">${line.monto}</td>
       %endif
       <td width="9%" style="font-size:8px;text-align:right">${final}</td>
     </tr>
     %endfor
</table>
%endif
%if o.line_ids2:
<H6><left>PARTIDAS DESTINO o AUMENTO</center></H6>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:8px">
  <thead style="display: table-header-group">
    <tr>
      <th style="font-size:8px" width="52%"></th>
      <th style="font-size:8px" width="17%">TRASPASO DE CREDITO</th>
      <th style="font-size:8px" width="27%"></th>
    </tr>
  </thead>
</table>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:8px">
  <thead style="display: table-header-group">
    <tr>
      <th style="font-size:8px" width="15%">PARTIDA</th>
      <th style="font-size:8px" width="31%">CONCEPTO</th>
      <th style="font-size:8px" width="9%">PRESUPUESTO INICIAL</th>
      <th style="font-size:8px" width="9%">AUMENTO</th>
      <th style="font-size:8px" width="9%">DISMINUCION</th>
      <th style="font-size:8px" width="9%">SUPLEMENTOS</th>
      <th style="font-size:8px" width="9%">REDUCCIONES</th>
      <th style="font-size:8px" width="9%">PRESUPUESTO FINAL</th>
    </tr>
  </thead>
  <% final1 =  0 
     %>
  %for line in o.line_ids2:
  <% 
     final1 = line.budget_id.planned_amount + line.monto
     %>
     <tr style="page-break-inside:avoid">
       <td width="15%" style="font-size:8px;text-align:center">${line.budget_id.code}</td>
       <td width="31%" style="font-size:8px;text-align:left">${line.budget_id.name}</td>
       <td width="9%" style="font-size:8px;text-align:right">${line.budget_id.planned_amount}</td>
       <td width="9%" style="font-size:8px;text-align:right">${0}</td>
       %if line.traspaso:
       <td width="9%" style="font-size:8px;text-align:right">${line.monto}</td>
       %endif
       <td width="9%" style="font-size:8px;text-align:right">${0}</td>
       %if not line.traspaso:
       <td width="9%" style="font-size:8px;text-align:right">${line.monto}</td>
       %endif
       <td width="9%" style="font-size:8px;text-align:right">${0}</td>
       <td width="9%" style="font-size:8px;text-align:right">${final1}</td>
     </tr>
     %endfor
</table>
%endif
</body>
<table style="page-break-inside:avoid" width="100%">
  <tr style="height:35px">
    <th></th>
    <th></th>
    <th></th>
  </tr>
  <tr style="height:35px">
    <th></th>
    <th></th>
    <th></th>
  </tr>
  <tr style="font-size:11px">
    <th width="33%">JEFATURA PRESUPUESTOS</th>
    <th width="33%">DIRECCION FINANCIERA</th>
    <th width="33%">ALCALDE</th>
  </tr>  
  <tr style="height:35px">
    <th></th>
    <th></th>
    <th></th>
  </tr>
  <tr style="height:35px">
    <th>__________________</th>
    <th>__________________</th>
    <th>__________________</th>
  </tr>
</table>
%endfor
</html>
