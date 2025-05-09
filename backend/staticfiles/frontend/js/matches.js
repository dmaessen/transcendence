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
            loadProfile(opponentLink.dataset.userID);
        });
        opponentCell.appendChild(opponentLink);
        row.appendChild(opponentCell);
        
        allMatchesTable.appendChild(row);
    });
}

async function loadAllMatches(userID) {
    try {
        const response = await fetch(`/data/api/allUserMatches/?userID=${userID}`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
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
        } else {
            console.error("Data.matches is not an array:", data.matches);
        }
    } catch (error) {
        console.error("Error fetching matches data:", error);
    }
}

const allMatchesLink = document.querySelector('[data-bs-toggle="modal"][data-bs-target="#allMatchesModal"]');
if (allMatchesLink) {
    allMatchesLink.addEventListener("click", function() {
        const userID = document.getElementById("AllMatchesModal").dataset.userId;
        loadAllMatches(userID);
    });
}

const closeAllMatchesBtn = document.getElementById("closeAllMatchesBtn");
if(closeAllMatchesBtn){
    closeAllMatchesBtn.addEventListener("click", function() {
        console.log("profile close clicked");
        const allMatchesModalElement = document.getElementById("allMatchesModal");
        const allMatchesModal = bootstrap.Modal.getInstance(allMatchesModalElement);
        allMatchesModal.hide();
        const profileModalElement = document.getElementById("profileModal");
        const profileModal = bootstrap.Modal.getInstance(profileModalElement);
        profileModal.show();
    });
}