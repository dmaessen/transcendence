window.addEventListener("popstate", (event) => {
    const state = event.state;
    if (!state) return;

    // Close all currently open modals
    document.querySelectorAll(".modal.show").forEach(modalEl => {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    });
    
    const gameMode = state.gameMode;
    console.log("Game mode from state:", gameMode);
    // Clean canvas leftovers
    if(currentModal = game) {
        gameCanvas.style.display = "none";
        instructions1.style.display = "none";
        instructions2.style.display = "none";
        document.getElementById("tournamentBracket").style.display = "none"; // this working??
        document.getElementById("tournamentBracket4").style.display = "none"; // this working??
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            if (gameState.mode != "Tournament - 4 Players" && gameState.mode != "Tournament - 8 Players" && gameState.mode != "4" && gameState.mode != "8")
                websocket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
            else 
                websocket.send(JSON.stringify({ action: "disconnect"}));
            websocket.close();
        }
    }

    // Remove leftover backdrop
    document.body.classList.remove("modal-open");
    document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());

    console.log('Pop:', state.modalID);

    switch(state.modalID) {
        case "profileModal":
            loadProfile(state.userID, true, false);
            break;
        case "editProfileModal":
            profileModal.hide();
            editProfileModal.show();
            break;
        case "AllMatchesModal":
            loadAllMatches(state.userID, false);
            break;
        case "AllTournamentsModal":
            loadAllTournaments(state.userID, false);
            break;
        case "friendsModal":
            loadFriends(false);
            break;
        case "addFriendsModal":
            loadFriendsRequests(false);
            break;
        case "gameMenu":
            gameMenu.show();
            break;
        case "gameMenuTournament":
            gameMenuTournament.show();
            break;
        case "gameMenuFirst":
            gameMenuFirst.show();
            break;
        case "SignInMenu":
            SignInMenu.show(); // If applicable
            break;
        case "fourPlayersTournament":
        case "eightPlayersTournament":
        case "onePlayer":
        case "twoPlayers":
        case "twoPlayersRemote":
            startGame(gameMode);
            break;
        default:
            console.warn("Unknown modalID:", state.modalID);
            break;
    }
});
//TODO not go back further than the main menu if logged 
//TODO go back from game logic outside modal