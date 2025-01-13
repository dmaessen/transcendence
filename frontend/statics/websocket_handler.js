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
            socket.send(JSON.stringify({action: "start", mode}));
        }
    };

    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleServerMessage(message);
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
            gameState.gameId = message.gameId;
            console.log(`Game initialized with ID: ${gameState.gameId}`);
            updateGameState(message.data);
            break;
        case "update":
            updateGameState(message.data);
            break;
        case "end":
            alert(`Game Over: ${message.reason}`);
            break;
        default:
            console.warn("Unknown message type received:", message.type);
    }
}
