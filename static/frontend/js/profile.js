// const dataUrl = "http://localhost:8000/data/";

function addFriend(userID) {
    console.log("addFriend userID: ", userID);
    fetch(`/data/api/addFriend/`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // if needed for authentication
            "Content-Type": "application/json",
        },
        body: JSON.stringify({userID: userID})
    })
    .then(response => {
        if (!response.ok)
            {
            throw new Error(`HTML error, status: ${response.status}`)
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log("Friend added successfully");
        } else {
            console.error("Failed to add friend:", data.error);
        }
    })
    .catch(error => console.log("Error adding a friend: ", error));
}

function deleteFriend(userID) {
    fetch(`data/api/deleteFriend`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // if needed for authentication
            "Content-Type": "application/json",
        },
        body: JSON.stringify({userID: userID})
    })
    .then(response => {
        if (!response.ok)
            {
            throw new Error(`HTML error, status: ${response.status}`)
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log("Friend deleted successfully");
        } else {
            console.error("Failed to delete friend:", data.error);
        }
    })
    .catch(error => console.log("Error deleting a friend: ", error));
}

function populateTournament(data) {
    console.log("populateTournaments data: ", data);
    if (!Array.isArray(data)) {
        console.error("Provided data is not an array:", data);
        return;
    }

    // Clear existing rows
    tournamentsTable.innerHTML = "";

    // Create a table head and append headers
    let thead = tournamentsTable.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        tournamentsTable.appendChild(thead);
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
        tournamentsTable.appendChild(row);
    });
}

function populateMatches(data) {
    // console.log("populateMatches data: ", data);
    if (!Array.isArray(data)) {
        console.error("Provided data is not an array:", data);
        return;
    }

    // Clear existing rows
    matchesTable.innerHTML = "";

    // Create a table head and append headers
    let thead = matchesTable.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        matchesTable.appendChild(thead);
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
        
        matchesTable.appendChild(row);
    });
}

function loadUserData(userID) {
    fetch(`/data/api/userData/?userID=${userID}`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
            "Content-Type": "application/json",
        },
    })
    .then(response => {
        if (!response.ok)
            {
            throw new Error(`HTML error, status: ${response.status}`)
        }
        return response.json();
    })
    .then(data => {
        console.log("loadProfile user data:", data);

        document.getElementById("userAvatar").src = data.avatar;
        document.getElementById("username").textContent = data.username;
        document.getElementById("userEmail").textContent = data.email;
        document.getElementById("btnType").textContent = data.btnType;

        let btnType = document.getElementById("btnType")
        btnType.disabled = false;
        btnType.removeEventListener("click")
        btnType.addEventListener("click", function() {
            if(data.btnType == "Add friend") {
                addFriend(userID);
            }
            else if(data.btnType == "Edit profile"){
                let modal = new bootstrap.Modal(document.getElementById("editProfileModal"));
                modal.show();
            }
            else if(data.btnType == "Delete friend") {
                deleteFriend(userID);
            }
            else if (data.btnType === "Friend request sent") {
                btnType.disabled = true;
            }
        })
    })
    .catch(error => console.error("Error fetching user data:", error));
}

function loadMatchesData(userID) {
    fetch(`/data/api/userMatches/?userID=${userID}`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
            "Content-Type": "application/json",
        },
    }) // Fetch 3 latest matches from user 
    .then(response => {
        if (!response.ok)
            {
            throw new Error(`HTML error, status: ${response.status}`)
        }
        return response.json();
    })
    .then(data => {
        console.log("Raw response:", data);  // Log the whole response
        console.log("Matches:", data.matches);  // Check the 'matches' array specifically

        // Ensure that we're checking 'data.matches' correctly
        if (Array.isArray(data.matches)) {
            populateMatches(data.matches);
            // populateTable(matchesTable, data.matches, ["match_start", "winner_name", "opponent", "opponentID"], 1);
        } else {
            console.error("Data.matches is not an array:", data.matches);
        }
    })
    .catch(error => console.error("Error fetching matches data:", error));
}

function loadTournametsData(userID) {
    fetch(`/data/api/userTournaments/?userID=${userID}`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
            "Content-Type": "application/json",
        },
    }) // Fetch 3 latest tournament data from user
    .then(response => {
        if (!response.ok)
            {
            throw new Error(`HTML error, status: ${response.status}`)
        }
        return response.json();
    })
    .then(data => {
        console.log("Raw response:", data);  // Log the whole response
        console.log("Tournaments:", data.tournaments);  // Check the 'tournaments' array specifically

        // Ensure that we're checking 'data.matches' correctly
        if (Array.isArray(data.tournaments)) {
            populateTournament(data.tournaments);
            // populateTable(tournamentsTable, data.tournaments, ["start_date", "winner", ], 2);
        } else {
            console.error("Data.tournaments is not an array:", data.tournaments);
        } 
    })
    .catch(error => console.error("Error fetching tournament data:", error));
}

function loadProfile(userID) {
    console.log("UserID: ", userID);
    loadUserData(userID);
    loadMatchesData(userID);
    loadTournametsData(userID);
}

const profileBtn = document.getElementById("profileBtn");
if (profileBtn) {
    profileBtn.addEventListener("click", function () {
        loadProfile("self");
    });
}
