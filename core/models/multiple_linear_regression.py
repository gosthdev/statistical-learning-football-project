from datetime import datetime
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
import joblib
from ..config import FEATURES_COLUMNS, N_SPLITS, HOME_TARGET, AWAY_TARGET
from .base_model import BaseModel

class MultipleLinearRegressionModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.df = None

        self.X = None
        self.y_home = None
        self.y_away = None
        # Train
        self.X_train_final = None
        self.y_home_train_final = None
        self.y_away_train_final = None

        # Test
        self.df_test = None
        # self.X_test_final = None
        # self.y_home_test_final = None
        # self.y_away_test_final = None

        self.test_index = None
        # idk this variable
        # self.info_test_final = None

        # paths
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.models_dir = os.path.join(project_root, 'data', 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # models 
        self.model_home = None
        self.model_away = None

        # models paths
        date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.home_model_path = os.path.join(self.models_dir, f'home_model_{date}.pkl')
        self.away_model_path = os.path.join(self.models_dir, f'away_model_{date}.pkl')

        self.test_path = os.path.join(project_root, 'data', 'test', 'multiple_linear_regression_test.csv')

    def train(self):
        self.df = self.df.dropna()
        self.X = self.df[FEATURES_COLUMNS]
        self.y_home = self.df[HOME_TARGET]
        self.y_away = self.df[AWAY_TARGET]

        tscv_final = TimeSeriesSplit(n_splits=N_SPLITS)
        # Get the last train/test split directly
        train_index, self.test_index = list(tscv_final.split(self.X))[-1]
        
        # Training
        self.X_train_final = self.X.iloc[train_index]
        self.y_home_train_final = self.y_home.iloc[train_index]
        self.y_away_train_final = self.y_away.iloc[train_index]
        # Testing
        # self.X_test_final = self.X.iloc[test_index]
        # self.y_home_test_final = self.y_home.iloc[test_index]
        # self.y_away_test_final = self.y_away.iloc[test_index]

        # self.info_test_final = self.df.iloc[test_index]
        self.model_home = LinearRegression().fit(self.X_train_final, self.y_home_train_final)
        self.model_away = LinearRegression().fit(self.X_train_final, self.y_away_train_final)


    def save(self):
        print(f"Saving models to {self.home_model_path} and {self.away_model_path}")
        if self.model_home:
            joblib.dump(self.model_home, self.home_model_path)
        if self.model_away:
            joblib.dump(self.model_away, self.away_model_path)
        os.mkdir(os.path.dirname(self.test_path), exist_ok=True)
        self.df.iloc[self.test_index].to_csv(self.test_path, index=False)
        print("Models saved successfully.")
        print(f"Test data saved to {self.test_path}")
    
    def load_models(self):
        print(f"Searching for latest models in {self.models_dir}")
        
        try:
            home_models = [f for f in os.listdir(self.models_dir) if f.startswith('home_model_') and f.endswith('.pkl')]
            away_models = [f for f in os.listdir(self.models_dir) if f.startswith('away_model_') and f.endswith('.pkl')]

            if not home_models or not away_models:
                print("Error: No model files found in the directory.")
                self.model_home = None
                self.model_away = None
                return

            latest_home_model_file = max(home_models, key=lambda f: os.path.getmtime(os.path.join(self.models_dir, f)))
            latest_away_model_file = max(away_models, key=lambda f: os.path.getmtime(os.path.join(self.models_dir, f)))

            self.home_model_path = os.path.join(self.models_dir, latest_home_model_file)
            self.away_model_path = os.path.join(self.models_dir, latest_away_model_file)

            print(f"Loading models from {self.home_model_path} and {self.away_model_path}")
            self.model_home = joblib.load(self.home_model_path)
            self.model_away = joblib.load(self.away_model_path)
            print("Models loaded successfully.")
        except Exception as e:
            print(f"An error occurred while loading models: {e}")
            self.model_home = None
            self.model_away = None
    
    def load_test_data(self):
        df_test = pd.read_csv(self.test_path)
        df_test['Date'] = pd.to_datetime(df_test['Date'])
        self.df_test = df_test
        print(f"Test data loaded successfully from {self.test_path}. Number of records: {len(self.df_test)}")

    def predict(self, home_team: str, away_team: str, date: str):
        """
        Returns:
            tuple: (pred_h, pred_a, real_h, real_a) | (None, None, None, None)
        """
        # --- 1. Validaciones iniciales ---
        if self.model_home is None or self.model_away is None:
            print("Error: Los modelos no están cargados. Ejecuta train_model() primero.")
            return None, None, None, None
        
        if self.df_test is None:
            print("Error: El dataset de prueba (df_test) no está cargado. Ejecuta load_test_data() primero.")
            return None, None, None, None

        # --- 2. Encontrar el partido específico en el dataset de prueba ---
        try:
            match_date = pd.to_datetime(date, format='%d/%m/%y')
            
            # 'HomeTeam', 'AwayTeam', y 'Date' son columnas estructurales básicas.
            match_record = self.df_test[
                (self.df_test['HomeTeam'] == home_team) &
                (self.df_test['AwayTeam'] == away_team) &
                (self.df_test['Date'] == match_date)
            ]

            if match_record.empty:
                print(f"Error: No se encontró el partido {home_team} vs {away_team} en la fecha {date} en el dataset de prueba.")
                return None, None, None, None

        except Exception as e:
            print(f"Error al buscar el partido en el dataset de prueba: {e}")
            return None, None, None, None

        # --- 3. Preparar los datos para la predicción ---
        # Se asume que self.feature_columns se ha poblado usando FEATURES_COLUMNS de config.py
        input_data = match_record[FEATURES_COLUMNS]

        # --- 4. Realizar la predicción ---
        pred_h = self.model_home.predict(input_data)[0]
        pred_a = self.model_away.predict(input_data)[0]

        # --- 5. Obtener el resultado real del registro encontrado ---
        # ¡CAMBIADO! Usamos las constantes importadas para seguridad y consistencia.
        real_h = match_record[HOME_TARGET].iloc[0]
        real_a = match_record[AWAY_TARGET].iloc[0]

        print(f"Predicción para {home_team} vs {away_team}: {pred_h:.2f} - {pred_a:.2f}")
        print(f"Resultado real: {real_h} - {real_a}")

        # --- 6. Devolver la tupla completa ---
        return pred_h, pred_a, real_h, real_a

