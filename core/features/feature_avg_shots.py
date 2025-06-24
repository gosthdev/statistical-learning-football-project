import pandas as pd
from .base_calculator import FeatureCalculator
from .utils import get_historical
from ..config import AVG_SHOTS_COLUMNS
class AvgShotsCalculator(FeatureCalculator):
    def calculate(self, processed_df: pd.DataFrame, n_matches: int) -> pd.DataFrame:
        print("Calculating average goals...")
        
        results = processed_df.apply(
            self._calculate_avg_previous_shots,
            axis=1,
            args=(processed_df, n_matches)
        )

        results.columns = AVG_SHOTS_COLUMNS
        return pd.concat([processed_df, results], axis=1)
    
    def _calculate_avg_previous_shots(self, row, all_matches, n_matches):
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        
        # Get historical matches for the local and away teams before the current match Date
        local_history, away_history = get_historical(row, all_matches, n_matches)
        
        if local_history.empty or away_history.empty:
            return pd.Series([None, None, None, None])  
        # Calculate goals in favor and against for home team
        h_shots_in_favor = local_history.apply(lambda x: x['HS'] if x['HomeTeam'] == home_team else x['AS'], axis=1)
        h_shots_against = local_history.apply(lambda x: x['AS'] if x['HomeTeam'] == home_team else x['HS'], axis=1)

        # Calculate goals in favor and against for away team
        a_shots_in_favor = away_history.apply(lambda x: x['HS'] if x['HomeTeam'] == away_team else x['AS'], axis=1)
        a_shots_against = away_history.apply(lambda x: x['AS'] if x['HomeTeam'] == away_team else x['HS'], axis=1)
        # Calculate average goals for home team
        h_avg_shots = h_shots_in_favor.mean()
        h_avg_shots_against = h_shots_against.mean()

        # Calculate average goals for away team
        a_avg_shots = a_shots_in_favor.mean()
        a_avg_shots_against = a_shots_against.mean()

        return pd.Series([h_avg_shots, h_avg_shots_against, a_avg_shots, a_avg_shots_against])