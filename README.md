🤖 Bot Discord — Wielofunkcyjny Asystent Modularny
Opis projektu
Projekt bota Discord jest zaprojektowany w języku Python z użyciem biblioteki discord.py. Celem jest utworzenie bota, który będzie oferował różne funkcjonalności, takie jak: zarządzanie muzyką, moderowanie serwera, prezentowanie ofert gier i inne. 
Bot jest modułowy, co oznacza, że jest podzielony na wiele komponentów odpowiadających za różne funkcje.
📁 Struktura projektu


⚙️ Opis najważniejszych plików
📁 cogs/
Zawiera wszystkie główne funkcjonalności bota w postaci osobnych modułów.
Plik	Opis
games.py	Komendy `!sales` i `!epic` pokazujące promocje Steam oraz darmowe gry na Epic Games
music.py	Odtwarzanie muzyki z YouTube, komendy: `!music`, `!queue`, `!skip`, `!stop`
moderation.py	Moderacja: ban, mute, kick, czyszczenie wiadomości
list.py	Praca z listami użytkowników
sort.py	Sortowanie danych (liczby, teksty)
utils.py	Funkcje pomocnicze (formatowanie daty, generowanie komunikatów itd.)
math_calculator.py	Kalkulator matematyczny: operacje arytmetyczne, funkcje matematyczne, konwersja systemów liczbowych
📁 db/
- `database.py` — logika interakcji z bazą danych SQLite
- `bot_database.db` — główna baza danych
- `__init__.py` — inicjalizacja modułu

🔧 bot.py
- Główny punkt startowy aplikacji
- Dynamiczne ładowanie wszystkich `cogs`
- Połączenie z bazą danych
- Obsługa eventów i uruchomienie bota

🛠️ Użyte technologie
Komponent	Opis
discord.py	Główna biblioteka do tworzenia bota
yt_dlp + ffmpeg	Streaming muzyki z YouTube
requests	Pobieranie danych z API (Steam, Epic)
sqlite3	Prosta wbudowana baza danych
asyncio	Architektura asynchroniczna
embed	Formatowane wiadomości na Discordzie
Struktura projektu
Projekt posiada następującą strukturę folderów i plików:
1. cogs:
   - pycache: folder zawierający pliki kompilacji.
   - games.py: moduł odpowiedzialny za komendy związane z grami (Steam, Epic Games Store).
   - list.py: lista dostępnych komend.
   - music.py: moduł do zarządzania muzyką na serwerze.
   - moderation.py: komendy do moderowania serwera.
   - sort.py: sortowanie danych związanych z grami.
   - utils.py: pomocnicze funkcje.
   - math_calculator.py: moduł oferujący funkcje kalkulatora matematycznego.
2. db:
   - pycache: folder zawierający pliki kompilacji.
   - init.py: plik inicjalizujący bazę danych.
   - bot_database.db: baza danych przechowująca dane bota.
   - database.py: moduł do zarządzania bazą danych.
3. bot.py: główny plik uruchamiający bota.
4. security.md: dokumentacja dotycząca bezpieczeństwa bota.
5. readme.md: dokumentacja projektu.
6. requirements.txt: lista zależności bota.
7. .gitignore: plik ignorujący niepotrzebne pliki w repozytorium.

//Opis struktury kodu
Projekt wykorzystuje podejście modularne, co oznacza, że każda funkcjonalność bota jest oddzielona w osobnym modułach. To pozwala na łatwiejsze zarządzanie kodem oraz umożliwia rozbudowę bota o nowe funkcjonalności w przyszłości. 
Moduł bot.py
Moduł główny, który uruchamia bota i ładuje wszystkie rozszerzenia (moduły) przy starcie bota. Odpowiada za konfigurację i uruchomienie bota na podstawie tokena.
Moduł music.py
Moduł odpowiedzialny za zarządzanie muzyką na serwerze. Wykorzystuje bibliotekę yt-dlp do pobierania muzyki z YouTube oraz FFmpeg do odtwarzania utworów. Zawiera komendy do dodawania utworów do kolejki, pomijania utworów, zatrzymywania odtwarzania i wyświetlania kolejki.
Moduł games.py
Moduł odpowiedzialny za wyświetlanie gier na Steam i darmowych gier w Epic Games Store. Komenda '!sales' pobiera dane o grach ze Steam z rabatami, a komenda '!epic' pokazuje darmowe gry dostępne w Epic Games Store.
Moduł moderation.py
Moduł odpowiedzialny za moderowanie serwera Discord. Obejmuje komendy do wyrzucania i banowania użytkowników, zarządzania kanałami tekstowymi i głosowymi oraz czyszczenia wiadomości w kanałach.
Moduł utils.py
Moduł zawierający pomocnicze funkcje wspierające inne części systemu, np. do zarządzania źródłami audio i formatami danych.
Moduł math_calculator.py
Moduł zapewniający funkcje kalkulatora matematycznego. Umożliwia przeprowadzanie podstawowych operacji matematycznych (dodawanie, odejmowanie, mnożenie, dzielenie), funkcji matematycznych (sin, cos, tan, pierwiastek kwadratowy, logarytmy) oraz konwersję między różnymi systemami liczbowymi (dziesiętny, dwójkowy, szesnastkowy). Wszystkie obliczenia przeprowadzane są bezpiecznie, z walidacją danych wejściowych.

Opis komend
Komendy muzyczne
!music <link>: Dodaje utwór z YouTube do kolejki.
!skip: Pomija aktualnie odtwarzany utwór.
!stop: Zatrzymuje odtwarzanie i usuwa kolejkę.
!queue (lub !q): Wyświetla aktualną kolejkę muzyczną.
Komendy do gier
!sales: Wyświetla listę gier na Steam z rabatami.
!epic: Pokazuje darmowe gry w Epic Games Store.
Komendy moderacyjne
!kick @user: Wyrzuca użytkownika z serwera.
!ban @user: Banowanie użytkownika na serwerze.
!clear <typ kanału>: Usuwa wszystkie kanały danego typu.
!clean [ilość]: Usuwa wiadomości w bieżącym kanale.
!delete_voice_channel <nazwa>: Usuwa kanał głosowy o podanej nazwie.
!delete_text_channel <nazwa>: Usuwa kanał tekstowy o podanej nazwie.
Komendy kalkulatora
!calc <wyrażenie>: Wykonuje obliczenia matematyczne (np. !calc 2 + 2, !calc sqrt(16)).
!binary <liczba>: Konwertuje między systemem dziesiętnym a dwójkowym (np. !binary 10, !binary 0b1010).
!hex <liczba>: Konwertuje między systemem dziesiętnym a szesnastkowym (np. !hex 255, !hex 0xFF).



✅ Funkcje bota
•	 Integracje API: Steam, Epic Games Store
•	 Muzyka: odtwarzanie z YouTube
•	 Moderacja: ban, mute, czyszczenie wiadomości
•	 Baza danych: oparta na SQLite (bez potrzeby serwera)
•	 Architektura modularna: łatwa rozbudowa
•	 Automatyczne ładowanie modułów
•	 Bezpieczne przechowywanie danych (tokeny itp.)
•	 Kalkulator matematyczny: podstawowe operacje, funkcje matematyczne, konwersje systemów liczbowych
