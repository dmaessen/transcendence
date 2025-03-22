const saveChangesBtn = document.getElementById("saveChanges");

if (saveChangesBtn) {
    saveChangesBtn.addEventListener("click", async function(event) {
        try {
            const newUsername = document.getElementById("newUsername").value;
            const newMail = document.getElementById("newMail").value;
            const newAvatar = document.getElementById("newAvatar").files[0];

            console.log("New Username:", newUsername);
            console.log("New Email:", newMail);

            const formData = new FormData();

            if (newUsername) 
                formData.append("newUsername", newUsername);
            if (newMail)
                formData.append("newMail", newMail);
            if (newAvatar) 
                formData.append("newAvatar", newAvatar);

            const response = await fetch(`/data/api/editProfile/`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // if needed for authentication
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error, status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Edit Data:", data);

            if (newUsername) 
                document.getElementById("username").textContent = data.username;
            if(newMail)
                document.getElementById("userEmail").textContent = data.email;

            if (data.avatar_url) {
                document.getElementById("userAvatar").src = data.avatar_url; // Assuming API returns the new image URL
            }
            loadProfile("self");
        } catch (error) {
            console.error("Error updating profile:", error);
        }
    });
}
