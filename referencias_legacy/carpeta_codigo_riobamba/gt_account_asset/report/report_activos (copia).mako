<html>
<head WIDTH="200%">
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
<body WIDTH="100%">
  <H1><left>DIRECCION: DIRECCION FINANCIERA</center></H1>
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
<table WIDTH="100%" BGCOLOR="#D8D8D8" rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px">
<tr>
      <td WIDTH="15%" style="text-align:left;font-size:26px"> C&oacute;digo</td>	
      <td WIDTH="35%" style="text-align:left;font-size:26px"> Descripci&oacute;n</td>	
      <td WIDTH="8%" style="text-align:center;font-size:26px">Marca</td>
      <td WIDTH="8%" style="text-align:center;font-size:26px">Modelo</td>
      <td WIDTH="8%" style="text-align:center;font-size:26px">Color</td>
      <td WIDTH="8%" style="text-align:center;font-size:26px"> Transacci&oacute;n</td>
      <td WIDTH="8%" style="text-align:center;font-size:26px"> Fecha Compra</td>
      <td WIDTH="8%" style="text-align:center;font-size:26px"> Estado</td>
      <td WIDTH="8%" style="text-align:center;font-size:26px"> Costo hist&oacute;rico</td>
      <td WIDTH="8%" style="text-align:center;font-size:26px"> Depreciacion</td>
      <td WIDTH="8%" style="text-align:center;font-size:26px"> Valor actual</td>			
    <tr/>
</table>
  %for inv in objects :
  <%
     custodio = inv.employee_id.complete_name
     purchase_value_total += inv.purchase_value
     salvage_value_total += inv.depreciacion
     residual_value_total += inv.valor_actual
     %>
  <table WIDTH="100%" rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px">
    
    <tr>
      <td WIDTH="15%" style="text-align:left;font-size:20px">${inv.code or ''|entity}</td>
      <td WIDTH="35%" style="text-align:left;font-size:20px">${inv.name or ''|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${inv.marca or ''|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${inv.modelo or ''|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${inv.color or ''|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${inv.transaction_id.name or ''|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${inv.purchase_date or ''|entity}</td>
      <td width="8%" style="text-align:center;font-size:20px">${(inv.state == 'draft') and 'Borrador' or (inv.state == 'open') and 'Operativo' or (inv.state == 'review') and 'En revision' or (inv.state == 'no_depreciate') and 'Operativo' or 'Dado de baja'|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${inv.purchase_value or '0.00'|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${inv.depreciacion or '0.00'|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${inv.valor_actual or '0.00'|entity}</td>
      
    </tr>
  </table>
  %endfor
  <table WIDTH="100%" rules="none">
    <tr>
      <td WIDTH="15%" style="text-align:center;font-size:20px">${''}</td>
      <td WIDTH="35%" style="text-align:center;font-size:20px">${''}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${''}</td>
      <td width="8%" style="text-align:center;font-size:20px">${''}</td>
      <td width="8%" style="text-align:center;font-size:20px">${''}</td>
      <td width="8%" style="text-align:center;font-size:20px">${''}</td>
      <td width="8%" style="text-align:center;font-size:20px">${''}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${'Subtotal USD'}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${purchase_value_total or '0.00'|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${salvage_value_total or '0.00'|entity}</td>
      <td WIDTH="8%" style="text-align:center;font-size:20px">${residual_value_total or '0.00'|entity}</td>
      
    </tr>
  </table>
  <table width="100%">
    <tr style="height:35px">
    </tr>
    <tr style="height:35px">
    </tr>
    <tr style="font-size:22px">
      <th width="33%">Creado por</th>
      <th width="33%">Jefe Inventario</th>
      <th width="33%">Custodio</th>
    </tr>  
    <tr style="height:35px">
    </tr>
    <tr style="height:35px">
      <th>__________________</th>
      <th>__________________</th>
      <th>__________________</th>
    </tr>
    <tr style="font-size:22px">
      <th width="33%">${user.employee_id.complete_name or ''}</th>
      <th width="33%">${user.context_department_id.manager_id.complete_name or ''}</th>
      <th width="33%">${custodio or ''}</th>
    </tr>  
  </table>
</body>
</html>
