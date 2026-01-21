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
    %for obj in objects :
    <%vars = _vars(obj)%>
    <%res = lineas(obj)%>
    <H2><center>DATOS DE BALANCE</center></H2>
    <table WIDTH="100%"  rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px">
      <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="center"><b>CODIGO</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>NOMBRE</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>FLUJO DEBE</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>FLUJO HABER</b></td>
      </thead>
      %for balance_line in res['lineas_balance']:
      <tr style="page-break-inside:avoid">
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="left">${balance_line.code}</td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">${balance_line.desc}</td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right">${balance_line.debe_flujo}</td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right">${balance_line.haber_flujo}</td>
      </tr>
      %endfor
    </table>
    <br/>
    <H2><center>DATOS DE CEDULA</center></H2>
    <table WIDTH="100%"  rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px">
      <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="center"><b>CODIGO</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>NOMBRE</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>DEVENGADO</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>PAGADO/RECAUDADO</b></td>
      </thead>
      %for cedula_line in res['lineas_cedula']:
      <tr style="page-break-inside:avoid">
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="left">${cedula_line.code}</td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">${cedula_line.desc}</td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right">${cedula_line.devengado_amount}</td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right">${cedula_line.paid_amount}</td>
      </tr>
      %endfor
    </table>
    
    <H2><center>DETALLE DE ASIENTOS</center></H2>
    %for move in res['moves']:
    <p>${move.name} - ${move.date}</p>
    <table WIDTH="100%"  rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px">
      <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="center"><b>CODIGO</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="center"><b>NOMBRE</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="center"><b>PARTIDA</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>DEBE</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>HABER</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>DEVENGADO</b></td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center"><b>PAGADO/RECAUDADO</b></td>
      </thead>
      %for moveline in move.line_id:
      %if (moveline.account_id.id in vars['account_ids_with_child']):
      <tr style="page-break-inside:avoid">
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="left">${moveline.account_id.code}</td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="left">${moveline.account_id.name}</td>
	%if (moveline.budget_id):
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="left">${moveline.budget_id.code}</td>

	%else:
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="left"></td>
	%endif
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">${moveline.debit}</td>
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right">${moveline.credit}</td>
	%if (moveline.budget_accrued):
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right">Devengado</td>
	%else:
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right"></td>
	%endif
	%if (moveline.budget_paid):
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right">Pagado/Recaudado</td>
	%else:
	<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right"></td>
	%endif
      </tr>
      %endif
      %endfor
    </table>
    %endfor
    %endfor
  </body>
  
</html>
