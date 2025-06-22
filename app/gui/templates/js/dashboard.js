function initializeDashboard() {
    console.log("Initializing dashboard view...");

    const viewContainer = document.getElementById('view-dashboard');
    if (!viewContainer) {
        console.error("Dashboard view container not found!");
        return;
    }

    const tableHead = viewContainer.querySelector('#data-table thead');
    const tableBody = viewContainer.querySelector('#data-table tbody');
    const loadingMessage = viewContainer.querySelector('#loading-message');

    if (!tableHead || !tableBody || !loadingMessage) {
        console.error('Dashboard table elements not found!');
        return;
    }

    // La función de renderizado no cambia.
    function renderTable(dataToRender) {
        if (!dataToRender || dataToRender.length === 0) {
            loadingMessage.textContent = 'No data available to display.';
            return;
        }
        const headers = Object.keys(dataToRender[0]);
        tableHead.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
        tableBody.innerHTML = dataToRender.map(row => 
            `<tr>${headers.map(h => `<td>${row[h] === null ? 'null' : row[h]}</td>`).join('')}</tr>`
        ).join('');
        loadingMessage.style.display = 'none';
    }

    // --- LÓGICA "PUSH" ---
    // 1. Definimos las funciones globales que Python puede llamar.
    window.renderDashboardData = (data) => {
        console.log("Data received from Python push.");
        renderTable(data);
    };

    window.renderDashboardError = (errorMessage) => {
        console.error("Error pushed from Python:", errorMessage);
        loadingMessage.textContent = errorMessage;
        loadingMessage.style.display = 'block';
    };

    // 2. Solicitamos los datos a Python (llamada "dispara y olvida").
    try {
        loadingMessage.textContent = 'Requesting data from Python...';
        loadingMessage.style.display = 'block';
        pywebview.api.get_data();
    } catch (e) {
        renderDashboardError(`Failed to call API: ${e.message}`);
    }
}