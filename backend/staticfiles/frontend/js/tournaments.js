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
    headerRow.innerHTML = "<th>Tournament date</th><th>Winner</th>";
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

async function loadAllTournaments(userID) {
    try {
        const response = await fetch(`/data/api/userAllTournaments/?userID=${userID}`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
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
        } else {
            console.error("Data.tournaments is not an array:", data.tournaments);
        }
    } catch (error) {
        console.error("Error fetching tournament data:", error);
    }
}

const allTournamentsLink = document.querySelector('[data-bs-toggle="modal"][data-bs-target="#allTournamentsModal"]');
if (allTournamentsLink) {
    allTournamentsLink.addEventListener("click", function() {
        const userID = document.getElementById("AllTournamentsModal").dataset.userId;
        console.log("heeeeeey!!");
        loadAllTournaments(userID);
    });
}

const closeAllTournamentsBtn = document.getElementById("closeAllTournamentsBtn");
if(closeAllTournamentsBtn){
    closeAllTournamentsBtn.addEventListener("click", function() {
        console.log("profile close clicked");
        const allTournamentsModalElement = document.getElementById("allTournamentsModal");
        const allTournamentsModal = bootstrap.Modal.getInstance(allTournamentsModalElement);
        allTournamentsModal.hide();
        const profileModalElement = document.getElementById("profileModal");
        const profileModal = bootstrap.Modal.getInstance(profileModalElement);
        profileModal.show();
    });
}