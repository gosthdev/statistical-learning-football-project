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
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self.df = df.dropna()

        self.X = None
        self.y_home = None
        self.y_away = None
        # Train
        self.X_train_final = None
        self.y_home_train_final = None
        self.y_away_train_final = None

        # Test
        self.X_test_final = None
        self.y_home_test_final = None
        self.y_away_test_final = None

        # idk this variable
        self.info_test_final = None

        # paths
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.models_dir = os.path.join(project_root, 'data', 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.home_model_path = os.path.join(self.models_dir, f'home_model_{date}.pkl')
        self.away_model_path = os.path.join(self.models_dir, f'away_model_{date}.pkl')

    def train(self):
        self.X = self.df[FEATURES_COLUMNS]
        self.y_home = self.df[HOME_TARGET]
        self.y_away = self.df[AWAY_TARGET]

        tscv_final = TimeSeriesSplit(n_splits=N_SPLITS)
        # Get the last train/test split directly
        train_index, test_index = list(tscv_final.split(self.X))[-1]
        
        # Training
        self.X_train_final = self.X.iloc[train_index]
        self.y_home_train_final = self.y_home.iloc[train_index]
        self.y_away_train_final = self.y_away.iloc[train_index]
        # Testing
        self.X_test_final = self.X.iloc[test_index]
        self.y_home_test_final = self.y_home.iloc[test_index]
        self.y_away_test_final = self.y_away.iloc[test_index]

        self.info_test_final = self.df.iloc[test_index]
        self.model_home = LinearRegression().fit(self.X_train_final, self.y_home_train_final)
        self.model_away = LinearRegression().fit(self.X_train_final, self.y_away_train_final)


    def save(self):
        print(f"Saving models to {self.home_model_path} and {self.away_model_path}")
        if self.model_home:
            joblib.dump(self.model_home, self.home_model_path)
        if self.model_away:
            joblib.dump(self.model_away, self.away_model_path)
        print("Models saved successfully.")
    
    def load(self):
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