<html>
<head>
    <style type="text/css">
    ${css}
    tr.dept td {
    background-color: #454243;
    }
    table th {
	padding:3px 12px 9px 12px;
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
    table {
    width: 100%;
    }
    </style>
</head>
 <body>
   <h1 style="text-align:center;" align="center">Reporte de Actividades</h1>
  <table  width="100%">
    <tr>
      <th style="text-align: center;font-size:11px" width="55%">ACTIVIDAD</th>
      <th style="text-align: center;font-size:11px" width="13%">FECHA INICIO</th>
      <th style="text-align: center;font-size:11px" width="13%">FECHA FIN</th>
      <th style="text-align: center;font-size:11px" width="10%">PESO</th>
      <th style="text-align: center;font-size:11px" width="13%">AVANCE (%)</th>
    </tr>
  
  %for data in browse_group(objects):
  
     <tr>
       <th class="project" colspan="5" align="left">${ data['name'] }</th>
     </tr>
     %for o in data['project_ids']:
     <tr>
       <th align="left" colspan="4">${ o.name }</th>
       <th align="right" colspan="1">${ formatLang(get_progress(o), digits=2) }%</th>
     </tr>
     %for task in o.tasks:
     <tr>
       <td style="text-align: left;font-size:11px" width="55%">${ task.name}</td>
       <td style="text-align: center;font-size:11px" width="13%">${ task.date_start }</td>
       <td style="text-align: center;font-size:11px" width="13%">${ task.date_end }</td>
       <td style="text-align: center;font-size:11px" width="10%">${ task.weight }</td>
       <td style="text-align: right;font-size:11px" width="13%">${ formatLang(task.progress_time, digits=2) }%</td>
     </tr>
     %endfor
     %endfor
   </table>
   %endfor
</body>
</html>
