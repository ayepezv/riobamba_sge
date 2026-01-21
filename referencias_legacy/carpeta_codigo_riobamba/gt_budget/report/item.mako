<html>
<head WIDTH="200%">
    <!--style type="text/css">
        ${css}    ${css}
    td {
    padding:2px 4px 2px 4px;
    font-size:10px;
    }
    table th {
	padding:2px 4px 2px 4px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
    font-size:10px;
    }
    .project {
	padding:3px 12px 9px 12px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ababab), to(#ababab));
	background: -moz-linear-gradient(top,  #ededed,  #ababab);
    font-size:12px;
    }
    table_basic {
    width: 100%;
    }
    table_title {
	border-top:1px solid #ffffff;
    }
    hr {
    border: 0;
    border-bottom: 1px solid #FFFFFF;
    border-top: 1px solid #AAAAAA;
    clear: both;
    height: 0;
    margin: 12px 0 18px;
    }
    </style-->
</head>
<body WIDTH="100%">
  <H3><left>DIRECCION: DIRECCION FINANCIERA</center></H3>
<H4><left>LISTA DE PARTIDAS</center></H4>
<!--table WIDTH="200%" >
  <tr>
    <td WIDTH="20%" style="text-align:left;font-size:18px"></td>	
    <td WIDTH="40%" style="text-align:left;font-size:18px"></td>					
    <td WIDTH="10%" style="text-align:center;font-size:18px"></td>
    <td WIDTH="8%" style="text-align:center;font-size:18px"></td>
      <td WIDTH="8%" style="text-align:center;font-size:18px"></td>
    <td WIDTH="8%" style="text-align:center;font-size:18px"></td>
      <td WIDTH="8%" style="text-align:center;font-size:18px"></td>
      <td WIDTH="8%" style="text-align:center;font-size:18px"></td>			
    <tr/>
  </table-->
  <%
     total = 0
     %> 
<table WIDTH="100%"  rules="none" border="1" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:8px">
  <tr BGCOLOR="#D8D8D8">
    <td WIDTH="30%" style="text-align:left;font-size:10px">Codigo</td>
    <td WIDTH="10%" style="text-align:left;font-size:10px">Inicial</td>	
    <td WIDTH="10%" style="text-align:center;font-size:10px">Reforma</td>
    <td WIDTH="10%" style="text-align:center;font-size:10px">Codificado</td>
    <td WIDTH="10%" style="text-align:center;font-size:10px">Comprometido</td>
    <td WIDTH="10%" style="text-align:center;font-size:10px">Devengado</td>
    <td WIDTH="10%" style="text-align:center;font-size:10px">Pagado</td>
    <td WIDTH="10%" style="text-align:center;font-size:10px">Disponible</td>
  <tr/>

%for inv in objects :

<tr style="border: 1px solid black; page-break-inside: avoid;" >
  <td WIDTH="30%" style="border: 1px solid black;text-align:left;font-size:8px">${inv.code or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:left;font-size:8px">${inv.planned_amount or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:center;font-size:8px">${inv.reform_amount or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:center;font-size:8px">${inv.codif_amount or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:center;font-size:8px">${inv.commited_amount or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:center;font-size:8px">${inv.devengado_amount or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:center;font-size:8px">${inv.paid_amount or ''|entity}</td>
  <td WIDTH="10%" style="border: 1px solid black;text-align:center;font-size:8px">${inv.avai_amount or ''|entity}</td>
</tr>
%endfor
</table>
<table width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
  </tr>
  <tr style="font-size:10px">
    <th width="33%">Creado por</th>
  </tr>  
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
    <th>__________________</th>
  </tr>
  <tr style="font-size:10px">
    <th width="33%">${user.employee_id.complete_name or ''}</th>
  </tr>  
</table>
</body>
</html>
