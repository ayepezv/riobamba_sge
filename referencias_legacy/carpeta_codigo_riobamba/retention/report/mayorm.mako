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
	  <td width="100%" style="font-size:14;text-align:center;">MAYOR DE CUENTA</td>	  	  
	</tr>	
	<tr>
	  <td width="100%" style="font-size:14;text-align:center;">DESDE: ${o.date_start or ''}</td>	  	  
	</tr>	
	<tr>
	  <td width="100%" style="font-size:14;text-align:center;">HASTA:${o.date_end or ''}</td>	  	  
	</tr>	
  </table>
  <%
     total_saldo = total_debitos = total_creditos = 0
     %>
  %for line_acc in o.line_ids:
  <% 
     total_debitos += line_acc.debe
     total_creditos += line_acc.haber
     %>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:7px">
    <tr>
      <td style="font-weight: bold;font-size:8px" width="8%">CUENTA:</td>
      <td style="font-weight: bold;font-size:8px" width="12%"></td>
      <td style="font-size:8px" width="46%">${line_acc.account_id.code or ''} - ${line_acc.account_id.name or ''}</td>
    </tr> 
    <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
      <tr>
        <th style="font-size:8px" width="8%">FECHA</th>
        <th style="font-size:8px" width="12%">COMP.</th>
        <th style="font-size:8px" width="46%">REFERENCIA</th>
        <th style="font-size:8px" width="16%">CUENTA</th>
        <th style="font-size:8px" width="7%">DEBE</th>
        <th style="font-size:8px" width="7%">HABER</th>
        <th style="font-size:8px" width="7%">SALDO</th>
      </tr>
    </thead>
	<%
	   a=0
	   %>
    <tr style="page-break-inside:avoid">
      <td width="8%" style="font-size:9px;text-align:left">${}</td>
      <td width="12%" style="font-size:9px;text-align:left">${}</td>
      <td width="46%" style="font-size:9px;text-align:left">"SALDO ANTERIOR"</td>
      <td width="16%" style="font-size:9px;text-align:left">${}</td>
      <td width="7%" style="font-size:9px;text-align:right">${}</td>
      <td width="7%" style="font-size:9px;text-align:right">${}</td>
      <td width="7%" style="font-size:9px;text-align:right">${line_acc.saldo_anterior}</td>
    </tr>
    %if (line_acc.inicial_debe>0 or line_acc.inicial_haber>0):
    <tr style="page-break-inside:avoid">
      <td width="8%" style="font-size:9px;text-align:left">${}</td>
      <td width="12%" style="font-size:9px;text-align:left">${}</td>
      <td width="46%" style="font-size:9px;text-align:left">${}</td>
      <td width="16%" style="font-size:9px;text-align:left">ASIENTO APERTURA</td>
      <td width="7%" style="font-size:9px;text-align:right">${line_acc.inicial_debe}</td>
      <td width="7%" style="font-size:9px;text-align:right">${line_acc.inicial_haber}</td>
      <td width="7%" style="font-size:9px;text-align:right">${}</td>
    </tr>
    %endif
    %for line in line_acc.line_line_ids:
	<%
	   a+=1
	   %>
    <tr style="border: 1px solid black;page-break-inside:avoid">
      <td width="8%" style="font-size:9px;text-align:left">${line.date}</td>
      <td width="12%" style="font-size:9px;text-align:left">${line.doc}</td>
      <td width="46%" style="font-size:9px;text-align:left">${line.name}</td>
      <td width="16%" style="font-size:9px;text-align:left">${line.account_id.code} - ${line.account_id.name}</td>
      <td width="7%" style="font-size:9px;text-align:right">${line.debit}</td>
      <td width="7%" style="font-size:9px;text-align:right">${line.credit}</td>
      <td width="7%" style="font-size:9px;text-align:right">${line.saldo}</td>
    </tr>
    %endfor      
  </table>
  <% 
     total_saldo = abs(line_acc.t_i-line_acc.t_g)
     %>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:8px">
    <tr style="page-break-inside:avoid">
      <td width="79%" style="font-size:9px;text-align:left">SON ${a} COMPROBANTES SUMAN TOTAL: </td>
      <td width="7%" style="font-size:9px;text-align:left">${line_acc.t_i}</td>
      <td width="7%" style="font-size:9px;text-align:right">${line_acc.t_g}</td>
      <td width="7%" style="font-size:9px;text-align:right"><b>${total_saldo}</b></td>
    </tr>
  </table>
  
    %endfor
  %endfor
</html>
