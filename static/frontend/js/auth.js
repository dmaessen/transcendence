let loginsocket;

async function loginWebSocket(){
    console.log("Let's open those sockets bebê");
    try {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        loginsocket = new WebSocket(`${protocol}://${window.location.host}/ws/online_users/`);

        loginsocket.onopen =  async(event) => {
            console.log("onlineSocket openned");
            pingInterval = setInterval(() => {
                loginsocket.send(JSON.stringify({ type: "ping", message: "Haroooooooo!" }));
            }, 15000);
        }
        loginsocket.onmessage = (event) => {
            console.log("Received message:", event.data);
        };
        loginsocket.onclose = (event) => {
            console.log("onlineSocket closed", event);
            clearInterval(pingInterval);
            // window.location.reload();        
        };
        loginsocket.onerror = async function(error) {
            console.error("onlineSocket error:", error);
        };
    } catch (errror) {
        console.log("Error: ", errror);
    }
}

const baseUrl = `https://${window.location.host}/api/authentication/`;
// Helper functions
function loadGoogleScript(callback) {
    const script = document.createElement('script');
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = callback;
    document.head.appendChild(script);
}

async function checkLoginStatus() {
    console.log("Checking login status...");
    await refreshAccessToken();
    try {
        const response = await fetch(`${baseUrl}me/`, {
            method: "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
        });

        if (!response.ok) {
            console.warn(`[checkLoginStatus] Status: ${response.status} ${response.statusText}`);
            return false;
        }

        const data = await response.json();

        if (data.error) {
            console.warn("User is not authenticated", data.error);
            return false;
        } 
        console.log("User is authenticated:", data);
        return true;
    } catch (err) {
        console.log("Error checking login status:", err);
        return false;
    }
}

async function fetchUserData() {
    console.log("Fetching user data...");
    try {
        const response = await fetch(`${baseUrl}data/`, {
            method: "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
        });

        if (response.status === 401) {
            // refresh if token expired
            await fetch("/api/authentication/refresh/", {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
            });
            return fetchUserData();
        }

        const data = await response.json();
        if (data){
            console.log("Data:", data);
            return data 
        } else {
            return "invalid login"
        }
    } catch (error) {
        console.log("Error fetching data:", error);
    }
}

function getCSRFToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
}

async function refreshAccessToken() {
    console.log("Refreshing access token...");
    try {
        const response = await fetch(`${baseUrl}refresh/`, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
        });
        const data = await response.json();
        if (!response.ok) {
            console.error("Refresh token invalid:", data);
            return null;
        }
        console.log("Access token refreshed.");
        return data.access_token;
    } catch (error) {
        console.error("Error refreshing token", error);
        return null;
    }
}

// DOM management function
document.addEventListener("DOMContentLoaded", async function () {
        const mainMenu = document.getElementById("mainMenuContainer");
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
        const qrBackProfile = document.getElementById("QR_backProfile");
        const confirm2FA = document.getElementById("confirm2FA");
        const confirm2FAProfile = document.getElementById("confirm2FAProfile");
        const disable2FA = document.getElementById("disable2FA");
        const submitOTP = document.getElementById("submitOTPButton");
        const returnOTP = document.getElementById("returnToLogin");
        const logoutButton = document.getElementById("logoutBtn");
        const deleteAccountBtn = document.getElementById("deleteAccount");
        const qrCodeImage = document.getElementById("qrCodeImage");
        const otpKey = document.getElementById("otpKey");
        const otpInputContainer = document.getElementById("otpContainer");
        const otpInput = document.getElementById("otpToken");
        const loginForm = document.getElementById("loginForm");
        const registerForm = document.getElementById("registerForm");
        const gameMenu = document.getElementById("gameMenuFirst");
        const qrContainerProfile = document.getElementById("qrContainerProfile");
        const enable2FAButton = document.getElementById("enable2FA");

        const SignInModal = bootstrap.Modal.getOrCreateInstance(signInMenu);
        const gameMenuModal = bootstrap.Modal.getOrCreateInstance(gameMenu);

        let user_logged = await checkLoginStatus();
        if (!user_logged) {
            console.log("No access token found. Showing SignInMenu...");
            SignInModal.show();
            gameMenuModal.hide();
        } else {
            console.log("User already logged in. Hiding SignInMenu");
            SignInModal.hide();
            gameMenuModal.show();
            if (!loginsocket || loginsocket.readyState !== WebSocket.OPEN) {
                await loginWebSocket();
            }
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
                registerContainer.style.display = "block";
            });
        }

        if (qrBackProfile && qrContainerProfile) {
            qrBackProfile.addEventListener("click", function () {
                qrContainerProfile.style.display = "none";
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
                console.log("42 code:", ftCode);
                const response = await fetch("/api/authentication/42/callback/", {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ code: ftCode }),
                });

                let data = {}
                try {
                    await response.json();
                } catch (jsonError) {
                    console.warn("response is not valid JSON");
                    data = { error: "unexpected response format"};
                }
                if (response.ok) {
                    alert("42 login successful!");
                    window.location.href = "/";
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
            alert("Google login successful!");
            window.history.replaceState({}, document.title, "/");
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
                                    credentials: "include",
                                    headers: {
                                        "Content-Type": "application/json",
                                        "X-CSRFToken": getCSRFToken(),
                                    },
                                    body: JSON.stringify({ id_token: response.credential }),
                                });
                                const data = await result.json();
                                if (result.ok) {
                                    alert("google login successful")
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
                            window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=https://localhost:8443/api/authentication/google/callback/&response_type=code&scope=openid%20email%20profile`;
                        });
                    }
                    const googleButtonLogin = document.getElementById("googleButtonLogin");
                    if (googleButtonLogin) {
                        googleButtonLogin.addEventListener('click', () => {
                            window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=https://localhost:8443/api/authentication/google/callback/&response_type=code&scope=openid%20email%20profile`;
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
                e.preventDefault();
                const name = document.getElementById("registerName").value;
                const username = document.getElementById("registerUsername").value;
                const email = document.getElementById("registerEmail").value;
                const password = document.getElementById("registerPassword").value;
                const enable2FACheck = document.getElementById("enable2FAonRegister")?.checked;
                
                let registerData
                try {
                        registerData = await fetch(`${baseUrl}register/`, {
                        method: "POST",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken(),
                        },
                        body: JSON.stringify({ username, name, email, password }),
                    });
                } catch (err) {
                        console.error("error trying to register", err);
                        return
                }
                console.log("registerdata: ", registerData);
                try {
                    if (!registerData.ok) {
                        let errorMsg = `Error ${registerData.status}`;
                        try {
                            const errorJson = await registerData.json();
                            errorMsg += `: ${errorJson.error || JSON.stringify(errorJson)}`;
                        } catch (err) {
                            const errorText = await registerData.text();
                            errorMsg += `: ${errorText}`;
                        }
                        alert(`Registration failed: ${errorMsg}`);
                        return;
                    }
                    alert("Registration successful! You will now be logged in automatically");
                    if (!enable2FACheck)
                        window.location.href = "/";
                    if (enable2FACheck) {
                        let twoFAResponse;
                        try {
                            twoFAResponse = await fetch(`${baseUrl}register-2fa/`, {
                                method: "POST",
                                credentials: "include",
                                headers: {
                                    "Content-Type": "application/json",
                                    "X-CSRFToken": getCSRFToken(),
                                },
                            });
                        } catch (err) {
                            console.error("error trying to register using 2fa", err);
                            alert ("2fa register issue");
                            return;
                        }
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
                    }
                } catch (error) {
                    console.error("Error in registration flow:", error);
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
            try {
                const requestBody = { email, password };
                if (otp_token) requestBody.otp_token = otp_token;
                const response = await fetch(`${baseUrl}login/`, {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify(requestBody),
                });
                console.log("login response object:", response);

                let data;
                try {
                    data = await response.json();
                } catch (jsonError) {
                    console.error("Failed to parse login response JSON", jsonError);
                    data = {};
                }
            
                console.log("login response data:", data);
                if (response.ok) {
                    alert("logged in succesfully")
                    window.location.href = "/";
                    setTimeout(() => {
                        window.location.href = "/";
                    }, 30);
                } else if (response.status === 403 && data.detail?.includes("CSRF")) {
                    alert("CSRF token validation failed. Please refresh the page or check your login security settings.");
                    console.error("CSRF error details:", data);
                    return;
                }
                else if (response.status === 403) {
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
                e.preventDefault();
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
            logoutButton.addEventListener("click", async function () {
                try {
                    const response = await fetch(`${baseUrl}sign_out/`, {
                        method: "GET",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken(),
                        },
                    })
                    if (response.ok){ 
                        alert("Logged out successfully!");
                        window.location.href = "/";
                    } else {
                        const data = await response.text();
                        alert("logout failed");
                        console.error("logout response: ", data);
                    }
                } catch {
                    console.error("Logout error", error);
                    alert("an error occured during logout");
                }
            });
        }

        if (deleteAccountBtn) {
            deleteAccountBtn.addEventListener("click", async function () {
                if (!confirm("Are you sure you want to delete your account? This is a permanent and definitive!")) {
                    return;
                }
                try { 
                    const response = await fetch(`${baseUrl}delete/`, {
                        method: "DELETE",
                        credentials: "include",
                    });
                    if (response.status === 204){
                        alert("your account has now been permenantly removed")
                        window.location.href = "/";
                    } else {
                        const data = await response.json();
                        alert("Error: " + (data.detail || "Account could not be deleted."));
                    }
                } catch (e) {
                    console.error("error deleting account: ". e);
                    alert("An error occured");
                }
            });
        }
        if (enable2FAButton) {
            enable2FAButton.addEventListener("click", async function () {
                try {
                    const twoFAResponse = await fetch(`${baseUrl}register-2fa/`, {
                        method: "POST",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken(),
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
                    if (qrContainerProfile) qrContainerProfile.style.display = "block";
                    if (qrCodeImageProfile) {
                        qrCodeImageProfile.src = `${twoFAData.qr_code}`;
                        qrCodeImageProfile.style.display = "block";
                    }
                    if (otpKey) otpKeyProfile.innerText = twoFAData.otp_secret;
                } catch (error) {
                    console.error("Error registering 2FA:", error);
                    alert("there have been issues, please start panicking!");
                }
            });
        }
        if (confirm2FA) {
            confirm2FA.addEventListener("click", async function () {
                try {
                    const response = await fetch(`${baseUrl}enable-2fa/`, {
                        method: "POST",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken(),
                        },
                    });
                    if (response.ok) {
                        alert("2FA enabled!");
                        qrContainer.style.display = "none";
                        window.location.href = "/"
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
        if (confirm2FAProfile) {
            confirm2FAProfile.addEventListener("click", async function () {
                try {
                    const response = await fetch(`${baseUrl}enable-2fa/`, {
                        method: "POST",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken(),
                        },
                    });
                    if (response.ok) {
                        alert("2FA enabled!");
                        qrContainerProfile.style.display = "none";
                        window.location.href = "/"
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
                await fetch(`${baseUrl}disable-2fa/`, {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                });
                alert("2FA disabled");
            });
        }
});
