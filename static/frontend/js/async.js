async function fetchData(url, options = {}) {
    try {
        const finalOptions = {
            credentials: "include",
            ...options,
        };

        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching data:", error);
        //throw error; // rethrow the error after logging it
    }
}
//TODO check what it does 