const profileModalElement = document.getElementById("profileModal");
const profileModal = new bootstrap.Modal(profileModalElement);

async function addFriend(userID) {
    // console.log("addFriend userID: ", userID);
    try {
        const response = await fetch(`/data/api/addFriend/`, {
            method: "POST",
            credentials: "include",
            headers: {
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
            credentials: "include",
            headers: {
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
    // console.log("populateTournaments data: ", data);
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
        // console.log("tournament userWon: ", item.userWon);
        const row = document.createElement("tr");

        const dateCell = document.createElement("td");
        dateCell.textContent = item.start_date;
        row.appendChild(dateCell);

        const winnerCell = document.createElement("td");
        if (item.winnerID == "Unknown"){
            winnerCell.textContent = "Unknown";
        } else if (item.userWon == false) {
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
            if(item.opponentID == "Unknown"){
                winnerCell.textContent = "Unknown"
            } else {
                const winnerLink = document.createElement("span");
                winnerLink.textContent = item.winner_name;
                winnerLink.dataset.userID = item.opponentID;
                winnerLink.style.cursor = "pointer"; // Make it look clickable
                winnerLink.style.color = "gray"; // Make it look like a link
    
                winnerLink.addEventListener("click", function(){
                    loadProfile(winnerLink.dataset.userID);
                });
                winnerCell.appendChild(winnerLink);
            }
        } else {
            winnerCell.textContent = item.winner_name;
        }
        row.appendChild(winnerCell);
        
        const opponentCell = document.createElement("td");
        if (item.opponentID == "Unknown"){
            opponentCell.textContent = "Unknown";
        } else {
            const opponentLink = document.createElement("span");
            opponentLink.textContent = item.opponent;
            opponentLink.dataset.userID = item.opponentID;
            opponentLink.style.cursor = "pointer"; // Make it look clickable
            opponentLink.style.color = "gray"; // Make it look like a link
            opponentLink.addEventListener("click", function(){
                loadProfile(opponentLink.dataset.userID);
            });
            opponentCell.appendChild(opponentLink);
        }
        row.appendChild(opponentCell);
        
        matchesTable.appendChild(row);
    });
}

async function loadUserData(userID) {
    // console.log("loadProfile userID: ", userID);
    try {
        const response = await fetch(`/data/api/userData/?userID=${userID}`, {
            method: "GET",
            credentials: "include",
            headers: {
            },
        });
        if (!response.ok) {
            throw new Error(`Error, status: ${response.status}`);
        }

        const data = await response.json();
        // console.log("loadProfile user data:", data);

        document.getElementById("userAvatar").src = data.avatar;
        document.getElementById("username").textContent = data.username;
        document.getElementById("userEmail").textContent = data.email;
        document.getElementById("btnType").textContent = data.btnType;
        document.getElementById("matchesPlayed").textContent = data.matches_played;
        document.getElementById("wins").textContent = data.matches_won;
        document.getElementById("losses").textContent = data.matches_lost;
        document.getElementById("currentUser").dataset.userId = data.user_id;
        friendshipID = data.friendshipID;

        let btnType = document.getElementById("btnType");
        btnType.disabled = false;
        btnType.onclick = () => {
            if (data.btnType === "Add friend") {
                addFriend(userID);
                loadProfile(userID);
            } else if (data.btnType === "Edit profile") {
                currentModal = "editProfileModal";
                history.pushState({ modalID: "editProfileModal" }, "", "?modal=editProfileModal");
                console.log("Push: editProfileModal");
                profileModal.hide();
                editProfileModal.show();
            } else if (data.btnType === "Delete friend") {
                deleteFriend(userID);
                loadProfile(userID);
            } else if (data.btnType === "Cancel request") {
                deleteFriend(userID);
                loadProfile(userID);
            } else if (data.btnType === "Accept request") {
                acceptFriend(friendshipID);
                loadProfile(userID);
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
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`Error, status: ${response.status}`);
        }

        const data = await response.json();
        // console.log("Raw response:", data);
        // console.log("Matches:", data.matches);

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
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error, status: ${response.status}`);
        }

        const data = await response.json();
        // console.log("Raw response:", data);
        // console.log("Tournaments:", data.tournaments);

        if (Array.isArray(data.tournaments)) {
            populateTournament(data.tournaments);
        } else {
            console.error("Data.tournaments is not an array:", data.tournaments);
        }
    } catch (error) {
        console.error("Error fetching tournament data:", error);
    }
}

async function loadProfile(userID, openModal = true, push = true) {
    try {
        //Avoid black backgroud
        // const profileModalElement = document.getElementById("profileModal");
        const existingModal = bootstrap.Modal.getInstance(profileModalElement);
        if (existingModal) {
            existingModal.hide();
        }

        //Load all the information on the page
        await loadUserData(userID);
        await loadMatchesData(userID);
        await loadTournametsData(userID);

        if (openModal) {
            if (push) {
                const state = { modalID: "profileModal", userID: userID };
                const url = `?modal=profileModal&user=${userID}`;
                currentModal = "profileModal";
                history.pushState(state, '', url);
                console.log("Push: ", state);
            }
        
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
        // console.log("profile close clicked");
        history.back();
    });
}
