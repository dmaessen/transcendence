let tournamentStartTime = null;
let countdownInterval = null;
let countdownElement = document.getElementById("tournamentCountdown"); // Assuming this element exists in the HTML

// Function to start the countdown
function startTournamentCountdown() {
    tournamentStartTime = Date.now();
    updateTournamentCountdown();

    countdownInterval = setInterval(updateTournamentCountdown, 1000); // Update every second
}

// Function to update the countdown
function updateTournamentCountdown() {
    if (!tournamentStartTime) return;

    const timeElapsed = Math.floor((Date.now() - tournamentStartTime) / 1000);
    const timeRemaining = 300 - timeElapsed; // 5 minutes (300 seconds)

    if (timeRemaining <= 0) {
        clearInterval(countdownInterval); // Stop the countdown when it reaches 0
        tournamentCanceled();
        return;
    }

    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    countdownElement.textContent = `Time remaining: ${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
}

// Function to handle tournament cancellation after timeout
function tournamentCanceled() {
    alert("Tournament has been canceled due to inactivity.");
    // You could also reset the UI or show a message about cancellation
    // and notify the backend to cancel the tournament as well.
    // Update the UI here to reflect the tournament has been canceled.
    socket.send(JSON.stringify({ action: "cancel_tournament" }));
}

function onPlayerJoinTournament() {
    // Start the countdown when the first player joins
    if (!tournamentStartTime) {
        startTournamentCountdown();
    }
}

// when the tournament is full
function onTournamentFull() {
    clearInterval(countdownInterval);
    socket.send(JSON.stringify({ action: "start_tournament" }));
	// start 1v1 games maybe with the other .js files
}
