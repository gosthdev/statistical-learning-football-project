document.addEventListener('DOMContentLoaded', () => {
    const sidebarContainer = document.getElementById('sidebar-container');
    const mainContent = document.getElementById('main-content');

    // --- NAVIGATION CORE ---

    // Main function to initialize the application
    async function initializeApp() {
        try {
            // CHANGE: Use a relative path instead of the absolute file system path.
            const response = await fetch('sidebar.html');
            if (!response.ok) throw new Error('Could not load sidebar.');
            sidebarContainer.innerHTML = await response.text();
            addNavListeners();
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
        try {
            const response = await fetch(`${viewName}.html`);
            if (!response.ok) throw new Error(`Could not find ${viewName}.html`);

            mainContent.innerHTML = await response.text();
            document.title = `${viewName.charAt(0).toUpperCase() + viewName.slice(1)} - Goal Predictor`;
            updateActiveLink(viewName);

            // If the dashboard is loaded, initialize its specific logic
            if (viewName === 'dashboard') {
                initializeDashboard();
            }
        } catch (error) {
            console.error(`Error loading view: ${viewName}`, error);
            mainContent.innerHTML = `<div class="welcome-message"><h2>Error loading page.</h2></div>`;
        }
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
                
                const jsonString = await pywebview.api.get_data();
                // Parse the JSON string into a JavaScript array of objects
                const data = JSON.parse(jsonString);
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