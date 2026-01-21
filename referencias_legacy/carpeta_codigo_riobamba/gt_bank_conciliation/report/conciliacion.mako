<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <%
     aux_acumulado = saldo_final = 0
     aux_acumulado = o.bank_resumen.final_estado_cuenta - o.bank_resumen.saldo_final_sistema
     aux_cuenta = o.bank_resumen.final_estado_cuenta - aux_acumulado
     %>
  <table WIDTH="100%">
     %if o.concilied_ok=='Libro Bancos':
     <tr>
       <td width="100%" style="font-size:14;text-align:center;">CONCILIACION BANCARIA : LIBRO BANCOS</td>	  	  
     </tr>	
     %else:
     <tr>
       <td width="100%" style="font-size:14;text-align:center;">CONCILIACION BANCARIA : ${o.concilied_ok}</td>	  	  
     </tr>
     %endif
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">DESDE: ${o.date_start or ''}</td>	  	  
    </tr>	
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">HASTA:${o.date_end or ''}</td>	  	  
    </tr>	
  </table>
  %for line_acc in o.line_ids:
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
    <tr>
      <td style="font-weight: bold;font-size:11px" width="8%">CUENTA:</td>
      <td style="font-weight: bold;font-size:11px" width="12%"></td>
      <td style="font-size:11px" width="46%">${line_acc.account_id.code or ''} - ${line_acc.account_id.name or ''}</td>
    </tr> 
    <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
      <tr>
        <th style="font-size:11px" width="8%">FECHA</th>
        <th style="font-size:11px" width="5%">COMP.</th>
        <th style="font-size:11px" width="20%">REFERENCIA</th>
        <th style="font-size:11px" width="20%">DOCUMENTO</th>
        <th style="font-size:11px" width="21%">EMPRESA/BENEFICIARIO</th>
        <th style="font-size:11px" width="5%">CONCILIADO</th>
        <th style="font-size:11px" width="7%">INGRESOS</th>
        <th style="font-size:11px" width="7%">EGRESOS</th>
        <th style="font-size:11px" width="7%">SALDO</th>
      </tr>
    </thead>
    <%
       a=aux_todo=resta=debit_all=credit_all=aux_cuenta=0
       %>
    %if o.concilied_ok!='No Conciliado':
    <tr style="page-break-inside:avoid">
      <td width="8%" style="font-size:11px;text-align:left">${}</td>
      <td width="5%" style="font-size:11px;text-align:left">${}</td>
      <td width="20%" style="font-size:11px;text-align:left">${}</td>
      <td width="20%" style="font-size:11px;text-align:left"><b>"SALDO ANTERIOR"</b></td>
      <td width="21%" style="font-size:11px;text-align:left">${}</td>
      <td width="5%" style="font-size:11px;text-align:left">${}</td>
      <td width="7%" style="font-size:11px;text-align:right">${}</td>
      <td width="7%" style="font-size:11px;text-align:right">${}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line_acc.saldo_anterior}</td>
    </tr>
    %endif
    %if o.concilied_ok in ('Conciliado','No Conciliado'):
    <%
       aux_acumulado=0
       %>
    %endif
    %for line in line_acc.line_line_ids:
    %if o.concilied_ok in ('Conciliado','No Conciliado'):
    <%
       aux_acumulado+=(line.debit+line.credit)#abs(line_acc.saldo_final)
       %>
    %endif
    <%
       a+=1
       aux_todo += (line.debit+line.credit)
       debit_all += line.debit
       credit_all += line.credit
       %>
    <tr style="border: 1px solid black;page-break-inside:avoid">
      <td width="8%" style="font-size:11px;text-align:left">${line.date}</td>
      <td width="5%" style="font-size:11px;text-align:left">${line.doc}</td>
      <td width="20%" style="font-size:11px;text-align:left">${line.name}</td>
      <td width="20%" style="font-size:11px;text-align:left">${line.documento}</td>
      <td width="21%" style="font-size:11px;text-align:left">${line.partner_id.ced_ruc} - ${line.partner_id.name}</td>
      <td width="5%" style="font-size:11px;text-align:right">
	%if line.conciliado:
	SI
	%else:
	NO
	%endif
      </td>
      <td width="7%" style="font-size:11px;text-align:right">${line.debit}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line.credit}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line.saldo}</td>
    </tr>
    %endfor
    %if o.concilied_ok!='No Conciliado':
    <tr style="page-break-inside:avoid">
      <td width="8%" style="font-size:11px;text-align:left"></td>
      <td width="5%" style="font-size:11px;text-align:left"></td>
      <td width="20%" style="font-size:11px;text-align:left"></td>
      <td width="20%" style="font-size:11px;text-align:left"></td>
      <td width="21%" style="font-size:11px;text-align:left"><b>SON ${a} Comprobantes TOTAL:</b></td>
      <td width="5%" style="font-size:11px;text-align:left"></td>
      <td width="7%" style="font-size:11px;text-align:left">${line_acc.debe}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line_acc.haber}</td>
      <td width="7%" style="font-size:11px;text-align:right"><b>${line_acc.saldo_final}</b></td>
    </tr>
    %endif      
  </table>
  <!--table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
    %if o.concilied_ok=='No Conciliado':
    <tr style="page-break-inside:avoid">
      <td width="79%" style="font-size:11px;text-align:left"></td>
      <td width="7%" style="font-size:11px;text-align:left"></td>
      <td width="7%" style="font-size:11px;text-align:right">SALDO FINAL ACUMULADO</td>
      <td width="7%" style="font-size:11px;text-align:right"><b>${aux_acumulado}</b></td>
    </tr>
    %endif
  </table-->
    %endfor
  %if o.concilied_ok=='No Conciliado':
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:right"><b>Acumulado</b></td>
      <td width="50%" style="font-size:11px;text-align:left"><b>${aux_acumulado}</b></td>
    </tr>
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:center"><b>Saldo Segun Libro Bancos = ${o.bank_resumen.saldo_final_sistema}</b></td>
      <td width="50%" style="font-size:11px;text-align:center"><b>Saldo segun estado de cuenta = ${o.bank_resumen.final_estado_cuenta}</b></td>
    </tr>
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
    <tr style="page-break-inside:avoid">
      <td width="25%" style="font-size:11px;text-align:right"><b></b></td>
      <td width="25%" style="font-size:11px;text-align:right"><b></b></td>
      <td width="25%" style="font-size:11px;text-align:right"><b>Saldo Libro Bancos</b></td>
      <td width="25%" style="font-size:11px;text-align:right"><b>Estado Cuenta Menos Acumulado</b></td>
    </tr>
    <tr style="page-break-inside:avoid">
      <td width="25%" style="font-size:11px;text-align:right"><b></b></td>
      <td width="25%" style="font-size:11px;text-align:right"><b></b></td>
      <td width="25%" style="font-size:11px;text-align:right"><b>${o.bank_resumen.saldo_final_sistema}</b></td>
      <%
	 resta = o.bank_resumen.final_estado_cuenta - aux_todo
	 aux_cuenta = o.bank_resumen.final_estado_cuenta - aux_acumulado
	 saldo_final = aux_cuenta - o.bank_resumen.saldo_final_sistema
	 %>
      <td width="25%" style="font-size:11px;text-align:right"><b>${aux_cuenta}</b></td>
    </tr>
  </table>
  %endif
  %if o.concilied_ok=='No Conciliado':
  %if abs(saldo_final)<0.001: #aux_cuenta
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:right"><b>ESTADO</b></td>
      <td width="50%" style="font-size:11px;text-align:left"><b>CORRECTO</b></td>
      <td width="50%" style="font-size:11px;text-align:right"><b>SALDO</b></td>
      <td width="50%" style="font-size:11px;text-align:left"><b>${'{:,.2f}'.format(0)}</b></td>
    </tr>
  </table>
  %else:
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:11px">
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:11px;text-align:right"><b>ESTADO</b></td>
      <td width="50%" style="font-size:11px;text-align:left"><b>INCORRECTO</b></td>
      <td width="50%" style="font-size:11px;text-align:right"><b>SALDO</b></td>
      <td width="50%" style="font-size:11px;text-align:left"><b>${'{:,.2f}'.format(saldo_final)}</b></td>
    </tr>
  </table>
  %endif
  %endif
  %endfor
  <footer>
    <table style="page-break-inside:avoid" width="100%">
      <br>
      <tr style="font-size:13px">
	<th width="33%">RESPONSABLE</th>
      </tr>  
      <tr>
      </tr>
      <tr>
      </tr>
      <tr style="height:35px">
	<th width="33%">________________________</th>
      </tr>
      <tr style="font-size:15px">
	<th width="33%">Martinez Conde Carolina Pamela</th>
      </tr>  
    </table>
  </footer>
</html>
