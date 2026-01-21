<html>
  <head>
    <style type="text/css">
      .break { page-break-before: always; }
      table {
	  font-family:Arial, Helvetica, sans-serif;
	  color:#666;
	  font-size:12px;
	  margin:20px;
	  -moz-border-radius:2px;
	  -webkit-border-radius:1px;
	  -moz-box-shadow: 0 1px 2px #d1d1d1;
	  -webkit-box-shadow: 0 0px 0px #d1d1d1;
      }
      table th {
	  padding:3px 12px 9px 12px;
	  border-top:1px solid #fafafa;
	  background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	  background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
      }
      table th:first-child {
	  text-align: left;
	  padding-left:20px;
      }
      table td {
	  padding:5px;
      }
      h1 {
      font-size:12px;
      }
    </style>    
  </head>
  <body>
    %for k,v in data['form'].items():
    <table cellpadding="0" cellspacing="0" border="0" width="100%">
      <caption>${ data['deps'][k] }</caption>
      <thead>
        <tr>
          <th width="10%">CANTON</th>
          <th width="10%">PARROQUIA</th>
          <th width="50%">PROYECTO</th>
          <th width="20%">PRESUPUESTO</th>
        </tr>
      </thead>
      <tbody>
      %for item in v:
       <tr>
         <td>
         </td>
         <td></td>
         <td>${ item[0] }</td>
         <td style="text-align:center;">$ ${ item[1]}</td>
       </tr> 
      %endfor
      </tbody>
    </table>
    %endfor
  </body>
</html>
