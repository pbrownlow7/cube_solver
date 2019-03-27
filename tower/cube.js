var globScramble = [];

$(document).ready(function() {
	/*var faces = [];
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
	}*/

	$("#solve").toggleClass("normalButton");
	$("#generate").toggleClass("disabledButton");
	$("#generate").prop("disabled", false);
	
	$("#generate").click(function() {
		generateScramble();
	});

	$("#solve").click(function() {
		solveScramble();
	});

	$("#stats").click(function() {
		showStats();
	});
});

/*function updateCube(cols) {
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
}*/

function generateScramble() {
	$("#scramble").html("Generating...").hide().fadeIn(500);
	disableGenerate();
	setTimeout(function(){
		$.ajax({
			url: "http://127.0.0.1:5000",
			success: function(response) {
				$("#scramble").html(response.nice_sc);
				$("#solveHolder").empty();
				globScramble = response.usable_sc;
				scrambleCube(globScramble, 0);
			},
			
		});
	}, 1000);
}

function solveScramble() {
	var objMap = {scramble: globScramble};
	$.ajax({
		type: "POST",
		url: "http://127.0.0.1:5000/solve",
		data: JSON.stringify(objMap),
		contentType: "application/json",
		success: function(solveResponse) {
			for(var i=0; i < solveResponse.mov.length; i++) {
				var obj = solveResponse.mov[i];
				if(i == (solveResponse.mov.length)-1) {
					$("#solveHolder").append("<p class='solveText' id='time'>Time Taken:</p>");
					$("#solveHolder").append("<p class='solveText' id="+i+">"+obj+" seconds</p>");
				} else {
					$("#solveHolder").append("<p class='solveText' id="+i+">"+obj+"</p>");
				}
			}
			moves_list = solveResponse.moves_list;
			disableSolve();
			solveCube(moves_list, 0);
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

/*function updateProxy() {
	if(snapsIndex < snapshots.length) {
		setTimeout(function() {
			updateCube(snapshots[snapsIndex]);
			snapsIndex++;
			updateProxy();
		}, 1000);
	}
}*/

function showStats() {
	$("body").load("stats.html");
	//alert("Rendering graphs");
}

function enableSolve() {
	$("#solve").prop("disabled", false);
	$("#solve").toggleClass("disabledButton normalButton");
}

function disableSolve() {
	$("#solve").prop("disabled", true);
	$("#solve").toggleClass("disabledButton normalButton");
}

function enableGenerate() {
	$("#generate").prop("disabled", false);
	$("#generate").toggleClass("disabledButton normalButton");
}

function disableGenerate() {
	$("#generate").prop("disabled", true);
	$("#generate").toggleClass("disabledButton normalButton");
}

function scrambleCube(scramble, sIndex) {
	if(sIndex < scramble.length) {
		setTimeout(function() {
			switch(scramble[sIndex]) {
				case "R":
					rotateRight();
					break;
				case "R'":
					rotateRightPrime();
					break;
				case "L":
					rotateLeft();
					break;
				case "L'":
					rotateLeftPrime();
					break;
				case "U":
					rotateUp();
					break;
				case "U'":
					rotateUpPrime();
					break;
				case "D":
					rotateDown();
					break;
				case "D'":
					rotateDownPrime();
					break;
				case "F":
					rotateFront();
					break;
				case "F'":
					rotateFrontPrime();
					break;
				case "B":
					rotateBack();
					break;
				case "B'":
					rotateBackPrime();
					break;
				case "M":
					rotateMiddle();
					break;
				case "M'":
					rotateMiddlePrime();
					break;
				case "r":
					rotateRightWide();
					break;
				case "r'":
					rotateRightWidePrime();
					break;
				case "l":
					rotateLeftWide();
					break;
				case "l'":
					rotateLeftWidePrime();
					break;
				case "u":
					rotateUpWide();
					break;
				case "u'":
					rotateUpWidePrime();
					break;
				case "d":
					rotateDownWide();
					break;
				case "d'":
					rotateDownWidePrime();
					break;
				case "f":
					rotateFrontWide();
					break;
				case "f'":
					rotateFrontWidePrime();
					break;
				case "b":
					rotateBackWide();
					break;
				case "b'":
					rotateBackWidePrime();
					break;
				case "x":
					rotateX();
					break;
				case "x'":
					rotateXPrime();
					break;
				case "y":
					rotateY();
					break;
				case "y'":
					rotateYPrime();
					break;
				case "z":
					rotateZ();
					break;
				case "z'":
					rotateZPrime();
					break;
			}
			sIndex++;
			scrambleCube(scramble, sIndex);
		}, 200);
	} else {
		if($("#solve").hasClass("disabledButton")) {
			enableSolve();
		}
	}
}

function solveCube(moves_list, solveIndex) {
	if(solveIndex < moves_list.length) {
		setTimeout(function() {
			switch(moves_list[solveIndex]) {
				case "R":
					rotateRight();
					break;
				case "R'":
					rotateRightPrime();
					break;
				case "L":
					rotateLeft();
					break;
				case "L'":
					rotateLeftPrime();
					break;
				case "U":
					rotateUp();
					break;
				case "U'":
					rotateUpPrime();
					break;
				case "D":
					rotateDown();
					break;
				case "D'":
					rotateDownPrime();
					break;
				case "F":
					rotateFront();
					break;
				case "F'":
					rotateFrontPrime();
					break;
				case "B":
					rotateBack();
					break;
				case "B'":
					rotateBackPrime();
					break;
				case "M":
					rotateMiddle();
					break;
				case "M'":
					rotateMiddlePrime();
					break;
				case "r":
					rotateRightWide();
					break;
				case "r'":
					rotateRightWidePrime();
					break;
				case "l":
					rotateLeftWide();
					break;
				case "l'":
					rotateLeftWidePrime();
					break;
				case "u":
					rotateUpWide();
					break;
				case "u'":
					rotateUpWidePrime();
					break;
				case "d":
					rotateDownWide();
					break;
				case "d'":
					rotateDownWidePrime();
					break;
				case "f":
					rotateFrontWide();
					break;
				case "f'":
					rotateFrontWidePrime();
					break;
				case "b":
					rotateBackWide();
					break;
				case "b'":
					rotateBackWidePrime();
					break;
				case "x":
					rotateX();
					break;
				case "x'":
					rotateXPrime();
					break;
				case "y":
					rotateY();
					break;
				case "y'":
					rotateYPrime();
					break;
				case "z":
					rotateZ();
					break;
				case "z'":
					rotateZPrime();
					break;
			}
			solveIndex++;
			solveCube(moves_list, solveIndex);
		}, 300);
	} else {
		enableGenerate();
	}
}

function rotateUpPrime() {
	side_values = getUpSideColours();
	face_colours = getUpFaceColours();
	upPrimeRotation(side_colours, face_colours);
}

function rotateUp() {
	side_colours = getUpSideColours();
	face_colours = getUpFaceColours();
	upRotation(side_colours, face_colours);
}

function rotateDown() {
	side_colours = getDownSideColours();
	face_colours = getDownFaceColours();
	downRotation(side_colours, face_colours);
}

function rotateDownPrime() {
	side_colours = getDownSideColours();
	face_colours = getDownFaceColours();
	downPrimeRotation(side_colours, face_colours);
}

function rotateFrontPrime() {
	side_colours = getFrontSideColours();
	face_colours = getFrontFaceColours();
	frontPrimeRotation(side_colours, face_colours);
}

function rotateFront() {
	side_colours = getFrontSideColours();
	face_colours = getFrontFaceColours();
	frontRotation(side_colours, face_colours);
}

function rotateBack() {
	side_colours = getBackSideColours();
	face_colours = getBackFaceColours();
	backRotation(side_colours, face_colours);
}

function rotateBackPrime() {
	side_colours = getBackSideColours();
	face_colours = getBackFaceColours();
	backPrimeRotation(side_colours, face_colours);
}

function rotateRightPrime() {
	side_colours = getRightSideColours();
	face_colours = getRightFaceColours();
	rightPrimeRotation(side_colours, face_colours);
}

function rotateRight() {
	side_colours = getRightSideColours();
	face_colours = getRightFaceColours();
	rightRotation(side_colours, face_colours);
}

function rotateLeft() {
	side_colours = getLeftSideColours();
	face_colours = getLeftFaceColours();
	leftRotation(side_colours, face_colours);
}

function rotateLeftPrime() {
	side_colours = getLeftSideColours();
	face_colours = getLeftFaceColours();
	leftPrimeRotation(side_colours, face_colours);
}

function rotateMiddle() {
	colours = getMiddleColours();
	middleRotation(colours);
}

function rotateMiddlePrime() {
	colours = getMiddleColours();
	middlePrimeRotation(colours);
}

function rotateMiddleY() {
	colours = getMiddleYColours();
	middleYRotation(colours);
}

function rotateMiddleYPrime() {
	colours = getMiddleYColours();
	middleYPrimeRotation(colours);
}

function rotateMiddleZ() {
	colours = getMiddleZColours();
	middleZRotation(colours);
}

function rotateMiddleZPrime() {
	colours = getMiddleZColours();
	middleZPrimeRotation(colours);
}

function rotateUpWide() {
	rotateUp();
	rotateMiddleYPrime();
}

function rotateUpWidePrime() {
	rotateUpPrime();
	rotateMiddleY();
}

function rotateDownWide() {
	rotateDown();
	rotateMiddleY();
}

function rotateDownWidePrime() {
	rotateDownPrime();
	rotateMiddleYPrime();
}

function rotateRightWide() {
	rotateRight();
	rotateMiddlePrime();
}

function rotateRightWidePrime() {
	rotateRightPrime();
	rotateMiddle();
}

function rotateLeftWide() {
	rotateLeft();
	rotateMiddle();
}

function rotateLeftWidePrime() {
	rotateLeftPrime();
	rotateMiddlePrime();
}

function rotateFrontWide() {
	rotateFront();
	rotateMiddleZ();
}

function rotateFrontWidePrime() {
	rotateFrontPrime();
	rotateMiddleZPrime();
}

function rotateBackWide() {
	rotateBack();
	rotateMiddleZPrime();
}

function rotateBackWidePrime() {
	rotateBackPrime();
	rotateMiddleZ();
}

function rotateX() {
	rotateLeftWidePrime();
	rotateRight();
}

function rotateXPrime() {
	rotateLeftWide();
	rotateRightPrime();
}

function rotateY() {
	rotateUpWide();
	rotateDownPrime();
}

function rotateYPrime() {
	rotateUpWidePrime();
	rotateDown();
}

function rotateZ() {
	rotateFrontWide();
	rotateBackPrime();
}

function rotateZPrime() {
	rotateFrontWidePrime();
	rotateBack();
}

function getUpSideColours() {
	side_colours = [
		$("#layer1 #front #one").css("background-color"),
		$("#layer1 #front #two").css("background-color"),
		$("#layer1 #front #three").css("background-color"),
		$("#layer1 #right #one").css("background-color"),
		$("#layer1 #right #two").css("background-color"),
		$("#layer1 #right #three").css("background-color"),
		$("#layer1 #back #one").css("background-color"),
		$("#layer1 #back #two").css("background-color"),
		$("#layer1 #back #three").css("background-color"),
		$("#layer1 #left #one").css("background-color"),
		$("#layer1 #left #two").css("background-color"),
		$("#layer1 #left #three").css("background-color")
	];

	return side_colours;
}

function getUpFaceColours() {
	face_colours = [
		$("#layer1 #top1 #one").css("background-color"),
		$("#layer1 #top1 #two").css("background-color"),
		$("#layer1 #top1 #three").css("background-color"),
		$("#layer1 #top2 #one").css("background-color"),
		$("#layer1 #top2 #three").css("background-color"),
		$("#layer1 #top3 #one").css("background-color"),
		$("#layer1 #top3 #two").css("background-color"),
		$("#layer1 #top3 #three").css("background-color")
	];

	return face_colours;
}

function upPrimeRotation(side_colours, face_colours) {
	$("#layer1 #front #one").css("background-color", side_colours[11]);
	$("#layer1 #front #two").css("background-color", side_colours[10]);
	$("#layer1 #front #three").css("background-color", side_colours[9]);
	$("#layer1 #right #one").css("background-color", side_colours[0]);
	$("#layer1 #right #two").css("background-color", side_colours[1]);
	$("#layer1 #right #three").css("background-color", side_colours[2]);
	$("#layer1 #back #three").css("background-color", side_colours[3]);
	$("#layer1 #back #two").css("background-color", side_colours[4]);
	$("#layer1 #back #one").css("background-color", side_colours[5]);
	$("#layer1 #left #one").css("background-color", side_colours[6]);
	$("#layer1 #left #two").css("background-color", side_colours[7]);
	$("#layer1 #left #three").css("background-color", side_colours[8]);

	$("#layer1 #top1 #one").css("background-color", face_colours[5]);
	$("#layer1 #top1 #two").css("background-color", face_colours[3]);
	$("#layer1 #top1 #three").css("background-color", face_colours[0]);
	$("#layer1 #top2 #one").css("background-color", face_colours[6]);
	$("#layer1 #top2 #three").css("background-color", face_colours[1]);
	$("#layer1 #top3 #one").css("background-color", face_colours[7]);
	$("#layer1 #top3 #two").css("background-color", face_colours[4]);
	$("#layer1 #top3 #three").css("background-color", face_colours[2]);
}

function upRotation(side_colours, face_colours) {
	$("#layer1 #front #one").css("background-color", side_colours[3]);
	$("#layer1 #front #two").css("background-color", side_colours[4]);
	$("#layer1 #front #three").css("background-color", side_colours[5]);
	$("#layer1 #right #one").css("background-color", side_colours[8]);
	$("#layer1 #right #two").css("background-color", side_colours[7]);
	$("#layer1 #right #three").css("background-color", side_colours[6]);
	$("#layer1 #back #three").css("background-color", side_colours[11]);
	$("#layer1 #back #two").css("background-color", side_colours[10]);
	$("#layer1 #back #one").css("background-color", side_colours[9]);
	$("#layer1 #left #one").css("background-color", side_colours[2]);
	$("#layer1 #left #two").css("background-color", side_colours[1]);
	$("#layer1 #left #three").css("background-color", side_colours[0]);

	$("#layer1 #top1 #one").css("background-color", face_colours[2]);
	$("#layer1 #top1 #two").css("background-color", face_colours[4]);
	$("#layer1 #top1 #three").css("background-color", face_colours[7]);
	$("#layer1 #top2 #one").css("background-color", face_colours[1]);
	$("#layer1 #top2 #three").css("background-color", face_colours[6]);
	$("#layer1 #top3 #one").css("background-color", face_colours[0]);
	$("#layer1 #top3 #two").css("background-color", face_colours[3]);
	$("#layer1 #top3 #three").css("background-color", face_colours[5]);
}

function getDownSideColours() {
	side_colours = [
		$("#layer3 #front #one").css("background-color"),
		$("#layer3 #front #two").css("background-color"),
		$("#layer3 #front #three").css("background-color"),
		$("#layer3 #right #one").css("background-color"),
		$("#layer3 #right #two").css("background-color"),
		$("#layer3 #right #three").css("background-color"),
		$("#layer3 #back #one").css("background-color"),
		$("#layer3 #back #two").css("background-color"),
		$("#layer3 #back #three").css("background-color"),
		$("#layer3 #left #one").css("background-color"),
		$("#layer3 #left #two").css("background-color"),
		$("#layer3 #left #three").css("background-color")
	];

	return side_colours;
}

function getDownFaceColours() {

	bottom_colours = [
		$("#layer3 #bottom1 #one").css("background-color"),
		$("#layer3 #bottom1 #two").css("background-color"),
		$("#layer3 #bottom1 #three").css("background-color"),
		$("#layer3 #bottom2 #one").css("background-color"),
		$("#layer3 #bottom2 #three").css("background-color"),
		$("#layer3 #bottom3 #one").css("background-color"),
		$("#layer3 #bottom3 #two").css("background-color"),
		$("#layer3 #bottom3 #three").css("background-color")
	];
	
	return bottom_colours;
}

function downRotation(side_colours, face_colours) {
	$("#layer3 #front #one").css("background-color", side_colours[11]);
	$("#layer3 #front #two").css("background-color", side_colours[10]);
	$("#layer3 #front #three").css("background-color", side_colours[9]);
	$("#layer3 #right #one").css("background-color", side_colours[0]);
	$("#layer3 #right #two").css("background-color", side_colours[1]);
	$("#layer3 #right #three").css("background-color", side_colours[2]);
	$("#layer3 #back #one").css("background-color", side_colours[5]);
	$("#layer3 #back #two").css("background-color", side_colours[4]);
	$("#layer3 #back #three").css("background-color", side_colours[3]);
	$("#layer3 #left #one").css("background-color", side_colours[6]);
	$("#layer3 #left #two").css("background-color", side_colours[7]);
	$("#layer3 #left #three").css("background-color", side_colours[8]);

	$("#layer3 #bottom1 #one").css("background-color", face_colours[5]);
	$("#layer3 #bottom1 #two").css("background-color", face_colours[3]);
	$("#layer3 #bottom1 #three").css("background-color", face_colours[0]);
	$("#layer3 #bottom2 #one").css("background-color", face_colours[6]);
	$("#layer3 #bottom2 #three").css("background-color", face_colours[1]);
	$("#layer3 #bottom3 #one").css("background-color", face_colours[7]);
	$("#layer3 #bottom3 #two").css("background-color", face_colours[4]);
	$("#layer3 #bottom3 #three").css("background-color", face_colours[2]);
}

function downPrimeRotation(side_colours, face_colours) {
	$("#layer3 #front #one").css("background-color", side_colours[3]);
	$("#layer3 #front #two").css("background-color", side_colours[4]);
	$("#layer3 #front #three").css("background-color", side_colours[5]);
	$("#layer3 #right #one").css("background-color", side_colours[8]);
	$("#layer3 #right #two").css("background-color", side_colours[7]);
	$("#layer3 #right #three").css("background-color", side_colours[6]);
	$("#layer3 #back #one").css("background-color", side_colours[9]);
	$("#layer3 #back #two").css("background-color", side_colours[10]);
	$("#layer3 #back #three").css("background-color", side_colours[11]);
	$("#layer3 #left #one").css("background-color", side_colours[2]);
	$("#layer3 #left #two").css("background-color", side_colours[1]);
	$("#layer3 #left #three").css("background-color", side_colours[0]);

	$("#layer3 #bottom1 #one").css("background-color", face_colours[2]);
	$("#layer3 #bottom1 #two").css("background-color", face_colours[4]);
	$("#layer3 #bottom1 #three").css("background-color", face_colours[7]);
	$("#layer3 #bottom2 #one").css("background-color", face_colours[1]);
	$("#layer3 #bottom2 #three").css("background-color", face_colours[6]);
	$("#layer3 #bottom3 #one").css("background-color", face_colours[0]);
	$("#layer3 #bottom3 #two").css("background-color", face_colours[3]);
	$("#layer3 #bottom3 #three").css("background-color", face_colours[5]);
}

function getFrontSideColours() {
	side_colours = [
		$("#layer1 #top1 #one").css("background-color"),
		$("#layer1 #top1 #two").css("background-color"),
		$("#layer1 #top1 #three").css("background-color"),
		$("#layer1 #left #one").css("background-color"),
		$("#layer2 #left #one").css("background-color"),
		$("#layer3 #left #one").css("background-color"),
		$("#layer3 #bottom1 #one").css("background-color"),
		$("#layer3 #bottom1 #two").css("background-color"),
		$("#layer3 #bottom1 #three").css("background-color"),
		$("#layer1 #right #one").css("background-color"),
		$("#layer2 #right #one").css("background-color"),
		$("#layer3 #right #one").css("background-color")
	];

	return side_colours;
}

function getFrontFaceColours() {

	front_colours = [
		$("#layer1 #front #one").css("background-color"),
		$("#layer1 #front #two").css("background-color"),
		$("#layer1 #front #three").css("background-color"),
		$("#layer2 #front #one").css("background-color"),
		$("#layer2 #front #three").css("background-color"),
		$("#layer3 #front #one").css("background-color"),
		$("#layer3 #front #two").css("background-color"),
		$("#layer3 #front #three").css("background-color")
	];		

	return front_colours;
}

function frontPrimeRotation(side_colours, face_colours) {
	$("#layer1 #top1 #one").css("background-color", side_colours[9]);
	$("#layer1 #top1 #two").css("background-color", side_colours[10]);
	$("#layer1 #top1 #three").css("background-color", side_colours[11]);
	$("#layer1 #left #one").css("background-color", side_colours[2]);
	$("#layer2 #left #one").css("background-color", side_colours[1]);
	$("#layer3 #left #one").css("background-color", side_colours[0]);
	$("#layer3 #bottom1 #one").css("background-color", side_colours[3]);
	$("#layer3 #bottom1 #two").css("background-color", side_colours[4]);
	$("#layer3 #bottom1 #three").css("background-color", side_colours[5]);
	$("#layer1 #right #one").css("background-color", side_colours[8]);
	$("#layer2 #right #one").css("background-color", side_colours[7]);
	$("#layer3 #right #one").css("background-color", side_colours[6]);

	$("#layer1 #front #one").css("background-color", face_colours[2]);
	$("#layer1 #front #two").css("background-color", face_colours[4]);
	$("#layer1 #front #three").css("background-color", face_colours[7]);
	$("#layer2 #front #one").css("background-color", face_colours[1]);
	$("#layer2 #front #three").css("background-color", face_colours[6]);
	$("#layer3 #front #one").css("background-color", face_colours[0]);
	$("#layer3 #front #two").css("background-color", face_colours[3]);
	$("#layer3 #front #three").css("background-color", face_colours[5]);
}

function frontRotation(side_colours, face_colours) {
	$("#layer1 #top1 #one").css("background-color", side_colours[5]);
	$("#layer1 #top1 #two").css("background-color", side_colours[4]);
	$("#layer1 #top1 #three").css("background-color", side_colours[3]);
	$("#layer1 #left #one").css("background-color", side_colours[6]);
	$("#layer2 #left #one").css("background-color", side_colours[7]);
	$("#layer3 #left #one").css("background-color", side_colours[8]);
	$("#layer3 #bottom1 #one").css("background-color", side_colours[11]);
	$("#layer3 #bottom1 #two").css("background-color", side_colours[10]);
	$("#layer3 #bottom1 #three").css("background-color", side_colours[9]);
	$("#layer1 #right #one").css("background-color", side_colours[0]);
	$("#layer2 #right #one").css("background-color", side_colours[1]);
	$("#layer3 #right #one").css("background-color", side_colours[2]);

	$("#layer1 #front #one").css("background-color", face_colours[5]);
	$("#layer1 #front #two").css("background-color", face_colours[3]);
	$("#layer1 #front #three").css("background-color", face_colours[0]);
	$("#layer2 #front #one").css("background-color", face_colours[6]);
	$("#layer2 #front #three").css("background-color", face_colours[1]);
	$("#layer3 #front #one").css("background-color", face_colours[7]);
	$("#layer3 #front #two").css("background-color", face_colours[4]);
	$("#layer3 #front #three").css("background-color", face_colours[2]);
}

function getBackSideColours() {
	side_colours = [
		$("#layer1 #top3 #three").css("background-color"),
		$("#layer1 #top3 #two").css("background-color"),
		$("#layer1 #top3 #one").css("background-color"),
		$("#layer1 #left #three").css("background-color"),
		$("#layer2 #left #three").css("background-color"),
		$("#layer3 #left #three").css("background-color"),
		$("#layer3 #bottom3 #one").css("background-color"),
		$("#layer3 #bottom3 #two").css("background-color"),
		$("#layer3 #bottom3 #three").css("background-color"),
		$("#layer3 #right #three").css("background-color"),
		$("#layer2 #right #three").css("background-color"),
		$("#layer1 #right #three").css("background-color")
	];
	
	return side_colours;
}

function getBackFaceColours() {

	back_colours = [
		$("#layer1 #back #one").css("background-color"),
		$("#layer1 #back #two").css("background-color"),
		$("#layer1 #back #three").css("background-color"),
		$("#layer2 #back #one").css("background-color"),
		$("#layer2 #back #three").css("background-color"),
		$("#layer3 #back #one").css("background-color"),
		$("#layer3 #back #two").css("background-color"),
		$("#layer3 #back #three").css("background-color")
	];		

	return back_colours;
}

function backRotation(side_colours, face_colours) {
	$("#layer1 #top3 #three").css("background-color", side_colours[9]);
	$("#layer1 #top3 #two").css("background-color", side_colours[10]);
	$("#layer1 #top3 #one").css("background-color", side_colours[11]);
	$("#layer1 #left #three").css("background-color", side_colours[0]);
	$("#layer2 #left #three").css("background-color", side_colours[1]);
	$("#layer3 #left #three").css("background-color", side_colours[2]);
	$("#layer3 #bottom3 #one").css("background-color", side_colours[3]);
	$("#layer3 #bottom3 #two").css("background-color", side_colours[4]);
	$("#layer3 #bottom3 #three").css("background-color", side_colours[5]);
	$("#layer3 #right #three").css("background-color", side_colours[6]);
	$("#layer2 #right #three").css("background-color", side_colours[7]);
	$("#layer1 #right #three").css("background-color", side_colours[8]);

	$("#layer1 #back #one").css("background-color", face_colours[2]);
	$("#layer1 #back #two").css("background-color", face_colours[4]);
	$("#layer1 #back #three").css("background-color", face_colours[7]);
	$("#layer2 #back #one").css("background-color", face_colours[1]);
	$("#layer2 #back #three").css("background-color", face_colours[6]);
	$("#layer3 #back #one").css("background-color", face_colours[0]);
	$("#layer3 #back #two").css("background-color", face_colours[3]);
	$("#layer3 #back #three").css("background-color", face_colours[5]);
}

function backPrimeRotation(side_colours, face_colours) {
	$("#layer1 #top3 #three").css("background-color", side_colours[3]);
	$("#layer1 #top3 #two").css("background-color", side_colours[4]);
	$("#layer1 #top3 #one").css("background-color", side_colours[5]);
	$("#layer1 #left #three").css("background-color", side_colours[6]);
	$("#layer2 #left #three").css("background-color", side_colours[7]);
	$("#layer3 #left #three").css("background-color", side_colours[8]);
	$("#layer3 #bottom3 #one").css("background-color", side_colours[9]);
	$("#layer3 #bottom3 #two").css("background-color", side_colours[10]);
	$("#layer3 #bottom3 #three").css("background-color", side_colours[11]);
	$("#layer3 #right #three").css("background-color", side_colours[0]);
	$("#layer2 #right #three").css("background-color", side_colours[1]);
	$("#layer1 #right #three").css("background-color", side_colours[2]);

	$("#layer1 #back #one").css("background-color", face_colours[5]);
	$("#layer1 #back #two").css("background-color", face_colours[3]);
	$("#layer1 #back #three").css("background-color", face_colours[0]);
	$("#layer2 #back #one").css("background-color", face_colours[6]);
	$("#layer2 #back #three").css("background-color", face_colours[1]);
	$("#layer3 #back #one").css("background-color", face_colours[7]);
	$("#layer3 #back #two").css("background-color", face_colours[4]);
	$("#layer3 #back #three").css("background-color", face_colours[2]);
}

function getRightSideColours() {
	side_colours = [
		$("#layer1 #top3 #three").css("background-color"),
		$("#layer1 #top2 #three").css("background-color"),
		$("#layer1 #top1 #three").css("background-color"),
		$("#layer1 #front #three").css("background-color"),
		$("#layer2 #front #three").css("background-color"),
		$("#layer3 #front #three").css("background-color"),
		$("#layer3 #bottom1 #three").css("background-color"),
		$("#layer3 #bottom2 #three").css("background-color"),
		$("#layer3 #bottom3 #three").css("background-color"),
		$("#layer3 #back #three").css("background-color"),
		$("#layer2 #back #three").css("background-color"),
		$("#layer1 #back #three").css("background-color")
	];

	return side_colours;
}

function getRightFaceColours() {

	right_colours = [
		$("#layer1 #right #one").css("background-color"),
		$("#layer1 #right #two").css("background-color"),
		$("#layer1 #right #three").css("background-color"),
		$("#layer2 #right #one").css("background-color"),
		$("#layer2 #right #three").css("background-color"),
		$("#layer3 #right #one").css("background-color"),
		$("#layer3 #right #two").css("background-color"),
		$("#layer3 #right #three").css("background-color")
	];

	return right_colours;
}

function rightPrimeRotation(side_colours, face_colours) {
	$("#layer1 #top3 #three").css("background-color", side_colours[9]);
	$("#layer1 #top2 #three").css("background-color", side_colours[10]);
	$("#layer1 #top1 #three").css("background-color", side_colours[11]);
	$("#layer1 #front #three").css("background-color", side_colours[0]);
	$("#layer2 #front #three").css("background-color", side_colours[1]);
	$("#layer3 #front #three").css("background-color", side_colours[2]);
	$("#layer3 #bottom1 #three").css("background-color", side_colours[3]);
	$("#layer3 #bottom2 #three").css("background-color", side_colours[4]);
	$("#layer3 #bottom3 #three").css("background-color", side_colours[5]);
	$("#layer3 #back #three").css("background-color", side_colours[6]);
	$("#layer2 #back #three").css("background-color", side_colours[7]);
	$("#layer1 #back #three").css("background-color", side_colours[8]);

	$("#layer1 #right #one").css("background-color", face_colours[2]);
	$("#layer1 #right #two").css("background-color", face_colours[4]);
	$("#layer1 #right #three").css("background-color", face_colours[7]);
	$("#layer2 #right #one").css("background-color", face_colours[1]);
	$("#layer2 #right #three").css("background-color", face_colours[6]);
	$("#layer3 #right #one").css("background-color", face_colours[0]);
	$("#layer3 #right #two").css("background-color", face_colours[3]);
	$("#layer3 #right #three").css("background-color", face_colours[5]);
}

function rightRotation(side_colours, face_colours) {
	$("#layer1 #top3 #three").css("background-color", side_colours[3]);
	$("#layer1 #top2 #three").css("background-color", side_colours[4]);
	$("#layer1 #top1 #three").css("background-color", side_colours[5]);
	$("#layer1 #front #three").css("background-color", side_colours[6]);
	$("#layer2 #front #three").css("background-color", side_colours[7]);
	$("#layer3 #front #three").css("background-color", side_colours[8]);
	$("#layer3 #bottom1 #three").css("background-color", side_colours[9]);
	$("#layer3 #bottom2 #three").css("background-color", side_colours[10]);
	$("#layer3 #bottom3 #three").css("background-color", side_colours[11]);
	$("#layer3 #back #three").css("background-color", side_colours[0]);
	$("#layer2 #back #three").css("background-color", side_colours[1]);
	$("#layer1 #back #three").css("background-color", side_colours[2]);

	$("#layer1 #right #one").css("background-color", face_colours[5]);
	$("#layer1 #right #two").css("background-color", face_colours[3]);
	$("#layer1 #right #three").css("background-color", face_colours[0]);
	$("#layer2 #right #one").css("background-color", face_colours[6]);
	$("#layer2 #right #three").css("background-color", face_colours[1]);
	$("#layer3 #right #one").css("background-color", face_colours[7]);
	$("#layer3 #right #two").css("background-color", face_colours[4]);
	$("#layer3 #right #three").css("background-color", face_colours[2]);
}

function getLeftSideColours() {
	side_colours = [
		$("#layer1 #top3 #one").css("background-color"),
		$("#layer1 #top2 #one").css("background-color"),
		$("#layer1 #top1 #one").css("background-color"),
		$("#layer1 #front #one").css("background-color"),
		$("#layer2 #front #one").css("background-color"),
		$("#layer3 #front #one").css("background-color"),
		$("#layer3 #bottom1 #one").css("background-color"),
		$("#layer3 #bottom2 #one").css("background-color"),
		$("#layer3 #bottom3 #one").css("background-color"),
		$("#layer3 #back #one").css("background-color"),
		$("#layer2 #back #one").css("background-color"),
		$("#layer1 #back #one").css("background-color")
	];

	return side_colours;
}

function getLeftFaceColours() {

	left_colours = [
		$("#layer1 #left #one").css("background-color"),
		$("#layer1 #left #two").css("background-color"),
		$("#layer1 #left #three").css("background-color"),
		$("#layer2 #left #one").css("background-color"),
		$("#layer2 #left #three").css("background-color"),
		$("#layer3 #left #one").css("background-color"),
		$("#layer3 #left #two").css("background-color"),
		$("#layer3 #left #three").css("background-color")
	];

	return left_colours;
}

function leftRotation(side_colours, face_colours) {
	$("#layer1 #top3 #one").css("background-color", side_colours[9]);
	$("#layer1 #top2 #one").css("background-color", side_colours[10]);
	$("#layer1 #top1 #one").css("background-color", side_colours[11]);
	$("#layer1 #front #one").css("background-color", side_colours[0]);
	$("#layer2 #front #one").css("background-color", side_colours[1]);
	$("#layer3 #front #one").css("background-color", side_colours[2]);
	$("#layer3 #bottom1 #one").css("background-color", side_colours[3]);
	$("#layer3 #bottom2 #one").css("background-color", side_colours[4]);
	$("#layer3 #bottom3 #one").css("background-color", side_colours[5]);
	$("#layer3 #back #one").css("background-color", side_colours[6]);
	$("#layer2 #back #one").css("background-color", side_colours[7]);
	$("#layer1 #back #one").css("background-color", side_colours[8]);

	$("#layer1 #left #one").css("background-color", face_colours[2]);
	$("#layer1 #left #two").css("background-color", face_colours[4]);
	$("#layer1 #left #three").css("background-color", face_colours[7]);
	$("#layer2 #left #one").css("background-color", face_colours[1]);
	$("#layer2 #left #three").css("background-color", face_colours[6]);
	$("#layer3 #left #one").css("background-color", face_colours[0]);
	$("#layer3 #left #two").css("background-color", face_colours[3]);
	$("#layer3 #left #three").css("background-color", face_colours[5]);
}

function leftPrimeRotation(side_colours, face_colours) {
	$("#layer1 #top3 #one").css("background-color", side_colours[3]);
	$("#layer1 #top2 #one").css("background-color", side_colours[4]);
	$("#layer1 #top1 #one").css("background-color", side_colours[5]);
	$("#layer1 #front #one").css("background-color", side_colours[6]);
	$("#layer2 #front #one").css("background-color", side_colours[7]);
	$("#layer3 #front #one").css("background-color", side_colours[8]);
	$("#layer3 #bottom1 #one").css("background-color", side_colours[9]);
	$("#layer3 #bottom2 #one").css("background-color", side_colours[10]);
	$("#layer3 #bottom3 #one").css("background-color", side_colours[11]);
	$("#layer3 #back #one").css("background-color", side_colours[0]);
	$("#layer2 #back #one").css("background-color", side_colours[1]);
	$("#layer1 #back #one").css("background-color", side_colours[2]);

	$("#layer1 #left #one").css("background-color", face_colours[5]);
	$("#layer1 #left #two").css("background-color", face_colours[3]);
	$("#layer1 #left #three").css("background-color", face_colours[0]);
	$("#layer2 #left #one").css("background-color", face_colours[6]);
	$("#layer2 #left #three").css("background-color", face_colours[1]);
	$("#layer3 #left #one").css("background-color", face_colours[7]);
	$("#layer3 #left #two").css("background-color", face_colours[4]);
	$("#layer3 #left #three").css("background-color", face_colours[2]);
}

function getMiddleColours() {
	colours = [
		$("#layer1 #front #two").css("background-color"),
		$("#layer2 #front #two").css("background-color"),
		$("#layer3 #front #two").css("background-color"),
		$("#layer3 #bottom1 #two").css("background-color"),
		$("#layer3 #bottom2 #two").css("background-color"),
		$("#layer3 #bottom3 #two").css("background-color"),
		$("#layer3 #back #two").css("background-color"),
		$("#layer2 #back #two").css("background-color"),
		$("#layer1 #back #two").css("background-color"),
		$("#layer1 #top3 #two").css("background-color"),
		$("#layer1 #top2 #two").css("background-color"),
		$("#layer1 #top1 #two").css("background-color")
	];

	return colours;
}

function middleRotation(colours) {
	$("#layer1 #front #two").css("background-color", colours[9]);
	$("#layer2 #front #two").css("background-color", colours[10]);
	$("#layer3 #front #two").css("background-color", colours[11]);
	$("#layer3 #bottom1 #two").css("background-color", colours[0]);
	$("#layer3 #bottom2 #two").css("background-color", colours[1]);
	$("#layer3 #bottom3 #two").css("background-color", colours[2]);
	$("#layer3 #back #two").css("background-color", colours[3]);
	$("#layer2 #back #two").css("background-color", colours[4]);
	$("#layer1 #back #two").css("background-color", colours[5]);
	$("#layer1 #top3 #two").css("background-color", colours[6]);
	$("#layer1 #top2 #two").css("background-color", colours[7]);
	$("#layer1 #top1 #two").css("background-color", colours[8]);
}

function middlePrimeRotation(colours) {
	$("#layer1 #front #two").css("background-color", colours[3]);
	$("#layer2 #front #two").css("background-color", colours[4]);
	$("#layer3 #front #two").css("background-color", colours[5]);
	$("#layer3 #bottom1 #two").css("background-color", colours[6]);
	$("#layer3 #bottom2 #two").css("background-color", colours[7]);
	$("#layer3 #bottom3 #two").css("background-color", colours[8]);
	$("#layer3 #back #two").css("background-color", colours[9]);
	$("#layer2 #back #two").css("background-color", colours[10]);
	$("#layer1 #back #two").css("background-color", colours[11]);
	$("#layer1 #top3 #two").css("background-color", colours[0]);
	$("#layer1 #top2 #two").css("background-color", colours[1]);
	$("#layer1 #top1 #two").css("background-color", colours[2]);
}

function getMiddleYColours() {
	colours = [
		$("#layer2 #front #one").css("background-color"),
		$("#layer2 #front #two").css("background-color"),
		$("#layer2 #front #three").css("background-color"),
		$("#layer2 #right #one").css("background-color"),
		$("#layer2 #right #two").css("background-color"),
		$("#layer2 #right #three").css("background-color"),
		$("#layer2 #back #three").css("background-color"),
		$("#layer2 #back #two").css("background-color"),
		$("#layer2 #back #one").css("background-color"),
		$("#layer2 #left #three").css("background-color"),
		$("#layer2 #left #two").css("background-color"),
		$("#layer2 #left #one").css("background-color")
	];

	return colours;
}

function middleYPrimeRotation(colours) {
	$("#layer2 #front #one").css("background-color", colours[3]);
	$("#layer2 #front #two").css("background-color", colours[4]);
	$("#layer2 #front #three").css("background-color", colours[5]);
	$("#layer2 #right #one").css("background-color", colours[6]);
	$("#layer2 #right #two").css("background-color", colours[7]);
	$("#layer2 #right #three").css("background-color", colours[8]);
	$("#layer2 #back #three").css("background-color", colours[9]);
	$("#layer2 #back #two").css("background-color", colours[10]);
	$("#layer2 #back #one").css("background-color", colours[11]);
	$("#layer2 #left #three").css("background-color", colours[0]);
	$("#layer2 #left #two").css("background-color", colours[1]);
	$("#layer2 #left #one").css("background-color", colours[2]);
}

function middleYRotation(colours) {
	$("#layer2 #front #one").css("background-color", colours[9]);
	$("#layer2 #front #two").css("background-color", colours[10]);
	$("#layer2 #front #three").css("background-color", colours[11]);
	$("#layer2 #right #one").css("background-color", colours[0]);
	$("#layer2 #right #two").css("background-color", colours[1]);
	$("#layer2 #right #three").css("background-color", colours[2]);
	$("#layer2 #back #three").css("background-color", colours[3]);
	$("#layer2 #back #two").css("background-color", colours[4]);
	$("#layer2 #back #one").css("background-color", colours[5]);
	$("#layer2 #left #three").css("background-color", colours[6]);
	$("#layer2 #left #two").css("background-color", colours[7]);
	$("#layer2 #left #one").css("background-color", colours[8]);
}

function getMiddleZColours() {
	colours = [
		$("#layer1 #top2 #one").css("background-color"),
		$("#layer1 #top2 #two").css("background-color"),
		$("#layer1 #top2 #three").css("background-color"),
		$("#layer1 #right #two").css("background-color"),
		$("#layer2 #right #two").css("background-color"),
		$("#layer3 #right #two").css("background-color"),
		$("#layer3 #bottom2 #three").css("background-color"),
		$("#layer3 #bottom2 #two").css("background-color"),
		$("#layer3 #bottom2 #one").css("background-color"),
		$("#layer3 #left #two").css("background-color"),
		$("#layer2 #left #two").css("background-color"),
		$("#layer1 #left #two").css("background-color")
	];

	return colours;
}

function middleZRotation(colours) {
	$("#layer1 #top2 #one").css("background-color", colours[9]);
	$("#layer1 #top2 #two").css("background-color", colours[10]);
	$("#layer1 #top2 #three").css("background-color", colours[11]);
	$("#layer1 #right #two").css("background-color", colours[0]);
	$("#layer2 #right #two").css("background-color", colours[1]);
	$("#layer3 #right #two").css("background-color", colours[2]);
	$("#layer3 #bottom2 #three").css("background-color", colours[3]);
	$("#layer3 #bottom2 #two").css("background-color", colours[4]);
	$("#layer3 #bottom2 #one").css("background-color", colours[5]);
	$("#layer3 #left #two").css("background-color", colours[6]);
	$("#layer2 #left #two").css("background-color", colours[7]);
	$("#layer1 #left #two").css("background-color", colours[8]);
}

function middleZPrimeRotation(colours) {
	$("#layer1 #top2 #one").css("background-color", colours[3]);
	$("#layer1 #top2 #two").css("background-color", colours[4]);
	$("#layer1 #top2 #three").css("background-color", colours[5]);
	$("#layer1 #right #two").css("background-color", colours[6]);
	$("#layer2 #right #two").css("background-color", colours[7]);
	$("#layer3 #right #two").css("background-color", colours[8]);
	$("#layer3 #bottom2 #three").css("background-color", colours[9]);
	$("#layer3 #bottom2 #two").css("background-color", colours[10]);
	$("#layer3 #bottom2 #one").css("background-color", colours[11]);
	$("#layer3 #left #two").css("background-color", colours[0]);
	$("#layer2 #left #two").css("background-color", colours[1]);
	$("#layer1 #left #two").css("background-color", colours[2]);
}
