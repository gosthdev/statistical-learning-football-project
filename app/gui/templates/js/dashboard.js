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
    const tableContainer = viewContainer.querySelector('#table-container');

    if (!tableHead || !tableBody || !loadingMessage || !tableContainer) {
        console.error('Dashboard table elements not found!');
        return;
    }

    // State variables for infinite scrolling
    let currentPage = 0;
    let pageSize = 100;
    let isLoading = false;
    let hasMoreData = true;
    let totalRecords = 0;

    // Function to render initial table
    function renderInitialTable(dataToRender, total = null) {
        if (!dataToRender || dataToRender.length === 0) {
            loadingMessage.textContent = 'No data available to display.';
            return;
        }
        
        totalRecords = total || dataToRender.length;
        
        // Render headers once
        const headers = Object.keys(dataToRender[0]);
        tableHead.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
        
        // Render initial rows
        tableBody.innerHTML = dataToRender.map(row => 
            `<tr>${headers.map(h => `<td>${row[h] === null ? 'null' : row[h]}</td>`).join('')}</tr>`
        ).join('');
        
        loadingMessage.style.display = 'none';
        
        // Show record count info
        const infoElement = document.createElement('div');
        infoElement.className = 'table-info';
        infoElement.id = 'table-info';
        infoElement.textContent = `Showing ${dataToRender.length} of ${totalRecords} records`;
        tableContainer.appendChild(infoElement);
        
        // Set initial page
        currentPage = 0;
        hasMoreData = dataToRender.length < totalRecords;
    }
    
    // Function to append more rows to the existing table
    function appendRows(dataToRender) {
        if (!dataToRender || dataToRender.length === 0) {
            return;
        }
        
        // Get headers from the table
        const headers = Array.from(tableHead.querySelectorAll('th')).map(th => th.textContent);
        
        // Create HTML for new rows
        const newRowsHtml = dataToRender.map(row => 
            `<tr>${headers.map(h => `<td>${row[h] === null ? 'null' : row[h]}</td>`).join('')}</tr>`
        ).join('');
        
        // Append to existing content
        tableBody.innerHTML += newRowsHtml;
        
        // Update info text
        const infoElement = document.getElementById('table-info');
        if (infoElement) {
            const currentCount = tableBody.querySelectorAll('tr').length;
            infoElement.textContent = `Showing ${currentCount} of ${totalRecords} records`;
        }
    }
    
    // Function to load more data when scrolling
    function loadMoreData() {
        if (isLoading || !hasMoreData) return;
        
        isLoading = true;
        
        // Add loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'loading-indicator';
        loadingIndicator.textContent = 'Loading more records...';
        tableContainer.appendChild(loadingIndicator);
        
        // Request next page
        currentPage++;
        const startIndex = currentPage * pageSize;
        
        console.log(`Requesting more data from index ${startIndex}`);
        
        pywebview.api.get_more_data(startIndex, pageSize)
            .then(nextBatch => {
                if (nextBatch && nextBatch.length > 0) {
                    appendRows(nextBatch);
                    hasMoreData = (startIndex + nextBatch.length) < totalRecords;
                } else {
                    hasMoreData = false;
                }
            })
            .catch(error => {
                console.error('Error loading more data:', error);
                hasMoreData = false;
            })
            .finally(() => {
                loadingIndicator.remove();
                isLoading = false;
            });
    }

    // Add scroll event listener
    tableContainer.addEventListener('scroll', () => {
        // Check if scrolled near bottom
        const { scrollTop, scrollHeight, clientHeight } = tableContainer;
        
        // If scrolled within 100px of bottom, load more data
        if (scrollHeight - scrollTop - clientHeight < 100 && hasMoreData) {
            loadMoreData();
        }
    });

    // --- LÓGICA "PUSH" ---
    // 1. Definimos las funciones globales que Python puede llamar.
    window.renderDashboardData = (data, total = null) => {
        console.log("Data received from Python push.", 
                   Array.isArray(data) ? `${data.length} rows` : 'not an array');
        
        if (Array.isArray(data)) {
            renderInitialTable(data, total);
        } else {
            loadingMessage.textContent = 'Received invalid data format.';
        }
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