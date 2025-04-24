let loginsocket;

async function loginWebSocket(){
    console.log("Let's open those sockets bebê");

    const token = localStorage.getItem("access_token");
    if (!token) {
        console.error("No token no game!");
        return;
    }
    // console.log("toke: ", token);
    try {

        loginsocket = new WebSocket(`ws://${window.location.host}/ws/online_users/?token=${token}`)
        // console.log("socket: ", loginsocket);
        if (!token) {
            console.error("No access token found! WebSocket authentication will fail.");
            return;
        }
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
    
            // Clear tokens
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            console.log("tokens cleaned");
    
            //refresh the page 
            window.location.reload();
            // logOut(); This is dumb as user can logout in any modal 
        
        };
        loginsocket.onerror = async function(error) {
            console.error("onlineSocket error:", error);
        };
        // console.log("socket: ", loginsocket);
    } catch (errror) {
        console.log("Error: ", errror);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    
    const showLogin = document.getElementById("showLogin");
    const showRegister = document.getElementById("showRegister");
    const loginContainer = document.getElementById("loginContainer");
    const registerContainer = document.getElementById("registerContainer");
    const backToMain1 = document.getElementById("backToMain1");
    const backToMain2 = document.getElementById("backToMain2");
    const qrBack = document.getElementById("QR_back");
    const confirm2FA = document.getElementById("confirm2FA")
    const disable2FA = document.getElementById("disable2FA");
    const submitOTP = document.getElementById("submitOTPButton");
    const returnOTP = document.getElementById("returnToLogin");
    // Debugging: Check if elements exist
    
    console.log("Elements found:", {
        showLogin,
        showRegister,      
        loginContainer,
        registerContainer,
        backToMain1,
        backToMain2,
        qrBack,
        confirm2FA,
        disable2FA,
        submitOTP,
        returnOTP
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

    if (returnOTP){
        showLogin.addEventListener("click", function() {
            otpContainer.style.display = "none";
            loginContainer.style.display = "block";
        })
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

const baseUrl = "/api/authentication/";

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

    document.getElementById("QR_back").addEventListener("click", function() {
        qrContainer.style.display = "none";
    });

    document.getElementById("confirm2FA").addEventListener("click", function () {
        setup2FA();
        alert("2FA set up!");
    })

    document.getElementById("disable2FA").addEventListener("click", function (){
        disable2FA();
        alert("2FA disabled");
    })

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

            const name = document.getElementById("registerName").value;
            const username = document.getElementById("registerUsername").value;
            const email = document.getElementById("registerEmail").value;
            const password = document.getElementById("registerPassword").value;
            const enable2FA = document.getElementById("enable2FAonRegister").checked;

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
                console.log("Server response, from registration:", registrationDataResponse);
                
                if (!registerData.ok) {
                    if (registerData.status == 400){
                        alert ("registration failed, user may already exist") 
                    }
                    else {
                        alert(`Registration failed: ${JSON.stringify(registerData)}`);
                    }
                    return;
                }

                alert("Registration successful! You will now be logged in automatically");

                // const requestBody = {email, password};

                // const loginData = await fetch(`${baseUrl}login/`, {
                //     method: "POST",
                //     headers: {
                //         "Content-Type": "application/json",
                //         "X-CSRFToken": getCSRFToken(),
                //     },
                //     body: JSON.stringify(requestBody),
                // });
                
                const accessToken = registrationDataResponse.access;
                const refreshToken = registrationDataResponse.refresh;

                if (!accessToken || !refreshToken) {
                    alert("Registration successful, but failed to retrieve tokens.");
                    return;
                }

                // if (!loginData.ok) {
                //     alert("Login failed. Please log in manually.");
                //     return;
                // }

                // const loginDataResponse = await loginData.json();
                // alert("Server response, from login:", loginDataResponse);
                
                // console.log("accesstoken = ", accessToken);
                // console.log("refreshtoken = ", refreshToken);

                localStorage.setItem("access_token", accessToken);
                localStorage.setItem("refresh_token", refreshToken);
                
                if (!localStorage.getItem("access_token") || !localStorage.getItem("refresh_token")) {
                    alert("Login failed somehow")
                    return ;
                }
                // alert("login complete.");

                if (enable2FA) {
                    console.log("Enabling 2FA...");
                    // const accessToken = loginData.access;

                    const twoFAResponse = await fetch(`${baseUrl}register-2fa/`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${accessToken}`,
                        },
                    });

                    const twoFAData = await twoFAResponse.json();
                    // console.log("2FA response:", twoFAData);

                    if (!twoFAResponse.ok) {
                        alert(`2FA Setup Failed: ${JSON.stringify(twoFAData)}`);
                        return;
                    }

                    if (!twoFAData.qr_code) {
                        alert("2FA response missing QR code.");
                        return;
                    }

                    document.getElementById("registerContainer").style.display = "none";
                    document.getElementById("qrContainer").style.display = "block";
                    document.getElementById("qrCodeImage").src = `${twoFAData.qr_code}`;
                    document.getElementById("qrCodeImage").style.display = "block";
                    document.getElementById("otpKey").innerText = twoFAData.otp_secret;
                }

                // window.location.href = "/game_server";

            } catch (error) {
                console.error("Error:", error);
                alert("An error occurred. Check the console.");
            }
        });
    }
})

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const otpInputContainer = document.getElementById("otpContainer");
    const otpInput = document.getElementById("otpToken");
    const otpSubmitButton = document.getElementById('submitOTPButton');
    const otpReturn = document.getElementById('returnToLogin');

    console.log("OTP Submit Button:", otpSubmitButton);

    function saveLoginCredentials(email, password){
        sessionStorage.setItem("loginEmail", email);
        sessionStorage.setItem("loginPassword", password);
    }

    function getSavedLoginCredentials(){
        return {
            email: sessionStorage.getItem("loginEmail"),
            password: sessionStorage.getItem("loginPassword")
        }
    }

    async function loginRequest(email, password, otp_token = null) {
        try {
            const requestBody = {email, password};
            if (otp_token) requestBody.otp_token = otp_token;

            const response = await fetch(`${baseUrl}login/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();
            console.log("Server response:", data);

            if (response.ok) {
                localStorage.setItem("access_token", data.access);
                localStorage.setItem("refresh_token", data.refresh);
                
                alert("Login successful!");
                console.log("login done");

                //connect heartbeat socket 
                await loginWebSocket();

                //handle the modals closing/oppening
                const loginModalElement = document.getElementById("SignInMenu");
                const mainMenuModalElement = document.getElementById("gameMenuFirst");
                console.log("loginModalElement:", loginModalElement);
                console.log("mainMenuModalElement:", mainMenuModalElement);
                const loginModal = bootstrap.Modal.getOrCreateInstance(loginModalElement);
                loginModal.hide();
                const mainMenuModal = bootstrap.Modal.getOrCreateInstance(mainMenuModalElement);
                mainMenuModal.show();

            } else if(response.status === 403){
                otpInputContainer.style.display = "block";
                loginForm.style.display = "none"; // should the login form be hidden?
                alert("2FA required. enter your OTP code please.");
                
            } else if(response.status === 401 && data["2fa_required"]){
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
            console.log("Login form submitted!");

            // if (otpInputContainer.style.display === "block"){
            //     const otp_token = otpInput.value.trim();
            //     if (!otp_token) {
            //         alert("Please enter the OTP token");
            //         return;
            //     }
            //     await loginRequest(email, password, otp_token)
            //     return;
            // }
            const email = document.getElementById("loginEmail").value.trim();
            const password = document.getElementById("loginPassword").value.trim();

            saveLoginCredentials(email, password);

            await loginRequest(email, password);
        });
    }

    if (otpReturn){
        showLogin.addEventListener("click", function() {
            otpContainer.style.display = "none";
            loginContainer.style.display = "block";
        })
    }

    if (otpSubmitButton) {
        otpSubmitButton.addEventListener("click", async function () {
            console.log("OTP Submit button clicked!");

            const { email, password } = getSavedLoginCredentials();
            const otp_token = otpInput.value.trim();

            if (!otp_token) {
                alert("Please enter the OTP token.");
                return;
            }
            console.log("Submitting OTP:", otp_token);

            await loginRequest(email, password, otp_token);
        })
    }
});

// document.getElementById("logoutBtn").click = () => alert("clicked!");
// function logOut () {
//     console.log("Logout button clicked");

//     // Clear tokens
//     localStorage.removeItem("access_token");
//     localStorage.removeItem("refresh_token");
//     alert("Logged out successfully!");

//     // Handle modal switching
//     const loginModalElement = document.getElementById("SignInMenu");
//     const mainMenuModalElement = document.getElementById("gameMenuFirst");

//     const mainMenuModal = bootstrap.Modal.getOrCreateInstance(mainMenuModalElement);
//     const loginModal = bootstrap.Modal.getOrCreateInstance(loginModalElement);

//     mainMenuModal.hide();

//     // Optionally delay showing login modal to let the previous one close
//     setTimeout(() => {
//         loginModal.show();
//     }, 200);
// }


document.addEventListener("DOMContentLoaded", function () {
    const logoutButton = document.getElementById("logoutBtn");

    if (logoutButton) {
        // logoutButton.addEventListener("click", logOut);
        logoutButton.addEventListener("click", function () {
            console.log("Logout button clicked");

            // Clear tokens
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            alert("Logged out successfully!");

            // Handle modal switching
            const loginModalElement = document.getElementById("SignInMenu");
            const mainMenuModalElement = document.getElementById("gameMenuFirst");

            const mainMenuModal = bootstrap.Modal.getOrCreateInstance(mainMenuModalElement);
            const loginModal = bootstrap.Modal.getOrCreateInstance(loginModalElement);

            mainMenuModal.hide();

            // Optionally delay showing login modal to let the previous one close
            setTimeout(() => {
                loginModal.show();
            }, 200);
        });
    }
    })


// document.addEventListener("DOMContentLoaded", function () {
//     const logoutButton = document.getElementById("Logout");
//     console.log("logout button clicked");

//     if (logoutButton) {
//         logoutButton.addEventListener("click", function () {
            
//             localStorage.removeItem("access_token");
//             localStorage.removeItem("refresh_token");
//             alert("Logged out successfully!");
//             //handle the modals closing/oppening
//             const loginModalElement = document.getElementById("SignInMenu");
//             const mainMenuModalElement = document.getElementById("gameMenuFirst");
//             console.log("loginModalElement:", loginModalElement);
//             console.log("mainMenuModalElement:", mainMenuModalElement);
//             const mainMenuModal = bootstrap.Modal.getOrCreateInstance(mainMenuModalElement);
//             mainMenuModal.hide();
//             const loginModal = bootstrap.Modal.getOrCreateInstance(loginModalElement);
//             loginModal.show();
//         });
//     }
// });

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
            // .then(resp => resp.json().then(data => ({ status: resp.status, body: data })))
            .then(resp => {
                if (resp.status === 204) {alert("Your account is now removed permanently");
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("refresh_token");
                    window.location.href = "/game_server/";
                }
                else {
                    return resp.json().then(data => {
                        alert("Error: " + (data.detail || "Account could not be deleted."));
                    });
                }
            })  
            // .catch(error => {console.error("Error:", error);
            // alert("an error occured"); });
        });
    }
});

document.addEventListener("DOMContentLoaded", function () 
{
    const enable2FAButton = document.getElementById("enable2FA");
    const qrContainer = document.getElementById("qrContainer");
    const qrCodeImage = document.getElementById("qrCodeImage")
    const otpKey = document.getElementById("otpKey")
    const confirm2FA = document.getElementById("confirm2FA")
    const qrBack = document.getElementById("qrBack")
    
    console.log("Enable 2FA button clicked");
    
    if (enable2FAButton) 
    {
        enable2FAButton.addEventListener("click", async function ()
        {
            console.log("Enable 2FA button clicked")
            let accessToken = localStorage.getItem("access_token");

            if (!accessToken) {
                console.log("no access token found when enabling 2FA");
                console.log("trying to refresh..");
                accessToken = await refreshAccessToken();
                if (!accessToken){
                    alert("You are not logged in, please do so now.")
                    window.location.href = "/game_server/"
                    return
                };
            }
            try 
            {
                alert("using this access token", accessToken);

                const twoFAResponse = await fetch(`${baseUrl}register-2fa/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${accessToken}`,
                    },
                });

                const twoFAData = await twoFAResponse.json();
                console.log("2FA response:", twoFAData);

                if (!twoFAResponse.ok) {
                    alert(`2FA Setup Failed: ${JSON.stringify(twoFAData)}`);
                    return;
                }

                if (!twoFAData.qr_code) {
                    alert("2FA response missing QR code.");
                    return;
                }

                document.getElementById("registerContainer").style.display = "none";
                document.getElementById("qrContainer").style.display = "block";
                document.getElementById("qrCodeImage").src = `${twoFAData.qr_code}`;
                document.getElementById("qrCodeImage").style.display = "block";
                document.getElementById("otpKey").innerText = twoFAData.otp_secret;
            // }

                // const data = await response.json();
                
                // console.log("2fa register return data: {otp_secret ", data.otp_secret, "}")

                // document.getElementById("qrCodeImage").src = data.qr_code;
                // document.getElementById("otpKey").innerText = data.otp_secret;
                
                // document.getElementById("registerContainer").style.display = "none";
                // document.getElementById("qrContainer").style.display = "block";

                // if (response.ok) 
                // {
                //     qrCodeImage.src = `${data.qr_code}`;
                //     // qrCodeImage.src = `data:image/png;base64,${data.qr_code}`;
                //     otpKey.innerText = data.otp_uri;
                //     qrContainer.style.display = "block";
                // } 
                // else 
                // {
                //     alert(`error: ${JSON.stringify(data)}`);
                // }
            } 
            catch (error) 
            {
                console.error("Error regestering 2FA:", error);
                alert("there have been issues, please start panicking!");
            }
        });
    }
    if (confirm2FA) {
        confirm2FA.addEventListener("click", async function () 
        {
            try 
            {
                const response = await fetch(`${baseUrl}enable-2fa/`, 
                {
                    method: "POST",
                    headers: 
                    {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                        "X-CSRFToken": getCSRFToken(),
                    },
                });
                
                if (response.ok) 
                {
                    alert("2FA enabled!");
                    qrContainer.style.display = "none";
                }
                else if (response.status === 500)
                {
                    alert("there was an issue generating the otp code")
                }
                else
                {
                    alert("2FA failure :(");
                }
            }
            catch (error) 
            {
                console.error("Error confirming 2FA :(", error);
            }
        });
    }

    if (qrBack) 
    {
        qrBack.addEventListener("click", async function () 
        {
            qrContainer.style.display = "none";
        });
    }
});


function disable2FA() {
    let access_token = localStorage.getItem("access_token");

    if(!access_token){
        access_token = refreshAccessToken();
        if(!access_token){
            alert("you are not logged in, please do so now");
            return null;
        }
    }

    const response = fetch(`${baseUrl}disable-2fa/`, 
        {
            method: "POST",
            headers: 
            {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access_token}`,
                "X-CSRFToken": getCSRFToken(),
            },
        })
}

function setup2FA() {
    let access_token;

    access_token = localStorage.getItem("access_token"); 
    if (!access_token) {
        try {
            access_token = refreshAccessToken()
        } catch (error) {
            console.error("Error refreshing token", error);
            alert("No refresh token found, please login.")
            // window.location.href = "/game_server";;
            return null;
        }
    }

    const response = fetch(`${baseUrl}register-2fa/`, 
    {
        method: "POST",
        headers: 
        {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${access_token}`,
            "X-CSRFToken": getCSRFToken(),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.qr_code) {
            document.getElementById("qrCodeImage").src = data.qr_code;
            document.getElementById("otpKey").innerText = data.otp_secret;
            document.getElementById("qrContainer").style.display = "block";
        }
        else {
            alert ("there was a problem in setting up your 2fa");
        }
    })
    .catch(error => console.error("Error:", error))
}

async function refreshAccessToken(){
    let accessToken = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");

    if (!refreshToken) {
        console.warn("No refresh token found, please login.");
        alert("No refresh token found, please login.")
        // windowl.location.href = "/game_server";
        return null;
    }

    try {
        const response = await fetch(`${baseUrl}refresh/`, {
            method: "POST",
            headers: { "Content-Type": "application/json"}, 
            body: JSON.stringify({refresh: refreshToken}),
        });

        const data = await response.json();

        if (!response.ok) {
            console.error("Refresh token invalid:", data);
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            alert("Session expired. Please log in again.");
            // window.location.href = "/game_server";
            return null;
        } 
        alert("refresh access token called, new access token:", accessToken)
        localStorage.setItem("access_token", data.access);
        console.log("Access token refreshed.");
        return data.access
    } catch (error) {
        console.error("Error refreshing token", error);
        // window.location.href = "/game_server";;
        return null;
    }
}


window.onload = async function () {
    const urlParams = new URLSearchParams(window.location.search);
    const ftCode = urlParams.get("code");
    
    if (ftCode) {
        console.log("42 code received:", ftCode);
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
            console.log("42 Callback Response:", data);

            if (response.ok) {
                localStorage.setItem("access_token", data.access);
                localStorage.setItem("refresh_token", data.refresh);
                alert("42 login successful!");
                window.location.href = "/game_server";
            } else {
                alert("42 login failed: " + (data.error || JSON.stringify(data)));
            }
        } catch (error) {
            console.error("Error handling 42 code:", error);
            alert("An error occurred during 42 login.");
        }

    }
    async function handleGoogleCredentialResponse(response) {
        console.log("Google credential response:", response);

        try {
            const result = await fetch("/api/authentication/google-login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({
                    id_token: response.credential,
                }),
            });

            const data = await result.json();
            console.log("Server response:", data);

            if (result.ok) {
                localStorage.setItem("access_token", data.access);
                localStorage.setItem("refresh_token", data.refresh);
                alert("Google login successful!");
                window.location.href = "/game_server";
            } else {
                console.log("data: ", data);
                alert(data.error || "Google login failed.");
            }
        } catch (error) {
            console.error("Error during Google login:", error);
            alert("An error occurred during Google login.");
        }
    }
    const googleClientId = document
        .querySelector('meta[name="google-signin-client_id"]')
        ?.getAttribute("content");

    const googleSignInRegDiv = document.getElementById("googleSignInButtonRegister");

    if (googleClientId && googleSignInRegDiv && window.google) {
        google.accounts.id.initialize({
            client_id: googleClientId,
            callback: handleGoogleCredentialResponse,
        });


        // google.accounts.id.renderButton(
        //     googleSignInRegDiv,
        //     {
        //         theme: "outline",
        //         size: "large",
        //         width: 300,
        //     }
        // );

    const googleSignInLogDiv = document.getElementById("googleSignInButtonLogin");

    if (googleClientId && googleSignInLogDiv && window.google) {
        google.accounts.id.initialize({
            client_id: googleClientId,
            callback: handleGoogleCredentialResponse,
        });


        // google.accounts.id.renderButton(
        //     googleSignInLogDiv,
        //     {
        //         theme: "outline",
        //         size: "large",
        //         width: 300,
        //     });
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


    } else {
        console.warn("Google Sign-In setup failed: missing client ID, container, or GIS script.");
    }
};

