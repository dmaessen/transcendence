async function acceptFriend(friendshipID) {
    console.log("friendshipID: ", friendshipID);
    try {
        const response = await fetch(`/data/api/acceptFriendship/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // if needed for authentication
                "Content-Type": "application/json",
            },
            body: JSON.stringify({friendshipID: friendshipID})
        });
        if (!response.ok) {
            throw new Error(`Error, status: ${response.status}`);
        }
        const data = await response.json();
        if (data.success) {
            loadFriendsRequests();
            console.log("Friend added successfully");
        } else {
            console.error("Failed to add friend:", data.error);
        }
    } catch (error) {
        console.error("Error adding a friend:", error);
    }
}

async function declineFriend(friendshipID) {
    console.log("friendshipID: ", friendshipID);
    try {
        const response = await fetch(`/data/api/cancelFriendship/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // if needed for authentication
                "Content-Type": "application/json",
            },
            body: JSON.stringify({friendshipID: friendshipID})
        });
        if (!response.ok) {
            throw new Error(`Error, status: ${response.status}`);
        }
        const data = await response.json();
        if (data.success) {
            loadFriendsRequests();
            console.log("Friend added successfully");
        } else {
            console.error("Failed to add friend:", data.error);
        }
    } catch (error) {
        console.error("Error adding a friend:", error);
    }
}

function populateFRequests(data) {
    console.log("populateFriendsRequest: ", data);
    if (!Array.isArray(data)) {
        console.error("Provided data is not an array:", data);
        return;
    }

    // Clear existing rows
    frienshipRequestTable.innerHTML = "";

    // Create a table head and append headers
    let thead = frienshipRequestTable.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        frienshipRequestTable.appendChild(thead);
    }
    let headerRow = document.createElement("tr");
    headerRow.innerHTML = "<th>Username</th><th>Accept</th><th>Decline</th>";
    thead.appendChild(headerRow);

    data.forEach(item => {
        const row = document.createElement("tr");
        
        const usernameCell = document.createElement("td");
        if(item.user_id === item.sender_id){
            usernameCell.textContent = item.receiver;
        } else {
            usernameCell.textContent = item.sender;
        }
        row.appendChild(usernameCell);
        
        const acceptCell = document.createElement("td");
        if(item.user_id != item.sender_id) {
            const acceptLink = document.createElement("span");
            acceptLink.textContent = "✔️";
            acceptLink.dataset.friendshipID = item.friendship_id;
            acceptLink.style.cursor = "pointer"; // Make it look clickable
            acceptLink.style.color = "green"; // Make it look like a link
            acceptLink.addEventListener("click", function(){
            acceptFriend(acceptLink.dataset.friendshipID);
            });
            acceptCell.appendChild(acceptLink);
        } else {
            acceptCell.textContent = "";
        }
        row.appendChild(acceptCell);

        const declineCell = document.createElement("td");
        const declineLink = document.createElement("span");
        declineLink.textContent = "❌";
        declineLink.dataset.friendshipID = item.friendship_id;
        declineLink.style.cursor = "pointer"; // Make it look clickable
        declineLink.addEventListener("click", function(){
           declineFriend(declineLink.dataset.friendshipID);
        });
        declineCell.appendChild(declineLink);
        row.appendChild(declineCell);

        frienshipRequestTable.appendChild(row);
    });
}

async function loadFriendsRequests() {
    console.log("loadFRequest");
    try {
        const response = await fetch(`/data/api/friendsRequests`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // if needed for authentication
            }
        });
        if (!response.ok) {
            throw new Error(`error, status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Raw response:", data);
        
        if (Array.isArray(data)) {
            populateFRequests(data);
        } else {
            console.error("Data.fRequests is not an array:", data);
        }
        
    } catch(error) {
        console.error("Error fetching matches data:", error);
    }
}

const addFriendBtn = document.getElementById("addFriendsBtn");
if(addFriendBtn) {
    addFriendBtn.addEventListener("click", loadFriendsRequests);
}

const searchInput = document.getElementById("searchInput")
const searchResults = document.getElementById("searchResults")

searchInput.addEventListener("input", async function(){
    const query = searchInput.value.trim() // trim to remove unsesired spaces before or after

    if (query.lenght == 0) 
        return;

    const response = await fetch(`/data/api/searchUser/?usename=${encodeURIComponent(query)}`, {
        method: POST,
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
        
    })
})