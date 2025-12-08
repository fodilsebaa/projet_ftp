import pandas as pd

class ArrivalAnalyzer:
    def __init__(self, df, timestamp_col='timestamp', id_col='patient_id'):
        self.df = df.copy()
        self.ts = timestamp_col
        self.id = id_col

    def hourly_counts(self):
        df = self.df.copy()
        df['hour'] = df[self.ts].dt.floor('H')
        res = df.groupby('hour')[self.id].nunique().reset_index().rename(columns={'hour':'timestamp','patient_id':'count'})
        return res

    def daily_counts(self):
        df = self.df.copy()
        df['day'] = df[self.ts].dt.date
        res = df.groupby('day')[self.id].nunique().reset_index().rename(columns={'day':'date','patient_id':'count'})
        return res

    def busiest_hour(self):
        h = self.hourly_counts()
        row = h.sort_values('count', ascending=False).iloc[0]
        return row['timestamp'], int(row['count'])

    def busiest_day(self):
        d = self.daily_counts()
        row = d.sort_values('count', ascending=False).iloc[0]
        return str(row['date']), int(row['count'])

    def total_patients(self):
        return int(self.df[self.id].nunique())

    def average_daily(self):
        d = self.daily_counts()
        return float(d['count'].mean())
