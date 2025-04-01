# Generator numerów KW i pobieranie danych Kw_app

## Opis

Ten program łączy dwie funkcjonalności:
- **Generowanie numerów ksiąg wieczystych:** Na podstawie wybranego prefiksu (dostępnego z rozwijanej listy), zakresu liczb oraz obliczania cyfry kontrolnej program generuje numery ksiąg w formacie `PREFIX/XXXXXXXX/C` i zapisuje je do pliku `ksiegi.txt`.
- **Pobieranie danych:** Program wykorzystuje Selenium do automatyzacji przeglądarki i pobierania danych z serwisu [przegladarka-ekw.ms.gov.pl](https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW). Pobierane dane są analizowane przy użyciu BeautifulSoup, a wyniki zapisywane są w pliku `wyniki.json`.

Program posiada interfejs graficzny oparty na Tkinter, który udostępnia dwie zakładki:
1. **Generowanie numerów:** Umożliwia wybór prefiksu z uporządkowanej listy (np. „RA1G – GRÓJEC”), wprowadzenie zakresu liczb oraz generowanie numerów ksiąg.
2. **Pobieranie danych:** Umożliwia wskazanie pliku z numerami ksiąg i rozpoczęcie procesu pobierania danych ze strony.

## Użycie

**Generowanie numerów:**
- Wybierz prefiks z rozwijanej listy (np. „RA1G – GRÓJEC”).
- Wprowadź zakres start i koniec dla 8-cyfrowej części numeru.
- Kliknij przycisk "Generuj numery". Wygenerowane numery zostaną zapisane do pliku ksiegi.txt oraz wyświetlone w logu.

**Pobieranie danych:**
- Wskaż plik z numerami ksiąg (domyślnie ksiegi.txt).
- Kliknij przycisk "Uruchom pobieranie". Program rozpocznie przeszukiwanie strony dla każdego numeru, a wyniki zapisze w pliku wyniki.json.

## Uwagi
1. Program korzysta z Selenium do automatyzacji przeglądarki. Aby uruchomić przeglądarkę w trybie headless, odkomentuj linię z argumentem --headless w funkcji init_driver.
2. Upewnij się, że masz stabilne połączenie internetowe, aby proces pobierania danych przebiegał bez zakłóceń.
3. W przypadku błędów podczas pobierania danych, program automatycznie podejmuje ponowne próby z opóźnieniem.
4. Program powstał w celach szkoleniowych - nie zalecam korzystania z niego do innych działań!
