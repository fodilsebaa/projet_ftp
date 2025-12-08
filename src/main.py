import argparse
from pathlib import Path
from src.data_loader import DataLoader
from src.analyzer import ArrivalAnalyzer
from src.plotter import plot_hourly, plot_daily
from src.report import generate_summary

def main():
    parser = argparse.ArgumentParser(prog='PatientArrivalCounter', description='Analyse des arrivées des patients (sans IA)')
    parser.add_argument('command', choices=['analyze'], help='Commande (analyze)')
    parser.add_argument('--csv', required=True, help='Chemin vers le CSV d\'entrée')
    parser.add_argument('--out', default='data/output', help='Dossier de sortie pour résultats')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    dl = DataLoader(csv_path)
    df = dl.load_csv()
    dl.validate(df)
    df = dl.parse_dates(df)

    analyzer = ArrivalAnalyzer(df)
    hourly = analyzer.hourly_counts()
    daily = analyzer.daily_counts()

    # save CSVs
    hourly.to_csv(out_dir / 'hourly_counts.csv', index=False)
    daily.to_csv(out_dir / 'daily_counts.csv', index=False)

    # plots
    plot_hourly(hourly, out_path=str(out_dir / 'hourly.png'))
    plot_daily(daily, out_path=str(out_dir / 'daily.png'))

    # summary
    bh, bhc = analyzer.busiest_hour()
    bd, bdc = analyzer.busiest_day()
    total = analyzer.total_patients()
    avg = analyzer.average_daily()
    summary = generate_summary(out_dir / 'summary.json', total, bh, bhc, bd, bdc, avg)
    print('Analysis finished. Results in', out_dir)

if __name__ == '__main__':
    main()
