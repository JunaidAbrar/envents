/**
 * Custom Lightbox Implementation
 * This allows for clicking on images to display them in a larger format
 */
document.addEventListener('DOMContentLoaded', function() {
    // Create lightbox elements
    const lightbox = document.createElement('div');
    lightbox.id = 'lightbox';
    lightbox.className = 'lightbox hidden fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90';
    
    const lightboxContent = document.createElement('div');
    lightboxContent.className = 'lightbox-content relative max-w-5xl w-full mx-4 flex justify-center';
    
    const lightboxImage = document.createElement('img');
    lightboxImage.className = 'object-contain max-h-[85vh] max-w-full w-auto';
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'absolute top-2 right-2 text-white bg-gray-800 bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center';
    closeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>';
    
    const prevBtn = document.createElement('button');
    prevBtn.className = 'absolute left-2 top-1/2 transform -translate-y-1/2 text-white bg-gray-800 bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center';
    prevBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>';
    
    const nextBtn = document.createElement('button');
    nextBtn.className = 'absolute right-2 top-1/2 transform -translate-y-1/2 text-white bg-gray-800 bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center';
    nextBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>';
    
    // Append elements
    lightboxContent.appendChild(lightboxImage);
    lightboxContent.appendChild(closeBtn);
    lightboxContent.appendChild(prevBtn);
    lightboxContent.appendChild(nextBtn);
    lightbox.appendChild(lightboxContent);
    document.body.appendChild(lightbox);
    
    // Variables to track current image and gallery
    let currentImageIndex = 0;
    let galleryImages = [];
    
    // Function to open lightbox
    function openLightbox(imgSrc, index, images) {
        lightboxImage.src = imgSrc;
        currentImageIndex = index;
        galleryImages = images;
        
        // Show/hide navigation buttons based on gallery size
        if (galleryImages.length <= 1) {
            prevBtn.classList.add('hidden');
            nextBtn.classList.add('hidden');
        } else {
            prevBtn.classList.remove('hidden');
            nextBtn.classList.remove('hidden');
        }
        
        lightbox.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent scrolling when lightbox is open
    }
    
    // Function to close lightbox
    function closeLightbox() {
        lightbox.classList.add('hidden');
        document.body.style.overflow = '';
    }
    
    // Function to navigate to previous image
    function showPrevImage() {
        if (galleryImages.length <= 1) return;
        
        currentImageIndex = (currentImageIndex - 1 + galleryImages.length) % galleryImages.length;
        lightboxImage.src = galleryImages[currentImageIndex];
    }
    
    // Function to navigate to next image
    function showNextImage() {
        if (galleryImages.length <= 1) return;
        
        currentImageIndex = (currentImageIndex + 1) % galleryImages.length;
        lightboxImage.src = galleryImages[currentImageIndex];
    }
    
    // Event listeners
    closeBtn.addEventListener('click', closeLightbox);
    prevBtn.addEventListener('click', showPrevImage);
    nextBtn.addEventListener('click', showNextImage);
    
    // Close lightbox when clicking outside the image
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (lightbox.classList.contains('hidden')) return;
        
        if (e.key === 'Escape') {
            closeLightbox();
        } else if (e.key === 'ArrowLeft') {
            showPrevImage();
        } else if (e.key === 'ArrowRight') {
            showNextImage();
        }
    });
    
    // Initialize gallery on all pages
    initializeGallery();
});

// Function to initialize gallery functionality on any page
function initializeGallery() {
    const galleries = document.querySelectorAll('.photo-gallery');
    
    galleries.forEach(gallery => {
        const mainPhoto = gallery.querySelector('.main-photo img');
        const thumbnails = gallery.querySelectorAll('.thumbnail img');
        const lightbox = document.getElementById('lightbox');
        
        // Create array of all image sources in this gallery
        const allImages = Array.from(thumbnails).map(img => img.getAttribute('data-full-src') || img.src);
        
        // Handle main photo click
        if (mainPhoto) {
            mainPhoto.addEventListener('click', function() {
                const mainImgSrc = mainPhoto.getAttribute('data-full-src') || mainPhoto.src;
                let mainImgIndex = allImages.indexOf(mainImgSrc);
                if (mainImgIndex === -1) mainImgIndex = 0;
                
                openLightbox(mainImgSrc, mainImgIndex, allImages);
            });
            
            // Make main photo look clickable
            mainPhoto.classList.add('cursor-pointer', 'hover:opacity-90');
        }
        
        // Handle thumbnail clicks
        thumbnails.forEach((thumbnail, index) => {
            thumbnail.addEventListener('click', function(e) {
                e.preventDefault();
                // Update main photo if it exists
                if (mainPhoto) {
                    const fullSrc = thumbnail.getAttribute('data-full-src') || thumbnail.src;
                    mainPhoto.src = fullSrc;
                    mainPhoto.alt = thumbnail.alt;
                    
                    // Also set data-full-src on main photo if it exists on thumbnail
                    if (thumbnail.getAttribute('data-full-src')) {
                        mainPhoto.setAttribute('data-full-src', thumbnail.getAttribute('data-full-src'));
                    }
                    
                    // Mark this thumbnail as active
                    thumbnails.forEach(t => t.parentNode.classList.remove('ring-2', 'ring-indigo-500'));
                    thumbnail.parentNode.classList.add('ring-2', 'ring-indigo-500');
                }
                
                // Double-click to open the lightbox
                if (e.detail === 2) {
                    const imgSrc = thumbnail.getAttribute('data-full-src') || thumbnail.src;
                    openLightbox(imgSrc, index, allImages);
                }
            });
        });
    });
}

// Global function to open lightbox - can be called from anywhere
function openLightbox(imgSrc, index, images) {
    const lightbox = document.getElementById('lightbox');
    const lightboxImage = lightbox.querySelector('.lightbox-content img');
    const prevBtn = lightbox.querySelector('.lightbox-content button:nth-child(3)');
    const nextBtn = lightbox.querySelector('.lightbox-content button:nth-child(4)');
    
    lightboxImage.src = imgSrc;
    window.currentImageIndex = index;
    window.galleryImages = images;
    
    // Show/hide navigation buttons based on gallery size
    if (images.length <= 1) {
        prevBtn.classList.add('hidden');
        nextBtn.classList.add('hidden');
    } else {
        prevBtn.classList.remove('hidden');
        nextBtn.classList.remove('hidden');
    }
    
    lightbox.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent scrolling when lightbox is open
}