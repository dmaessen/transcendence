
const baseUrl = "http://127.0.0.1:8000/api/authentication";

document.getElementById("registerForm").addEventListener("submit", async function (e) {
    console.log("script.js loaded successfully!, registerform");
    e.preventDefault();
    console.log("Register form submitted!");
    {% comment %} const username = document.getElementById("registerUsername").value; {% endcomment %}
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;

    console.log("sending data: ", { email, password });
    try{
        const response = await fetch(`${baseUrl}/register/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();
        console.log("Server response:", data);
        if (response.ok) {
            alert("Registration successful! You can now log in.");
        } else {
            alert(`Error: ${JSON.stringify(data)}`);
        }
    } catch (error) {
        console.error("Error: ", error);
        alert("An error occured. check the console")
    }
});

document.getElementById("loginForm").addEventListener("submit", async function (e) {
    console.log("script.js loaded successfully!, loginform");
    e.preventDefault();
    console.log("Login form submitted!");

    const username = document.getElementById("loginUsername").value;
    const password = document.getElementById("loginPassword").value;

    console.log("Sending data:", { email, password });
    
    try {
        const response = await fetch(`${baseUrl}/login/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        console.log("Server response:", data);
        if (response.ok) {
            localStorage.setItem("access", data.access);
            localStorage.setItem("refresh", data.refresh);
            alert("Login successful!");
        } else {
            alert("Login failed!");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occured. Check the console.");
    }
});