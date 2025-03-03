
const baseUrl = "http://localhost:8000/api/authentication";

function getCSRFToken() {
    const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']");
    return csrfToken ? csrfToken.value : "";
}

// document.getElementById("registerForm").addEventListener("submit", async function (e) {
//     console.log("script.js loaded successfully!, registerform");
//     e.preventDefault();
//     console.log("Register form submitted!");
//     const username = document.getElementById("registerUsername").value;
//     const email = document.getElementById("registerEmail").value;
//     const password = document.getElementById("registerPassword").value;

//     console.log("sending data: ", { email, password });
//     try{
//         const response = await fetch(`${baseUrl}/register/`, {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ username, email, password }),
//         });

//         const data = await response.json();
//         console.log("Server response:", data);
//         if (response.ok) {
//             alert("Registration successful! You can now log in.");
//         } else {
//             alert(`Error: ${JSON.stringify(data)}`);
//         }
//     } catch (error) {
//         console.error("Error: ", error);
//         alert("An error occured. check the console")
//     }
// });

// document.getElementById("loginForm").addEventListener("submit", async function (e) {
//     console.log("script.js loaded successfully!, loginform");
//     e.preventDefault();
//     console.log("Login form submitted!");

//     const username = document.getElementById("loginUsername").value;
//     const password = document.getElementById("loginPassword").value;

//     console.log("Sending data:", { email, password });
    
//     try {
//         const response = await fetch(`${baseUrl}/login/`, {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ username, password }),
//         });

//         const data = await response.json();
//         console.log("Server response:", data);
//         if (response.ok) {
//             localStorage.setItem("access", data.access);
//             localStorage.setItem("refresh", data.refresh);
//             alert("Login successful!");
//         } else {
//             alert("Login failed!");
//         }
//     } catch (error) {
//         console.error("Error:", error);
//         alert("An error occured. Check the console.");
//     }
// });

document.addEventListener("DOMContentLoaded", function () {
    // Ensure Bootstrap is loaded
    console.log("auth.js fully loaded!");
    const signInButton = document.getElementById("signIn");
    if (signInButton) {
        console.log("Sign in button found!");
        signInButton.addEventListener("click", function () {
            console.log("Sign in button clicked!");
            const signInModal = new bootstrap.Modal(document.getElementById("SignInMenu"));
            signInModal.show();
        });
    } else {
        console.log("Sign in button NOT found!");
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            console.log("Register form submitted!");

            const username = document.getElementById("registerUsername").value;
            const email = document.getElementById("registerEmail").value;
            const password = document.getElementById("registerPassword").value;

            try {
                const response = await fetch(`${baseUrl}register/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ username, email, password }),
                });

                const data = await response.json();
                console.log("Server response:", data);

                if (response.ok) {
                    alert("Registration successful! You can now log in.");
                    window.location.reload(); // Reload page to show login form
                } else {
                    alert(`Error: ${JSON.stringify(data)}`);
                }
            } catch (error) {
                console.error("Error:", error);
                alert("An error occurred. Check the console.");
            }
        });
    }
})

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            console.log("Login form submitted!");

            const email = document.getElementById("loginEmail").value;
            const password = document.getElementById("loginPassword").value;

            try {
                const response = await fetch(`${baseUrl}login/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();
                console.log("Server response:", data);

                if (response.ok) {
                    localStorage.setItem("access", data.access);
                    localStorage.setItem("refresh", data.refresh);
                    alert("Login successful!");
                    window.location.href = "index.html"; // Redirect to home page
                } else {
                    alert("Login failed! Check your credentials.");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("An error occurred. Check the console.");
            }
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const logoutButton = document.getElementById("logoutButton");

    if (logoutButton) {
        logoutButton.addEventListener("click", function () {
            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            alert("Logged out successfully!");
            window.location.reload();
        });
    }
});

document.addEventListener("closeRegister").addEventListener("click", function (){
    // const registerMenu = document.getElementById("registerMenu");
    // registerMenu.style.display = "none";
    // registerMenu.setAttribute("aria-hidden", "true");
    // registerMenu.removeAttributeNode("tabindex");
    console.log("closeregister");
    signInModal.hide();
})