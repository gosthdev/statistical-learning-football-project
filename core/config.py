HOME_TARGET = 'FTHG'
AWAY_TARGET = 'FTAG'
N = 5
ESSENTIAL_COLUMNS = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS', 'HC', 'AC']
STREAK_COLUMNS = ['H_WinStreak', 'A_WinStreak']
AVG_GOALS_COLUMNS = ['H_AvgGoals', 'H_AvgGoalsAgainst', 'A_AvgGoals', 'A_AvgGoalsAgainst']
AVG_SHOTS_COLUMNS = ['H_AvgShots', 'H_AvgShotsAgainst', 'A_AvgShots', 'A_AvgShotsAgainst']
AVG_CORNERS_COLUMNS = ['H_AvgCorners', 'H_AvgCornersAgainst', 'A_AvgCorners', 'A_AvgCornersAgainst']
AVG_POINTS_COLUMNS = ['H_Points', 'A_Points']
EFFICIENCY_COLUMNS = ['H_Eff_GoalsPerShot', 'A_Eff_GoalsPerShot']
FEATURES_COLUMNS = STREAK_COLUMNS + AVG_GOALS_COLUMNS + AVG_SHOTS_COLUMNS + AVG_CORNERS_COLUMNS + AVG_POINTS_COLUMNS + EFFICIENCY_COLUMNS

N_SPLITS = 10