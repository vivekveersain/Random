async function getAllGroupMembers() {
    let members = new Set(); // To store unique members
    let startTime = Date.now(); // Capture the start time

    // Function to scroll down the participants list to load more members
    function scrollDown() {
        const panel = document.querySelector("div[role='list']");
        if (panel) {
            panel.scrollBy(0, 500); // Scroll down to load more members
        }
    }

    // Keep extracting data for 15 seconds
    while (Date.now() - startTime < 45000) { // 45 seconds
        scrollDown();
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second

        // Get all participant names from the current visible list
        let elements = document.querySelectorAll("div[role='listitem'] span[dir='auto']");
        
        // Add participant names to the Set (avoiding duplicates)
        elements.forEach(el => {
            let name = el.innerText.trim();
            if (name && !name.includes(":")) { // Exclude unwanted text like messages
                members.add(name);
            }
        });
    }

    // Log the extracted member names to the console
    console.log([...members].join("\n"));
}

// Run the function to extract group members for 15 seconds
getAllGroupMembers();
