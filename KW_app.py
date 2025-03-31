import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time, random, json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# Funkcja obliczająca cyfrę kontrolną
def oblicz_cyfre_kontrolna_kw(numer_kw):
    wartosci = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 11, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17, 'H': 18, 'I': 19,
        'J': 20, 'K': 21, 'L': 22, 'M': 23, 'N': 24, 'O': 25, 'P': 26, 'R': 27,
        'S': 28, 'T': 29, 'U': 30, 'W': 31, 'X': 10, 'Y': 32, 'Z': 33
    }
    numer_kw_oczyszczony = ''.join(znak for znak in numer_kw if znak not in ['/', ' '])
    if len(numer_kw_oczyszczony) != 12:
        return "Błąd: Numer KW (bez cyfry kontrolnej) musi zawierać dokładnie 12 znaków"
    numer_bez_cyfry = numer_kw_oczyszczony[:12]
    wynik = []
    for znak in numer_bez_cyfry:
        if znak.upper() in wartosci:
            wynik.append(wartosci[znak.upper()])
        else:
            wynik.append(znak)
    suma = (wynik[0]*1 + wynik[1]*3 + wynik[2]*7 + wynik[3]*1 +
            wynik[4]*3 + wynik[5]*7 + wynik[6]*1 + wynik[7]*3 +
            wynik[8]*7 + wynik[9]*1 + wynik[10]*3 + wynik[11]*7)
    cyfra_kontrolna = suma % 10
    return cyfra_kontrolna

# Funkcja generująca numery ksiąg wieczystych
def generuj_numery_ksieg(prefix, start_range, end_range):
    wyniki = []
    for numer in range(start_range, end_range + 1):
        numer_str = f"{numer:08d}"
        podstawa = f"{prefix}/{numer_str}"
        kontrolna = oblicz_cyfre_kontrolna_kw(podstawa)
        pelny_numer = f"{prefix}/{numer_str}/{kontrolna}"
        wyniki.append(pelny_numer)
    return wyniki

# Inicjalizacja przeglądarki (Selenium)
def init_driver():
    chrome_options = Options()
    # Jeśli chcesz uruchamiać przeglądarkę w tle, odkomentuj poniższą linię:
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)
    return driver, wait

# Funkcja przetwarzająca HTML do słownika wyników
def parse_results(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    record_data = {}
    rows = soup.find_all("div", class_="form-row")
    for row in rows:
        label_div = row.find("div", class_="label-column-50")
        content_div = row.find("div", class_="content-column-50")
        if label_div and content_div:
            label_text = label_div.get_text(separator=" ", strip=True).rstrip(":")
            content_text = content_div.get_text(separator=" ", strip=True)
            if "Właściciel" in label_text:
                paragraphs = [p.strip() for p in content_div.stripped_strings]
                content_text = "; ".join(paragraphs)
            if "Oznaczenie wydziału" in label_text:
                content_text = content_text.replace("V", "").strip()
            if "Położenie" in label_text:
                p_tag = content_div.find("p")
                if p_tag:
                    content_text = ' '.join(p_tag.get_text().split())
            record_data[label_text] = content_text
    return record_data

# Lista dostępnych prefiksów (uporządkowana alfabetycznie według kodu)
PREFIX_OPTIONS = sorted([
    "BB1B - BIELSKO-BIAŁA",
    "BB1C - CIESZYN",
    "BB1Z - ŻYWIEC",
    "BI1B - BIAŁYSTOK",
    "BI1P - BIELSK PODLASKI",
    "BI1S - SOKÓŁKA",
    "BI2P - HAJNÓWKA",
    "BI3P - SIEMIATYCZE",
    "BY1B - BYDGOSZCZ",
    "BY1I - INOWROCŁAW",
    "BY1M - MOGILNO",
    "BY1N - NAKŁO NAD NOTECIĄ",
    "BY1S - ŚWIECIE",
    "BY1T - TUCHOLA",
    "BY1U - SZUBIN",
    "BY1Z - ŻNIN",
    "BY2T - SĘPÓLNO KRAJEŃSKIE",
    "CIKW - WARSZAWA",
    "CZ1C - CZĘSTOCHOWA",
    "CZ1L - LUBLINIEC",
    "CZ1M - MYSZKÓW",
    "CZ1Z - ZAWIERCIE",
    "CZ2C - KŁOBUCK",
    "DIRS - ŻŻ DIRS",
    "EL1B - BRANIEWO",
    "EL1D - DZIAŁDOWO",
    "EL1E - ELBLĄG",
    "EL1I - IŁAWA",
    "EL1N - NOWE MIASTO LUBAWSKIE",
    "EL1O - OSTRÓDA",
    "EL2O - MORĄG",
    "GD1A - STAROGARD GDAŃSKI",
    "GD1E - KOŚCIERZYNA",
    "GD1G - GDAŃSK",
    "GD1I - KWIDZYN",
    "GD1M - MALBORK",
    "GD1R - KARTUZY",
    "GD1S - SOPOT",
    "GD1T - TCZEW",
    "GD1W - WEJHEROWO",
    "GD1Y - GDYNIA",
    "GD2I - SZTUM",
    "GD2M - NOWY DWÓR GDAŃSKI",
    "GD2W - PUCK",
    "GL1G - GLIWICE",
    "GL1J - JASTRZĘBIE-ZDRÓJ",
    "GL1R - RACIBÓRZ",
    "GL1S - RUDA ŚLĄSKA",
    "GL1T - TARNOWSKIE GÓRY",
    "GL1W - WODZISŁAW ŚLĄSKI",
    "GL1X - ŻORY",
    "GL1Y - RYBNIK",
    "GL1Z - ZABRZE",
    "GW1G - GORZÓW WIELKOPOLSKI",
    "GW1K - STRZELCE KRAJEŃSKIE",
    "GW1M - MIĘDZYRZECZ",
    "GW1S - SŁUBICE",
    "GW1U - SULĘCIN",
    "JG1B - BOLESŁAWIEC",
    "JG1J - JELENIA GÓRA",
    "JG1K - KAMIENNA GÓRA",
    "JG1L - LUBAŃ",
    "JG1S - LWÓWEK ŚLĄSKI",
    "JG1Z - ZGORZELEC",
    "KA1B - BĘDZIN",
    "KA1C - CHORZÓW",
    "KA1D - DĄBROWA GÓRNICZA",
    "KA1I - SIEMIANOWICE ŚLĄSKIE",
    "KA1J - JAWORZNO",
    "KA1K - KATOWICE",
    "KA1L - MYSŁOWICE",
    "KA1M - MIKOŁÓW",
    "KA1P - PSZCZYNA",
    "KA1S - SOSNOWIEC",
    "KA1T - TYCHY",
    "KA1Y - BYTOM",
    "KI1A - STASZÓW",
    "KI1B - BUSKO ZDRÓJ",
    "KI1H - STARACHOWICE",
    "KI1I - KAZIMIERZA WIELKA",
    "KI1J - JĘDRZEJÓW",
    "KI1K - KOŃSKIE",
    "KI1L - KIELCE",
    "KI1O - OSTROWIEC ŚWIĘTOKRZYSKI",
    "KI1P - PIŃCZÓW",
    "KI1R - SKARŻYSKO-KAMIENNA",
    "KI1S - SANDOMIERZ",
    "KI1T - OPATÓW",
    "KI1W - WŁOSZCZOWA",
    "KN1K - KOŁO",
    "KN1N - KONIN",
    "KN1S - SŁUPCA",
    "KN1T - TUREK",
    "KO1B - BIAŁOGARD",
    "KO1D - DRAWSKO POMORSKIE",
    "KO1E - SŁAWNO",
    "KO1I - SZCZECINEK",
    "KO1K - KOSZALIN",
    "KO1L - KOŁOBRZEG",
    "KO1W - WAŁCZ",
    "KO2B - ŚWIDWIN",
    "KR1B - SUCHA BESKIDZKA",
    "KR1C - CHRZANÓW",
    "KR1E - OŚWIĘCIM",
    "KR1H - PROSZOWICE",
    "KR1I - WIELICZKA",
    "KR1K - CZERNICHÓW",
    "KR1M - MIECHÓW",
    "KR1O - OLKUSZ",
    "KR1P - KRAKÓW",
    "KR1S - SŁOMNIKI",
    "KR1W - WADOWICE",
    "KR1Y - MYŚLENICE",
    "KR2E - KĘTY",
    "KR2I - NIEPOŁOMICE",
    "KR2K - KRZESZOWICE",
    "KR2P - SKAŁA",
    "KR2Y - DOBCZYCE",
    "KR3I - SKAWINA",
    "KS1B - BRZOZÓW",
    "KS1E - LESKO",
    "KS1J - JASŁO",
    "KS1K - KROSNO",
    "KS1S - SANOK",
    "KS2E - USTRZYKI DOLNE",
    "KZ1A - KALISZ",
    "KZ1E - KĘPNO",
    "KZ1J - JAROCIN",
    "KZ1O - OSTRZESZÓW",
    "KZ1P - PLESZEW",
    "KZ1R - KROTOSZYN",
    "KZ1W - OSTRÓW WIELKOPOLSKI",
    "LD1B - BRZEZINY",
    "LD1G - ZGIERZ",
    "LD1H - SKIERNIEWICE",
    "LD1K - KUTNO",
    "LD1M - ŁÓDŹ",
    "LD1O - ŁOWICZ",
    "LD1P - PABIANICE",
    "LD1R - RAWA MAZOWIECKA",
    "LD1Y - ŁĘCZYCA",
    "LE1G - GŁOGÓW",
    "LE1J - JAWOR",
    "LE1L - LEGNICA",
    "LE1U - LUBIN",
    "LE1Z - ZŁOTORYJA",
    "LM1G - GRAJEWO",
    "LM1L - ŁOMŻA",
    "LM1W - WYSOKIE MAZOWIECKIE",
    "LM1Z - ZAMBRÓW",
    "LU1A - LUBARTÓW",
    "LU1B - BIAŁA PODLASKA",
    "LU1C - CHEŁM",
    "LU1I - LUBLIN",
    "LU1K - KRAŚNIK",
    "LU1O - OPOLE LUBELSKIE",
    "LU1P - PUŁAWY",
    "LU1R - RADZYŃ PODLASKI",
    "LU1S - ŚWIDNIK",
    "LU1U - ŁUKÓW",
    "LU1W - WŁODAWA",
    "LU1Y - RYKI",
    "NS1G - GORLICE",
    "NS1L - LIMANOWA",
    "NS1M - MUSZYNA",
    "NS1S - NOWY SĄCZ",
    "NS1T - NOWY TARG",
    "NS1Z - ZAKOPANE",
    "NS2L - MSZANA DOLNA",
    "OL1B - BISKUPIEC",
    "OL1C - OLECKO",
    "OL1E - EŁK",
    "OL1G - GIŻYCKO",
    "OL1K - KĘTRZYN",
    "OL1L - LIDZBARK WARMIŃSKI",
    "OL1M - MRĄGOWO",
    "OL1N - NIDZICA",
    "OL1O - OLSZTYN",
    "OL1P - PISZ",
    "OL1S - SZCZYTNO",
    "OL1Y - BARTOSZYCE",
    "OL2G - WĘGORZEWO",
    "OP1B - BRZEG",
    "OP1G - GŁUBCZYCE",
    "OP1K - KĘDZIERZYN-KOŹLE",
    "OP1L - OLESNO",
    "OP1N - NYSA",
    "OP1O - OPOLE",
    "OP1P - PRUDNIK",
    "OP1S - STRZELCE OPOLSKIE",
    "OP1U - KLUCZBORK",
    "OS1M - OSTRÓW MAZOWIECKA",
    "OS1O - OSTROŁĘKA",
    "OS1P - PRZASNYSZ",
    "OS1U - PUŁTUSK",
    "OS1W - WYSZKÓW",
    "PL1C - CIECHANÓW",
    "PL1E - SIERPC",
    "PL1G - GOSTYNIN",
    "PL1L - PŁOŃSK",
    "PL1M - MŁAWA",
    "PL1O - SOCHACZEW",
    "PL1P - PŁOCK",
    "PL1Z - ŻYRARDÓW",
    "PL2M - ŻUROMIN",
    "PO1A - SZAMOTUŁY",
    "PO1B - WĄGROWIEC",
    "PO1D - ŚRODA WLKP.",
    "PO1E - WOLSZTYN",
    "PO1F - WRZEŚNIA",
    "PO1G - GNIEZNO",
    "PO1H - CHODZIEŻ",
    "PO1I - PIŁA",
    "PO1K - KOŚCIAN",
    "PO1L - LESZNO",
    "PO1M - ŚREM",
    "PO1N - NOWY TOMYŚL",
    "PO1O - OBORNIKI",
    "PO1P - POZNAŃ (V)",
    "PO1R - RAWICZ",
    "PO1S - GRODZISK WLKP.",
    "PO1T - TRZCIANKA",
    "PO1Y - GOSTYŃ",
    "PO1Z - ZŁOTÓW",
    "PO2A - MIĘDZYCHÓD",
    "PO2H - WYRZYSK",
    "PO2P - POZNAŃ (VI)",
    "PO2T - CZARNKÓW",
    "PR1J - JAROSŁAW",
    "PR1L - LUBACZÓW",
    "PR1P - PRZEMYŚL",
    "PR1R - PRZEWORSK",
    "PR2R - SIENIAWA",
    "PT1B - BEŁCHATÓW",
    "PT1O - OPOCZNO",
    "PT1P - PIOTRKÓW TRYBUNALSKI",
    "PT1R - RADOMSKO",
    "PT1T - TOMASZÓW MAZOWIECKI",
    "RA1G - GRÓJEC",
    "RA1K - KOZIENICE",
    "RA1L - LIPSKO",
    "RA1P - PRZYSUCHA",
    "RA1R - RADOM",
    "RA1S - SZYDŁOWIEC",
    "RA1Z - ZWOLEŃ",
    "RA2G - BIAŁOBRZEGI",
    "RA2Z - PIONKI",
    "RZ1A - ŁAŃCUT",
    "RZ1D - DĘBICA",
    "RZ1E - LEŻAJSK",
    "RZ1R - ROPCZYCE",
    "RZ1S - STRZYŻÓW",
    "RZ1Z - RZESZÓW",
    "RZ2Z - TYCZYN",
    "SI1G - GARWOLIN",
    "SI1M - MIŃSK MAZOWIECKI",
    "SI1P - SOKOŁÓW PODLASKI",
    "SI1S - SIEDLCE",
    "SI1W - WĘGRÓW",
    "SI2S - ŁOSICE",
    "SL1B - BYTÓW",
    "SL1C - CHOJNICE",
    "SL1L - LĘBORK",
    "SL1M - MIASTKO",
    "SL1S - SŁUPSK",
    "SL1Z - CZŁUCHÓW",
    "SO1C - CZELADŹ",
    "SR1L - ŁASK",
    "SR1S - SIERADZ",
    "SR1W - WIELUŃ",
    "SR1Z - ZDUŃSKA WOLA",
    "SR2L - PODDĘBICE",
    "SR2W - PAJĘCZNO",
    "SU1A - AUGUSTÓW",
    "SU1N - SEJNY",
    "SU1S - SUWAŁKI",
    "SW1D - DZIERŻONIÓW",
    "SW1K - KŁODZKO",
    "SW1S - ŚWIDNICA",
    "SW1W - WAŁBRZYCH",
    "SW1Z - ZĄBKOWICE ŚLĄSKIE",
    "SW2K - NOWA RUDA",
    "SZ1C - CHOSZCZNO",
    "SZ1G - GRYFICE",
    "SZ1K - KAMIEŃ POMORSKI",
    "SZ1L - ŁOBEZ",
    "SZ1M - MYŚLIBÓRZ",
    "SZ1O - GOLENIÓW",
    "SZ1S - SZCZECIN",
    "SZ1T - STARGARD",
    "SZ1W - ŚWINOUJŚCIE",
    "SZ1Y - GRYFINO",
    "SZ2S - POLICE",
    "SZ2T - PYRZYCE",
    "TB1K - KOLBUSZOWA",
    "TB1M - MIELEC",
    "TB1N - NISKO",
    "TB1S - STALOWA WOLA",
    "TB1T - TARNOBRZEG",
    "TO1B - BRODNICA",
    "TO1C - CHEŁMNO",
    "TO1G - GOLUB-DOBRZYŃ",
    "TO1T - TORUŃ",
    "TO1U - GRUDZIĄDZ",
    "TO1W - WĄBRZEŹNO",
    "TR1B - BRZESKO",
    "TR1D - DĄBROWA TARNOWSKA",
    "TR1O - BOCHNIA",
    "TR1T - TARNÓW",
    "TR2T - TUCHÓW",
    "WA1G - GRODZISK MAZOWIECKI",
    "WA1I - PIASECZNO",
    "WA1L - LEGIONOWO",
    "WA1M - WARSZAWA (VI)",
    "WA1N - NOWY DWÓR MAZOWIECKI",
    "WA1O - OTWOCK",
    "WA1P - PRUSZKÓW",
    "WA1W - WOŁOMIN",
    "WA2M - WARSZAWA (VII)",
    "WA3M - WARSZAWA (IX)",
    "WA4M - WARSZAWA (X)",
    "WA5M - WARSZAWA (XIII)",
    "WA6M - WARSZAWA (XV)",
    "WL1A - ALEKSANDRÓW KUJAWSKI",
    "WL1L - LIPNO",
    "WL1R - RADZIEJÓW",
    "WL1W - WŁOCŁAWEK",
    "WL1Y - RYPIN",
    "WR1E - OLEŚNICA",
    "WR1K - WROCŁAW",
    "WR1L - WOŁÓW",
    "WR1M - MILICZ",
    "WR1O - OŁAWA",
    "WR1S - ŚRODA ŚLĄSKA",
    "WR1T - STRZELIN",
    "WR1W - TRZEBNICA",
    "ZA1B - BIŁGORAJ",
    "ZA1H - HRUBIESZÓW",
    "ZA1J - JANÓW LUBELSKI",
    "ZA1K - KRASNYSTAW",
    "ZA1T - TOMASZÓW LUBELSKI",
    "ZA1Z - ZAMOŚĆ",
    "ZG1E - ZIELONA GÓRA",
    "ZG1G - ŻAGAŃ",
    "ZG1K - KROSNO ODRZAŃSKIE",
    "ZG1N - NOWA SÓL",
    "ZG1R - ŻARY",
    "ZG1S - ŚWIEBODZIN",
    "ZG1W - WSCHOWA",
    "ZG2K - GUBIN",
    "ZG2S - SULECHÓW"
])

# Główna klasa aplikacji okienkowej
class KwApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generator numerów KW i pobieranie danych")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        # Notebook z dwiema zakładkami
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        # Zakładka: Generowanie numerów
        self.tab_generate = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_generate, text="Generowanie numerów")

        # Prefiks z rozwijanej listy
        ttk.Label(self.tab_generate, text="Wybierz prefiks:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_prefix = ttk.Combobox(self.tab_generate, values=PREFIX_OPTIONS, state="readonly")
        # Ustaw domyślnie "RA1G - GRÓJEC" (jeśli jest na liście)
        if "RA1G - GRÓJEC" in PREFIX_OPTIONS:
            self.combo_prefix.set("RA1G - GRÓJEC")
        else:
            self.combo_prefix.current(0)
        self.combo_prefix.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.tab_generate, text="Zakres start (8-cyfrowa liczba):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_start = ttk.Entry(self.tab_generate)
        self.entry_start.insert(0, "94000")
        self.entry_start.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.tab_generate, text="Zakres koniec (8-cyfrowa liczba):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_end = ttk.Entry(self.tab_generate)
        self.entry_end.insert(0, "94100")
        self.entry_end.grid(row=2, column=1, padx=5, pady=5)

        self.btn_generate = ttk.Button(self.tab_generate, text="Generuj numery", command=self.generate_numbers)
        self.btn_generate.grid(row=3, column=0, columnspan=2, pady=10)

        self.txt_generate = tk.Text(self.tab_generate, height=15)
        self.txt_generate.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.tab_generate.rowconfigure(4, weight=1)
        self.tab_generate.columnconfigure(1, weight=1)

        # Zakładka: Pobieranie danych
        self.tab_scrape = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_scrape, text="Pobieranie danych")

        ttk.Label(self.tab_scrape, text="Plik z numerami ksiąg:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_kw_file = ttk.Entry(self.tab_scrape, width=50)
        self.entry_kw_file.insert(0, "ksiegi.txt")
        self.entry_kw_file.grid(row=0, column=1, padx=5, pady=5)
        self.btn_browse = ttk.Button(self.tab_scrape, text="Przeglądaj", command=self.browse_file)
        self.btn_browse.grid(row=0, column=2, padx=5, pady=5)

        self.btn_scrape = ttk.Button(self.tab_scrape, text="Uruchom pobieranie", command=self.start_scraping_thread)
        self.btn_scrape.grid(row=1, column=0, columnspan=3, pady=10)

        self.txt_scrape = tk.Text(self.tab_scrape, height=20)
        self.txt_scrape.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.tab_scrape.rowconfigure(2, weight=1)
        self.tab_scrape.columnconfigure(1, weight=1)

    def log_generate(self, message):
        self.txt_generate.insert(tk.END, message + "\n")
        self.txt_generate.see(tk.END)

    def log_scrape(self, message):
        self.txt_scrape.insert(tk.END, message + "\n")
        self.txt_scrape.see(tk.END)

    def generate_numbers(self):
        try:
            # Pobranie wybranego prefiksu – wyciągnięcie kodu przed " - "
            selected = self.combo_prefix.get()
            if " - " in selected:
                prefix = selected.split(" - ")[0]
            else:
                prefix = selected
            start_range = int(self.entry_start.get().strip())
            end_range = int(self.entry_end.get().strip())
        except ValueError:
            messagebox.showerror("Błąd", "Zakresy muszą być liczbami całkowitymi.")
            return

        self.log_generate("Rozpoczynam generowanie numerów...")
        numbers = generuj_numery_ksieg(prefix, start_range, end_range)
        # Zapis do pliku
        with open("ksiegi.txt", "w", encoding="utf-8") as file:
            for numer in numbers:
                file.write(numer + "\n")
        self.log_generate(f"Wygenerowano {len(numbers)} numerów. Zapisano do pliku ksiegi.txt.")
        self.log_generate("Numery ksiąg:")
        for numer in numbers:
            self.log_generate(numer)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Wybierz plik z numerami ksiąg", filetypes=[("Pliki tekstowe", "*.txt")])
        if file_path:
            self.entry_kw_file.delete(0, tk.END)
            self.entry_kw_file.insert(0, file_path)

    def start_scraping_thread(self):
        t = threading.Thread(target=self.scrape_records)
        t.daemon = True
        t.start()

    def scrape_records(self):
        kw_file = self.entry_kw_file.get().strip()
        try:
            with open(kw_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.log_scrape(f"Błąd przy otwieraniu pliku: {e}")
            return

        results = {}
        self.log_scrape("Inicjalizacja przeglądarki...")
        try:
            driver, wait = init_driver()
        except Exception as e:
            self.log_scrape(f"Błąd przy inicjalizacji przeglądarki: {e}")
            return

        for record in lines:
            parts = record.split("/")
            if len(parts) != 3:
                self.log_scrape(f"Pominięto rekord (niepoprawny format): {record}")
                continue
            kodWydzialu, numerKsiegi, cyfraKontrolna = parts

            while True:
                try:
                    driver.get("https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW")
                    select_element = wait.until(EC.presence_of_element_located((By.ID, "kodWydzialu")))
                    driver.execute_script(
                        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                        select_element, kodWydzialu
                    )
                    numer_field = wait.until(EC.visibility_of_element_located((By.ID, "numerKsiegiWieczystej")))
                    numer_field.clear()
                    numer_field.send_keys(numerKsiegi)
                    cyfra_field = wait.until(EC.visibility_of_element_located((By.ID, "cyfraKontrolna")))
                    cyfra_field.clear()
                    cyfra_field.send_keys(cyfraKontrolna)
                    driver.find_element(By.ID, "wyszukaj").click()
                    section_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.section")))
                    html_content = section_element.get_attribute("innerHTML")
                    if "The requested URL was rejected" in html_content:
                        raise Exception("URL rejected")
                    record_data = parse_results(html_content)
                    results[record] = record_data
                    self.log_scrape(f"Przetworzono: {record}")
                    break
                except Exception as e:
                    self.log_scrape(f"Błąd dla rekordu {record}: {e}")
                    with open("wyniki.json", "w", encoding="utf-8") as f:
                        json.dump(results, f, ensure_ascii=False, indent=4)
                    self.log_scrape("Zamykam przeglądarkę i odczekuję 30 sekund przed ponowną próbą...")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    time.sleep(30)
                    try:
                        driver, wait = init_driver()
                    except Exception as ex:
                        self.log_scrape(f"Błąd przy ponownej inicjalizacji: {ex}")
                        return
            with open("wyniki.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            delay = random.uniform(4, 10)
            self.log_scrape(f"Oczekiwanie {delay:.2f} sekund przed następnym zapytaniem...")
            time.sleep(delay)
        with open("wyniki.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        self.log_scrape("Wszystkie wyniki zapisane do pliku wyniki.json")
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == '__main__':
    app = KwApp()
    app.mainloop()
