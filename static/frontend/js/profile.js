// function populateTable(table, data, columns) {
//     console.log("table: ",table);
//     console.log("data: ", data);
//     console.log("columns: ", columns);
//     if (!table) {
//         console.error("Table not found!");
//         return;
//     }
//     console.log("Populating table with columns:", columns);

//     // Clear existing rows
//     table.innerHTML = "";

//     // Populate new data
//     data.forEach(item => {
//         const row = document.createElement("tr");
//         columns.forEach(col => {
//             const cell = document.createElement("td");
//             cell.textContent = item[col] || "N/A"; // Handle missing data
//             row.appendChild(cell);
//         });
//         table.appendChild(row);
//     });
// }

// document.addEventListener("DOMContentLoaded", function () {
//     const profileBtn = document.getElementById("profileBtn");
//     const profileModal = new bootstrap.Modal(document.getElementById("profileModal"));
//     if (profileBtn) {
//         profileBtn.addEventListener("click", function () {
//             console.log("hey");
//             fetch("/get_user_data/") // Django API endpoint
//                 .then(response => response.json())
//                 .then(data => {
//                     console.log("Raw response:", data); // Loga a resposta bruta

//                     document.getElementById("userAvatar").src = data.avatar || "default.png";
//                     document.getElementById("username").textContent = data.username;
//                     document.getElementById("userEmail").textContent = data.email

//                     profileModal.show();

//                 })
                
//             fetch("/get_user_matches/") // Django API endpoint
//                 .then(response => response.json())
//                 .then(data => {
//                     console.log("Raw response:", data); // Loga a resposta bruta

//                     //figure out how to populate the tables here
//                     profileModal.show();

//                 })

//             fetch("/get_user_tournaments/") // Django API endpoint
//                 .then(response => response.json())
//                 .then(data => {
//                     console.log("Raw response:", data); // Loga a resposta bruta
//                     //figure out how to populate the tables here

//                     profileModal.show();

//                 })
//                 .catch(error => console.error("Error fetching profile:", error));
//         });
//     }
// });

function populateTable(table, data, columns) {
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
    const profileModal = new bootstrap.Modal(document.getElementById("profileModal"));

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

                    profileModal.show();
                });
                // .catch(error => console.error("Error fetching data:", error));

                fetch("/data/api/userMatches/")
                .then(response => response.json())
                .then(data => {
                    console.log("Raw response:", data);  // Log the whole response
                    console.log("Matches:", data.matches);  // Check the 'matches' array specifically
            
                    // Ensure that we're checking 'data.matches' correctly
                    if (Array.isArray(data.matches)) {
                        populateTable(matchesTable, data.matches, ["match_start", "winner", "opponent"]);
                    } else {
                        console.error("Data.matches is not an array:", data.matches);
                    }
                })
                .catch(error => console.error("Error fetching matches:", error));

            fetch("/data/api/userTournaments/") // Fetch tournament data
                .then(response => response.json())
                .then(data => {
                    console.log("Raw response:", data);  // Log the whole response
                    console.log("Tournaments:", data.tournaments);  // Check the 'tournaments' array specifically

                    // Ensure that we're checking 'data.matches' correctly
                    if (Array.isArray(data.tournaments)) {
                        populateTable(tournamentsTable, data.tournaments, ["start_date", "winner"]);
                    } else {
                        console.error("Data.tournaments is not an array:", data.tournaments);
                    }
                })
        });
    }
});
