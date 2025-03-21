const searchInput = document.getElementById("searchInput")
const searchResults = document.getElementById("searchResults")

searchInput.addEventListener("input", function(){
    const query = searchInput.value.trim() // trim to remove unsesired spaces before or after

    if (query.lenght == 0) 
        return;

    fetch(`/data/api/searchUser/?usename=${encodeURIComponent(query)}`)
    .then (response => response.json())
    .then (data => {
        
    })
})