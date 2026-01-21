<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>	
	</p>
    %for inv in objects :
	<table WIDTH=300 border="0" >
		<tr>
			<barCode code="code128" x="26.9mm">${inv.code or ''|entity}</barCode>		
		</tr>
		<tr>
			<td WIDTH=300  style="font-size:10px">${inv.name or ''|entity}</td>
		</tr>
		<tr>
			<td WIDTH=300  style="font-size:10px" > ${inv.employee_id.complete_name or ''|entity}</td>			
		</tr>
	</table>
    %endfor
</body>
</html>
