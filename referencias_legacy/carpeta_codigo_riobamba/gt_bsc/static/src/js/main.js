openerp.gt_bsc = function (db) {
    
    db.gt_bsc = {};
    
    //PLANTILLA Formulacion
    db.gt_bsc.BscFormulacion = db.web.OldWidget.extend({
    	template: 'bsc_formulacion',
    	init: function() {
            this._super.apply(this, arguments);
            this.ds_formulacion = new db.web.DataSetSearch(this, 'bsc.formulation');
            this.ds_project_configuration = new db.web.DataSetSearch(this, 'project.configuration');
            this.rango1_min = 0;
            this.rango1_max = 0;
            this.rango2_min = 0;
            this.rango2_max = 0;
            this.rango3_min = 0;
            this.rango3_max = 0;
            this.color1 = "#F74447";
            this.color2 = "#F79A44";
            this.color3 = "#01DF3A";
        },
        start: function (){
        	
        	self = this;
        	this.ds_project_configuration.read_slice(['id','name','active','red_start','red_end','yel_start','yel_end','blue_start','blue_end'], {domain: [['active', '=', true ]] }).then(function(result) {
        		for(var i in result) {
        			self.rango1_min = result[i].red_start;
		            self.rango1_max = result[i].red_end;
		            self.rango2_min = result[i].yel_start;
		            self.rango2_max = result[i].yel_end;
		            self.rango3_min = result[i].blue_start;
		            self.rango3_max = result[i].blue_end;
        		}
        	});
			this.ds_formulacion.read_slice(['id','fy_id','mision','vision','politica','mision_indicador1','mision_indicador2','vision_indicador1','vision_indicador2','politica_indicador1','politica_indicador2'], 0).then(function(result) {
				for(var i in result) {
                    var indicador1 = parseFloat(result[i].mision_indicador1.toFixed(2));
                    var indicador2 = parseFloat(result[i].mision_indicador2.toFixed(2));
                    var color1 = "#FFFFFF";
                    var color2 = "#FFFFFF";
                    if ((indicador1>=self.rango1_min) && (indicador1<=self.rango1_max)) {
						color1=self.color1;
					}
					if ((indicador1>=self.rango2_min) && (indicador1<=self.rango2_max)) {
						color1=self.color2;
					}
					if ((indicador1>=self.rango3_min) && (indicador1<=self.rango3_max)) {
						color1=self.color3;
					}
					if ((indicador2>=self.rango1_min) && (indicador2<=self.rango1_max)) {
						color2=self.color1;
					}
					if ((indicador2>=self.rango2_min) && (indicador2<=self.rango2_max)) {
						color2=self.color2;
					}
					if ((indicador2>=self.rango3_min) && (indicador2<=self.rango3_max)) {
						color2=self.color3;
					}
	                $(".bsc_mision").append('<div style="width:90%;" class="borde_sombra fuente_pequena">' + result[i].mision + 
	                	'<br/><table width="100%"><tr><td width="20%">Eficacia:</td><td width="80%">' +
	                	'<div id="progress"><span id="percent" >' + indicador1 + '%</span><div id="bar" style="width:' + indicador1 + '%;background-color:' + color1 + ';"></div></div>' +
	                	'</td></tr><tr><td width="20%">Eficiencia:</td><td width="80%">' +
	                	'<div id="progress"><span id="percent" >' + indicador2 + '%</span><div id="bar" style="width:' + indicador2 + '%;background-color:' + color2 + ';"></div></div>' +
	                	'</td></tr></table>' + 
	                	'</div>');
                    var mision_promedio = (indicador1+indicador2)/2;
		            var chart1 = new AmCharts.AmAngularGauge();
	                chart1.axes = [{
	                    startValue: 0,
	                    axisThickness: 1,
	                    endValue: 100,
	                    //bottomTextYOffset: -20,
	                    bottomText: mision_promedio + "%\nTotal",
	                    bottomTextFontSize: 15,
	                    fontSize:8,
	                    bands: [{
	                            startValue: self.rango1_min,
	                            endValue: self.rango1_max,
	                            color: self.color1,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango2_min,
	                            endValue: self.rango2_max,
	                            color: self.color2,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango3_min,
	                            endValue: self.rango3_max,
	                            color: self.color3,
	                            innerRadius: "75%"
	                        }
	                    ]
	                }];
	                chart1.arrows = [{value:mision_promedio}];
	                chart1.write("bsc_mision_promedio");
	                
	                
	                indicador1 = parseFloat(result[i].vision_indicador1.toFixed(2));
                    indicador2 = parseFloat(result[i].vision_indicador2.toFixed(2));
                    color1 = "#FFFFFF";
                    color2 = "#FFFFFF";
                    if ((indicador1>=self.rango1_min) && (indicador1<=self.rango1_max)) {
						color1=self.color1;
					}
					if ((indicador1>=self.rango2_min) && (indicador1<=self.rango2_max)) {
						color1=self.color2;
					}
					if ((indicador1>=self.rango3_min) && (indicador1<=self.rango3_max)) {
						color1=self.color3;
					}
					if ((indicador2>=self.rango1_min) && (indicador2<=self.rango1_max)) {
						color2=self.color1;
					}
					if ((indicador2>=self.rango2_min) && (indicador2<=self.rango2_max)) {
						color2=self.color2;
					}
					if ((indicador2>=self.rango3_min) && (indicador2<=self.rango3_max)) {
						color2=self.color3;
					}
	                $(".bsc_vision").append('<div style="width:90%;" class="borde_sombra fuente_pequena">' + result[i].vision + 
	                	'<br/><table width="100%"><tr><td width="20%">Eficacia:</td><td width="80%">' +
	                	'<div id="progress"><span id="percent" >' + indicador1 + '%</span><div id="bar" style="width:' + indicador1 + '%;background-color:' + color1 + ';"></div></div>' +
	                	'</td></tr><tr><td width="20%">Eficiencia:</td><td width="80%">' +
	                	'<div id="progress"><span id="percent" >' + indicador2 + '%</span><div id="bar" style="width:' + indicador2 + '%;background-color:' + color2 + ';"></div></div>' +
	                	'</td></tr></table>' + 
	                	'</div>');
                    var vision_promedio = (indicador1+indicador2)/2;
		            var chart3 = new AmCharts.AmAngularGauge();
	                chart3.axes = [{
	                    startValue: 0,
	                    axisThickness: 1,
	                    endValue: 100,
	                    //bottomTextYOffset: -20,
	                    bottomText: vision_promedio + "%\nTotal",
	                    bottomTextFontSize: 15,
	                    fontSize:8,
	                    bands: [{
	                            startValue: self.rango1_min,
	                            endValue: self.rango1_max,
	                            color: self.color1,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango2_min,
	                            endValue: self.rango2_max,
	                            color: self.color2,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango3_min,
	                            endValue: self.rango3_max,
	                            color: self.color3,
	                            innerRadius: "75%"
	                        }
	                    ]
	                }];
	                chart3.arrows = [{value:vision_promedio}];
	                chart3.write("bsc_vision_promedio");
	                
	                indicador1 = parseFloat(result[i].politica_indicador1.toFixed(2));
                    indicador2 = parseFloat(result[i].politica_indicador2.toFixed(2));
                    color1 = "#FFFFFF";
                    color2 = "#FFFFFF";
                    if ((indicador1>=self.rango1_min) && (indicador1<=self.rango1_max)) {
						color1=self.color1;
					}
					if ((indicador1>=self.rango2_min) && (indicador1<=self.rango2_max)) {
						color1=self.color2;
					}
					if ((indicador1>=self.rango3_min) && (indicador1<=self.rango3_max)) {
						color1=self.color3;
					}
					if ((indicador2>=self.rango1_min) && (indicador2<=self.rango1_max)) {
						color2=self.color1;
					}
					if ((indicador2>=self.rango2_min) && (indicador2<=self.rango2_max)) {
						color2=self.color2;
					}
					if ((indicador2>=self.rango3_min) && (indicador2<=self.rango3_max)) {
						color2=self.color3;
					}
	                $(".bsc_politica").append('<div style="width:90%;" class="borde_sombra fuente_pequena">' + result[i].politica + 
	                	'<br/><table width="100%"><tr><td width="20%">Eficacia:</td><td width="80%">' +
	                	'<div id="progress"><span id="percent" >' + indicador1 + '%</span><div id="bar" style="width:' + indicador1 + '%;background-color:' + color1 + ';"></div></div>' +
	                	'</td></tr><tr><td width="20%">Eficiencia:</td><td width="80%">' +
	                	'<div id="progress"><span id="percent" >' + indicador2 + '%</span><div id="bar" style="width:' + indicador2 + '%;background-color:' + color2 + ';"></div></div>' +
	                	'</td></tr></table>' + 
	                	'</div>');
                    var politica_promedio = (indicador1+indicador2)/2;
		            var chart5 = new AmCharts.AmAngularGauge();
	                chart5.axes = [{
	                    startValue: 0,
	                    axisThickness: 1,
	                    endValue: 100,
	                    //bottomTextYOffset: -20,
	                    bottomText: politica_promedio + "%\nTotal",
	                    bottomTextFontSize: 15,
	                    fontSize:8,
	                    bands: [{
	                            startValue: self.rango1_min,
	                            endValue: self.rango1_max,
	                            color: self.color1,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango2_min,
	                            endValue: self.rango2_max,
	                            color: self.color2,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango3_min,
	                            endValue: self.rango3_max,
	                            color: self.color3,
	                            innerRadius: "75%"
	                        }
	                    ]
	                }];
	                chart5.arrows = [{value:politica_promedio}];
	                chart5.write("bsc_politica_promedio");
				}
            });
			
        },
    });
    
    //PLANTILLA Inicio
    db.gt_bsc.BscInicio = db.web.OldWidget.extend({
    	template: 'bsc_inicio',
    	init: function() {
            this._super.apply(this, arguments);
            this.ds_formulacion = new db.web.DataSetSearch(this, 'bsc.formulation');
            this.ds_project_configuration = new db.web.DataSetSearch(this, 'project.configuration');
            this.rango1_min = 0;
            this.rango1_max = 0;
            this.rango2_min = 0;
            this.rango2_max = 0;
            this.rango3_min = 0;
            this.rango3_max = 0;
            this.color1 = "#F74447";
            this.color2 = "#F79A44";
            this.color3 = "#01DF3A";
        },
        start: function (){
        	
        	self = this;
        	this.ds_project_configuration.read_slice(['id','name','active','red_start','red_end','yel_start','yel_end','blue_start','blue_end'], {domain: [['active', '=', true ]] }).then(function(result) {
        		for(var i in result) {
        			self.rango1_min = result[i].red_start;
		            self.rango1_max = result[i].red_end;
		            self.rango2_min = result[i].yel_start;
		            self.rango2_max = result[i].yel_end;
		            self.rango3_min = result[i].blue_start;
		            self.rango3_max = result[i].blue_end;
        		}
        	});
			this.ds_formulacion.read_slice(['id','fy_id','general_indicador1','general_indicador2'], 0).then(function(result) {
				for(var i in result) {
                    var indicador1 = parseFloat(result[i].general_indicador1.toFixed(2));
                    var indicador2 = parseFloat(result[i].general_indicador2.toFixed(2));
                    var color1 = "#FFFFFF";
                    var color2 = "#FFFFFF";
                    if ((indicador1>=self.rango1_min) && (indicador1<=self.rango1_max)) {
						color1=self.color1;
					}
					if ((indicador1>=self.rango2_min) && (indicador1<=self.rango2_max)) {
						color1=self.color2;
					}
					if ((indicador1>=self.rango3_min) && (indicador1<=self.rango3_max)) {
						color1=self.color3;
					}
					if ((indicador2>=self.rango1_min) && (indicador2<=self.rango1_max)) {
						color2=self.color1;
					}
					if ((indicador2>=self.rango2_min) && (indicador2<=self.rango2_max)) {
						color2=self.color2;
					}
					if ((indicador2>=self.rango3_min) && (indicador2<=self.rango3_max)) {
						color2=self.color3;
					}
		            var chart1 = new AmCharts.AmAngularGauge();
	                chart1.axes = [{
	                    startValue: 0,
	                    axisThickness: 1,
	                    endValue: 100,
	                    //bottomTextYOffset: -20,
	                    bottomText: indicador1 + "%\nEficacia",
	                    bottomTextFontSize: 15,
	                    fontSize:8,
	                    bands: [{
	                            startValue: self.rango1_min,
	                            endValue: self.rango1_max,
	                            color: self.color1,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango2_min,
	                            endValue: self.rango2_max,
	                            color: self.color2,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango3_min,
	                            endValue: self.rango3_max,
	                            color: self.color3,
	                            innerRadius: "75%"
	                        }
	                    ]
	                }];
	                chart1.arrows = [{value:indicador1}];
	                chart1.write("bsc_indicador1");
	                
		            var chart3 = new AmCharts.AmAngularGauge();
	                chart3.axes = [{
	                    startValue: 0,
	                    axisThickness: 1,
	                    endValue: 100,
	                    //bottomTextYOffset: -20,
	                    bottomText: indicador2 + "%\nEficiencia",
	                    bottomTextFontSize: 15,
	                    fontSize:8,
	                    bands: [{
	                            startValue: self.rango1_min,
	                            endValue: self.rango1_max,
	                            color: self.color1,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango2_min,
	                            endValue: self.rango2_max,
	                            color: self.color2,
	                            innerRadius: "75%"
	                        },
	                        {
	                            startValue: self.rango3_min,
	                            endValue: self.rango3_max,
	                            color: self.color3,
	                            innerRadius: "75%"
	                        }
	                    ]
	                }];
	                chart3.arrows = [{value:indicador2}];
	                chart3.write("bsc_indicador2");
				}
            });
			
        },
    });
    
    //PLANTILLA Ejes Estratégicos
    db.gt_bsc.BscEjesEstrategicos = db.web.OldWidget.extend({
    	template: 'bsc_ejesestrategicos',
    	init: function() {
    		self = this;
            this._super.apply(this, arguments);
            //informacion de ejes
            this.ds_ejes = new db.web.DataSetSearch(this, 'project.axis');
            this.datos_ejes = [];
            //informacion de estrategias
            this.ds_estrategias = new db.web.DataSetSearch(this, 'project.estrategy');
            this.datos_estrategias = [];
            //informacion de configuracion
            this.ds_project_configuration = new db.web.DataSetSearch(this, 'project.configuration');
            this.rango1_min = 0;
            this.rango1_max = 0;
            this.rango2_min = 0;
            this.rango2_max = 0;
            this.rango3_min = 0;
            this.rango3_max = 0;
            this.color1 = "#F74447";
            this.color2 = "#F79A44";
            this.color3 = "#01DF3A";
        },
        start: function (){
        	self = this;
        	var tabla_mapa = "";
        	var tabla_estrategias = "";
        	function crear(){
        		//$(".pruebas").append(self.datos_ejes.length);
        		if (self.datos_ejes.length>0){
        			var porcentaje = 100/self.datos_ejes.length;
        			var contador_ejes = -1;
        			var contador_estrategias = -1;
        			for(var i in self.datos_ejes) {
        				contador_ejes = contador_ejes + 1;
        				contador_estrategias = 0;
        				var indicador1 = self.datos_ejes[i].bsc_indicador1.toFixed(2);
        				var indicador2 = self.datos_ejes[i].bsc_indicador2.toFixed(2);
        				var color1 = "#FFFFFF";
        				var color2 = "#FFFFFF";
        				if ((indicador1>=self.rango1_min) && (indicador1<=self.rango1_max)) {
        					color1=self.color1;
        				}
        				if ((indicador1>=self.rango2_min) && (indicador1<=self.rango2_max)) {
        					color1=self.color2;
        				}
        				if ((indicador1>=self.rango3_min) && (indicador1<=self.rango3_max)) {
        					color1=self.color3;
        				}
        				if ((indicador2>=self.rango1_min) && (indicador2<=self.rango1_max)) {
        					color2=self.color1;
        				}
        				if ((indicador2>=self.rango2_min) && (indicador2<=self.rango2_max)) {
        					color2=self.color2;
        				}
        				if ((indicador2>=self.rango3_min) && (indicador2<=self.rango3_max)) {
        					color2=self.color3;
        				}
        				tabla_mapa = tabla_mapa + "<div style='position:absolute;width:150px;height:100px;left:" + (25+(contador_ejes*200)) + "px;top:" + (contador_estrategias*150) + "px;' class='borde_sombra fuente_pequena degradado'>" + 
        				"<table width='100%'><tr><td height='60px' colspan='2'><center><b>" + self.datos_ejes[i].name + "</b></center></td>" +
        				'</tr><tr><td width="20%">Eficacia:</td><td width="80%">' +
        				'<div id="progress"><span id="percent" >' + indicador1 + '%</span><div id="bar_dos" style="width:' + indicador1 + '%;background-color:' + color1 + ';"></div></div>' +
        				'</td></tr><tr><td width="20%">Eficiencia:</td><td width="80%">' +
        				'<div id="progress"><span id="percent" >' + indicador2 + '%</span><div id="bar_dos" style="width:' + indicador2 + '%;background-color:' + color2 + ';"></div></div>' +
        				'</td></tr></table>' + 
        				"</div>";
        				for(var j in self.datos_estrategias) {
        					if (self.datos_estrategias[j].axis_id[0]==self.datos_ejes[i].id){
        						contador_estrategias = contador_estrategias + 1;
        						var indicador1 = self.datos_estrategias[j].bsc_indicador1.toFixed(2);
        						var indicador2 = self.datos_estrategias[j].bsc_indicador2.toFixed(2);
        						var color1 = "#FFFFFF";
        						var color2 = "#FFFFFF";
        						if ((indicador1>=self.rango1_min) && (indicador1<=self.rango1_max)) {
        							color1=self.color1;
    							}
    							if ((indicador1>=self.rango2_min) && (indicador1<=self.rango2_max)) {
    								color1=self.color2;
								}
								if ((indicador1>=self.rango3_min) && (indicador1<=self.rango3_max)) {
									color1=self.color3;
								}
								if ((indicador2>=self.rango1_min) && (indicador2<=self.rango1_max)) {
									color2=self.color1;
								}
								if ((indicador2>=self.rango2_min) && (indicador2<=self.rango2_max)) {
									color2=self.color2;
								}
								if ((indicador2>=self.rango3_min) && (indicador2<=self.rango3_max)) {
									color2=self.color3;
								}
								tabla_mapa = tabla_mapa + 
								"<div style='position:absolute;width:150px;height:100px;left:" + (25+(contador_ejes*200)) + "px;top:" + (contador_estrategias*150) + "px;' class='borde_sombra fuente_pequena estrategia_" + self.datos_estrategias[j].id + "' id='estrategia_" + self.datos_estrategias[j].id + "'>" + 
								"<table width='100%'><tr><td height='60px' colspan='2' id='estrategia_" + self.datos_estrategias[j].id + "'><center><b>" + self.datos_estrategias[j].name + "</b></center></td>" +
								'</tr><tr><td width="20%" id="estrategia_' + self.datos_estrategias[j].id + '">Eficacia:</td><td width="80%">' +
								'<div id="progress"><span id="percent" >' + indicador1 + '%</span><div id="bar_dos" style="width:' + indicador1 + '%;background-color:' + color1 + ';"></div></div>' +
								'</td></tr><tr><td width="20%" id="estrategia_' + self.datos_estrategias[j].id + '">Eficiencia:</td><td width="80%">' +
								'<div id="progress"><span id="percent" >' + indicador2 + '%</span><div id="bar_dos" style="width:' + indicador2 + '%;background-color:' + color2 + ';"></div></div>' +
								'</td></tr></table>' + 
								"</div>";
							}
						}
					}
					$(".bsc_div_mapa").append(tabla_mapa);
					//for(var i in self.datos_ejes) {
						for(var j in self.datos_estrategias) {
							self.$element.find(".estrategia_"+ self.datos_estrategias[j].id).click(_.bind(function (a){
								/*$('_blank').do_action({
									type: 'ir.actions.act_window',
									res_model: "project.project",
									res_id: self.datos_ejes[i].id,
									views: [[false, 'tree']],
									target: '_blank',
									nodestroy:true,
								});*/
								if ($(a.target).attr('id')){
									var win = window.open('http://10.10.10.30/web/webclient/home#view_type=page&title=Estrategias&model=project.estrategy&action_id=1051&id='+$(a.target).attr('id').substr(11),'_blank');
								};
								/*win.do_action({
									type: 'ir.actions.act_window',
									res_model: "project.project",
									res_id: self.datos_ejes[i].id,
									views: [[false, 'tree']],
									target: '_blank',
									nodestroy:true,
								});*/
							}, this));
						}
					//}
				}
			};
			this.ds_project_configuration.read_slice(['id','name','active','red_start','red_end','yel_start','yel_end','blue_start','blue_end'], {domain: [['active', '=', true ]] }).then(function(result) {
				for(var i in result) {
					self.rango1_min = result[i].red_start;
					self.rango1_max = result[i].red_end;
					self.rango2_min = result[i].yel_start;
					self.rango2_max = result[i].yel_end;
					self.rango3_min = result[i].blue_start;
					self.rango3_max = result[i].blue_end;
				}
			});
        	this.ds_ejes.read_slice(['id','name','bsc_indicador1','bsc_indicador2'], 0).then(
        		function(result) {
        			self.datos_ejes = result;
	            	//$(".pruebas").append('ejes');
            	}
        	);
        	this.ds_estrategias.read_slice(['id','sequence','name','axis_id','bsc_indicador1','bsc_indicador2'], 0).then(function(result) {
            	self.datos_estrategias = result;
            	//$(".pruebas").append('resultados');
            	crear();
            });	
        },
    });
        
    //PLANTILLA Perspectiva
    db.gt_bsc.BscPerspectivas = db.web.OldWidget.extend({
    	template: 'bsc_perspectivas',
    	init: function() {
	    self = this;
            this._super.apply(this, arguments);
            //informacion de ejes
            this.ds_perspectivas = new db.web.DataSetSearch(this, 'bsc.perspectiva');
            this.datos_perspectivas = [];
            //informacion de configuracion
            this.ds_project_configuration = new db.web.DataSetSearch(this, 'project.configuration');
            this.rango1_min = 0;
            this.rango1_max = 0;
            this.rango2_min = 0;
            this.rango2_max = 0;
            this.rango3_min = 0;
            this.rango3_max = 0;
            this.color1 = "#F74447";
            this.color2 = "#F79A44";
            this.color3 = "#01DF3A";
            
        },
        start: function (){
        	self = this;
        	this.ds_project_configuration.read_slice(['id','name','active','red_start','red_end','yel_start','yel_end','blue_start','blue_end'], {domain: [['active', '=', true ]] }).then(function(result) {
        		for(var i in result) {
        			self.rango1_min = result[i].red_start;
		            self.rango1_max = result[i].red_end;
		            self.rango2_min = result[i].yel_start;
		            self.rango2_max = result[i].yel_end;
		            self.rango3_min = result[i].blue_start;
		            self.rango3_max = result[i].blue_end;
        		}
        	});
        	
        	var tabla_perspectivas = "<tr>";
        	function crear(){
				if (self.datos_perspectivas.length>0){
					var contador_perspectivas = 0;
					for(var i in self.datos_perspectivas) {
						contador_perspectivas = contador_perspectivas + 1;
						var indicador1 = parseFloat(self.datos_perspectivas[i].indicador1.toFixed(2));
	                    var indicador2 = parseFloat(self.datos_perspectivas[i].indicador2.toFixed(2));
	                    var color1 = "#FFFFFF";
	                    var color2 = "#FFFFFF";
	                    if ((indicador1>=self.rango1_min) && (indicador1<=self.rango1_max)) {
							color1=self.color1;
						}
						if ((indicador1>=self.rango2_min) && (indicador1<=self.rango2_max)) {
							color1=self.color2;
						}
						if ((indicador1>=self.rango3_min) && (indicador1<=self.rango3_max)) {
							color1=self.color3;
						}
						if ((indicador2>=self.rango1_min) && (indicador2<=self.rango1_max)) {
							color2=self.color1;
						}
						if ((indicador2>=self.rango2_min) && (indicador2<=self.rango2_max)) {
							color2=self.color2;
						}
						if ((indicador2>=self.rango3_min) && (indicador2<=self.rango3_max)) {
							color2=self.color3;
						}
	                    
						tabla_perspectivas = tabla_perspectivas + 
							"<td style='position:relative;width:30%;'>" + 
							"<div style='position:relative;width:90%;' class='borde_sombra fuente_pequena'><center><b>" + self.datos_perspectivas[i].name + "</b></center>" +
							
							'<br/><table width="100%"><tr><td width="20%">Eficacia:</td><td width="80%">' +
		                	'<div id="progress"><span id="percent" >' + indicador1 + '%</span><div id="bar" style="width:' + indicador1 + '%;background-color:' + color1 + ';"></div></div>' +
		                	'</td></tr><tr><td width="20%">Eficiencia:</td><td width="80%">' +
		                	'<div id="progress"><span id="percent" >' + indicador2 + '%</span><div id="bar" style="width:' + indicador2 + '%;background-color:' + color2 + ';"></div></div>' +
		                	'</td></tr></table>' +
							"</td>" + 
							"<td style='position:relative;width:20%;'>" + 
							"<div style='width:150px;height:175px;' id='promedio_" + self.datos_perspectivas[i].id + "'/>" + "</td>";
						if (contador_perspectivas%2==0){
							tabla_perspectivas = tabla_perspectivas + "</tr><tr>";
						}
					}
					tabla_perspectivas = tabla_perspectivas + "</tr>";
					$(".table_bsc_perspectivas").append(tabla_perspectivas);
					for(var i in self.datos_perspectivas) {
						var perspectiva_indicador1 = parseFloat(self.datos_perspectivas[i].indicador1.toFixed(2));
	                    var perspectiva_indicador2 = parseFloat(self.datos_perspectivas[i].indicador2.toFixed(2));
	                    var perspectiva_promedio = (perspectiva_indicador1+perspectiva_indicador2)/2;
	                    
			            var chart1 = new AmCharts.AmAngularGauge();
		                chart1.axes = [{
		                    startValue: 0,
		                    axisThickness: 1,
		                    endValue: 100,
		                    //bottomTextYOffset: -20,
		                    bottomText: perspectiva_promedio + "%\nTotal",
		                    bottomTextFontSize: 13,
		                    fontSize:8,
		                    bands: [{
		                            startValue: self.rango1_min,
		                            endValue: self.rango1_max,
		                            color: self.color1,
		                            innerRadius: "75%"
		                        },
		                        {
		                            startValue: self.rango2_min,
		                            endValue: self.rango2_max,
		                            color: self.color2,
		                            innerRadius: "75%"
		                        },
		                        {
		                            startValue: self.rango3_min,
		                            endValue: self.rango3_max,
		                            color: self.color3,
		                            innerRadius: "75%"
		                        }
		                    ]
		                }];
		                chart1.arrows = [{value:perspectiva_promedio}];
		                chart1.write("promedio_"+self.datos_perspectivas[i].id);
					}
				}
			};
        	this.ds_perspectivas.read_slice(['id','name','indicador1','indicador2'], 0).then(
            	function(result) {
	            	self.datos_perspectivas = result;
	            	crear();
            	}
            );
			
        },
    });
    
    //PLANTILLA PRINCIPAL
    db.gt_bsc.BscHome = db.web.OldWidget.extend({
    	template: 'bsc_main',
        init: function() {
            this._super.apply(this, arguments);
            //this.ds_formulacion = new db.web.DataSetSearch(this, 'bsc.formulation');
            //this.ds_objetivos = new db.web.DataSetSearch(this, 'bsc.objetive');
            //this.ds_pespectiva = new db.web.DataSetSearch(this, 'bsc.perspectiva');
        },
        start: function () {
           this.$element.find(".oe_bsc_menu_item a").click(_.bind(this.cambiar_opcion, this));
           
        },
        cambiar_opcion: function(a) {
            var id = $(a.target).data("category-id");
            $(".oe_bsc_homepage_right").empty();
            if (id === 1) { //============================== FORMULACION
            	var bsc_inicio = new db.gt_bsc.BscInicio(this);
          		bsc_inicio.appendTo($(".oe_bsc_homepage_right"));
          	};
            if (id === 2) { //============================== FORMULACION
            	var bsc_formulacion = new db.gt_bsc.BscFormulacion(this);
          		bsc_formulacion.appendTo($(".oe_bsc_homepage_right"));
          	};
          	if (id === 3) { //============================== EJES ESTRATEGICOS
          		var bsc_ejesestrategicos = new db.gt_bsc.BscEjesEstrategicos(this);
          		bsc_ejesestrategicos.appendTo($(".oe_bsc_homepage_right"));
          	};
          	if (id === 4) {  //============================== PERSPECTIVAS
          		var bsc_perspectivas = new db.gt_bsc.BscPerspectivas(this);
          		bsc_perspectivas.appendTo($(".oe_bsc_homepage_right"));
          	};
        },
    });
    
    db.web.client_actions.add('bsc.ui', 'db.gt_bsc.BscHome');
    
    db.web.client_actions.add('bsc.ui.inicio', 'db.gt_bsc.BscInicio');
    db.web.client_actions.add('bsc.ui.filosofia', 'db.gt_bsc.BscFormulacion');
    db.web.client_actions.add('bsc.ui.ejes', 'db.gt_bsc.BscEjesEstrategicos');
    db.web.client_actions.add('bsc.ui.perspectivas', 'db.gt_bsc.BscPerspectivas');
    
};