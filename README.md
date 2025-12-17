# PatientArrivalCounter
Outil pour analyser les arrivées de patients.

## Usage
```bash
python -m src.main analyze --csv data/sample_data.csv --out data/output
or with gui
python -m src.gui
```

Résultats générés dans `data/output/` :
- hourly_counts.csv
- daily_counts.csv
- hourly.png, daily.png
- summary.json
