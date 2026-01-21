<html>
  <head>
    <style type="text/css">
      ${css}
    </style>
  </head>
  <body>
    %for o in objects:
    <H3><left>ORDENANZA REFORMATORIA</center></H3>
<H4><left>ASIGANCION SEGUN EL OBJETO DEL GASTO</center></H4>
<H5><left>REFORMA PRESUPUESTARIA : ${o.name} de el: ${o.date}</center></H5>
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
  <% 
     final = final2 = t_ini = t_au = t_dis = t_sup = t_red = 0 
     %>
  %for line in o.line_ids:
  <% 
     final1 = line.budget_id.planned_amount - line.monto
     final2 += final1
     t_ini += line.budget_id.planned_amount
     if line.traspaso:
         t_au += line.monto
     else:
         t_red += line.monto
     %>
  <tr style="page-break-inside:avoid">
    <td width="15%" style="font-size:8px;text-align:center">${line.budget_id.code}</td>
    <td width="31%" style="font-size:8px;text-align:left">${line.budget_id.name}</td>
    <td width="9%" style="font-size:8px;text-align:right">${'{:,.2f}'.format(line.budget_id.planned_amount)}</td>
    <td width="9%" style="font-size:8px;text-align:right">${0}</td>
    %if line.traspaso:
    <td width="9%" style="font-size:8px;text-align:right">${'{:,.2f}'.format(line.monto)}</td>
    %endif
    <td width="9%" style="font-size:8px;text-align:right">${0}</td>
    <td width="9%" style="font-size:8px;text-align:right">${0}</td>
    %if not line.traspaso:
    <td width="9%" style="font-size:8px;text-align:right">${'{:,.2f}'.format(line.monto)}</td>
    %endif
    <td width="9%" style="font-size:8px;text-align:right">${'{:,.2f}'.format(final1)}</td>
  </tr>
  %endfor
  %if len(o.line_ids)>0:
  <tr style="page-break-inside:avoid">
    <td width="15%" style="font-size:8px;text-align:center"><b>TOTALES</b></td>
    <td width="31%" style="font-size:8px;text-align:left"></td>
    <td width="9%" style="font-size:8px;text-align:right"><b>${'{:,.2f}'.format(t_ini)}</b></td>
    <td width="9%" style="font-size:8px;text-align:right"><b>${0}</b></td>
    %if line.traspaso:
    <td width="9%" style="font-size:8px;text-align:right"><b>${'{:,.2f}'.format(t_au)}</b></td>
    %endif
    <td width="9%" style="font-size:8px;text-align:right"><b>${0}</b></td>
    <td width="9%" style="font-size:8px;text-align:right"><b>${0}</b></td>
    %if not line.traspaso:
    <td width="9%" style="font-size:8px;text-align:right"><b>${'{:,.2f}'.format(t_red)}</b></td>
    %endif
    <td width="9%" style="font-size:8px;text-align:right"><b>${'{:,.2f}'.format(final2)}</b></td>
  </tr>
%endif
</table>


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
  <% 
     final1 = final2 = t_ini_2 = t_au_2 = t_red_2 =  0 
     %>
  %for line in o.line_ids2:
  <%
     final = line.budget_id.planned_amount + line.monto
     final2 += final
     t_ini_2 += line.budget_id.planned_amount
     if line.traspaso:
         t_au_2 += line.monto
     else:
         t_red_2 += line.monto
     %>
     <tr style="page-break-inside:avoid">
       <td width="15%" style="font-size:8px;text-align:center">${line.budget_id.code}</td>
       <td width="31%" style="font-size:8px;text-align:left">${line.budget_id.name}</td>
       <td width="9%" style="font-size:8px;text-align:right">${'{:,.2f}'.format(line.budget_id.planned_amount)}</td>
       %if line.traspaso:
       <td width="9%" style="font-size:8px;text-align:right">${'{:,.2f}'.format(line.monto)}</td>
       %endif
       <td width="9%" style="font-size:8px;text-align:right">${0}</td>
       <td width="9%" style="font-size:8px;text-align:right">${0}</td>
       %if not line.traspaso:
       <td width="9%" style="font-size:8px;text-align:right">${'{:,.2f}'.format(line.monto)}</td>
       %endif
       <td width="9%" style="font-size:8px;text-align:right">${0}</td>
       <td width="9%" style="font-size:8px;text-align:right">${'{:,.2f}'.format(final)}</td>
     </tr>
     %endfor
     <tr style="page-break-inside:avoid">
       <td width="15%" style="font-size:8px;text-align:center"><b>TOTALES</b></td>
       <td width="31%" style="font-size:8px;text-align:left"></td>
       <td width="9%" style="font-size:8px;text-align:right"><b>${'{:,.2f}'.format(t_ini_2)}</b></td>
       %if line.traspaso:
       <td width="9%" style="font-size:8px;text-align:right"><b>${'{:,.2f}'.format(t_au_2)}</b></td>
       %endif
       <td width="9%" style="font-size:8px;text-align:right"><b>${0}</b></td>
       <td width="9%" style="font-size:8px;text-align:right"><b>${0}</b></td>
       %if not line.traspaso:
       <td width="9%" style="font-size:8px;text-align:right"><b>${'{:,.2f}'.format(t_red_2)}</b></td>
       %endif
       <td width="9%" style="font-size:8px;text-align:right"><b>${0}</b></td>
       <td width="9%" style="font-size:8px;text-align:right"><b>${'{:,.2f}'.format(final2)}</b></td>
     </tr>
</table>
<br>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:8px">
  <tr>
    <th style="font-size:8px" width="15%"></th>
    <th style="font-size:8px" width="31%"></th>
    <th style="font-size:8px" width="9%">PRESUPUESTO INICIAL</th>
    <th style="font-size:8px" width="9%">AUMENTO</th>
    <th style="font-size:8px" width="9%">DISMINUCION</th>
    <th style="font-size:8px" width="9%">SUPLEMENTOS</th>
    <th style="font-size:8px" width="9%">REDUCCIONES</th>
    <th style="font-size:8px" width="9%">PRESUPUESTO FINAL</th>
  </tr>
  <tr>
    <th style="font-size:8px" width="15%"></th>
    <th style="font-size:8px" width="31%">TOTAL PRESUPUESTO</th>
    <th style="font-size:8px" width="9%">${'{:,.2f}'.format(o.inicial)}</th>
    <th style="font-size:8px" width="9%">${'{:,.2f}'.format(o.tr_suma)}</th>
    <th style="font-size:8px" width="9%">${'{:,.2f}'.format(o.tr_resta)}</th>
    <th style="font-size:8px" width="9%">${'{:,.2f}'.format(o.aum_suma)}</th>
    <th style="font-size:8px" width="9%">${'{:,.2f}'.format(o.dis_suma)}</th>
    <th style="font-size:8px" width="9%">${'{:,.2f}'.format(o.total_presupuesto)}</th>
  </tr>
</table>
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
