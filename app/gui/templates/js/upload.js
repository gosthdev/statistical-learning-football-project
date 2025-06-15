document.addEventListener('DOMContentLoaded', () => {
    // Selección de elementos del DOM
    const dropZone = document.getElementById('drop-zone');
    const browseBtn = document.getElementById('browse-btn');
    const fileInput = document.getElementById('file-input');
    const loadDefaultBtn = document.getElementById('load-default-btn');
    const fileListContainer = document.getElementById('file-list-container');
    const fileList = document.getElementById('file-list');
    const processBtn = document.getElementById('process-btn');

    let loadedFiles = []; // Array para almacenar los archivos cargados (nombres o rutas)

    // --- MANEJADORES DE EVENTOS ---

    // Abrir selector de archivos al hacer clic en "Browse"
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // Manejar archivos seleccionados desde el input
    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
        fileInput.value = ''; // Reset file input to allow selecting the same file again if removed
    });

    // Cargar datasets por defecto
    loadDefaultBtn.addEventListener('click', async () => {
        try {
            const defaultFiles = await pywebview.api.load_default_datasets();
            if (defaultFiles && defaultFiles.length > 0) {
                // Avoid adding duplicates if already loaded
                const newDefaultFiles = defaultFiles
                    .map(fileName => ({ name: fileName, path: null, type: 'default' }))
                    .filter(df => !loadedFiles.some(lf => lf.type === 'default' && lf.name === df.name));
                
                loadedFiles = loadedFiles.concat(newDefaultFiles);
                updateFileListUI();
            } else {
                alert('No default datasets found or an error occurred.');
            }
        } catch (error) {
            console.error('Error loading default datasets:', error);
            alert('Failed to load default datasets.');
        }
    });

    // Iniciar procesamiento de archivos
    processBtn.addEventListener('click', async () => {
        if (loadedFiles.length === 0) return;
        // Deshabilita el botón para evitar clics múltiples
        processBtn.disabled = true;
        processBtn.textContent = 'Processing...';
        
        try {
            // Llama a la API de Python para que procese los archivos
            const response = await window.webview.api.process_files(loadedFiles);
            console.log(response.message);
            // Aquí podrías mostrar un mensaje de éxito y navegar a la siguiente pantalla (dashboard)
            // window.location.href = 'dashboard.html';
        } catch (error) {
            console.error('Error processing files:', error);
        } finally {
            // Reactiva el botón
            processBtn.disabled = false;
            processBtn.textContent = 'Process Files';
        }
    });

    // --- LÓGICA DE DRAG & DROP ---

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    // --- FUNCIONES AUXILIARES ---

    function handleFiles(files) {
        console.log('--- handleFiles called ---');
        console.log('Initial loadedFiles:', JSON.parse(JSON.stringify(loadedFiles)));

        const newFiles = Array.from(files).map(file => {
            console.log('Processing file:', file.name, 'path:', file.path); // file.path might be undefined
            return { name: file.name, path: file.path, type: 'uploaded' };
        });
        console.log('New files mapped:', JSON.parse(JSON.stringify(newFiles)));

        const uniqueNewFiles = newFiles.filter(nf => {
            return !loadedFiles.some(lf => {
                // Check for duplicates
                if (lf.type === 'uploaded' && nf.type === 'uploaded') {
                    // If paths are available and match, it's a duplicate
                    if (nf.path && lf.path && nf.path === lf.path) {
                        // console.log(`Duplicate based on path: new ${nf.name} (${nf.path}) vs loaded ${lf.name} (${lf.path})`);
                        return true;
                    }
                    // If paths are undefined for both, check by name
                    if (nf.path === undefined && lf.path === undefined && nf.name === lf.name) {
                        // console.log(`Duplicate based on name (undefined paths): new ${nf.name} vs loaded ${lf.name}`);
                        return true;
                    }
                    // If one path is defined and the other isn't, they are different files for this check,
                    // unless we want to be stricter and say if a named file is already there, don't add.
                    // For now, this logic prioritizes path if available, otherwise name if paths are consistently undefined.
                }
                return false; // Not a duplicate based on this logic
            });
        });
        console.log('Unique new files to add:', JSON.parse(JSON.stringify(uniqueNewFiles)));

        loadedFiles = loadedFiles.concat(uniqueNewFiles);
        console.log('Updated loadedFiles:', JSON.parse(JSON.stringify(loadedFiles)));
        
        updateFileListUI();
        console.log('--- handleFiles finished ---');
    }

    function removeFileAtIndex(index) {
        if (index > -1 && index < loadedFiles.length) {
            loadedFiles.splice(index, 1); // Remove 1 element at the given index
            console.log('Updated loadedFiles after remove:', JSON.parse(JSON.stringify(loadedFiles)));
            updateFileListUI();
        }
    }

    function updateFileListUI() {
        fileList.innerHTML = ''; // Clear existing list items

        if (loadedFiles.length > 0) {
            fileListContainer.classList.remove('hidden');
            processBtn.disabled = false;

            loadedFiles.forEach((file, index) => {
                const li = document.createElement('li');
                
                const fileNameSpan = document.createElement('span');
                fileNameSpan.textContent = file.name;
                li.appendChild(fileNameSpan);

                const removeBtn = document.createElement('button');
                removeBtn.textContent = 'Remove';
                // Add classes for styling - you can create a specific class or reuse existing ones
                removeBtn.classList.add('btn', 'btn-remove-file'); // Added 'btn-remove-file' for specific styling

                removeBtn.addEventListener('click', (event) => {
                    event.stopPropagation(); // Prevent potential event bubbling
                    removeFileAtIndex(index);
                });

                li.appendChild(removeBtn);
                fileList.appendChild(li);
            });
        } else {
            fileListContainer.classList.add('hidden');
            processBtn.disabled = true;
        }
    }
});