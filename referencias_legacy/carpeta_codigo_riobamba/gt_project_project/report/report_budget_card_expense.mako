<!DOCTYPE HTML>
<html>
  <head>
</head>
<body>
%for o in objects:
<% 
     vars = _vars(o)
%> 
<table cellspacing="0" cellpadding="0" WIDTH="100%">
  <tr>
    <th style="font-size:16px" WIDTH="100%">CEDULA DE EGRESOS</th>
  </tr>  
</table>
<%programs=_get_programs(o)%>
<%j=0%>
<%totalp_planned_amount=totalp_reform_amount=totalp_codif_amount=totalp_commited_amount=totalp_devengado_amount=totalp_paid_amount=totalp_commited_balance=totalp_devengado_balance=0%>
%for program in programs:
%if program['id']!=False:
<%j+=1%>
<br/>
<table cellspacing="0" cellpadding="0" WIDTH="100%">
  <tr>
    <th style="font-size:16px" WIDTH="100%">${program['sequence']} - ${program['name']}</th>
  </tr>
</table>
%endif
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">   
    <tr>
      <td style="font-size:14px" WIDTH="15%">Fechas:</td>
      <td style="font-size:14px" align="left" WIDTH="85%">Del: ${vars['date_from']} Al: ${vars['date_to']}</td>    
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td align="left" style="font-size:12px" WIDTH="7%">PARTIDA</td>
      <td align="center" style="font-size:12px" WIDTH="45%">DENOMINACION</td>
      <td align="center" style="font-size:12px" WIDTH="6%">ASIGNACION INCIAL <br>(A)</td>
      <td align="center" style="font-size:12px" WIDTH="6%">REFORMAS <br> (B)</td>
      <td align="center" style="font-size:12px" WIDTH="6%">CODIFCADO <br>(C)=A+B</td>
      <td align="center" style="font-size:12px" WIDTH="6%">COMPROMETIDO <br>(D)</td>
      <td align="center" style="font-size:12px" WIDTH="6%">DEVENGADO <br>(E)</td>
      <td align="center" style="font-size:12px" WIDTH="6%">PAGADO <br>(F)</td>
      <td align="center" style="font-size:12px" WIDTH="6%">SALDO X COMP <br>(G)=C-D</td>
      <td align="center" style="font-size:12px" WIDTH="6%">SALDO X DEVENGAR <br>(H)=C-E</td>
    </tr>
  </thead>

  <%res=_get_totales(o,program['id'])%>
  <%result_dic=res.values()%>
  <%import operator%>
  <%dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))%>
  %for values in dic_ord:
  %if values['code']!=0 and values['code']!='0' and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['commited_amount']!=0 or values['devengado_amount']!=0 or values['paid_amount']!=0 or values['commited_balance']!=0 or values['devengado_balance']!=0):
  %if vars['tipo_nivel']=='p':
      %if (values['nivel']<= vars['nivel']) or vars['nivel']==0:
      %if vars['sobregiro']==False or (vars['sobregiro']==True and (values['devengado_balance']<0 or values['commited_balance']<0)):
      <tr style="border: 1px solid black; page-break-inside: avoid;">
       <td WIDTH="7%" align="left">${ values['code']}</td>
       <td WIDTH="45%" align="left">${ values['general_budget_name']}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['commited_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['devengado_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
       %if values['commited_balance']>0.01 or values['commited_balance']<-0.01:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['commited_balance'])}</td>
       %else:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(0)}</td>
       %endif
       %if values['devengado_balance']>0.01 or values['devengado_balance']<-0.01:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['devengado_balance'])}</td>
       %else:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(0)}</td>
       %endif
      </tr>
      %endif  
      %endif
  %elif vars['tipo_nivel']=='h':
      %if (values['nivel']>= vars['nivel']) or vars['nivel']==0:
      %if vars['sobregiro']==False or (vars['sobregiro']==True and (values['devengado_balance']<0 or values['commited_balance']<0)):
      <tr style="border: 1px solid black; page-break-inside: avoid;">
       <td WIDTH="7%" align="left">${ values['code']}</td>
       <td WIDTH="45%" align="left">${ values['general_budget_name']}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['commited_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['devengado_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
       %if values['commited_balance']>0.01 or values['commited_balance']<-0.01:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['commited_balance'])}</td>
       %else:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(0)}</td>
       %endif
       %if values['devengado_balance']>0.01 or values['devengado_balance']<-0.01:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['devengado_balance'])}</td>
       %else:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(0)}</td>
       %endif
      </tr>
      %endif  
      %endif
  %else:
      %if (vars['nivel'] > 0 and values['nivel']== vars['nivel']) or vars['nivel']==0:
      %if vars['sobregiro']==False or (vars['sobregiro']==True and abs(values['devengado_balance'])!=0 and abs(values['commited_balance'])!=0 and (values['devengado_balance']<0 or values['commited_balance']<0)):
      %if vars['sobregiro']==False or (vars['sobregiro']==True and (abs(values['devengado_balance'])<0.01 or abs(values['commited_balance'])>0.01)):
      <tr style="border: 1px solid black; page-break-inside: avoid;">
       <td WIDTH="7%" align="left">${ values['code']}</td>
       <td WIDTH="45%" align="left">${ values['general_budget_name']}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['commited_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['devengado_amount'])}</td>
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
       %if values['commited_balance']>0.01 or values['commited_balance']<-0.01:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['commited_balance'])}</td>
       %else:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(0)}</td>
       %endif
       %if values['devengado_balance']>0.01 or values['devengado_balance']<-0.01:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(values['devengado_balance'])}</td>
       %else:
       <td WIDTH="6%" align="right">${'{:,.2f}'.format(0)}</td>
       %endif
      </tr>
      %endif  
      %endif  
      %endif
  %endif  
  %endif
  %endfor
  <!--tfoot style="display: table-row-group"-->
<tr style="border: 1px solid black; page-break-inside: avoid;">
  <%
     totalp_planned_amount += res['total']['planned_amount']
     totalp_reform_amount += res['total']['reform_amount']
     totalp_codif_amount += res['total']['codif_amount']
     totalp_commited_amount += res['total']['commited_amount']
     totalp_devengado_amount += res['total']['devengado_amount']
     totalp_paid_amount += res['total']['paid_amount']
     totalp_commited_balance += res['total']['commited_balance']
     totalp_devengado_balance += res['total']['devengado_balance']
     %>
    <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right"></td>
    <td WIDTH="45%" style="font-weight: bold;font-size:12px" align="right">TOTALES</td>        
    <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['planned_amount'])}</td>
    <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['reform_amount'])}</td>
    <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['codif_amount'])}</td>    
    <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['commited_amount'])}</td>
    <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['devengado_amount'])}</td>
    <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['paid_amount'])}</td>
    <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['commited_balance'])}</td>
    <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['devengado_balance'])}</td>      
  <!--tfoot-->
</tr>

<!--/table-->
%endfor
%if program['id']!=False and j==len(programs):
<tr style="border: 1px solid black;">
  <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right"></td>
  <td WIDTH="45%" style="font-weight: bold;font-size:12px" align="right">TOTAL PROGRAMAS</td>        
  <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(totalp_planned_amount)}</td>
  <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(totalp_reform_amount)}</td>
  <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(totalp_codif_amount)}</td>
  <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(totalp_commited_amount)}</td>
  <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(totalp_devengado_amount)}</td>
  <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(totalp_paid_amount)}</td>
  <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(totalp_commited_balance)}</td>
  <td WIDTH="6%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(totalp_devengado_balance)}</td>
</tr>
  %endif
</table>
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
