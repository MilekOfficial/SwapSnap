const reactionsDiv = document.getElementById('reactions');
const randomPhotoDiv = document.getElementById('random-photo');
const reactionSection = document.getElementById('reaction-section');
let currentPhotoUrl = '';

// Function to upload a photo
function uploadPhoto() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    if (!file) {
        alert('Wybierz plik do przesłania.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
            } else {
                alert('Błąd podczas przesyłania.');
            }
        })
        .catch(error => console.error('Error:', error));
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
            randomPhotoDiv.innerHTML = `<img src="${currentPhotoUrl}" alt="Losowe zdjęcie" />`;

            // Display reactions
            const reactions = data.reactions;
            displayReactions(reactions);

            // Show the reaction section
            reactionSection.style.display = 'block';
        })
        .catch(error => console.error('Error:', error));
}

// Function to display reactions
function displayReactions(reactions) {
    reactionsDiv.innerHTML = ''; // Clear previous reactions

    if (reactions.length === 0) {
        reactionsDiv.innerHTML = '<p>Brak reakcji dla tego zdjęcia.</p>';
        return;
    }

    const reactionsList = document.createElement('ul');
    reactionsList.classList.add('reactions-list');

    reactions.forEach(reaction => {
        const listItem = document.createElement('li');
        listItem.textContent = `${reaction.emoji} przez użytkownika ${reaction.user_id}`;
        reactionsList.appendChild(listItem);
    });

    reactionsDiv.appendChild(reactionsList);
}

// Function to react to the current photo
function react(emoji) {
    const randomPhotoElement = document.getElementById("random-photo");
    const reactionsContainer = document.getElementById("reactions");

    if (!randomPhotoElement || !randomPhotoElement.firstChild) {
        console.error("No photo to react to.");
        return;
    }

    const photoUrl = randomPhotoElement.firstChild.src;

    // Send reaction to the backend
    fetch("/react", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ photo_url: photoUrl, emoji: emoji }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to send reaction.");
            }
            return response.json();
        })
        .then((data) => {
            if (data.reactions) {
                // Update reactions UI
                reactionsContainer.innerHTML = "";
                data.reactions.forEach((reaction) => {
                    const listItem = document.createElement("li");
                    listItem.textContent = `${reaction.user_id}: ${reaction.emoji}`;
                    reactionsContainer.appendChild(listItem);
                });
            }
        })
        .catch((error) => {
            console.error("Error reacting:", error);
        });
}
