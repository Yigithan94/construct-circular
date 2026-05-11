// Handle delete project
function deleteProject(projectId) {
    if (confirm('Are you sure you want to delete this project?')) {
        fetch(`/project/${projectId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                window.location.reload();
            }
        });
    }
}

// Handle delete criterion
function deleteCriterion(criterionId) {
    if (confirm('Are you sure you want to delete this criterion?')) {
        fetch(`/criterion/${criterionId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                window.location.reload();
            }
        });
    }
}

// Form validation and auto-hide flash messages
document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-hide flash messages after 4 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(alert) {
        // Only auto-hide success and info messages, keep error messages visible
        if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
            setTimeout(function() {
                // Add fade out animation
                alert.style.transition = 'opacity 0.5s ease-out';
                alert.style.opacity = '0';
                
                // Remove from DOM after animation
                setTimeout(function() {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 500);
            }, 4000); // 4 seconds delay
        }
    });

    // Language submenu hover handler
    const languageSubmenu = document.querySelector('.dropdown-submenu');
    const logoutItem = document.querySelector('.logout-item');
    
    if (languageSubmenu && logoutItem) {
        languageSubmenu.addEventListener('mouseenter', function() {
            logoutItem.classList.add('pushed-down');
        });
        
        languageSubmenu.addEventListener('mouseleave', function() {
            logoutItem.classList.remove('pushed-down');
        });
    }
});

// Weight input validation
const weightInput = document.querySelector('input[name="weight"]');
if (weightInput) {
    weightInput.addEventListener('input', function() {
        const value = parseFloat(this.value);
        if (value < 0) this.value = 0;
        if (value > 1) this.value = 1;
    });
}

// Loading Overlay Functions
function showLoading(message = 'İşlem yapılıyor...') {
    // Create overlay if it doesn't exist
    let overlay = document.getElementById('loadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <div class="loading-text">${message}</div>
            </div>
        `;
        document.body.appendChild(overlay);
    } else {
        // Update message if overlay exists
        const textElement = overlay.querySelector('.loading-text');
        if (textElement) {
            textElement.textContent = message;
        }
    }
    
    // Show overlay
    overlay.classList.add('active');
    document.body.style.cursor = 'wait';
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
    document.body.style.cursor = 'default';
}

// Add loading to Calculate TOPSIS button
document.addEventListener('DOMContentLoaded', function() {
    // TOPSIS calculation button
    const topsisButton = document.querySelector('button[type="submit"][name="calculate_topsis"]');
    if (topsisButton) {
        topsisButton.closest('form').addEventListener('submit', function() {
            showLoading('TOPSIS hesaplanıyor... Lütfen bekleyin.');
            topsisButton.classList.add('btn-loading');
        });
    }

    // Save scores button - find by text content
    const allButtons = document.querySelectorAll('button[type="submit"]');
    allButtons.forEach(button => {
        const buttonText = button.textContent.trim();
        if (buttonText.includes('Save') || buttonText.includes('Kaydet')) {
            button.closest('form')?.addEventListener('submit', function() {
                showLoading('Skorlar kaydediliyor...');
                button.classList.add('btn-loading');
            });
        }
    });

    // Generic form submit handler for other forms
    const forms = document.querySelectorAll('form[method="post"]');
    forms.forEach(form => {
        // Skip if already has a specific handler
        if (form.querySelector('button[name="calculate_topsis"]')) return;
        
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.classList.contains('btn-loading')) {
                showLoading('İşlem yapılıyor...');
                submitButton.classList.add('btn-loading');
            }
        });
    });
});
