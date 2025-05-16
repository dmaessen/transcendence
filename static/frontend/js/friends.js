const friendsModalElement = document.getElementById("friendsModal");
const friendsModal = new bootstrap.Modal(friendsModalElement);

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
    headerRow.innerHTML =
        "<th>" + fText + "</th>" +
        "<th>" + sText + "</th>";
    thead.appendChild(headerRow);

    data.forEach(item => {
        const row = document.createElement("tr");

        const nameCell = document.createElement("td");
        const nameLink = document.createElement("span");
        nameLink.textContent = item.friend;
        nameLink.dataset.userID = item.friend_id;
        nameLink.style.cursor = "pointer";
        nameLink.style.color = "gray";

        nameLink.addEventListener("click", function() {
            const friendsModalElement = document.getElementById("friendsModal");
            const friendsModal = bootstrap.Modal.getInstance(friendsModalElement);
            friendsModal.hide();
            loadProfile(nameLink.dataset.userID);
        });
        nameCell.appendChild(nameLink);

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

async function loadFriends(push = true) {
    try{
        friendsModal.show();
        const response = await fetch(`/data/api/getFriends`, {
            method: "GET",
            credentials: "include",
            headers: {
            },
        });
        if (!response.ok) {
            throw new Error(`Error, status: ${response.status}`);
        }
        const data = await response.json();
        populateFriends(data);
        if(push)
            history.pushState({ modalID: "friendsModal" }, "", "?modal=friendsModal");
    } catch (error){
        console.error("Error loading friendsModal", error);0

    }
}

const friendsBtn = document.getElementById("friendsBtn");
if (friendsBtn) {
    friendsBtn.addEventListener("click", () => {
        loadFriends();
    });
}

const closeFriendsBtn = document.getElementById("closeFriendsBtn");
if(closeFriendsBtn){
    closeFriendsBtn.addEventListener("click", function() {
        history.back();
    });
}
