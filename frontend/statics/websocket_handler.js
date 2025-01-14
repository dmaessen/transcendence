//const serverUrl = "ws://localhost:8000/ws/game_server/";
const wsUrl = `ws://${window.location.host}/ws/game_server/`;

let socket;

function connectWebSocket(mode) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log("WebSocket already connected.");
        return;
    }

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("Connected to the game server.");
        //initializeGame(); // Perform any necessary setup
        if (gameState) {
            console.log("WebSocket readyState before sending start:", socket.readyState);
            socket.send(JSON.stringify({ action: "start", mode }));
            console.log("WebSocket message sent to start game.");
        }
        console.log("Connected to the game server #2.");
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
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        alert(`WebSocket error: ${error.message}`);
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

function handleServerMessage(message) {
    switch (message.type) {
        case "started":
            gameState.gameId = message.game_id;
            console.log(`Game initialized with ID: ${gameState.gameId}`);
            //updateGameState(message.data);
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
