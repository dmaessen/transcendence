
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

const baseUrl = "http://localhost:8000/api/authentication/";

function getCSRFToken() {
    const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']");
    return csrfToken ? csrfToken.value : "";
}

document.addEventListener("DOMContentLoaded", function () {
    const signInMenu = document.getElementById("SignInMenu");
    const loginContainer = document.getElementById("loginContainer");
    const registerContainer = document.getElementById("registerContainer");

    document.getElementById("showLogin").addEventListener("click", function () {
        loginContainer.style.display = "block";
        registerContainer.style.display = "none";
    });

    document.getElementById("showRegister").addEventListener("click", function () {
        registerContainer.style.display = "block";
        loginContainer.style.display = "none";
    });

    document.getElementById("backToMain1").addEventListener("click", function () {
        loginContainer.style.display = "none";
    });

    document.getElementById("backToMain2").addEventListener("click", function () {
        registerContainer.style.display = "none";
    });

    // Close forms when modal is closed
    signInMenu.addEventListener("hidden.bs.modal", function () {
        loginContainer.style.display = "none";
        registerContainer.style.display = "none";
    });
});


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

document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            console.log("Register form submitted!");

            const name = document.getElementById("registerName").value;
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
                    body: JSON.stringify({ username, name, email, password }),
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
                    localStorage.setItem("access_token", data.access);
                    localStorage.setItem("refresh_token", data.refresh);
                    const twoFaResponse = await fetch("http://localhost:8000/api/authentication/login-2fa/");
                    if (twoFaResponse.ok) {
                        window.location.href = "/enable-2fa/"; // Redirect to 2FA page
                    } else {
                        alert("Login successful!");
                        window.location.href = "/game_server";
                    }
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
    const logoutButton = document.getElementById("Logout");
    console.log("logout button clicked");

    if (logoutButton) {
        logoutButton.addEventListener("click", function () {
            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            alert("Logged out successfully!");
            window.location.href = "/";
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const deleteAccountBtn = document.getElementById("deleteAccount");

    if (deleteAccountBtn){
        deleteAccountBtn.addEventListener("click", function () {
            if (!confirm("Are you sure you want to delete your account? This is a permanent and definitive!")) 
                {
                return;
                }
                const token = localStorage.getItem("access_token");
                if (!token) {
                    alert("you are currently not logged in. please log in first");
                    return;
                }
                fetch(`${baseUrl}delete/`, {
                method: "DELETE",
                headers: { "Authorization": "Bearer " + token, "Content-Type": "application/json" }
            })
            .then(resp => {
                if (resp.ok) {alert("Your account is now removed permanently");
                    localStorage.removeItem("access_token");
                    window.location.href = "/game_server/";
                }
                else {
                    return response.json().then(data => {
                        alert("Error: " + (data.detail || "Account could not be deleted."));
                    });
                }
            })  
            .catch(error => console.error("Error:", error));
        })
        
    }
});