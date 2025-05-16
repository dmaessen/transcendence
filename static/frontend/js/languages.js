// When the user selects from the dropdown
document.getElementById("languageDropdown").addEventListener("change", async (e) => {
    e.preventDefault();
    const loggedin = await checkLoginStatus();
    if (loggedin === true) {
        localStorage.setItem("manualLangSelection", "true");
        console.log("ITS TRUE I AM LOGGED IN");
    }
    // Submit the form *after* localStorage is set
    document.getElementById("language-switch-form").submit();
});

function applyPreferredLanguageAfterLogin() {
    const manuallySelected = localStorage.getItem("manualLangSelection");
    if (manuallySelected) {
        if (manuallySelected === "true") {
            localStorage.setItem("manualLangSelection", "false");
            return ;
        } else if (manuallySelected === "false") {
            getUserPreferredLanguage();
        }
    } else {
        getUserPreferredLanguage();
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
