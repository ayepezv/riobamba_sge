<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>

</head>
<body style="overflow:visible;">
  <%
     total = total_ganado = total_decimo = total_anticipo = total_judicial = 0
     ttdic = ttene = ttfeb = ttmar = ttabr = ttmay = ttjun = ttjul = ttago = ttsep = ttoct = ttnov = ttdic = 0
     %>
  
    %for decimo in objects:
    <tr style="border: 1px solid black;"><h4 style="text-align:center;" align="center">ROL DECIMO TERCERO ${decimo.contract_type.name} DEL: ${decimo.period_start.date_start} -  ${decimo.period_end.date_stop}</h4></tr>
    <%
       total=0
       %>
    
    %for programa_id in all_programas(decimo):
    <table WIDTH="100%">
      <tr>
	<td width="100%" style="font-size:14;text-align:center;">PROGRAMA/DIRECCION ${programa_id.sequence or  ''} - ${programa_id.name or  ''}</td>	  	  
      </tr>	
    </table>   
    <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:8px">
      <thead style="display: table-header-group">
      <tr>
        <th style="font-size:10px" width="5%">Nro.</th>
        <th style="font-size:10px" width="10%">Funcionario</th>
	<th style="font-size:10px" width="5%">DIC</th>
        <th style="font-size:10px" width="5%">ENE</th>
        <th style="font-size:10px" width="5%">FEB</th>
        <th style="font-size:10px" width="5%">MAR</th>
        <th style="font-size:10px" width="5%">ABR</th>
        <th style="font-size:10px" width="5%">MAY</th>
        <th style="font-size:10px" width="5%">JUN</th>
        <th style="font-size:10px" width="5%">JUL</th>

	<th style="font-size:10px" width="5%">AGO</th>
        <th style="font-size:10px" width="5%">SEP</th>
        <th style="font-size:10px" width="5%">OCT</th>
        <th style="font-size:10px" width="5%">NOV</th>
	<th style="font-size:10px" width="5%">Total Decimo(+)</th>
	<th style="font-size:10px" width="5%">Descuento Ret. Judicial(-)</th>
        <th style="font-size:10px" width="5%">Neto a Recibir</th>
        <th style="font-size:10px" width="5%">Partida</th>
        <th style="font-size:10px" width="5%">Firma</th>
      </tr>
    </thead>
    <%
       a=0
       total_programa = total_decimo_programa = total_ganado_programa = total_anticipo_programa = total_judicial_programa = 0
       tdic = tene = tfeb = tmar = tabr = tmay = tjun = tjul = tago = tsep = toct = tnov = tdic = 0
       %>
    %for decimo_id in all_decimo(decimo,programa_id):
    <% 
       a+=1
       total_decimo += decimo_id.total_decimo
       total_programa+=decimo_id.recibir
       total_judicial_programa+=decimo_id.descuento_judicial
       total+=decimo_id.recibir
       total_judicial+=decimo_id.descuento_judicial
       total_decimo_programa += decimo_id.total_decimo
       tdic += decimo_id.dic
       tene += decimo_id.ene
       tfeb += decimo_id.feb
       tmar += decimo_id.mar
       tabr += decimo_id.abr
       tmay += decimo_id.may
       tjun += decimo_id.jun
       tjul += decimo_id.jul
       tago += decimo_id.ago
       tsep += decimo_id.sep
       toct += decimo_id.oct
       tnov += decimo_id.nov
       ttdic += decimo_id.dic
       ttene += decimo_id.ene
       ttfeb += decimo_id.feb
       ttmar += decimo_id.mar
       ttabr += decimo_id.abr
       ttmay += decimo_id.may
       ttjun += decimo_id.jun
       ttjul += decimo_id.jul
       ttago += decimo_id.ago
       ttsep += decimo_id.sep
       ttoct += decimo_id.oct
       ttnov += decimo_id.nov
       %>
    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <th style="font-size:10px" width="5%">${a}</th>
      <th style="font-size:10px;text-align:left" width="10%">${decimo_id.employee_id.complete_name}</th>
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.dic)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.ene)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.feb)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.mar)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.abr)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.may)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.jun)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.jul)}</th>   
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.ago) }</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.sep) }</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.oct)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.nov)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.total_decimo)}</th>     
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.descuento_judicial)}</th>
      <th style="font-size:10px;text-align:right" width="5%">${ '{:,.2f}'.format(decimo_id.recibir)}</th>
      <th style="font-size:10px" width="5%">${decimo_id.budget_id.code}</th>
      <th style="font-size:10px;text-align:right" width="5%"></th>
    </tr>
    %endfor
    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <th style="font-size:10px" width="5%"></th>
      <th style="font-size:10px" width="5%">TOTAL PROGRAMA</th>
            <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tdic)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tene)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tfeb)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tmar)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tabr)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tmay)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tjun)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tjul)}</th>

      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tago)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tsep)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(toct)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(tnov)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(total_decimo_programa)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(total_judicial_programa)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(total_programa)}</th>
      <th style="font-size:10px" width="5%"></th>
      <th style="font-size:10px" width="5%"></th>
    </tr>
    %endfor

%endfor

    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <th style="font-size:10px" width="5%"></th>
      <th style="font-size:10px" width="10%">TOTAL DECIMO TERCERO</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttdic)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttene)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttfeb)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttmar)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttabr)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttmay)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttjun)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttjul)}</th>

      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttago)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttsep)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttoct)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(ttnov)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(total_decimo)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(total_judicial)}</th>
      <th style="font-size:10px" width="5%">${ '{:,.2f}'.format(decimo.total)}</th>
      <th style="font-size:10px" width="5%"></th>
      <th style="font-size:10px" width="5%"></th>
    </tr>
  </table>
<table width="100%" style="page-break-inside:avoid">
  <tr style="height:25px">
    <th></th>
  </tr>
  <tr style="font-size:11px">
    <th width="33%">CREADO POR</th>
    <th width="33%">REVISADO POR</th>
    <th width="33%">AUTORIZADO</th>
  </tr>  
  <tr style="height:25px">
    <th></th>
  </tr>
  <tr style="height:25px">
    <th>______________________</th>
    <th>______________________</th>
    <th>______________________</th>
  </tr>
  <tr style="font-size:11px">
    <th width="33%">${decimo.creado_por.employee_id.complete_name}</th>
    <th width="33%">SOFIA ROSA CASTILLO HEREDIA</th>
    <th width="33%">${user.context_department_id.manager_id.complete_name}</th>
  </tr>  
</table>
<table width="100%" style="page-break-inside:avoid">
  <tr style="height:25px">
    <th></th>
    <th></th>
  </tr>
  <tr style="height:25px">
      <th>________________________</th>
      <th>________________________</th>
      <th>________________________</th>
      <th>________________________</th>
    </tr>
    <tr style="font-size:10px">
      <th width="25%">REVISADO POR</th>
      <th width="25%">CONTADOR GENERAL</th>
      <th width="25%">ESPECIALISTA DE PRESUPUESTOS</th>
      <th width="25%">DIRECTOR FINANCIERO</th>
    </tr>  
    <tr style="font-size:10px">
      <th width="25%"></th>
      <th width="25%"></th>
      <th width="25%"></th>
      <th width="25%">AUTORIZO TRANSFERENCIA</th>
    </tr>  
  </table>
</body>
</html>
