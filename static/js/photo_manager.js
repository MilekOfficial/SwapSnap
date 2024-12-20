class PhotoManager {
    constructor() {
        this.currentPhoto = null;
        this.loadingPhoto = false;
        this.photoContainer = document.getElementById('photo-container');
        this.errorContainer = document.getElementById('error-container');
        this.uploadForm = document.getElementById('upload-form');
        this.nextButton = document.getElementById('next-photo');
        
        this.initializeEventListeners();
        this.fetchRandomPhoto();
    }

    initializeEventListeners() {
        if (this.nextButton) {
            this.nextButton.addEventListener('click', () => this.fetchRandomPhoto());
        }

        if (this.uploadForm) {
            this.uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
        }
    }

    showError(message) {
        if (this.errorContainer) {
            this.errorContainer.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
        }
    }

    showSuccess(message) {
        if (this.errorContainer) {
            this.errorContainer.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
        }
    }

    async fetchRandomPhoto() {
        if (this.loadingPhoto) return;
        
        try {
            this.loadingPhoto = true;
            this.showLoading();
            
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

    showLoading() {
        if (this.photoContainer) {
            const loadingSpinner = document.createElement('div');
            loadingSpinner.className = 'loading-spinner';
            this.photoContainer.innerHTML = '';
            this.photoContainer.appendChild(loadingSpinner);
        }
    }

    displayPhoto(photo) {
        if (!this.photoContainer) return;
        
        const img = document.createElement('img');
        img.src = photo.url;
        img.alt = 'Random photo';
        img.className = 'img-fluid rounded shadow';
        
        // Show loading until image is loaded
        this.showLoading();
        
        img.onload = () => {
            this.photoContainer.innerHTML = '';
            this.photoContainer.appendChild(img);
        };
        
        img.onerror = () => {
            this.showError('Failed to load image');
            this.photoContainer.innerHTML = '';
        };
    }

    async handleUpload(e) {
        e.preventDefault();
        
        const formData = new FormData(this.uploadForm);
        const fileInput = this.uploadForm.querySelector('input[type="file"]');
        
        if (!fileInput.files.length) {
            this.showError('Please select a file to upload');
            return;
        }

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('Photo uploaded successfully!');
                this.uploadForm.reset();
                // Display the newly uploaded photo
                this.displayPhoto(data);
            } else {
                this.showError(data.error || 'Failed to upload photo');
            }
        } catch (error) {
            console.error('Error uploading photo:', error);
            this.showError('Error uploading photo');
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

    updateReactions(reactions) {
        const reactionsContainer = document.getElementById('reactions-container');
        if (!reactionsContainer) return;

        reactionsContainer.innerHTML = '';
        
        Object.entries(reactions).forEach(([reaction, count]) => {
            const button = document.createElement('button');
            button.className = 'reaction-btn';
            button.innerHTML = `${reaction} <span class="badge bg-secondary">${count}</span>`;
            button.onclick = () => this.addReaction(this.currentPhoto.filename, reaction);
            reactionsContainer.appendChild(button);
        });
    }

    async addReaction(photoFilename, reaction) {
        try {
            const response = await fetch('/api/reaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: photoFilename,
                    reaction: reaction
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.updateReactions(data.reactions);
            } else {
                this.showError('Failed to add reaction');
            }
        } catch (error) {
            console.error('Error adding reaction:', error);
            this.showError('Error adding reaction');
        }
    }
}

// Initialize photo manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.photoManager = new PhotoManager();
});
