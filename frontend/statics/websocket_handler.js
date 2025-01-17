//const serverUrl = "ws://localhost:8000/ws/game_server/";
const wsUrl = `ws://${window.location.host}/ws/game_server/`;

let socket;
let reconnecting = false;
let resetting = false;

function connectWebSocket(mode) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log("WebSocket already connected.");
        return;
    }

    if (reconnecting) {
        console.warn("Reconnection already in progress.");
        return;
    }

    reconnecting = true;
    console.log("Attempting to connect to websocket...");
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("Connected to the game server.");
        reconnecting = false;
        startGameMenu();
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
        alert("Connection to the game server lost.");
        reconnecting = false;
        //location.reload();
        setTimeout(() => connectWebSocket(mode), 2000); // Reconnect after 2 seconds
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        alert(`WebSocket error: ${error.message}`);
        reconnecting = false;
    };
}

function sendPlayerAction(action, data) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        if (!gameState.gameId) {
            console.warn("No game ID available. Cannot send action.");
            return;
        }
        socket.send(JSON.stringify({ action, game_id: gameState.gameId, data, }));
    } else {
        console.warn("WebSocket is not open. Unable to send data.");
    }
}

function resetGame(mode) {
    console.log("---- in restGame() ------"); // to rm
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "reset", gameId: gameState.gameId, mode }));
    }
    gameState.running = false;
    displayStartPrompt();
}

function handleServerMessage(message) {
    switch (message.type) {
        case "started": // to rm
            gameState.gameId = message.game_id;
            console.log(`Game initialized with ID: ${gameState.gameId}`);
            gameState.running = true;
            break;
        case "reset":
            gameState.gameId = message.game_id;
            console.log(`RESTING GAME Game initialized with ID: ${gameState.gameId}`);
            break;
        case "update":
            updateGameState(message.data);
            break;
        case "end":
            showEndMenu(`Game Over: ${message.reason}`);
            //alert(`Game Over: ${message.reason}`);
            break;
        default:
            console.warn("Unknown message type received:", message.type);
    }
}
