# Praxisbeispiel: Lead-Status Modul

> **Modul:** `lead_status`  
> **Schicht:** Frontend · API · Backend  
> **Zweck:** Ermöglicht dem Erfasser, den Status seiner eigenen Leads einzusehen, Details abzurufen, Kommentare zu bearbeiten und Leads zum Löschen vorzumerken.

---

## Architekturübersicht

Das Modul folgt dem **3-Schichten-Modell**, das im gesamten Projekt durchgängig verwendet wird:

```
┌─────────────────────────────────────┐
│         PRÄSENTATIONSSCHICHT     │
│         LeadStatusView (Flet)    │  ← frontend/lead_status_view.py
└────────────────┬────────────────────┘
                 │ HTTP (REST)
┌────────────────▼────────────────────┐
│           API-SCHICHT            │
│      FastAPI – /api/lead-status  │  ← api/api_routes.py
└────────────────┬────────────────────┘
                 │ Python-Methodenaufruf
┌────────────────▼────────────────────┐
│          LOGIK- & DATENSCHICHT   │
│  LeadStatusManager + Lead-Model  │  ← backend/lead_status_manager.py
│          MariaDB-Datenbank       │
└─────────────────────────────────────┘
```

| Schicht | Datei | Verantwortlichkeit |
|---|---|---|
| Präsentation | `frontend/lead_status_view.py` | GUI-Aufbau, Benutzerinteraktion |
| API | `api/api_routes.py` (ab Zeile 635) | HTTP-Endpunkte, Request-Validierung |
| Logik/Daten | `backend/lead_status_manager.py` | Geschäftslogik, SQL-Abfragen |

---

## Datenmodell – Klasse `Lead`

**Datei:** `backend/lead_status_manager.py`

Die Klasse `Lead` ist ein einfaches Datenobjekt (*Model*), das eine Datenbankzeile als Python-Objekt kapselt. Sie wird von `LeadStatusManager`-Methoden befüllt und zurückgegeben.

### Attribute

| Attribut | Typ | Quelle | Beschreibung |
|---|---|---|---|
| `lead_id` | `int` | Tabelle `lead` | Primärschlüssel des Leads |
| `datum_erfasst` | `datetime` | Tabelle `lead` | Erfassungszeitpunkt |
| `status_id` | `int` | Tabelle `lead` | Numerischer Statusschlüssel (1–5) |
| `bearbeiter_id` | `int` | Tabelle `lead` | FK → Tabelle `benutzer` |
| `erfasser_id` | `int` | Tabelle `lead` | FK → Tabelle `benutzer` |
| `kunde_name` | `str` | JOIN `firma` | Anzeigename des Kunden |
| `produkt_name` | `str` | JOIN `produkte` | Bezeichnung des Produkts |
| `status_name` | `str` | JOIN `status` | Lesbarer Statustext |
| `bearbeiter_name` | `str` | JOIN `benutzer` | Vor- und Nachname des Bearbeiters |

### Statuswerte

| `status_id` | `status_name` | Bedeutung |
|---|---|---|
| `1` | Offen | Lead wurde erstellt, wartet auf Bearbeitung |
| `2` | In Bearbeitung | Lead wird aktiv bearbeitet |
| `3` | Erledigt | Lead wurde abgeschlossen |
| `4` | Abgelehnt | Lead wurde vom Bearbeiter abgelehnt |
| `5` | Angebot erstellt | Ein Angebot wurde generiert |

---

## Backend – Klasse `LeadStatusManager`

**Datei:** `backend/lead_status_manager.py`

Zentrale Manager-Klasse für alle Lead-Status-Operationen. Nimmt im Konstruktor eine `Database`-Instanz entgegen und kapselt sämtliche SQL-Abfragen.

```python
manager = LeadStatusManager(db: Database)
```

### Methoden

---

#### `get_my_created_leads(erfasser_id)`

Gibt alle Leads zurück, die der angegebene Benutzer erfasst hat.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `erfasser_id` | `int` | ID des eingeloggten Benutzers |

**Rückgabe:** `list[Lead]` – Liste von Lead-Objekten, sortiert nach Erfassungsdatum (neueste zuerst). Leere Liste, wenn keine Leads vorhanden.

> Führt einen JOIN über `ansprechpartner`, `firma`, `produkte`, `status` und `benutzer` durch, um alle Anzeigefelder in einem einzigen Datenbankaufruf zu laden.

---

#### `get_lead_by_id(lead_id)`

Gibt einen einzelnen Lead mit vollständigen Detailinformationen zurück.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `lead_id` | `int` | Primärschlüssel des gesuchten Leads |

**Rückgabe:** `dict | None` – Rohdaten-Dictionary aus der Datenbank, oder `None` wenn nicht gefunden.

> Enthält erweiterte JOIN-Felder wie `ansprechpartner_name`, `kunde_email`, `produktgruppe_name`, `produktzustand_name` und `quelle_name`.

---

#### `get_lead_aktionen(lead_id)`

Gibt den vollständigen Aktivitätsverlauf eines Leads zurück, ohne interne `lead_angesehen`-Einträge.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `lead_id` | `int` | ID des Leads |

**Rückgabe:** `list[dict]` – Liste von Aktions-Einträgen, sortiert nach Zeitstempel absteigend. Jede Aktion enthält `benutzer_name` und `ziel_name`.

---

#### `get_lead_kommentare(lead_id)`

Gibt alle Kommentare zu einem Lead zurück.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `lead_id` | `int` | ID des Leads |

**Rückgabe:** `list[dict]` – Liste der Kommentare, sortiert nach Datum aufsteigend.

---

#### `update_kommentar(kommentar_id, new_text)`

Aktualisiert den Text eines bestehenden Kommentars und setzt das Datum auf den aktuellen Zeitpunkt.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `kommentar_id` | `int` | ID des zu ändernden Kommentars |
| `new_text` | `str` | Neuer Kommentartext |

**Rückgabe:** Ergebnis der Datenbankoperation oder `None` bei Fehler.

---

#### `has_recent_action(lead_id, erfasser_id=None)`

Prüft, ob ein Lead in den letzten 24 Stunden eine neue, noch nicht gesehene Aktion erhalten hat.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `lead_id` | `int` | ID des Leads |
| `erfasser_id` | `int \| None` | Wenn übergeben, wird der "zuletzt gesehen"-Zeitstempel des Benutzers berücksichtigt |

**Rückgabe:** `bool` – `True` wenn ungesehene Aktionen vorhanden sind.

> Aktionen vom Typ `zum Löschen vorgemerkt` und `lead_angesehen` werden bei dieser Prüfung ignoriert.

---

#### `mark_lead_as_viewed(lead_id, benutzer_id)`

Markiert einen Lead als vom Benutzer angesehen. Löscht vorherige `lead_angesehen`-Einträge dieses Benutzers für diesen Lead und fügt einen neuen ein.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `lead_id` | `int` | ID des Leads |
| `benutzer_id` | `int` | ID des Benutzers |

**Rückgabe:** Kein Rückgabewert.

---

#### `get_last_action_type(lead_id)`

Gibt den Typ der zuletzt eingetragenen Aktion zurück.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `lead_id` | `int` | ID des Leads |

**Rückgabe:** `str | None` – z. B. `"angenommen"`, `"abgelehnt"`, `"zum Löschen vorgemerkt"`.

---

#### `mark_lead_for_deletion(lead_id, benutzer_id, kommentar=None)`

Markiert einen Lead zum Löschen. Führt vor der Aktion drei Validierungen durch:

1. Lead muss existieren
2. Der aufrufende Benutzer muss der Erfasser sein
3. Der Lead-Status muss `Offen` (`status_id = 1`) sein

| Parameter | Typ | Beschreibung |
|---|---|---|
| `lead_id` | `int` | ID des Leads |
| `benutzer_id` | `int` | ID des anfragenden Benutzers |
| `kommentar` | `str \| None` | Optionaler Begründungstext |

**Rückgabe:** `tuple[bool, str]` – Erfolgsstatus und lesbare Statusmeldung.

| Rückgabe | Bedeutung |
|---|---|
| `(True, "Lead wurde erfolgreich...")` | Vorgemerkt |
| `(False, "Lead nicht gefunden")` | Lead-ID ungültig |
| `(False, "Sie können nur Ihre eigenen...")` | Kein Erfasser |
| `(False, "Nur offene Leads können...")` | Falscher Status |
| `(False, "Lead ist bereits...")` | Doppelte Vormerkung |

---

#### `is_lead_marked_for_deletion(lead_id)`

Prüft ob ein Lead bereits zum Löschen vorgemerkt ist.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `lead_id` | `int` | ID des Leads |

**Rückgabe:** `bool`

---

#### `get_count_marked_for_deletion()`

Gibt die Gesamtanzahl aller aktuell zum Löschen vorgemerkten Leads zurück.

**Rückgabe:** `int`

---

## API-Schicht – Endpunkte `/api/lead-status`

**Datei:** `api/api_routes.py`  
**Router-Prefix:** `/api/lead-status`  
**Tag:** `Lead-Status`

Die FastAPI-Routen bilden die Brücke zwischen Frontend und Backend. Alle Endpunkte instanziieren intern den `LeadStatusManager` und delegieren die Verarbeitung an diesen.

### Request-Modelle (Pydantic)

```python
class UpdateKommentarRequest(BaseModel):
    new_text: str

class MarkForDeletionRequest(BaseModel):
    benutzer_id: int
    kommentar: Optional[str] = None

class MarkViewedRequest(BaseModel):
    benutzer_id: int
```

### Endpunktübersicht

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/api/lead-status/my/{erfasser_id}` | Alle eigenen Leads des Erfassers |
| `GET` | `/api/lead-status/{lead_id}` | Detailansicht eines Leads |
| `GET` | `/api/lead-status/{lead_id}/aktionen` | Aktivitätsverlauf eines Leads |
| `GET` | `/api/lead-status/{lead_id}/kommentare` | Kommentare zu einem Lead |
| `PUT` | `/api/lead-status/kommentar/{kommentar_id}` | Kommentar aktualisieren |
| `GET` | `/api/lead-status/{lead_id}/has-recent-action` | Ungesehene Aktionen prüfen |
| `POST` | `/api/lead-status/{lead_id}/mark-viewed` | Lead als gesehen markieren |
| `POST` | `/api/lead-status/{lead_id}/mark-for-deletion` | Lead zum Löschen vormerken |
| `GET` | `/api/lead-status/{lead_id}/is-marked-for-deletion` | Lösch-Vormerkung prüfen |
| `GET` | `/api/lead-status/marked-for-deletion/count` | Anzahl vorgemerkter Leads |
| `GET` | `/api/lead-status/{lead_id}/last-action-type` | Letzten Aktionstyp abrufen |

### Endpunkte im Detail

---

#### `GET /api/lead-status/my/{erfasser_id}`

Gibt alle Leads zurück, die vom angegebenen Benutzer erfasst wurden.

**Pfadparameter:** `erfasser_id: int`

**Antwort:**
```json
[
  {
    "lead_id": 42,
    "kunde_name": "Musterfirma GmbH",
    "produkt_name": "Produkt A",
    "status_name": "Offen",
    "status_id": 1,
    "datum_erfasst": "2024-01-15T09:30:00",
    "bearbeiter_name": "Max Mustermann"
  }
]
```

---

#### `GET /api/lead-status/{lead_id}`

Gibt die vollständigen Detaildaten eines Leads zurück.

**Pfadparameter:** `lead_id: int`

**Fehler:** `404` wenn Lead nicht gefunden.

---

#### `GET /api/lead-status/{lead_id}/aktionen`

Gibt den Aktivitätsverlauf eines Leads zurück (ohne `lead_angesehen`-Einträge).

**Pfadparameter:** `lead_id: int`

---

#### `GET /api/lead-status/{lead_id}/kommentare`

Gibt alle Kommentare zu einem Lead zurück.

**Pfadparameter:** `lead_id: int`

---

#### `PUT /api/lead-status/kommentar/{kommentar_id}`

Aktualisiert den Text eines bestehenden Kommentars.

**Pfadparameter:** `kommentar_id: int`

**Request Body:**
```json
{ "new_text": "Aktualisierter Kommentartext" }
```

**Antwort:**
```json
{ "success": true }
```

---

#### `GET /api/lead-status/{lead_id}/has-recent-action`

Prüft ob ein Lead in den letzten 24 Stunden ungesehene Aktivität hat.

**Pfadparameter:** `lead_id: int`  
**Query-Parameter:** `erfasser_id: int` (optional)

**Antwort:**
```json
{ "has_update": true }
```

---

#### `POST /api/lead-status/{lead_id}/mark-viewed`

Markiert einen Lead als vom Benutzer gesehen.

**Pfadparameter:** `lead_id: int`

**Request Body:**
```json
{ "benutzer_id": 7 }
```

**Antwort:**
```json
{ "success": true }
```

---

#### `POST /api/lead-status/{lead_id}/mark-for-deletion`

Markiert einen Lead zum Löschen (nur Erfasser, nur offene Leads).

**Pfadparameter:** `lead_id: int`

**Request Body:**
```json
{
  "benutzer_id": 7,
  "kommentar": "Nicht mehr benötigt"
}
```

**Antwort:**
```json
{ "success": true, "message": "Lead wurde erfolgreich zum Löschen vorgemerkt" }
```

---

#### `GET /api/lead-status/{lead_id}/is-marked-for-deletion`

**Antwort:**
```json
{ "is_marked": false }
```

---

#### `GET /api/lead-status/marked-for-deletion/count`

**Antwort:**
```json
{ "count": 3 }
```

---

#### `GET /api/lead-status/{lead_id}/last-action-type`

**Antwort:**
```json
{ "aktion_typ": "angenommen" }
```

---

## Frontend – Klasse `LeadStatusView`

**Datei:** `frontend/lead_status_view.py`  
**Framework:** Flet

Präsentationsklasse, die die Lead-Status-Oberfläche aufbaut. Kommuniziert ausschließlich über den `LeadStatusClient` mit der API – kein direkter Backend-Zugriff.

```python
view = LeadStatusView(
    page: ft.Page,
    lead_manager: LeadStatusClient,
    current_user: dict
)
```

### Methoden

| Methode | Beschreibung |
|---|---|
| `render()` | Hauptmethode – baut die gesamte Listenansicht neu auf |
| `_build_filter_dropdown()` | Erstellt das Status-Filter-Dropdown |
| `_create_lead_card(lead)` | Rendert eine einzelne Lead-Karte mit Status-Badge |
| `_show_lead_details(lead)` | Wechselt zur Detailansicht (`LeadDetailViewStatus`) |
| `_go_back_to_menu()` | Navigiert zurück zum Hauptmenü via `AppController` |

### Klasse `LeadDetailViewStatus`

Detailansicht für einen einzelnen Lead. Wird von `LeadStatusView._show_lead_details()` aufgerufen.

| Methode | Beschreibung |
|---|---|
| `render()` | Baut die vollständige Detailseite auf |
| `_build_aktion_section()` | Rendert den Aktivitätsverlauf |
| `_build_kommentar_section()` | Rendert Kommentare mit optionalem Bearbeiten-Button |
| `_edit_kommentar(kommentar)` | Öffnet Bearbeitungs-Dialog für einen Kommentar |
| `_mark_for_deletion()` | Öffnet Bestätigungs-Dialog für Lösch-Vormerkung |
| `_go_back()` | Navigiert zurück zur Lead-Liste |

### Status-Farben (UI)

| `status_id` | Farbe | Flet-Konstante |
|---|---|---|
| `1` – Offen | Grün | `ft.Colors.GREEN` |
| `2` – In Bearbeitung | Orange | `ft.Colors.ORANGE` |
| `3` – Erledigt | Dunkelgrau | `ft.Colors.GREY_700` |
| `4` – Abgelehnt | Rot | `ft.Colors.RED` |
| `5` – Angebot erstellt | Blau | `ft.Colors.BLUE_400` |

---

## Abhängigkeiten

```
LeadStatusView
    └── LeadStatusClient        (API-Client, HTTP-Wrapper)
            └── FastAPI Router  (/api/lead-status/*)
                    └── LeadStatusManager
                            └── Database (MariaDB Singleton)
```

Der `AppController` setzt die `app_controller`-Referenz in der View nach der Initialisierung, um Navigation zwischen Views zu ermöglichen.
