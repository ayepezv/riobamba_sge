<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">GESTION FINANCIERA : PRESUPUESTOS</td>	
    </tr>
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">RESUMEN DE GASTOS PROGRAMADOS INICIAL ${o.poa_id.name or  ''}</td>	  	  
    </tr>
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:14px" width="12%">Desde: ${o.poa_id.date_start or  ''}</td>
      <td style="font-weight: bold;font-size:14px" width="12%">Hasta: ${o.poa_id.date_end or  ''}</td>
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
        <th style="font-size:12px" width="5%">78</th>
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
        <th style="font-size:12px" width="5%">Transf. Donac. Inv.</th>
        <th style="font-size:12px" width="5%">Act. Larg. Duracion</th>
        <th style="font-size:12px" width="5%">Inv. Financieras</th>
        <th style="font-size:12px" width="5%">Amort. Deuda Pub.</th>
        <th style="font-size:12px" width="5%">Aplic. Finan</th>
        <th style="font-size:12px" width="5%"></th>
        <th style="font-size:12px" width="5%"></th>
      </tr>
    </thead>
	<%
	   a=subtot=subtot2=total=0
	   t_51 = t_53 = t_56 = t_58 = t_71 = t_73 = t_75 = t_77 = t_78 = t_84 = t_87 = t_96 = t_97 = ts = ts2 = t = 0 
	   %>
    %for programa_id in get_programa_gp(o.poa_id):
	<%
	   aux_name=get_programa_name(programa_id)
	   aux_51 = get_budget_gp(programa_id,'51','0')
	   t_51 += aux_51
	   aux_53 = get_budget_gp(programa_id,'53','0')
	   t_53 += aux_53
	   aux_56 = get_budget_gp(programa_id,'56','57')
	   t_56 += aux_56
	   aux_58 = get_budget_gp(programa_id,'58','0')
	   t_58 += aux_58
	   subtot = aux_51 + aux_53 + aux_56 + aux_58
	   ts += subtot
	   aux_71 = get_budget_gp(programa_id,'71','0')
	   t_71 += aux_71
	   aux_73 = get_budget_gp(programa_id,'73','0')
	   t_73 += aux_73
	   aux_75 = get_budget_gp(programa_id,'75','0')
	   t_75 += aux_75
	   aux_77 = get_budget_gp(programa_id,'77','0')
	   t_77 += aux_77
	   aux_78 = get_budget_gp(programa_id,'78','0')
	   t_78 += aux_78
	   aux_84 = get_budget_gp(programa_id,'84','0')
	   t_84 += aux_84
	   aux_87 = get_budget_gp(programa_id,'87','0')
	   t_87 += aux_87
	   aux_96 = get_budget_gp(programa_id,'96','0')
	   t_96 += aux_96
	   aux_97 = get_budget_gp(programa_id,'97','0')
	   t_97 += aux_97
	   subtot2 = aux_71 + aux_73 + aux_75 + aux_77 + aux_78 + aux_84 + aux_87 + aux_96 + aux_97
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
      <td width="5%" style="font-size:12px;text-align:right">${ '{:,.2f}'.format(aux_78) }</td>
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
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_78) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_84) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_87) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_96) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t_97) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(ts2) }</b></td>
      <td width="5%" style="font-size:12px;text-align:right"><b>${ '{:,.2f}'.format(t) }</b></td>
    </tr>
  </table>
  %endfor
</html>
