/**
 * Electro_Fahes - Main JavaScript
 * Additional interactivity and enhancements
 */

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    
    // Mobile Navigation Toggle
    initMobileNav();
    
    // Flash Messages Auto-dismiss
    initFlashMessages();
    
    // Form Validation
    initFormValidation();
    
    // Smooth Scrolling
    initSmoothScroll();
    
    // Image Preview
    initImagePreview();
});

/**
 * Mobile Navigation
 */
function initMobileNav() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        // Toggle menu
        navToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
        
        // Close menu when clicking a link
        const navLinks = navMenu.querySelectorAll('.nav-link:not(.disabled)');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }
}

/**
 * Flash Messages Auto-dismiss
 */
function initFlashMessages() {
    const flashAlerts = document.querySelectorAll('.flash-alert');
    
    flashAlerts.forEach(alert => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
        
        // Manual dismiss on click
        alert.addEventListener('click', () => {
            alert.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => alert.remove(), 300);
        });
    });
}

/**
 * Form Validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = 'var(--error)';
                    
                    setTimeout(() => {
                        input.style.borderColor = '';
                    }, 3000);
                }
            });
            
            // Validate email
            const emailInputs = form.querySelectorAll('input[type="email"]');
            emailInputs.forEach(input => {
                if (input.value && !isValidEmail(input.value)) {
                    isValid = false;
                    input.style.borderColor = 'var(--error)';
                    showMessage('Please enter a valid email address', 'error');
                }
            });
            
            // Validate password length
            const passwordInputs = form.querySelectorAll('input[type="password"]');
            passwordInputs.forEach(input => {
                if (input.value && input.value.length < 6) {
                    isValid = false;
                    input.style.borderColor = 'var(--error)';
                    showMessage('Password must be at least 6 characters', 'error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // Remove error styling on input
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                input.style.borderColor = '';
            });
        });
    });
}

/**
 * Smooth Scrolling
 */
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

/**
 * Image Preview for File Uploads
 */
function initImagePreview() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    // Check if preview element exists
                    let preview = document.getElementById('imagePreview');
                    let previewImg = document.getElementById('previewImg');
                    
                    if (preview && previewImg) {
                        previewImg.src = e.target.result;
                        preview.style.display = 'block';
                    }
                };
                
                reader.readAsDataURL(file);
            }
        });
    });
}

/**
 * Utility Functions
 */

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showMessage(message, type = 'info') {
    const flashContainer = document.querySelector('.flash-container') || createFlashContainer();
    
    const alert = document.createElement('div');
    alert.className = `flash-alert flash-${type}`;
    alert.innerHTML = `
        <div class="flash-icon">
            ${type === 'success' ? '✓' : type === 'error' ? '✕' : type === 'warning' ? '⚠' : 'ℹ'}
        </div>
        <div class="flash-text">${message}</div>
    `;
    
    flashContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
    return container;
}

/**
 * Loading State for Forms
 */
function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span>⏳</span> Processing...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText;
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showMessage,
        setLoading,
        isValidEmail
    };
}