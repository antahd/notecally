import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from calendar import monthrange
import sqlite3
import os
import random  
from cal_bin_lib import write_note  
from binhandler import binary_sys_init  
 # note_db_scan muista tämä
TITLE_FONT_SIZE = 16
TEXT_FONT_SIZE = 14
kanta = "sqlite" #Muuta tämä myöhemmin if:ksi ja vaihtelevaksi
sovellus = "tkinter" #Sama tähän.
DB_PATH = "events.db"

# Aloita database - myöhemmin muuta if statementiksi
def initialize_database():
    db_path = "events.db"
    if kanta == "sqlite":    
        # Tarkista, onko tietokanta olemassa
        if not os.path.exists(db_path):
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

            initial_events = [
                ("2025-01-01", "Uudenvuodenpäivä", "Vuoden ensimmäinen päivä"),
                ("2025-02-14", "Ystävänpäivä", "Muista ystäviäsi ja rakkaitasi"),
                ("2025-03-08", "Kansainvälinen naistenpäivä", "Juhlistetaan naisia"),
                ("2025-04-01", "Aprillipäivä", "Hauskoja kepposia")
            ]
            cursor.executemany("""
                INSERT INTO events (date, event_name, event_description)
                VALUES (?, ?, ?)
            """, initial_events)
            conn.commit()
            conn.close()
        else:
            print(f"Database '{db_path}' already exists. Skipping initialization.")

# Etsi tiedot
def fetch_events_for_month(month_index):
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    month_str = f"2025-{month_index:02d}-%"
    cursor.execute("""
        SELECT date, event_name, event_description
        FROM events
        WHERE date LIKE ?
    """, (month_str,))
    events = cursor.fetchall()
    conn.close()
    return events


def show_add_event_popup(selected_month, events_listbox, kuukaudet_suomeksi, current_year, update_events):
    popup = tk.Toplevel()
    popup.title("Lisää tapahtuma")
    popup.geometry("500x500")
    popup.configure(bg="#A7D8DE")

    tk.Label(popup, text="Tapahtuman nimi:", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=5)
    event_name_entry = tk.Entry(popup, font=("Arial", TEXT_FONT_SIZE))
    event_name_entry.pack(pady=5, fill="x", padx=10)

    tk.Label(popup, text="Tapahtuman päivämäärä (MM-DD):", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=5)
    event_date_entry = tk.Entry(popup, font=("Arial", TEXT_FONT_SIZE))
    event_date_entry.pack(pady=5, fill="x", padx=10)

    tk.Label(popup, text="Tapahtuman kuvaus:", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=5)
    event_description_entry = tk.Text(popup, font=("Arial", TEXT_FONT_SIZE), height=8, wrap="word")
    event_description_entry.pack(pady=5, fill="x", padx=10)

    def on_save():
        event_name = event_name_entry.get()
        event_date = event_date_entry.get().replace(" ", "-").strip()
        event_description = event_description_entry.get("1.0", "end").strip()
        parts = event_date.split("-")

        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            tk.messagebox.showerror("Virheellinen päivämäärä", "Anna päivämäärä muodossa MM-DD.")
            return

        month, day = map(int, parts)
        if not (1 <= month <= 12 and 1 <= day <= 31):
            tk.messagebox.showerror("Virheellinen päivämäärä", "Anna oikea kuukausi ja päivä.")
            return

        if event_name and event_date:
            try:
                year = current_year
                if kanta == "binary":
                    binary_sys_init()
                    millennia = year // 1000
                    hundreds = year % 1000
                    date_tuple = (millennia, hundreds, month, day)
                    pituus = len(event_name)
                    for i in range(pituus):
                        id_input = random.randint(0, 1000)
                    write_note(
                        date_in=date_tuple,
                        id_input=id_input,
                        name=event_name,
                        content=event_description,
                        depon=(),
                        depof=(),
                        append_db=True,
                        produce_note=True
                    )
                    tk.messagebox.showinfo("Onnistui", "Tapahtuma lisätty binäärimuotoon.")
                else:
                    formatted_date = f"{year:04d}-{month:02d}-{day:02d}"
                    conn = sqlite3.connect("events.db")
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO events (date, event_name, event_description)
                        VALUES (?, ?, ?)
                    """, (formatted_date, event_name, event_description))
                    conn.commit()
                    conn.close()
                if selected_month == kuukaudet_suomeksi[month - 1]:
                    update_events(selected_month, events_listbox, kuukaudet_suomeksi)
                popup.destroy()
            except Exception as e:
                tk.messagebox.showerror("Virhe", f"Tapahtui virhe: {e}")

    save_button = tk.Button(popup, text="Lisää tapahtuma", bg="#E0FFFF", fg="#000000", font=("Arial", TEXT_FONT_SIZE), command=on_save)
    save_button.pack(pady=10)

def add_event(selected_month, events_listbox, kuukaudet_suomeksi, current_year, update_events):
    if sovellus == "tkinter":
        if selected_month is None:
            tk.messagebox.showerror("Virhe", "Valitse kuukausi ennen tapahtuman lisäämistä.")
            return
        show_add_event_popup(selected_month, events_listbox, kuukaudet_suomeksi, current_year, update_events)
    else:
        def add_event_sqlite(event_name, event_date, event_description):
            parts = event_date.split("-")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                return
            month, day = map(int, parts)
            year = current_year
            formatted_date = f"{year:04d}-{month:02d}-{day:02d}"
            conn = sqlite3.connect("events.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (date, event_name, event_description)
                VALUES (?, ?, ?)
            """, (formatted_date, event_name, event_description))
            conn.commit()
            conn.close()
            if callable(update_events):
                update_events(selected_month, events_listbox, kuukaudet_suomeksi)
        return add_event_sqlite

def show_edit_event_popup(selected_month, events_listbox, event_name_entry, event_date_entry, event_description_entry, kuukaudet_suomeksi, current_year, update_events):
    selected_event_index = events_listbox.curselection()
    if selected_event_index:
        selected_event = events_listbox.get(selected_event_index)
        if selected_event:  
            event_parts = selected_event.split(": ")
            if len(event_parts) >= 2:
                event_date = event_parts[0]
                event_details = event_parts[1].split(" - ")
                event_name = event_details[0]
                event_description = event_details[1] if len(event_details) > 1 else ""

                popup = tk.Toplevel()
                popup.title("Muokkaa tapahtumaa")
                popup.geometry("500x500")
                popup.configure(bg="#A7D8DE")

                tk.Label(popup, text="Tapahtuman nimi:", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=5)
                popup_event_name_entry = tk.Entry(popup, font=("Arial", TEXT_FONT_SIZE))
                popup_event_name_entry.pack(pady=5, fill="x", padx=10)
                popup_event_name_entry.insert(0, event_name)

                tk.Label(popup, text="Tapahtuman päivämäärä (MM-DD):", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=5)
                popup_event_date_entry = tk.Entry(popup, font=("Arial", TEXT_FONT_SIZE))
                popup_event_date_entry.pack(pady=5, fill="x", padx=10)
                popup_event_date_entry.insert(0, event_date[5:])

                tk.Label(popup, text="Tapahtuman kuvaus:", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=5)
                popup_event_description_entry = tk.Text(popup, font=("Arial", TEXT_FONT_SIZE), height=8, wrap="word")
                popup_event_description_entry.pack(pady=5, fill="x", padx=10)
                popup_event_description_entry.insert("1.0", event_description)

                def save_changes():
                    new_event_name = popup_event_name_entry.get()
                    new_event_date = popup_event_date_entry.get().replace(" ", "-")
                    new_event_description = popup_event_description_entry.get("1.0", "end").strip()
                    if new_event_name and new_event_date:
                        try:
                            month, day = map(int, new_event_date.split("-"))
                            year = current_year
                            if kanta == "binary":
                                millennia = year // 1000
                                hundreds = year % 1000
                                date_tuple = (millennia, hundreds, month, day)
                                pituus = len(new_event_name)
                                for i in range(pituus):
                                    id_input = random.randint(0, 1000)
                                write_note(
                                    date_in=date_tuple,
                                    id_input=id_input,
                                    name=new_event_name,
                                    content=new_event_description,
                                    depon=(),
                                    depof=(),
                                    append_db=True,
                                    produce_note=True
                                )
                                popup.destroy()
                                tk.messagebox.showinfo("Onnistui", "Tapahtuma päivitetty binäärimuotoon.")
                                if selected_month == kuukaudet_suomeksi[month - 1]:
                                    update_events(selected_month, events_listbox, kuukaudet_suomeksi)
                            else:
                                formatted_date = f"{year:04d}-{month:02d}-{day:02d}"
                                conn = sqlite3.connect("events.db")
                                cursor = conn.cursor()
                                cursor.execute("""
                                    UPDATE events
                                    SET date = ?, event_name = ?, event_description = ?
                                    WHERE date = ? AND event_name = ?
                                """, (formatted_date, new_event_name, new_event_description, event_date, event_name))
                                conn.commit()
                                conn.close()
                                if selected_month == kuukaudet_suomeksi[month - 1]:
                                    update_events(selected_month, events_listbox, kuukaudet_suomeksi)
                                popup.destroy()
                                tk.messagebox.showinfo("Onnistui", "Tapahtuma päivitetty onnistuneesti.")
                        except ValueError:
                            tk.messagebox.showerror("Virheellinen päivämäärä", "Anna päivämäärä muodossa MM-DD.")

                save_button = tk.Button(popup, text="Tallenna muutokset", bg="#E0FFFF", fg="#000000", font=("Arial", TEXT_FONT_SIZE), command=save_changes)
                save_button.pack(pady=10)

def edit_event(selected_month, events_listbox, event_name_entry, event_date_entry, event_description_entry, kuukaudet_suomeksi, current_year, update_events):
    if sovellus == "tkinter":
        if selected_month is None:
            tk.messagebox.showerror("Virhe", "Valitse kuukausi ennen tapahtuman muokkaamista.")
            return
        show_edit_event_popup(selected_month, events_listbox, event_name_entry, event_date_entry, event_description_entry, kuukaudet_suomeksi, current_year, update_events)
    else:
        def edit_event_sqlite(old_event_date, old_event_name, new_event_name, new_event_date, new_event_description):
            parts = new_event_date.split("-")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                return
            month, day = map(int, parts)
            year = current_year
            formatted_date = f"{year:04d}-{month:02d}-{day:02d}"
            conn = sqlite3.connect("events.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE events
                SET date = ?, event_name = ?, event_description = ?
                WHERE date = ? AND event_name = ?
            """, (formatted_date, new_event_name, new_event_description, old_event_date, old_event_name))
            conn.commit()
            conn.close()
            if callable(update_events):
                update_events(selected_month, events_listbox, kuukaudet_suomeksi)
        return edit_event_sqlite

def delete_event(selected_month, events_listbox, kuukaudet_suomeksi, update_events):
    if sovellus == "tkinter":
        if selected_month is None:
            tk.messagebox.showerror("Virhe", "Valitse kuukausi ennen tapahtuman poistamista.")
            return
        selected_event_index = events_listbox.curselection()
        if selected_event_index:
            selected_event = events_listbox.get(selected_event_index)
            if selected_event:
                event_parts = selected_event.split(": ")
                if len(event_parts) >= 2:
                    event_date = event_parts[0]
                    event_name = event_parts[1].split(" - ")[0]
                    conn = sqlite3.connect("events.db")
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM events
                        WHERE date = ? AND event_name = ?
                    """, (event_date, event_name))
                    conn.commit()
                    conn.close()
                    update_events(selected_month, events_listbox, kuukaudet_suomeksi)
    else:
        def delete_event_sqlite(event_date, event_name):
            conn = sqlite3.connect("events.db")
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM events
                WHERE date = ? AND event_name = ?
            """, (event_date, event_name))
            conn.commit()
            conn.close()
            if callable(update_events):
                update_events(selected_month, events_listbox, kuukaudet_suomeksi)
        return delete_event_sqlite
