$(document).ready(function() {
	d_points = []
	pll_d_points = []
	
	var oll_stats;
	var pll_stats;
	$.getJSON("stats.json", function(json) {
		oll_stats = json
		//console.log("blah");
		//console.log(Object.keys(oll_stats).length);
	});

	$.getJSON("pll_stats.json", function(json) {
		pll_stats = json
		//console.log("blah");
		//console.log(Object.keys(oll_stats).length);
	});

	$("#canvas").css({
		"width": 300,
		"height": 300,
		"background-color": "black"
	});

	/*setTimeout(function() {
		//console.log(oll_stats);
		var keys = Object.keys(oll_stats);
		for(var i = 0; i < keys.length; i++) {
			//console.log("Cmere now");
			//console.log(key);
			if(keys[i] != "total") {
				var dict = {};
				dict.label = keys[i];
				dict.y = oll_stats[keys[i]];
				d_points.push(dict);
			}
		}

		var keys = Object.keys(pll_stats);
		for(var i = 0; i < keys.length; i++) {
			//console.log("Cmere now");
			//console.log(key);
			if (keys[i] != "total") {
				var dict = {};
				dict.label = keys[i];
				dict.y = pll_stats[keys[i]];
				pll_d_points.push(dict);
			}
		}
	
		var chart = new CanvasJS.Chart("chartContainer", {
			animationEnabled: true,
			title:{
				text: "Frequency of OLL Algorithms (Over " + oll_stats["total"] + ")"              
			},
			data: [              
				{
					mouseover: function(e) {
						console.log(document.getElementById("hideme").value);
						//console.log("here");
					},
					//toolTipContent: {
					//	enabled: false,
					//},
					type: "column",
					dataPoints: d_points
				}
			]
		});

		var chart2 = new CanvasJS.Chart("pllContainer", {
			animationEnabled: true,
			title:{
				text: "Frequency of PLL Algorithms (Over " + pll_stats["total"] + ")"              
			},
			data: [              
				{
					type: "column",
					dataPoints: pll_d_points
				}
			]
		});
		chart.render();
		chart2.render();
	}, 200);*/
});
