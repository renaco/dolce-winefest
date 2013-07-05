var dolcePapa = (function($){
	"use strict";
	var timerPanel = 10,
		contPastilla = $(".cont_pastillas"),
		t,
		contador = 0,
		itemSelected = new Array(),
		itemSelectedTemp = new Array(),
		idRandom = new Array(),
		idRandomTemp = new Array(),
		myTime 
		
	function init(){}
	
	
	function panelTime(idPanel){	
		var idPanel = idPanel;
		var nextPanel = idPanel.next();			
		var timer = idPanel.find(".timer .magenta");	
		idRandomTemp = idPanel.attr("data-id");			
		countPanel(1);
		clickPanelItem(idPanel);
		activarTiempo(timerPanel, timer, function(complete){
				idPanel.find("ul li").unbind('click');
				changePanel(idPanel, nextPanel, itemSelectedTemp, idRandomTemp);
			
			}
		);
	}
	function limpiarTiempo(){
		clearTimeout(t);
	}	
	function activarTiempo(n, idTimer, oncomplete){
		var $idTimer = $(idTimer);
		var $idTimerCanvas = $(idTimer).parent().find(".timerCircle").attr("id");
	
		var action; 
		var ncat = n.toString();
		
		myTime = new Timer($idTimerCanvas, ncat + "000", 50, function() { }, "#fff", "#2DDCCE");
		myTime.start();
		
		function countDown(){
			n--;
			
			if(n > 0){
				t = window.setTimeout(countDown,1000);
				if (ncat.length == 1){
				  $idTimer.text("0" + n);
				}else{
					$idTimer.text(n);
				}
			}else{
				$idTimer.text("0" + 0);
				oncomplete(action);				
			}	  
		}
		t = window.setTimeout(countDown,1000);	
	}
	function countPanel(step){
		var num;
		var contadorText = $("#contador .num");
		contador = contador + step;
		contadorText.text(contador);
	}
	function changePanel(id, next, items, ramdom){	
		var items = getItemSelection();
		var ramdom = getRamdomSelection();
		var idPhoto = id.attr("id");
		if(id.hasClass("last")){
			envioParametros(items, ramdom);			
		}else{
			var idP = $("#" + idPhoto + "-img");			
			idP.fadeOut(function(){	});				
			id.fadeOut(function(){			
				next.fadeIn();			
				panelTime(next);				
			});			
		}	
	}
	function envioParametros(items, idRandom){		

		var $form = $("#form_game");		
		var idItems = items;
		var idRandom = idRandom;
		
		var res =  idRandom[0] + ":" + idItems[0] + "," + idRandom[1] + ":" + idItems[1] + "," + idRandom[2] + ":" + idItems[2];
		
		$("#resp").val(res);	
		_gaq.push(['_trackEvent','Diapadre-Conversion', 'Paso-Final', '']);
		$form.submit();
		
	}
	function clickPanelItem(idPanel){
		var ids = idPanel.find("ul li");
		var numClick = idPanel.attr("data-num");
		idRandomTemp = idPanel.attr("data-id");
		var nextPanel = idPanel.next();	
		var countClick = 0;	
		
		ids.each(function(index, id){
			var id = $(id);			
			id.bind('click', function(e){
				e.preventDefault();
				countClick++;
				itemSelectedTemp.push(id.find("a").attr("id"));				
				if(countClick == numClick){
					id.addClass("selected");					
					ids.unbind('click');
					changePanel(idPanel, nextPanel, itemSelectedTemp, idRandomTemp);
					limpiarTiempo();
					myTime.stop();
					
				}else{
					$(this).unbind('click');
					id.addClass("selected");
				}							
			});
		});	
		
	}
	function getItemSelection(){	
		var itemSelectedTempJoin = itemSelectedTemp.join("-");		
		itemSelected.push(itemSelectedTempJoin);		
		itemSelectedTemp =  [];
		return itemSelected;
	}
	function getRamdomSelection(){	
		var ramdomSelectedTempJoin = idRandomTemp;		
		idRandom.push(ramdomSelectedTempJoin);		
		idRandomTemp =  [];
		return idRandom;
	}
	
	function countContPastillas(){	
		var $contPastillas = $('.cont_pastillas');
		if ($contPastillas.length == 0){
		  return;
		}else{
			return $contPastillas.length;	
		}		 
	}
	
	return {
		init: init,
		panelTime: panelTime,
		changePanel: changePanel,
		getItemSelection: getItemSelection,
		countContPastillas: countContPastillas,
		countPanel: countPanel,
		clickPanelItem: clickPanelItem,
		_: ''
	};
	
	
}(jQuery));


