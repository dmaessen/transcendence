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
    try {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        
        if (mode == "4" || mode == "8")
            websocket = new WebSocket(`${protocol}://${window.location.host}/ws/tournament/`);
            // websocket = new WebSocket(`ws://${window.location.host}/ws/tournament/`);
            // websocket = new WebSocket(`ws://${window.location.host}?token=${token}`);
        else
            websocket = new WebSocket(`${protocol}://${window.location.host}/ws/game_server/`);
            // websocket = new WebSocket(`ws://${window.location.host}/ws/game_server/`);
            // websocket = new WebSocket(`ws://${window.location.host}/ws/game_server/?token=${token}`);
    
        websocket.onopen = async() => {
            console.log("Connected to the game server.");
            websocket.send(JSON.stringify({ action: "connect", mode: mode }));
            reconnecting = false;
            if (mode != "4" && mode != "8") {
                startGameMenu();
            } else if (mode == "4" || mode == "8") {
                try {
                    const data = await fetchData("/tournament-status/");
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
    } catch(error){
        console.error("Failed to create WebSocket:", error);
    }
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
    currentModal = "gameMenuFirst";
    gameMenuFirst.show();
    history.pushState({ modalID: "gameMenuFirst" }, "", "?modal=gameMenuFirst");
}

const returnToTournamentWaitingRoom = async (message) => {
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    instructions3.style.display = "none";
    gameCanvas.style.display = "none";
    gameTitle.style.display = "none";
    if (websocket && websocket.readyState === WebSocket.OPEN)
        websocket.send(JSON.stringify({ action: "disconnect_1v1game", mode: gameState.mode, game_id: gameState.gameId }));
    showWaitingRoomTournament(gameState.mode);
}

function addWinnersTournament(message) {
    console.log(`MADE IT HERE TO ADD_WINNERS ----- V2`); // to rm
    if (gameState.mode == "4") {
        if (message.winners.length === 2) {
            winners4 = JSON.parse(localStorage.getItem("winners4")) || [];
            for (let i = 0; i < 2; i++) {
                let username = message.winners[i];
                if (!winners4.includes(username)) {
                    winners4.push(username);
                }
            }
            localStorage.setItem("winners4", JSON.stringify(winners4));
        }
        else if (message.winners.length === 1) {
            winner_final = JSON.parse(localStorage.getItem("winner_final")) || [];
            let username = message.winners[0];
            if (!winner_final.includes(username)) {
                winner_final.push(username);
                localStorage.setItem("winner_final", JSON.stringify(winner_final));
            }
        }
    } 
    else {
        if (message.round == 1) {
            winners8 = JSON.parse(localStorage.getItem("winners8")) || [];
            for (let i = 0; i < 4; i++) {
                let username = message.winners[i];
                if (!winners8.includes(username)) {
                    winners8.push(username);
                }
            }
            localStorage.setItem("winners8", JSON.stringify(winners8));
        } else if (message.round == 2) {
            winners8_final = JSON.parse(localStorage.getItem("winners8_final")) || [];
            for (let i = 0; i < 4; i++) {
                let username = message.winners[i];
                if (!winners8_final.includes(username)) {
                    winners8_final.push(username);
                }
            }
            localStorage.setItem("winners8_final", JSON.stringify(winners8_final));
        } else if (message.round === 1) {
            winner_final = JSON.parse(localStorage.getItem("winner_final")) || [];
            let username = message.winners[0];
            if (!winner_final.includes(username)) {
                winner_final.push(username);
                localStorage.setItem("winner_final", JSON.stringify(winner_final));
            }
        }
    }
}

const returnToStartMenuAfterTournament = async () => {
    await sleep(1000);
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    instructions3.style.display = "none";
    gameCanvas.style.display = "none";
    gameTitle.style.display = "none";
    document.getElementById("tournamentBracket4").style.display = "none";
    document.getElementById("tournamentBracket").style.display = "none";
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        await sleep(500);
        websocket.close();
    }
    currentModal = "gameMenuFirst";
    gameMenuFirst.show();
    history.pushState({ modalID: "gameMenuFirst" }, "", "?modal=gameMenuFirst");
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
        case "trigger_auto_start":
            websocket.send(JSON.stringify({ action: "ready", mode: gameState.mode }));
            break;
        case "end":
            showEndMenu(`${message.reason}`);
            if (gameState.mode != "8" && gameState.mode != "4")
                returnToStartMenu();
            else
                returnToTournamentWaitingRoom(message);
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
            document.getElementById("tournamentBracket").style.display = "none";
            document.getElementById("tournamentBracket4").style.display = "none";
            instructions3.style.display = "block";
            gameState.running = false;
            startGameMenu();
            break;
        case "tournament_update":
            console.log(`MESSAGE COMING IN`); // to rm
            break;
        case "update_tournament":
            console.log(`Players in tournament: ${message.players_in}`);
            console.log(`Remaining spots: ${message.remaining_spots}`);
            break;
        case "end_tournament":
            returnToStartMenuAfterTournament();
            break;
        case "add_winners":
            addWinnersTournament(message);
            break;
        case "join_tournament":
            document.getElementById("tournamentBtn").textContent = "Join tournament";
            joinTournament(data);
        case "ongoing_tournament":
            btn = document.getElementById("tournamentBtn");
            btn.textContent = "Ongoing tournament"
            btn.disable() = true;
        // default:
        //     console.warn("Unknown message type received:", message.type);
    }
}
