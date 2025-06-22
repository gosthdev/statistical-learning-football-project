function initializeDashboard() {
    console.log("Initializing dashboard view...");

    // El caché de datos ahora es local a la lógica del dashboard
    let data = null; 

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

    // Función para renderizar la tabla con los datos
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

    // Función asíncrona para llamar a la API de Python
    async function loadData() {
        try {
            loadingMessage.textContent = 'Fetching data from Python API...';
            loadingMessage.style.display = 'block';
            
            const jsonString = await pywebview.api.get_data();
            console.log("Received data from API:\n", jsonString);
            const parsedData = JSON.parse(jsonString);

            if (parsedData.error) {
                throw new Error(parsedData.error);
            }

            // Guardamos los datos en nuestra variable de caché
            data = parsedData; 
            renderTable(data);

        } catch (error) {
            console.error('Error loading data:', error);
            loadingMessage.textContent = 'Failed to load data. Please try again later.';
        }
    }

    // --- LÓGICA DE CACHÉ ---
    // Si ya tenemos los datos, simplemente renderizamos la tabla.
    if (data) {
        console.log("Using cached data to render the table.");
        renderTable(data);
    } else {
        // Si no, los cargamos desde la API.
        loadData();
    }
}