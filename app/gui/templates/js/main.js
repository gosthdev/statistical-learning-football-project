window.addEventListener('pywebviewready', () => {
    const sidebarContainer = document.getElementById('sidebar-container');
    const mainContent = document.getElementById('main-content');

    // Add event listeners to the menu links
    function addNavListeners() {
        const navLinks = sidebarContainer.querySelectorAll('.nav-item');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const viewName = link.getAttribute('data-view');
                window.location.hash = viewName; // Update hash for state
            });
        });

        // Listen for hash changes to navigate
        window.addEventListener('hashchange', () => {
            const viewName = window.location.hash.substring(1) || 'dashboard';
            loadView(viewName);
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
            
            viewContainer = document.createElement('div');
            viewContainer.id = viewId;
            viewContainer.className = 'view-container';
            mainContent.appendChild(viewContainer);
    
            try {
                const response = await fetch(`${viewName}.html`);
                if (!response.ok) {
                    throw new Error(`Could not load ${viewName}.html (Status: ${response.status})`);
                }
                
                const html = await response.text();
                viewContainer.innerHTML = html;
    
                // Ejecuta los inicializadores específicos de la vista.
                if (viewName === 'dashboard') {
                    initializeDashboard();
                } else if (viewName === 'predictions') {
                    initializePredictions();
                }
    
            } catch (error) {
                console.error(`Error loading view: ${viewName}`, error);
                viewContainer.innerHTML = `<div class="welcome-message"><h2>Error loading page.</h2><p>Could not find content for '${viewName}'.</p></div>`;
            }
        } else {
            console.log(`Showing cached view '${viewName}'.`);
        }
    
        viewContainer.style.display = 'flex';
        document.title = `${viewName.charAt(0).toUpperCase() + viewName.slice(1)} - Goal Predictor`;
        updateActiveLink(viewName);
    }
    
    // Update which menu link appears as "active"
    function updateActiveLink(activeView) {
        const navLinks = sidebarContainer.querySelectorAll('.nav-item');
        navLinks.forEach(link => {
            if (link.getAttribute('data-view') === activeView) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    // --- START THE APPLICATION ---
    async function initializeApp() {
        try {
            // 1. Cargar la barra lateral y los listeners
            const sidebarResponse = await fetch('sidebar.html');
            if (!sidebarResponse.ok) throw new Error('Could not load sidebar.');
            sidebarContainer.innerHTML = await sidebarResponse.text();
            addNavListeners();

            // 2. Eliminar el mensaje de bienvenida
            const welcomeMessage = mainContent.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }

            // 3. Cargar la vista inicial (ya no necesitamos comprobar datos aquí)
            const initialView = window.location.hash.substring(1) || 'dashboard';
            console.log(`Loading initial view: ${initialView}`);
            loadView(initialView);

        } catch (error) {
            console.error('Error initializing the app:', error);
            mainContent.innerHTML = `<div class="welcome-message"><h2>Fatal error loading the application.</h2><p>${error.message}</p></div>`;
        }
    }

    initializeApp();
});