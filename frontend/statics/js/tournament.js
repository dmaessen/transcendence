//{/* <canvas id="tournamentBracket" width="800" height="600"></canvas> */}

// const gameCanvas = document.getElementById('tournamentBracket');
const tournContext = gameCanvas.getContext('2d');

let players = [];
let matches = [];

function drawBracket(mode) {
    tournContext.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
    tournContext.font = "20px Courier New";
    tournContext.textAlign = "center";

    if (mode === '4') {
        draw4PlayerBracket();
    } else if (mode === '8') {
        draw8PlayerBracket();
    }
}

function draw4PlayerBracket() {
    // Draw lines for 4 player bracket
    tournContext.beginPath();
    tournContext.moveTo(gameCanvas.width / 2, 50);
    tournContext.lineTo(gameCanvas.width / 2, 150);
    tournContext.moveTo(gameCanvas.width / 4, 150);
    tournContext.lineTo(gameCanvas.width * 3 / 4, 150);
    tournContext.moveTo(gameCanvas.width / 4, 150);
    tournContext.lineTo(gameCanvas.width / 4, 250);
    tournContext.moveTo(gameCanvas.width * 3 / 4, 150);
    tournContext.lineTo(gameCanvas.width * 3 / 4, 250);
    tournContext.stroke();

    // Draw player names or placeholders
    tournContext.fillText("Player 1", gameCanvas.width / 4, 130);
    tournContext.fillText("Player 2", gameCanvas.width * 3 / 4, 130);
    tournContext.fillText("Winner 1", gameCanvas.width / 2, 50);
    tournContext.fillText("Winner 2", gameCanvas.width / 2, 230);
}

function draw8PlayerBracket() {
    // Draw lines for 8 player bracket
    tournContext.beginPath();
    tournContext.moveTo(gameCanvas.width / 2, 50);
    tournContext.lineTo(gameCanvas.width / 2, 100);
    tournContext.moveTo(gameCanvas.width / 2, 150);
    tournContext.lineTo(gameCanvas.width / 2, 200);
    tournContext.moveTo(gameCanvas.width / 4, 100);
    tournContext.lineTo(gameCanvas.width * 3 / 4, 100);
    tournContext.moveTo(gameCanvas.width / 4, 200);
    tournContext.lineTo(gameCanvas.width * 3 / 4, 200);
    tournContext.moveTo(gameCanvas.width / 4, 100);
    tournContext.lineTo(gameCanvas.width / 4, 150);
    tournContext.moveTo(gameCanvas.width * 3 / 4, 100);
    tournContext.lineTo(gameCanvas.width * 3 / 4, 150);
    tournContext.moveTo(gameCanvas.width / 4, 200);
    tournContext.lineTo(gameCanvas.width / 4, 250);
    tournContext.moveTo(gameCanvas.width * 3 / 4, 200);
    tournContext.lineTo(gameCanvas.width * 3 / 4, 250);
    tournContext.stroke();

    // Draw player names or placeholders
    tournContext.fillText("Player 1", gameCanvas.width / 4, 80);
    tournContext.fillText("Player 2", gameCanvas.width * 3 / 4, 80);
    tournContext.fillText("Player 3", gameCanvas.width / 4, 180);
    tournContext.fillText("Player 4", gameCanvas.width * 3 / 4, 180);
    tournContext.fillText("Winner 1", gameCanvas.width / 2, 50);
    tournContext.fillText("Winner 2", gameCanvas.width / 2, 150);
    tournContext.fillText("Winner 3", gameCanvas.width / 2, 250);
}

function updateBracket(winners) {
    // Update the bracket with the winners of the matches
    // This function should be called after each match to update the bracket
    // winners is an array of objects with matchId and winnerId
    // Example: [{matchId: 1, winnerId: 'Player 1'}, {matchId: 2, winnerId: 'Player 3'}]

    // Update the bracket based on the winners
    // This is a placeholder for the actual update logic
    drawBracket(mode);
}

// Example usage
drawBracket(mode);








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
