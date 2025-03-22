const searchInput = document.getElementById("searchInput")
const searchResults = document.getElementById("searchResults")

searchInput.addEventListener("input", async function(){
    const query = searchInput.value.trim() // trim to remove unsesired spaces before or after

    if (query.lenght == 0) 
        return;

    const response = await fetch(`/data/api/searchUser/?usename=${encodeURIComponent(query)}`, {
        method: POST,
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
        
    })
})