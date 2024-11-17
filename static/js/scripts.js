const reactionsDiv = document.getElementById('reactions');
const randomPhotoDiv = document.getElementById('random-photo');
const reactionSection = document.getElementById('reaction-section');
let currentPhotoUrl = '';
const imgbbApiKey = 'your_imgbb_api_key_here'; // Replace with your ImgBB API key

// Function to upload a photo to ImgBB
function uploadPhoto() {
    let fileInput = document.getElementById('file-upload');
    let file = fileInput.files[0];

    if (!file) {
<<<<<<< HEAD
        alert("Please add a photo.");
=======
        alert("Add photo.");
>>>>>>> fdbabf195d718c9cecd78b66bb1025d1a5c93e02
        return;
    }

    let formData = new FormData();
    formData.append("image", file);

    fetch(`https://api.imgbb.com/1/upload?key=${imgbbApiKey}`, {
        method: "POST",
        body: formData,
    })
<<<<<<< HEAD
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const imageUrl = data.data.url;
                alert("Photo uploaded successfully!");

                // Display the uploaded photo
                displayUploadedPhoto(imageUrl);

                // Optional: Call your server to handle the uploaded image
                // saveImageToServer(imageUrl);
            } else {
                alert("Error uploading photo: " + data.error.message);
            }
        })
        .catch(error => {
            console.error("Error uploading photo:", error);
            alert("An error occurred while uploading the photo.");
        });
}

// Function to display the uploaded photo
function displayUploadedPhoto(imageUrl) {
    randomPhotoDiv.innerHTML = `<img src="${imageUrl}" alt="Uploaded Photo" />`;
    currentPhotoUrl = imageUrl; // Set the uploaded photo as the current photo
    reactionSection.style.display = 'block';
=======
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
>>>>>>> fdbabf195d718c9cecd78b66bb1025d1a5c93e02
}

// Function to fetch a random photo (if hosted on your server)
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
            console.error("Error fetching random photo:", error);
        });
}

// Function to display reactions
function displayReactions(reactions) {
    reactionsDiv.innerHTML = ''; // Clear previous reactions

    if (reactions.length === 0) {
<<<<<<< HEAD
        reactionsDiv.innerHTML = '<p>No reactions yet.</p>';
=======
        reactionsDiv.innerHTML = '<p>No reactions.</p>';
>>>>>>> fdbabf195d718c9cecd78b66bb1025d1a5c93e02
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
<<<<<<< HEAD
        alert('No photo available to react to.');
=======
        alert('Dont have photo.');
>>>>>>> fdbabf195d718c9cecd78b66bb1025d1a5c93e02
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
        .catch(error => console.error('Error reacting to photo:', error));
}
