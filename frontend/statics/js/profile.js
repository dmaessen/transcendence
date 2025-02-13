function populateTable(table, data, columns) {
    // Clear any existing rows
    table.innerHTML = "";
    
    // Iterate over the data and create new rows
    data.forEach(item => {
        const row = document.createElement("tr");
        columns.forEach(col => {
            const cell = document.createElement("td");
            cell.textContent = item[col] || "N/A"; // Handle missing data
            row.appendChild(cell);
        });
        table.appendChild(row);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const profileBtn = document.getElementById("profileBtn");
    const profileModal = new bootstrap.Modal(document.getElementById("profileModal"));
    if (profileBtn) {
        profileBtn.addEventListener("click", function () {
            console.log("hey");
            fetch("/get_user_data/") // Django API endpoint
                .then(response => response.json())
                // .then(text => {
                //     console.log("Raw response:", text); // Loga a resposta bruta
                //     return JSON.parse(text); // Converte para JSON manualmente
                // })
                .then(data => {
                    document.getElementById("userAvatar").src = data.avatar;
                    document.getElementById("username").textContent = data.username;
                    document.getElementById("userEmail").textContent = data.email;
                    
                    // Populate matches table
                    const matchesTable = document.querySelector(".matches table:nth-of-type(1)");
                    populateTable(matchesTable, data.matches, ["date", "winner", "opponent"]);

                    // Populate tournaments table
                    const tournamentsTable = document.querySelector(".matches table:nth-of-type(2)");
                    populateTable(tournamentsTable, data.tournaments, ["date", "winner"]);

                    profileModal.show();

                })
                .catch(error => console.error("Error fetching profile:", error));
        });
    }
});
