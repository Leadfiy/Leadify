from database import Database

db = Database(
    host="127.0.0.1",
    user="WIV_Denis",
    password="denisHDD1996",  
    database="leadify",
    port=3306
)

# -------------------------------------------------
# READ-FUNKTIONEN FÜRS AUSSENDIENSTMODUL
# -------------------------------------------------

def get_alle_firmen():
    """
    Gibt alle Firmen mit Basisinformationen zurück.
    """
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
        LEFT JOIN ort o ON f.ort_id = o.id
        ORDER BY f.name ASC;
    """
    return db.fetch_all(sql)


def get_firma_by_id(firma_id):
    """
    Gibt eine einzelne Firma inklusive Branche und Ort zurück.
    """
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
        LEFT JOIN ort o ON f.ort_id = o.id
        WHERE f.id = %s;
    """
    return db.fetch_one(sql, (firma_id,))


def get_ansprechpartner_by_firma(firma_id):
    """
    Gibt alle Ansprechpartner einer Firma zurück.
    """
    sql = """
        SELECT 
            a.id,
            an.anrede,
            a.vorname,
            a.nachname,
            a.email,
            a.telefon,
            p.positionsname AS position
        FROM ansprechpartner a
        LEFT JOIN anrede an ON a.anrede_id = an.id
        LEFT JOIN position p ON a.position_id = p.id
        WHERE a.firma_id = %s
        ORDER BY a.nachname ASC;
    """
    return db.fetch_all(sql, (firma_id,))


# -------------------------------------------------
# TESTBLOCK (wird nur ausgeführt bei: python Außendienst.py)
# -------------------------------------------------
#if __name__ == "__main__":
#    print("Starte Test...")
#   print(get_alle_firmen())

# -------------------------------------------------
# CREAT-FUNKTIONEN FÜRS AUSSENDIENSTMODUL
# -------------------------------------------------

def create_firma(name, strasse, hausnummer, branche_id, ort_id):
    """
    Legt eine neue Firma in der Datenbank an.
    
    Parameter:
    - name: Name der Firma
    - strasse: Straßenname
    - hausnummer: Hausnummer
    - branche_id: Verweis auf die Branche (Fremdschlüssel)
    - ort_id: Verweis auf den Ort (Fremdschlüssel)

    Rückgabe:
    - True/False oder Cursor-Objekt je nach Erfolg
    """

    # SQL-INSERT-Befehl: Fügt eine neue Firma in die Tabelle 'firma' ein
    sql = """
        INSERT INTO firma (name, strasse, hausnummer, branche_id, ort_id)
        VALUES (%s, %s, %s, %s, %s)
    """

    # Parameter werden sauber & sicher an SQL übergeben (keine SQL-Injection möglich)
    params = (name, strasse, hausnummer, branche_id, ort_id)

    # Query ausführen → db.query macht automatisch commit()
    return db.query(sql, params)

def create_ansprechpartner(firma_id, anrede_id, vorname, nachname, email, telefon, position_id):
    """
    Legt einen neuen Ansprechpartner für eine Firma an.
    
    Parameter:
    - firma_id: ID der Firma (FK)
    - anrede_id: Anrede (Herr/Frau …)
    - vorname: Vorname des Ansprechpartners
    - nachname: Nachname
    - email: Kontakt-E-Mail
    - telefon: Telefonnummer
    - position_id: Position/Titel (z. B. Geschäftsführer)

    Rückgabe:
    - True/False oder Cursor je nach Erfolg
    """

    sql = """
        INSERT INTO ansprechpartner 
            (firma_id, anrede_id, vorname, nachname, email, telefon, position_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    params = (firma_id, anrede_id, vorname, nachname, email, telefon, position_id)

    return db.query(sql, params)


def create_lead(firma_id, ansprechpartner_id, beschreibung, status_id, erstellt_von):
    """
    Legt einen neuen Lead an.
    
    Parameter:
    - firma_id: Firma, mit der der Lead verknüpft ist
    - ansprechpartner_id: Ansprechpartner der Firma
    - beschreibung: Beschreibung des Leads (Text)
    - status_id: Lead-Status (z. B. neu, in Bearbeitung, gewonnen)
    - erstellt_von: User-ID des Außendienstmitarbeiters

    Rückgabe:
    - True/False oder Cursor je nach Erfolg
    """

    sql = """
        INSERT INTO lead (firma_id, ansprechpartner_id, beschreibung, status_id, erstellt_von)
        VALUES (%s, %s, %s, %s, %s)
    """

    params = (firma_id, ansprechpartner_id, beschreibung, status_id, erstellt_von)

    return db.query(sql, params)

if __name__ == "__main__":
    print("=== TEST: CREATE FIRMA ===")
    result = create_firma("Testfirma GmbH", "Musterweg", "10", 1, 1)
    print("Ergebnis:", result)



