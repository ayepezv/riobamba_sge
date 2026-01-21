<html>
<head WIDTH="200%">
  <style type="text/css">
        ${css}
    </style>
    <!--style type="text/css">
        ${css}    ${css}
    td {
    padding:2px 4px 2px 4px;
    font-size:10px;
    }
    table th {
	padding:2px 4px 2px 4px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
    font-size:10px;
    }
    .project {
	padding:3px 12px 9px 12px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ababab), to(#ababab));
	background: -moz-linear-gradient(top,  #ededed,  #ababab);
    font-size:12px;
    }
    table_basic {
    width: 100%;
    }
    table_title {
	border-top:1px solid #ffffff;
    }
    hr {
    border: 0;
    border-bottom: 1px solid #FFFFFF;
    border-top: 1px solid #AAAAAA;
    clear: both;
    height: 0;
    margin: 12px 0 18px;
    }
    </style-->
</head>
<body>
  <H1><left>DIRECCION: DIRECCION ADMINISTRATIVA</center></H1>
<H1><left>REPORTE INVENTARIO DE ACTIVOS</center></H1>
<!--table WIDTH="200%" >
    <tr>
      <td WIDTH="20%" style="text-align:left;font-size:18px"></td>	
      <td WIDTH="40%" style="text-align:left;font-size:18px"></td>					
      <td WIDTH="10%" style="text-align:center;font-size:18px"></td>
      <td WIDTH="8%" style="text-align:center;font-size:18px"></td>
      <td WIDTH="8%" style="text-align:center;font-size:18px"></td>
      <td WIDTH="8%" style="text-align:center;font-size:18px"></td>
      <td WIDTH="8%" style="text-align:center;font-size:18px"></td>
      <td WIDTH="8%" style="text-align:center;font-size:18px"></td>			
    <tr/>
</table-->
<%
   purchase_value_total = salvage_value_total = residual_value_total = 0
   %> 
<table WIDTH="100%"  border="1" cellpadding="2" style="border-collapse:collapse;font-size:12px">
  <thead style="display: table-header-group">
    <tr>
      <td WIDTH="13%" style="text-align:left;font-size:14px"> C&oacute;digo</td>	
      <td WIDTH="30%" style="text-align:left;font-size:14px"> Descripci&oacute;n</td>	
      <td WIDTH="10%" style="text-align:center;font-size:14px">Custodio</td>
      <td WIDTH="8%" style="text-align:center;font-size:14px">Marca</td>
      <td WIDTH="8%" style="text-align:center;font-size:14px">Modelo</td>
      <td WIDTH="8%" style="text-align:center;font-size:14px">Color</td>
      <td WIDTH="8%" style="text-align:center;font-size:14px"> Transacci&oacute;n</td>
      <td WIDTH="8%" style="text-align:center;font-size:14px"> Fecha Compra</td>
      <td WIDTH="8%" style="text-align:center;font-size:14px"> Estado</td>
      <td WIDTH="8%" style="text-align:center;font-size:14px"> Costo hist&oacute;rico</td>
      <td WIDTH="8%" style="text-align:center;font-size:14px"> Depreciacion</td>
      <td WIDTH="8%" style="text-align:center;font-size:14px"> Valor actual</td>			
    <tr/>
  </thead>
  %for inv in objects :
  <%
     custodio = inv.employee_id.complete_name
     purchase_value_total += inv.purchase_value
     salvage_value_total += inv.depreciacion
     residual_value_total += inv.valor_actual
     %>
  <tr style="border: 1px solid black;page-break-inside:avoid">
    <td WIDTH="13%" style="border: 1px solid black;text-align:left;font-size:12px">${inv.code or ''|entity}</td>
    <td WIDTH="30%" style="border: 1px solid black;text-align:left;font-size:12px">${inv.name or ''|entity}</td>
    <td WIDTH="10%" style="border: 1px solid black;text-align:left;font-size:12px">${inv.employee_id.complete_name or ''|entity}</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px">${inv.marca or ''|entity}</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px">${inv.modelo or ''|entity}</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px">${inv.color or ''|entity}</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px">${inv.transaction_id.name or ''|entity}</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px">${inv.purchase_date or ''|entity}</td>
    <td width="8%" style="border: 1px solid black;text-align:center;font-size:12px">${(inv.state == 'draft') and 'Borrador' or (inv.state == 'open') and 'Operativo' or (inv.state == 'review') and 'En revision' or (inv.state == 'no_depreciate') and 'Operativo' or 'Dado de baja'|entity}</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px">${inv.purchase_value or '0.00'|entity}</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px">${inv.depreciacion or '0.00'|entity}</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px">${inv.valor_actual or '0.00'|entity}</td>
  </tr>
  %if len(inv.componentes_ids) > 0:
  <tr>		
    <td style="border: 1px solid black;text-align:left;font-size:12px"><b>COMPONENTES</b></td>
  </tr>
  <tr>		
    <td WIDTH="13%"></td>
    <td WIDTH="30%" style="border: 1px solid black;text-align:left;font-size:12px" BGCOLOR="#D8D8D8">Nombre</td>
    <td WIDTH="10%" style="border: 1px solid black;text-align:left;font-size:12px" BGCOLOR="#D8D8D8">Descripci&oacute;n</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:left;font-size:12px" BGCOLOR="#D8D8D8">Marca</b></td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:left;font-size:12px" BGCOLOR="#D8D8D8">No. Serie</td>
    <td WIDTH="8%" style="border: 1px solid black;text-align:left;font-size:12px" BGCOLOR="#D8D8D8">Cantidad</td>
    <td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
  </tr>
%for componente in inv.componentes_ids:		
<tr>		
  <td style="border: 1px solid black;text-align:left;font-size:12px" WIDTH="13%" ></td>
  <td style="border: 1px solid black;text-align:left;font-size:12px" WIDTH="30%" >${componente.name or ''|entity}</td>
  <td style="border: 1px solid black;text-align:left;font-size:12px" WIDTH="10%" >${componente.value or ''|entity}</td>
  <td style="border: 1px solid black;text-align:left;font-size:12px" WIDTH="8%" >${componente.marca or ''|entity}</b></td>
<td style="border: 1px solid black;text-align:left;font-size:12px" WIDTH="8%" >${componente.serie or ''|entity}</td>
<td style="border: 1px solid black;text-align:left;font-size:12px" WIDTH="8%" >${componente.cantidad or ''|entity}</td>
<td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
    <td WIDTH="8%"></td>
</tr>
%endfor
  %endif
%endfor
<tr>
      <td WIDTH="13%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="30%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="10%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="8%" style="text-align:center;font-size:12px">${''}</td>
      <td width="8%" style="text-align:center;font-size:12px">${''}</td>
      <td width="8%" style="text-align:center;font-size:12px">${''}</td>
      <td width="8%" style="text-align:center;font-size:12px">${''}</td>
      <td width="8%" style="text-align:center;font-size:12px">${''}</td>
      <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px"><b>${'TOTAL USD'}</b></td>
      <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px"><b>${ '{:,.2f}'.format(purchase_value_total) }</b></td>
      <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px"><b>${ '{:,.2f}'.format(salvage_value_total) }</b></td>
      <td WIDTH="8%" style="border: 1px solid black;text-align:center;font-size:12px"><b>${ '{:,.2f}'.format(residual_value_total) }</b></td>
</tr>
</table>

<table width="100%">
  <tr style="font-size:12px">
    <th width="100%">Creado por</th>
  </tr>  
  <tr style="height:35px">
    <th>__________________</th>
  </tr>
  <tr style="font-size:12px">
    <th width="100%">${user.employee_id.complete_name or ''}</th>
  </tr>  
</table>
</body>
</html>
