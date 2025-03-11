// let gameMenuStarted = false;

async function drawBracket(mode) {
    console.log("drawBracket called with mode:", mode);
    if (mode == "4") {
        document.getElementById("tournamentBracket4").style.display = "grid";
        document.getElementById("tournamentBracket4").style.background = "white"; // Remove black
    }
    else {
        document.getElementById("tournamentBracket").style.display = "grid";
        document.getElementById("tournamentBracket").style.background = "white"; // Remove black
    }

    await updateBracketWithData(mode);
    let tournamentInterval = setInterval(async () => await updateBracketWithData(mode), 5000); // Auto-update every 5s
}

function stopTournamentUpdates() {
    if (tournamentInterval) {
        clearInterval(tournamentInterval);
        console.log("Tournament updates stopped.");
    }
}

async function updateBracketWithData(mode) {
    try {
        const data = await fetchData("http://localhost:8080/api/tournament-status/");
        console.log("Fetched tournament status:", data);

        if (data) {
            updatePlayerFields(mode, data.players, data.results);
            updateBracket(mode, data.bracket, data.players, data.winners, data.current_round);

            // console.log("Tournament active:", data.tournament_active);
            // console.log("Players in:", data.players_in);
            // console.log("Mode:", mode);
            // if (data.matches.length == 0)
            //     gameMenuStarted = false; // to reset between end of matches

            if (data.matches && data.matches.length > 0) {
                document.getElementById("tournamentBracket").style.display = "none";
                document.getElementById("tournamentBracket4").style.display = "none";
                await sleep(4000);
                startGameMenu(); // it glitches here as being called every 5sec and then the start prompt gets triggered again
                // gameMenuStarted = true;
            }

            // Stop updates if tournament is over or a player quits
            // if (!data.tournament_active || data.players_in < mode) {
            //     stopTournamentUpdates();
            // }
        }
    } catch (error) {
        console.error("Error fetching tournament status:", error);
    }
}

function updatePlayerFields(mode, players, results = []) {
    let playerElem;
    let resultElem;

    for (let i = 0; i < mode; i++) {
        if (mode == 8) {
            playerElem = document.getElementById(`Player${i + 1}`);
            resultElem = document.getElementById(`Result${i + 1}`);
        } else if (mode == "4") {
            playerElem = document.getElementById(`Player${i + 1}_`);
            resultElem = document.getElementById(`Result${i + 1}_`);
        }
        document.querySelectorAll("[id^='Player']").forEach(elem => {
            elem.style.display = "block";
            elem.style.color = "black";
            elem.style.fontSize = "14px";
        });
        document.querySelectorAll("[id^='Result']").forEach(elem => {
            elem.style.display = "block";
            elem.style.color = "black";
            elem.style.fontSize = "14px bold";
            elem.style.border = "1px solid blue"; // debugging
        });

        if (playerElem) {
            playerElem.innerText = players[i] ? players[i].username : `Waiting... `;
        }
        if (resultElem) {
            resultElem.innerText = results[i] !== undefined ? results[i] : " 0 ";
        }
    }
}

// review this for 4 players
function updateBracket(mode, bracket, players, winners, currentRound) {
    console.log("Updating bracket with mode:", mode);
    console.log("Bracket Winners:", winners);

    winners.forEach((winner, index) => {
        const winnerElem = document.getElementById(`Player${index + 9}`); // Winner fields start at Player9
        if (winnerElem) {
            winnerElem.textContent = winner ? winner.username : `Winner ${index + 1}`;
        }
    });

    if (winners.length === 1 && winners[0]) {
        displayChampion(winners[0].username);
    }
}

function displayChampion(championName) {
    const championElem = document.createElement("div");
    championElem.classList.add("champion-display");
    championElem.style.color = "gold";
    championElem.style.fontSize = "24px";
    championElem.style.textAlign = "center";
    championElem.textContent = `Champion: ${championName}`;

    document.body.appendChild(championElem);
}









// const tournCanvas = document.getElementById('tournamentBracket');
// const tournContext = tournCanvas.getContext('2d');

// async function drawBracket(mode) {
//     console.log("drawBracket called with mode:", mode);

//     tournCanvas.style.display = 'block';
//     tournCanvas.width = 800;
//     tournCanvas.height = 600;
//     tournContext.clearRect(0, 0, tournCanvas.width, tournCanvas.height);
//     tournContext.fillStyle = "#000000";
//     tournContext.fillRect(0, 0, tournCanvas.width, tournCanvas.height);
//     tournContext.strokeStyle = "#FFFFFF";
//     tournContext.fillStyle = "#FFFFFF";
//     tournContext.font = "14px Courier New";
//     tournContext.textAlign = "center";

//     await updateBracketWithData(mode);
//     let tournamentInterval = setInterval(async () => await updateBracketWithData(mode), 5000); // auto-update every 5s 
//     // make the above stop when tournament over or if someone quits the tournament
// }

// // call stopTournamentUpdates() below when the tournament ends or a player quits
// function stopTournamentUpdates() {
//     if (tournamentInterval) {
//         clearInterval(tournamentInterval);
//         console.log("Tournament updates stopped.");
//     }
// }

// async function updateBracketWithData(mode) {
//     try {
//         const data = await fetchData("http://localhost:8080/api/tournament-status/");
//         console.log("Fetched tournament status:", data);
//         if (data) {
//             updateBracket(mode, data.bracket, data.players, data.winners, data.current_round);
//         }
//     } catch (error) {
//         console.error("Error fetching tournament status:", error);
//     }
// }

// function updateBracket(mode, bracket, players, winners, currentRound) {
//     tournContext.clearRect(0, 0, tournCanvas.width, tournCanvas.height);
//     drawBracketStructure(mode);

//     tournContext.font = "18px Courier New";
//     players.forEach((player, index) => {
//         const x = tournCanvas.width / 8 * (index % 2 === 0 ? 1 : 7);
//         const y = 60 + Math.floor(index / 2) * 120; // Increase spacing
//         tournContext.fillText(player.username || `Player ${index + 1}`, x, y);
//     });

//     tournContext.font = "20px Courier New"; // Slightly larger font for winners
//     winners.forEach((winner, index) => {
//         const x = tournCanvas.width / 2;
//         const y = 280 + index * 120; // Increase spacing
//         tournContext.fillText(winner.username || `Winner ${index + 1}`, x, y);
//     });

//     if (winners.length === 1) {
//         displayChampion(winners[0].username);
//     }
// }

// function drawBracketStructure(mode) {
//     tournContext.beginPath();
//     tournContext.strokeStyle = "#FFFFFF";
//     if (mode == "4") {
//         drawBracketStructure4();
//     } else if (mode == "8") {
//         drawBracketStructure8();
//     }
//     tournContext.stroke();
// }

// function drawBracketStructure4() {
//     tournContext.moveTo(tournCanvas.width / 4, 100);
//     tournContext.lineTo(tournCanvas.width / 2, 100);
//     tournContext.moveTo(tournCanvas.width * 3 / 4, 100);
//     tournContext.lineTo(tournCanvas.width / 2, 100);
//     tournContext.moveTo(tournCanvas.width / 2, 100);
//     tournContext.lineTo(tournCanvas.width / 2, 200);
// }

// // function drawBracketStructure8() {
// //     tournContext.moveTo(tournCanvas.width / 8, 50);
// //     tournContext.lineTo(tournCanvas.width / 4, 50);
// //     tournContext.moveTo(tournCanvas.width * 3 / 8, 50);
// //     tournContext.lineTo(tournCanvas.width / 4, 50);
// //     tournContext.moveTo(tournCanvas.width / 4, 50);
// //     tournContext.lineTo(tournCanvas.width / 4, 150);
// //     tournContext.moveTo(tournCanvas.width * 5 / 8, 50);
// //     tournContext.lineTo(tournCanvas.width * 3 / 4, 50);
// //     tournContext.moveTo(tournCanvas.width * 7 / 8, 50);
// //     tournContext.lineTo(tournCanvas.width * 3 / 4, 50);
// //     tournContext.moveTo(tournCanvas.width * 3 / 4, 50);
// //     tournContext.lineTo(tournCanvas.width * 3 / 4, 150);
// //     tournContext.moveTo(tournCanvas.width / 4, 150);
// //     tournContext.lineTo(tournCanvas.width * 3 / 4, 150);
// //     tournContext.moveTo(tournCanvas.width / 2, 150);
// //     tournContext.lineTo(tournCanvas.width / 2, 250);
// // }

// function drawBracketStructure8() {
//     // First round lines
//     tournContext.moveTo(tournCanvas.width / 16, 60);
//     tournContext.lineTo(tournCanvas.width / 8, 60);
//     tournContext.moveTo(tournCanvas.width * 3 / 16, 60);
//     tournContext.lineTo(tournCanvas.width / 8, 60);
//     tournContext.moveTo(tournCanvas.width / 8, 60);
//     tournContext.lineTo(tournCanvas.width / 8, 120);

//     tournContext.moveTo(tournCanvas.width * 5 / 16, 60);
//     tournContext.lineTo(tournCanvas.width * 3 / 8, 60);
//     tournContext.moveTo(tournCanvas.width * 7 / 16, 60);
//     tournContext.lineTo(tournCanvas.width * 3 / 8, 60);
//     tournContext.moveTo(tournCanvas.width * 3 / 8, 60);
//     tournContext.lineTo(tournCanvas.width * 3 / 8, 120);

//     tournContext.moveTo(tournCanvas.width * 9 / 16, 60);
//     tournContext.lineTo(tournCanvas.width * 5 / 8, 60);
//     tournContext.moveTo(tournCanvas.width * 11 / 16, 60);
//     tournContext.lineTo(tournCanvas.width * 5 / 8, 60);
//     tournContext.moveTo(tournCanvas.width * 5 / 8, 60);
//     tournContext.lineTo(tournCanvas.width * 5 / 8, 120);

//     tournContext.moveTo(tournCanvas.width * 13 / 16, 60);
//     tournContext.lineTo(tournCanvas.width * 7 / 8, 60);
//     tournContext.moveTo(tournCanvas.width * 15 / 16, 60);
//     tournContext.lineTo(tournCanvas.width * 7 / 8, 60);
//     tournContext.moveTo(tournCanvas.width * 7 / 8, 60);
//     tournContext.lineTo(tournCanvas.width * 7 / 8, 120);

//     // Second round lines
//     tournContext.moveTo(tournCanvas.width / 8, 120);
//     tournContext.lineTo(tournCanvas.width / 4, 120);
//     tournContext.moveTo(tournCanvas.width * 3 / 8, 120);
//     tournContext.lineTo(tournCanvas.width / 4, 120);
//     tournContext.moveTo(tournCanvas.width / 4, 120);
//     tournContext.lineTo(tournCanvas.width / 4, 240);

//     tournContext.moveTo(tournCanvas.width * 5 / 8, 120);
//     tournContext.lineTo(tournCanvas.width * 3 / 4, 120);
//     tournContext.moveTo(tournCanvas.width * 7 / 8, 120);
//     tournContext.lineTo(tournCanvas.width * 3 / 4, 120);
//     tournContext.moveTo(tournCanvas.width * 3 / 4, 120);
//     tournContext.lineTo(tournCanvas.width * 3 / 4, 240);

//     // Final round lines
//     tournContext.moveTo(tournCanvas.width / 4, 240);
//     tournContext.lineTo(tournCanvas.width / 2, 240);
//     tournContext.moveTo(tournCanvas.width * 3 / 4, 240);
//     tournContext.lineTo(tournCanvas.width / 2, 240);
//     tournContext.moveTo(tournCanvas.width / 2, 240);
//     tournContext.lineTo(tournCanvas.width / 2, 360);
// }

// function displayChampion(championName) {
//     tournContext.fillStyle = "#FFD700"; // gold champ
//     tournContext.font = "20px Courier New";
//     tournContext.fillText(`Champion: ${championName}`, tournCanvas.width / 2, 300);
// }










// let tournamentStartTime = null;
// let countdownInterval = null;
// let countdownElement = document.getElementById("tournamentCountdown"); // Assuming this element exists in the HTML

// // Function to start the countdown
// function startTournamentCountdown() {
//     tournamentStartTime = Date.now();
//     updateTournamentCountdown();

//     countdownInterval = setInterval(updateTournamentCountdown, 1000); // Update every second
// }

// // Function to update the countdown
// function updateTournamentCountdown() {
//     if (!tournamentStartTime) return;

//     const timeElapsed = Math.floor((Date.now() - tournamentStartTime) / 1000);
//     const timeRemaining = 300 - timeElapsed; // 5 minutes (300 seconds)

//     if (timeRemaining <= 0) {
//         clearInterval(countdownInterval); // Stop the countdown when it reaches 0
//         tournamentCanceled();
//         return;
//     }

//     const minutes = Math.floor(timeRemaining / 60);
//     const seconds = timeRemaining % 60;
//     countdownElement.textContent = `Time remaining: ${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
// }

// // Function to handle tournament cancellation after timeout
// function tournamentCanceled() {
//     alert("Tournament has been canceled due to inactivity.");
//     // You could also reset the UI or show a message about cancellation
//     // and notify the backend to cancel the tournament as well.
//     // Update the UI here to reflect the tournament has been canceled.
//     socket.send(JSON.stringify({ action: "cancel_tournament" }));
// }

// function onPlayerJoinTournament() {
//     // Start the countdown when the first player joins
//     if (!tournamentStartTime) {
//         startTournamentCountdown();
//     }
// }

// // when the tournament is full
// function onTournamentFull() {
//     clearInterval(countdownInterval);
//     socket.send(JSON.stringify({ action: "start_tournament" }));
// 	// start 1v1 games maybe with the other .js files
// }
