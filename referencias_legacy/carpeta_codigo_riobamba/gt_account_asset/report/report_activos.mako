<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  <H4><left>DIRECCION: DIRECCION ADMINISTRATIVA</center></H4>
<H4><left>REPORTE INVENTARIO DE  
%if objects[0].type=='Larga Duracion':
ACTIVOS FIJOS
%else:
BIENES SUJETOS A CONTROL
%endif
</center></H4>
  <%
     purchase_value_total = salvage_value_total = residual_value_total = 0
     %> 

<table WIDTH="100%"  rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
    <td WIDTH="13%" style="text-align:left;font-size:12px"> C&oacute;digo</td>	
    <td WIDTH="30%" style="text-align:left;font-size:12px"> Descripci&oacute;n</td>
    <td WIDTH="13%" style="text-align:center;font-size:12px">Categoria</td>
    <td WIDTH="10%" style="text-align:center;font-size:12px">Custodio</td>
    <td WIDTH="8%" style="text-align:center;font-size:12px">Marca</td>
    <td WIDTH="8%" style="text-align:center;font-size:12px">Modelo</td>
    <td WIDTH="8%" style="text-align:center;font-size:12px">Color</td>
    <td WIDTH="8%" style="text-align:center;font-size:12px"> Fecha Compra</td>
    <td WIDTH="8%" style="text-align:center;font-size:12px"> Fecha Entrega</td>
    <td WIDTH="8%" style="text-align:center;font-size:12px"> Proveedor</td>
    <td WIDTH="8%" style="text-align:center;font-size:12px"> Estado</td>
    <td WIDTH="8%" style="text-align:center;font-size:12px"> Costo hist&oacute;rico</td>
    <td WIDTH="7%" style="text-align:center;font-size:12px"> Dep.</td>
    <td WIDTH="7%" style="text-align:center;font-size:12px"> Val. actual</td>			
  <thead/>

%for inv in objects :
<%
   custodio = inv.employee_id.complete_name
   purchase_value_total += inv.purchase_value
   salvage_value_total += inv.depreciacion
   residual_value_total += inv.valor_actual
   %>
<tr style="border: 1px solid black;page-break-inside:avoid" >
  <td WIDTH="13%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">${inv.code or ''|entity}</td>
  <td WIDTH="30%" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">${inv.name or ''|entity} - ${inv.serial_number or ''|entity}</td>
  <td WIDTH="13%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.category_id.name or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.employee_id.complete_name or ''|entity}</td>
  <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.marca or ''|entity}</td>
  <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.modelo or ''|entity}</td>
  <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.color or ''|entity}</td>
  <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.purchase_date or ''|entity}</td>
  <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.date_entrega or ''|entity}</td>
  <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.partner_id.name or ''|entity}</td>
  <td width="8%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${(inv.state == 'draft') and 'Borrador' or (inv.state == 'open') and 'Operativo' or (inv.state == 'review') and 'En revision' or (inv.state == 'no_depreciate') and 'Operativo' or 'Dado de baja'|entity}</td>
  <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.purchase_value or '0.00'|entity}</td>
  <td WIDTH="7%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.depreciacion or '0.00'|entity}</td>
  <td WIDTH="7%" style="border: 1px solid black;text-align:center;font-size:12px;page-break-inside:avoid">${inv.valor_actual or '0.00'|entity}</td>
</tr>
%endfor
  <tr style="page-break-inside:avoid">
      <td WIDTH="23%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="23%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="23%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="7%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="7%" style="text-align:center;font-size:12px"><b>${''}</b></td>
  </tr>
  <tr style="page-break-inside:avoid">
      <td WIDTH="23%" style="text-align:center;font-size:12px">${user.employee_id.complete_name or ''}</td>
      <td WIDTH="23%" style="text-align:center;font-size:12px">${user.context_department_id.coordinador_id.complete_name or ''}</td>
      <td WIDTH="23%" style="text-align:center;font-size:12px">${custodio or ''}</td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="7%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="7%" style="text-align:center;font-size:12px"><b>${''}</b></td>
  </tr>
    <tr style="page-break-inside:avoid">
      <td WIDTH="23%" style="text-align:center;font-size:12px">Elaborado por</td>
      <td WIDTH="23%" style="text-align:center;font-size:12px">Responsable</td>
      <td WIDTH="23%" style="text-align:center;font-size:12px">Custodio</td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="7%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="7%" style="text-align:center;font-size:12px"><b>${''}</b></td>

  </tr>
    <tr style="border: 1px solid black;page-break-inside:avoid">
      <td WIDTH="23%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="23%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="23%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${''}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${'SUBTOTAL USD'}</b></td>
      <td WIDTH="8%" style="text-align:center;font-size:12px"><b>${purchase_value_total or '0.00'|entity}</b></td>
      <td WIDTH="7%" style="text-align:center;font-size:12px"><b>${salvage_value_total or '0.00'|entity}</b></td>
      <td WIDTH="7%" style="text-align:center;font-size:12px"><b>${residual_value_total or '0.00'|entity}</b></td>
  </tr>
</table>
<table style="page-break-inside:avoid" width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
  </tr>
  <tr style="font-size:12px">
    <th width="100%">Creado por</th>
  </tr>  
  <tr style="height:35px">
  </tr>
  <tr style="height:12px">
    <th>__________________</th>
  </tr>
  <tr style="font-size:12px">
    <th width="100%">${user.employee_id.complete_name or ''}</th>
  </tr>  
</table>
</body>
</html>
