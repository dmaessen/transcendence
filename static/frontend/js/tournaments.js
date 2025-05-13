const allTournamentsModalElement = document.getElementById("allTournamentsModal");
const allTournamentsModal = new bootstrap.Modal(allTournamentsModalElement);

function populateAllTournament(data) {
    console.log("populateTournaments data: ", data);
    if (!Array.isArray(data)) {
        console.error("Provided data is not an array:", data);
        return;
    }

    // Clear existing rows
    allTournamentsTable.innerHTML = "";

    // Create a table head and append headers
    let thead = allTournamentsTable.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        allTournamentsTable.appendChild(thead);
    }
    let headerRow = document.createElement("tr");
    const tText = document.getElementById("text_tournament_date").textContent.trim();
    const wText = document.getElementById("text_winner").textContent.trim();
    headerRow.innerHTML =
        "<th>" + tText + "</th>" +
        "<th>" + wText + "</th>";
    thead.appendChild(headerRow);

    data.forEach(item => {
        // console.log("tournament winer: ", item.winner);
        // console.log("tournamente winnerID: ", item.winnerID);
        console.log("tournament userWon: ", item.userWon);
        const row = document.createElement("tr");

        const dateCell = document.createElement("td");
        dateCell.textContent = item.start_date;
        row.appendChild(dateCell);

        const winnerCell = document.createElement("td");
        if (item.userWon == false) {
            const winnerLink = document.createElement("span");
            winnerLink.textContent = item.winner;
            winnerLink.dataset.userID = item.winnerID;
            winnerLink.style.cursor = "pointer"; // Make it look clickable
            winnerLink.style.color = "gray"; // Make it look like a link

            winnerLink.addEventListener("click", function(){
                // const allTournamentsModalElement = document.getElementById("allTournamentsModal");
                // const allTournamentsModal = bootstrap.Modal.getInstance(allTournamentsModalElement);
                allTournamentsModal.hide();
                loadProfile(winnerLink.dataset.userID);
            });
            winnerCell.appendChild(winnerLink);
        } else {
            winnerCell.textContent = item.winner;
        }

        row.appendChild(winnerCell);
        allTournamentsTable.appendChild(row);
    });
}

async function loadAllTournaments(userID, push = true) {
    try {
        // const allTournamentsModalElement = document.getElementById("allTournamentsModal");
        // const allTournamentsModal = new bootstrap.Modal(allTournamentsModalElement);
        allTournamentsModal.show();
        const response = await fetch(`/data/api/userAllTournaments/?userID=${userID}`, {
            method: "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error, status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Raw response:", data);
        console.log("Tournaments:", data.tournaments);

        if (Array.isArray(data.tournaments)) {
            populateAllTournament(data.tournaments);
            if (push) {
                const state = { modalID: "AllTournamentsModal", userID: userID };
                const url = `?modal=AllTournamentsModal&user=${userID}`;
                currentModal = "AllTournamentsModal";
                history.pushState(state, '', url);
                console.log("Push: ", state);
            }
        } else {
            console.error("Data.tournaments is not an array:", data.tournaments);
        }
    } catch (error) {
        console.error("Error fetching tournament data:", error);
    }
}

const allTournamentsLink = document.getElementById("AllTournamentsModal");
if (allTournamentsLink) {
    allTournamentsLink.addEventListener("click", function () {
        const userID = document.getElementById("currentUser").dataset.userId;
        loadAllTournaments(userID);

    });
}

const closeAllTournamentsBtn = document.getElementById("closeAllTournamentsBtn");
if(closeAllTournamentsBtn){
    closeAllTournamentsBtn.addEventListener("click", function() {
        console.log("profile close clicked");
        history.back();
    });
}