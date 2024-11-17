const reactionsDiv = document.getElementById('reactions');
const randomPhotoDiv = document.getElementById('random-photo');
const reactionSection = document.getElementById('reaction-section');
let currentPhotoUrl = '';

// Function to upload a photo
// Funkcja do wysyłania zdjęcia na serwer
function uploadPhoto() {
    let fileInput = document.getElementById('file-upload');
    let file = fileInput.files[0];

    if (!file) {
        alert("Add photo.");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "File uploaded successfully!") {
            // Po udanym wysłaniu zdjęcia, wyświetlamy losowe zdjęcie
            alert(data.message);
            getRandomPhoto();
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        alert("Error.");
    });
}

// Funkcja do pobierania losowego zdjęcia
function getRandomPhoto() {
    fetch("/random_photo")
    .then(response => response.json())
    .then(data => {
        if (data.photo_url) {
            // Wyświetlamy losowe zdjęcie
            let randomPhotoSection = document.getElementById("random-photo-section");
            randomPhotoSection.style.display = "block"; // Pokazujemy sekcję z losowym zdjęciem
            let randomPhoto = document.getElementById("random-photo");
            randomPhoto.innerHTML = `<img src="${data.photo_url}" alt="Random Photo" />`;

            // Wyświetlamy reakcje, jeśli są
            let reactionsSection = document.getElementById("reactions");
            reactionsSection.innerHTML = data.reactions.map(reaction => {
                return `<span class="emoji">${reaction.emoji}</span>`;
            }).join(" ");
        } else {
            alert("Error code 1.");
        }
    })
    .catch(error => {
        alert("Error code 2.");
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
        reactionsDiv.innerHTML = '<p>No reactions.</p>';
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
        alert('Dont have photo.');
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
        .catch(error => console.error('Error:', error));
}
