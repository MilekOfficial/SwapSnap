// Upload the photo
function uploadPhoto() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file to upload');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.photo_url) {
            document.getElementById('uploaded-photo').innerHTML = '';  // Clear the uploaded photo display
            getRandomPhoto(); // Immediately show random photo after upload
        }
    })
    .catch(error => console.error('Error uploading photo:', error));
}

// Fetch a random photo and display it
function getRandomPhoto() {
    fetch('/random_photo')
    .then(response => response.json())
    .then(data => {
        if (data.photo_url) {
            // Display random photo
            document.getElementById('random-photo').innerHTML = `<img src="${data.photo_url}" alt="Random Photo">`;

            // Display the reactions
            showReactions(data.reactions);

            // Show the reaction section
            document.getElementById('reaction-section').style.display = 'block';
        }
    })
    .catch(error => console.error('Error fetching random photo:', error));
}

// Display the reactions on the random photo
function showReactions(reactions) {
    const reactionsDiv = document.getElementById('reactions');
    if (reactions.length === 0) {
        reactionsDiv.innerHTML = 'No reactions yet';
    } else {
        reactionsDiv.innerHTML = reactions.join(' ');
    }
}

// React with an emoji
// React with an emoji
// React with an emoji
function react(emoji) {
    const randomPhoto = document.getElementById('random-photo').querySelector('img');
    if (!randomPhoto) return;

    const photoUrl = randomPhoto.src;

    // Ensure we are passing the correct photo_url and emoji
    fetch('/react', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ photo_url: photoUrl, emoji: emoji })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // Refresh the random photo to include the new reaction
            getRandomPhoto();
        } else {
            console.error('Error adding reaction:', data.error || 'Unknown error');
        }
    })
    .catch(error => console.error('Error reacting to photo:', error));
}