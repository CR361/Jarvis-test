/**
 * Jarvis CRM - Main JavaScript Functions
 */

// Initialisatie wanneer document geladen is
document.addEventListener('DOMContentLoaded', function() {
    // Setup datatables indien beschikbaar
    initializeDatatables();
    
    // Initialiseer tooltips
    initializeTooltips();
    
    // Voeg event listeners toe voor dynamische elementen
    setupDynamicEvents();
});

/**
 * Initialiseer DataTables voor betere tabelweergave indien beschikbaar
 */
function initializeDatatables() {
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.datatable').DataTable({
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.25/i18n/Dutch.json"
            },
            pageLength: 25,
            responsive: true
        });
    }
}

/**
 * Initialiseer Bootstrap tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Voeg event listeners toe voor dynamische elementen
 */
function setupDynamicEvents() {
    // Dynamisch toevoegen van factuuritems
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            const itemsContainer = document.getElementById('invoice-items');
            const itemCount = itemsContainer.getElementsByClassName('invoice-item').length;
            
            const newItem = document.createElement('div');
            newItem.className = 'invoice-item row mb-3';
            newItem.innerHTML = `
                <div class="col-md-6">
                    <input type="text" name="item_description[]" class="form-control" placeholder="Omschrijving" required>
                </div>
                <div class="col-md-2">
                    <input type="number" name="item_quantity[]" class="form-control" placeholder="Aantal" min="0.01" step="0.01" value="1" required>
                </div>
                <div class="col-md-3">
                    <input type="number" name="item_unit_price[]" class="form-control" placeholder="Prijs per eenheid" min="0.01" step="0.01" required>
                </div>
                <div class="col-md-1">
                    <button type="button" class="btn btn-danger btn-sm remove-item-btn">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            `;
            
            itemsContainer.appendChild(newItem);
            
            // Voeg event listener toe aan de verwijderknop
            const removeBtn = newItem.querySelector('.remove-item-btn');
            removeBtn.addEventListener('click', function() {
                newItem.remove();
            });
        });
    }
    
    // Verwijderen van factuuritems (voor bestaande items)
    document.querySelectorAll('.remove-item-btn').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.invoice-item').remove();
        });
    });
    
    // Template select voor contracten
    const templateSelect = document.getElementById('template-select');
    if (templateSelect) {
        templateSelect.addEventListener('change', function() {
            if (this.value) {
                window.location.href = window.location.pathname + '?template=' + this.value;
            }
        });
    }
}

/**
 * Bereken totalen voor factuuritems
 */
function calculateInvoiceTotals() {
    let total = 0;
    
    // Verzamel alle items
    document.querySelectorAll('.invoice-item').forEach(item => {
        const quantity = parseFloat(item.querySelector('input[name="item_quantity[]"]').value) || 0;
        const unitPrice = parseFloat(item.querySelector('input[name="item_unit_price[]"]').value) || 0;
        const itemTotal = quantity * unitPrice;
        
        // Update subtotaal indien nodig
        const subtotalEl = item.querySelector('.item-subtotal');
        if (subtotalEl) {
            subtotalEl.textContent = '€' + itemTotal.toFixed(2);
        }
        
        total += itemTotal;
    });
    
    // Update totaal indien het element bestaat
    const totalEl = document.getElementById('invoice-total');
    if (totalEl) {
        totalEl.textContent = '€' + total.toFixed(2);
    }
}

/**
 * Bevestig verwijderacties met een dialoog
 */
function confirmDelete(message) {
    return confirm(message || 'Weet u zeker dat u dit item wilt verwijderen?');
}

/**
 * Helper functie om AJAX-verzoeken te versturen
 */
function sendAjaxRequest(url, method, data, onSuccess, onError) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    
    // CSRF-token uit de meta-tag halen en meesturen
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (token) {
        xhr.setRequestHeader('X-CSRF-TOKEN', token);
    }
    
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            if (onSuccess) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    onSuccess(response);
                } catch (e) {
                    onSuccess(xhr.responseText);
                }
            }
        } else {
            if (onError) {
                onError(xhr.statusText, xhr.status);
            } else {
                console.error('AJAX Error:', xhr.statusText);
            }
        }
    };
    
    xhr.onerror = function() {
        if (onError) {
            onError('Network Error');
        } else {
            console.error('Network Error');
        }
    };
    
    xhr.send(data ? JSON.stringify(data) : null);
}