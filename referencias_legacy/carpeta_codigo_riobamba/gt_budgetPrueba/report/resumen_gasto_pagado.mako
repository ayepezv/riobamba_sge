<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
<% 
     vars = _vars(o)
%>
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">GESTION FINANCIERA : PRESUPUESTOS</td>	
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">RESUMEN DE GASTOS PROGRAMADOS PAGADO ${o.poa_id.name or  ''}</td>	  	  
    </tr>
  </table>
<table cellspacing="0" cellpadding="1" WIDTH="100%">
  <tr>
    <td style="font-size:14px" WIDTH="15%">Fechas:</td>
    <td style="font-size:14px" align="left" WIDTH="85%">Del: ${vars['date_from']} Al: ${vars['date_to']}</td>    
  </tr>   
</table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:8px">
    <thead style="display: table-header-group">
      <tr>
        <th style="font-size:12px" width="15%"><b>Programa</b></th>
        <th style="font-size:12px" width="5%">51</th>
        <th style="font-size:12px" width="5%">53</th>
        <th style="font-size:12px" width="5%">56-57</th>
        <th style="font-size:12px" width="5%">58</th>
        <th style="font-size:12px" width="5%"><b>Subtotal</b></th>
        <th style="font-size:12px" width="5%">71</th>
        <th style="font-size:12px" width="5%">73</th>
        <th style="font-size:12px" width="5%">75</th>
        <th style="font-size:12px" width="5%">77</th>
        <th style="font-size:12px" width="5%">84</th>
        <th style="font-size:12px" width="5%">87</th>
        <th style="font-size:12px" width="5%">96</th>
        <th style="font-size:12px" width="5%">97</th>
        <th style="font-size:12px" width="5%"><b>Subtotal</b></th>
        <th style="font-size:12px" width="5%"><b>Total</b></th>
      </tr>
      <tr>
        <th style="font-size:12px" width="15%"></th>
        <th style="font-size:12px" width="5%">Personal</th>
        <th style="font-size:12px" width="5%">Bien-Ser-Consumo</th>
        <th style="font-size:12px" width="5%">Otros Gastos</th>
        <th style="font-size:12px" width="5%">Tra. Corriente</th>
        <th style="font-size:12px" width="5%"></th>
        <th style="font-size:12px" width="5%">Personal</th>
        <th style="font-size:12px" width="5%">Bien Serv. Inv.</th>
        <th style="font-size:12px" width="5%">Obra Publica</th>
        <th style="font-size:12px" width="5%">Provisiones</th>
        <th style="font-size:12px" width="5%">Act. Larg. Duracion</th>
        <th style="font-size:12px" width="5%">Inv. Financieras</th>
        <th style="font-size:12px" width="5%">Amort. Deuda Pub.</th>
        <th style="font-size:12px" width="5%">Apli. Financiamiento</th>
        <th style="font-size:12px" width="5%"></th>
        <th style="font-size:12px" width="5%"></th>
      </tr>
    </thead>
	<%
	   a=subtot=subtot2=total=0
	   t_51 = t_53 = t_56 = t_58 = t_71 = t_73 = t_75 = t_77 = t_84 = t_87 = t_96 = t_97 = ts = ts2 = t = 0 
	   %>
    %for programa_id in get_programa_gp_pagado(o.poa_id):
	<%
	   aux_name=get_programa_name_pagado(programa_id)
	   aux_51 = get_budget_gp_pagado(programa_id,'51','0')
	   t_51 += aux_51
	   aux_53 = get_budget_gp_pagado(programa_id,'53','0')
	   t_53 += aux_53
	   aux_56 = get_budget_gp_pagado(programa_id,'56','57')
	   t_56 += aux_56
	   aux_58 = get_budget_gp_pagado(programa_id,'58','0')
	   t_58 += aux_58
	   subtot = aux_51 + aux_53 + aux_56 + aux_58
	   ts += subtot
	   aux_71 = get_budget_gp_pagado(programa_id,'71','0')
	   t_71 += aux_71
	   aux_73 = get_budget_gp_pagado(programa_id,'73','0')
	   t_73 += aux_73
	   aux_75 = get_budget_gp_pagado(programa_id,'75','0')
	   t_75 += aux_75
	   aux_77 = get_budget_gp_pagado(programa_id,'77','0')
	   t_77 += aux_77
	   aux_84 = get_budget_gp_pagado(programa_id,'84','0')
	   t_84 += aux_84
	   aux_87 = get_budget_gp_pagado(programa_id,'87','0')
	   t_87 += aux_87
	   aux_96 = get_budget_gp_pagado(programa_id,'96','0')
	   t_96 += aux_96
	   aux_97 = get_budget_gp_pagado(programa_id,'97','0')
	   t_97 += aux_97
	   subtot2 = aux_71 + aux_73 + aux_75 + aux_77 + aux_84 + aux_87 + aux_96 + aux_97
	   ts2 += subtot2
	   total = subtot + subtot2
	   t += total
	   %>
    <tr style="page-break-inside:avoid">
      <td width="15%" style="font-size:10px;text-align:left"><b>${ aux_name }</b> </td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_51) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_53) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_56) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_58) }</td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(subtot) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_71) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_73) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_75) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_77) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_84) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_87) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_96) }</td>
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_97) }</td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(subtot2) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(total) }</b></td>
    </tr>
    %endfor 
    <tr style="page-break-inside:avoid">
      <td width="15%" style="font-size:12px;text-align:right"><b>TOTAL</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_51) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_53) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_56) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_58) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(ts) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_71) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_73) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_75) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_77) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_84) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_87) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_96) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_97) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(ts2) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t) }</b></td>
    </tr>
    <tr style="page-break-inside:avoid">
      <td width="15%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${}</b></td>
    </tr>
    <tr style="page-break-inside:avoid">
      <%
	 tp_51 = tp_53 = tp_56 = tp_58 = tp_71 = tp_73 = tp_75 = tp_77 = tp_84 = tp_87 = tp_96 = tp_97 = stc = sti = t = 0
	 tp_51 = get_budget_gp_pagado_field('51','0','codif_amount')
	 tp_53 = get_budget_gp_pagado_field('53','0','codif_amount')
	 tp_56 = get_budget_gp_pagado_field('56','57','codif_amount')
	 tp_58 = get_budget_gp_pagado_field('58','0','codif_amount')
	 tp_71 = get_budget_gp_pagado_field('71','0','codif_amount')
	 tp_73 = get_budget_gp_pagado_field('73','0','codif_amount')
	 tp_75 = get_budget_gp_pagado_field('75','0','codif_amount')
	 tp_77 = get_budget_gp_pagado_field('77','0','codif_amount')
	 tp_84 = get_budget_gp_pagado_field('84','0','codif_amount')
	 tp_87 = get_budget_gp_pagado_field('87','0','codif_amount')
	 tp_96 = get_budget_gp_pagado_field('96','0','codif_amount')
	 tp_97 = get_budget_gp_pagado_field('97','0','codif_amount')
	 stc = tp_51 + tp_53 + tp_56 + tp_58
	 sti = tp_71 + tp_73 + tp_75 + tp_77 + tp_84 + tp_87 + tp_96 + tp_97
	 t = stc + sti
	 %>
      <td style="font-size:12px" width="15%"><b>Presupuestado</b></td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_51)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_53)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_56)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_58)}</td>
      <th style="font-size:12px;text-align:right" width="5%"><b>${ '{:,.2f}'.format(stc)}</b></th>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_71)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_73)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_75)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_77)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_84)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_87)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_96)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tp_97)}</td>
      <th style="font-size:12px;text-align:right" width="5%"><b>${ '{:,.2f}'.format(sti)}</b></th>
      <th style="font-size:12px;text-align:right" width="5%"><b>${ '{:,.2f}'.format(t)}</b></th>
    </tr>
    <tr style="page-break-inside:avoid">
      <%
	 tpg_51 = tpg_53 = tpg_56 = tpg_58 = tpg_71 = tpg_73 = tpg_75 = tpg_77 = tpg_84 = tpg_87 = tpg_96 = tpg_97 = stcg = stig = tg = 0
	 tpg_51 = get_budget_gp_pagado_field('51','0','paid_amount')
	 tpg_53 = get_budget_gp_pagado_field('53','0','paid_amount')
	 tpg_56 = get_budget_gp_pagado_field('56','57','paid_amount')
	 tpg_58 = get_budget_gp_pagado_field('58','0','paid_amount')
	 tpg_71 = get_budget_gp_pagado_field('71','0','paid_amount')
	 tpg_73 = get_budget_gp_pagado_field('73','0','paid_amount')
	 tpg_75 = get_budget_gp_pagado_field('75','0','paid_amount')
	 tpg_77 = get_budget_gp_pagado_field('77','0','paid_amount')
	 tpg_84 = get_budget_gp_pagado_field('84','0','paid_amount')
	 tpg_87 = get_budget_gp_pagado_field('87','0','paid_amount')
	 tpg_96 = get_budget_gp_pagado_field('96','0','paid_amount')
	 tpg_97 = get_budget_gp_pagado_field('97','0','paid_amount')
	 stcg = tpg_51 + tpg_53 + tpg_56 + tpg_58
	 stig = tpg_71 + tpg_73 + tpg_75 + tpg_77 + tpg_84 + tpg_87 + tpg_96 + tpg_97
	 tg = stcg + stig
	 %>
      <th style="font-size:12px" width="15%"><b>Gastado</b></th>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_51)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_53)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_56)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_58)}</td>
      <th style="font-size:12px;text-align:right" width="5%"><b>${ '{:,.2f}'.format(stcg)}</b></th>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_71)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_73)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_75)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_77)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_84)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_87)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_96)}</td>
      <td style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tpg_97)}</td>
      <th style="font-size:12px;text-align:right" width="5%"><b>${ '{:,.2f}'.format(stig)}</b></th>
      <th style="font-size:12px;text-align:right" width="5%"><b>${ '{:,.2f}'.format(tg)}</b></th>
    </tr>
    <tr style="page-break-inside:avoid">
      <%
	 tps_51 = tps_53 = tps_56 = tps_58 = tps_71 = tps_73 = tps_75 = tps_77 = tps_84 = tps_87 = tps_96 = tps_97 = stcs = stis = ts = 0
	 tps_51 = tp_51 - tpg_51
	 tps_53 = tp_53 - tpg_53
	 tps_56 = tp_56 - tpg_56
	 tps_58 = tp_58 - tpg_58
	 tps_71 = tp_71 - tpg_71
	 tps_73 = tp_73 - tpg_73
	 tps_75 = tp_75 - tpg_75
	 tps_77 = tp_77 - tpg_77
	 tps_84 = tp_84 - tpg_84
	 tps_87 = tp_87 - tpg_87
	 tps_96 = tp_96 - tpg_96
	 tps_97 = tp_97 - tpg_97
	 stcs = tps_51 + tps_53 + tps_56 + tps_58
	 stis = tps_71 + tps_73 + tps_75 + tps_77 + tps_84 + tps_87 + tps_96 + tps_97
	 ts = stcs + stis
	 %>
      <th style="font-size:12px" width="15%"><b>Saldo</b></th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_51)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_53)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_56)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_58)}</th>
      <th style="font-size:12px;text-align:right" width="5%"><b>${ '{:,.2f}'.format(stcs)}</b></th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_71)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_73)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_75)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_77)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_84)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_87)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_96)}</th>
      <th style="font-size:12px;text-align:right" width="5%">${ '{:,.2f}'.format(tps_97)}</th>
      <th style="font-size:12px;text-align:right" width="5%"><b>${ '{:,.2f}'.format(stis)}</b></th>
      <th style="font-size:12px;text-align:right" width="5%"><b>${ '{:,.2f}'.format(ts)}</b></th>
    </tr>
  </table>
  %endfor
</html>
