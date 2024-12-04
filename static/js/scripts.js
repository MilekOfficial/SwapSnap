const reactionsDiv = document.getElementById('reactions');
const randomPhotoDiv = document.getElementById('random-photo');
const reactionSection = document.getElementById('reaction-section');
let currentPhotoUrl = '';

// Function to upload a photo
function uploadPhoto() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please add a photo.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === "File uploaded successfully!") {
                alert(data.message);
                getRandomPhoto(); // Fetch a new random photo after upload
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error uploading photo:', error);
            alert("An error occurred during upload.");
        });
}

// Function to fetch a random photo and its reactions
function getRandomPhoto() {
    fetch('/random_photo', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Display the random photo
            currentPhotoUrl = data.photo_url;
            randomPhotoDiv.innerHTML = `<img src="${currentPhotoUrl}" alt="Random Photo" />`;

            // Display reactions
            const reactions = data.reactions;
            displayReactions(reactions);

            // Show the reaction section
            reactionSection.style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching random photo:', error);
            alert("An error occurred while fetching a random photo.");
        });
}

// Function to display reactions
function displayReactions(reactions) {
    reactionsDiv.innerHTML = ''; // Clear previous reactions

    if (reactions.length === 0) {
        reactionsDiv.innerHTML = '<p>No reactions yet.</p>';
        return;
    }

    const reactionsList = document.createElement('ul');
    reactionsList.classList.add('reactions-list');

    reactions.forEach(reaction => {
        const listItem = document.createElement('li');
        listItem.textContent = `${reaction.emoji} from user ${reaction.user_id}`;
        reactionsList.appendChild(listItem);
    });

    reactionsDiv.appendChild(reactionsList);
}

// Function to react to the current photo
function react(emoji) {
    if (!currentPhotoUrl) {
        alert('No photo to react to.');
        return;
    }

    fetch('/react', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            photo_url: currentPhotoUrl,
            emoji: emoji,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Update displayed reactions
            const reactions = data.reactions;
            displayReactions(reactions);
        })
        .catch(error => {
            console.error('Error reacting to photo:', error);
            alert("An error occurred while submitting your reaction.");
        });
}

function showElement(selector) {
    // Find the element by the provided selector
    const element = document.querySelector(selector);
    
    if (element) {
        // Make the element visible
        element.style.display = 'block'; // or 'flex', 'grid', etc., depending on your layout
        element.style.visibility = 'visible';
        element.style.opacity = '1'; // Useful if using a fade-in effect
    } else {
        console.error(`Element not found with selector: ${selector}`);
    }
}

// Example usage:
// Assuming you have an element with the id "myElement" that is hidden

