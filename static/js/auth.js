// Helper functions
function loadGoogleScript(callback) {
    const script = document.createElement('script');
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = callback;
    document.head.appendChild(script);
}

const baseUrl = "http://localhost:8000/api/authentication/";

// function getCSRFToken() {
//     const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']");
//     return csrfToken ? csrfToken.value : "";
// }

function getCSRFToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
}

function scheduleTokenRefresh() {
    setInterval(async () => {
        console.log("Attempting automatic token refresh...");
        const newAccessToken = await refreshAccessToken();
        if (!newAccessToken) {
            console.warn("Automatic token refresh failed. User may need to re-login soon.");
        }
    }, 29 * 60 * 1000);
}

async function refreshAccessToken() {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
        console.warn("No refresh token found, please login.");
        return null;
    }

    try {
        const response = await fetch(`${baseUrl}refresh/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh: refreshToken }),
        });
        const data = await response.json();

        if (!response.ok) {
            console.error("Refresh token invalid:", data);
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            alert("Session expired. Please log in again.");
            return null;
        }
        localStorage.setItem("access_token", data.access);
        console.log("Access token refreshed.");
        return data.access;
    } catch (error) {
        console.error("Error refreshing token", error);
        return null;
    }
}

// DOM management function
document.addEventListener("DOMContentLoaded", async function () {
        let accessToken = localStorage.getItem("access_token")
        const mainMenu = document.getElementById("mainMenuContainer")
        const signInMenu = document.getElementById("SignInMenu");
        const signInButton = document.getElementById("signIn");
        const loginContainer = document.getElementById("loginContainer");
        const registerContainer = document.getElementById("registerContainer");
        const qrContainer = document.getElementById("qrContainer");
        const showLogin = document.getElementById("showLogin");
        const showRegister = document.getElementById("showRegister");
        const backToMain1 = document.getElementById("backToMain1");
        const backToMain2 = document.getElementById("backToMain2");
        const qrBack = document.getElementById("QR_back");
        const confirm2FA = document.getElementById("confirm2FA");
        const disable2FA = document.getElementById("disable2FA");
        const submitOTP = document.getElementById("submitOTPButton");
        const returnOTP = document.getElementById("returnToLogin");
        const logoutButton = document.getElementById("logoutBtn");
        const deleteAccountBtn = document.getElementById("deleteAccount");
        const enable2FAButton = document.getElementById("enable2FA");
        const qrCodeImage = document.getElementById("qrCodeImage");
        const otpKey = document.getElementById("otpKey");
        const otpInputContainer = document.getElementById("otpContainer");
        const otpInput = document.getElementById("otpToken");
        const loginForm = document.getElementById("loginForm");
        const registerForm = document.getElementById("registerForm");
        const gameMenu = document.getElementById("gameMenuFirst")

        const SignInModal = bootstrap.Modal.getOrCreateInstance(signInMenu);
        const gameMenuModal = bootstrap.Modal.getOrCreateInstance(gameMenu);
        if (!accessToken) {
            console.log("No access token found. Showing SignInMenu...");
            SignInModal.show();
            gameMenuModal.hide();
        } else {
            console.log("User already logged in. Hiding SignInMenu");
            SignInModal.hide();
            gameMenuModal.show();
        }

        if (showLogin) {
            showLogin.addEventListener("click", function () {
                mainMenuContainer.style.display = "none";
                loginContainer.style.display = "block";
            });
        }
        if (showRegister) {
            showRegister.addEventListener("click", function () {
                mainMenuContainer.style.display = "none";
                loginContainer.style.display = "block";
            });
        }
        if (showLogin && loginContainer && registerContainer) {
            showLogin.addEventListener("click", function () {
                loginContainer.style.display = "block";
                registerContainer.style.display = "none";
            });
        }
        if (showRegister && loginContainer && registerContainer) {
            showRegister.addEventListener("click", function () {
                registerContainer.style.display = "block";
                loginContainer.style.display = "none";
            });
        }
        if (backToMain1 && loginContainer) {
            backToMain1.addEventListener("click", function () {
                loginContainer.style.display = "none";
                mainMenuContainer.style.display = "block";
            });
        }
        if (backToMain2 && registerContainer) {
            backToMain2.addEventListener("click", function () {
                registerContainer.style.display = "none";
                mainMenuContainer.style.display = "block";
            });
        }
        if (qrBack && qrContainer) {
            qrBack.addEventListener("click", function () {
                qrContainer.style.display = "none";
            });
        }

        if (signInButton && signInMenu) {
            signInButton.addEventListener("click", function () {
                const signInModal = new bootstrap.Modal(signInMenu);
                signInModal.show();
            });
        }

        const urlParams = new URLSearchParams(window.location.search);
        const ftCode = urlParams.get("code");
        if (ftCode) {
            try {
                const response = await fetch("/api/authentication/42/callback/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ code: ftCode }),
                });
                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem("access_token", data.access);
                    localStorage.setItem("refresh_token", data.refresh);
                    scheduleTokenRefresh();
                    if (signInMenu) {
                        const signInModal = bootstrap.Modal.getInstance(signInMenu);
                        if (signInModal) signInModal.hide();
                    }
                    alert("42 login successful!");
                    setTimeout(() => {
                        window.location.href = "/";
                    }, 30);
                } else {
                    alert("42 login failed: " + (data.error || JSON.stringify(data)));
                }
            } catch (error) {
                console.error("Error handling 42 code:", error);
                alert("An error occurred during 42 login.");
            }
        }
        const urlAccessToken = urlParams.get("access");
        const urlRefreshToken = urlParams.get("refresh");
        if (urlAccessToken && urlRefreshToken) {
            localStorage.setItem("access_token", urlAccessToken);
            localStorage.setItem("refresh_token", urlRefreshToken);
            alert("Google login successful!");
            window.history.replaceState({}, document.title, "/game_server");
            setTimeout(() => {
                window.location.href = "/";
            }, 30);
        }
        const googleClientId = document
            .querySelector('meta[name="google-signin-client_id"]')
            ?.getAttribute("content");
        if (googleClientId) {
            loadGoogleScript(() => {
                if (window.google) {
                    google.accounts.id.initialize({
                        client_id: googleClientId,
                        callback: async (response) => {
                            try {
                                const result = await fetch("/api/authentication/google-login/", {
                                    method: "POST",
                                    headers: {
                                        "Content-Type": "application/json",
                                        "X-CSRFToken": getCSRFToken(),
                                    },
                                    body: JSON.stringify({ id_token: response.credential }),
                                });
                                const data = await result.json();
                                if (result.ok) {
                                    localStorage.setItem("access_token", data.access);
                                    localStorage.setItem("refresh_token", data.refresh);
                                    scheduleTokenRefresh();
                                    if (signInMenu) {
                                        const signInModal = bootstrap.Modal.getInstance(signInMenu);
                                        if (signInModal) signInModal.hide();
                                    }

                                    window.location.href = "/";
                                } else {
                                    alert("Google login failed: " + (data.error || JSON.stringify(data)));
                                }
                            } catch (error) {
                                console.error("Error during Google login:", error);
                                alert("An error occurred during Google login.");
                            }
                        },
                    });
                    const googleButtonRegister = document.getElementById("googleButtonRegister");
                    if (googleButtonRegister) {
                        googleButtonRegister.addEventListener('click', () => {
                            window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=http://localhost:8000/api/authentication/google/callback/&response_type=code&scope=openid%20email%20profile`;
                        });
                    }
                    const googleButtonLogin = document.getElementById("googleButtonLogin");
                    if (googleButtonLogin) {
                        googleButtonLogin.addEventListener('click', () => {
                            window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=http://localhost:8000/api/authentication/google/callback/&response_type=code&scope=openid%20email%20profile`;
                        });
                    }
                }
            });
        }

        const FtSignInLogDiv = document.getElementById("FtInButtonLogin");
        if (FtSignInLogDiv) {
            FtSignInLogDiv.innerHTML = `
                <a href="/api/authentication/42/login/" class="btn btn-outline-dark w-100 mb-2 d-flex align-items-center justify-content-start" style="gap: 10px;">
                    <img src="/static/images/42_Logo.png" alt="42 Logo" style="height: 20px;">
                    <span>Sign in with 42</span>
                </a>
            `;
        }
        const FtSignInRegDiv = document.getElementById("FtInButtonRegister");
        if (FtSignInRegDiv) {
            FtSignInRegDiv.innerHTML = `
                <a href="/api/authentication/42/login/" class="btn btn-outline-dark w-100 mb-2 d-flex align-items-center justify-content-start" style="gap: 10px;">
                    <img src="/static/images/42-logo.png" alt="42 Logo" style="height: 20px;">
                    <span>Sign in with 42</span>
                </a>
            `;
        }

        if (registerForm) {
            registerForm.addEventListener("submit", async function (e) {
                // e.preventDefault();
                const name = document.getElementById("registerName").value;
                const username = document.getElementById("registerUsername").value;
                const email = document.getElementById("registerEmail").value;
                const password = document.getElementById("registerPassword").value;
                const enable2FA = document.getElementById("enable2FAonRegister")?.checked;
                try {
                    const registerData = await fetch(`${baseUrl}register/`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken(),
                        },
                        body: JSON.stringify({ username, name, email, password }),
                    });
                    const registrationDataResponse = await registerData.json();
                    if (!registerData.ok) {
                        if (registerData.status == 400) {
                            alert("registration failed, user may already exist")
                        } else {
                            alert(`Registration failed: ${JSON.stringify(registerData)}`);
                        }
                        return;
                    }
                    alert("Registration successful! You will now be logged in automatically");
                    const accessToken = registrationDataResponse.access;
                    const refreshToken = registrationDataResponse.refresh;
                    if (!accessToken || !refreshToken) {
                        alert("Registration successful, but failed to retrieve tokens.");
                        return;
                    }
                    localStorage.setItem("access_token", accessToken);
                    localStorage.setItem("refresh_token", refreshToken);
                    if (!localStorage.getItem("access_token") || !localStorage.getItem("refresh_token")) {
                        alert("Login failed somehow");
                        return;
                    }
                    scheduleTokenRefresh()
                    if (enable2FA) {
                        let refreshedToken = await refreshAccessToken();
                        const tokenToUse = refreshedToken || accessToken;
                        const twoFAResponse = await fetch(`${baseUrl}register-2fa/`, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "Authorization": `Bearer ${tokenToUse}`,
                            },
                        });
                        const twoFAData = await twoFAResponse.json();
                        if (!twoFAResponse.ok) {
                            alert(`2FA Setup Failed: ${JSON.stringify(twoFAData)}`);
                            return;
                        }
                        if (!twoFAData.qr_code) {
                            alert("2FA response missing QR code.");
                            return;
                        }
                        registerContainer.style.display = "none";
                        qrContainer.style.display = "block";
                        qrCodeImage.src = `${twoFAData.qr_code}`;
                        qrCodeImage.style.display = "block";
                        otpKey.innerText = twoFAData.otp_secret;
                    }
                    setTimeout(() => {
                        window.location.href = "/";
                    }, 30);
                    
                } catch (error) {
                    console.error("Error:", error);
                    alert("An error occurred. Check the console.");
                }
            });
        }

        function saveLoginCredentials(email, password) {
            sessionStorage.setItem("loginEmail", email);
            sessionStorage.setItem("loginPassword", password);
        }
        function getSavedLoginCredentials() {
            return {
                email: sessionStorage.getItem("loginEmail"),
                password: sessionStorage.getItem("loginPassword")
            }
        }
        async function loginRequest(email, password, otp_token = null) {
            if (localStorage.getItem("refresh_token")) {
                await refreshAccessToken();
            }
            try {
                const requestBody = { email, password };
                if (otp_token) requestBody.otp_token = otp_token;
                const response = await fetch(`${baseUrl}login/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify(requestBody),
                });
                const data = await response.json().catch(() => ({})); // 
                if (response.status === 403 && data.detail?.includes("CSRF")) {
                    alert("CSRF token validation failed. Please refresh the page or check your login security settings.");
                    console.error("CSRF error details:", data);
                    return;
                }

                // const data = await response.json();
                if (response.ok) {
                    localStorage.setItem("access_token", data.access);
                    localStorage.setItem("refresh_token", data.refresh);
                    setTimeout(() => {
                        window.location.href = "/";
                    }, 30);
                    // Optionally: open websocket here after refreshing token
                    // await loginWebSocket();
                } else if (response.status === 403) {
                    otpInputContainer.style.display = "block";
                    loginForm.style.display = "none";
                    alert("2FA required. enter your OTP code please.");
                } else if (response.status === 401 && data["2fa_required"]) {
                    alert("wrong OTP code entered, please try again");
                } else {
                    alert("login failed, check credentials");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("An error occurred. Check the console.");
            }
        }
        if (loginForm) {
            loginForm.addEventListener("submit", async function (e) {
                // e.preventDefault();
                const email = document.getElementById("loginEmail").value.trim();
                const password = document.getElementById("loginPassword").value.trim();
                saveLoginCredentials(email, password);
                await loginRequest(email, password);
            });
        }
        if (returnOTP && showLogin && otpInputContainer && loginContainer) {
            showLogin.addEventListener("click", function () {
                otpInputContainer.style.display = "none";
                loginContainer.style.display = "block";
            });
        }
        if (submitOTP && otpInput && otpInputContainer) {
            submitOTP.addEventListener("click", async function () {
                const { email, password } = getSavedLoginCredentials();
                const otp_token = otpInput.value.trim();
                if (!otp_token) {
                    alert("Please enter the OTP token.");
                    return;
                }
                await loginRequest(email, password, otp_token);
            });
        }

        if (logoutButton) {
            logoutButton.addEventListener("click", function () {
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                alert("Logged out successfully!");
                window.location.href = "/game_server/";
            });
        }

        if (deleteAccountBtn) {
            deleteAccountBtn.addEventListener("click", async function () {
                if (!confirm("Are you sure you want to delete your account? This is a permanent and definitive!")) {
                    return;
                }
                let token = localStorage.getItem("access_token");
                if (!token) {
                    token = await refreshAccessToken();
                    if (!token) {
                        alert("you are currently not logged in. please log in first");
                        return;
                    }
                }
                fetch(`${baseUrl}delete/`, {
                    method: "DELETE",
                    headers: { "Authorization": "Bearer " + token, "Content-Type": "application/json" }
                })
                .then(resp => {
                    if (resp.status === 204) {
                        alert("Your account is now removed permanently");
                        localStorage.removeItem("access_token");
                        localStorage.removeItem("refresh_token");
                        window.location.href = "/game_server/";
                    } else {
                        return resp.json().then(data => {
                            alert("Error: " + (data.detail || "Account could not be deleted."));
                        });
                    }
                });
            });
        }
        if (enable2FAButton) {
            enable2FAButton.addEventListener("click", async function () {
                let accessToken = localStorage.getItem("access_token");
                if (!accessToken) {
                    accessToken = await refreshAccessToken();
                    if (!accessToken) {
                        alert("You are not logged in, please do so now.");
                        window.location.href = "/game_server/";
                        return;
                    }
                }
                try {
                    const twoFAResponse = await fetch(`${baseUrl}register-2fa/`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${accessToken}`,
                        },
                    });
                    const twoFAData = await twoFAResponse.json();
                    if (!twoFAResponse.ok) {
                        alert(`2FA Setup Failed: ${JSON.stringify(twoFAData)}`);
                        return;
                    }
                    if (!twoFAData.qr_code) {
                        alert("2FA response missing QR code.");
                        return;
                    }
                    if (registerContainer) registerContainer.style.display = "none";
                    if (qrContainer) qrContainer.style.display = "block";
                    if (qrCodeImage) {
                        qrCodeImage.src = `${twoFAData.qr_code}`;
                        qrCodeImage.style.display = "block";
                    }
                    if (otpKey) otpKey.innerText = twoFAData.otp_secret;
                } catch (error) {
                    console.error("Error registering 2FA:", error);
                    alert("there have been issues, please start panicking!");
                }
            });
        }
        if (confirm2FA && qrContainer) {
            confirm2FA.addEventListener("click", async function () {
                try {
                    const response = await fetch(`${baseUrl}enable-2fa/`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                            "X-CSRFToken": getCSRFToken(),
                        },
                    });
                    if (response.ok) {
                        alert("2FA enabled!");
                        qrContainer.style.display = "none";
                    } else if (response.status === 500) {
                        alert("there was an issue generating the otp code");
                    } else {
                        alert("2FA failure :(");
                    }
                } catch (error) {
                    console.error("Error confirming 2FA :(", error);
                }
            });
        }
        if (disable2FA) {
            disable2FA.addEventListener("click", async function () {
                let access_token = localStorage.getItem("access_token");
                if (!access_token) {
                    access_token = await refreshAccessToken();
                    if (!access_token) {
                        alert("you are not logged in, please do so now");
                        return;
                    }
                }
                await fetch(`${baseUrl}disable-2fa/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${access_token}`,
                        "X-CSRFToken": getCSRFToken(),
                    },
                });
                alert("2FA disabled");
            });
        }
});
