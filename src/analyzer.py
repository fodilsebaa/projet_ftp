import pandas as pd

class ArrivalAnalyzer:
    """
    Effectue une analyse statistique des données relatives à l'arrivée des patients.
    """
    def __init__(self, df, timestamp_col='timestamp', id_col='patient_id'):
        """Initialisez l'analyseur avec un DataFrame.
        Arguments :
        df (pandas.DataFrame) : DataFrame contenant les arrivées des patients."""
        
        self.df = df.copy()
        self.ts = timestamp_col
        self.id = id_col

    def hourly_counts(self):
        """
        Calcule le nombre d'arrivées de patients par heure.

        Retourne :
        pandas.DataFrame : nombre d'arrivées par heure.
        """
        df = self.df.copy()
        df['hour'] = df[self.ts].dt.floor('H')
        res = df.groupby('hour')[self.id].nunique().reset_index().rename(columns={'hour':'timestamp','patient_id':'count'})
        return res

    def daily_counts(self):
        """
        Calcule le nombre d'arrivées de patients par Jour.

        Retourne :
        pandas.DataFrame : nombre d'arrivées par jour.
        """
        df = self.df.copy()
        df['day'] = df[self.ts].dt.date
        res = df.groupby('day')[self.id].nunique().reset_index().rename(columns={'day':'date','patient_id':'count'})
        return res

    def busiest_hour(self):
        """
        Calcule l'heure la plus fréquentée.

        Retourne :
        tuple : (heure la plus fréquentée, nombre d'arrivées)
        """
        h = self.hourly_counts()
        row = h.sort_values('count', ascending=False).iloc[0]
        return row['timestamp'], int(row['count'])

    def busiest_day(self):
        """
        calcule le jour le plus fréquenté.
        
        retourne :
        tuple : (jour le plus fréquenté, nombre d'arrivées)
        """
        d = self.daily_counts()
        row = d.sort_values('count', ascending=False).iloc[0]
        return str(row['date']), int(row['count'])

    def total_patients(self):
        return int(self.df[self.id].nunique())

    def average_daily(self):
        d = self.daily_counts()
        return float(d['count'].mean())
