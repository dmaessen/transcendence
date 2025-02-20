const websocket = `ws://${window.location.host}/ws/game_server/`;
const tournamentwebsocket = `ws://${window.location.host}/ws/tournament/`;

let socket;
let reconnecting = false;
let resetting = false;
//let tournamentOpen = false; // switch back to off at some point maybe after xxx minutes or whatever

function connectWebSocket(mode) {
    // if (socket && socket.readyState === WebSocket.OPEN) { // this will go wrong no if we are doing one player then tournament?? dif socket
    //     console.log("WebSocket already connected.");
    //     startGameMenu(); // or not
    //     return;
    // }

    if (reconnecting) {
        console.warn("Reconnection already in progress.");
        return;
    }

    reconnecting = true;
    console.log("Attempting to connect to websocket...");
    if (mode == "4" || mode == "8")
        socket = new WebSocket(tournamentwebsocket);
    else
        socket = new WebSocket(websocket);

    socket.onopen = async() => {
        console.log("Connected to the game server.");
        socket.send(JSON.stringify({ action: "connect", mode: mode }));
        reconnecting = false;
        if (mode != "4" && mode != "8") {
            startGameMenu();
        } else if (mode == "4" || mode == "8") {
            try {
                const data = await fetchData("http://localhost:8080/api/tournament-status/");
                console.log("Fetched tournament status:", data);
                if (data.players_in == 0) {
                    socket.send(JSON.stringify({ action: "start_tournament", mode: mode }));
                    console.log("start_tounrment from connectWebsocket undergoing");
                }
                socket.send(JSON.stringify({ action: "join_tournament", mode: mode }));
                showWaitingRoomTournament(mode);
            } catch (error) {
                console.error("Error fetching tournament status:", error);
            }
            // fetchTournamentStatus();
            // fetch("http://localhost:8080/api/tournament-status/") // without /api here
            //     .then(response => response.json())
            //     .then(data => {
            //         console.log("Fetched tournament status:", data);
            //         if (data.players_in == 0) {
            //             socket.send(JSON.stringify({ action: "start_tournament", mode: mode }));
            //             console.log("start_tounrment from connectWebsocket undergoing");
            //         }
            //         socket.send(JSON.stringify({ action: "join_tournament", mode: mode }));
            //         showWaitingRoomTournament(mode);
            //     })
            // .catch(error => console.error("Error fetching tournament status:", error));
        }
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
        console.log(`Disconnected from the game server: ${gameState.playerId}`);
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
    console.log(`(FRONTEND) message.typ here is: ${message.type}`);

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
        case "match_found":
            console.log("(FRONTEND) Match found:", message.game_id);
            break;
        case 'match_start':
            gameState.gameId = message.game_id;
            console.log(`Game initialized with ID: ${gameState.gameId}`);
            startGameMenu();
            //gameState.running = true;
            break;
        // case "tournament_status": // needed
        //     if (message.active) {
        //         tournamentBanner.style.display = "block";
        //         setTimeout(() => {
        //             tournamentBanner.style.display = "none";
        //         }, 20000); // 20sec
        //     }
        //     break;
        // case "match_result":
        //     // ADD STUFF
        //     break;
        case "tournament_full":
            //tournamentOpen = false;
            break;
        case "update_tournament":
            console.log(`Players in tournament: ${message.players_in}`); // to rm
            console.log(`Remaining spots: ${message.remaining_spots}`); // to rm
            // if (message.remaining_spots > 0) {
            //showTournamentAdBanner(message.players_in, message.remaining_spots + message.players_in);
            // } else {
            //     tournamentBanner.style.display = "none";
            // }
            break;
        case "tournament_end":
            // show the overall winner
            break;
        // default:
        //     console.warn("Unknown message type received:", message.type);
    }
}
