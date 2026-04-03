# Technische Strategie

> Dieser Abschnitt beschreibt die methodischen Entscheidungen hinter dem Technologie-Stack von Leadify,
> begründet die Wahl der eingesetzten Frameworks und Bibliotheken und dokumentiert konkrete
> Herausforderungen sowie die entwickelten Lösungsansätze.

---

## 1. Technologie-Stack

| Komponente | Technologie | Einsatzbereich |
|---|---|---|
| Frontend / GUI | Flet (Python) | Benutzeroberfläche, Desktop & Android |
| API-Schicht | FastAPI (Python) | HTTP-Schnittstelle zwischen Frontend und Backend |
| Backend / Logik | Python (Manager-Klassen) | Geschäftslogik, Validierung, Datenbankzugriff |
| Datenbank | MariaDB | Relationale Datenspeicherung |
| DB-Verwaltung | phpMyAdmin | Administrationswerkzeug für die Datenbank |
| Authentifizierung | Token-basiert (eigene Implementierung) | Login, Auto-Login, Geräteverwaltung |
| Deployment (Entwicklung) | Lokaler Server + Tailscale (VPN) | Erreichbarkeit der API für mobile Endgeräte |

---

## 2. Begründung der Technologiewahl

### 2.1 Flet – Frontend-Framework

**Eingesetzt für:** Aufbau der gesamten Benutzeroberfläche (Desktop und Android)

Flet wurde als Frontend-Framework gewählt, da es auf Python basiert und damit die im Unterricht
erworbenen Kenntnisse direkt nutzbar waren. Ein entscheidender Faktor war darüber hinaus,
dass Flet die Kompilierung einer nativen Android-Anwendung aus einer einzigen Python-Codebasis
ermöglicht – ohne eine zweite Programmiersprache erlernen zu müssen. Da die Entwicklung einer
mobilen Anwendung von Anfang an eine zentrale Anforderung des Projekts darstellte, war dies
ausschlaggebend für die Entscheidung.

**Abwägung gegenüber Alternativen:**

| Kriterium | Flet | Flutter | React Native |
|---|---|---|---|
| Sprache | Python (bekannt) | Dart (unbekannt) | JavaScript (unbekannt) |
| Mobile-Unterstützung | ✓ Android/iOS | ✓ vollständig | ✓ vollständig |
| Einarbeitungsaufwand | gering | hoch | hoch |
| Python-Integration | nativ | nicht möglich | nicht möglich |
| Community / Reife | wachsend | etabliert | etabliert |

Flutter und React Native schieden aus, da beide vollständig fremde Programmiersprachen erfordern
(Dart bzw. JavaScript), was den Einarbeitungsaufwand im Rahmen des Projektzeitraums erheblich
erhöht hätte. Flet ermöglichte eine direkte Weiterverwendung der vorhandenen Python-Kenntnisse.

**Bewertung nach Projektanforderungen:**

- **Wartbarkeit:** Frontend und Backend teilen dieselbe Sprache (Python), was die Codebasis
  einheitlich und einfacher wartbar macht.
- **Skalierbarkeit:** Flet eignet sich gut für mittelgroße Anwendungen; bei sehr hoher Nutzerzahl
  oder komplexen Animationen stoßen Flutter oder native Ansätze schneller an Grenzen.
- **Performance:** Für den geplanten Einsatzbereich (internes CRM-Tool) ausreichend. Komplexe
  Renderoperationen wurden bewusst vermieden.

---

### 2.2 FastAPI – API-Schicht

**Eingesetzt für:** HTTP-Schnittstelle zwischen Frontend und Backend

FastAPI wurde verhältnismäßig spät im Projektverlauf eingeführt – erst gegen Ende der
Entwicklungszeit, als die Portierung der Anwendung auf Android in Angriff genommen wurde.
Die Entscheidung folgte dabei einer bewussten Priorisierung: Zunächst sollte sichergestellt
werden, dass die Anwendung auf dem Desktop stabil läuft und alle Funktionen vollständig
implementiert sind. Erst danach wurde die mobile Nutzung als nächster Schritt angegangen,
was das Architekturrefactoring und die Einführung von FastAPI als Kommunikationsschicht
nach sich zog (siehe auch [Abschnitt 3.2](#32-architekturrefactoring-und-mobile-erreichbarkeit)).

FastAPI wurde dabei als API-Framework gewählt, da es sich durch hohe Performance, automatische
Datenvalidierung über Pydantic-Modelle und eine sehr übersichtliche Entwicklererfahrung auszeichnet.
Besonders relevant war die native Unterstützung von asynchronen Anfragen, was die
Reaktionsfähigkeit der mobilen Anwendung verbessert.

**Abwägung gegenüber Alternativen:**

| Kriterium | FastAPI | Flask |
|---|---|---|
| Performance | sehr hoch (ASGI) | mittel (WSGI) |
| Datenvalidierung | automatisch (Pydantic) | manuell |
| Dokumentation (Swagger) | automatisch generiert | nur mit Erweiterungen |
| Async-Unterstützung | nativ | eingeschränkt |
| Einarbeitungsaufwand | gering | sehr gering |
| Verbreitung im Unterricht | gering | gering |

Flask wäre eine naheliegende Alternative gewesen, da es noch einfacher zu starten ist.
Allerdings fehlen Flask die automatische Validierung und die integrierte API-Dokumentation,
die FastAPI über Swagger UI automatisch bereitstellt – ein Vorteil, der die Entwicklung
und das Debugging spürbar beschleunigte. Die Performance-Vorteile durch das ASGI-Protokoll
kommen insbesondere bei der mobilen Nutzung zum Tragen.

**Bewertung nach Projektanforderungen:**

- **Wartbarkeit:** Pydantic-Modelle erzwingen klare Datenstrukturen und machen Schnittstellen
  explizit dokumentiert.
- **Skalierbarkeit:** FastAPI ist für deutlich größere Lasten ausgelegt als im aktuellen Projekt
  benötigt – bietet damit Spielraum für zukünftige Erweiterungen.
- **Performance:** Einer der schnellsten Python-Web-Frameworks; für mobile Anfragen mit
  geringer Latenz gut geeignet.

---

### 2.3 MariaDB – Datenbank

**Eingesetzt für:** Persistente, relationale Datenspeicherung

MariaDB wurde gewählt, da relationale Datenbanken bereits im ersten Schuljahr Teil des Unterrichts
waren und grundlegende SQL-Kenntnisse vorhanden waren. Die relationale Struktur eignet sich
für das Datenmodell von Leadify sehr gut, da zwischen Leads, Benutzern, Firmen, Produkten
und Aktionen viele Beziehungen bestehen, die über JOINs effizient abgefragt werden können.

**Abwägung gegenüber Alternativen:**

| Kriterium | MariaDB | SQLite | PostgreSQL |
|---|---|---|---|
| Vorwissen vorhanden | ✓ | teilweise | ✗ |
| Mehrbenutzer-fähig | ✓ | eingeschränkt | ✓ |
| Netzwerkzugriff | ✓ | ✗ (lokal) | ✓ |
| Setup-Aufwand | gering | minimal | mittel |
| Kostenlos | ✓ | ✓ | ✓ |
| Geeignet für mobile App | ✓ | ✗ | ✓ |

SQLite wurde als mögliche Alternative in Betracht gezogen, schied jedoch aus, da es keinen
echten Netzwerkzugriff unterstützt – ein K.O.-Kriterium für eine Anwendung, bei der mehrere
Benutzer gleichzeitig auf dieselbe Datenbank zugreifen und die mobile App über das Netzwerk
kommuniziert. PostgreSQL wäre eine leistungsfähige Alternative gewesen, allerdings war der
Setup-Aufwand und das fehlende Vorwissen ein Hinderungsgrund im gegebenen Zeitrahmen.

**Bewertung nach Projektanforderungen:**

- **Wartbarkeit:** Standardisiertes SQL; einfach zu verstehen, gut dokumentiert.
- **Skalierbarkeit:** Für den aktuellen Nutzungsumfang mehr als ausreichend. Bei sehr hohem
  Concurrent-Load wäre PostgreSQL performanter, was für dieses Projekt jedoch nicht relevant ist.
- **Performance:** Für die Abfragelast des Projekts (JOINs über wenige tausend Datensätze)
  vollständig ausreichend.

---

### 2.4 phpMyAdmin – Datenbankverwaltung

**Eingesetzt für:** Administration, Schemaentwicklung und manuelle Datenpflege

phpMyAdmin wurde als Verwaltungswerkzeug eingesetzt, da es ebenfalls aus dem Unterricht bekannt
war und einen einfachen grafischen Zugang zur Datenbank ohne zusätzliche Tools bietet. Es diente
vor allem in der Entwicklungsphase zur schnellen Überprüfung von Datenbankstrukturen und
Testdaten.

Alternativen wie DBeaver oder MySQL Workbench bieten mehr Funktionen für komplexe Datenbankarbeit,
waren aber für den Einsatzzweck (Schulprojekt, bekannte Umgebung) nicht notwendig.

---

### 2.5 Authentifizierung

**Eingesetzt für:** Benutzerverwaltung, Login, Auto-Login und Geräteerkennung

Die Authentifizierung wurde als eigene Implementierung über den `AuthManager` umgesetzt.
Token-basiertes Login ermöglicht Auto-Login auf bekannten Geräten über gespeicherte
Device-IDs und Tokens, ohne dass eine externe Authentifizierungsbibliothek (z. B. OAuth2)
benötigt wurde.

Für den Einsatzrahmen des Projekts – ein internes Tool mit überschaubarer Nutzerzahl – war
eine eigene, schlanke Implementierung wartbarer und transparenter als eine externe Lösung.
Bei einer späteren Öffnung der Anwendung nach außen wäre die Einführung von OAuth2 oder JWT
eine sinnvolle Erweiterung.

---

## 3. Herausforderungen & Lösungen

### 3.1 Lokale Datenbank – keine entwicklerübergreifende Synchronisation

**Problem:**  
In der frühen Entwicklungsphase lief die MariaDB-Datenbank ausschließlich lokal auf einem
einzelnen Rechner. Datenbankänderungen (neue Tabellen, Spalten, Testdaten) waren für andere
Teammitglieder nicht automatisch sichtbar. Jede Schemaänderung musste manuell kommuniziert
und auf allen Entwicklungsumgebungen nachgezogen werden.

**Lösung:**  
Die Datenbankstruktur wurde in SQL-Migrationsskripten festgehalten, sodass Änderungen
reproduzierbar waren. Für Tests wurde die Datenbank auf einem zentralen Gerät im lokalen
Netzwerk betrieben, auf das alle Teammitglieder zugreifen konnten.

**Reflexion:**  
Langfristig wäre ein gemeinsam gehosteter Entwicklungsserver (z. B. in der Cloud) die
sauberere Lösung. Im Projektrahmen war der gewählte Ansatz jedoch pragmatisch und ausreichend.

---

### 3.2 Architekturrefactoring und mobile Erreichbarkeit

Diese beiden Herausforderungen hängen direkt zusammen, da die Notwendigkeit des
Architekturrefactorings und die Frage der Erreichbarkeit für mobile Endgeräte denselben
Auslöser hatten: die Entscheidung, Leadify auf Android zu portieren.

**Problem – monolithische Architektur:**  
Zu Beginn des Projekts griff das Flet-Frontend direkt auf die Datenbank zu. Präsentationslogik
und Datenbankabfragen waren in denselben Klassen vermischt. Solange die Anwendung ausschließlich
auf dem Desktop lief, war dies funktional – die Stabilität und vollständige Implementierung
aller Features hatte in dieser Phase bewusst Vorrang. Erst als die Portierung auf Android
in Angriff genommen wurde, offenbarte sich die direkte Datenbankverbindung als K.O.-Kriterium:
Eine Android-App kann keine direkte MariaDB-Verbindung über das Netzwerk aufbauen.

**Problem – Erreichbarkeit für mobile Endgeräte:**  
Gleichzeitig stellte sich die Frage, wie die neu eingeführte FastAPI-Schicht während der
Testphase vom Smartphone aus erreichbar gemacht werden kann. Der Server lief lokal auf einem
Entwicklungsrechner, und eine einfache lokale IP-Adresse ist nur im selben WLAN-Netz erreichbar.

**Lösung:**  
Die Architektur wurde gezielt in ein Drei-Schichten-Modell überführt:

1. Das Frontend wurde auf reine Darstellungslogik reduziert (View-Klassen)
2. FastAPI wurde als Kommunikationsschicht eingeführt
3. Die Geschäftslogik wurde in Manager-Klassen im Backend ausgelagert

Für die Erreichbarkeit des lokalen Servers vom Smartphone aus wurde **Tailscale** eingesetzt –
ein VPN-Dienst, der alle verbundenen Geräte in ein gemeinsames virtuelles Netzwerk einbindet.
Dadurch war der Entwicklungsrechner mit dem laufenden FastAPI-Server über eine stabile
Tailscale-IP vom Android-Gerät aus erreichbar, unabhängig davon, in welchem WLAN sich
die Geräte befanden.

**Reflexion:**  
Der späte Zeitpunkt des Refactorings war eine bewusste Projektentscheidung: Erst Stabilität
und Funktionsumfang sicherstellen, dann die Plattformerweiterung angehen. Dies war pragmatisch
sinnvoll, bedeutete aber gleichzeitig, dass das Refactoring unter Zeitdruck stattfand.
Eine frühere Planung der Zielarchitektur hätte diesen Aufwand verteilt. Tailscale erwies sich
als unkomplizierte und zuverlässige Lösung für die Testphase; für einen produktiven Betrieb
wäre ein fest adressierbarer Server (VPS oder Cloud-Hosting) die konsequente nächste Stufe.

---

### 3.4 Plattformübergreifende Kompatibilität (Desktop & Android)

**Problem:**  
Flet verhält sich auf Desktop und Android in einigen Bereichen unterschiedlich – insbesondere
bei der Darstellung von UI-Elementen, Seitenbreiten und Schriftgrößen. Eine Oberfläche, die
auf dem Desktop übersichtlich wirkt, konnte auf einem Smartphone-Bildschirm überladen sein.

**Lösung:**  
An kritischen Stellen wurde die Bildschirmbreite (`page.width`) ausgewertet, um zwischen
mobiler und Desktop-Darstellung zu unterscheiden. Beispielsweise werden in der Lead-Status-Ansicht
bei schmalen Bildschirmen (< 600 px) nur Icons statt vollständiger Beschriftungen angezeigt:

```python
is_mobile = self.page.width and self.page.width < 600
```

**Reflexion:**  
Ein systematisches responsives Layout-Konzept von Beginn an (z. B. konsequente Nutzung von
relativen Breiten statt fixer Pixelwerte) hätte punktuelle Anpassungen dieser Art reduziert.

---

### 3.5 Datums- und Zeitzonenbehandlung zwischen Datenbank und API

**Problem:**  
MariaDB liefert `datetime`-Felder als Python-`datetime`-Objekte zurück. Diese sind nicht
direkt JSON-serialisierbar, was bei der Übertragung über die API zu Fehlern führte.

**Lösung:**  
In den API-Hilfsfunktionen (`_lead_to_dict`, `_rows_to_dicts` etc.) werden alle
`datetime`-Objekte vor der Rückgabe in ISO-8601-Strings konvertiert:

```python
for key, val in d.items():
    if isinstance(val, datetime):
        d[key] = val.isoformat()
```

Das Frontend parst diese Strings bei Bedarf zurück in lesbare Datumsformate.

---

## 4. Gesamtbewertung der Architekturentscheidungen

| Aspekt | Bewertung | Anmerkung |
|---|---|---|
| **Wartbarkeit** | ✓ gut | Klare Schichtentrennung, einheitliche Sprache (Python) |
| **Skalierbarkeit** | ◑ bedingt | Für Schulprojekt ausreichend; Cloud-Hosting für Wachstum nötig |
| **Performance** | ✓ ausreichend | FastAPI + MariaDB bewältigen die projektrelevante Last problemlos |
| **Einarbeitungsaufwand** | ✓ gering | Alle gewählten Technologien basierten auf vorhandenem Vorwissen |
| **Mobile-Fähigkeit** | ✓ erreicht | Durch 3-Schichten-Modell und FastAPI realisiert |
| **Technische Schulden** | ⚠ vorhanden | Lokale DB, kein Cloud-Hosting, kein CI/CD – bewusste Einschränkungen im Projektrahmen |
