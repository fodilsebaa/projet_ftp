import json
from pathlib import Path

def generate_summary(out_json_path, total_patients, busiest_hour, busiest_hour_count, busiest_day, busiest_day_count, average_daily):
    """
    cree un résumé des analyses et l'enregistre sous forme de fichier JSON.
    """
    summary = {
        "total_patients": total_patients,
        "busiest_hour": str(busiest_hour),
        "busiest_hour_count": int(busiest_hour_count),
        "busiest_day": str(busiest_day),
        "busiest_day_count": int(busiest_day_count),
        "average_daily": float(average_daily)
    }
    Path(out_json_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    return summary
