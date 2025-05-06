window.addEventListener("popstate", (event) => {
    const state = event.state;
    if (!state) return;

    // Close all currently open modals
    document.querySelectorAll(".modal.show").forEach(modalEl => {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    });

    // Clean canvas leftovers
    gameCanvas.style.display = "none";
    instructions1.style.display = "none";
    instructions2.style.display = "none";
    const gameMode = state.gameMode;

    console.log("Game mode from state:", gameMode);

    // Optionally remove leftover backdrop
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
            exitGame();
            break;
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