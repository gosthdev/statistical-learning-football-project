def get_historical(row, matchs, n_matchs): 
    current_date = row['Date']
    home_team = row['HomeTeam']
    away_team = row['AwayTeam']

    # Filtrar partidos estrictamente anteriores a la fecha actual
    past_matches = matchs[matchs['Date'] < current_date]

    # --- Métricas para el Equipo Local ---
    # Filtrar los últimos N partidos donde jugó el equipo local (ya sea de local o visitante)
    local_history = past_matches[
        (past_matches['HomeTeam'] == home_team) | (past_matches['AwayTeam'] == home_team)
    ].tail(n_matchs)

    away_history = past_matches[ (past_matches['HomeTeam'] == away_team) | (past_matches['AwayTeam'] == away_team)
    ].tail(n_matchs)

    return (local_history, away_history)