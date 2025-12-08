import flet as ft
from db_config import db_host, db_user, db_password, db_databse, db_port
import database
from auth_manager import AuthManager
from lead_bearbeitung import LeadBearbeitungManager, LeadBearbeitungView
from admin_menu import AdminMenuView
from lead_loeschen import LeadLoeschenView


class AppController:
    """Hauptsteuerung der Anwendung - verwaltet Navigation und Benutzer-Status"""
    
    def __init__(self, page: ft.Page, db: database.Database):
        self.page = page
        self.db = db
        self.auth = AuthManager(db)
        self.current_user = None
        self.lead_bearbeitung_view = None  # Speichere Lead-View für persistente Filter
        
        # Page-Konfiguration
        self.page.title = "Leadify"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
    
    def start(self):
        """Startet die Anwendung und prüft Auto-Login"""
        is_logged_in, user_data, message = self.auth.check_auto_login()
        
        if is_logged_in:
            self.current_user = user_data
            
            # Prüfe Rolle: Admin (rolle_id = 1) oder normaler User (rolle_id = 2)
            if user_data.get('rolle_id') == 1:
                self.show_admin_menu()  # Admin-Dashboard
            else:
                self.show_main_app()    # Normales User-Dashboard
                
        elif "Warte noch auf Admin-Freigabe" in message:
            self.show_pending_approval()
        else:
            self.show_login_screen()
    
    def show_admin_menu(self):
        """Zeigt das Admin-Hauptmenü"""
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        self.page.padding = 0
        
        admin_view = AdminMenuView(self.page, self.current_user, self)
        admin_view.render()
    
    def show_delete_leads(self):
        """Zeigt die Lead-Löschungs-Ansicht"""
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        self.page.padding = 0
        
        delete_view = LeadLoeschenView(self.page, self.db, self.current_user, self)
        delete_view.render()
    
    def show_main_app(self):
        """Zeigt das Hauptmenü nach erfolgreichem Login (für normale User)"""
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        
        # Hamburger Menü
        menu_drawer = ft.NavigationDrawer(
            controls=[
                ft.Container(height=10),
                ft.ListTile(
                    title=ft.Text(f"Willkommen, {self.current_user.get('vorname', 'Benutzer')}!"),
                    subtitle=ft.Text(self.current_user.get('email', '')),
                ),
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INBOX),
                    title=ft.Text("Meine Nachrichten"),
                    on_click=lambda e: self._show_leads()
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ADD_CIRCLE),
                    title=ft.Text("Lead erstellen"),
                    on_click=lambda e: self._show_create_lead_placeholder()
                ),
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOGOUT),
                    title=ft.Text("Abmelden"),
                    on_click=self._handle_logout
                ),
            ]
        )
        
        self.page.drawer = menu_drawer
        
        # Willkommensbildschirm
        username = self.current_user.get('vorname') or self.current_user.get('email')
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    # Header mit Hamburger-Button
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.MENU,
                            icon_size=30,
                            on_click=lambda e: self._toggle_drawer()
                        ),
                        ft.Text("Leadify", size=24, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=30)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(),
                    
                    # Willkommenstext
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Willkommen zu Leadify!", size=28, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Hallo {username}", size=18, color="grey"),
                            ft.Divider(height=40, color="transparent"),
                            ft.Text("Was möchtest du heute tun?", size=16, weight=ft.FontWeight.W_500),
                        ], spacing=10),
                        padding=20
                    ),
                    
                    ft.Divider(height=20, color="transparent"),
                    
                    # Schnellzugriff-Buttons
                    ft.Column([
                        ft.ElevatedButton(
                            content=ft.Column([
                                ft.Icon(ft.Icons.INBOX, size=40),
                                ft.Text("Meine Nachrichten", size=16, weight=ft.FontWeight.W_500),
                                ft.Text("Bearbeite deine Leads", size=12, color="grey")
                            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            width=300,
                            height=120,
                            on_click=lambda e: self._show_leads()
                        ),
                        
                        ft.ElevatedButton(
                            content=ft.Column([
                                ft.Icon(ft.Icons.ADD_CIRCLE, size=40),
                                ft.Text("Lead erstellen", size=16, weight=ft.FontWeight.W_500),
                                ft.Text("Neuen Lead hinzufügen", size=12, color="grey")
                            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            width=300,
                            height=120,
                            on_click=lambda e: self._show_create_lead_placeholder()
                        ),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ], expand=True),
                padding=20
            )
        )
    
    def _toggle_drawer(self):
        """Öffnet/Schließt das Hamburger-Menü"""
        self.page.drawer.open = not self.page.drawer.open
        self.page.update()
    
    def _show_leads(self):
        """Zeigt die Lead-Bearbeitung UI"""
        self.page.drawer.open = False
        self.page.update()
        
        self.page.clean()
        
        # Lead-Bearbeitung Manager initialisieren
        lead_manager = LeadBearbeitungManager(self.db)
        
        # Erstelle die View nur beim ersten Mal, danach wiederverwenden
        if self.lead_bearbeitung_view is None:
            self.lead_bearbeitung_view = LeadBearbeitungView(self.page, lead_manager, self.current_user)
            self.lead_bearbeitung_view.app_controller = self  # Referenz zum Controller für Navigation
        else:
            # Update Manager und Page
            self.lead_bearbeitung_view.lead_manager = lead_manager
            self.lead_bearbeitung_view.page = self.page
        
        self.lead_bearbeitung_view.render()
    
    def _show_create_lead_placeholder(self):
        """Zeigt Placeholder für Lead-Erstellung (noch nicht implementiert)"""
        self.page.drawer.open = False
        self.page.clean()
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: self.show_main_app()
                        ),
                        ft.Text("Lead erstellen", size=24, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Divider(),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.CONSTRUCTION, size=64, color="orange"),
                            ft.Text("Funktion noch nicht implementiert", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("Die Lead-Erstellung ist derzeit noch in Entwicklung.", size=14, color="grey"),
                            ft.Divider(height=30, color="transparent"),
                            ft.ElevatedButton(
                                "Zurück zum Menü",
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda e: self.show_main_app()
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=40
                    )
                ], expand=True),
                padding=20
            )
        )

    
    def show_pending_approval(self):
        """Zeigt Wartebildschirm für Admin-Freigabe"""
        self.page.clean()
        
        def check_approval(e):
            is_logged_in, user_data, message = self.auth.check_auto_login()
            if is_logged_in:
                self.current_user = user_data
                # Prüfe Rolle und leite entsprechend weiter
                if user_data.get('rolle_id') == 1:
                    self.show_admin_menu()
                else:
                    self.show_main_app()
            else:
                status_text.value = message
                self.page.update()
        
        status_text = ft.Text(
            "Deine Registrierung wird noch geprüft.\nBitte warte auf die Freigabe durch einen Administrator.",
            text_align=ft.TextAlign.CENTER
        )
        
        self.page.add(
            ft.Column([
                ft.Icon(ft.Icons.HOURGLASS_EMPTY, size=64, color="orange"),
                status_text,
                ft.Divider(height=20, color="transparent"),
                ft.ElevatedButton(
                    "Status aktualisieren",
                    icon=ft.Icons.REFRESH,
                    on_click=check_approval
                ),
                ft.TextButton(
                    "Zur Anmeldung",
                    on_click=lambda e: self.show_login_screen()
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def show_register_screen(self):
        """Zeigt Registrierungsformular - nur Email + Passwort"""
        self.page.clean()
        
        email_field = ft.TextField(
            label="Firmen-E-Mail-Adresse",
            width=300,
            autofocus=True,
            hint_text="vorname.nachname@firma.de"
        )
        
        password_field = ft.TextField(
            label="Passwort erstellen",
            password=True,
            can_reveal_password=True,
            width=300,
            hint_text="Mindestens 8 Zeichen"
        )
        
        confirm_field = ft.TextField(
            label="Passwort bestätigen",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        status_text = ft.Text("", color="red")
        
        def register_clicked(e):
            email = email_field.value
            password = password_field.value
            confirm = confirm_field.value
            
            # Validierung
            if not email or not password or not confirm:
                status_text.value = "Bitte alle Felder ausfüllen."
                status_text.color = "red"
            elif password != confirm:
                status_text.value = "Die Passwörter stimmen nicht überein."
                status_text.color = "red"
            elif len(password) < 8:
                status_text.value = "Passwort muss mindestens 8 Zeichen lang sein."
                status_text.color = "red"
            else:
                # Registrierung durchführen
                success, message, token = self.auth.register_user(email, password)
                
                if success:
                    status_text.value = message
                    status_text.color = "green"
                    self.page.update()
                    # Warte kurz, dann zum Wartebildschirm
                    import time
                    time.sleep(1.5)
                    self.show_pending_approval()
                else:
                    status_text.value = message
                    status_text.color = "red"
            
            self.page.update()
        
        self.page.add(
            ft.Column([
                ft.Text("Erstmalige Registrierung", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Gib deine Firmen-E-Mail ein und wähle ein Passwort.", 
                       color="grey", size=12),
                ft.Divider(height=20, color="transparent"),
                email_field,
                password_field,
                confirm_field,
                ft.ElevatedButton("Registrieren", width=300, on_click=register_clicked),
                status_text,
                ft.Divider(height=10, color="transparent"),
                ft.TextButton("Bereits registriert? Zur Anmeldung", 
                             on_click=lambda e: self.show_login_screen())
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def show_login_screen(self):
        """Zeigt Login-Formular"""
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
        
        email_field = ft.TextField(
            label="E-Mail-Adresse",
            width=300,
            autofocus=True
        )
        
        password_field = ft.TextField(
            label="Passwort",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        status_text = ft.Text("", color="red")
        
        def login_clicked(e):
            email = email_field.value
            password = password_field.value
            
            if not email or not password:
                status_text.value = "Bitte alle Felder ausfüllen."
                status_text.color = "red"
                self.page.update()
                return
            
            success, message, user_data = self.auth.login_user(email, password)
            
            if success:
                self.current_user = user_data
                
                # Prüfe Rolle und leite entsprechend weiter
                if user_data.get('rolle_id') == 1:
                    self.show_admin_menu()  # Admin
                else:
                    self.show_main_app()    # Normaler User
            else:
                status_text.value = message
                status_text.color = "red"
                self.page.update()
        
        self.page.add(
            ft.Column([
                ft.Text("Anmeldung", size=24, weight=ft.FontWeight.BOLD),
                email_field,
                password_field,
                ft.ElevatedButton("Anmelden", width=300, on_click=login_clicked),
                status_text,
                ft.Divider(height=10, color="transparent"),
                ft.TextButton("Noch kein Konto? Registrieren", 
                             on_click=lambda e: self.show_register_screen())
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def _handle_logout(self, e):
        """Private Methode für Logout-Logik"""
        # Hamburger-Menü schließen
        if self.page.drawer:
            self.page.drawer.open = False
            self.page.update()
        
        # Logout durchführen
        self.auth.logout()
        self.current_user = None
        
        # Zur Login-Seite navigieren
        self.show_login_screen()


def main(page: ft.Page):
    """Entry Point der Anwendung"""
    # Datenbankverbindung
    db = database.Database(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_databse,
        port=db_port
    )
    
    # App-Controller initialisieren und starten
    app = AppController(page, db)
    app.start()