const reactionsDiv = document.getElementById('reactions');
const randomPhotoDiv = document.getElementById('random-photo');
let currentPhotoUrl = '';

// Function to fetch a random photo and its reactions
function getRandomPhoto() {
    randomPhotoDiv.innerHTML = '<div class="loading">Loading...</div>';
    
    fetch('/random_photo', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                triggerAlert(data.error);
                randomPhotoDiv.innerHTML = '<div class="error">No photos available</div>';
                return;
            }

            // Display the random photo
            currentPhotoUrl = data.photo_url;
            const img = new Image();
            img.onload = function() {
                randomPhotoDiv.innerHTML = '';
                randomPhotoDiv.appendChild(img);
                img.classList.add('img-fluid');
            };
            img.onerror = function() {
                randomPhotoDiv.innerHTML = '<div class="error">Error loading image</div>';
                triggerAlert("Error loading image");
            };
            img.src = currentPhotoUrl;
            img.alt = "Random Photo";

            // Display reactions
            const reactions = data.reactions;
            displayReactions(reactions);
        })
        .catch(error => {
            console.error('Error fetching random photo:', error);
            randomPhotoDiv.innerHTML = '<div class="error">Error loading photo</div>';
            triggerAlert("An error occurred while fetching the photo.");
        });
}

// Function to display reactions
function displayReactions(reactions) {
    reactionsDiv.innerHTML = ''; // Clear previous reactions

    if (!reactions || reactions.length === 0) {
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
        triggerAlert('No photo to react to.');
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
                triggerAlert(data.error);
                return;
            }
            displayReactions(data.reactions);
            triggerAlert('Reaction added!', 'success');
        })
        .catch(error => {
            console.error('Error adding reaction:', error);
            triggerAlert('An error occurred while adding your reaction.');
        });
}

// Configure Dropzone
Dropzone.options.fileDropzone = {
    maxFilesize: 5, // Maximum file size in MB
    acceptedFiles: 'image/*',
    init: function() {
        this.on("success", function(file, response) {
            if (response.success) {
                getRandomPhoto();
                triggerAlert("Photo uploaded successfully!", "success");
            } else {
                triggerAlert(response.error || "Error uploading photo");
            }
        });
        this.on("error", function(file, errorMessage) {
            triggerAlert(typeof errorMessage === 'string' ? errorMessage : "Error uploading photo");
            this.removeFile(file);
        });
        this.on("addedfile", function(file) {
            if (file.size > 5 * 1024 * 1024) {
                triggerAlert("File is too large (max 5MB)");
                this.removeFile(file);
            }
        });
    }
};

function triggerAlert(message, type = 'error') {
    const alertContainer = document.getElementById('alert-container');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertContainer.appendChild(alertDiv);

    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

function toggleTheme() {
    const toggleElement = document.getElementById('toggle');
    const isDarkMode = toggleElement.checked;
    const bodyElement = document.body;

    if (isDarkMode) {
        bodyElement.classList.add('dark-mode');
    } else {
        bodyElement.classList.remove('dark-mode');
    }

    localStorage.setItem('darkMode', isDarkMode);
}

// Load a random photo when the page loads
document.addEventListener('DOMContentLoaded', () => {
    getRandomPhoto();
    
    // Initialize theme
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    const toggleElement = document.getElementById('toggle');
    if (toggleElement) {
        toggleElement.checked = isDarkMode;
        toggleTheme();
    }
});
