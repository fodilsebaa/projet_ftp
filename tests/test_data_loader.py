from src.data_loader import DataLoader
import pandas as pd

def test_load_and_validate(tmp_path):
    p = tmp_path / 's.csv'
    df = pd.DataFrame({'timestamp':['2024-01-01 10:00:00'],'patient_id':[1]})
    df.to_csv(p, index=False)
    dl = DataLoader(p)
    df2 = dl.load_csv()
    assert 'timestamp' in df2.columns
    assert dl.validate(df2) is True
    df3 = dl.parse_dates(df2)
    assert df3['timestamp'].dtype.kind in ('M',)
