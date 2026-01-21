<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body style="overflow:visible;">	
    %for payroll in objects:
<!-- COLUMNA 1 -->
    <table style="font-size:8px;overflow:visible;" width="100%" border="1" rules="rows">

	%for linea in generate_dict(payroll):
	<tr style="page-break-before:always;overflow:visible;">
	  <%
	     bandera=0
	     total=0
	  %>
	  %if linea[0]=='TOTAL':
	  <%
	     total=1
	  %>
	  %endif
	  %for celda in linea:
	  %if total==1:
	  <th style="text-align:right;text-weight:bold;">${celda}</th>
	  %else:
	  
	  %if bandera==0:
	  <th style="text-weight:bold;text-align:left;">${celda}</th>
	  <%
	     bandera=1
	  %>
	  %else:
	  <th style="text-align:right;text-weight:normal;">${celda}</th>
	  %endif

	  %endif
	  %endfor
    	</tr>
	%endfor
    </table>
<!-- FIN COLUMNA 1 -->
    %endfor

</body>
</html>
