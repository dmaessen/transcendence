const tournCanvas = document.getElementById('tournamentBracket');
// const gameCanvas = document.getElementById("game");
const tournContext = tournCanvas.getContext('2d');

let players = []; // from backnend with usernames
let matches = []; // from backend

function drawBracket(mode) {
    console.log("drawBracket called with mode:", mode);

    tournCanvas.style.display = 'block';
    tournCanvas.width = 800; // Set the width of the canvas
    tournCanvas.height = 600; // Set the height of the canvas

    tournContext.clearRect(0, 0, tournCanvas.width, tournCanvas.height);
    tournContext.fillStyle = "#000000";
    tournContext.fillRect(0, 0, tournCanvas.width, tournCanvas.height);
    tournContext.font = "20px Courier New";
    tournContext.textAlign = "center";
    tournContext.strokeStyle = "#FFFFFF";
    tournContext.fillStyle = "#FFFFFF";

    if (mode == "4") {
        drawBracketStructure4();
    } else if (mode == "8") {
        drawBracketStructure8();
    }

    fetchTournamentStatus();
    fetch("http://localhost:8080/api/tournament-status/")
        .then(response => response.json())
        .then(data => {
            console.log("Fetched tournament status:", data);
            if (data) { 
                players = data.players; // check on this
                updateBracketWithPlayers(mode);
            }
        })
        .catch(error => console.error("Error fetching tournament status:", error));
}

function drawBracketStructure4() {
    tournContext.beginPath();
    tournContext.moveTo(tournCanvas.width / 4, 100);
    tournContext.lineTo(tournCanvas.width / 2, 100);
    tournContext.moveTo(tournCanvas.width * 3 / 4, 100);
    tournContext.lineTo(tournCanvas.width / 2, 100);
    tournContext.moveTo(tournCanvas.width / 2, 100);
    tournContext.lineTo(tournCanvas.width / 2, 200);
    tournContext.stroke();
}

function drawBracketStructure8() {
    tournContext.beginPath();
    tournContext.moveTo(tournCanvas.width / 8, 50);
    tournContext.lineTo(tournCanvas.width / 4, 50);
    tournContext.moveTo(tournCanvas.width * 3 / 8, 50);
    tournContext.lineTo(tournCanvas.width / 4, 50);
    tournContext.moveTo(tournCanvas.width / 4, 50);
    tournContext.lineTo(tournCanvas.width / 4, 150);
    tournContext.moveTo(tournCanvas.width * 5 / 8, 50);
    tournContext.lineTo(tournCanvas.width * 3 / 4, 50);
    tournContext.moveTo(tournCanvas.width * 7 / 8, 50);
    tournContext.lineTo(tournCanvas.width * 3 / 4, 50);
    tournContext.moveTo(tournCanvas.width * 3 / 4, 50);
    tournContext.lineTo(tournCanvas.width * 3 / 4, 150);
    tournContext.moveTo(tournCanvas.width / 4, 150);
    tournContext.lineTo(tournCanvas.width * 3 / 4, 150);
    tournContext.moveTo(tournCanvas.width / 2, 150);
    tournContext.lineTo(tournCanvas.width / 2, 250);
    tournContext.stroke();
}

function updateBracketWithPlayers(mode) {
    if (mode === '4') {
        tournContext.fillText(players[0] || "Player 1", tournCanvas.width / 4, 90);
        tournContext.fillText(players[1] || "Player 2", tournCanvas.width * 3 / 4, 90);
        tournContext.fillText(players[2] || "Winner 1", tournCanvas.width / 2, 190);
        tournContext.fillText(players[3] || "Final Winner", tournCanvas.width / 2, 290);
    } else if (mode === '8') {
        tournContext.fillText(players[0] || "Player 1", tournCanvas.width / 8, 40);
        tournContext.fillText(players[1] || "Player 2", tournCanvas.width * 3 / 8, 40);
        tournContext.fillText(players[2] || "Player 3", tournCanvas.width * 5 / 8, 40);
        tournContext.fillText(players[3] || "Player 4", tournCanvas.width * 7 / 8, 40);
        tournContext.fillText(players[4] || "Player 5", tournCanvas.width / 8, 140);
        tournContext.fillText(players[5] || "Player 6", tournCanvas.width * 3 / 8, 140);
        tournContext.fillText(players[6] || "Player 7", tournCanvas.width * 5 / 8, 140);
        tournContext.fillText(players[7] || "Player 8", tournCanvas.width * 7 / 8, 140);
        tournContext.fillText(players[8] || "Winner 1", tournCanvas.width / 4, 240);
        tournContext.fillText(players[9] || "Winner 2", tournCanvas.width * 3 / 4, 240);
        tournContext.fillText(players[10] || "Final Winner", tournCanvas.width / 2, 340);
    }
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
