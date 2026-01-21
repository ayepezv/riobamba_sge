<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>

</head>
<body style="overflow:visible;">	
    %for payroll in objects:
    <tr style="border: 1px solid black;"><h2 style="text-align:center;" align="center">${payroll.name}</h1></tr>
<tr style="border: 1px solid black;"><h5 style="text-align:center;" align="center">DESDE: ${payroll.date_start} HASTA: ${payroll.date_end} </h5></tr>
<!-- COLUMNA 1 -->
%for program_id in all_programas(payroll):
    <%
       first=0
       %>
    <table cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px;border: 1px solid black"  width="100%" border="1" rules="none">
      <tr style="border: 1px solid black;"><h2 style="text-align:center;" align="center">PROGRAMA : ${program_id.sequence} - ${program_id.name}</h1></tr>
     %for linea in generate_dict(payroll,program_id):
          %if first==0:
           <%
           maxl=len(linea)
           %>
            <thead BGCOLOR="#D8D8D8" style="display: table-header-group;border: 1px solid black;text-align:left;font-size:20px;page-break-inside:avoid">
  	  %else:
	    <tr style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">
	  %endif
	<%
	     bandera=0
	     total=0
	  %>
	  %if linea[0]=='TOTAL':
	  <%
	     total=1
	  %>
	  %endif
	   <%
              lenlinea=len(linea)
	      nc = 1
           %>
	   %for celda in linea:
	   %if lenlinea<maxl-1:
	       %if nc==1:
	              <th BGCOLOR="#D8D8D8" style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">${celda}</th>
	       %else:
		      %if nc==lenlinea:
                           <th colspan="8" BGCOLOR="#D8D8D8" style="border: 1px solid black;text-align:left;font-size:11px;" >${celda}</th>
	              %else:
			   <th BGCOLOR="#D8D8D8" style="border: 1px solid black;text-align:left;font-size:11px;" >${celda}</th>
		      %endif
			    
	       %endif
          %else:
	       %if nc==1:
	              <th  style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid">${celda}</th>
	       %else:
         	      <th  style="border: 1px solid black;text-align:right;font-size:11px;" >${celda}</th>
	        %endif
	   %endif
	   <%
	      nc = nc + 1
           %>	       
	  %endfor
	  %if first==0:
            </thead>
  	  %else:
	    </tr>
	  %endif
	  <%
	      first=first+1
	  %>
	%endfor
    </table>
<!-- FIN COLUMNA 1 -->
    %endfor
<table cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px"   width="100%" border="1" rules="none">
  <tr><h1 style="text-align:center;" align="center">TOTALES ROL</h1></tr>
  %for lineac in get_rubro_total(payroll):
  <tr style="border: 1px solid black;text-align:left;font-size:12px;page-break-inside:avoid"  >
    %for celdac in lineac:
	  <th style="border: 1px solid black;text-align:right;font-size:12px;page-break-inside:avoid" >${celdac}</th>
	  %endfor
</tr>
%endfor
</table>
%endfor
  <table width="100%" style="page-break-inside:avoid">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="font-size:11px">
      <th width="33%">REALIZADO POR</th>
      <th width="33%">REVISADO POR</th>
      <th width="33%">AUTORIZADO</th>
    </tr>  
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
      </tr>
    <tr style="height:35px">
      <th>______________________</th>
      <th>______________________</th>
      <th>______________________</th>
    </tr>
    <tr style="font-size:11px">
      <th width="33%">${user.employee_id.complete_name}</th>
      <th width="33%">CASTILLO HEREDIA SOFIA ROSA</th>
      <th width="33%">${user.context_department_id.manager_id.complete_name}</th>
    </tr>  
  </table>
 <table width="100%" style="page-break-inside:avoid">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th>________________________</th>
      <th>________________________</th>
      <th>________________________</th>
      <th>________________________</th>
    </tr>
    <tr style="font-size:11px">
      <th width="25%">REVISADO POR</th>
      <th width="25%">CONTADOR GENERAL</th>
      <th width="25%">ESPECIALISTA DE PRESUPUESTOS</th>
      <th width="25%">DIRECTOR FINANCIERO</th>
    </tr>  
    <tr style="font-size:11px">
      <th width="25%"></th>
      <th width="25%"></th>
      <th width="25%"></th>
      <th width="25%">AUTORIZO TRANSFERENCIA</th>
    </tr>  
  </table>
</body>
</html>
