// Forces page reload when modal is opened but user is not logged in
const modals = document.querySelectorAll(".modal");
modals.forEach(modal => {
    modal.addEventListener("show.bs.modal", async function () {
        const isLoggedIn = await checkLoginStatus();
        if (!isLoggedIn && modal.id !== "SignInMenu") {
            window.location.reload();
        }
    });
});

window.addEventListener("beforeunload", () => {
    if (socket && socket.readyState === WebSocket.OPEN && socket !== loginsocket) {
        console.log("Closing WebSocket before page unload.");
        gameState.running = false;
        stopTimer();
        instructions1.style.display = "none";
        instructions2.style.display = "none";
        gameCanvas.style.display = "none";
        gameTitle.style.display = "none";
        socket.send(JSON.stringify({ action: "disconnect", mode: gameState.mode, game_id: gameState.gameId }));
        socket.close()
    }
    if (checkLoginStatus) {
        SignInMenu.show();
    } else {
        currentModal = "gameMenuFirst";
        gameMenuFirst.show();
        history.pushState({ modalID: "gameMenuFirst" }, "", "?modal=gameMenuFirst");
    }
    // localStorage.removeItem("manualLangSelection");
});

window.addEventListener("load", async () => {
    loggedin = await checkLoginStatus();
    console.log("loggedin: ", loggedin);

    if (loggedin) {
        if (!loginsocket || loginsocket.readyState !== WebSocket.OPEN) {
            await loginWebSocket();
        }
        applyPreferredLanguageAfterLogin();
        currentModal = "gameMenuFirst";
        gameMenuFirst.show();
        history.pushState({ modalID: "gameMenuFirst" }, "", "?modal=gameMenuFirst");
        try {
            const bracketElement = document.getElementById("tournamentBracket");
            bracketElement.style.display = "none";
            const data = await fetchData("/tournament-status/");
            console.log("Fetched tournament status:", data);
            if (data.remaining_spots > 0 && data.players_in != 0) {
                showTournamentAdBanner(data.players_in, data.players_in + data.remaining_spots);
            }
        } catch (error) {
            console.error("Error fetching tournament status:", error);
        }
    } else {
        SignInMenu.show();
    }
});
