/**
 * Custom JavaScript for Resource Planning Application
 * This file contains client-side functionality
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Add confirm dialog to delete buttons
    document.querySelectorAll('.btn-delete').forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Dynamic form fields for project templates
    setupDynamicFormFields();
    
    // Search functionality
    setupSearch();
});

/**
 * Setup dynamic form fields for adding multiple items
 */
function setupDynamicFormFields() {
    // Add phase button for project templates
    var addPhaseBtn = document.getElementById('add-phase-btn');
    if (addPhaseBtn) {
        addPhaseBtn.addEventListener('click', function() {
            var phasesContainer = document.getElementById('phases-container');
            var phaseIndex = phasesContainer.querySelectorAll('.phase-item').length;
            
            var phaseHtml = `
                <div class="card mb-3 phase-item">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span>Phase ${phaseIndex + 1}</span>
                        <button type="button" class="btn btn-sm btn-danger remove-phase-btn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Phase Name</label>
                            <input type="text" class="form-control" name="phase_name[]" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <textarea class="form-control" name="phase_description[]" rows="2"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Duration (days)</label>
                            <input type="number" class="form-control" name="phase_duration[]" min="1">
                        </div>
                    </div>
                </div>
            `;
            
            // Create a temporary container to hold our HTML
            var temp = document.createElement('div');
            temp.innerHTML = phaseHtml;
            
            // Append the new phase to the container
            phasesContainer.appendChild(temp.firstElementChild);
            
            // Add event listener to the remove button
            var removeBtn = phasesContainer.lastElementChild.querySelector('.remove-phase-btn');
            removeBtn.addEventListener('click', function() {
                this.closest('.phase-item').remove();
                // Renumber phases
                document.querySelectorAll('.phase-item').forEach(function(item, index) {
                    item.querySelector('.card-header span').textContent = 'Phase ' + (index + 1);
                });
            });
        });
    }
}

/**
 * Setup search functionality
 */
function setupSearch() {
    var searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                var searchForm = document.getElementById('search-form');
                if (searchForm) {
                    searchForm.submit();
                }
            }
        });
    }
    
    // AJAX search for product catalog
    var catalogSearchInput = document.getElementById('catalog-search');
    if (catalogSearchInput) {
        catalogSearchInput.addEventListener('keyup', function() {
            var query = this.value.trim();
            if (query.length >= 2) {
                fetch('/catalog/search?query=' + encodeURIComponent(query), {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    var resultsContainer = document.getElementById('search-results');
                    if (resultsContainer) {
                        resultsContainer.innerHTML = '';
                        
                        if (data.length === 0) {
                            resultsContainer.innerHTML = '<p class="text-muted">No products found.</p>';
                            return;
                        }
                        
                        var table = document.createElement('table');
                        table.className = 'table table-hover';
                        
                        var thead = document.createElement('thead');
                        thead.innerHTML = `
                            <tr>
                                <th>Name</th>
                                <th>Type</th>
                                <th>Group</th>
                                <th>Actions</th>
                            </tr>
                        `;
                        table.appendChild(thead);
                        
                        var tbody = document.createElement('tbody');
                        data.forEach(function(product) {
                            var tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td>${product.name}</td>
                                <td>${product.type}</td>
                                <td>${product.group || 'N/A'}</td>
                                <td>
                                    <a href="/catalog/view/${product.id}" class="btn btn-sm btn-info">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                </td>
                            `;
                            tbody.appendChild(tr);
                        });
                        table.appendChild(tbody);
                        
                        resultsContainer.appendChild(table);
                    }
                })
                .catch(error => {
                    console.error('Error searching products:', error);
                });
            }
        });
    }
}
