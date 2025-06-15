from abc import ABC, abstractmethod
import pandas as pd

class FeatureCalculator(ABC):
    """
    Clase base abstracta para todos los calculadores de características.
    Cada calculador debe implementar el método 'calculate'.
    """
    @abstractmethod
    def calculate(self, full_df: pd.DataFrame, processed_df: pd.DataFrame, n_matches: int) -> pd.DataFrame:
        """
        Calcula una nueva característica y la añade al dataframe procesado.

        Args:
            full_df (pd.DataFrame): El dataframe completo con todos los datos originales.
            processed_df (pd.DataFrame): El dataframe que se está construyendo con las nuevas features.
            n_matches (int): El número de partidos previos a considerar.

        Returns:
            pd.DataFrame: El dataframe procesado con la nueva característica añadida.
        """
        pass