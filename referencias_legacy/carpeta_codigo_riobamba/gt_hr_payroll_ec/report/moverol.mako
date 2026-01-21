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
      <td width="100%" style="font-size:14;text-align:center;">PREASIENTO DE ROL: ${o.name} </td>	  	  
    </tr>	
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
      <tr>
        <th style="font-size:11px" width="55%">CUENTA</th>
        <th style="font-size:11px" width="10%">DEBE</th>
        <th style="font-size:11px" width="10%">HABER</th>
        <th style="font-size:11px" width="25%">PARTIDA</th>
      </tr>
    </thead>
	<%
	   debit = credit = 0
	   %>
    %for line in o.move_id.line_id:
	<%
	   debit+=line.debit
	   credit+=line.credit
	   %>
    <tr>
      <td width="55%" style="font-size:11px;text-align:left">${line.account_id.code} - ${line.account_id.name}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.debit or '0.00'}</td>
      <td width="10%" style="font-size:11px;text-align:right">${line.credit or '0.00'}</td>
      <td width="25%" style="font-size:11px;text-align:center">${line.budget_id.name or ''}</td>
    </tr>
    %endfor   
      <tr>
      <td width="55%" style="font-size:11px;text-align:left"><b>TOTAL</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${debit}</b></td>
      <td width="10%" style="font-size:11px;text-align:right"><b>${credit}</b></td>
      <td width="25%" style="font-size:11px;text-align:center">${}</td>
    </tr>
  </table>
  %endfor
</html>
