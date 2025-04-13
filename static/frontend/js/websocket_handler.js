// const webwebsocket = `ws://${window.location.host}/ws/game_server/`;
// const tournamentwebwebsocket = `ws://${window.location.host}/ws/tournament/`;

let websocket;
// let tournamentwebwebsocket;

// let socket;
let reconnecting = false; // needed??
let resetting = false; // needed?

function connectWebSocket(mode) {
    // if (websocket && websocket.readyState === WebwebSocket.OPEN) { // this will go wrong no if we are doing one player then tournament?? dif websocket
    //     console.log("WebwebSocket already connected.");
    //     startGameMenu(); // or not
    //     return;
    // }

    if (reconnecting) {
        console.warn("Reconnection already in progress.");
        return;
    }
    
    const token = localStorage.getItem("access_token");
    if (!token) {
        console.error("No token no game!");
        return;
    }
    console.log("token: ", token);

    reconnecting = true;
    console.log("Attempting to connect to websocket...");
    if (mode == "4" || mode == "8")
        websocket = new WebSocket(`ws://${window.location.host}/ws/tournament/?token=${token}`);
        // websocket = new WebSocket(`ws://${window.location.host}/ws/tournament/`);
    else
        websocket = new WebSocket(`ws://${window.location.host}/ws/game_server/?token=${token}`);

    websocket.onopen = async() => {
        console.log("Connected to the game server.");
        websocket.send(JSON.stringify({ action: "connect", mode: mode }));
        reconnecting = false;
        if (mode != "4" && mode != "8") {
            startGameMenu();
        } else if (mode == "4" || mode == "8") {
            try {
                const data = await fetchData("http://localhost:8080/api/tournament-status/");
                console.log("Fetched tournament status:", data);
                if (data.players_in == 0) {
                    websocket.send(JSON.stringify({ action: "start_tournament", mode: mode }));
                    gameState.mode = mode;
                    console.log("start_tounrment from connectWebsocket undergoing");
                }
                websocket.send(JSON.stringify({ action: "join_tournament", mode: mode }));
                gameState.mode = mode;
                showWaitingRoomTournament(mode);
            } catch (error) {
                console.error("Error fetching tournament status:", error);
            }
        }
    };

    websocket.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleServerMessage(message);
        } catch (error) {
            console.error("Error parsing WebSocket message:", error, event.data);
        }
    };

    websocket.onclose = () => {
        console.log(`Disconnected from the game server: ${gameState.playerId}`);
        reconnecting = false;
        //setTimeout(() => connectWebwebSocket(mode), 2000); // reconnects after 2 seconds
    };

    websocket.onerror = (error) => {
        console.error("WebSocket error:", error);
        alert(`WebSocket error: ${error.message}`);
        reconnecting = false;
    };
}

function resetGame(mode) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({ action: "reset", gameId: gameState.gameId, mode }));
    }
    gameState.running = false;
    displayStartPrompt();
}

const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))

const returnToStartMenu = async () => {
    await sleep(6000);
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    gameCanvas.style.display = "none";
    gameTitle.style.display = "none";
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
        await sleep(500);
        websocket.close();
    }
    gameMenuFirst.show();
}

const returnToTournamentWaitingRoom = async () => {
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    instructions3.style.display = "none";
    gameCanvas.style.display = "none";
    gameTitle.style.display = "none";
    if (websocket && websocket.readyState === WebSocket.OPEN)
        websocket.send(JSON.stringify({ action: "disconnect_1v1game", mode: gameState.mode, game_id: gameState.gameId }));
    showWaitingRoomTournament(gameState.mode);
}

const returnToStartMenuAfterTournament = async () => {
    await sleep(5000);
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    instructions3.style.display = "none";
    gameCanvas.style.display = "none";
    gameTitle.style.display = "none";
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        await sleep(500);
        websocket.close();
    }
    gameMenuFirst.show();
}

function handleServerMessage(message) {
    console.log(`(FRONTEND) message.type here is: ${message.type}`);

    switch (message.type) {
        case "started":
            gameState.running = true;
            gameState.gameId = message.game_id;
            console.log(`Game initialized with ID: ${gameState.gameId}`);
            if (gameState.mode != "One Player" && gameState.mode != "Two Players (hot seat)") {
                startTimer();
                updateGameState(message.data);
            }
            break;
        case "reset":
            gameState.gameId = message.game_id;
            console.log(`Game in reset with ID: ${gameState.gameId}`);
            break;
        case "update":
            updateGameState(message.data);
            break;
        case "end":
            showEndMenu(`${message.reason}`);
            if (gameState.mode != "8" && gameState.mode != "4")
                returnToStartMenu();
            else
                returnToTournamentWaitingRoom();
            break;
        case "game_end":
            showEndMenu(`${message.reason}`);
            if (gameState.mode != "8" && gameState.mode != "4")
                returnToStartMenu();
            else
                returnToTournamentWaitingRoom();
            break;
        case "match_found":
            console.log("(FRONTEND) Match found:", message.game_id);
            break;
        case 'match_start':
            // gameState.gameId = message.game_id;
            // console.log(`Game initialized with ID: ${gameState.gameId}`);
            document.getElementById("tournamentBracket").style.display = "none";
            document.getElementById("tournamentBracket4").style.display = "none";
            instructions3.style.display = "block";
            gameState.running = false; // right??
            startGameMenu();
            break;
        case "tournament_update":
            console.log(`MESSAGE COMING IN`); // to rm
            break;
        case "update_tournament":
            console.log(`Players in tournament: ${message.players_in}`); // to rm
            console.log(`Remaining spots: ${message.remaining_spots}`); // to rm
            break;
        case "end_tournament":
            returnToStartMenuAfterTournament();
            break;
        // default:
        //     console.warn("Unknown message type received:", message.type);
    }
}
