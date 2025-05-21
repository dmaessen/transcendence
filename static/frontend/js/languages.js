// When the user selects from the dropdown
document.getElementById("languageDropdown").addEventListener("change", async (e) => {
    e.preventDefault();
    const loggedin = await checkLoginStatus();
    if (loggedin === true) {
        localStorage.setItem("manualLangSelection", "true");
    }
    // Submit the form *after* localStorage is set
    document.getElementById("language-switch-form").submit();
});

function applyPreferredLanguageAfterLogin() {
    if (localStorage.getItem("initialLoginApplied") === null) {
        localStorage.setItem("initialLoginApplied", "false");
    }

    const manuallySelected = localStorage.getItem("manualLangSelection");
    const loginApplied = localStorage.getItem("initialLoginApplied");

    console.log("manualLangSelection:", manuallySelected);
    console.log("initialLoginApplied:", loginApplied);
    if (manuallySelected) {
        console.log("YOU"); //rm
        if (manuallySelected === "true") {
            console.log("YOU1"); //rm
            localStorage.setItem("manualLangSelection", "false");
            return ;
        } else if (manuallySelected === "false" && loginApplied === "true") {
            getUserPreferredLanguage();
            console.log("YOU2"); // rm
        }
    } else {
        localStorage.setItem("initialLoginApplied", "true");
        getUserPreferredLanguage();
        console.log("YOU3"); // rm
    }
}

function getUserPreferredLanguage() {
    // Check if the page has already been reloaded for language change
    fetch('/data/api/get_profile/', {
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to fetch user profile");
        return response.json();
    })
    .then(data => {
        if (data.preferred_language) {
            const currentLanguage = document.documentElement.lang; // Get current language from <html lang="...">
            console.log("Current language:", currentLanguage);
            console.log("Preferred language:", data.preferred_language);
            if (currentLanguage === data.preferred_language) {
                console.log("Preferred language already applied, skipping reload.");
                return;
            }
            console.log("Applying preferred language via set_language:", data.preferred_language);
            
            return fetch("/i18n/setlang/", {
                method: "POST",
                credentials: 'include',
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: `language=${data.preferred_language}&next=/`
            }).then(() => {
                location.reload();
            });
        } else {
            // gameMenuFirst.show();
        }
    })
    .catch(error => {
        console.error("Error loading preferred language:", error);
    });
}
