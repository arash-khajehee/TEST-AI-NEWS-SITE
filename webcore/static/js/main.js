// Main JavaScript for News Website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initBackToTop();
    initSearch();
    initComments();
    initSocialSharing();
    initNewsletter();
    initTooltips();
    initLazyLoading();
});

// Back to Top Button
function initBackToTop() {
    const backToTopButton = document.getElementById('backToTop');
    
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'flex';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// Search functionality
function initSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    const searchForm = document.querySelector('form[action*="search"]');
    
    if (searchInput && searchForm) {
        // Add search suggestions (you can implement AJAX search here)
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length > 2) {
                // Implement search suggestions
                debounce(performSearch, 300)(query);
            }
        });
        
        // Clear search on escape
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                this.blur();
            }
        });
    }
}

// Comments functionality
function initComments() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea[name="content"]');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // Comment form validation
    const commentForms = document.querySelectorAll('form[action*="comment"]');
    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const textarea = this.querySelector('textarea[name="content"]');
            if (textarea && textarea.value.trim().length < 10) {
                e.preventDefault();
                showAlert('Comment must be at least 10 characters long.', 'warning');
                textarea.focus();
            }
        });
    });
}

// Social sharing functionality
function initSocialSharing() {
    // Track social sharing clicks
    const socialLinks = document.querySelectorAll('a[href*="facebook.com"], a[href*="twitter.com"], a[href*="linkedin.com"], a[href*="wa.me"]');
    
    socialLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Track share event
            trackShare(this.href);
        });
    });
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('button[onclick*="copyToClipboard"]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            copyToClipboard(url);
        });
    });
}

// Newsletter subscription
function initNewsletter() {
    const newsletterForms = document.querySelectorAll('form[action*="newsletter"]');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const email = this.querySelector('input[name="email"]');
            if (email && !isValidEmail(email.value)) {
                e.preventDefault();
                showAlert('Please enter a valid email address.', 'danger');
                email.focus();
            }
        });
    });
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function performSearch(query) {
    // Implement AJAX search here
    console.log('Searching for:', query);
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Link copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showAlert('Link copied to clipboard!', 'success');
        } else {
            showAlert('Failed to copy link.', 'danger');
        }
    } catch (err) {
        showAlert('Failed to copy link.', 'danger');
    }
    
    document.body.removeChild(textArea);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function trackShare(platform) {
    // Implement analytics tracking here
    console.log('Share tracked:', platform);
    
    // Example: Send to analytics service
    if (typeof gtag !== 'undefined') {
        gtag('event', 'share', {
            'method': platform,
            'content_type': 'article'
        });
    }
}

// Reading progress indicator
function initReadingProgress() {
    const article = document.querySelector('.article-content');
    if (!article) return;
    
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        z-index: 9999;
        transition: width 0.3s ease;
    `;
    
    document.body.appendChild(progressBar);
    
    window.addEventListener('scroll', function() {
        const articleTop = article.offsetTop;
        const articleHeight = article.offsetHeight;
        const windowHeight = window.innerHeight;
        const scrollTop = window.pageYOffset;
        
        const progress = Math.min(
            Math.max((scrollTop - articleTop + windowHeight) / articleHeight, 0),
            1
        );
        
        progressBar.style.width = (progress * 100) + '%';
    });
}

// Initialize reading progress if on article page
if (document.querySelector('.article-content')) {
    initReadingProgress();
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals and clear search
    if (e.key === 'Escape') {
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput && document.activeElement === searchInput) {
            searchInput.value = '';
            searchInput.blur();
        }
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Image zoom functionality
function initImageZoom() {
    const images = document.querySelectorAll('.article-body img');
    
    images.forEach(img => {
        img.style.cursor = 'zoom-in';
        img.addEventListener('click', function() {
            // Create modal for image zoom
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${this.alt || 'Image'}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center">
                            <img src="${this.src}" alt="${this.alt}" class="img-fluid">
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            modal.addEventListener('hidden.bs.modal', function() {
                modal.remove();
            });
        });
    });
}

// Initialize image zoom if on article page
if (document.querySelector('.article-body')) {
    initImageZoom();
}

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        const perfData = performance.getEntriesByType('navigation')[0];
        console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
    });
}

// Service Worker registration (for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}



