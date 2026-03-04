# Installation & Inbetriebnahme

Leadify basiert auf einer klar getrennten Drei-Schichten-Architektur bestehend aus Frontend, Backend und Datenbank.
Für einen erfolgreichen Start muss zunächst die Datenbank eingerichtet und anschließend der Backend-Server gestartet werden, bevor die Anwendung genutzt werden kann.

---

## Voraussetzungen

| Komponente | Mindestversion |
|---|---|
| Python | 3.10+ |
| Git | beliebig |
| SQL-Datenbank | MySQL 8.0+ / MariaDB 10.6+ |

---

## Schritt 1 – Repository beziehen

Klonen Sie das Leadify-Repository auf Ihren lokalen Rechner:

```bash
git clone https://github.com/LeadManagementApp-School/Leadify.git
cd Leadify
```

Alternativ kann das Repository als ZIP-Datei heruntergeladen und anschließend entpackt werden.

---

## Schritt 2 – Abhängigkeiten installieren

Leadify verwendet ein Python-Backend mit definierten Projektabhängigkeiten, die in der `pyproject.toml` hinterlegt sind.
Installieren Sie alle Pakete innerhalb einer virtuellen Umgebung:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

=== "via requirements.txt"

    ```bash
    pip install -r requirements.txt
    ```

=== "via pyproject.toml"

    ```bash
    pip install .
    ```

---

## Schritt 3 – Datenbank einrichten

Leadify speichert alle Daten in einer SQL-Datenbank. Importieren Sie die mitgelieferte Datenbankdatei in Ihr Datenbanksystem und stellen Sie sicher, dass der Datenbankserver aktiv und erreichbar ist.

👉 [Leadify SQL Herunterladen](#)

---

## Schritt 4 – Umgebungsvariablen konfigurieren

Im Repository befindet sich eine Vorlagedatei `db_config_example.env`. Benennen Sie diese in `db_config.env` um und tragen Sie Ihre Datenbankzugangsdaten ein:

```bash
cp db_config_example.env db_config.env
```

Öffnen Sie anschließend `db_config.env` und passen Sie die Werte entsprechend an:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=leadify
DB_USER=ihr_benutzername
DB_PASSWORD=ihr_passwort
```

---

## Schritt 5 – Backend-Server starten

Starten Sie das Backend mit folgendem Befehl:

```bash
uvicorn api.api_main:app --host 0.0.0.0 --port 8000 --reload
```

| Parameter | Beschreibung |
|---|---|
| `--host 0.0.0.0` | Server ist im lokalen Netzwerk erreichbar |
| `--port 8000` | Standardport der API |
| `--reload` | Automatischer Neustart bei Codeänderungen (nur Entwicklung) |

Nach erfolgreichem Start ist die API unter folgender Adresse erreichbar:

```
http://SERVER-IP:8000
```

!!! warning "Produktionsumgebung"
    Der Parameter `--reload` ist ausschließlich für die Entwicklung vorgesehen. Für den produktiven Einsatz wird ein geeigneter Deployment-Ansatz empfohlen – z. B. mit Reverse Proxy, SSL-Zertifikat und einem Prozessmanager wie `systemd` oder `supervisor`.

---

## Schritt 6 – Desktop-Anwendung starten

Sobald das Backend aktiv ist, kann die Desktop-Anwendung gestartet werden:

```bash
python main.py
```

Beim ersten Start der Anwendung wird eine **Server-IP-Adresse** abgefragt. Geben Sie hier die IP-Adresse ein, auf der das Backend erreichbar ist. (z. B. die IP-Adresse des Rechners)

---

## Schritt 7 – Mobile Anwendung einrichten

=== "Android"

    Laden Sie die bereitgestellte `.apk`-Datei herunter und installieren Sie sie auf Ihrem Android-Gerät.

    👉 [APK-Datei herunterladen](#)

=== "iOS"

    Laden Sie die bereitgestellte `.ipa`-Datei herunter und installieren Sie sie auf Ihrem iOS-Gerät.

    👉 [iOS-App herunterladen](#)

Beim ersten Start wird wieder die **Server-IP-Adresse** abgefragt. Geben Sie hier die IP-Adresse des Rechners ein, auf dem das Backend läuft (z. B. `192.168.178.25`).

Ihre lokale IP-Adresse ermitteln Sie mit:

```bash
ipconfig      # Windows
ifconfig      # macOS / Linux
```

!!! info "Netzwerkvoraussetzungen"
    Damit die mobile Anwendung mit dem Backend kommunizieren kann, muss eine der folgenden Bedingungen erfüllt sein:

    - Mobilgerät und Backend-Server befinden sich im **selben WLAN**
    - Es besteht eine aktive **VPN-Verbindung** zwischen Gerät und Server
    - Das Backend ist **öffentlich gehostet** und über das Internet erreichbar

---

Nach erfolgreicher Konfiguration wird der Registrierungs- bzw. Login-Bildschirm von Leadify geladen.
