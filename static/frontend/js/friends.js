function populateFriends(data) {
    if (!Array.isArray(data)) {
        console.error("Provided data is not an array:", data);
        return;
    }

    // Clear existing rows
    friendsTable.innerHTML = "";

    // Create a table head and append headers
    let thead = friendsTable.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        friendsTable.appendChild(thead);
    }
    let headerRow = document.createElement("tr");
    const fText = document.getElementById("text_friend").textContent.trim();
    const sText = document.getElementById("text_status").textContent.trim();
    // headerRow.innerHTML = "<th>Friend</th><th>Status</th>";
    headerRow.innerHTML =
        "<th>" + fText + "</th>" +
        "<th>" + sText + "</th>";
    thead.appendChild(headerRow);

    data.forEach(item => {
        const row = document.createElement("tr");

        const nameCell = document.createElement("td");
        nameCell.textContent = item.friend;
        row.appendChild(nameCell);

        const statusCell = document.createElement("td");
        if(item.is_online == false){
            statusCell.textContent = "🔴";
        } else {
            statusCell.textContent = "🟢";
        }
        row.appendChild(statusCell);
        friendsTable.appendChild(row);
    });
}

async function loadFriends() {
    const response = await fetch(`/data/api/getFriends`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
    });
    if (!response.ok) {
        throw new Error(`Error, status: ${response.status}`);
    }
    const data = await response.json();
    console.log("response: ", data);
    populateFriends(data);
    
}

const friendsBtn = document.getElementById("friendsBtn");
if(friendsBtn) {
    friendsBtn.addEventListener("click", loadFriends)
}

const closeFriendsBtn = document.getElementById("closeFriendsBtn");
if(closeFriendsBtn){
    closeFriendsBtn.addEventListener("click", function() {
        console.log("profile close clicked");
        const friendsModalElement = document.getElementById("friendsModal");
        const friendsModal = bootstrap.Modal.getInstance(friendsModalElement);
        friendsModal.hide();
        const gameMenuFirstElement = document.getElementById("gameMenuFirst");
        const gameMenuFirst = bootstrap.Modal.getOrCreateInstance(gameMenuFirstElement);
        gameMenuFirst.show();
    });
}
