function initializePredictions() {
    console.log("Initializing predictions view...");

    // --- Selección de Elementos del DOM ---
    const teams = [
        "Alaves", "Almeria", "Ath Bilbao", "Ath Madrid", "Barcelona", "Betis", "Cadiz",
        "Celta", "Eibar", "Elche", "Espanol", "Getafe", "Girona", "Granada", "Huesca",
        "Las Palmas", "Leganes", "Levante", "Mallorca", "Osasuna", "Real Madrid", "Sevilla",
        "Sociedad", "Valencia", "Valladolid", "Vallecano", "Villarreal"
    ];

    const homeSelect = document.getElementById('home-team-select');
    const awaySelect = document.getElementById('away-team-select');
    const homeCard = document.getElementById('home-team-card');
    const awayCard = document.getElementById('away-team-card');
    
    // --- Referencias para los controles y resultados de la predicción ---
    const dateInput = document.getElementById('match-date-input');
    const predictBtn = document.querySelector('.predict-button');
    const homePredictionResult = document.getElementById('home-prediction-result');
    const awayPredictionResult = document.getElementById('away-prediction-result');
    const homeActualResult = document.getElementById('home-actual-result');
    const awayActualResult = document.getElementById('away-actual-result');

    if (!homeSelect || !awaySelect || !predictBtn || !dateInput) {
        console.error("Prediction view elements not found. Aborting initialization.");
        return;
    }

    // --- Lógica de Selección de Equipos (sin cambios) ---
    teams.forEach(team => {
        homeSelect.add(new Option(team, team));
        awaySelect.add(new Option(team, team));
    });

    function updateTeamCard(selectElement, cardElement) {
        const selectedTeam = selectElement.value;
        const imageName = selectedTeam ? selectedTeam.toLowerCase().replace(/ /g, '_') : '';
        const imageUrl = imageName ? `./img/${imageName}.webp` : '';
        cardElement.style.backgroundImage = imageUrl ? `url('${imageUrl}')` : 'none';
        cardElement.classList.toggle('has-image', !!selectedTeam);
    }

    homeSelect.addEventListener('change', () => updateTeamCard(homeSelect, homeCard));
    awaySelect.addEventListener('change', () => updateTeamCard(awaySelect, awayCard));

    // --- LÓGICA DEL BOTÓN DE PREDICCIÓN ---
    predictBtn.addEventListener('click', async () => {
        const homeTeam = homeSelect.value;
        const awayTeam = awaySelect.value;
        const matchDate = dateInput.value; // Formato: YYYY-MM-DD

        if (!homeTeam || !awayTeam || !matchDate) {
            alert('Please select both teams and a match date.');
            return;
        }

        // Convertir la fecha de YYYY-MM-DD a DD/MM/YY para la API
        const [year, month, day] = matchDate.split('-');
        const formattedDate = `${day}/${month}/${year.slice(-2)}`;

        // Feedback para el usuario
        predictBtn.disabled = true;
        predictBtn.textContent = 'Predicting...';
        homePredictionResult.textContent = '...';
        awayPredictionResult.textContent = '...';
        homeActualResult.textContent = '...';
        awayActualResult.textContent = '...';
        
        // Hide comparison table while loading
        document.getElementById('prediction-comparison-section').style.display = 'none';

        try {
            const result = await pywebview.api.get_prediction(homeTeam, awayTeam, formattedDate);
            
            if (result.error) {
                alert(`Error: ${result.error}`);
                homePredictionResult.textContent = '-';
                awayPredictionResult.textContent = '-';
                homeActualResult.textContent = '-';
                awayActualResult.textContent = '-';
            } else {
                // Update prediction results
                homePredictionResult.textContent = result.predicted_home_goals.toFixed(2);
                awayPredictionResult.textContent = result.predicted_away_goals.toFixed(2);

                // Update actual results (check if they exist)
                homeActualResult.textContent = result.actual_home_goals !== undefined ? result.actual_home_goals : '-';
                awayActualResult.textContent = result.actual_away_goals !== undefined ? result.actual_away_goals : '-';
                
                // Update comparison table
                updatePredictionComparisonTable(result);
            }
        } catch (e) {
            alert(`An API error occurred: ${e.message}`);
        } finally {
            // Restore button
            predictBtn.disabled = false;
            predictBtn.textContent = 'Predict Goals';
        }
    });

    // NEW: Add function to update the comparison table
    function updatePredictionComparisonTable(result) {
        // Get prediction values
        const homeGoals = result.predicted_home_goals;
        const awayGoals = result.predicted_away_goals;
        
        // Get actual values (may be undefined)
        const actualHomeGoals = result.actual_home_goals;
        const actualAwayGoals = result.actual_away_goals;
        const hasActualResults = actualHomeGoals !== undefined && actualAwayGoals !== undefined;
        
        // Calculate rounded values using the specified rule
        const roundedHomeGoals = Math.floor(homeGoals + 0.5);
        const roundedAwayGoals = Math.floor(awayGoals + 0.5);
        
        // Determine match results for rounded values
        let roundedResult = '';
        if (roundedHomeGoals > roundedAwayGoals) {
            roundedResult = 'home win';
        } else if (roundedHomeGoals < roundedAwayGoals) {
            roundedResult = 'away win';
        } else {
            roundedResult = 'draw';
        }
        
        // Determine match results for non-rounded values
        let noroundResult = '';
        if (homeGoals > awayGoals) {
            noroundResult = 'home win';
        } else if (homeGoals < awayGoals) {
            noroundResult = 'away win';
        } else {
            noroundResult = 'draw';
        }
        
        // Update rounded results row
        document.getElementById('rounded-home').textContent = roundedHomeGoals;
        document.getElementById('rounded-away').textContent = roundedAwayGoals;
        
        const roundedResultCell = document.getElementById('rounded-result');
        roundedResultCell.textContent = roundedResult;
        roundedResultCell.className = getResultClass(roundedResult);
        
        // Update non-rounded results row
        document.getElementById('noround-home').textContent = homeGoals.toFixed(2);
        document.getElementById('noround-away').textContent = awayGoals.toFixed(2);
        
        const noroundResultCell = document.getElementById('noround-result');
        noroundResultCell.textContent = noroundResult;
        noroundResultCell.className = getResultClass(noroundResult);
        
        // Update actual results row
        if (hasActualResults) {
            // Determine actual match result
            let actualResult = '';
            if (actualHomeGoals > actualAwayGoals) {
                actualResult = 'home win';
            } else if (actualHomeGoals < actualAwayGoals) {
                actualResult = 'away win';
            } else {
                actualResult = 'draw';
            }
            
            document.getElementById('actual-home').textContent = actualHomeGoals;
            document.getElementById('actual-away').textContent = actualAwayGoals;
            
            const actualResultCell = document.getElementById('actual-result');
            actualResultCell.textContent = actualResult;
            actualResultCell.className = getResultClass(actualResult);
        } else {
            // No actual results available
            document.getElementById('actual-home').textContent = '-';
            document.getElementById('actual-away').textContent = '-';
            
            const actualResultCell = document.getElementById('actual-result');
            actualResultCell.textContent = '-';
            actualResultCell.className = '';
        }
        
        // Show the comparison table section
        document.getElementById('prediction-comparison-section').style.display = 'block';
    }

    // Helper function to get CSS class based on result
    function getResultClass(result) {
        if (result === 'home win') return 'result-home-win';
        if (result === 'away win') return 'result-away-win';
        if (result === 'draw') return 'result-draw';
        return '';
    }

    // --- CÓDIGO PARA LA TABLA DE DATOS DE PRUEBA (sin cambios) ---
    const tableHead = document.querySelector('#predictions-data-table thead');
    const tableBody = document.getElementById('test-matchups-body');
    const loadingMessage = document.getElementById('predictions-loading-message');

    if (!tableHead || !tableBody || !loadingMessage) {
        console.error("Prediction table elements not found. Aborting table initialization.");
        return;
    }

    function renderTable(dataToRender) {
        // Comprueba si la respuesta de la API es un objeto de error
        if (typeof dataToRender === 'string') {
            try { dataToRender = JSON.parse(dataToRender); } catch (e) { /* no es json */ }
        }
        if (dataToRender.error) {
            loadingMessage.textContent = dataToRender.error;
            return;
        }
        if (!dataToRender || dataToRender.length === 0) {
            loadingMessage.textContent = 'No test data available.';
            return;
        }

        // Renderiza las cabeceras dinámicamente
        const headers = Object.keys(dataToRender[0]);
        tableHead.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;

        // Renderiza las filas
        tableBody.innerHTML = dataToRender.map(row => 
            `<tr>${headers.map(h => `<td>${row[h] === null ? 'null' : row[h]}</td>`).join('')}</tr>`
        ).join('');

        loadingMessage.style.display = 'none';
    }

    // Hacemos las funciones globales para que Python pueda llamarlas
    window.renderPredictionsTable = (data) => {
        console.log("Test data received from Python push.");
        renderTable(data);
    };

    window.renderPredictionsError = (errorMessage) => {
        console.error("Error pushed from Python:", errorMessage);
        loadingMessage.textContent = errorMessage;
        loadingMessage.style.display = 'block';
    };

    // Solicitamos los datos de prueba a Python
    try {
        loadingMessage.style.display = 'block';
        pywebview.api.get_test_data();
    } catch (e) {
        renderPredictionsError(`Failed to call API: ${e.message}`);
    }
}