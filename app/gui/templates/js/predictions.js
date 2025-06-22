function initializePredictions() {
    console.log("Initializing predictions view...");

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

    // Salir si los elementos no se encuentran (por si el script se ejecuta en otra vista)
    if (!homeSelect || !awaySelect) {
        console.error("Prediction view elements not found. Aborting initialization.");
        return;
    }

    // Populate dropdowns
    teams.forEach(team => {
        const optionHome = new Option(team, team);
        const optionAway = new Option(team, team);
        homeSelect.add(optionHome);
        awaySelect.add(optionAway);
    });

    function updateTeamCard(selectElement, cardElement) {
        const selectedTeam = selectElement.value;
        if (selectedTeam) {
            // Convert team name to filename format (lowercase, spaces to underscores)
            let imageName = selectedTeam.toLowerCase().replace(/ /g, '_');
            const imageUrl = `./img/${imageName}.webp`;

            cardElement.style.backgroundImage = `url('${imageUrl}')`;
            cardElement.classList.add('has-image');
        } else {
            cardElement.style.backgroundImage = 'none';
            cardElement.classList.remove('has-image');
        }
    }

    homeSelect.addEventListener('change', () => updateTeamCard(homeSelect, homeCard));
    awaySelect.addEventListener('change', () => updateTeamCard(awaySelect, awayCard));
}