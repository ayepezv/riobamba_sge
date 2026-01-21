<html>
<head>
    <style type="text/css">
    ${css}
    td {
    padding:2px 4px 2px 4px;
    }
    table th {
	padding:2px 4px 2px 4px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
    font-size:12px;
    }
    .project {
	padding:3px 12px 9px 12px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ababab), to(#ababab));
	background: -moz-linear-gradient(top,  #ededed,  #ababab);
    font-size:12px;
    }
    </style>
</head>
 <body>
   <h1 style="text-align:center;" align="center">Proyectos por Eje</h1>
   <table class="table_basic table_title">
     <theader>
       <th>PERIODO FISCAL:</th>
       ${ get_fy() }
     </theader>
   </table>
   <hr>
   <table width="100%">
     %for data in browse_group(objects):
     <tr>
       <th style="font-size:11px;" width="26%">DIRECCION</th>
       <th style="font-size:11px;" width="34%">${ data['name'] } (${data['count']})</th>
       <th style="font-size:11px;" width="8%">FECHA INICIO</th>
       <th style="font-size:11px;" width="8%">FECHA FIN</th>
       <th style="font-size:11px;" width="8%">ESTADO</th>
       <th style="font-size:11px;" width="8%">AVANCE (%)</th>
       <th style="font-size:10px;" width="8%">CUMPLIMIENTO (%)</th>                                     
     </tr>
     <tr>
       <th width="26%" align="center"></th> 
       <th width="34%" align="left"></th>
       <th width="8%" align="center"></th> 
       <th width="8%" align="center"></th> 
       <th width="8%" align="center"></th> 
       <th width="8%" align="right">${ formatLang(data['progress'], digits=2) }%</th>
       <th width="8%" align="right">${ formatLang(data['compliance'], digits=2) }%</th>
     </tr>
     %for o in data['project_ids']:
     <tr style="font-size:10px;">
       <td width="26%">${ o.department_id.name }</td>
       <td width="34%" align="left">${ o.name }</td>
       <td width="8%" align="right">${ convert_date(o.date_start) }</td>
       <td width="8%" align="right">${ convert_date(o.date) }</td>
       <td width="8%" align="center">${ o.STATES_LOG[o.state] }</td>       
       <td width="8%" align="right">${ formatLang(o.activity_progress, digits=2) }%</td>
       <td width="8%" align="right">${ formatLang(o.compliance, digits=2) }%</td>
     </tr>
     %endfor
     %endfor
   </table>
</body>
</html>
