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
            atualizarResumoMudancas();
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
            atualizarResumoMudancas();
        });
    });


    // Add change event listeners to all text inputs
    Object.values(fields).forEach(field => {
        const input = document.getElementById(field.inputId);
        if (input) {
            input.addEventListener('input', atualizarResumoMudancas);
            input.addEventListener('change', atualizarResumoMudancas);
        }
    });

    // Initialize summary on page load
    atualizarResumoMudancas();

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

// Function to safely get input value
function getInputValue(elementId) {
    const element = document.getElementById(elementId);
    return element ? element.value : '';
}

// Function to safely get hidden value
function getHiddenValue(elementName) {
    const element = document.querySelector(`input[name="original_${elementName}"]`);
    if (!element) return '';
    const value = element.value;
    return value === '""' || value === 'None' ? '' : value;
}

// Function to check if value is empty
function isEmpty(value) {
    if (value === null || value === undefined) return true;
    return value.trim() === '' || value === 'None' || value === '""';
}

// Define field mappings
const fields = {
    'data__1': {
        inputId: 'novaDataEntregaAEREO',
        resumeId: 'resumo-data__1',
        newValueId: 'nova-data__1'
    },
    'date3__1': {
        inputId: 'novaDataEntregaTERRESTRE',
        resumeId: 'resumo-date3__1',
        newValueId: 'nova-date3__1'
    },
    'date9__1': {
        inputId: 'novaDataEntregaCRIACAO',
        resumeId: 'resumo-date9__1',
        newValueId: 'nova-date9__1'
    },
    'date7__1': {
        inputId: 'novaDataEntregaSALES',
        resumeId: 'resumo-date7__1',
        newValueId: 'nova-date7__1'
    },
    'texto16__1': {
        inputId: 'novaOpcao1A',
        resumeId: 'resumo-texto16__1',
        newValueId: 'nova-texto16__1'
    },
    'dup__of_op__o_1a__1': {
        inputId: 'novaOpcao1B',
        resumeId: 'resumo-dup__of_op__o_1a__1',
        newValueId: 'nova-dup__of_op__o_1a__1'
    },
    'text0__1': {
        inputId: 'novaOpcao1C',
        resumeId: 'resumo-text0__1',
        newValueId: 'nova-text0__1'
    },
    'dup__of_op__o_1c0__1': {
        inputId: 'novaOpcao2A',
        resumeId: 'resumo-dup__of_op__o_1c0__1',
        newValueId: 'nova-dup__of_op__o_1c0__1'
    },
    'dup__of_op__o_1c5__1': {
        inputId: 'novaOpcao2B',
        resumeId: 'resumo-dup__of_op__o_1c5__1',
        newValueId: 'nova-dup__of_op__o_1c5__1'
    },
    'dup__of_op__o_1c__1': {
        inputId: 'novaOpcao2C',
        resumeId: 'resumo-dup__of_op__o_1c__1',
        newValueId: 'nova-dup__of_op__o_1c__1'
    },
    'dup__of_op__o_2c__1': {
        inputId: 'novaOpcao3A',
        resumeId: 'resumo-dup__of_op__o_2c__1',
        newValueId: 'nova-dup__of_op__o_2c__1'
    },
    'dup__of_op__o_3a__1': {
        inputId: 'novaOpcao3B',
        resumeId: 'resumo-dup__of_op__o_3a__1',
        newValueId: 'nova-dup__of_op__o_3a__1'
    },
    'dup__of_op__o_3b__1': {
        inputId: 'novaOpcao3C',
        resumeId: 'resumo-dup__of_op__o_3b__1',
        newValueId: 'nova-dup__of_op__o_3b__1'
    },
    'dup__of_op__o_3c9__1': {
        inputId: 'novaOpcao4A',
        resumeId: 'resumo-dup__of_op__o_3c9__1',
        newValueId: 'nova-dup__of_op__o_3c9__1'
    },
    'dup__of_op__o_3c4__1': {
        inputId: 'novaOpcao4B',
        resumeId: 'resumo-dup__of_op__o_3c4__1',
        newValueId: 'nova-dup__of_op__o_3c4__1'
    },
    'dup__of_op__o_3c__1': {
        inputId: 'novaOpcao4C',
        resumeId: 'resumo-dup__of_op__o_3c__1',
        newValueId: 'nova-dup__of_op__o_3c__1'
    }
};

// Function to update the summary of changes
function atualizarResumoMudancas() {
    let hasChanges = false;

    // Process each field
    Object.entries(fields).forEach(([fieldName, fieldInfo]) => {
        const currentValue = getInputValue(fieldInfo.inputId);
        const originalValue = getHiddenValue(fieldName);
        const resumeElem = document.getElementById(fieldInfo.resumeId);
        const newValueElem = document.getElementById(fieldInfo.newValueId);

        if (!resumeElem || !newValueElem) return;

        if (currentValue && !isEmpty(currentValue) && currentValue !== originalValue) {
            resumeElem.style.display = 'block';
            newValueElem.textContent = currentValue;
            hasChanges = true;
        } else {
            resumeElem.style.display = 'none';
        }
    });

    // Update no changes message
    const semMudancas = document.getElementById('sem-mudancas');
    if (semMudancas) {
        semMudancas.style.display = hasChanges ? 'none' : 'block';
    }
}
