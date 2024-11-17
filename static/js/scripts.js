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
        alert("Please add a photo.");
        return;
    }

    let formData = new FormData();
    formData.append("image", file);

    fetch(`https://api.imgbb.com/1/upload?key=${imgbbApiKey}`, {
        method: "POST",
        body: formData,
    })
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
        alert('No photo available to react to.');
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
