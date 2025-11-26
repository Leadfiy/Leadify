from database import Database


class AussendienstManager:
    """Verwaltet alle Operationen für den Außendienst"""
    
    def __init__(self, db: Database):
        self.db = db
    
    # -----------------------------------------------------------------
    # 1) READ – Firmen & Ansprechpartner
    # -----------------------------------------------------------------
    
    def get_alle_firmen(self):
        """Gibt Liste aller Firmen zurück."""
        sql = """
            SELECT 
                f.id,
                f.name AS firma,
                f.strasse,
                f.hausnummer,
                COALESCE(b.name, 'Keine') AS branche,
                COALESCE(o.ort, 'Keine') AS ort
            FROM firma f
            LEFT JOIN branche b ON f.branche_id = b.id
            LEFT JOIN ort o ON f.ort_id = o.id_ort
            ORDER BY f.name ASC
        """
        return self.db.fetch_all(sql)
    
    def get_firma_by_id(self, firma_id):
        """Gibt eine Firma anhand der ID zurück."""
        sql = """
            SELECT 
                f.id,
                f.name AS firma,
                f.strasse,
                f.hausnummer,
                b.name AS branche,
                o.ort AS ort
            FROM firma f
            LEFT JOIN branche b ON f.branche_id = b.id
            LEFT JOIN ort o ON f.ort_id = o.id_ort
            WHERE f.id = ?
        """
        return self.db.fetch_one(sql, (firma_id,))
    
    def get_ansprechpartner_by_firma(self, firma_id):
        """Gibt alle Ansprechpartner einer Firma zurück."""
        sql = """
            SELECT 
                a.id,
                an.bezeichnung AS anrede,
                a.vorname,
                a.nachname,
                a.email,
                a.telefon,
                p.bezeichnung AS position
            FROM ansprechpartner a
            LEFT JOIN anrede an ON a.anrede_id = an.id
            LEFT JOIN position p ON a.position_id = p.id
            WHERE a.firma_id = ?
            ORDER BY a.nachname ASC
        """
        return self.db.fetch_all(sql, (firma_id,))
    
    def get_produktgruppen(self):
        """Gibt alle Produktgruppen zurück."""
        sql = "SELECT produkt_id, produkt FROM produktgruppe ORDER BY produkt"
        return self.db.fetch_all(sql)
    
    def get_produkte_by_gruppe(self, produktgruppe_id):
        """Gibt alle Produkte einer Produktgruppe zurück."""
        # HINWEIS: produkte Tabelle hat KEINE produktgruppe_id Spalte!
        # Daher geben wir alle Produkte zurück (die produktgruppe_id ist informativ)
        sql = """
            SELECT produkt_id, produkt 
            FROM produkte 
            ORDER BY produkt
        """
        return self.db.fetch_all(sql)
    
    def get_produktzustaende(self):
        """Gibt alle Produktzustände zurück (Neu, Gebraucht, etc.)."""
        sql = "SELECT id, zustand FROM produktzustand ORDER BY zustand"
        return self.db.fetch_all(sql)
    
    def get_quellen(self):
        """Gibt alle Lead-Quellen zurück (Messe, Telefonat, etc.)."""
        sql = "SELECT id_quelle AS id, quelle FROM quelle ORDER BY quelle"
        return self.db.fetch_all(sql)
    
    def get_verfuegbare_bearbeiter(self):
        """Gibt alle Innendienst-Mitarbeiter zurück."""
        sql = """
            SELECT benutzer_id, CONCAT(vorname, ' ', nachname) as name
            FROM benutzer 
            WHERE is_approved = 1 AND rolle_id IN (1, 2)
            ORDER BY vorname, nachname
        """
        return self.db.fetch_all(sql)
    
    # -----------------------------------------------------------------
    # 2) CREATE – Lead anlegen
    # -----------------------------------------------------------------
    
    def create_lead(self, ansprechpartner_id, produkt_id, produktgruppe_id,
                   produktzustand_id, quelle_id, erfasser_id, 
                   bearbeiter_id=None, beschreibung=None):
        """
        Erstellt neuen Lead.
        WICHTIG: firma_id wird NICHT gespeichert (kommt über ansprechpartner)!
        
        Returns: lead_id des neu erstellten Leads oder None bei Fehler
        """
        # Berechne nächste lead_id (da kein auto_increment)
        max_lead = self.db.fetch_one("SELECT MAX(lead_id) as max_id FROM lead")
        next_lead_id = (max_lead['max_id'] or 0) + 1
        
        sql = """
            INSERT INTO lead 
            (lead_id, ansprechpartner_id, produkt_id, produktgruppe_id, 
             produktzustand_id, quelle_id, erfasser_id, bearbeiter_id, 
             status_id, datum_erfasst)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, NOW())
        """
        params = (
            next_lead_id,
            ansprechpartner_id,
            produkt_id,
            produktgruppe_id,
            produktzustand_id,
            quelle_id,
            erfasser_id,
            bearbeiter_id
        )
        
        # Lead erstellen
        result = self.db.query(sql, params)
        
        if result:
            lead_id = next_lead_id
            
            # Beschreibung als Kommentar hinzufügen (falls vorhanden)
            if beschreibung and beschreibung.strip():
                self.add_kommentar(lead_id, beschreibung)
            
            return lead_id
        
        return None
    
    # -----------------------------------------------------------------
    # 3) UPDATE – Kommentare
    # -----------------------------------------------------------------
    
    def add_kommentar(self, lead_id, kommentar_text):
        """Kommentar zu einem Lead hinzufügen."""
        sql = """
            INSERT INTO kommentar (lead_id, Datum, text)
            VALUES (?, NOW(), ?)
        """
        return self.db.query(sql, (lead_id, kommentar_text))


# -----------------------------------------------------------------
# TESTBLOCK – nur wenn Datei direkt ausgeführt wird
# -----------------------------------------------------------------
# if __name__ == "__main__":
#     print("Starte Außendienst-Test...")
    
    
#     print("\n--- Firmenliste ---")
#     firmen = manager.get_alle_firmen()
#     for f in firmen[:3]:  # Nur erste 3 anzeigen
#         print(f)
    
#     print("\n--- Produktgruppen ---")
#     print(manager.get_produktgruppen())
    
#     print("\n--- Bearbeiter (Innendienst) ---")
#     print(manager.get_verfuegbare_bearbeiter())