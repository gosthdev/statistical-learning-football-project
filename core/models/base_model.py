from abc import ABC, abstractmethod
import pandas as pd

class BaseModel(ABC):
    """
    Clase base abstracta para todas las implementaciones de modelos.
    """
    def __init__(self):
        self.model_home = None
        self.model_away = None

    @abstractmethod
    def train(self, data: pd.DataFrame):
        """
        Entrena los modelos para goles de local y visitante.
        Debe devolver un diccionario con las métricas de evaluación.
        """
        pass

    @abstractmethod
    def save(self, home_path: str, away_path: str):
        """
        Guarda los modelos entrenados en disco.
        """
        pass