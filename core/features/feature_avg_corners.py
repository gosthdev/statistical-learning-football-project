import pandas as pd
from .base_calculator import FeatureCalculator
from .utils import get_historical
from config import AVG_CORNERS_COLUMNS
class AvgCornersCalculator(FeatureCalculator):
    def calculate(self, processed_df: pd.DataFrame, n_matches: int) -> pd.DataFrame:
        print("Calculating average corners...")
        
        results = processed_df.apply(
            self._calculate_avg_previous_corners,
            axis=1,
            args=(processed_df, n_matches)
        )

        results.columns = AVG_CORNERS_COLUMNS
        return pd.concat([processed_df, results], axis=1)

    def _calculate_avg_previous_corners(self, row, all_matches, n_matches):
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        
        # Get historical matches for the local and away teams before the current match Date
        local_history, away_history = get_historical(row, all_matches, n_matches)
        
        if local_history.empty or away_history.empty:
            return pd.Series([None, None, None, None])  
        # Calculate corners in favor and against for home team
        h_corners_in_favor = local_history.apply(lambda x: x['HC'] if x['HomeTeam'] == home_team else x['AC'], axis=1)
        h_corners_against = local_history.apply(lambda x: x['AC'] if x['HomeTeam'] == home_team else x['HC'], axis=1)

        # Calculate corners in favor and against for away team
        a_corners_in_favor = away_history.apply(lambda x: x['HC'] if x['HomeTeam'] == away_team else x['AC'], axis=1)
        a_corners_against = away_history.apply(lambda x: x['AC'] if x['HomeTeam'] == away_team else x['HC'], axis=1)
        # Calculate average corners for home team
        h_avg_corners = h_corners_in_favor.mean()
        h_avg_corners_against = h_corners_against.mean()

        # Calculate average corners for away team
        a_avg_corners = a_corners_in_favor.mean()
        a_avg_corners_against = a_corners_against.mean()

        return pd.Series([h_avg_corners, h_avg_corners_against, a_avg_corners, a_avg_corners_against])