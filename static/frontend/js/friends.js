const friendsBtn = document.getElementById("friendsBnt");

if(friendsBtn) {
    friendsBtn.addEventListener("click", function() {
        fetch(`/data/api/friendsData`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                "Content-Type": "application/json",
            },
        })
        .then(response => {
            if (!response.ok)
                {
                throw new Error(`HTML error, status: ${response.status}`)
            }
            return response.json();
            })
        .then(data => {
            // console.log("Raw response:", data);

        })
            // .then(response => response.json())
        .catch(error => console.error("Error fetching user data:", error));
    })
}