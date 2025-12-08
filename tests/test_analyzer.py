from src.analyzer import ArrivalAnalyzer
import pandas as pd

def test_hourly_daily_counts():
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(['2024-01-01 10:21:00','2024-01-01 10:40:00','2024-01-02 11:00:00']),
        'patient_id': [1,2,3]
    })
    an = ArrivalAnalyzer(df)
    h = an.hourly_counts()
    d = an.daily_counts()
    assert h['count'].sum() == 3
    assert d['count'].sum() == 3
    bh, bhc = an.busiest_hour()
    bd, bdc = an.busiest_day()
    assert isinstance(bhc, int)
    assert isinstance(bdc, int)
