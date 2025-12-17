import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import io
import os
from src.database import init_db, insert_analysis
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.data_loader import DataLoader
from src.analyzer import ArrivalAnalyzer
from src.plotter import plot_hourly, plot_daily
from src.report import generate_summary

# Styling constants
BG = "#1f2326"
PANEL_BG = "#16171a"
ACCENT = "#4A90E2"
TEXT = "#E6E6E6"
SUB_TEXT = "#A9B0B6"
BTN_BG = "#2E86FF"
BTN_FG = "#FFFFFF"
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUB = ("Segoe UI", 11)
FONT_NORMAL = ("Segoe UI", 10)

class PatientArrivalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Patient Arrival Counter")
        self.geometry("980x640")
        self.minsize(900, 600)
        self.configure(bg=BG)

        # state
        self.csv_path = None
        self.out_dir = Path("data/output")
        self.current_df = None
        self.hourly_df = None
        self.daily_df = None
        self.summary = None

        # menu,header and body building
        self.build_menu()
        self.build_header()
        self.build_body()

    # Menubar
    def build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Ouvrir CSV...", command=self.action_open_csv)
        file_menu.add_command(label="Choisir dossier de sortie...", command=self.action_choose_out)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Accueil", command=lambda: self.show_page("home"))
        view_menu.add_command(label="Analyser", command=lambda: self.show_page("analyze"))
        view_menu.add_command(label="Graphiques", command=lambda: self.show_page("plots"))
        menubar.add_cascade(label="Voir", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Guide d'utilisation", command=lambda: self.show_page("guide"))
        help_menu.add_command(label="À propos", command=lambda: self.show_page("about"))
        menubar.add_cascade(label="Aide", menu=help_menu)

        self.config(menu=menubar)

    # Header
    def build_header(self):
        header = tk.Frame(self, bg=BG, height=70)
        header.pack(side="top", fill="x")
        title = tk.Label(header, text="Patient Arrival Counter", font=FONT_TITLE, fg=ACCENT, bg=BG)
        subtitle = tk.Label(header, text="Analyse simple des arrivées", font=FONT_NORMAL, fg=SUB_TEXT, bg=BG)
        title.pack(anchor="w", padx=20, pady=(8,0))
        subtitle.pack(anchor="w", padx=20)

    # Body (sidebar + content)
    def build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(side="top", fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(body, bg=PANEL_BG, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Sidebar items
        nav_items = [
            ("Accueil", "home"),
            ("Analyser un CSV", "analyze"),
            ("Graphiques", "plots"),
            ("Résultats", "results"),
            ("Guide d'utilisation", "guide"),
            ("À propos", "about")
        ]
        for text, page in nav_items:
            b = tk.Button(sidebar, text=text, font=FONT_SUB, fg=TEXT, bg=PANEL_BG, bd=0, relief="flat",
                          anchor="w", command=lambda p=page: self.show_page(p), padx=15, pady=8, cursor="hand2")
            b.pack(fill="x")

        # Main content area
        self.content = tk.Frame(body, bg=BG)
        self.content.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Pages dictionary
        self.pages = {}
        for page_name in ("home", "analyze", "plots", "results", "guide", "about"):
            frame = tk.Frame(self.content, bg=BG)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[page_name] = frame

        self.build_home(self.pages["home"])
        self.build_analyze(self.pages["analyze"])
        self.build_plots(self.pages["plots"])
        self.build_results(self.pages["results"])
        self.build_guide(self.pages["guide"])
        self.build_about(self.pages["about"])

        # start on home
        self.show_page("home")

    # ---------------------------
    # Page builders
    # ---------------------------
    def build_home(self, frame):
        tk.Label(frame, text="Bienvenue", font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT).pack(anchor="nw")
        text = (
            "Ce logiciel vous permet d'analyser rapidement un fichier CSV contenant\n"
            "les arrivées de patients (colonnes obligatoires : timestamp, patient_id).\n\n"
            "Fonctions disponibles :\n"
            "- Charger un CSV\n"
            "- Lancer l'analyse (compte horaire et journalier)\n"
            "- Storer chaque analyse dans une base de donnée sqlite\n"
            "- Générer des graphiques et un résumé JSON\n\n"
            "Utilisez le menu Fichier ou allez dans 'Analyser un CSV' pour démarrer."
        )
        tk.Label(frame, text=text, font=("Segoe UI", 10), bg=BG, fg=SUB_TEXT, justify="left").pack(anchor="nw", pady=10, padx=6)

    def build_analyze(self, frame):
        tk.Label(frame, text="Analyser un CSV", font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT).pack(anchor="nw")
        container = tk.Frame(frame, bg=BG)
        container.pack(fill="both", expand=True, pady=8)

        # Controls on top
        controls = tk.Frame(container, bg=BG)
        controls.pack(fill="x", padx=6, pady=4)

        self.csv_entry = tk.Entry(controls, font=FONT_NORMAL, bg="#2b2f33", fg=TEXT, width=60)
        self.csv_entry.pack(side="left", padx=(0,6))
        tk.Button(controls, text="Parcourir", command=self.action_open_csv, bg=BTN_BG, fg=BTN_FG, bd=0, cursor="hand2").pack(side="left", padx=4)
        tk.Button(controls, text="Choisir dossier sortie", command=self.action_choose_out, bg=BTN_BG, fg=BTN_FG, bd=0, cursor="hand2").pack(side="left", padx=4)

        # Action buttons
        action_frame = tk.Frame(container, bg=BG)
        action_frame.pack(fill="x", padx=6, pady=8)
        tk.Button(action_frame, text="Lancer l'analyse", command=self.start_analysis_thread, bg=ACCENT, fg="white", bd=0, padx=10, pady=6, cursor="hand2").pack(side="left")
        tk.Button(action_frame, text="Réinitialiser", command=self.reset_state, bg="#444", fg="white", bd=0, padx=10, pady=6, cursor="hand2").pack(side="left", padx=8)

        # Table preview area
        preview_frame = tk.Frame(container, bg=BG)
        preview_frame.pack(fill="both", expand=True, padx=6, pady=6)

        lbl = tk.Label(preview_frame, text="Aperçu du CSV (10 premières lignes)", bg=BG, fg=TEXT, font=FONT_NORMAL)
        lbl.pack(anchor="nw")

        cols = ("timestamp", "patient_id")
        tree_container = tk.Frame(preview_frame)
        tree_container.pack(fill="both", expand=True, pady=6)

        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=200, anchor="center")
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        # Status
        self.status_var = tk.StringVar(value="Prêt")
        status_lbl = tk.Label(frame, textvariable=self.status_var, bg=BG, fg=SUB_TEXT, anchor="w")
        status_lbl.pack(fill="x", padx=6, pady=6)

    def build_plots(self, frame):
        tk.Label(frame, text="Graphiques", font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT).pack(anchor="nw")

        # Canvas area for plot
        self.plot_area = tk.Frame(frame, bg=BG)
        self.plot_area.pack(fill="both", expand=True, padx=6, pady=6)

        # Buttons to show specific plots
        btns = tk.Frame(frame, bg=BG)
        btns.pack(fill="x", padx=6)
        tk.Button(btns, text="Montrer patients par heure", command=lambda: self.show_plot("hourly"), bg=BTN_BG, fg=BTN_FG, bd=0, cursor="hand2").pack(side="left", padx=6)
        tk.Button(btns, text="Montrer patients par jour", command=lambda: self.show_plot("daily"), bg=BTN_BG, fg=BTN_FG, bd=0, cursor="hand2").pack(side="left", padx=6)

    def build_results(self, frame):
        tk.Label(frame, text="Résultats", font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT).pack(anchor="nw", padx=6, pady=(6,2))
        self.results_text = tk.Text(frame, height=12, bg="#121314", fg=TEXT, insertbackground=TEXT, font=FONT_NORMAL)
        self.results_text.pack(fill="both", expand=True, padx=6, pady=6)

    def build_guide(self, frame):
        tk.Label(frame, text="Guide d'utilisation", font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT).pack(anchor="nw", padx=6)
        guide_text = """
            Mode d'emploi rapide :

            1) Préparez un fichier CSV contenant au minimum deux colonnes :
            - timestamp : au format 'YYYY-MM-DD HH:MM:SS' (ou autre format lisible par pandas)
            - patient_id : identifiant unique du patient (ou identifiant par visite)

            2) Allez dans 'Analyser un CSV' -> Parcourir -> sélectionnez le CSV.
            (Optionnel) Choisissez un dossier de sortie (sinon 'data/output').

            3) Cliquez sur 'Lancer l'analyse'.
            Le logiciel génère :
                - hourly_counts.csv
                - daily_counts.csv
                - hourly.png
                - daily.png
                - summary.json
            
            4) Visualisez les graphiques dans 'Graphiques' et les résultats dans 'Résultats'.
            5) Storer les analyses dans une base données sqlite qui ce trouve dans le dossier de output
            """
        txt = tk.Text(frame, wrap="word", bg="#121314", fg=TEXT, insertbackground=TEXT, font=("Segoe UI", 10))
        txt.insert("1.0", guide_text.strip())
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=6, pady=6)

    def build_about(self, frame):
        tk.Label(frame, text="À propos", font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT).pack(anchor="nw", padx=6)
        about = (
            "PatientArrivalCounter\n"
            "Version : 1.0\n"
            "Auteur : Sebaa Fodil,Doctorant SIAD\n\n"
            "Outil simple pour analyser les arrivées de patients aux urgences.\n"
        )
        tk.Label(frame, text=about, font=FONT_NORMAL, bg=BG, fg=SUB_TEXT, justify="left").pack(anchor="nw", padx=6, pady=10)

    # Page switching
    def show_page(self, page_name):
        for name, frame in self.pages.items():
            if name == page_name:
                frame.lift()
            else:
                frame.lower()
    def action_open_csv(self):
        p = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"), ("All files","*.*")])
        if p:
            self.csv_path = Path(p)
            # update entry if exists
            try:
                self.csv_entry.delete(0, tk.END)
                self.csv_entry.insert(0, str(p))
            except Exception:
                pass
            # preview
            self.preview_csv(p)

    def action_choose_out(self):
        p = filedialog.askdirectory()
        if p:
            self.out_dir = Path(p)
            messagebox.showinfo("Dossier sortie", f"Dossier de sortie : {self.out_dir}")

    def preview_csv(self, path):
        try:
            dl = DataLoader(path)
            df = dl.load_csv()
            dl.validate(df)
            df = dl.parse_dates(df)
            self.current_df = df
            # update treeview
            for r in self.tree.get_children():
                self.tree.delete(r)
            preview = df.head(10)
            for _, row in preview.iterrows():
                self.tree.insert("", "end", values=(str(row.get("timestamp")), str(row.get("patient_id"))))
            self.status_var.set(f"Fichier chargé : {os.path.basename(path)} ({len(df)} lignes)")
        except Exception as e:
            messagebox.showerror("Erreur lors du chargement", str(e))

    def reset_state(self):
        self.csv_entry.delete(0, tk.END)
        for r in self.tree.get_children():
            self.tree.delete(r)
        self.current_df = None
        self.hourly_df = None
        self.daily_df = None
        self.summary = None
        self.status_var.set("Réinitialisé")

    def start_analysis_thread(self):
        # Use a thread to keep UI responsive
        t = threading.Thread(target=self.run_analysis, daemon=True)
        t.start()

    def run_analysis(self):
        try:
            # Validate current path
            if self.csv_entry.get():
                csv = Path(self.csv_entry.get())
            else:
                messagebox.showerror("Erreur", "Aucun fichier CSV sélectionné.")
                return

            if not csv.exists():
                messagebox.showerror("Erreur", "Fichier CSV inexistant.")
                return

            out_dir = self.out_dir or Path("data/output")
            out_dir.mkdir(parents=True, exist_ok=True)

            self.status_var.set("Analyse en cours...")
            dl = DataLoader(csv)
            df = dl.load_csv()
            dl.validate(df)
            df = dl.parse_dates(df)
            analyzer = ArrivalAnalyzer(df)
            hourly = analyzer.hourly_counts()
            daily = analyzer.daily_counts()

            # Save outputs
            hourly.to_csv(out_dir / "hourly_counts.csv", index=False)
            daily.to_csv(out_dir / "daily_counts.csv", index=False)

            # Generate plots (these functions save PNG files)
            # We call the plot functions with explicit output file names
            plot_hourly(hourly, out_path=str(out_dir / "hourly.png"))
            plot_daily(daily, out_path=str(out_dir / "daily.png"))

            # summary
            bh, bhc = analyzer.busiest_hour()
            bd, bdc = analyzer.busiest_day()
            total = analyzer.total_patients()
            avg = analyzer.average_daily()

            summary = generate_summary(out_dir / "summary.json", total, bh, bhc, bd, bdc, avg)

            # update state
            self.current_df = df
            self.hourly_df = hourly
            self.daily_df = daily
            self.summary = summary

            # update results display
            self._update_results_display(summary)
            self.status_var.set("Analyse terminée.")
            messagebox.showinfo("Succès", f"Analyse terminée. Résultats dans : {out_dir}")

            # switch to results page
            self.show_page("results")
            # Initialiser la base (crée si n'existe pas)
            init_db()

            # Enregistrer l'analyse
            insert_analysis(
                file_name=csv.name,
                total_patients=total,
                busiest_hour=str(bh),
                busiest_day=str(bd)
            )
        except Exception as e:
            self.status_var.set("Erreur")
            messagebox.showerror("Erreur pendant l'analyse", str(e))

    def _update_results_display(self, summary):
        txt = self.results_text
        txt.configure(state="normal")
        txt.delete("1.0", "end")
        lines = [
            f"Total patients (identifiants uniques): {summary.get('total_patients')}",
            f"Busiest hour: {summary.get('busiest_hour')} (count = {summary.get('busiest_hour_count')})",
            f"Busiest day: {summary.get('busiest_day')} (count = {summary.get('busiest_day_count')})",
            f"Average daily arrivals: {summary.get('average_daily'):.2f}"
        ]
        txt.insert("1.0", "\n".join(lines))
        txt.configure(state="disabled")

    def show_plot(self, which):
        # clear plot area
        for w in self.plot_area.winfo_children():
            w.destroy()

        if which == "hourly":
            png = self.out_dir / "hourly.png"
        else:
            png = self.out_dir / "daily.png"

        if png.exists():
                try:
                    img = Image.open(png)
                    img = img.resize((760, 420), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    lbl = tk.Label(self.plot_area, image=photo, bg=BG)
                    lbl.image = photo
                    lbl.pack(expand=True)
                    return
                except Exception:
                    # afficher message d'erreur en cas de problème
                    lbl = tk.Label(self.plot_area, text=f"Le fichier {png.name} existe mais n'a pas pu être affiché.\nOuvre-le dans le dossier de sortie.",
                                bg=BG, fg=SUB_TEXT, font=FONT_NORMAL, justify="center")
                    lbl.pack(expand=True)
        else:
            lbl = tk.Label(self.plot_area, text="Aucun graphique généré. Lancez l'analyse d'abord.",
                           bg=BG, fg=SUB_TEXT, font=FONT_NORMAL)
            lbl.pack(expand=True)

# Run app
def main():
    app = PatientArrivalApp()
    app.mainloop()

if __name__ == "__main__":
    main()
