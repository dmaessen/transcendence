//const serverUrl = "ws://localhost:8000/ws/game_server/";
const websocket = `ws://${window.location.host}/ws/game_server/`;
const tournamentwebsocket = `ws://${window.location.host}/ws/tournament/`;

let socket;
let reconnecting = false;
let resetting = false;

function connectWebSocket(mode) {
    if (socket && socket.readyState === WebSocket.OPEN) { // this will go wrong no if we are doing one player then tournament?? dif socket
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
    if (mode == "Tournament - 4 Players" || mode == "Tournament - 8 Players")
        socket = new WebSocket(tournamentwebsocket);
    else
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

function resetGame(mode) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "reset", gameId: gameState.gameId, mode }));
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
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
        await sleep(500);
        socket.close();
    }
    gameMenuFirst.show();
}

function handleServerMessage(message) {
    const tournamentBanner = document.getElementById("tournamentBanner");
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
        case "tournament_status": // needed
            if (message.active) {
                tournamentBanner.style.display = "block";
                setTimeout(() => {
                    tournamentBanner.style.display = "none";
                }, 20000); // 20sec
            }
            break;
        case "match_found":
            console.log("Tournament match found:", message.game_id);
            startGame(message.game_id); // Your existing game logic -- CHECK ON THIS
            break;
        case "match_result":
            // ADD STUFF
            break;
        case "update_tournament":
            document.getElementById("playersInTournament").textContent = `${message.players_in}/${message.remaining_spots + message.players_in}`;
            if ((message.players_in == 4 && message.mode == "Tournament - 4 Players") 
                || (message.players_in == 8 && message.mode == "Tournament - 8 Players")) {
                tournamentBanner.style.display = "none";
                socket.send(JSON.stringify({ action: "start_tournament" }));
            }
            break;
        case "tournament_end":
            // ADD STUFF
            break;
        // default:
        //     console.warn("Unknown message type received:", message.type);
    }
}

