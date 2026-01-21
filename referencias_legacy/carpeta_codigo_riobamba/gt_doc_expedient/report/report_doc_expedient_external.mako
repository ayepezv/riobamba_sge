<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
        <img src="../images/project.png" border=0>	
	    %for expedient in objects:  
			<center><h2>Tramite: ${expedient.code}</h2></center>
			<br/>
			<center><h2>Fecha: ${expedient.creation_date}</h2></center>
			<br/>
			<center><h2>Solicitante: ${expedient.institution}</h2></center>
			<br/>
			<center><h2>Descripción: ${expedient.resumen}</h2></center>
			<br/>
			<center><h3>Usted podrá realizar el seguimiento de</h3></center
			<center><h3>sus trámites en internet ingresando a</h3></center>
			<center><h1>http://vus.azuay.gob.ec</h1></center>
			<center><h3>o llamando al Gobierno Provincial del</h3></center>
			<center><h3>Azuay al teléfono <h1>07-2842588</h1></h3></center>
			<center><h3>extensión<h1>2601</h1></h3></center>
			
			
			
			
			
			<center><h3>Administración 2009-2014</h3></center>
 
        %endfor
	
    </p>
    </p>
</body>
</html>
