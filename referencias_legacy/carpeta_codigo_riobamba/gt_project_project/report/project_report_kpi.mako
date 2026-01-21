<html>
<head>
    <style type="text/css">
      body h2 {
      font-size:14px;
      }
      h2 {
      align:center;
      }
      #container {
        width : 600px;
        height: 384px;
        margin: 8px auto;
      }
      table th {
	  padding:3px 12px 9px 12px;
	  border-top:1px solid #fafafa;
	  background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	  background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
      font-size:12px;
      }
      .kpi {
	  padding:6px 12px 6px 12px;
	  border-top:1px solid #fafafa;
	  background: -webkit-gradient(linear, left top, left bottom, from(#ababab), to(#ababab));
	  background: -moz-linear-gradient(top,  #ededed,  #ababab);
      font-size:12px;
     
    }
    </style>
</head>
 <body>
   <table width="100%">
     <tr>
       <td colspan="27"><h1 style="text-align:center;" align="center">Reporte de Indicadores</h1></td>
     </tr>
     <tr>
       <th width="28%"></th>
       <th width="12%" colspan="2">ENERO</th>
       <th width="12%" colspan="2">FEBRERO</th>
       <th width="12%" colspan="2">MARZO</th>
       <th width="12%" colspan="2">ABRIL</th>
       <th width="12%" colspan="2">MAYO</th>
       <th width="12%" colspan="2">JUNIO</th>
       <th width="12%" colspan="2">JULIO</th>
       <th width="12%" colspan="2">AGOSTO</th>
       <th width="12%" colspan="2">SEPTIEMBRE</th>
       <th width="12%" colspan="2">OCTUBRE</th>
       <th width="12%" colspan="2">NOVIEMBRE</th>
       <th width="12%" colspan="2">DICIEMBRE</th>
       <th width="12%" colspan="2">TOTAL</th>
     </tr>
     <tr>
       <th width="28%"></th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
       <th width="6%">PLAN</th>
       <th width="6%">AVANCE</th>
     </tr>
   %for o in objects:
     <tr>
       <td class="kpi" width="28%" colspan="27"><b>${ o.name }</b></td>
     </tr>
     %for kpi in o.pointer_detail_ids:
     <tr>
       <td style="font-size:11px">${ kpi.kpi_id.name }</td>
       %for item in get_months(kpi):
       <td style="text-align: right;font-size:11px">${ formatLang(item['planned'], digits=2) }</td>
       <td style="text-align: right;font-size:11px">${ formatLang(item['executed'], digits=2) } </td>
       %endfor
       <td style="text-align: right;font-size:11px"><b>${ formatLang(kpi.planned, digits=2) } </b></td>
       <td style="text-align: right;font-size:11px"><b>${ formatLang(item['executed'], digits=2) }</b> </td>
     </tr>
     %endfor
     <br>
   %endfor
   </table>
</body>
</html>
