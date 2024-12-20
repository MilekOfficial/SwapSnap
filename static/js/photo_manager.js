class PhotoManager {
    constructor() {
        this.currentPhoto = null;
        this.loadingPhoto = false;
        this.photoContainer = document.getElementById('photo-container');
        this.photosGrid = document.getElementById('photos-grid');
        this.errorContainer = document.getElementById('error-container');
        this.uploadForm = document.getElementById('upload-form');
        this.refreshButton = document.getElementById('refresh-photos');
        this.photoDetails = document.getElementById('photo-details');
        
        this.initializeEventListeners();
        this.loadPhotos();
    }

    initializeEventListeners() {
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', () => this.loadPhotos());
        }

        if (this.uploadForm) {
            this.uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
            
            // Add drag and drop support
            const uploadZone = this.uploadForm.querySelector('.upload-zone');
            if (uploadZone) {
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                    uploadZone.addEventListener(eventName, (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                    });
                });

                uploadZone.addEventListener('dragenter', () => uploadZone.classList.add('dragover'));
                uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
                uploadZone.addEventListener('drop', (e) => {
                    uploadZone.classList.remove('dragover');
                    const fileInput = this.uploadForm.querySelector('input[type="file"]');
                    if (fileInput && e.dataTransfer.files.length) {
                        fileInput.files = e.dataTransfer.files;
                    }
                });
            }
        }
    }

    showError(message) {
        if (this.errorContainer) {
            this.errorContainer.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <i class="bi bi-exclamation-triangle-fill"></i> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
        }
    }

    showSuccess(message) {
        if (this.errorContainer) {
            this.errorContainer.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    <i class="bi bi-check-circle-fill"></i> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
        }
    }

    async loadPhotos() {
        if (this.loadingPhoto) return;
        
        try {
            this.loadingPhoto = true;
            this.showGridLoading();
            
            const response = await fetch('/api/photos');
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Error fetching photos');
            }
            
            this.displayPhotoGrid(data.photos);
            
        } catch (error) {
            console.error('Error fetching photos:', error);
            this.showError('Failed to load photos. Please try again.');
        } finally {
            this.loadingPhoto = false;
        }
    }

    showGridLoading() {
        if (this.photosGrid) {
            this.photosGrid.innerHTML = '<div class="loading-spinner"></div>';
        }
    }

    displayPhotoGrid(photos) {
        if (!this.photosGrid) return;
        
        this.photosGrid.innerHTML = '';
        
        if (!photos || !photos.length) {
            this.photosGrid.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="bi bi-images fs-1"></i>
                    <p class="mt-2">No photos found</p>
                </div>
            `;
            return;
        }
        
        photos.forEach(photo => {
            const photoElement = document.createElement('div');
            photoElement.className = 'photo-item';
            photoElement.innerHTML = `
                <img src="${photo.thumbnail}" alt="Photo" loading="lazy">
                <div class="overlay">
                    <div class="photo-date">${new Date(photo.timestamp).toLocaleDateString()}</div>
                </div>
            `;
            
            photoElement.addEventListener('click', () => {
                this.currentPhoto = photo;
                this.displayPhotoDetails(photo);
                this.loadReactions(photo.filename);
            });
            
            this.photosGrid.appendChild(photoElement);
        });
    }

    displayPhotoDetails(photo) {
        if (!this.photoDetails || !photo.details) return;

        const { processed } = photo.details;
        if (!processed) return;

        const dateSpan = document.getElementById('photo-date');
        const dimensionsSpan = document.getElementById('photo-dimensions');
        const sizeSpan = document.getElementById('photo-size');
        const typeSpan = document.getElementById('photo-type');

        if (dateSpan) {
            const date = new Date(photo.timestamp);
            dateSpan.textContent = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        }

        if (dimensionsSpan) {
            dimensionsSpan.textContent = `${processed.width} × ${processed.height} px`;
        }

        if (sizeSpan) {
            sizeSpan.textContent = processed.size;
        }

        if (typeSpan) {
            typeSpan.textContent = processed.format.toUpperCase();
        }
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
            this.showGridLoading();
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showSuccess('Photo uploaded successfully!');
                this.uploadForm.reset();
                
                // Reload all photos
                await this.loadPhotos();
            } else {
                this.showError(data.error || 'Failed to upload photo');
            }
        } catch (error) {
            console.error('Error uploading photo:', error);
            this.showError('Error uploading photo. Please try again.');
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
                this.showError(data.error || 'Failed to add reaction');
            }
        } catch (error) {
            console.error('Error adding reaction:', error);
            this.showError('Failed to add reaction');
        }
    }
}

// Initialize photo manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.photoManager = new PhotoManager();
});
