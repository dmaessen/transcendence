// let gameMenuStarted = false;

async function drawBracket(mode) {
    console.log("drawBracket called with mode:", mode);
    if (mode == "4") {
        document.getElementById("tournamentBracket4").style.display = "grid";
        document.getElementById("tournamentBracket4").style.background = "white";
        clearPlayerFields(mode);
    }
    else {
        document.getElementById("tournamentBracket").style.display = "grid";
        document.getElementById("tournamentBracket").style.background = "white";
        clearPlayerFields(mode);
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
            updateBracket(mode, data.bracket, data.winners, data.current_round, data.final_winner);

            // console.log("Tournament active:", data.tournament_active);
            // console.log("Players in:", data.players_in);
            // console.log("Mode:", mode);
            // if (data.matches.length == 0)
            //     gameMenuStarted = false; // to reset between end of matches

            // if (data.matches && data.matches.length > 0) {
            //     document.getElementById("tournamentBracket").style.display = "none";
            //     document.getElementById("tournamentBracket4").style.display = "none";
            //     // await sleep(4000);
            //     // startGameMenu(); // it glitches here as being called every 5sec and then the start prompt gets triggered again
            //     // gameMenuStarted = true;
            // }
            

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
            // elem.style.border = "1px solid blue";
        });

        if (playerElem) {
            playerElem.innerText = players[i] ? players[i].username : `Waiting... `;
        }
        // if (resultElem) {
        //     resultElem.innerText = results[i] !== undefined ? results[i] : " 0 ";
        // }
    }
}

function updateBracket(mode, bracket, winners, currentRound, final_winner) {
    console.log("Updating bracket with mode:", mode);
    // console.log("Bracket Winners:", winners);
    // do we need to receive winners in this function??

    let playerElem;
    let resultElem;
    let winners4 = [];

    if (mode == "4" && final_winner != null) {
        playerElem = document.getElementById(`Player${13}_`);
        if (playerElem && playerElem.textContent.trim() === final_winner.username) {
            resultElem = document.getElementById(`Result${13}_`);
            if (resultElem) {
                resultElem.innerText = " 👑 ";
            }
        } else {
            resultElem = document.getElementById(`Result${14}_`);
            if (resultElem) {
                resultElem.innerText = " 👑 ";
            }
        }
    }
    if (mode == "8" && final_winner != null) {
        playerElem = document.getElementById(`Player${13}`);
        if (playerElem && playerElem.textContent.trim() === final_winner[0].username) {
            resultElem = document.getElementById(`Result${13}`);
            if (resultElem) {
                resultElem.innerText = " 👑 ";
            }
        } else {
            resultElem = document.getElementById(`Result${14}`);
            if (resultElem) {
                resultElem.innerText = " 👑 ";
            }
        }
    }
    if (mode == "4" && (currentRound == 1 || currentRound == 2)) { // WORKING
        if (bracket && bracket[1]) {
            for (let i = 0; i < mode; i++) {
                playerElem = document.getElementById(`Player${i + 1}_`);
                resultElem = document.getElementById(`Result${i + 1}_`);
    
                bracket[1].forEach(match => {
                    match.forEach(playerObj => {  
                        let playerName = playerObj.player.username;  
                        if (playerElem && playerElem.textContent.trim() === playerName) {
                            if (playerObj.winner) {
                                resultElem.innerText = " 👑 ";
                                winners4.push(playerName);
                            }
                        }
                    });
                });}}
    }
    if (mode == "8" && (currentRound == 1 || currentRound == 2)) { // rework this based on winner bool if not working
        if (bracket && bracket[1]) {
            for (let i = 0; i < mode; i++) {
                playerElem = document.getElementById(`Player${i + 1}`);
                resultElem = document.getElementById(`Result${i + 1}`);
                bracket[1].forEach(match => {
                    match.forEach(playerObj => {  
                        let playerName = playerObj.player.username;  
                        if (playerElem && playerElem.textContent.trim() === playerName) {
                            if (playerObj.winner) {
                                resultElem.innerText = " 👑 ";
                            }
                        }
                    });
        });}}
    }
    if (mode == "4" && winners4.length == 2){ // WORKING
        playerElem = document.getElementById(`Player${13}_`);
        if (playerElem){
            playerElem.innerText = winners4[0];
        }
        playerElem = document.getElementById(`Player${14}_`);
        if (playerElem){
            playerElem.innerText = winners4[1];
        }
    }
    if (mode == "8" && currentRound == 2) {
        playerElem = document.getElementById(`Player${9}`);
        if (playerElem) {
            playerElem.innerText = bracket[currentRound][0][0].username;
        }
        playerElem = document.getElementById(`Player${10}`);
        if (playerElem) {
            playerElem.innerText = bracket[currentRound][0][1].username;
        }
        playerElem = document.getElementById(`Player${11}`);
        if (playerElem) {
            playerElem.innerText = bracket[currentRound][1][0].username;
        }
        playerElem = document.getElementById(`Player${12}`);
        if (playerElem) {
            playerElem.innerText = bracket[currentRound][1][1].username;
        }
    }
    if (mode == "8" && currentRound == 3) {
        playerElem = document.getElementById(`Player${13}`);
        if (playerElem) {
            playerElem.innerText = bracket[currentRound][0][0].username;
        }
        playerElem = document.getElementById(`Player${14}`);
        if (playerElem) {
            playerElem.innerText = bracket[currentRound][0][1].username;
        }

        for (let i = 0; i < 4; i++) { // rework this based on winner bool if not working
            playerElem = document.getElementById(`Player${i + 9}`);
            resultElem = document.getElementById(`Result${i + 9}`);
            for (let j = 0; j < winners.length; j++) {
                if (playerElem && playerElem.textContent.trim() === winners[j].username) {
                    if (resultElem) {
                        resultElem.innerText = " 👑 ";
                    }
                }
            }
        }
    }
}

// Clear brackets from previous players/results
function clearPlayerFields(mode) {
    let playerElem;
    let resultElem;

    if (mode == 8) {
        for (let i = 0; i < 14; i++) {
            playerElem = document.getElementById(`Player${i + 1}`);
            resultElem = document.getElementById(`Result${i + 1}`);

            document.querySelectorAll("[id^='Player']").forEach(elem => {
                elem.style.display = "block";
                elem.style.color = "black";
                elem.style.fontSize = "14px";
            });
            document.querySelectorAll("[id^='Result']").forEach(elem => {
                elem.style.display = "block";
                elem.style.color = "black";
                elem.style.fontSize = "14px";
            });
            if (playerElem) {
                playerElem.innerText = `Waiting... `;
            }
            if (resultElem) {
                resultElem.innerText = " ";
            }
        }
    } else if (mode == 4) {
        for (let i = 0; i < mode; i++) {
            playerElem = document.getElementById(`Player${i + 1}_`);
            resultElem = document.getElementById(`Result${i + 1}_`);
            document.querySelectorAll("[id^='Player']").forEach(elem => {
                elem.style.display = "block";
                elem.style.color = "black";
                elem.style.fontSize = "14px";
            });
            document.querySelectorAll("[id^='Result']").forEach(elem => {
                elem.style.display = "block";
                elem.style.color = "black";
                elem.style.fontSize = "14px";
            });
            if (playerElem) {
                playerElem.innerText = `Waiting... `;
            }
            if (resultElem) {
                resultElem.innerText = " ";
            }
        }
        for (let i = 12; i < 14; i++) {
            playerElem = document.getElementById(`Player${i + 1}_`);
            resultElem = document.getElementById(`Result${i + 1}_`);
            document.querySelectorAll("[id^='Player']").forEach(elem => {
                elem.style.display = "block";
                elem.style.color = "black";
                elem.style.fontSize = "14px";
            });
            document.querySelectorAll("[id^='Result']").forEach(elem => {
                elem.style.display = "block";
                elem.style.color = "black";
                elem.style.fontSize = "14px";
            });
            if (playerElem) {
                playerElem.innerText = `Waiting... `;
            }
            if (resultElem) {
                resultElem.innerText = " ";
            }
        }
    }
}





