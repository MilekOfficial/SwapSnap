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
function triggerAlert(message) {
    // Create the alert div
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-warning alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Append the alert to the alert-container
    const alertContainer = document.getElementById('alert-container');
    alertContainer.appendChild(alertDiv);

    // Optional: Automatically remove the alert after a few seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        alertDiv.addEventListener('transitionend', () => alertDiv.remove());
    }, 5000); // 5 seconds
}
function everythingDoneAlert() {
            // Create the alert element
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                <strong>File Uploded!</strong> Thank's for using SwapSnap.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            // Append the alert to the container
            const alertContainer = document.getElementById('alert-container');
            alertContainer.appendChild(alertDiv);

            // Optional: Auto-dismiss after 5 seconds
            setTimeout(() => {
                alertDiv.classList.remove('show');
                alertDiv.addEventListener('transitionend', () => alertDiv.remove());
            }, 5000);
        }

// script.js
document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("themeToggle");

  // Sprawdzanie zapisanych preferencji w LocalStorage
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.classList.add("dark-theme");
  }

  // Przełączanie trybu
  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-theme");

    // Zapisywanie stanu w LocalStorage
    if (document.body.classList.contains("dark-theme")) {
      localStorage.setItem("theme", "dark");
    } else {
      localStorage.setItem("theme", "light");
    }
  });
});

//gsafklgjhdskajhfakjshflhhhhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhlhllll4 r74eufdchyj 87rofucyehjd4 87fceoruydhjxani4sw  8oc7fyruhdeajx4wnq3i 8aeorqw347fyduhjcn
//i need to be js project on github
//ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]
//ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]ofhjsdzp[a q34a8erwi7uhy]
