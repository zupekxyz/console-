import os
import sys
from ping3 import ping
import pyfiglet
from colorama import Fore, Style
from flask import Flask, request, send_from_directory, render_template_string
import threading
import requests
from bs4 import BeautifulSoup
import random

# Przechowywanie zmiennych
variables = {}

def print_banner():
    banner = pyfiglet.figlet_format("Console")
    print(Fore.RED + banner + Style.RESET_ALL)
    print(Fore.YELLOW + "Witaj w mojej konsoli! Wpisz -help, aby zobaczyć dostępne polecenia." + Style.RESET_ALL)

def show_help():
    help_text = """
    Dostępne polecenia:
    -help                 Wyświetla tę pomoc.
    -ping [host]          Sprawdza ping dla podanego hosta (np. -ping google.com).
    -browser connect      Tworzy tymczasową stronę internetową dostępną przez 5 minut.
    -browser connect off  Wyłącza uruchomioną tymczasową stronę internetową.
    -browser create scan  Tworzy stronę 1:1 z zeskanowanej strony.
    -scan [url]           Pobiera zasoby strony internetowej i zapisuje je lokalnie.
    -exit                 Wyjście z konsoli.
    -vars                 Wyświetla zapisane zmienne.
    """
    print(Fore.CYAN + help_text + Style.RESET_ALL)

def ping_host(host):
    try:
        result = ping(host, timeout=2)  # Mierzy czas odpowiedzi (w sekundach)
        if result:
            print(Fore.GREEN + f"Ping do {host}: {round(result * 1000, 2)} ms" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Nie można uzyskać odpowiedzi od {host}." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Błąd podczas pingu: {e}" + Style.RESET_ALL)

scan_logs = []

def start_temporary_server():
    app = Flask(__name__)
    visitors = []

    @app.route('/', methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            # Przechwytywanie danych z formularzy
            form_data = request.form
            for key, value in form_data.items():
                print(Fore.GREEN + f"Zmienna {key} = {value}" + Style.RESET_ALL)

        user_agent = request.headers.get('User-Agent', 'Nieznany')
        ip_address = request.remote_addr

        # Geolocation Mockup
        city = "Unknown City"  # Można zintegrować z usługą lokalizacji IP

        log_entry = {
            "ip": ip_address,
            "city": city,
            "device": "Telefon" if "Mobile" in user_agent else "PC" if "Windows" in user_agent or "Mac" in user_agent else "Other"
        }
        print(Fore.GREEN + f"Odwiedzający: {log_entry}" + Style.RESET_ALL)

        # HTML z formularzem i JavaScript do przechwytywania kliknięć
        html_content = """
        <html>
        <body>
        <form method="POST">
            <label for="username">Nazwa użytkownika:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Hasło:</label><br>
            <input type="password" id="password" name="password"><br><br>
            <input type="checkbox" id="remember" name="remember">
            <label for="remember">Zapamiętaj mnie</label><br><br>
            <button type="submit">Zaloguj się</button>
        </form>
        <button id="other-button">Kliknij mnie!</button>

        <script>
        // Przechwytywanie kliknięć i formularzy
        document.getElementById("other-button").onclick = function() {
            console.log("Kliknięto przycisk inny niż formularz.");
            let newUrl = window.location.href.slice(0, -1) + String.fromCharCode(Math.random() * (122 - 97) + 97);  // Modyfikacja URL
            window.location.href = newUrl;  // Zmieniamy URL
        };
        </script>
        </body>
        </html>
        """
        return render_template_string(html_content), 200

    def run_server():
        print(Fore.GREEN + "Serwer uruchomiony pod adresem: http://127.0.0.1:5001" + Style.RESET_ALL)
        app.run(host='0.0.0.0', port=5001)

    global server_thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

def stop_temporary_server():
    global server_thread
    if server_thread and server_thread.is_alive():
        print(Fore.YELLOW + "Zamykanie serwera..." + Style.RESET_ALL)
        server_thread.join()
    else:
        print(Fore.RED + "Serwer nie jest uruchomiony." + Style.RESET_ALL)

def scan_website(url):
    try:
        print(Fore.CYAN + f"Rozpoczynam skanowanie strony: {url}" + Style.RESET_ALL)
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Tworzenie folderu
        folder_name = "scanned_site"
        os.makedirs(folder_name, exist_ok=True)

        # Zapis głównego HTML
        with open(os.path.join(folder_name, "index.html"), "w", encoding="utf-8") as file:
            file.write(response.text)

        # Pobieranie zasobów (style, obrazy, skrypty)
        resources = []

        for tag in soup.find_all(['link', 'script', 'img', 'form', 'button']):
            attr = 'src' if tag.name in ['script', 'img'] else 'href' if tag.name == 'link' else None
            if tag.name == "form":
                resources.append({"type": "form", "action": tag.get("action")})
            elif tag.name == "button":
                resources.append({"type": "button", "text": tag.get_text()})
            if tag.has_attr(attr):
                resources.append(tag[attr])

        for resource in resources:
            print(Fore.GREEN + f"Pobrano zasób: {resource}" + Style.RESET_ALL)

        print(Fore.GREEN + f"Skanowanie zakończone. Pliki zapisano w folderze: {folder_name}" + Style.RESET_ALL)

        # Zapis do logów
        global scan_logs
        scan_logs.append({
            "url": url,
            "resources": resources
        })

    except Exception as e:
        print(Fore.RED + f"Błąd podczas skanowania strony: {e}" + Style.RESET_ALL)

def browser_connect():
    print(Fore.CYAN + "Uruchamiam tymczasowy serwer WWW..." + Style.RESET_ALL)
    threading.Thread(target=start_temporary_server, daemon=True).start()

def browser_create_scan():
    global scan_logs

    if not scan_logs:
        print(Fore.RED + "Brak zapisanych logów ze skanowania." + Style.RESET_ALL)
        return

    # Ścieżka do folderu z zeskanowaną stroną
    folder_name = "scanned_site"

    # Flask - uruchamiamy serwer, który serwuje skopiowane pliki strony
    app = Flask(__name__)

    # Przyjmujemy wszystkie zasoby statyczne (CSS, JS, obrazy)
    @app.route('/<path:filename>')
    def serve_file(filename):
        return send_from_directory(folder_name, filename)

    @app.route('/')
    def home():
        user_agent = request.headers.get('User-Agent', 'Nieznany')
        ip_address = request.remote_addr

        # Geolocation Mockup
        city = "Unknown City"  # Można zintegrować z usługą lokalizacji IP

        log_entry = {
            "ip": ip_address,
            "city": city,
            "device": "Telefon" if "Mobile" in user_agent else "PC" if "Windows" in user_agent or "Mac" in user_agent else "Other"
        }

        print(Fore.GREEN + f"Odwiedzający: {log_entry}" + Style.RESET_ALL)

        # Załaduj oryginalny plik HTML
        with open(os.path.join(folder_name, "index.html"), 'r', encoding="utf-8") as file:
            html_content = file.read()

        # Zmodyfikuj HTML, aby pokazywał IP i urządzenie
        html_content = html_content.replace("</body>", f"<p>IP: {log_entry['ip']}</p><p>Urządzenie: {log_entry['device']}</p></body>")
        return html_content

    def run_server():
        print(Fore.GREEN + f"Serwer uruchomiony pod adresem: http://127.0.0.1:5001" + Style.RESET_ALL)
        app.run(host='0.0.0.0', port=5001)

    threading.Thread(target=run_server, daemon=True).start()

def save_variable(var_name, value):
    global variables
    variables[var_name] = value
    print(Fore.GREEN + f"Zmienna {var_name} została zapisana: {value}" + Style.RESET_ALL)

def show_variables():
    global variables
    if variables:
        for name, value in variables.items():
            print(Fore.GREEN + f"{name} = {value}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Brak zapisanych zmiennych." + Style.RESET_ALL)

def main():
    print_banner()

    while True:
        try:
            user_input = input(Fore.BLUE + "<< " + Style.RESET_ALL).strip()
            if not user_input:
                continue

            if user_input == "-help":
                show_help()

            elif user_input.startswith("-ping"):
                parts = user_input.split()
                if len(parts) == 2:
                    host = parts[1]
                    ping_host(host)
                else:
                    print(Fore.RED + "Podaj host do pingu, np. -ping google.com" + Style.RESET_ALL)

            elif user_input == "-browser connect":
                browser_connect()

            elif user_input == "-browser connect off":
                stop_temporary_server()

            elif user_input == "-browser create scan":
                browser_create_scan()

            elif user_input.startswith("-scan"):
                parts = user_input.split()
                if len(parts) == 2:
                    url = parts[1]
                    scan_website(url)
                else:
                    print(Fore.RED + "Podaj adres URL do skanowania, np. -scan https://example.com" + Style.RESET_ALL)

            elif user_input.startswith("-vars"):
                show_variables()

            elif "=" in user_input:
                var_name, value = user_input.split("=", 1)
                var_name = var_name.strip()
                value = value.strip()
                save_variable(var_name, value)

            elif user_input == "-exit":
                print(Fore.YELLOW + "Zamykanie konsoli..." + Style.RESET_ALL)
                break

            else:
                print(Fore.RED + f"Nieznane polecenie: {user_input}. Wpisz -help, aby zobaczyć listę komend." + Style.RESET_ALL)

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nZamykanie konsoli..." + Style.RESET_ALL)
            break

if __name__ == "__main__":
    main()
