class PhotoManager {
    constructor() {
        this.currentPhoto = null;
        this.loadingPhoto = false;
    }

    async fetchRandomPhoto() {
        if (this.loadingPhoto) return;
        
        try {
            this.loadingPhoto = true;
            const response = await fetch('/api/photos/random');
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Error fetching photo');
            }
            
            this.currentPhoto = data.photo;
            this.displayPhoto(data.photo);
            await this.loadReactions(data.photo.filename);
            
        } catch (error) {
            console.error('Error fetching random photo:', error);
            this.showError('Failed to load photo. Please try again.');
        } finally {
            this.loadingPhoto = false;
        }
    }

    async loadReactions(photoFilename) {
        try {
            const response = await fetch(`/api/reaction/${photoFilename}`);
            const data = await response.json();
            
            if (data.success) {
                this.updateReactions(data.reactions);
            }
        } catch (error) {
            console.error('Error loading reactions:', error);
        }
    }

    displayPhoto(photo) {
        const photoContainer = document.getElementById('photo-container');
        const img = document.createElement('img');
        img.src = photo.url;
        img.alt = 'Random photo';
        img.className = 'img-fluid rounded shadow';
        
        // Clear previous photo
        photoContainer.innerHTML = '';
        photoContainer.appendChild(img);
        
        // Update metadata
        const metadataContainer = document.getElementById('photo-metadata');
        if (metadataContainer) {
            const timestamp = new Date(photo.timestamp).toLocaleString();
            metadataContainer.innerHTML = `
                <p class="text-muted mb-2">Uploaded: ${timestamp}</p>
            `;
        }
    }

    updateReactions(reactions) {
        const reactionsContainer = document.getElementById('reactions-container');
        if (!reactionsContainer) return;

        reactionsContainer.innerHTML = '';
        
        for (const [emoji, count] of Object.entries(reactions)) {
            const button = document.createElement('button');
            button.className = 'btn btn-light me-2 mb-2';
            button.innerHTML = `${emoji} <span class="badge bg-secondary">${count}</span>`;
            button.onclick = () => this.addReaction(emoji);
            reactionsContainer.appendChild(button);
        }
    }

    async addReaction(emoji) {
        if (!this.currentPhoto) return;
        
        try {
            const response = await fetch('/api/reaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    photo: this.currentPhoto.filename,
                    reaction: emoji
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.updateReactions(data.reactions);
            }
        } catch (error) {
            console.error('Error adding reaction:', error);
            this.showError('Failed to add reaction. Please try again.');
        }
    }

    showError(message) {
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
        }
    }
}

// Initialize photo manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.photoManager = new PhotoManager();
    
    // Load initial random photo
    window.photoManager.fetchRandomPhoto();
    
    // Set up next photo button
    const nextButton = document.getElementById('next-photo-btn');
    if (nextButton) {
        nextButton.addEventListener('click', () => {
            window.photoManager.fetchRandomPhoto();
        });
    }
});
