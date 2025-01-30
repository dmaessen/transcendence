//const serverUrl = "ws://localhost:8000/ws/game_server/";
const websocket = `ws://${window.location.host}/ws/game_server/`;
const tournamentWebsocket = `ws://${window.location.host}/ws/tournament/`;

let socket;
let tournamentsocket;
let reconnecting = false;
let resetting = false;

function connectWebSocket(mode) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log("WebSocket already connected.");
        startGameMenu(); // or not
        return;
    }

    if (reconnecting) {
        console.warn("Reconnection already in progress.");
        return;
    }

    reconnecting = true;
    console.log("Attempting to connect to websocket...");
    socket = new WebSocket(websocket);

    socket.onopen = () => {
        console.log("Connected to the game server.");
        socket.send(JSON.stringify({ action: "connect", mode: mode }));
        reconnecting = false;
        startGameMenu();

        // if (mode === "Tournament - 4 Players" || mode === "Tournament - 8 Players") // check what to do to make this banner work
        //     socket.send(JSON.stringify({ action: "start_tournament" })); // but we also need to turn this off
    };

    socket.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleServerMessage(message);
        } catch (error) {
            console.error("Error parsing WebSocket message:", error, event.data);
        }
    };

    socket.onclose = () => {
        console.log("Disconnected from the game server.");
        reconnecting = false;
        //setTimeout(() => connectWebSocket(mode), 2000); // reconnects after 2 seconds
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        alert(`WebSocket error: ${error.message}`);
        reconnecting = false;
    };
}

function connectTournamentWebSocket(mode) {
    if (tournamentsocket && tournamentsocket.readyState === WebSocket.OPEN) {
        console.log("(Tournament) WebSocket already connected.");
        //startGameMenu(); // or not
        return;
    }

    console.log("(Tournament) Attempting to connect to websocket...");
    tournamentsocket = new WebSocket(tournamentWebsocket);

    tournamentsocket.onopen = () => {
        console.log("(Tournament) Connected to the game server.");
        if (mode === "Tournament - 4 Players") {
            tournamentsocket.send(JSON.stringify({ action: "connect", mode: 4 }));
            tournamentsocket.send(JSON.stringify({ action: "start_tournament", mode: 4 }));
        } else if (mode === "Tournament - 8 Players") {
            tournamentsocket.send(JSON.stringify({ action: "connect", mode: 8 }));
            tournamentsocket.send(JSON.stringify({ action: "start_tournament", mode: 8 }));
        }
        //startGameMenu();
    };

    tournamentsocket.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleServerMessage(message);
        } catch (error) {
            console.error("(Tournament) Error parsing WebSocket message:", error, event.data);
        }
    };

    tournamentsocket.onclose = () => {
        console.log("(Tournament) Disconnected from the game server.");
        //setTimeout(() => connectWebSocket(mode), 2000); // reconnects after 2 seconds
    };

    tournamentsocket.onerror = (error) => {
        console.error("(Tournament) WebSocket error:", error);
        alert(`(Tournament) WebSocket error: ${error.message}`);
    };
}

function resetGame(mode) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "reset", gameId: gameState.gameId, mode }));
    }
    gameState.running = false;
    displayStartPrompt();
}

const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))

const returnToStartMenu = async () => {
    await sleep(10000); // reduce?
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    gameCanvas.style.display = "none";
    gameTitle.style.display = "none";
    socket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
    socket.close()
    gameMenuFirst.show();
}

function handleServerMessage(message) {
    switch (message.type) {
        case "started":
            gameState.gameId = message.game_id;
            console.log(`Game initialized with ID: ${gameState.gameId}`);
            gameState.running = true;
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
            returnToStartMenu();
            break;
        case "tournament_status":
            const banner = document.getElementById("tournamentBanner");
            if (data.active) {
                banner.style.display = "block";
                setTimeout(() => {
                    banner.style.display = "none";
                }, 20000); // 20sec
            }
        case "match_found":
            console.log("Tournament match found:", data.game_id);
            startGame(data.game_id); // Your existing game logic -- CHECK ON THIS
        // default:
        //     console.warn("Unknown message type received:", message.type);
    }
}

