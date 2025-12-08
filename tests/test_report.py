from src.report import generate_summary
import json, os
def test_generate_summary(tmp_path):
    p = tmp_path / 'out' / 'summary.json'
    summary = generate_summary(p, 10, '2024-01-01 10:00:00', 5, '2024-01-01', 8, 6.5)
    assert os.path.exists(p)
    assert summary['total_patients'] == 10
