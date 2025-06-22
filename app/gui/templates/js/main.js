document.addEventListener('DOMContentLoaded', () => {
    const sidebarContainer = document.getElementById('sidebar-container');
    const mainContent = document.getElementById('main-content');
    let data = null;
    // --- NAVIGATION CORE ---

    // Main function to initialize the application
    async function initializeApp() {
        try {
            // CHANGE: Use a relative path instead of the absolute file system path.
            const response = await fetch('sidebar.html');
            if (!response.ok) throw new Error('Could not load sidebar.');
            sidebarContainer.innerHTML = await response.text();
            addNavListeners();

            // Elimina el mensaje de bienvenida inicial antes de cargar la primera vista.
            const welcomeMessage = mainContent.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }

            // Load initial view based on URL hash or default to dashboard
            const initialView = window.location.hash.substring(1) || 'dashboard';
            loadView(initialView);
        } catch (error) {
            console.error('Error initializing the app:', error);
            mainContent.innerHTML = `<div class="welcome-message"><h2>Fatal error loading the application.</h2></div>`;
        }
    }

    // Add event listeners to the menu links
    function addNavListeners() {
        sidebarContainer.addEventListener('click', (e) => {
            if (e.target.matches('a.nav-item')) {
                e.preventDefault();
                const viewName = e.target.dataset.view;
                if (viewName) {
                    window.location.hash = viewName;
                    loadView(viewName);
                }
            }
        });
    }

    // Load the content of a view into the main area
    async function loadView(viewName) {
        // Oculta todas las vistas existentes
        const views = mainContent.querySelectorAll('.view-container');
        views.forEach(view => view.style.display = 'none');
    
        const viewId = `view-${viewName}`;
        let viewContainer = document.getElementById(viewId);
    
        // Si la vista no existe en el DOM, la creamos y la llenamos
        if (!viewContainer) {
            console.log(`Creating view '${viewName}' for the first time.`);
            
            // 1. Crea el contenedor de la vista primero y añádelo al DOM.
            viewContainer = document.createElement('div');
            viewContainer.id = viewId;
            viewContainer.className = 'view-container';
            mainContent.appendChild(viewContainer);
    
            try {
                // 2. Intenta buscar el contenido HTML.
                const response = await fetch(`${viewName}.html`);
                if (!response.ok) {
                    throw new Error(`Could not load ${viewName}.html (Status: ${response.status})`);
                }
                
                const html = await response.text();
                viewContainer.innerHTML = html;
    
                // 3. Ejecuta los inicializadores específicos de la vista.
                if (viewName === 'dashboard') {
                    initializeDashboard();
                } else if (viewName === 'predictions') {
                    initializePredictions();
                }
    
            } catch (error) {
                // 4. En caso de fallo, pon el mensaje de error DENTRO del contenedor de la vista.
                console.error(`Error loading view: ${viewName}`, error);
                viewContainer.innerHTML = `<div class="welcome-message"><h2>Error loading page.</h2><p>Could not find content for '${viewName}'.</p></div>`;
            }
        } else {    
            console.log(`Showing cached view '${viewName}'.`);
        }
    
        // 5. Muestra el contenedor de la vista correcta (ya sea con contenido o con un error).
        viewContainer.style.display = 'flex';
        document.title = `${viewName.charAt(0).toUpperCase() + viewName.slice(1)} - Goal Predictor`;
        updateActiveLink(viewName);
    }
    
    // Update which menu link appears as "active"
    function updateActiveLink(activeView) {
        sidebarContainer.querySelectorAll('.nav-item').forEach(link => {
            if (link.dataset.view === activeView) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    // --- DASHBOARD SPECIFIC LOGIC ---

    // Initialize everything needed for the dashboard view
    function initializeDashboard() {
        const tableHead = mainContent.querySelector('#data-table thead');
        const tableBody = mainContent.querySelector('#data-table tbody');
        const loadingMessage = mainContent.querySelector('#loading-message');

        if (!tableHead || !tableBody || !loadingMessage) {
            console.error('Dashboard table elements not found!');
            return;
        }

        // Function to render the table with the data
        function renderTable(data) {
            if (!data || data.length === 0) {
                loadingMessage.textContent = 'No data available to display.';
                return;
            }

            const headers = Object.keys(data[0]);
            tableHead.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;

            tableBody.innerHTML = data.map(row => 
                `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
            ).join('');

            loadingMessage.style.display = 'none';
        }

        // Async function to call the Python API
        async function loadData() {
            try {
                // This will be replaced by a real API call to the Python backend
                loadingMessage.textContent = 'Loading data...';
                
                if (data === null) {
                    console.log('Fetching data from Python API...');
                    const jsonString = await pywebview.api.get_data();
                    // Parse the JSON string into a JavaScript array of objects
                    data = JSON.parse(jsonString);
                }
                renderTable(data);

            } catch (error) {
                console.error('Error loading data:', error);
                loadingMessage.textContent = 'Failed to load data. Please try again later.';
            }
        }
        
        loadData(); // Call the function to get the data
    }

    // --- START THE APPLICATION ---
    initializeApp();
});