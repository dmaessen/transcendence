const gameMenuElementFirst = document.getElementById("gameMenuFirst");
const gameMenuElement = document.getElementById("gameMenu");
const gameMenuElementTournament = document.getElementById("gameMenuTournament");
const signInMenuElement = document.getElementById("SignInMenu");

const gameTitle = document.getElementById("gameTitle");
const exitButton = document.getElementById("exitButton");
const instructions1 = document.getElementById("game-instruction1");
const instructions2 = document.getElementById("game-instruction2");

const gameCanvas = document.getElementById("game");
const gameContext = gameCanvas.getContext("2d");

const tournamentMenuBtn = document.getElementById("tournamentBtn");
const tournamentBanner = document.getElementById("tournamentBanner");

let timerInterval;
let keyboardEnabled = true;
let tournamentSpotsOpen = false;

instructions1.style.display = "none";
instructions2.style.display = "none";

const gameMenuFirst = new bootstrap.Modal(gameMenuElementFirst, {
    backdrop: "static",
    keyboard: false,
});

const gameMenu = new bootstrap.Modal(gameMenuElement, {
    backdrop: "static",
    keyboard: false,
});

const gameMenuTournament = new bootstrap.Modal(gameMenuElementTournament, {
    backdrop: "static",
    keyboard: false,
});

const SignInMenu = new bootstrap.Modal(signInMenuElement, {
    backdrop: "static",
    keyboard: false,
});

const gameState = { 
    mode: null,
    gameId: null,
    players: [],
    running: false,
    // tournamentOngoing: false,
    playerId: null, // does Laura need?
};

async function login(email,password){
    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

function startGame(mode) {
    keyboardEnabled = true;
    gameState.running = false;
    gameState.mode = mode; 
    resetGame(mode);

    console.log(`Game started in ${mode} mode.`);
    gameMenu.hide();

    gameTitle.style.display = "block";
    gameCanvas.style.display = "block";
    gameCanvas.width = 1400;
    gameCanvas.height = 1000;
    gameCanvas.style.width = gameCanvas.width / 2 + "px";
    gameCanvas.style.height = gameCanvas.height / 2 + "px";

    if (mode === "One Player") {
        gameTitle.textContent = "One Player";
        instructions1.style.display = "block";
        connectWebSocket(mode);
    } if (mode === "Two Players (hot seat)") {
        gameTitle.textContent = "Two Players (hot seat)";
        instructions2.style.display = "block";
        connectWebSocket(mode);
    } if (mode === "Two Players (remote)") { // TODO
        alert(`${mode} mode is not yet implemented.`);
        gameTitle.textContent = "Two Players (remote)";
        instructions1.style.display = "block";
        connectWebSocket(mode);
    } if (mode === "Two Players (with a friend)") { // TODO
        alert(`${mode} mode is not yet implemented.`);
        gameTitle.textContent = "Two Players (with a friend)";
        instructions1.style.display = "block";
        //connectWebSocket(mode);
    } if (mode === "Tournament - 4 Players" || mode === "Tournament - 8 Players") { // TODO
        tournamentSpotsOpen = true;
        localStorage.setItem("tournamentSpotsOpen", "true");
        gameMenuTournament.hide();
        alert(`${mode} mode is not yet implemented.`);
        gameTitle.textContent = `${mode}`;
        instructions1.style.display = "block";
        if (mode === "Tournament - 4 Players")
            connectWebSocket(4);
        else
            connectWebSocket(8);
    }
}

// document.getElementById("profileBtn").addEventListener("click", () => ); // TODO connect with Laura
// document.getElementById("friendsBtn").addEventListener("click", () => ); // TODO connect with Laura
// document.getElementById("tournamentInfoBtn").addEventListener("click", () => ); // TODO connect with Laura

document.getElementById("playBtn").addEventListener("click", () => {
    gameMenuFirst.hide();
    gameMenu.show();
    if (tournamentSpotsOpen)
        tournamentMenuBtn.style.display = "none";
    else
        tournamentMenuBtn.style.display = "block";
});

document.getElementById("onePlayerBtn").addEventListener("click", () => startGame("One Player"));
document.getElementById("twoPlayersBtn").addEventListener("click", () => startGame("Two Players (hot seat)"));
document.getElementById("twoPlayersRemoteBtn").addEventListener("click", () => startGame("Two Players (remote)"));
document.getElementById("twoPlayersFriendsBtn").addEventListener("click", () => startGame("Two Players (with a friend)"));

document.getElementById("tournamentBtn").addEventListener("click", () => {
    if (!tournamentSpotsOpen) {
        gameMenuTournament.show();
        gameMenu.hide();
    } else {
        alert("A tournament is already ongoing.");
}});
document.getElementById("fourPlayersTournamentBtn").addEventListener("click", () => {
    startGame("Tournament - 4 Players");
    disableTournamentButtons();
    // showTournamentAdBanner();
});
document.getElementById("eightPlayersTournamentBtn").addEventListener("click", () => {
    startGame("Tournament - 8 Players");
    disableTournamentButtons();
    // showTournamentAdBanner();
});

document.getElementById("previous1Btn").addEventListener("click", () => {
    gameMenu.hide();
    gameMenuFirst.show();
});
document.getElementById("previous2Btn").addEventListener("click", () => {
    gameMenuTournament.hide();
    gameMenu.show();
});

document.getElementById("exitButton").addEventListener("click", () =>  {
    keyboardEnabled = false;
    gameState.running = false;
    stopTimer();
    document.getElementById("timer").innerHTML = " ";
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    gameCanvas.style.display = "none";
    gameTitle.style.display = "none";
    socket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
    socket.close()
    gameMenuFirst.show();
});

tournamentBanner.addEventListener("click", () => {
    if (localStorage.getItem("tournamentSpotsOpen") === "true") {
        connectWebSocket("tournament");
    }
});

async function fetchTournamentStatus() {
    try {
        const response = await fetch("http://localhost:8080/api/tournament-status/");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Tournament Status:", data);

        if (data.tournament_active) {
            console.log("tournament active in fetchTournamentStatus()")
            showTournamentAdBanner(data.players_in, data.players_in + data.remaining_spots);
        }
    } catch (error) {
        console.error("Error fetching tournament status:", error);
    }
}

window.addEventListener("load", () => {
    gameMenuFirst.show();
    
    fetchTournamentStatus();

    fetch("http://localhost:8080/api/tournament-status/")
        .then(response => response.json())
        .then(data => {
            console.log("Fetched tournament status:", data);
            if (data.tournament_active && data.remaining_spots != 0) {
                showTournamentAdBanner(data.players_in, data.players_in + data.remaining_spots);
            }
        })
        .catch(error => console.error("Error fetching tournament status:", error));
});

function disableTournamentButtons() {
    tournamentMenuBtn.style.display = "none";  // Hide the tournament button
    gameMenuTournament.hide(); // Hide the tournament menu
}

function showTournamentAdBanner(players_in, total_spots) {// Show banner to promote for other players
    if (tournamentSpotsOpen && players_in < total_spots) {
        localStorage.setItem("tournamentSpotOpen", "true"); // needed again here??
        tournamentBanner.style.display = "block"; 
        const playersInTournament = document.getElementById("playersInTournament");
        playersInTournament.textContent = `${players_in}/${total_spots}`;
    } else {
        tournamentSpotsOpen = false;
        localStorage.setItem("tournamentSpotsOpen", "false");
        tournamentBanner.style.display = "none";  // Hide it if no tournament or full
    }
}

function showWaitingRoomTournament() {
    gameContext.font = "50px Courier New";
    gameContext.fillStyle = "#000000";
    gameContext.fillRect(gameCanvas.width / 2 - 350, gameCanvas.height / 2 - 48, 700, 100);
    gameContext.fillStyle = "#ffffff";
    gameContext.textAlign = "center";
    gameContext.fillText("Waiting for players to join...", gameCanvas.width / 2, gameCanvas.height / 2 + 15);
    keyboardEnabled = false;
}

function updateGameState(data) {
    const { players, ball, score, net, width, height } = data;
    if (!players || !ball || !score || !net || !width || !height) {
        console.error("Invalid game state received:", data);
        return;
    }

    gameContext.clearRect(0, 0, gameCanvas.width, gameCanvas.height);

    // draw paddles for each player
    for (let playerId in players) {
        const player = players[playerId];
        gameContext.fillStyle = "white";
        gameContext.fillRect(player.x, player.y, player.width, player.height);
    }

    // draw ball
    gameContext.beginPath();
    gameContext.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    gameContext.fillStyle = "white";
    gameContext.fill();

    // draw net
    for (let i = 1; i < gameCanvas.height; i += net.height + net.gap) {
        gameContext.fillStyle = "white";
        gameContext.fillRect(net.x, i, net.width, net.height);
    }

    // draw scores
    gameContext.font = "60px Courier New";
    gameContext.fillText(score.player, gameCanvas.width / 4, 80);
    gameContext.fillText(score.opponent, (gameCanvas.width * 3) / 4, 80);
}

function displayStartPrompt() {
    gameContext.font = "50px Courier New";
    gameContext.fillStyle = "#000000";
    gameContext.fillRect(gameCanvas.width / 2 - 350, gameCanvas.height / 2 - 48, 700, 100);
    gameContext.fillStyle = "#ffffff";
    gameContext.textAlign = "center";
    gameContext.fillText("Press any key to start", gameCanvas.width / 2, gameCanvas.height / 2 + 15);
    keyboardEnabled = true;
}

function startGameMenu() {
    gameState.running = false;
    displayStartPrompt();
}

function showEndMenu(reason) {
    keyboardEnabled = false;
    gameState.running = false;
    stopTimer();
    document.getElementById("timer").innerHTML = "Game Over!"; // needed? or just maybe hide timer?

    gameContext.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
    gameContext.font = "50px Courier New";
    gameContext.fillStyle = "#000000";
    gameContext.fillRect(gameCanvas.width / 2 - 350, gameCanvas.height / 2 - 48, 700, 100);
    gameContext.fillStyle = "#ffffff";
    gameContext.textAlign = "center";
    gameContext.fillText(reason, gameCanvas.width / 2, gameCanvas.height / 2 + 15);

    document.getElementById("timer").innerHTML = " ";
}

function startTimer() {
    let distance = 0;
    if (timerInterval)
        clearInterval(timerInterval);
    
    timerInterval = setInterval(() => {
        distance += 1000; // incr the time by 1000ms/1sec
        let minutes = Math.floor(distance / (1000 * 60));
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);

        document.getElementById("timer").innerHTML = `${minutes}m ${seconds}s`;
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

document.addEventListener("keydown", (event) => {
    if (keyboardEnabled === false)
        return;
    if (!gameState.running && socket && socket.readyState === WebSocket.OPEN) {
        console.log("Key pressed. Starting the game...");
        gameState.running = true;
        socket.send(JSON.stringify({ action: "start", mode: gameState.mode }));
        startTimer();
    }
});

document.addEventListener("keydown", (event) => {
    let direction = null;
    if (gameState.mode != "Two Players (hot seat)" && gameState.running)
        direction = event.key === "ArrowUp" ? "up" : event.key === "ArrowDown" ? "down" : null;
    else (gameState.mode === "Two Players (hot seat)" && gameState.running)
        direction = event.key === "ArrowUp" ? "up" : event.key === "ArrowDown" ? "down" : event.key === "w" ? "w_up" : event.key === "s" ? "s_down" : null;
    if (direction) {
        console.log("ARROWS PRESSED");
        socket.send(JSON.stringify({ action: "move", direction: direction, game_id: gameState.gameId }));
    }
});

window.addEventListener("beforeunload", () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log("Closing WebSocket before page unload.");
        gameState.running = false;
        stopTimer();
        instructions1.style.display = "none";
        instructions2.style.display = "none";
        gameCanvas.style.display = "none";
        gameTitle.style.display = "none";
        socket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
        socket.close()
        gameMenuFirst.show();
    }
});
