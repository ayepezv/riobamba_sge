function openBudgetModal(url) {
    // Create Modal Overlay
    var overlay = document.createElement('div');
    overlay.className = 'budget-modal-overlay';

    // Create Modal Content Container
    var content = document.createElement('div');
    content.className = 'budget-modal-content';

    // Close Button
    var closeBtn = document.createElement('button');
    closeBtn.className = 'budget-modal-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = function () { document.body.removeChild(overlay); };

    // Iframe
    var iframe = document.createElement('iframe');
    iframe.src = url;
    iframe.className = 'budget-modal-frame';

    content.appendChild(closeBtn);
    content.appendChild(iframe);
    overlay.appendChild(content);
    document.body.appendChild(overlay);

    return false; // Prevent default link click
}

document.addEventListener('DOMContentLoaded', function () {
    // Event Delegation for Validation Error Links
    document.body.addEventListener('click', function (e) {
        if (e.target && e.target.classList.contains('filter-partida-error')) {
            e.preventDefault();
            var pid = e.target.getAttribute('data-pid');
            filterTableByPartida(pid);
        }
    });

    // Reset Filter Button (create if needed, easier to just reload but let's be nice)
    // For now, simpler: Users can reload page to reset, or we add a "Show All" button.
});

function filterTableByPartida(pid) {
    var rows = document.querySelectorAll('.dynamic-lineas'); // Jazzmin/Inline rows
    var found = 0;

    rows.forEach(function (row) {
        // Find the select for 'partida'
        // Name format: pac_lineas-{index}-partida
        // Note: Jazzmin inline prefixes might vary, usually [inline_related_name]-[index]-[field]
        // PACLinea related_name='lineas' -> id_lineas-0-partida

        var select = row.querySelector('select[name$="-partida"]');
        if (select) {
            if (select.value == pid) {
                row.style.display = '';
                row.style.backgroundColor = '#fae8e8'; // Highlight Red-ish
                found++;
                // Scroll to first match
                if (found === 1) row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                row.style.display = 'none';
            }
        } else {
            console.log("Select partida not found in row", row);
        }
    });

    // Show a toast or alert
    alert('Mostrando ' + found + ' filas para la partida seleccionada. Recarga la página para ver todas.');
}
