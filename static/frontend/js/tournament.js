let winners4 = JSON.parse(localStorage.getItem("winners4")) || [];
let winners8 = JSON.parse(localStorage.getItem("winners8")) || [];
let winners8_final = JSON.parse(localStorage.getItem("winners8_final")) || [];
let winner_final = JSON.parse(localStorage.getItem("winner_final")) || [];

let tournamentInterval = null;

async function selectTournamentBtn() {
    try{
        const data = await fetchData(`/tournament-status/`, {
        });
        if (data) {
            console.log("data: ", data);
            if (data.players_in > 0 && !data.running) {
                document.getElementById("tournamentBtn").textContent = "Join tournament";
                document.getElementById("tournamentBtn").addEventListener("click", () => {
                    gameMenuTournament.hide();
                    joinTournament(data);
                });
            }
            else if (data.running) {
                console.log("tournament is running atm");
                document.getElementById("tournamentBtn").style.display = "none"; // to hide the button
            }
            else {
                document.getElementById("tournamentBtn").textContent = "Start new tournament";
                document.getElementById("tournamentBtn").addEventListener("click", () => {
                    gameMenuTournament.show();
                    gameMenu.hide();});
            }
        }
    } catch (error){
        console.log("Error while fetching tournament data: ", error);
    }
}

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
    tournamentInterval = setInterval(async () => await updateBracketWithData(mode), 3000); // Auto-update every 3s
}

const stopTournamentUpdates = async (mode) => {
    await sleep(4000);
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
            if (!data.running && data.players_in == 0)
                clearPlayerFields(mode); // to make sure all fields are clean when starting
            if (data.remaining_spots == 0)
                updatePlayerFields(mode, data.players, data.results);
        }
    } catch (error) {
        console.error("Error fetching tournament status:", error);
    }
    updateBracket(mode);
}

function updatePlayerFields(mode, players) {
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
    localStorage.setItem("winners4", JSON.stringify([]));
    localStorage.setItem("winners8", JSON.stringify([]));
    localStorage.setItem("winners8_final", JSON.stringify([]));
    localStorage.setItem("winner_final", JSON.stringify([]));
}

async function updateBracket(mode) {
    console.log("Updating bracket with mode:", mode);

    let playerElem;
    let resultElem;

    if (mode == 4) {
        for (let i = 0; i < mode; i++) {
            playerElem = document.getElementById(`Player${i + 1}_`);
            resultElem = document.getElementById(`Result${i + 1}_`);
    
            winners4 = JSON.parse(localStorage.getItem("winners4")) || [];
            if (playerElem && winners4.includes(playerElem.textContent.trim())) {
                resultElem.innerHTML = "&nbsp;&nbsp;👑";
            }
        }

        winners4 = JSON.parse(localStorage.getItem("winners4")) || [];
        if (winners4.length === 2) {
            const playerElem13 = document.getElementById("Player13_");
            const playerElem14 = document.getElementById("Player14_");
            if (playerElem13) {
                playerElem13.innerText = winners4[0];
            }
            if (playerElem14) {
                playerElem14.innerText = winners4[1];
            }
        }

        winner_final = JSON.parse(localStorage.getItem("winner_final")) || [];
        if (winner_final.length === 1) {
            playerElem = document.getElementById(`Player${13}_`);
            if (playerElem && playerElem.textContent.trim() === winner_final) {
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

            await stopTournamentUpdates(mode);
            await clearArrayWinners();
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify({ action: "disconnect" }));
            }
            return;
        }
    }

    if (mode == 8) {
        for (let i = 0; i < mode; i++) {
            playerElem = document.getElementById(`Player${i + 1}`);
            resultElem = document.getElementById(`Result${i + 1}`);
    
            winners8 = JSON.parse(localStorage.getItem("winners8")) || [];
            if (playerElem && winners8.includes(playerElem.textContent.trim())) {
                resultElem.innerHTML = "&nbsp;&nbsp;👑";
            }
        }

        winners8 = JSON.parse(localStorage.getItem("winners8")) || [];
        if (winners8.length === 4) {
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

        winners8_final = JSON.parse(localStorage.getItem("winners8_final")) || [];
        if (winners8_final.length === 2) {
            for (let i = 0; i < 4; i++) {
                playerElem = document.getElementById(`Player${i + 9}`);
                resultElem = document.getElementById(`Result${i + 9}`);
        
                winners8_final = JSON.parse(localStorage.getItem("winners8_final")) || [];
                if (playerElem && winners8_final.includes(playerElem.textContent.trim())) {
                    resultElem.innerHTML = "&nbsp;&nbsp;👑";
                }
            }
        }

        winners8_final = JSON.parse(localStorage.getItem("winners8_final")) || [];
        if (winners8_final.length === 2) {
            const playerElem13 = document.getElementById("Player13");
            const playerElem14 = document.getElementById("Player14");
            if (playerElem13) {
                playerElem13.innerText = winners8_final[0];
            }
            if (playerElem14) {
                playerElem14.innerText = winners8_final[1];
            }
        }

        winner_final = JSON.parse(localStorage.getItem("winner_final")) || [];
        if (winner_final.length === 1) {
            playerElem = document.getElementById(`Player${13}`);
            if (playerElem && playerElem.textContent.trim() === winner_final) {
                resultElem = document.getElementById(`Result${13}`);
                if (resultElem) {
                    resultElem.innerHTML = "&nbsp;&nbsp;👑";
                }
            } else {
                resultElem = document.getElementById(`Result${14}`);
                if (resultElem) {
                    resultElem.innerHTML = "&nbsp;&nbsp;👑";
                }
            }

            await stopTournamentUpdates(mode);
            await clearArrayWinners();
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify({ action: "disconnect" }));
            }
            return;
        }
    }
}

// Clear brackets from previous players/results
function clearPlayerFields(mode) {
    let playerElem;
    let resultElem;

    localStorage.setItem("winners4", JSON.stringify([]));
    localStorage.setItem("winners8", JSON.stringify([]));
    localStorage.setItem("winners8_final", JSON.stringify([]));
    localStorage.setItem("winner_final", JSON.stringify([]));

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
                resultElem.innerHTML = "&nbsp;";
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
                resultElem.innerHTML = "&nbsp;";
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
                resultElem.innerHTML = "&nbsp;";
            }
        }
    }
}
