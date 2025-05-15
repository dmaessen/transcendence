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
let playerCount = 4;

instructions1.style.display = "none";
instructions2.style.display = "none";
instructions3.style.display = "none";

const gameMenuFirst = new bootstrap.Modal(gameMenuElementFirst, { backdrop: "static", keyboard: false, });
const gameMenu = new bootstrap.Modal(gameMenuElement, { backdrop: "static", keyboard: false, });
const gameMenuTournament = new bootstrap.Modal(gameMenuElementTournament, { backdrop: "static", keyboard: false, });
const SignInMenu = new bootstrap.Modal(signInMenuElement, { backdrop: "static", keyboard: false, });

const gameState = { 
    mode: null,
    gameId: null,
    players: [],
    running: false,
    playerId: null,
};

const gameModeTexts = document.getElementById("gameModeTexts");
const onePlayerText = gameModeTexts.dataset.one;
const hotseatText = gameModeTexts.dataset.hotseat;
const remoteText = gameModeTexts.dataset.remote;

function startGame(mode, usernames=null) {
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
        gameTitle.textContent = onePlayerText; // "One Player"
        instructions1.style.display = "block";
        connectWebSocket(mode);
    } if (mode === "Two Players (hot seat)") {
        gameTitle.textContent = hotseatText; // "Two Players (hot seat)"
        instructions2.style.display = "block";
        connectWebSocket(mode);
    } if (mode === "Two Players (remote)") {
        gameTitle.textContent = remoteText; // "Two Players (remote)"
        instructions1.style.display = "block";
        connectWebSocket(mode);
    } if (mode === "Tournament - 4 Players" || mode === "Tournament - 8 Players") {
        gameMenuTournament.hide();
        if (mode === "Tournament - 4 Players")
            connectWebSocket(4, usernames);
        else
            connectWebSocket(8, usernames);
    }
}

document.getElementById("playBtn").addEventListener("click", async() => {
    console.log("calling select btn!");
    await selectTournamentBtn();
    gameMenu.show();
    currentModal = "gameMenu";
    history.pushState({ modalID: "gameMenu" }, "", "?modal=gameMenu");
});

document.getElementById("onePlayerBtn").addEventListener("click", () => {
    startGame("One Player");
    currentModal = "game";
    const mode = "One Player";
    const encodedMode = encodeURIComponent(mode);
    history.pushState({ modalID: "onePlayer", gameMode: mode }, "", `?modal=onePlayer&type=${encodedMode}`);
});

document.getElementById("twoPlayersBtn").addEventListener("click", () => {
    startGame("Two Players (hot seat)");
    currentModal = "game";
    const mode = "Two Players (hot seat)";
    const encodedMode = encodeURIComponent(mode);
    history.pushState({ modalID: "twoPlayers", gameMode: mode }, "", `?modal=twoPlayers&type=${encodedMode}`);
});

document.getElementById("twoPlayersRemoteBtn").addEventListener("click", () => {
    startGame("Two Players (remote)");
    currentModal = "game";
    const mode = "Two Players (remote)";
    const encodedMode = encodeURIComponent(mode);
    history.pushState({ modalID: "twoPlayersRemote", gameMode: mode }, "", `?modal=twoPlayersRemote&type=${encodedMode}`);
});

document.getElementById("tournamentBtn").addEventListener("click", () => {
    gameMenuTournament.show();
   
    gameMenu.hide();
    currentModal = "gameMenuTournament";
    history.pushState({ modalID: "gameMenuTournament" }, "", "?modal=gameMenuTournament");
});

document.getElementById("fourPlayersTournamentBtn").addEventListener("click", () => {
    // startGame("Tournament - 4 Players");
    playerCount = 4;
    openUsernameModal();
    // disableTournamentButtons();
    currentModal = "game";
    const mode = "Tournament - 4 Players";
    const encodedMode = encodeURIComponent(mode);
    history.pushState({ modalID: "fourPlayersTournament", gameMode: mode }, "", `?modal=fourPlayersTournament&type=${encodedMode}`);
});

document.getElementById("eightPlayersTournamentBtn").addEventListener("click", () => {
    // startGame("Tournament - 8 Players");
    playerCount = 8;
    openUsernameModal();
    // disableTournamentButtons();
    currentModal = "game";
    const mode = "Tournament - 8 Players";
    const encodedMode = encodeURIComponent(mode);
    history.pushState({ modalID: "eightPlayersTournament", gameMode: mode }, "", `?modal=eightPlayersTournament&type=${encodedMode}`);
});

document.getElementById("previousBtn").addEventListener("click", () => {
    history.back();
});

document.getElementById("previous2Btn").addEventListener("click", () => {
    history.back();
});

function exitGame(){
    keyboardEnabled = false;
    gameState.running = false;
    stopTimer();
    document.getElementById("timer").innerHTML = " ";
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    gameCanvas.style.display = "none";
    gameTitle.style.display = "none";
    document.getElementById("tournamentBracket").style.display = "none";
    document.getElementById("tournamentBracket4").style.display = "none";
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        if (gameState.mode != "Tournament - 4 Players" && gameState.mode != "Tournament - 8 Players" && gameState.mode != "4" && gameState.mode != "8")
            websocket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
        else 
            websocket.send(JSON.stringify({ action: "disconnect"}));
        websocket.close();
    }
}

document.getElementById("exitButton").addEventListener("click", () =>  {
    exitGame();
    history.back();
    // gameMenuFirst.show();
    // currentModal = "gameMenuFirst";
    // history.pushState({ modalID: "gameMenuFirst" }, "", "?modal=gameMenuFirst");
});

async function joinTournament(data){
    document.querySelectorAll('.modal.show').forEach(modal => {
        bootstrap.Modal.getInstance(modal)?.hide();
    });

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

tournamentBanner.addEventListener("click", async(event) => {
    event.preventDefault();
    try {
        const data = await fetchData("/tournament-status/");
        console.log("Tournament Status:", data);
        if (data.remaining_spots > 0) {
            joinTournament(data);
        }
    } catch (error) {
        console.error("Error fetching tournament status:", error);
    }
});

// When the user selects from the dropdown
document.getElementById("languageDropdown").addEventListener("change", async (e) => {
    e.preventDefault(); // prevent default form submission
    const loggedin = await checkLoginStatus();
    if (loggedin === true) {
        localStorage.setItem("manualLangSelection", "true");
        console.log("ITS TRUE I AM LOGGED IN");
    }

    // Submit the form *after* localStorage is set
    document.getElementById("language-switch-form").submit();
});


function applyPreferredLanguageAfterLogin() {
    const manuallySelected = localStorage.getItem("manualLangSelection");
    console.log("HEEEEEY ", manuallySelected);
    if (manuallySelected) {
        console.log("LAAAAAAA");
        if (manuallySelected === "true") {
            console.log("LOOOOOOO");
            localStorage.setItem("manualLangSelection", "false");
            return ;
        } else if (manuallySelected === "false") {
            console.log("LIIIIIII");
            getUserPreferredLanguage(); // from server or cookie
        }
    } else {
        console.log("LEEEEEEEE");
        getUserPreferredLanguage(); // from server or cookie
    }
}

function getUserPreferredLanguage() {
    console.log("GETTING HERE AFTER LOGIN -- GAME.JS"); // to rm
    // Check if the page has already been reloaded for language change
    fetch('/data/api/get_profile/', {
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to fetch user profile");
        return response.json();
    })
    .then(data => {
        if (data.preferred_language) {
            const currentLanguage = document.documentElement.lang; // Get current language from <html lang="...">
            console.log("Current language:", currentLanguage);
            console.log("Preferred language:", data.preferred_language);
            if (currentLanguage === data.preferred_language) {
                console.log("Preferred language already applied, skipping reload.");
                return;
            }
            console.log("Applying preferred language via set_language:", data.preferred_language);
            
            return fetch("/i18n/setlang/", {
                method: "POST",
                credentials: 'include',
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: `language=${data.preferred_language}&next=/`
            }).then(() => {
                location.reload();
            });
        } else {
            // gameMenuFirst.show();
        }
    })
    .catch(error => {
        console.error("Error loading preferred language:", error);
        // gameMenuFirst.show(); // Fall back to showing the modal even on failure
    });
}

function showTournamentAdBanner(players_in, total_spots) { // Show banner to promote for other players
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
    tournamentBanner.style.display = "none";
    document.getElementById("timer").style.display = "none";
    gameTitle.style.display = "none";
    gameCanvas.style.display = "none";

    drawBracket(mode);
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
    const startPromptText = document.getElementById("startPromptText").textContent.trim();

    gameCanvas.style.display = "block";
    gameContext.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
    gameContext.font = "50px Courier New";
    gameContext.fillStyle = "#000000";
    gameContext.fillRect(gameCanvas.width / 2 - 350, gameCanvas.height / 2 - 48, 700, 100);
    gameContext.fillStyle = "#ffffff";
    gameContext.textAlign = "center";
    gameContext.fillText(startPromptText, gameCanvas.width / 2, gameCanvas.height / 2 + 15);
    // gameContext.fillText("Press any key twice to start", gameCanvas.width / 2, gameCanvas.height / 2 + 15);
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
    if (gameState.mode != "One Player" && gameState.mode != "Two Players (hot seat)"  && gameState.mode != "4" && gameState.mode != "8") {
        if (!gameState.running && websocket && websocket.readyState === WebSocket.OPEN) {
            console.log("Key pressed, 'ready' state, waiting for the other player to start the game...");
            websocket.send(JSON.stringify({ action: "ready", mode: gameState.mode }));
        }
    }
    else {
        if (!gameState.running && websocket && websocket.readyState === WebSocket.OPEN) {
            console.log("Key pressed. Starting the game...");
            gameState.running = true;
            websocket.send(JSON.stringify({ action: "start", mode: gameState.mode, game_id: gameState.gameId }));
            startTimer();
        }
    }
});

const pressedKeys = new Set();
document.addEventListener("keydown", (event) => { 
    if (gameState.running) {
        pressedKeys.add(event.key);
    }
});
document.addEventListener("keyup", (event) => { 
    if (gameState.running) {
        pressedKeys.delete(event.key);
    }
});
setInterval(() => {
    if (!gameState.running)
        return;

    let directions = [];
    if (gameState.mode != "Two Players (hot seat)" && gameState.mode != "4" && gameState.mode != "8") {
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




// ----------------------------------- NEW ---------------------------------------

function openUsernameModal() {
    const firstModal = bootstrap.Modal.getInstance(document.getElementById('gameMenuTournament'));
    if (firstModal) firstModal.hide();

    const container = document.getElementById('usernameFieldsContainer');
    container.innerHTML = '';
    for (let i = 0; i < playerCount; i++) {
        container.innerHTML += `
        <div class="mb-3">
            <input type="text" class="form-control username-input" placeholder="Username ${i + 1}" data-index="${i}">
            <div class="form-text text-danger d-none" id="user-error-${i}">User not found</div>
        </div>
        `;
    }

    const usernameModal = new bootstrap.Modal(document.getElementById('tournamentUsernameModal'));
    usernameModal.show();
}

document.getElementById('tournamentUserForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const inputs = document.querySelectorAll('.username-input');
    let allValid = true;

    for (let input of inputs) {
        const index = input.dataset.index;
        const username = input.value.trim();
        const errorEl = document.getElementById(`user-error-${index}`);

        if (!username) {
            input.classList.add('is-invalid');
            errorEl.textContent = 'Username required';
            errorEl.classList.remove('d-none');
            allValid = false;
            continue;
        }

        // checks backend
        const res = await fetch(`data/api/searchUser/?friendUsername=${username}`, {
            method: "GET",
            credentials: "include",
            headers: {
            },
        });
        const data = await res.json();

        if (!res.ok) {
            throw new Error(`Error, status: ${res.status}`);
        }

        if (data.user_id !== null) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            errorEl.classList.add('d-none');
        } else {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
            errorEl.textContent = 'User not found';
            errorEl.classList.remove('d-none');
            allValid = false;
        }
    }

    if (allValid) {
        // ✅ All usernames are valid — proceed to tournament logic
        const usernames = Array.from(inputs).map(input => input.value.trim());
        console.log('Valid usernames:', usernames);
        if (usernames.length == 4)
            startGame("Tournament - 4 Players", usernames);
            // connectWebSocket("4", usernames);
        else if (usernames.length == 8)
            startGame("Tournament - 8 Players", usernames);
        // const usernameModal = new bootstrap.Modal(document.getElementById('tournamentUsernameModal'));
        // usernameModal.hide();
    }
});
