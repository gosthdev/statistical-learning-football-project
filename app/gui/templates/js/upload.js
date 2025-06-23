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
    fileInput.addEventListener('change', async () => { // Make async
        if (fileInput.files.length > 0) {
            await handleFiles(fileInput.files); // Await file handling
            fileInput.value = ''; // Reset file input
        }
    });

    // Cargar datasets por defecto
    loadDefaultBtn.addEventListener('click', async () => {
        try {
            const defaultFileNames = await pywebview.api.load_default_datasets();
            if (defaultFileNames && defaultFileNames.length > 0) {
                const newDefaultFiles = defaultFileNames
                    .map(fileName => ({ name: fileName, content: null, type: 'default' })) // content is null for default
                    .filter(df => !loadedFiles.some(lf => lf.type === 'default' && lf.name === df.name));
                
                loadedFiles = loadedFiles.concat(newDefaultFiles);
                updateFileListUI();
            } else {
                alert('No default datasets found or an error occurred.');
            }
        } catch (error) {
            console.error('Error loading default datasets:', error);
        }
    });
    
    // Iniciar procesamiento de archivos
    processBtn.addEventListener('click', () => { // No longer async
        if (loadedFiles.length === 0) {
            return;
        }
        processBtn.disabled = true;
        processBtn.textContent = 'Processing...';
        
        // KEY CHANGE: Use .then() for a non-blocking call.
        // This fires the Python function and immediately continues, avoiding the race condition.
        // Python will handle navigation on success. We only care about the result if it's an error.
        pywebview.api.process_files(loadedFiles).then(result => {
            // This block will only run if Python returns a value, which it now only does on error.
            if (result && result.status === 'error') {
                console.error("Processing failed:", result.message);
                alert(`Processing failed: ${result.message}`);
                processBtn.disabled = false;
                processBtn.textContent = 'Process Files';
            }
        }).catch(error => {
            // This catches fundamental errors in the API call itself.
            console.error('Error calling process_files API:', error);
            alert('A critical error occurred while trying to process the files.');
            processBtn.disabled = false;
            processBtn.textContent = 'Process Files';
        });
    });

    // --- LÓGICA DE DRAG & DROP ---

    dropZone.addEventListener('dragover', (event) => {
        event.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', async (event) => { // Make async
        event.preventDefault();
        dropZone.classList.remove('dragover');
        if (event.dataTransfer.files.length > 0) {
            await handleFiles(event.dataTransfer.files); // Await file handling
        }
    });


    // --- FUNCIONES AUXILIARES ---

    // Function to read a single file's content
    function readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(reader.error);
            reader.readAsText(file); // Assuming CSVs are text files
        });
    }

    async function handleFiles(files) { // Make async
        console.log('--- handleFiles called (content reading mode) ---');
        
        const newFileObjectsPromises = Array.from(files).map(async (file) => {
            try {
                const content = await readFileAsText(file);
                console.log(`Read content for: ${file.name} (size: ${content.length})`);
                return { name: file.name, content: content, type: 'uploaded' };
            } catch (error) {
                console.error(`Error reading file ${file.name}:`, error);
                alert(`Could not read file: ${file.name}`);
                return null; // Or handle error appropriately
            }
        });

        const newFileObjects = (await Promise.all(newFileObjectsPromises)).filter(f => f !== null);

        // Filter out already added files based on name for uploaded files
        // (since content comparison would be too heavy and path is not used)
        const uniqueNewFiles = newFileObjects.filter(nf => 
            !loadedFiles.some(lf => lf.type === 'uploaded' && lf.name === nf.name)
        );
        
        loadedFiles = loadedFiles.concat(uniqueNewFiles);
        updateFileListUI();
        console.log('--- handleFiles finished (content reading mode) ---');
    }

    function removeFileAtIndex(index) {
        if (index > -1 && index < loadedFiles.length) {
            loadedFiles.splice(index, 1);
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