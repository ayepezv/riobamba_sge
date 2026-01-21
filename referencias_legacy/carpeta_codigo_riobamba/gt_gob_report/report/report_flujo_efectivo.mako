<!DOCTYPE HTML>
<html>
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
    <th colspan="2" style="font-size:19px" align="center">ESTADO DE FLUJO DE EFECTIVO</th>
  </tr>
</table>
<p style="font-size:15px"> Al ${ data['date_end']}</p>
<table width="100%" border="1" cellpadding="3" cellspacing="0" style="border-collapse:collapse;font-size:12px">
  <thead>   
    <tr BGCOLOR="#D8D8D8">
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
  <tr BGCOLOR="#D8D8D8">
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
    <th align="right" style="font-size:10px" WIDTH="20%">21388</th>
  </tr>
  <tr BGCOLOR="#D8D8D8">
    <th align="left" style="font-size:12px" WIDTH="40%">SUPERAVIT O DEFICIT DE CAPITAL</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['sd_capital']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['sd_capital']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>
  <tr BGCOLOR="#D8D8D8">
    <th align="left" style="font-size:12px" WIDTH="40%">SUPERAVIT O DEFICIT BRUTO</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['sd_bruto']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['sd_bruto']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>
</table>
<p style="page-break-after:always;"></p>
<table cellspacing="0" cellpadding="3" WIDTH="120%">
  <tr>
    <th colspan="4" style="font-size:19px" align="center">APLICACION DEL SUPERAVIT O FINANCIAMIENTO DEL DEFICIT</th>
  </tr>
</table>
<table width="100%" border="1" cellpadding="3" cellspacing="0" style="border-collapse:collapse;font-size:12px">
  <thead>   
    <tr BGCOLOR="#D8D8D8">
      <th align="center" style="font-size:12px" WIDTH="40%">CONCEPTOS</th>
      <th align="center" style="font-size:12px" WIDTH="20%">VIGENTE</th>
      <th align="center" style="font-size:12px" WIDTH="20%">ANTERIOR</th>
      <th align="center" style="font-size:12px" WIDTH="20%">FLUJOS DE*</th>
    </tr>
  </thead>
</table>
<table width="100%" border="1" cellpadding="3" cellspacing="0" style="border-collapse:collapse;font-size:12px">
  <tr BGCOLOR="#D8D8D8">
    <th align="left" style="font-size:12px" WIDTH="40%">FUENTES DE FINANCIAMIENTO</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['fuentes_financiamiento']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['fuentes_financiamiento']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">Creditos</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Financiamiento Público</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11336']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11336']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11336</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Cobros y Anticipos de fondos de años anteriores</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11397']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11397']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11397</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="=40%">Cobros de años anteriores</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11398']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11398']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11398</th>
  </tr>
  <tr BGCOLOR="#D8D8D8">
    <th align="left" style="font-size:12px" WIDTH="40%">USOS DE FINANCIAMIENTO</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['usos_financiamiento']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['usos_financiamiento']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">Debitos</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="=40%">Amortización de la deuda pública</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21396']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21396']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21396</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Depósitos y fondos de terceros de años anteriores</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21397']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21397']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21397</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Pagos de años anteriores</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21398']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21398']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21398</th>
  </tr>
  <tr BGCOLOR="#D8D8D8">
    <th align="left" style="font-size:12px" WIDTH="40%">SUPERAVIT O DEFICIT DE FINANCIAMIENTO</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['sd_financiamiento']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['sd_financiamiento']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">  </th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%"></th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>
  <tr BGCOLOR="#D8D8D8">
    <th align="left" style="font-size:12px" WIDTH="40%">FLUJOS NO PRESUPUESTARIOS</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['flujos_no_presupuestariosc']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['flujos_no_presupuestariosc']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">Créditos</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Títulos y valores temporales del Tesoro Nacional</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11340']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11340']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11340</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">COBROS IVA</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11381']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11381']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11381</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Anticipos de fondos de años anteriores</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11382']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11382']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11382</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Cobros años anteriores</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['11383']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['11383']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">11383</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%"></th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['flujos_no_presupuestariosd']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['flujos_no_presupuestariosd']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">Débitos</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Títulos y valores temporales del Tesoro Nacional</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21340']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21340']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21340</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Pagos IVA</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21381']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21381']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21381</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Depósitos y fondos de terceros de años anteriores</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21382']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21382']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21382</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Pagos años anteriores</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21383']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21383']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21383</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Pagos C X P Impuesto a la Renta Utilidades Ejer. Anterior</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['21395']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['21395']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">21395</th>
  </tr>
  <tr BGCOLOR="#D8D8D8">
    <th align="left" style="font-size:12px" WIDTH="40%">FLUJOS NETOS</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['flujos_netos']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['flujos_netos']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>
    <tr>
    <th align="left" style="font-size:12px" WIDTH="40%"></th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>
    <tr BGCOLOR="#D8D8D8">
    <th colspan="4" align="left" style="font-size:12px" WIDTH="40%">VARIACIONES NO PRESUPUESTARIAS</th>
   </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">De disponibilidades  (SI-SF)</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['111']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['111']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">SG111</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Anticipos de fondos  (SI-SF)</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['112']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['112']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">SG112</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Disminucion de disponibilidades  (SI-SF)</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['61991']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['61991']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">61991</th>
  </tr>
  <tr>
    <th align="left" style="font-size:12px" WIDTH="40%">Depositos y fondos de terceros  (SF-SI)</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['212']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['212']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">212</th>
  </tr>
  <tr BGCOLOR="#D8D8D8">
    <th align="left" style="font-size:12px" WIDTH="40%">VARIACIONES NETAS</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['variaciones_netas']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['variaciones_netas']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>
    <tr BGCOLOR="#D8D8D8">
    <th align="left" style="font-size:12px" WIDTH="40%">SUPERAVIT O DEFICIT BRUTO</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_act['sd_bruto2']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%">${'{:,.2f}'.format(res_ant['sd_bruto2']['balance'])}</th>
    <th align="right" style="font-size:10px" WIDTH="20%"></th>
  </tr>  
</table>
<footer>
  <table style="page-break-inside:avoid" width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
  </tr>
  <tr style="font-size:13px">
    <th width="40%">IMPRESO POR</th>
    <th width="20%"></th>
    <th width="40%">DIRECTOR FINANCIERO</th>
  </tr>  
  <tr>
  </tr>
  <tr>
  </tr>
  <tr style="height:35px">
    <th width="40%">_____________________</th>
    <th width="20%"></th>
    <th width="40%">_____________________</th>
  </tr>
  <tr style="font-size:15px">
    <th width="40%">${user.employee_id.complete_name or ''}<br/>${user.employee_id.job_id and user.employee_id.job_id.name  or ''}</th>
    <th width="20%"></th>
    <th width="40%">${user.context_department_id.manager_id.complete_name or ''}</th>
  </tr>  
</table>
</footer>
%endfor
</body>
<footer>
  <table style="page-break-inside:avoid" width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
    <th width="33%">________________________</th>
    <th width="33%">________________________</th>
    <th width="33%">________________________</th>
  </tr>
  <tr style="font-size:11px">
    <th width="33%">CONTADOR GENERAL</th>
    <th width="33%">DIRECTOR FINANCIERO</th>
    <th width="33%">${get_firmas('mx_a')}</th>
  </tr>  
  <tr style="font-size:12px">
    <th width="33%">${get_firmas('cg')}</th>
    <th width="33%">${get_firmas('df')}</th>
    <th width="33%">${get_firmas('ma')}</th>
  </tr>  
</table>
</footer>
</html>
