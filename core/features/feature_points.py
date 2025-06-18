import pandas as pd
from .base_calculator import FeatureCalculator
from .utils import get_historical
from ..config import AVG_POINTS_COLUMNS
class AvgPointsCalculator(FeatureCalculator):
    def calculate(self, processed_df: pd.DataFrame, n_matches: int) -> pd.DataFrame:
        print("Calculating average points...")
        
        results = processed_df.apply(
            self._calculate_previous_points,
            axis=1,
            args=(processed_df, n_matches)
        )

        results.columns = AVG_POINTS_COLUMNS
        return pd.concat([processed_df, results], axis=1)

    def _calculate_previous_points(self, row, all_matches, n_matches):
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        
        # Get historical matches for the local and away teams before the current match Date
        local_history, away_history = get_historical(row, all_matches, n_matches)
        
        if local_history.empty or away_history.empty:
            return pd.Series([None, None]) 
        
        h_points = self._calculate_team_score(local_history, home_team)
        a_points = self._calculate_team_score(away_history, away_team)
        
        return pd.Series([h_points, a_points])


    
    def _calculate_team_score(self, history, team):
        if history.empty:
            return 0 # If there are no historical matches, 0 points

        puntos = 0
        for _, match in history.iterrows():
            if match['HomeTeam'] == team: # The team played at home in this past match
                if match['FTR'] == 'H':
                    puntos += 3
                elif match['FTR'] == 'D':
                    puntos += 1
                # If FTR == 'A', no points are added
            elif match['AwayTeam'] == team: # The team played away
                if match['FTR'] == 'A':
                    puntos += 3
                elif match['FTR'] == 'D':
                    puntos += 1
                # If FTR == 'H', no points are added
        return puntos