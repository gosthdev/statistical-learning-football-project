import pandas as pd
from .base_calculator import FeatureCalculator
from .utils import get_historical
from config import EFFICIENCY_COLUMNS

class EfficiencyCalculator(FeatureCalculator):
    def calculate(self, processed_df: pd.DataFrame, n_matches: int) -> pd.DataFrame:
        print("Process efficiency goals/shots...")
        results = processed_df.apply(
            self._calculate_efficiency,
            axis=1,
            args=(processed_df, n_matches)
        )
        results.columns = EFFICIENCY_COLUMNS
        return pd.concat([processed_df, results], axis=1)

    def _calculate_efficiency(self, row, all_matches, n_matches):
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        local_history, away_history = get_historical(row, all_matches, n_matches)

        # home efficiency
        l_eff = 0.0
        if not local_history.empty:
            goles_local = local_history.apply(lambda x: x['FTHG'] if x['HomeTeam'] == home_team else x['FTAG'], axis=1).sum()
            remates_local = local_history.apply(lambda x: x['HS'] if x['HomeTeam'] == home_team else x['AS'], axis=1).sum()
            if remates_local > 0:
                l_eff = goles_local / remates_local

        # away efficiency
        v_eff = 0.0
        if not away_history.empty:
            goles_visitante = away_history.apply(lambda x: x['FTHG'] if x['HomeTeam'] == away_team else x['FTAG'], axis=1).sum()
            remates_visitante = away_history.apply(lambda x: x['HS'] if x['HomeTeam'] == away_team else x['AS'], axis=1).sum()
            if remates_visitante > 0:
                v_eff = goles_visitante / remates_visitante

        return pd.Series([l_eff, v_eff])