<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>	
    %for inv in objects :
	<H2><center>${inv.tipo_acta_id.name}</center></H2>
	</p>
	<table WIDTH=1200>
		<tr WIDTH=1200>
			<td WIDTH=1200 ><p>${get_text(objects)}</p></td>						
		</tr>
	</table>
    %endfor
</body>
</html>
