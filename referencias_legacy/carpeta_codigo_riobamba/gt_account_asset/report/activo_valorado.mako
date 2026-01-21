<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>

</head>
<body style="overflow:visible;">	
    %for valorado in objects:
    <tr style="border: 1px solid black;"><h2 style="text-align:center;" align="center">DIRECCION ADMINISTRATIVA</h2></tr>
<tr style="border: 1px solid black;"><h6 style="text-align:center;" align="center">REPORTE DE ACTIVOS VALORADO POR DEPARTAMENTO</h6></tr>
<tr style="border: 1px solid black;"><h6 style="text-align:center;" align="center">VALOR ${ valorado.valor } - ${ valorado.opc2 }</h6></tr>
<tr style="border: 1px solid black;"><h6 style="text-align:center;" align="center">Fechas: ${ valorado.date_start } - ${ valorado.date_stop }</h6></tr>
<!-- COLUMNA 1 -->
    <%
       first=0
       %>
    <table cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:12px;border: 1px solid black"  width="100%" border="1" rules="none">
     %for linea in generate_dict_valorado(valorado):
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
</body>
</html>
