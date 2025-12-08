import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def plot_hourly(hourly_df, out_path='docs/graphs/hourly.png'):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    hourly_df = hourly_df.copy()
    hourly_df['timestamp'] = pd.to_datetime(hourly_df['timestamp'])
    plt.figure(figsize=(10,4))
    plt.plot(hourly_df['timestamp'], hourly_df['count'], marker='o', linewidth=1)
    plt.xlabel('Hour')
    plt.ylabel('Patients')
    plt.title('Patients per Hour')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_daily(daily_df, out_path='docs/graphs/daily.png'):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    daily_df = daily_df.copy()
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    plt.figure(figsize=(10,4))
    plt.bar(daily_df['date'].dt.strftime('%Y-%m-%d'), daily_df['count'])
    plt.xlabel('Day')
    plt.ylabel('Patients')
    plt.title('Patients per Day')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
