document.addEventListener('DOMContentLoaded', function() {
    // Initialize Flatpickr for date fields
    const flatpickrConfig = {
        dateFormat: "d/m/Y",
        locale: "pt",
        allowInput: true,
        altInput: true,
        altFormat: "d/m/Y",
        disableMobile: true,
        static: true,
        theme: "dark",
        position: "auto",
        monthSelectorType: "static",
        minDate: "today",
        onChange: function(selectedDates, dateStr, instance) {
            // Update summary when date changes
            updateChangeSummary();
        },
        onOpen: function(selectedDates, dateStr, instance) {
            // Add custom class to the calendar for specific styling
            instance.calendarContainer.classList.add('custom-flatpickr');
        }
    };
    
    // Apply Flatpickr to all date fields
    document.querySelectorAll('.flatpickr-date').forEach(function(element) {
        flatpickr(element, flatpickrConfig);
        
        // Add specific styling and behavior for each date picker
        element.addEventListener('focus', function() {
            this.parentNode.classList.add('focused');
        });
        
        element.addEventListener('blur', function() {
            this.parentNode.classList.remove('focused');
            updateChangeSummary();
        });
    });
    
    // Function to update the change summary section
    function updateChangeSummary() {
        // Get all editable fields
        const fields = {
            'data__1': {
                current: document.getElementById('novaDataEntregaAEREO').value,
                original: document.querySelector('input[name="original_data__1"]').value,
                resumeElem: document.getElementById('resumo-data__1'),
                newValueElem: document.getElementById('nova-data__1')
            },
            'date3__1': {
                current: document.getElementById('novaDataEntregaTERRESTRE').value,
                original: document.querySelector('input[name="original_date3__1"]').value,
                resumeElem: document.getElementById('resumo-date3__1'),
                newValueElem: document.getElementById('nova-date3__1')
            },
            'date9__1': {
                current: document.getElementById('novaDataEntregaCRIACAO').value,
                original: document.querySelector('input[name="original_date9__1"]').value,
                resumeElem: document.getElementById('resumo-date9__1'),
                newValueElem: document.getElementById('nova-date9__1')
            },
            'date7__1': {
                current: document.getElementById('novaDataEntregaSALES').value,
                original: document.querySelector('input[name="original_date7__1"]').value,
                resumeElem: document.getElementById('resumo-date7__1'),
                newValueElem: document.getElementById('nova-date7__1')
            },
            'texto16__1': {
                current: document.getElementById('novaOpcao1A').value,
                original: document.querySelector('input[name="original_texto16__1"]').value,
                resumeElem: document.getElementById('resumo-texto16__1'),
                newValueElem: document.getElementById('nova-texto16__1')
            },
            'dup__of_op__o_1c0__1': {
                current: document.getElementById('novaOpcao2A').value,
                original: document.querySelector('input[name="original_dup__of_op__o_1c0__1"]').value,
                resumeElem: document.getElementById('resumo-dup__of_op__o_1c0__1'),
                newValueElem: document.getElementById('nova-dup__of_op__o_1c0__1')
            },
            'dup__of_op__o_2c__1': {
                current: document.getElementById('novaOpcao3A').value,
                original: document.querySelector('input[name="original_dup__of_op__o_2c__1"]').value,
                resumeElem: document.getElementById('resumo-dup__of_op__o_2c__1'),
                newValueElem: document.getElementById('nova-dup__of_op__o_2c__1')
            },
            'dup__of_op__o_3c9__1': {
                current: document.getElementById('novaOpcao4A').value,
                original: document.querySelector('input[name="original_dup__of_op__o_3c9__1"]').value,
                resumeElem: document.getElementById('resumo-dup__of_op__o_3c9__1'),
                newValueElem: document.getElementById('nova-dup__of_op__o_3c9__1')
            }
        };
        
        // Count changes to determine if we show the "no changes" message
        let changeCount = 0;
        
        // Update each field in the summary
        for (const [key, field] of Object.entries(fields)) {
            // Handle empty values consistently
            const current = field.current || '';
            const original = field.original || '';
            
            // Check if value changed
            if (current !== original && current !== '') {
                // Show this change in the summary
                field.resumeElem.style.display = 'block';
                field.newValueElem.textContent = current;
                changeCount++;
            } else {
                // Hide this item from summary
                field.resumeElem.style.display = 'none';
            }
        }
        
        // Show/hide the "no changes" message
        const noChangesMessage = document.getElementById('sem-mudancas');
        if (changeCount === 0) {
            noChangesMessage.style.display = 'block';
        } else {
            noChangesMessage.style.display = 'none';
        }
    }
    
    // Add change event listeners to all text inputs
    document.querySelectorAll('input[type="text"]:not(.flatpickr-date)').forEach(input => {
        input.addEventListener('input', updateChangeSummary);
        input.addEventListener('change', updateChangeSummary);
        input.addEventListener('blur', updateChangeSummary);
    });
    
    // Initialize summary on page load
    updateChangeSummary();
    
    // Validate file size before form submission
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const maxSizeInBytes = 16 * 1024 * 1024; // 16MB
            
            if (this.files.length > 0) {
                const fileSize = this.files[0].size;
                
                if (fileSize > maxSizeInBytes) {
                    this.classList.add('is-invalid');
                    if (!this.nextElementSibling || !this.nextElementSibling.classList.contains('invalid-feedback')) {
                        const feedback = document.createElement('div');
                        feedback.classList.add('invalid-feedback');
                        feedback.textContent = 'O arquivo excede o tamanho máximo de 16MB.';
                        this.parentNode.appendChild(feedback);
                    }
                    // Reset the file input
                    this.value = '';
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                    const invalidFeedback = this.nextElementSibling;
                    if (invalidFeedback && invalidFeedback.classList.contains('invalid-feedback')) {
                        invalidFeedback.remove();
                    }
                }
            }
        });
    }
    
    // Form submission validation
    const form = document.querySelector('form[action="/submit_readequacao"]');
    if (form) {
        form.addEventListener('submit', function(event) {
            // Check if any invalid inputs exist
            const invalidInputs = form.querySelectorAll('.is-invalid');
            if (invalidInputs.length > 0) {
                event.preventDefault();
                // Scroll to the first invalid input
                invalidInputs[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Create alert for user
                const alertDiv = document.createElement('div');
                alertDiv.classList.add('alert', 'alert-danger', 'alert-dismissible', 'fade', 'show');
                alertDiv.innerHTML = 'Por favor, corrija os erros no formulário antes de enviar.<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
                
                // Insert alert at the top of the form
                form.insertBefore(alertDiv, form.firstChild);
            }
        });
    }
    
    // Dismiss alerts after 5 seconds
    document.querySelectorAll('.alert:not(.alert-danger)').forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});
