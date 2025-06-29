document.addEventListener('DOMContentLoaded', function() {
    // Delete confirmation
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    e.preventDefault();
                    field.classList.add('error');
                    const errorMessage = field.parentNode.querySelector('.error-message');
                    if (!errorMessage) {
                        const message = document.createElement('span');
                        message.className = 'error-message';
                        message.style.color = 'var(--danger)';
                        message.style.fontSize = '0.875rem';
                        message.textContent = 'This field is required';
                        field.parentNode.appendChild(message);