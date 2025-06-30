class APIFormManager {
    constructor() {
        this.apiCounter = 0;
        this.init();
    }

    init() {
        this.bindEvents();
        this.addAPI(); // Add the first API by default
    }

    bindEvents() {
        // Add API button
        document.getElementById('add-api-btn').addEventListener('click', () => {
            this.addAPI();
        });

        // Reset form button
        document.getElementById('reset-form-btn').addEventListener('click', () => {
            this.resetForm();
        });

        // Form submission
        document.getElementById('yaml-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateYAML();
        });

        // Event delegation for dynamic elements
        document.getElementById('apis-container').addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-api-btn') || e.target.closest('.remove-api-btn')) {
                this.removeAPI(e.target.closest('.api-section'));
            } else if (e.target.classList.contains('add-header-btn') || e.target.closest('.add-header-btn')) {
                this.addHeader(e.target.closest('.api-section'));
            } else if (e.target.classList.contains('remove-header-btn') || e.target.closest('.remove-header-btn')) {
                this.removeHeader(e.target.closest('.header-item'));
            } else if (e.target.classList.contains('add-extractor-btn') || e.target.closest('.add-extractor-btn')) {
                this.addExtractor(e.target.closest('.api-section'));
            } else if (e.target.classList.contains('remove-extractor-btn') || e.target.closest('.remove-extractor-btn')) {
                this.removeExtractor(e.target.closest('.extractor-item'));
            }
        });
    }

    addAPI() {
        this.apiCounter++;
        const template = document.getElementById('api-template');
        const clone = template.content.cloneNode(true);
        
        // Update API number
        clone.querySelector('.api-number').textContent = this.apiCounter;
        
        // Add to container
        document.getElementById('apis-container').appendChild(clone);
        
        // Update remove button visibility
        this.updateRemoveButtonsVisibility();
    }

    removeAPI(apiSection) {
        if (document.querySelectorAll('.api-section').length > 1) {
            apiSection.remove();
            this.renumberAPIs();
            this.updateRemoveButtonsVisibility();
        }
    }

    renumberAPIs() {
        const apiSections = document.querySelectorAll('.api-section');
        apiSections.forEach((section, index) => {
            section.querySelector('.api-number').textContent = index + 1;
        });
        this.apiCounter = apiSections.length;
    }

    updateRemoveButtonsVisibility() {
        const apiSections = document.querySelectorAll('.api-section');
        const removeButtons = document.querySelectorAll('.remove-api-btn');
        
        removeButtons.forEach(button => {
            button.style.display = apiSections.length > 1 ? 'inline-block' : 'none';
        });
    }

    addHeader(apiSection) {
        const template = document.getElementById('header-template');
        const clone = template.content.cloneNode(true);
        const headersContainer = apiSection.querySelector('.headers-container');
        headersContainer.appendChild(clone);
    }

    removeHeader(headerItem) {
        headerItem.remove();
    }

    addExtractor(apiSection) {
        const template = document.getElementById('extractor-template');
        const clone = template.content.cloneNode(true);
        const extractorsContainer = apiSection.querySelector('.extractors-container');
        extractorsContainer.appendChild(clone);
    }

    removeExtractor(extractorItem) {
        extractorItem.remove();
    }

    resetForm() {
        if (confirm('Are you sure you want to reset the form? All data will be lost.')) {
            // Clear service name
            document.getElementById('service-name').value = '';
            
            // Clear all APIs
            document.getElementById('apis-container').innerHTML = '';
            this.apiCounter = 0;
            
            // Add one default API
            this.addAPI();
            
            // Hide alerts
            this.hideAlerts();
        }
    }

    collectFormData() {
        const formData = {
            service_name: document.getElementById('service-name').value.trim(),
            apis: []
        };

        const apiSections = document.querySelectorAll('.api-section');
        
        apiSections.forEach(section => {
            const apiData = {
                name: section.querySelector('.api-name').value.trim(),
                method: section.querySelector('.api-method').value,
                url: section.querySelector('.api-url').value.trim(),
                status_code: section.querySelector('.api-status-code').value,
                repeat: section.querySelector('.api-repeat').value,
                payload: section.querySelector('.api-payload').value.trim(),
                headers: [],
                extractors: []
            };

            // Collect headers
            const headerItems = section.querySelectorAll('.header-item');
            headerItems.forEach(item => {
                const key = item.querySelector('.header-key').value.trim();
                const value = item.querySelector('.header-value').value.trim();
                if (key && value) {
                    apiData.headers.push({ key, value });
                }
            });

            // Collect extractors
            const extractorItems = section.querySelectorAll('.extractor-item');
            extractorItems.forEach(item => {
                const type = item.querySelector('.extractor-type').value;
                const key = item.querySelector('.extractor-key').value.trim();
                const value = item.querySelector('.extractor-value').value.trim();
                if (key && value) {
                    apiData.extractors.push({ type, key, value });
                }
            });

            formData.apis.push(apiData);
        });

        return formData;
    }

    async generateYAML() {
        try {
            // Show loading state
            const generateBtn = document.getElementById('generate-yaml-btn');
            const originalText = generateBtn.innerHTML;
            generateBtn.innerHTML = 'Generating...';
            generateBtn.disabled = true;
            
            // Hide previous alerts
            this.hideAlerts();

            // Collect form data
            const formData = this.collectFormData();

            // Send to server
            const response = await fetch('/generate_yaml', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                // Show success message
                this.showSuccess();
                
                // Trigger download
                this.downloadYAML(result.yaml_content, result.filename);
            } else {
                // Show errors
                this.showErrors(result.errors || ['Unknown error occurred']);
            }

        } catch (error) {
            console.error('Error generating YAML:', error);
            this.showErrors(['Network error: Could not connect to server']);
        } finally {
            // Reset button state
            const generateBtn = document.getElementById('generate-yaml-btn');
            generateBtn.innerHTML = 'Generate YAML';
            generateBtn.disabled = false;
        }
    }

    downloadYAML(yamlContent, filename) {
        // Create blob and download
        const blob = new Blob([yamlContent], { type: 'application/x-yaml' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    showErrors(errors) {
        const errorAlert = document.getElementById('error-alert');
        const errorList = document.getElementById('error-list');
        
        errorList.innerHTML = '';
        errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error;
            errorList.appendChild(li);
        });
        
        errorAlert.classList.remove('d-none');
        errorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    showSuccess() {
        const successAlert = document.getElementById('success-alert');
        successAlert.classList.remove('d-none');
        successAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Hide success message after 5 seconds
        setTimeout(() => {
            successAlert.classList.add('d-none');
        }, 5000);
    }

    hideAlerts() {
        document.getElementById('error-alert').classList.add('d-none');
        document.getElementById('success-alert').classList.add('d-none');
    }
}

// Initialize the form manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new APIFormManager();
});
