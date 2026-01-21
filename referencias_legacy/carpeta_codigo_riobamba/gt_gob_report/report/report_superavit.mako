<!DOCTYPE HTML>
<html> <!--ESTA COPIADA LA PLANTILLA DEL FLUJO DE EFECTIVO -->
  <head>
    <style type="text/css">
      .line {
      border-bottom:1pt solid black;
      }
      .title {
      font-size: 9px;
      }
      .lines {
      font-size: 10px;
      }
    </style>  
  </head>
<body>
  %for o in objects:
  <% vars = _vars(o)  %>
  <%res=lineas(o)%>
  <%res_act=res['act']%>
  <%res_ant=res['ant']%>
<table cellspacing="0" cellpadding="3" WIDTH="120%">
  <tr>
    <th colspan="2" style="font-size:19px" align="center">${ user.company_id.name }</th>
  </tr>
  <tr>
    <th colspan="2" style="font-size:19px" align="center">SUPERAVIT</th>
  </tr>
</table>
<p style="font-size:15px"> Al ${ data['date_end']}</p>
<table width="100%" border="1" cellpadding="3" cellspacing="0" style="border-collapse:collapse;font-size:12px">
  <thead>   
    <tr>
      <th align="center" style="font-size:12px" WIDTH="40%">DENOMINACION</th>
      <th align="center" style="font-size:12px" WIDTH="20%">VIGENTE</th>
      <th align="center" style="font-size:12px" WIDTH="20%">ANTERIOR</th>
      <th align="center" style="font-size:12px" WIDTH="20%">FLUJOS DE*</th>
    </tr>
  </thead>
</table>
<table width="100%" border="1" cellpadding="3" cellspacing="0" style="border-collapse:collapse;font-size:12px">
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">FUENTES CORRIENTES</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['fuentes_corrientes']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['fuentes_corrientes']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">Creditos</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Impuestos</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11311']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11311']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11311</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Tasas y Contribuciones</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11313']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11313']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11313</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="=40%">Ventas de bienes y servicios</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11314']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11314']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11314</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Rentas de inversiones y multas</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11317']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11317']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11317</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="=40%">Transferencias y donaciones corrientes</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11318']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11318']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11318</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Otros Ingresos</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11319']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11319']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11319</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">USOS CORRIENTES</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['usos_corrientes']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['usos_corrientes']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">Debitos</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Gastos en personal</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21351']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21351']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21351</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Bienes y servicios de consumo</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21353']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21353']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21353</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Aporte fiscal corriente</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21355']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21355']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21355</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Gastos financieros</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21356']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21356']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21356</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Otros gastos corrientes</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21357']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21357']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21357</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Trasnsferencias y donaciones corrientes</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21358']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21358']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21358</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">SUPERAVIT O DEFICIT CORRIENTE</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['sd_corriente']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['sd_corriente']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">FUENTES DE CAPITAL</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['fuentes_capital']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['fuentes_capital']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">Creditos</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Venta de activos de larga duracion</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11324']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11324']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11324</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Trasnferencias y donaciones de capital</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11328']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11328']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11328</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">USOS DE PRODUCCION, INVERSION Y CAPITAL</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['usos_produccion']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['usos_produccion']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">Debitos</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Gastos en personal para produccion</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21361']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21361']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21361</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Bienes y servicios para produccion</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21363']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21363']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21363</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Otros gastos de produccion</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21367']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21367']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21367</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Gastos en personal para inversion</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21371']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21371']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21371</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Bienes y servicios para inversion</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21373']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21373']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21373</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Obras Publicas</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21375']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21375']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21375</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Otros gastos de inversion</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21377']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21377']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21377</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Trasnferencias y donaciones para inversion</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21378']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21378']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21378</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Activos de larga duracion</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21384']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21384']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21384</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Aporte fiscal de capital</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21385']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21385']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21385</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Inversiones financieras</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21387']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21387']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21387</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">(-) Recuperacion de inversiones</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11327']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11327']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11327</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Trasnferencias y donaciones de capital</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21388']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21388']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11327</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">SUPERAVIT O DEFICIT DE CAPITAL</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['sd_capital']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['sd_capital']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">SUPERAVIT O DEFICIT BRUTO</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['sd_bruto']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['sd_bruto']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>
</table>
%endfor
</body>
</html>
