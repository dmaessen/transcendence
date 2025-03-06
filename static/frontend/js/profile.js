function populateTable(table, data, columns, flag) {
    console.log("table:", table);
    console.log("data:", data);
    console.log("columns:", columns);
    
    if (!table) {
        console.error("Table not found!");
        return;
    }

    if (!Array.isArray(data)) {
        console.error("Provided data is not an array:", data);
        return;
    }

    // Clear existing rows
    table.innerHTML = "";

    // Create a table head and append headers
    let thead = table.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        table.appendChild(thead);
    }

    // Deal with headers
    let headerRow = document.createElement("tr");
    if (flag == 1) {
        headerRow.innerHTML = "<th>Match date</th><th>Winner</th><th>Opponent</th>";
    }
    if (flag == 2) {
        headerRow.innerHTML = "<th>Tournament date</th><th>Winner</th>";
    }
    thead.innerHTML = "";  // Clear existing header content
    thead.appendChild(headerRow);

    // Populate new data
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

    if (profileBtn) {
        profileBtn.addEventListener("click", function () {
            console.log("hey");
            
            fetch("/data/api/userData/") // Fetch user info
                .then(response => response.json())
                .then(data => {
                    console.log("Raw response:", data);

                    document.getElementById("userAvatar").src = data.avatar;
                    document.getElementById("username").textContent = data.username;
                    document.getElementById("userEmail").textContent = data.email;

                })
                .catch(error => console.error("Error fetching user data:", error));

            fetch("/data/api/userMatches/") // Fetch 3 latest matches from user 
                .then(response => response.json())
                .then(data => {
                    console.log("Raw response:", data);  // Log the whole response
                    console.log("Matches:", data.matches);  // Check the 'matches' array specifically
            
                    // Ensure that we're checking 'data.matches' correctly
                    if (Array.isArray(data.matches)) {
                        populateTable(matchesTable, data.matches, ["match_start", "winner_name", "opponent"], 1);
                    } else {
                        console.error("Data.matches is not an array:", data.matches);
                    }
                })
                .catch(error => console.error("Error fetching matches data:", error));

            fetch("/data/api/userTournaments/") // Fetch 3 latest tournament data from user
                .then(response => response.json())
                .then(data => {
                    console.log("Raw response:", data);  // Log the whole response
                    console.log("Tournaments:", data.tournaments);  // Check the 'tournaments' array specifically

                    // Ensure that we're checking 'data.matches' correctly
                    if (Array.isArray(data.tournaments)) {
                        populateTable(tournamentsTable, data.tournaments, ["start_date", "winner"], 2);
                    } else {
                        console.error("Data.tournaments is not an array:", data.tournaments);
                    } 
                })
                .catch(error => console.error("Error fetching tournament data:", error));
        });
    }
});
