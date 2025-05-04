async function addFriend(userID) {
    console.log("addFriend userID: ", userID);
    try {
        const response = await fetch(`/data/api/addFriend/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // if needed for authentication
                "Content-Type": "application/json",
            },
            body: JSON.stringify({userID: userID})
        });

        if (!response.ok) {
            throw new Error(`Error, status: ${response.status}`);
        }

        const data = await response.json();
        if (data.success) {
            loadUserData(userID);
            console.log("Friend added successfully");
        } else {
            console.error("Failed to add friend:", data.error);
        }
    } catch (error) {
        console.error("Error adding a friend:", error);
    }
}

async function deleteFriend(userID) {
    try {
        const response = await fetch(`/data/api/deleteFriend/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // if needed for authentication
                "Content-Type": "application/json",
            },
            body: JSON.stringify({userID: userID})
        });
        if (!response.ok) {
            throw new Error(`Error, status: ${response.status}`);
        }

        const data = await response.json();
        if (data.success) {
            loadUserData(userID);
            console.log("Friend deleted successfully");
        } else {
            console.error("Failed to delete friend:", data.error);
        }
    } catch (error) {
        console.error("Error deleting a friend:", error);
    }
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

async function loadUserData(userID) {
    console.log("loadProfile userID: ", userID);
    try {
        const response = await fetch(`/data/api/userData/?userID=${userID}`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
            },
        });
        if (!response.ok) {
            throw new Error(`Error, status: ${response.status}`);
        }

        const data = await response.json();
        console.log("loadProfile user data:", data);

        document.getElementById("userAvatar").src = data.avatar;
        document.getElementById("username").textContent = data.username;
        document.getElementById("userEmail").textContent = data.email;
        document.getElementById("btnType").textContent = data.btnType;
        document.getElementById("matchesPlayed").textContent = data.matches_played;
        document.getElementById("wins").textContent = data.matches_won;
        document.getElementById("losses").textContent = data.matches_lost;
        document.getElementById("AllMatchesModal").setAttribute("data-user-id", data.user_id);
        document.getElementById("AllTournamentsModal").setAttribute("data-user-id", data.user_id);
        friendshipID = data.friendshipID;

        let btnType = document.getElementById("btnType");
        btnType.disabled = false;
        btnType.onclick = () => {
            if (data.btnType === "Add friend") {
                addFriend(userID);
            } else if (data.btnType === "Edit profile") {
                let profileModalElement = document.getElementById("profileModal");
                let profileModal = bootstrap.Modal.getInstance(profileModalElement);
                profileModal.hide();
                let modal = new bootstrap.Modal(document.getElementById("editProfileModal"));
                modal.show();
            } else if (data.btnType === "Delete friend") {
                deleteFriend(userID);
            } else if (data.btnType === "Cancel request") {
                deleteFriend(userID);
            } else if (data.btnType === "Accept request") {
                acceptFriend(friendshipID);
            }
        };
    } catch (error) {
        console.error("Error fetching user data:", error);
    }
}

async function loadMatchesData(userID) {
    try {
        const response = await fetch(`/data/api/userMatches/?userID=${userID}`, {
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
            populateMatches(data.matches);
        } else {
            console.error("Data.matches is not an array:", data.matches);
        }
    } catch (error) {
        console.error("Error fetching matches data:", error);
    }
}

async function loadTournametsData(userID) {
    try {
        const response = await fetch(`/data/api/userTournaments/?userID=${userID}`, {
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
            populateTournament(data.tournaments);
        } else {
            console.error("Data.tournaments is not an array:", data.tournaments);
        }
    } catch (error) {
        console.error("Error fetching tournament data:", error);
    }
}

async function loadProfile(userID, openModal = true) {
    try {
        // Close possible already opened modals to avoid the backgroud from getting darker and darker
        const profileModalElement = document.getElementById("profileModal");
        const existingModal = bootstrap.Modal.getInstance(profileModalElement);
        if (existingModal) {
            existingModal.hide();
        }

        await loadUserData(userID);
        await loadMatchesData(userID);
        await loadTournametsData(userID);

        if (openModal) {
            const profileModalElement = document.getElementById("profileModal");
            const profileModal = new bootstrap.Modal(profileModalElement);
            profileModal.show();
        }
    } catch (error) {
        console.error("Error loading profile:", error);
    }
}

const profileBtn = document.getElementById("profileBtn");
if (profileBtn) {
    profileBtn.addEventListener("click", function () {
        loadProfile("self");
        
    });
}

const profileCloseButton = document.getElementById("profileCloseButton");
if(profileCloseButton){
    profileCloseButton.addEventListener("click", function() {
        console.log("profile close clicked");
        const profileModalElement = document.getElementById("profileModal");
        const profileModal = bootstrap.Modal.getInstance(profileModalElement);
        profileModal.hide();
        const gameMenuFirstElement = document.getElementById("gameMenuFirst");
        const gameMenuFirst = bootstrap.Modal.getOrCreateInstance(gameMenuFirstElement);
        gameMenuFirst.show();
    });
}
