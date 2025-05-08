const allMatchesModalElement = document.getElementById("allMatchesModal");
const allMatchesModal = new bootstrap.Modal(allMatchesModalElement);

function populateAllMatches(data) {
    // console.log("populateMatches data: ", data);
    if (!Array.isArray(data)) {
        console.error("Provided data is not an array:", data);
        return;
    }

    // Clear existing rows
    allMatchesTable.innerHTML = "";

    // Create a table head and append headers
    let thead = allMatchesTable.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        allMatchesTable.appendChild(thead);
    }
    let headerRow = document.createElement("tr");
    headerRow.innerHTML = "<th>Match date</th><th>Winner</th><th>Opponent</th>";
    thead.appendChild(headerRow);

    //Populate
    data.forEach(item => {
        const row = document.createElement("tr");

        const dateCell = document.createElement("td");
        dateCell.textContent = item.match_start || "N/A";
        row.appendChild(dateCell);
        
        const winnerCell = document.createElement("td");
        if (item.opponent === item.winner_name) {
            const winnerLink = document.createElement("span");
            winnerLink.textContent = item.winner_name;
            winnerLink.dataset.userID = item.opponentID;
            winnerLink.style.cursor = "pointer"; // Make it look clickable
            winnerLink.style.color = "gray"; // Make it look like a link

            winnerLink.addEventListener("click", function(){
                // const allMatchesModalElement = document.getElementById("allMatchesModal");
                // const allMatchesModal = bootstrap.Modal.getInstance(allMatchesModalElement);
                allMatchesModal.hide();
                loadProfile(winnerLink.dataset.userID);
            });
            winnerCell.appendChild(winnerLink);
        } else {
            winnerCell.textContent = item.winner_name;
        }
        row.appendChild(winnerCell);

        const opponentCell = document.createElement("td");
        const opponentLink = document.createElement("span");
        opponentLink.textContent = item.opponent;
        opponentLink.dataset.userID = item.opponentID;
        opponentLink.style.cursor = "pointer"; // Make it look clickable
        opponentLink.style.color = "gray"; // Make it look like a link

        opponentLink.addEventListener("click", function(){
            // const allMatchesModalElement = document.getElementById("allMatchesModal");
            // const allMatchesModal = bootstrap.Modal.getInstance(allMatchesModalElement);
            allMatchesModal.hide();
            loadProfile(opponentLink.dataset.userID);
        });
        opponentCell.appendChild(opponentLink);
        row.appendChild(opponentCell);
    
        allMatchesTable.appendChild(row);
    });
}

async function loadAllMatches(userID, push = true) {
    try {
        // const allMatchesModalElement = document.getElementById("allMatchesModal");
        // const allMatchesModal = new bootstrap.Modal(allMatchesModalElement);
        allMatchesModal.show();
        const response = await fetch(`/data/api/allUserMatches/?userID=${userID}`, {
            method: "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`Error, status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Raw response:", data);
        console.log("Matches:", data.matches);

        if (Array.isArray(data.matches)) {
            populateAllMatches(data.matches);
            if(push) {
                const state = { modalID: "AllMatchesModal", userID: userID };
                const url = `?modal=AllMatchesModal&user=${userID}`;
                currentModal = "AllMatchesModal";
                history.pushState(state, '', url);
                console.log("Push: ", state);
            }
        } else {
            console.error("Data.matches is not an array:", data.matches);
        }
    } catch (error) {
        console.error("Error fetching matches data:", error);
    }
}

const allMatchesLink = document.getElementById("AllMatchesModal");
if (allMatchesLink) {
    allMatchesLink.addEventListener("click", function () {
        const userID = document.getElementById("currentUser").dataset.userId;
        loadAllMatches(userID);
    });
}

const closeAllMatchesBtn = document.getElementById("closeAllMatchesBtn");
if(closeAllMatchesBtn){
    closeAllMatchesBtn.addEventListener("click", function() {
        console.log("profile close clicked");
        history.back();
    });
}