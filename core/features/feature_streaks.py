# core/features/streaks.py
import pandas as pd

from .base_calculator import FeatureCalculator
from .utils import get_historical
from ..config import STREAK_COLUMNS
class StreaksCalculator(FeatureCalculator):
    def calculate(self, processed_df: pd.DataFrame, n_matches: int) -> pd.DataFrame:
        print("Calculating winning streaks...")
        
        # Apply function to each row to calculate winning streaks
        results = processed_df.apply(
            self._calculate_streaks_wrapper,
            axis=1,
            args=(processed_df, n_matches)
        )
        results.columns = STREAK_COLUMNS
        
        # Merge the results with the current processed DataFrame
        return pd.concat([processed_df, results], axis=1)

    def _calculate_streaks_wrapper(self, row, all_matches, n_matches): # 
        equipo_local = row['HomeTeam']
        equipo_visitante = row['AwayTeam']
        # Get historical matches for the local and away teams before the current match Date
        local_history, away_history = get_historical(row, all_matches, n_matches)

        l_win_streak = self._calculate_winning_streak(local_history, equipo_local)

        v_win_streak = self._calculate_winning_streak(away_history, equipo_visitante)

        return pd.Series([l_win_streak, v_win_streak])

    def _calculate_winning_streak(self, historial, team_name):
        # If the team has no matches in the history, return 0
        if historial.empty:
            return 0

        current_streak = 0

        for _, match in historial.iloc[::-1].iterrows():

            # Check if the match is a win for the team
            won_match = False
            if (match['HomeTeam'] == team_name and match['FTR'] == 'H') or \
            (match['AwayTeam'] == team_name and match['FTR'] == 'A'):
                won_match = True

            if won_match:
                current_streak += 1
            else:
                # If the team did not win, break the streak
                break

        return current_streak