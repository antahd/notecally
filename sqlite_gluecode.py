import sqlite3

def initialize_sqlite():
    db_path = "events.db"
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            event_name TEXT NOT NULL,
            event_description TEXT
            )
    """)
    conn.commit()
    conn.close()

def fetch_month_events(month_index,year): # 0-12, this function might be unnecessary considering the rest of the translation done in this script
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    month_str = f"{str(year)}-{month_index:02d}-%" # apparently makes 1-9 into 01-09
    cursor.execute("""
        SELECT id, date, event_name
        FROM events
        WHERE date LIKE ?
    """, (month_str,))
    events = cursor.fetchall()
    conn.close()
    return events

def sqlite_entry_listing():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, date, event_name FROM events
    """)
    events = cursor.fetchall()
    conn.close()
    return events

#print(sqlite_entry_listing())

def insert_entry(date, event_name, event_description):
    conn = sqlite3.connect("events.db")
    event = (date, event_name, event_description)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO events (date, event_name, event_description)
    VALUES (?, ?, ?)
    """, event)
    conn.commit()
    conn.close()

def fetch_named_event(name, parse_text):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    if parse_text == True:
        cursor.execute("""
            SELECT id, date, event_name, event_description
            FROM events
            WHERE event_name LIKE ?
        """, (name,))
    else:
        cursor.execute("""
            SELECT id, date, event_name
            FROM events
            WHERE event_name LIKE ?
        """, (name,))
    event = cursor.fetchone()
    conn.close()
    return event


def compgl_nt_index_refresh():
    notelisting = []
    dep_on = []
    dep_of = []
    sql_note_data = sqlite_entry_listing()
    for row in sql_note_data:
        date_raw = row[1].split("-")
        year_raw = date_raw[0]
        if len(year_raw) > 3:
            ML = ''
            YYY = ''
            reduction = len(year_raw) - 3
            for i in range(reduction, len(year_raw)):
                YYY += ''.join(year_raw[i])
            for i in range(0,reduction):
                ML += ''.join(year_raw[i])
        else:
            ML = 0
            YYY = int(date_raw[0].lstrip("0"))

        ML = int(ML)
        YYY = int(YYY)
        MM = int(date_raw[1].lstrip("0"))
        DD = int(date_raw[2].lstrip("0"))
        year = (ML, YYY, MM, DD)
        notelisting.append((row[0],row[2],year,dep_on,dep_of))
    #print(notelisting)
    return notelisting

#compgl_nt_index_refresh() # [(1, 'test title', (2, 25, 5, 23), [], [])]

def compgl_read_note(note, parse_text=False):
    text = ""

    dep_on = [] # there is no dependancy information in the sqlite database, however this is part of my TUI API so something must be returned
    dep_of = [] # having these here also means it's possible for future implementation to be smoother.
    
    sql_note = fetch_named_event(note, parse_text)
    if parse_text == True:
        text = sql_note[3]
    date_raw = sql_note[1].split("-")
    date = (int(date_raw[0]), int(date_raw[1]), int(date_raw[2]))


    return (date, text, sql_note[0], dep_on, dep_of, sql_note[2])

def compgl_write_note(date_in, id_input, name, content, depon = (), depof = (), append_db = True, produce_note = True):
    # the many variables ignored, but still present here due to API compatibility:
    # id_input, depon, depof, append_db, produce_note
    # duct-tape miracle and a half
    ML_raw = date_in[0] * 1000
    YYY_raw = (date_in[1] + date_in[2] + date_in[3] + date_in[4])
    year = YYY_raw + ML_raw
    month = date_in[5]
    day = date_in[6]
    date_str = f"{str(year)}-{month:02d}-{day:02d}"

    insert_entry(date_str, name, content)

#compgl_write_note((20, 255,255,255,0,5,6),1,"write test","lol i wonder if this works")
#print(compgl_read_note("write test"))