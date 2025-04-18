const gameMenuElementFirst = document.getElementById("gameMenuFirst");
const gameMenuElement = document.getElementById("gameMenu");
const gameMenuElementTournament = document.getElementById("gameMenuTournament");
const signInMenuElement = document.getElementById("SignInMenu");

const gameTitle = document.getElementById("gameTitle");
const exitButton = document.getElementById("exitButton");
const instructions1 = document.getElementById("game-instruction1");
const instructions2 = document.getElementById("game-instruction2");
const instructions3 = document.getElementById("game-instruction3");

const gameCanvas = document.getElementById("game");
const gameContext = gameCanvas.getContext("2d");

const tournamentMenuBtn = document.getElementById("tournamentBtn");
const tournamentBanner = document.getElementById("tournamentBanner");

let timerInterval;
let keyboardEnabled = true;

instructions1.style.display = "none";
instructions2.style.display = "none";
instructions3.style.display = "none";

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
    playerId: null,
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
    } if (mode === "Two Players (remote)") {
        gameTitle.textContent = "Two Players (remote)";
        instructions1.style.display = "block";
        connectWebSocket(mode);
    } if (mode === "Tournament - 4 Players" || mode === "Tournament - 8 Players") { // TODO
        gameMenuTournament.hide();
        if (mode === "Tournament - 4 Players")
            connectWebSocket(4);
        else
            connectWebSocket(8);
    }
}

document.getElementById("playBtn").addEventListener("click", async() => {
    gameMenuFirst.hide();
    gameMenu.show();

    try {
        const data = await fetchData("/tournament-status/");
        console.log("Fetched tournament status:", data);
        if (data.remaining_spots > 0 && data.players_in > 0) // at least one in
                tournamentMenuBtn.style.display = "none";
            else // check on this
                tournamentMenuBtn.style.display = "block";
    } catch (error) {
        console.error("Error fetching tournament status:", error);
    }
});

document.getElementById("onePlayerBtn").addEventListener("click", () => startGame("One Player"));
document.getElementById("twoPlayersBtn").addEventListener("click", () => startGame("Two Players (hot seat)"));
document.getElementById("twoPlayersRemoteBtn").addEventListener("click", () => startGame("Two Players (remote)"));
document.getElementById("tournamentBtn").addEventListener("click", () => {
        gameMenuTournament.show();
        gameMenu.hide();});
document.getElementById("fourPlayersTournamentBtn").addEventListener("click", () => {
    startGame("Tournament - 4 Players");
    disableTournamentButtons();});
document.getElementById("eightPlayersTournamentBtn").addEventListener("click", () => {
    startGame("Tournament - 8 Players");
    disableTournamentButtons();});

document.getElementById("previous1Btn").addEventListener("click", () => {
    gameMenu.hide();
    gameMenuFirst.show();});
document.getElementById("previous2Btn").addEventListener("click", () => {
    gameMenuTournament.hide();
    gameMenu.show();});

document.getElementById("exitButton").addEventListener("click", () =>  {
    keyboardEnabled = false;
    gameState.running = false;
    stopTimer();
    document.getElementById("timer").innerHTML = " ";
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    gameCanvas.style.display = "none";
    gameTitle.style.display = "none";
    document.getElementById("tournamentBracket").style.display = "none"; // this working??
    document.getElementById("tournamentBracket4").style.display = "none"; // this working??
    websocket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
    websocket.close()
    gameMenuFirst.show();
    // also needs to be pulled out of games/tournament and declare opponent as the winner
});

tournamentBanner.addEventListener("click", async(event) => {
    event.preventDefault();
    try {
        const data = await fetchData("/tournament-status/");
        console.log("Tournament Status:", data);
        if (data.remaining_spots > 0) {
            gameMenuFirst.hide();
            gameMenu.hide();
            gameMenuTournament.hide();

            gameState.mode = data.players_in + data.remaining_spots; 
            keyboardEnabled = true;
            gameState.running = false;
            gameTitle.style.display = "block";
            gameCanvas.style.display = "block";
            gameCanvas.width = 1400;
            gameCanvas.height = 1000;
            gameCanvas.style.width = gameCanvas.width / 2 + "px";
            gameCanvas.style.height = gameCanvas.height / 2 + "px";

            connectWebSocket(data.players_in + data.remaining_spots);
        }
    } catch (error) {
        console.error("Error fetching tournament status:", error);
    }
});

window.addEventListener("load", async () => {
    //get token to check if user is logged, if it is, open main menu if not login modal
    const accessToken = localStorage.getItem("access_token");
    console.log("access_token on game: ", accessToken);
    if (accessToken) {
        // Ensure the onlineWebSocket is open if it wasn't already
        if (!loginsocket || loginsocket.readyState !== WebSocket.OPEN) {
            await loginWebSocket();
        }
        gameMenuFirst.show();
    } else {
        SignInMenu.show();
    }
    const bracketElement = document.getElementById("tournamentBracket");
    bracketElement.style.display = "none";

    try {
        const data = await fetchData("/tournament-status/");
        console.log("Fetched tournament status:", data);
        if (data.remaining_spots > 0 && data.players_in != 0) {
            showTournamentAdBanner(data.players_in, data.players_in + data.remaining_spots);
        }
    } catch (error) {
        console.error("Error fetching tournament status:", error);
    }
});

function disableTournamentButtons() {
    tournamentMenuBtn.style.display = "none";  // Hide the tournament button
    gameMenuTournament.hide(); // Hide the tournament menu
}

function showTournamentAdBanner(players_in, total_spots) {// Show banner to promote for other players
    if (players_in < total_spots) {
        tournamentBanner.style.display = "block"; 
        const playersInTournament = document.getElementById("playersInTournament");
        playersInTournament.textContent = `${players_in}/${total_spots}`;
    } else {
        tournamentBanner.style.display = "none";  // Hide it if no tournament or full
    }
}

function showWaitingRoomTournament(mode) {
    console.log("showWaitingRoomTournament called with mode:", mode);
    keyboardEnabled = false;
    gameState.running = false;
    tournamentBanner.style.display = "none"; // needed?
    document.getElementById("timer").style.display = "none"; // needed??
    //gameTitle.textContent = "Tournament";
    gameTitle.style.display = "none"; // needed??
    gameCanvas.style.display = "none"; // needed??

    // const bracketElement = document.getElementById("tournamentBracket");
    // console.log("Bracket element:", bracketElement);
    // bracketElement.style.display = "grid";
    drawBracket(mode);
}

function updateGameState(data) {
    // if (typeof data === "string") {
    //     try {
    //         data = JSON.parse(data);
    //     } catch (e) {
    //         console.error("Failed to parse game state JSON:", e);
    //         return;
    //     }
    // }

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
    gameContext.font = "30px Courier New";
    const playerIds = Object.keys(players);
    if (playerIds.length >= 1) {
        const player1 = players[playerIds[0]];
        gameContext.fillText(`${player1.username}: ${score.player}`, gameCanvas.width / 4, 80);
    }
    if (playerIds.length >= 2) {
        const player2 = players[playerIds[1]];
        gameContext.fillText(`${player2.username}: ${score.opponent}`, (gameCanvas.width * 3) / 4, 80);
    }
}

function displayStartPrompt() {
    gameCanvas.style.display = "block";
    gameContext.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
    gameContext.font = "50px Courier New";
    gameContext.fillStyle = "#000000";
    gameContext.fillRect(gameCanvas.width / 2 - 350, gameCanvas.height / 2 - 48, 700, 100);
    gameContext.fillStyle = "#ffffff";
    gameContext.textAlign = "center";
    gameContext.fillText("Press any key twice to start", gameCanvas.width / 2, gameCanvas.height / 2 + 15);
    keyboardEnabled = true;
}

function startGameMenu() {
    if (gameState.running == true)
        return;
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
    // if (!gameState.running && socket && socket.readyState === WebSocket.OPEN) {
    //     console.log("Key pressed. Starting the game...");
    //     gameState.running = true;
    //     socket.send(JSON.stringify({ action: "start", mode: gameState.mode }));
    //     startTimer();
    // }
    if (gameState.mode != "One Player" && gameState.mode != "Two Players (hot seat)") {
        if (!gameState.running && websocket && websocket.readyState === WebSocket.OPEN) {
            console.log("Key pressed, 'ready' state, waiting for the other player to start the game...");
            websocket.send(JSON.stringify({ action: "ready", mode: gameState.mode }));
            // gameContext.fillText("30sec to press any key to start", gameCanvas.width / 2, gameCanvas.height / 2 + 15);
            // startTimer();
        }
    }
    else {
        if (!gameState.running && websocket && websocket.readyState === WebSocket.OPEN) {
            console.log("Key pressed. Starting the game...");
            gameState.running = true;
            websocket.send(JSON.stringify({ action: "start", mode: gameState.mode }));
            startTimer();
        }
    }
});

const pressedKeys = new Set();
document.addEventListener("keydown", (event) => { 
    if (gameState.running) {
        pressedKeys.add(event.key);
        // sendMovements();
    }
});
document.addEventListener("keyup", (event) => { 
    if (gameState.running) {
        pressedKeys.delete(event.key);
    }
});
// function sendMovements() {
setInterval(() => {
    if (!gameState.running)
        return;

    let directions = [];

    if (gameState.mode != "Two Players (hot seat)") {
        if (pressedKeys.has("ArrowUp"))
            directions.push("up");
        if (pressedKeys.has("ArrowDown"))
            directions.push("down");
    } else {
        if (pressedKeys.has("ArrowUp"))
            directions.push("up");
        if (pressedKeys.has("ArrowDown"))
            directions.push("down");
        if (pressedKeys.has("w"))
            directions.push("w_up");
        if (pressedKeys.has("s"))
            directions.push("s_down");
    }

    if (directions.length > 0) {
        console.log("keys pressed: ", [...pressedKeys]); // to rm
        websocket.send(JSON.stringify({ action: "move", direction: directions, game_id: gameState.gameId }));
    }
}, 1000 / 60);

// document.addEventListener("keydown", (event) => {
//     let direction = null;
//     if (gameState.mode != "Two Players (hot seat)" && gameState.running)
//         direction = event.key === "ArrowUp" ? "up" : event.key === "ArrowDown" ? "down" : null;
//     else if (gameState.mode === "Two Players (hot seat)" && gameState.running)
//         direction = event.key === "ArrowUp" ? "up" : event.key === "ArrowDown" ? "down" : event.key === "w" ? "w_up" : event.key === "s" ? "s_down" : null;
//     if (direction) {
//         console.log("ARROWS PRESSED");
//         socket.send(JSON.stringify({ action: "move", direction: direction, game_id: gameState.gameId }));
//     }
// });

window.addEventListener("beforeunload", () => {
    if (socket && socket.readyState === WebSocket.OPEN && socket !== loginsocket) {
        console.log("Closing WebSocket before page unload.");
        gameState.running = false;
        stopTimer();
        instructions1.style.display = "none";
        instructions2.style.display = "none";
        gameCanvas.style.display = "none";
        gameTitle.style.display = "none";
        socket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
        socket.close()
        // SignInMenu.show();
    }
    const token = localStorage.getItem("access_token");
    if (!token) {
        SignInMenu.show();
    } else {
        gameMenuFirst.show();
    }
});
