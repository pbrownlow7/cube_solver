//console.log("Here");

/*var req = new XMLHttpRequest();
req.open('GET', 'test.json');
req.onload = function() {
	console.log("here");
	console.log(req.responseText);
};*/

//var cubeIndex = 0;
/*var cols = [
	['G', 'G', 'B', 'R', 'W', 'W', 'G', 'B', 'R', 'O', 'O', 'R', 'G', 'G', 'R', 'O', 'O', 'W', 'W', 'B', 'R', 'Y', 'Y', 'Y', 'Y', 'O', 'G', 'B', 'W', 'Y', 'W', 'G', 'Y', 'R', 'G', 'Y', 'O', 'O', 'B', 'R', 'Y', 'B', 'B', 'B', 'O', 'W', 'Y', 'R', 'G', 'O', 'R', 'W', 'W', 'B'],
	['Y', 'W', 'G', 'R', 'W', 'W', 'G', 'B', 'R', 'B', 'O', 'R', 'G', 'G', 'R', 'G', 'G', 'W', 'W', 'B', 'R', 'Y', 'Y', 'Y', 'Y', 'O', 'G', 'B', 'W', 'Y', 'B', 'B', 'Y', 'R', 'G', 'Y', 'O', 'O', 'B', 'R', 'O', 'O', 'O', 'B', 'O', 'W', 'Y', 'R', 'G', 'O', 'R', 'W', 'W', 'B']	
]*/
var propMapping = {0:0, 1:1, 2:2, 3:7, 4:8, 5:3, 6:6, 7:5, 8:4};
var colours = {"R":"#cf0a00", "W":"#ffffff", "G":"#019e1b", "Y":"#ffec1c", "O":"#ff4800", "B":"#022f59"};
var coloursList = ["#cf0a00", "#ffffff", "#019e1b", "#ffec1c", "#ff4800", "#022f59"];

var globScramble = [];
var snapshots = [];
var snapsIndex = 0;

function start() {
	if(window.XMLHttpRequest) {
		var xmlhttp = new XMLHttpRequest();
		console.log("created");
		xmlhttp.open("GET", "test.json", true);
		console.log("succeeded");
		xmlhttp.onreadystatechange = function() {
			console.log("here now");
			if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
				$("#h").html(xmlhttp.responseText);
			} else {
				console.log("here instead");
			}
			//console.log(xmlhttp.responseText);
		}
		console.log("Passed");
	} else {
		var xmlhttp = false;
		console.log("Failed");
	}
}

$(document).ready(function() {

	//var cols = ['G', 'G', 'B', 'R', 'W', 'W', 'G', 'B', 'R', 'O', 'O', 'R', 'G', 'G', 'R', 'O', 'O', 'W', 'W', 'B', 'R', 'Y', 'Y', 'Y', 'Y', 'O', 'G', 'B', 'W', 'Y', 'W', 'G', 'Y', 'R', 'G', 'Y', 'O', 'O', 'B', 'R', 'Y', 'B', 'B', 'B', 'O', 'W', 'Y', 'R', 'G', 'O', 'R', 'W', 'W', 'B'];
	//var niceScramble = "R D B D2 R D' U' F' U D L' D' F' R F R' U' B' R D' F B R2 L F' R' D";
	//var propMapping = {0:0, 1:1, 2:2, 3:7, 4:8, 5:3, 6:6, 7:5, 8:4}
	var faces = [];
	//var colours = {"R":"#cf0a00", "W":"#ffffff", "G":"#019e1b", "Y":"#ffec1c", "O":"#ff4800", "B":"#022f59"};
	//var colours = ["#cf0a00", "#ffffff", "#019e1b", "#ffec1c", "#ff4800", "#022f59"];
	var squarePos = {0:"topLeft", 1:"topMiddle", 2:"topRight", 3:"middleLeft", 4:"middleMiddle", 5:"middleRight", 6:"bottomLeft", 7:"bottomMiddle", 8:"bottomRight"};
	
	index = 0;
	for(var i = 0; i < 6; i++) {
		faces.push([]);
		fid = i.toString();
		$("#cubeHolder").append("<div class='face' id="+fid+"></div>");
		ftv = (Math.floor((i/3))*312)+(Math.floor((i/3))*4);
		ft = (ftv).toString()+"px";

		flv = ((i%3)*312)+((i%3)*4);
		fl = (flv).toString()+"px";

		$("#"+fid).css({
			"top": ft,
			"left": fl
		});

		for(var j = 0; j < 9; j ++) {
			sid = i.toString()+j.toString();
			$("#"+fid).append("<div class='square' id="+sid+"></div>");
			faces[i].push(sid);

			//console.log(Math.floor(j/3));
			tv = (Math.floor((j/3))*100)+(Math.floor((j/3))*4);
			t = (tv).toString()+"px";

			lv = ((j%3)*100)+((j%3)*4);
			l = (lv).toString()+"px";

			faceIndex = (Math.floor(index/9)) * 9;
			mapIndex = index-faceIndex;
			//colIndex = faceIndex + propMapping[mapIndex];
			//console.log(i);
			b = coloursList[Math.floor(index/9)];
			c = squarePos[mapIndex];

			$("#"+sid).css({
				"background-color": b,
				"top": t,
				"left": l
			});
			$("#"+sid).addClass(c);
			index++;
		}
	}

	$("#solve").toggleClass("normalButton");	
	
	$("#generate").click(function() {
		//$("#scramble").html("Generating...");
		generateScramble();
	});

	$("#solve").click(function() {
		solveScramble();
	});

	$("#stats").click(function() {
		showStats();
	});
});

function updateCube(cols) {
	//console.log("JJ");
	//console.log(cols);
	//var cols = ['G', 'G', 'B', 'R', 'W', 'W', 'G', 'B', 'R', 'O', 'O', 'R', 'G', 'G', 'R', 'O', 'O', 'W', 'W', 'B', 'R', 'Y', 'Y', 'Y', 'Y', 'O', 'G', 'B', 'W', 'Y', 'W', 'G', 'Y', 'R', 'G', 'Y', 'O', 'O', 'B', 'R', 'Y', 'B', 'B', 'B', 'O', 'W', 'Y', 'R', 'G', 'O', 'R', 'W', 'W', 'B'];
	//var propMapping = {0:0, 1:1, 2:2, 3:7, 4:8, 5:3, 6:6, 7:5, 8:4}
	//var colours = {"R":"#cf0a00", "W":"#ffffff", "G":"#019e1b", "Y":"#ffec1c", "O":"#ff4800", "B":"#022f59"};

	for(var i = 0; i < 6; i++) {
		for(var j = 0; j < 9; j ++) {
			sid = i.toString()+j.toString();
			$("#"+sid).fadeOut(300);
			//b = colours[Math.floor(Math.random() * 6)];
			//console.log(Math.floor(Math.random() * 6));
			//console.log(b);
			//$("#"+sid).css("background-color", b);
		}
	}
	
	setTimeout(function() {
		index = 0;
		for(var i = 0; i < 6; i++) {
			for(var j = 0; j < 9; j ++) {
				faceIndex = (Math.floor(index/9)) * 9;
				mapIndex = index-faceIndex;
				colIndex = faceIndex + propMapping[mapIndex];
				//console.log(cols[colIndex]);
				sid = i.toString()+j.toString();
				//console.log(cols[cubeIndex][colIndex]);
				//b = colours[cols[cubeIndex][colIndex]];
				b = colours[cols[colIndex]];
				

				$("#"+sid).css({
					"background-color": b,
					//"top": t,
					//"left": l
				});
				$("#"+sid).fadeIn(300);
				index++;
			}
		}
		//cubeIndex++;
	}, 500);
}

function generateScramble() {
	//console.log("Generate");
	$("#scramble").html("Generating...").hide().fadeIn(500);
	setTimeout(function(){
		//var cols = []
		$.ajax({
			url: "http://127.0.0.1:5000",
			success: function(response) {
				//console.log(response.scramble);
				$("#scramble").html(response.nice_sc);
				$("#solveHolder").empty();
				//cols = response.scramble;
				if($("#solve").hasClass("disabledButton")) {
					enableSolve();
				}
				globScramble = response.sc;
				globSnap = response.cube_snap;
				updateCube(response.cube_snap);
			},
			
		});
	}, 1000);
}

function solveScramble() {
	//console.log(globScramble);
	var objMap = {scramble: globScramble};
	$.ajax({
		type: "POST",
		url: "http://127.0.0.1:5000/solve",
		data: JSON.stringify(objMap),
		contentType: "application/json",
		success: function(solveResponse) {
			//console.log(solveResponse.snaps);
			for(var i=0; i < solveResponse.mov.length; i++) {
				var obj = solveResponse.mov[i];
				$("#solveHolder").append("<p class='solveText' id="+i+">"+obj+"</p>");
			}
			//console.log(solveResponse);
			snapshots = solveResponse.snaps;
			snapsIndex = 0;
			//console.log(snapshots);
			disableSolve();
			updateProxy();
		}
	});

	/*setTimeout(function(){
		updateProxy();
	}, 500);*/
	/*setTimeout(function() {
		updateCube(globSnap);
		//console.log("Solving animation");
	}, 2000);*/
}

function updateProxy() {
	if(snapsIndex < snapshots.length) {
		setTimeout(function() {
			updateCube(snapshots[snapsIndex]);
			snapsIndex++;
			updateProxy();
		}, 1000);
	}
}

function showStats() {
	console.log("Stats");
}

function enableSolve() {
	$("#solve").prop("disabled", false);
	$("#solve").toggleClass("disabledButton normalButton");
}

function disableSolve() {
	$("#solve").prop("disabled", true);
	$("#solve").toggleClass("disabledButton normalButton");
}


