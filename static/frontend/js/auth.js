
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded");
    
    const showLogin = document.getElementById("showLogin");
    const showRegister = document.getElementById("showRegister");
    const loginContainer = document.getElementById("loginContainer");
    const registerContainer = document.getElementById("registerContainer");
    const backToMain1 = document.getElementById("backToMain1");
    const backToMain2 = document.getElementById("backToMain2");

    // Debugging: Check if elements exist
    console.log("Elements found:", {
        showLogin,
        showRegister,
        loginContainer,
        registerContainer,
        backToMain1,
        backToMain2
    });

    if (showLogin) {
        console.log("Login button clicked");
        showLogin.addEventListener("click", function () {
            loginContainer.style.display = "block";
            registerContainer.style.display = "none";
        });
    } else {
        console.warn("showLogin button not found!");
    }

    if (showRegister) {
        console.log("Register button clicked");
        showRegister.addEventListener("click", function () {
            registerContainer.style.display = "block";
            loginContainer.style.display = "none";
        });
    } else {
        console.warn("showRegister button not found!");
    }

    if (backToMain1) {
        backToMain1.addEventListener("click", function () {
            loginContainer.style.display = "none";
        });
    } else {
        console.warn("backToMain1 button not found!");
    }

    if (backToMain2) {
        backToMain2.addEventListener("click", function () {
            registerContainer.style.display = "none";
        });
    } else {
        console.warn("backToMain2 button not found!");
    }
});

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
    const signInButton = document.getElementById("signIn");
    if (signInButton) {
        // console.log("Sign in button found!");
        signInButton.addEventListener("click", function () {
            console.log("Sign in button clicked!");
            const signInModal = new bootstrap.Modal(document.getElementById("SignInMenu"));
            signInModal.show();
        });
    } else {
        console.log("Sign in button NOT found!");
    }
});

// document.addEventListener("DOMContentLoaded", function () {

//     const showLogin = document.getElementById("showLogin");
//     const showRegister = document.getElementById("showRegister");
//     const loginContainer = document.getElementById("loginContainer");
//     const registerContainer = document.getElementById("registerContainer");
//     const backToMain1 = document.getElementById("backToMain1");
//     const backToMain2 = document.getElementById("backToMain2");

//     // Show login form
//     showLogin.addEventListener("click", function () {
//         loginContainer.style.display = "block";
//         registerContainer.style.display = "none";
//     });

//     // Show register form
//     showRegister.addEventListener("click", function () {
//         registerContainer.style.display = "block";
//         loginContainer.style.display = "none";
//     });

//     // Back to main menu
//     backToMain1.addEventListener("click", function () {
//         loginContainer.style.display = "none";
//     });

//     backToMain2.addEventListener("click", function () {
//         registerContainer.style.display = "none";
//     });
// });

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
