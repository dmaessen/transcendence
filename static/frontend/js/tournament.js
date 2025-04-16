let winners4 = [];
let winners8 = [];
let winners8_final = [];
let tournamentInterval = null;

async function drawBracket(mode) {
    console.log("drawBracket called with mode:", mode);
    if (mode == 4) {
        document.getElementById("tournamentBracket4").style.display = "grid";
        document.getElementById("tournamentBracket4").style.background = "white";
    }
    else {
        document.getElementById("tournamentBracket").style.display = "grid";
        document.getElementById("tournamentBracket").style.background = "white";
    }

    await updateBracketWithData(mode);
    tournamentInterval = setInterval(async () => await updateBracketWithData(mode), 5000); // Auto-update every 5s
}

const stopTournamentUpdates = async (mode) => {
    await sleep(2000);
    if (tournamentInterval) {
        clearInterval(tournamentInterval);
        console.log("Tournament updates stopped.");
    }
    clearPlayerFields(mode);
    console.log("Tournament updates stopped. DONE");
}

async function updateBracketWithData(mode) {
    try {
        const data = await fetchData("/tournament-status/");
        console.log("Fetched tournament status:", data);

        if (data) {
            // if (data.running == false && (data.players_in == 0 || data.players_in == 1))
            //     clearPlayerFields(mode);
            if (data.current_round < 2)
                updatePlayerFields(mode, data.players, data.results);
            updateBracket(mode, data.bracket, data.current_round, data.final_winner);
            if (data.running == false && data.final_winner != null) {
                await stopTournamentUpdates(mode);
                if (websocket && websocket.readyState === WebSocket.OPEN) {
                    websocket.send(JSON.stringify({ action: "disconnect" }));
                }
                return;
            }
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
        } else if (mode == 4) {
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
        });
        if (playerElem) {
            playerElem.innerText = players[i] ? players[i].username : `Waiting... `;
        }
    }
}

const clearArrayWinners = async () => {
    await sleep(3000);
    winners4 = [];
    winners8 = [];
    winners8_final = [];
}

async function updateBracket(mode, bracket, currentRound, final_winner) {
    console.log("Updating bracket with mode:", mode);

    let playerElem;
    let resultElem;

    if (mode == 4 && final_winner != null) {
        playerElem = document.getElementById(`Player${13}_`);
        if (playerElem && playerElem.textContent.trim() === final_winner.username) {
            resultElem = document.getElementById(`Result${13}_`);
            if (resultElem) {
                resultElem.innerHTML = "&nbsp;&nbsp;👑";
            }
        } else {
            resultElem = document.getElementById(`Result${14}_`);
            if (resultElem) {
                resultElem.innerHTML = "&nbsp;&nbsp;👑";
            }
        }
        await clearArrayWinners();
    }
    if (mode == 8 && final_winner != null) {
        playerElem = document.getElementById(`Player${13}`);
        if (playerElem && playerElem.textContent.trim() === final_winner.username) {
            resultElem = document.getElementById(`Result${13}`);
            if (resultElem) {
                resultElem.innerHTML = "&nbsp;&nbsp;👑";
            }
            resultElem = document.getElementById(`Result${14}`);
            if (resultElem) {
                resultElem.innerHTML = "&nbsp;";
            }
        } else {
            resultElem = document.getElementById(`Result${14}`);
            if (resultElem) {
                resultElem.innerHTML = "&nbsp;&nbsp;👑";
            }
            resultElem = document.getElementById(`Result${13}`);
            if (resultElem) {
                resultElem.innerHTML = "&nbsp;";
            }
        }
        await clearArrayWinners();
    }
    if (mode == 4 && (currentRound == 1 || currentRound == 2)) {
        if (bracket && bracket[1]) {
            for (let i = 0; i < mode; i++) {
                playerElem = document.getElementById(`Player${i + 1}_`);
                resultElem = document.getElementById(`Result${i + 1}_`);
    
                bracket[1].forEach(match => {
                    match.forEach(playerObj => {  
                        let playerName = playerObj.player.username;  
                        if (playerElem && playerElem.textContent.trim() === playerName) {
                            if (playerObj.winner) {
                                resultElem.innerHTML = "&nbsp;&nbsp;👑";
                                if (!winners4.includes(playerName)) {
                                    winners4.push(playerName);
                                }
                            }
                        }
                    });
                });}}
    }
    if (mode == 8 && (currentRound == 1 || currentRound == 2)) {
        if (bracket && bracket[1]) {
            for (let i = 0; i < mode; i++) {
                playerElem = document.getElementById(`Player${i + 1}`);
                resultElem = document.getElementById(`Result${i + 1}`);
                bracket[1].forEach(match => {
                    match.forEach(playerObj => {  
                        let playerName = playerObj.player.username;  
                        if (playerElem && playerElem.textContent.trim() === playerName) {
                            if (playerObj.winner) {
                                resultElem.innerHTML = "&nbsp;&nbsp;👑";
                                if (!winners8.includes(playerName)) {
                                    winners8.push(playerName);
                                }
                            }
                        }
                    });
        });}}
    }
    if (mode == 4 && winners4.length == 2){
        playerElem = document.getElementById(`Player${13}_`);
        if (playerElem){
            playerElem.innerText = winners4[0];
        }
        playerElem = document.getElementById(`Player${14}_`);
        if (playerElem){
            playerElem.innerText = winners4[1];
        }
    }
    if (mode == 8 && winners8.length == 4) {
        playerElem = document.getElementById(`Player${9}`);
        if (playerElem) {
            playerElem.innerText = winners8[0];
        }
        playerElem = document.getElementById(`Player${10}`);
        if (playerElem) {
            playerElem.innerText = winners8[1];
        }
        playerElem = document.getElementById(`Player${11}`);
        if (playerElem) {
            playerElem.innerText = winners8[2];
        }
        playerElem = document.getElementById(`Player${12}`);
        if (playerElem) {
            playerElem.innerText = winners8[3];
        }
    }
    if (mode == 8 && (currentRound == 3 || currentRound == 2)) {
        if (bracket && bracket[2]) {
            for (let i = 8; i < 13; i++) {
                playerElem = document.getElementById(`Player${i + 1}`);
                resultElem = document.getElementById(`Result${i + 1}`);
                bracket[2].forEach(match => {
                    match.forEach(playerObj => {  
                        let playerName = playerObj.player.username;  
                        if (playerElem && playerElem.textContent.trim() === playerName) {
                            if (playerObj.winner) {
                                resultElem.innerHTML = "&nbsp;&nbsp;👑";
                                if (!winners8_final.includes(playerName)) {
                                    winners8_final.push(playerName);
                                }
                            }
                        }
                    });
        });}}
    }
    if (mode == 8 && winners8_final.length == 2){
        playerElem = document.getElementById(`Player${13}`);
        if (playerElem){
            playerElem.innerText = winners8_final[0];
        }
        playerElem = document.getElementById(`Player${14}`);
        if (playerElem){
            playerElem.innerText = winners8_final[1];
        }
    }
}

// Clear brackets from previous players/results
function clearPlayerFields(mode) {
    let playerElem;
    let resultElem;

    winners4 = [];
    winners8 = [];
    winners8_final = [];

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
