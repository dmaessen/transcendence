const tournCanvas = document.getElementById('tournamentBracket');
const tournContext = tournCanvas.getContext('2d');

async function drawBracket(mode) {
    console.log("drawBracket called with mode:", mode);

    tournCanvas.style.display = 'block';
    tournCanvas.width = 800;
    tournCanvas.height = 600;
    tournContext.clearRect(0, 0, tournCanvas.width, tournCanvas.height);
    tournContext.fillStyle = "#000000";
    tournContext.fillRect(0, 0, tournCanvas.width, tournCanvas.height);
    tournContext.strokeStyle = "#FFFFFF";
    tournContext.fillStyle = "#FFFFFF";
    tournContext.font = "14px Courier New";
    tournContext.textAlign = "center";

    await updateBracketWithData(mode);
    let tournamentInterval = setInterval(async () => await updateBracketWithData(mode), 5000); // auto-update every 5s 
    // make the above stop when tournament over or if someone quits the tournament
}

// call stopTournamentUpdates() below when the tournament ends or a player quits
function stopTournamentUpdates() {
    if (tournamentInterval) {
        clearInterval(tournamentInterval);
        console.log("Tournament updates stopped.");
    }
}

async function updateBracketWithData(mode) {
    try {
        const data = await fetchData("http://localhost:8080/api/tournament-status/");
        console.log("Fetched tournament status:", data);
        if (data) {
            populatePlayerFields(data.players);
            updateBracket(mode, data.bracket, data.players, data.winners, data.current_round);
        }
    } catch (error) {
        console.error("Error fetching tournament status:", error);
    }
}

function populatePlayerFields(players) {
    document.getElementById('Player1').innerHTML = `<option>${players[0] ? players[0].username : 'Player 1'}</option>`;
    document.getElementById('Player2').innerHTML = `<option>${players[1] ? players[1].username : 'Player 2'}</option>`;
    document.getElementById('Player3').innerHTML = `<option>${players[2] ? players[2].username : 'Player 3'}</option>`;
    document.getElementById('Player4').innerHTML = `<option>${players[3] ? players[3].username : 'Player 4'}</option>`;
    document.getElementById('Player5').innerHTML = `<option>${players[4] ? players[4].username : 'Player 5'}</option>`;
    document.getElementById('Player6').innerHTML = `<option>${players[5] ? players[5].username : 'Player 6'}</option>`;
    document.getElementById('Player7').innerHTML = `<option>${players[6] ? players[6].username : 'Player 7'}</option>`;
    document.getElementById('Player8').innerHTML = `<option>${players[7] ? players[7].username : 'Player 8'}</option>`;

    document.getElementById('Player9').innerHTML = `<option>${players[8] ? players[8].username : 'Winner 1'}</option>`;
    document.getElementById('Player10').innerHTML = `<option>${players[9] ? players[9].username : 'Winner 2'}</option>`;
    document.getElementById('Player11').innerHTML = `<option>${players[10] ? players[10].username : 'Winner 1'}</option>`;
    document.getElementById('Player12').innerHTML = `<option>${players[11] ? players[11].username : 'Winner 2'}</option>`;

    document.getElementById('Player13').innerHTML = `<option>${players[12] ? players[12].username : 'Winner 1'}</option>`;
    document.getElementById('Player14').innerHTML = `<option>${players[13] ? players[13].username : 'Winner 2'}</option>`;
    // box only for winner
}

function updateBracket(mode, bracket, players, winners, currentRound) {
    tournContext.clearRect(0, 0, tournCanvas.width, tournCanvas.height);
    drawBracketStructure(mode);

    tournContext.font = "16px Courier New";
    players.forEach((player, index) => {
        const x = 70 + Math.floor(index / 2) * 200;
        const y = tournCanvas.height / 8 * (index % 2 === 0 ? 1 : 7);
        tournContext.fillText(player.username || `Player ${index + 1}`, x, y);
    });

    tournContext.font = "18px Courier New";
    winners.forEach((winner, index) => {
        const x = 300 + index * 200;
        const y = tournCanvas.height / 2;
        tournContext.fillText(winner.username || `Winner ${index + 1}`, x, y);
    });

    if (winners.length === 1) {
        displayChampion(winners[0].username);
    }
}

function drawBracketStructure(mode) {
    tournContext.beginPath();
    tournContext.strokeStyle = "#FFFFFF";
    if (mode == "4") {
        drawBracketStructure4();
    } else if (mode == "8") {
        drawBracketStructure8();
    }
    tournContext.stroke();
}

function drawBracketStructure4() {
    drawMatchBox(50, tournCanvas.height / 4, "Match 1");
    drawMatchBox(50, tournCanvas.height * 3 / 4, "Match 2");

    drawMatchBox(250, tournCanvas.height / 2, "Final");

    tournContext.beginPath();
    tournContext.moveTo(150, tournCanvas.height / 4);
    tournContext.lineTo(200, tournCanvas.height / 2);
    tournContext.moveTo(150, tournCanvas.height * 3 / 4);
    tournContext.lineTo(200, tournCanvas.height / 2);
    tournContext.stroke();
}

function drawBracketStructure8() {
    drawMatchBox(50, tournCanvas.height / 8, "Match 1");
    drawMatchBox(50, tournCanvas.height * 3 / 8, "Match 2");
    drawMatchBox(50, tournCanvas.height * 5 / 8, "Match 3");
    drawMatchBox(50, tournCanvas.height * 7 / 8, "Match 4");

    drawMatchBox(250, tournCanvas.height / 4, "Semi 1");
    drawMatchBox(250, tournCanvas.height * 3 / 4, "Semi 2");

    drawMatchBox(450, tournCanvas.height / 2, "Final");

    tournContext.beginPath();
    tournContext.moveTo(150, tournCanvas.height / 8);
    tournContext.lineTo(200, tournCanvas.height / 4);
    tournContext.moveTo(150, tournCanvas.height * 3 / 8);
    tournContext.lineTo(200, tournCanvas.height / 4);

    tournContext.moveTo(150, tournCanvas.height * 5 / 8);
    tournContext.lineTo(200, tournCanvas.height * 3 / 4);
    tournContext.moveTo(150, tournCanvas.height * 7 / 8);
    tournContext.lineTo(200, tournCanvas.height * 3 / 4);

    tournContext.moveTo(350, tournCanvas.height / 4);
    tournContext.lineTo(400, tournCanvas.height / 2);
    tournContext.moveTo(350, tournCanvas.height * 3 / 4);
    tournContext.lineTo(400, tournCanvas.height / 2);
    tournContext.stroke();
}

function drawMatchBox(x, y, label) {
    tournContext.strokeStyle = "#FFFFFF";
    tournContext.fillStyle = "#FFFFFF";
    tournContext.fillRect(x, y - 20, 100, 40);
    tournContext.strokeRect(x, y - 20, 100, 40);
    tournContext.fillStyle = "#000000";
    tournContext.fillText(label, x + 50, y);
}


function displayChampion(championName) {
    tournContext.fillStyle = "#FFD700"; // gold champ
    tournContext.font = "20px Courier New";
    tournContext.fillText(`Champion: ${championName}`, tournCanvas.width / 2, 300);
}






























// let tournamentStartTime = null;
// let countdownInterval = null;
// let countdownElement = document.getElementById("tournamentCountdown"); // Assuming this element exists in the HTML

// // Function to start the countdown
// function startTournamentCountdown() {
//     tournamentStartTime = Date.now();
//     updateTournamentCountdown();

//     countdownInterval = setInterval(updateTournamentCountdown, 1000); // Update every second
// }

// // Function to update the countdown
// function updateTournamentCountdown() {
//     if (!tournamentStartTime) return;

//     const timeElapsed = Math.floor((Date.now() - tournamentStartTime) / 1000);
//     const timeRemaining = 300 - timeElapsed; // 5 minutes (300 seconds)

//     if (timeRemaining <= 0) {
//         clearInterval(countdownInterval); // Stop the countdown when it reaches 0
//         tournamentCanceled();
//         return;
//     }

//     const minutes = Math.floor(timeRemaining / 60);
//     const seconds = timeRemaining % 60;
//     countdownElement.textContent = `Time remaining: ${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
// }

// // Function to handle tournament cancellation after timeout
// function tournamentCanceled() {
//     alert("Tournament has been canceled due to inactivity.");
//     // You could also reset the UI or show a message about cancellation
//     // and notify the backend to cancel the tournament as well.
//     // Update the UI here to reflect the tournament has been canceled.
//     socket.send(JSON.stringify({ action: "cancel_tournament" }));
// }

// function onPlayerJoinTournament() {
//     // Start the countdown when the first player joins
//     if (!tournamentStartTime) {
//         startTournamentCountdown();
//     }
// }

// // when the tournament is full
// function onTournamentFull() {
//     clearInterval(countdownInterval);
//     socket.send(JSON.stringify({ action: "start_tournament" }));
// 	// start 1v1 games maybe with the other .js files
// }
