import pandas as pd
from pathlib import Path

class DataLoader:
    def __init__(self, path):
        self.path = Path(path)

    def load_csv(self):
        """
        charger le fichier CSV dans un DataFrame
        """
        df = pd.read_csv(self.path)
        return df

    def validate(self, df, timestamp_col='timestamp', id_col='patient_id'):
        """
        valider que les colonnes nécessaires existent dans le DataFrame
        """
        if timestamp_col not in df.columns:
            raise ValueError(f"Missing column: {timestamp_col}")
        if id_col not in df.columns:
            raise ValueError(f"Missing column: {id_col}")
        return True

    def parse_dates(self, df, timestamp_col='timestamp'):
        """
        transformer la colonne de timestamp en objets datetime
        """
        df = df.copy()
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        return df
