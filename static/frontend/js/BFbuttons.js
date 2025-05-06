let currentModal;

window.addEventListener("popstate", (event) => {
    const state = event.state;
    if (!state) return;

    // Close all modals
    document.querySelectorAll(".modal.show").forEach(modalEl => {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    });

    console.log('Pop:', event.state);

    switch(state.modalID) {
        case "profileModal":
            loadProfile(state.userID, true, false);
            currentModal = "profileModal";
            break;
        case "editProfileModal":
            if (currentModal !== "editProfileModal") {
                profileModal.hide();
                editProfileModal.show();
                currentModal = "editProfileModal";
            }
            break;
        case "AllMatchesModal":
            loadAllMatches(state.userID, false);
            currentModal = "AllMatchesModal";
            break;
        case "AllTournamentsModal":
            loadAllTournaments(state.userID, false);
            currentModal = "AllTournamentsModal";
            break;
        case "friendsModal":
            loadFriends(false);
            currentModal = "friendsModal";
            break;
        case "addFriendsModal":
            loadFriendsRequests(false);
            currentModal = "addFriendsModal";
            break;
        case "gameMenu":
            if (currentModal !== "gameMenu") {
                gameMenu.hide();
                gameMenuFirst.show();
                currentModal = "gameMenu";
            }
            break;
        case "gameMenuTournament":
            if (currentModal !== "gameMenuTournament") {
                gameMenuTournament.hide();
                gameMenu.show();
                currentModal = "gameMenuTournament";
            }
            break;
        case "SignInMenu":
            break;
        default:
            console.warn("Unknown modalID:", state.modalID);
            break;
    }
});

document.querySelectorAll(".modal-pop-close").forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.preventDefault();  // optional, in case it's inside a form
        history.back();      // this will trigger your onpopstate logic
    });
});
