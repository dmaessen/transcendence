// const editProfileBtn = document.getElementById("editProfileBtn");

// if (editProfileBtn) {
//     editProfileBtn.addEventListener("click", function () {
//         fetch(`/data/api/userData/`, {
//             method: "GET",
//             headers: {
//                 "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
//                 "Content-Type": "application/json",
//             },
//         })
//         .then(response => {
//             if (!response.ok)
//                 {
//                 throw new Error(`HTML error, status: ${response.status}`)
//             }
//             return response.json();
//             })
//         .then(data => {
//             console.log("edit response:", data);

//             document.getElementById("newUsername").value = data.username;
//             document.getElementById("newMail").value = data.email;

//         })
//             // .then(response => response.json())
//         .catch(error => console.error("Error fetching user data:", error));
//     });
// }

const saveChangesBnt = document.getElementById("saveChanges");

if (saveChangesBnt){
    saveChangesBnt.addEventListener("click", function(event) {
        event.preventDefault();
        const newUsername = document.getElementById("newUsername").value;
        const newMail = document.getElementById("newMail").value;
        const newAvatar = document.getElementById("newAvatar").files[0];

        console.log("New Username:", newUsername);
        console.log("New Email:", newMail);

        const formData = new FormData();

        if(newUsername)
            formData.append("newUsername", newUsername);
        if(newMail)
            formData.append("newMail", newMail);
        if(newAvatar)
            formData.append("newAvatar", newAvatar);

        fetch(`/data/api/editProfile/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // if needed for authentication
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error, status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Profile updated successfully:", data);
            // Update DOM
            document.getElementById("username").textCotent = data.username;
            document.getElementById("userEmail").textContent = data.email;
            if (data.avatar_url) {
                document.getElementById("userAvatar").src = data.avatar_url; // Assuming API returns the new image URL
            }
             // Close edit modal
             let editProfileModalElement = document.getElementById("editProfileModal");
             let editProfileModal = bootstrap.Modal.getInstance(editProfileModalElement);
             editProfileModal.hide();

             // Delete profile modal
            //  let modalElement = document.getElementById("profileModal");
            //  let modal = bootstrap.Modal.getOrCreateInstance(modalElement);
            //  modal.dispose(); 

             if (profileBtn) {
                setTimeout(() => profileBtn.click(), 300); // Small delay to avoid Bootstrap issues
            }
             
            //  // Open new profile modal
            //  let profileModalElement = document.getElementById("profileModal");
            //  let profileModal = new bootstrap.Modal(profileModalElement);
            //  profileModal.show();
        })
        .catch(error => console.error("Error updating profile:", error));
    })
}
