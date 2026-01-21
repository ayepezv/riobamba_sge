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
    font-size:10px;
    }
    .project {
	padding:3px 3px 3px 3px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ababab), to(#ababab));
	background: -moz-linear-gradient(top,  #ededed,  #ababab);
    font-size:12px;
    }
    </style>
</head>
 <body>
   <h1 style="text-align:center;" align="center">Proyectos por Dirección / Coordinación</h1>
   <table class="table_basic table_title">
     <theader>
       <th>PERIODO FISCAL:</th>
       ${ get_fy() }
     </theader>
   </table>
   <hr>
   <table width="100%">
     <tr>
       <th width="55%">PROYECTO</th>
       <th width="10%">FECHA INICIO</th>
       <th width="10%">FECHA FIN</th>
       <th width="10%">ESTADO</th>
       <th width="10%">AVANCE (%)</th>
       <th width="5%">CUMPLIMIENTO (%)</th>                                     
     </tr>
     %for data in browse_group(objects):
     <br>
     <tr>
       <th width="50%" align="left">${ data['name'] } (${data['count']})</th>
       <th width="10%" align="center"></th> 
       <th width="10%" align="center"></th> 
       <th width="10%" align="center"></th> 
       <th width="10%" align="right">${ formatLang(data['progress'], digits=2) }%</th>
       <th width="10%" align="right">${ formatLang(data['compliance'], digits=2) }%</th>
     </tr>
     %for o in data['project_ids']:
     <tr style="font-size:10px;">
       <td style="font-size:10px;" width="50%" align="left">${ o.name }</td>
       <td style="font-size:10px;" width="10%" align="right">${ convert_date(o.date_start) }</td>
       <td style="font-size:10px;" width="10%" align="right">${ convert_date(o.date) }</td>
       <td style="font-size:10px;" width="10%" align="center">${ o.STATES_LOG[o.state] }</td>       
       <td style="font-size:10px;" width="10%" align="right">${ formatLang(o.activity_progress, digits=2) }%</td>
       <td style="font-size:10px;" width="10%" align="right">${ formatLang(o.compliance, digits=2) }%</td>
     </tr>
     %endfor
     %endfor
   </table>
</body>
</html>
