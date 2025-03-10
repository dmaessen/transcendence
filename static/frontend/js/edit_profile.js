const editProfileBtn = document.getElementById("editProfileBtn");

if (editProfileBtn) {
    editProfileBtn.addEventListener("click", function () {
        fetch(`/data/api/userData/`, {
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
            console.log("edit response:", data);

            document.getElementById("newUsername").value = data.username;
            document.getElementById("newMail").value = data.email;

        })
            // .then(response => response.json())
        .catch(error => console.error("Error fetching user data:", error));
    });
}

document.addEventListener("click", function() {
    document.getElementById("saveChanges");
    const newUsername = document.getElementById("newUsername");
    const newMail = document.getElementById("newMail");
    const newAvatar = document.getElementById("newAvatar");

    
})