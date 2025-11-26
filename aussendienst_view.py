import flet as ft
from datetime import datetime

# ============================================================================
# VIEW-KLASSE (User Interface für Außendienst)
# ============================================================================

class SearchField:
    """Eingabefeld mit Live-Suchfunktion"""
    
    def __init__(self, label: str, options: list, on_select=None, width=400):
        self.label = label
        self.options = options  # List of dicts mit 'key' und 'text'
        self.on_select = on_select
        self.width = width
        self.selected_value = None
        self.selected_text = ""
        self.filtered_options = []
        
        self.text_field = ft.TextField(
            label=label,
            width=width,
            on_change=self._on_text_change
        )
        
        self.suggestions_list = ft.ListView(
            visible=False,
            height=150,
            spacing=0
        )
        
        self.container = ft.Column([
            self.text_field,
            self.suggestions_list
        ], spacing=0)
    
    def _on_text_change(self, e):
        """Filtert Optionen basierend auf Eingabe"""
        search_text = e.control.value.lower() if e.control.value else ""
        
        print(f"[DEBUG SearchField] Text geändert: '{search_text}'")
        
        if not search_text:
            self.suggestions_list.visible = False
            # NICHT selected_value zurücksetzen bei jedem Keystroke!
        else:
            # Filtere Optionen
            self.filtered_options = [
                opt for opt in self.options
                if search_text in opt['text'].lower()
            ]
            
            # Prüfe ob exakte Übereinstimmung existiert
            exact_match = None
            for opt in self.options:
                if opt['text'].lower() == search_text:
                    exact_match = opt
                    break
            
            if exact_match:
                print(f"[DEBUG SearchField] Exakte Übereinstimmung gefunden: {exact_match['text']}")
                # Exakte Übereinstimmung gefunden - automatisch auswählen
                self._select_option(exact_match['key'], exact_match['text'])
            else:
                # Zeige Suggestions
                self.suggestions_list.controls.clear()
                for opt in self.filtered_options[:10]:  # Max 10 Suggestions
                    btn = ft.Container(
                        content=ft.Text(opt['text'], size=12),
                        padding=8,
                        bgcolor=ft.Colors.TRANSPARENT
                    )
                    btn.data = {'key': opt['key'], 'text': opt['text']}
                    btn.on_click = self._create_selection_handler(opt['key'], opt['text'])
                    self.suggestions_list.controls.append(btn)
                
                self.suggestions_list.visible = len(self.filtered_options) > 0
        
        self.container.update()
    
    def _create_selection_handler(self, key: str, text: str):
        """Erstellt einen Click-Handler für eine Option"""
        def handler(e):
            self._select_option(key, text)
        return handler
    
    def _select_option(self, key: str, text: str):
        """Wählt eine Option aus"""
        print(f"[DEBUG SearchField] Option ausgewählt: {text} (key={key})")
        self.text_field.value = text
        self.selected_value = key
        self.selected_text = text
        self.suggestions_list.visible = False
        
        if self.on_select:
            self.on_select(key)
        
        self.container.update()
    
    @property
    def value(self):
        """Gibt die ausgewählte ID zurück"""
        print(f"[DEBUG SearchField] .value aufgerufen -> {self.selected_value}")
        return self.selected_value
    
    @property
    def error_text(self):
        return self.text_field.error_text
    
    @error_text.setter
    def error_text(self, value):
        self.text_field.error_text = value
        self.container.update()

class AussendienstView:
    """Hauptansicht für Außendienst: Lead erstellen"""
    
    def __init__(self, page: ft.Page, aussendienst_manager, current_user: dict):
        self.page = page
        self.manager = aussendienst_manager
        self.current_user = current_user
        self.app_controller = None  # Wird von AppController gesetzt
        
        # Ausgewählte Werte
        self.selected_firma = None
        self.selected_ansprechpartner = None
        self.selected_produktgruppe = None
        self.selected_produkt = None
        self.selected_zustand = None
        self.selected_quelle = None
        self.selected_bearbeiter = None
        
        # UI-Komponenten
        self.firma_dropdown = None
        self.ansprechpartner_dropdown = None
        self.produktgruppe_dropdown = None
        self.produkt_dropdown = None
        self.zustand_dropdown = None
        self.quelle_dropdown = None
        self.bearbeiter_dropdown = None
        self.beschreibung_field = None
    
    def render(self):
        """Zeigt die Lead-Erfassungsmaske"""
        try:
            self.page.clean()
            
            # Header
            header = ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Zurück zum Menü",
                    on_click=lambda e: self._go_back_to_menu()
                ),
                ft.Text("Neuen Lead erfassen", size=24, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
            # Formular
            print("[DEBUG] Starte _build_form()")
            form = self._build_form()
            print("[DEBUG] _build_form() erfolgreich")
            
            # Buttons
            buttons = ft.Row([
                ft.ElevatedButton(
                    "Lead speichern",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e: self._save_lead(),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE
                ),
                ft.OutlinedButton(
                    "Abbrechen",
                    icon=ft.Icons.CANCEL,
                    on_click=lambda e: self._go_back_to_menu()
                )
            ], spacing=10)
            
            self.page.add(
                ft.Container(
                    content=ft.Column([
                        header,
                        ft.Divider(),
                        form,
                        ft.Divider(),
                        buttons
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True
                )
            )
        except Exception as ex:
            print(f"[DEBUG] FEHLER in render(): {ex}")
            import traceback
            traceback.print_exc()
            self.page.add(ft.Text(f"Fehler beim Laden: {str(ex)}", color="red"))
    
    def _build_form(self):
        """Erstellt das Lead-Erfassungs-Formular"""
        
        print("\n[DEBUG] ===== _build_form() gestartet =====")
        
        # 1. FIRMA auswählen (Eingabefeld mit Live-Suche)
        print("[DEBUG] Lade Firmen...")
        try:
            firmen = self.manager.get_alle_firmen()
            print(f"[DEBUG] Firmen geladen: {len(firmen)}")
            if firmen:
                print(f"[DEBUG] Erste 3 Firmen: {firmen[:3]}")
            else:
                print("[DEBUG] WARNUNG: Keine Firmen gefunden!")
            
            self.firma_options = [
                {'key': str(f['id']), 'text': f"{f['firma']} ({f['ort']})"}
                for f in firmen
            ]
        except Exception as e:
            print(f"[DEBUG] FEHLER beim Laden von Firmen: {e}")
            import traceback
            traceback.print_exc()
            self.firma_options = []
        
        self.firma_dropdown = SearchField(
            label="Firma auswählen *",
            options=self.firma_options,
            on_select=lambda key: self._on_firma_selected(key),
            width=400
        )
        print(f"[DEBUG] SearchField für Firma erstellt mit {len(self.firma_options)} Optionen")
        
        # 2. ANSPRECHPARTNER auswählen (Dropdown nach Firma-Auswahl)
        self.ansprechpartner_dropdown = ft.Dropdown(
            label="Ansprechpartner auswählen *",
            options=[],
            width=400
        )
        
        # 3. PRODUKTGRUPPE auswählen (Dropdown)
        produktgruppen = self.manager.get_produktgruppen()
        produktgruppe_options = [
            ft.dropdown.Option(key=str(pg['produkt_id']), text=pg['produkt'])
            for pg in produktgruppen
        ]
        
        self.produktgruppe_dropdown = ft.Dropdown(
            label="Produktgruppe auswählen *",
            options=produktgruppe_options,
            on_change=lambda e: self._on_produktgruppe_selected(e.control.value),
            width=400
        )
        
        # 4. PRODUKT auswählen (SearchField nach Produktgruppe-Auswahl)
        self.produkt_dropdown = SearchField(
            label="Produkt auswählen *",
            options=[],
            width=400
        )
        
        # 5. ZUSTAND auswählen (Dropdown)
        zustaende = self.manager.get_produktzustaende()
        zustand_options = [
            ft.dropdown.Option(key=str(z['id']), text=z['zustand'])
            for z in zustaende
        ]
        
        self.zustand_dropdown = ft.Dropdown(
            label="Zustand *",
            options=zustand_options,
            width=400
        )
        
        # 6. QUELLE auswählen (Dropdown)
        quellen = self.manager.get_quellen()
        quelle_options = [
            ft.dropdown.Option(key=str(q['id']), text=q['quelle'])
            for q in quellen
        ]
        
        self.quelle_dropdown = ft.Dropdown(
            label="Lead-Quelle *",
            options=quelle_options,
            width=400
        )
        
        # 7. BEARBEITER auswählen (Dropdown)
        bearbeiter = self.manager.get_verfuegbare_bearbeiter()
        bearbeiter_options = [
            ft.dropdown.Option(key=str(b['benutzer_id']), text=b['name'])
            for b in bearbeiter
        ]
        
        self.bearbeiter_dropdown = ft.Dropdown(
            label="An Innendienst zuweisen *",
            options=bearbeiter_options,
            width=400
        )
        
        # 8. BESCHREIBUNG (optional)
        self.beschreibung_field = ft.TextField(
            label="Beschreibung / Notizen (optional)",
            multiline=True,
            min_lines=4,
            max_lines=6,
            width=400
        )
        
        # Formular zusammenbauen
        return ft.Column([
            ft.Text("Kundendaten", size=18, weight=ft.FontWeight.BOLD),
            self.firma_dropdown.container,
            
            # Button zum Ansprechpartner laden
            ft.ElevatedButton(
                text="Ansprechpartner laden",
                on_click=lambda e: self._load_ansprechpartner(),
                icon=ft.Icons.SEARCH
            ),
            
            self.ansprechpartner_dropdown,
            
            ft.Divider(height=20),
            ft.Text("Produktinformationen", size=18, weight=ft.FontWeight.BOLD),
            self.produktgruppe_dropdown,
            self.produkt_dropdown.container,
            self.zustand_dropdown,
            
            ft.Divider(height=20),
            ft.Text("Lead-Details", size=18, weight=ft.FontWeight.BOLD),
            self.quelle_dropdown,
            self.bearbeiter_dropdown,
            self.beschreibung_field,
            
            ft.Text("* Pflichtfelder", size=12, color="grey", italic=True)
        ], spacing=15)
    
    # ---- Event Handlers ----
    
    def _on_firma_selected(self, firma_id):
        """Wird aufgerufen wenn Firma in SearchField ausgewählt wird"""
        if not firma_id:
            return
        
        self.selected_firma = int(firma_id)
        print(f"[DEBUG] Firma ausgewählt: {self.selected_firma}")
    
    def _load_ansprechpartner(self):
        """Lädt Ansprechpartner für die ausgewählte Firma"""
        # DEBUG: Zeige den aktuellen Zustand der SearchField
        print(f"\n[DEBUG] ===== _load_ansprechpartner() aufgerufen =====")
        print(f"  firma_dropdown Typ: {type(self.firma_dropdown)}")
        print(f"  firma_dropdown.text_field.value: {self.firma_dropdown.text_field.value}")
        print(f"  firma_dropdown.value (selected_value): {self.firma_dropdown.value}")
        print(f"  firma_options Länge: {len(self.firma_options) if hasattr(self, 'firma_options') else 'NICHT VORHANDEN'}")
        
        # Prüfe ob Firma eingegeben wurde
        firma_text = self.firma_dropdown.text_field.value.strip() if self.firma_dropdown.text_field.value else ""
        firma_id = self.firma_dropdown.value
        
        print(f"  Bereinigter firma_text: '{firma_text}'")
        print(f"  firma_id: '{firma_id}'")
        
        # Wenn keine ID ausgewählt, aber Text eingegeben, suche die ID
        if not firma_id and firma_text:
            print(f"\n[DEBUG] Suche Firma nach Text: '{firma_text}'")
            print(f"[DEBUG] Verfügbare Firmen:")
            for i, opt in enumerate(self.firma_options[:5]):  # Zeige erste 5
                print(f"    {i}: key={opt['key']}, text={opt['text']}")
            
            for opt in self.firma_options:
                if opt['text'].lower() == firma_text.lower():
                    firma_id = opt['key']
                    print(f"[DEBUG] EXAKTE ÜBEREINSTIMMUNG GEFUNDEN! Firma-ID: {firma_id}")
                    break
                # Auch Teilübereinstimmung versuchen
                elif firma_text.lower() in opt['text'].lower():
                    firma_id = opt['key']
                    print(f"[DEBUG] TEILÜBEREINSTIMMUNG GEFUNDEN! Firma-ID: {firma_id}, Text: {opt['text']}")
                    break
        
        if not firma_id:
            print(f"[DEBUG] FEHLER: Keine Firma-ID gefunden!")
            self.ansprechpartner_dropdown.error_text = "Bitte zuerst eine Firma auswählen oder eingeben"
            self.page.update()
            return
        
        try:
            self.selected_firma = int(firma_id)
            print(f"\n[DEBUG] Lade Ansprechpartner für Firma-ID: {self.selected_firma}")
            
            # Ansprechpartner laden - filtert nach firma_id
            ansprechpartner = self.manager.get_ansprechpartner_by_firma(self.selected_firma)
            print(f"[DEBUG] Ansprechpartner gefunden: {len(ansprechpartner)}")
            if ansprechpartner:
                print(f"[DEBUG] Erste 2: {ansprechpartner[:2]}")
            
            if ansprechpartner:
                # Dropdown-Optionen füllen
                self.ansprechpartner_dropdown.options = [
                    ft.dropdown.Option(
                        key=str(ap['id']),
                        text=f"{ap['anrede']} {ap['vorname']} {ap['nachname']} ({ap['position']})"
                    )
                    for ap in ansprechpartner
                ]
                
                # Ersten Ansprechpartner automatisch auswählen
                self.ansprechpartner_dropdown.value = str(ansprechpartner[0]['id'])
                self.selected_ansprechpartner = int(ansprechpartner[0]['id'])
                self.ansprechpartner_dropdown.error_text = None
                print(f"[DEBUG] Erster Ansprechpartner automatisch ausgewählt: {ansprechpartner[0]['id']}")
            else:
                self.ansprechpartner_dropdown.options = []
                self.ansprechpartner_dropdown.error_text = "Keine Ansprechpartner für diese Firma gefunden"
                print(f"[DEBUG] Keine Ansprechpartner für Firma {self.selected_firma}")
            
            self.page.update()
            
        except Exception as e:
            print(f"[DEBUG] FEHLER in _load_ansprechpartner(): {e}")
            import traceback
            traceback.print_exc()
            self.ansprechpartner_dropdown.error_text = f"Fehler: {str(e)}"
            self.page.update()
    
    def _on_produktgruppe_selected(self, produktgruppe_id):
        """Wird aufgerufen wenn Produktgruppe ausgewählt wird"""
        if not produktgruppe_id:
            self.produkt_dropdown.options = []
            return
        
        self.selected_produktgruppe = int(produktgruppe_id)
        
        # DEBUG
        print(f"[DEBUG] Produktgruppe ausgewählt: {self.selected_produktgruppe}")
        
        # Produkte laden
        try:
            produkte = self.manager.get_produkte_by_gruppe(self.selected_produktgruppe)
            print(f"[DEBUG] Produkte geladen: {len(produkte)} gefunden")
            print(f"[DEBUG] Erste Produkte: {produkte[:3] if produkte else 'KEINE'}")
            
            if produkte:
                self.produkt_dropdown.options = [
                    {'key': str(p['produkt_id']), 'text': p['produkt']}
                    for p in produkte
                ]
                self.produkt_dropdown.error_text = None
            else:
                self.produkt_dropdown.options = []
                self.produkt_dropdown.error_text = "Keine Produkte gefunden"
        except Exception as e:
            print(f"[DEBUG] FEHLER beim Laden von Produkten: {e}")
            self.produkt_dropdown.error_text = f"Fehler: {str(e)}"
        
        self.produkt_dropdown.container.update()
    
    def _save_lead(self):
        """Lead speichern - mit Validierung"""
        
        print("[DEBUG] ===== _save_lead() aufgerufen! =====")
        print(f"[DEBUG] firma: {self.firma_dropdown.value}")
        print(f"[DEBUG] produkt: {self.produkt_dropdown.value}")
        print(f"[DEBUG] bearbeiter: {self.bearbeiter_dropdown.value}")
        
        try:
            # Validierung
            errors = []
            
            # Prüfe Firma (SearchField)
            if not self.firma_dropdown.value:
                errors.append("Bitte Firma auswählen")
                self.firma_dropdown.error_text = "Pflichtfeld"
            else:
                self.firma_dropdown.error_text = None
            
            # Prüfe Ansprechpartner (Dropdown)
            if not self.ansprechpartner_dropdown.value:
                errors.append("Bitte Ansprechpartner auswählen")
                self.ansprechpartner_dropdown.error_text = "Pflichtfeld"
            else:
                self.ansprechpartner_dropdown.error_text = None
            
            # Prüfe Produktgruppe (Dropdown)
            if not self.produktgruppe_dropdown.value:
                errors.append("Bitte Produktgruppe auswählen")
                self.produktgruppe_dropdown.error_text = "Pflichtfeld"
            else:
                self.produktgruppe_dropdown.error_text = None
            
            # Prüfe Produkt (SearchField)
            if not self.produkt_dropdown.value:
                errors.append("Bitte Produkt auswählen")
                self.produkt_dropdown.error_text = "Pflichtfeld"
            else:
                self.produkt_dropdown.error_text = None
            
            # Prüfe Zustand (Dropdown)
            if not self.zustand_dropdown.value:
                errors.append("Bitte Zustand auswählen")
                self.zustand_dropdown.error_text = "Pflichtfeld"
            else:
                self.zustand_dropdown.error_text = None
            
            # Prüfe Quelle (Dropdown)
            if not self.quelle_dropdown.value:
                errors.append("Bitte Quelle auswählen")
            
            # Prüfe Bearbeiter (Dropdown)
            if not self.bearbeiter_dropdown.value:
                errors.append("Bitte Bearbeiter auswählen (Innendienst zuweisen)")
            
            # Wenn Fehler vorhanden, Dialog anzeigen
            if errors:
                self.page.update()
                error_dialog = ft.AlertDialog(
                    title=ft.Text("Validierungsfehler"),
                    content=ft.Column([
                        ft.Text("Bitte fülle alle Pflichtfelder aus:", weight=ft.FontWeight.BOLD),
                        *[ft.Text(f"• {error}", size=12) for error in errors]
                    ], tight=True),
                    actions=[ft.TextButton("OK", on_click=lambda e: self.page.close(error_dialog))]
                )
                self.page.open(error_dialog)
                return
            
            print("[DEBUG] Validierung erfolgreich - starte Lead-Erstellung")
            
            # Lead erstellen
            lead_id = self.manager.create_lead(
                ansprechpartner_id=int(self.ansprechpartner_dropdown.value),
                produkt_id=int(self.produkt_dropdown.value),
                produktgruppe_id=int(self.produktgruppe_dropdown.value),
                produktzustand_id=int(self.zustand_dropdown.value),
                quelle_id=int(self.quelle_dropdown.value),
                erfasser_id=self.current_user['benutzer_id'],
                bearbeiter_id=int(self.bearbeiter_dropdown.value),
                beschreibung=self.beschreibung_field.value
            )
            
            print(f"[DEBUG] Lead-Erstellung abgeschlossen: ID={lead_id}")
            
            if lead_id:
                # Erfolgs-Dialog
                success_dialog = ft.AlertDialog(
                    title=ft.Text("Erfolg!", color=ft.Colors.GREEN),
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN),
                        ft.Text(f"Lead #{lead_id} wurde erfolgreich erstellt!", 
                               text_align=ft.TextAlign.CENTER),
                        ft.Text("Der Lead wurde an den Innendienst weitergeleitet.",
                               size=12, color="grey", text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: self._after_save_success(success_dialog))
                    ]
                )
                self.page.open(success_dialog)
            else:
                raise Exception("Lead konnte nicht erstellt werden")
        
        except Exception as ex:
            print(f"[DEBUG] FEHLER in _save_lead: {ex}")
            import traceback
            traceback.print_exc()
            
            # Fehler-Dialog
            error_dialog = ft.AlertDialog(
                title=ft.Text("Fehler", color=ft.Colors.RED),
                content=ft.Text(f"Fehler beim Speichern: {str(ex)}"),
                actions=[ft.TextButton("OK", on_click=lambda e: self.page.close(error_dialog))]
            )
            self.page.open(error_dialog)
    
    def _after_save_success(self, dialog):
        """Nach erfolgreichem Speichern: Dialog schließen und zurück zum Menü"""
        self.page.close(dialog)
        self._go_back_to_menu()
    
    def _go_back_to_menu(self):
        """Kehrt zum Hauptmenü zurück"""
        if self.app_controller:
            self.app_controller.show_main_app()