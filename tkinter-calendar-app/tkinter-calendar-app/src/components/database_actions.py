import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from calendar import monthrange
import sqlite3
import os  


TITLE_FONT_SIZE = 16
TEXT_FONT_SIZE = 14

DB_PATH = "events.db"

# Aloita databse - myöhemmin muuta if statementiksi
def initialize_database():
    db_path = "events.db"
    
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

def add_event(selected_month, events_listbox, event_name_entry, event_date_entry, event_description_entry, kuukaudet_suomeksi, current_year, update_events):
    if selected_month is None:
        tk.messagebox.showerror("Virhe", "Valitse kuukausi ennen tapahtuman lisäämistä.")
        return
    event_name = event_name_entry.get()
    event_date = event_date_entry.get().replace(" ", "-")
    event_description = event_description_entry.get()
    if event_name and event_date:
        try:
            month, day = map(int, event_date.split("-"))
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
            if selected_month == kuukaudet_suomeksi[month - 1]:
                update_events(selected_month, events_listbox, kuukaudet_suomeksi)
            event_name_entry.delete(0, tk.END)
            event_date_entry.delete(0, tk.END)
            event_description_entry.delete(0, tk.END)
        except ValueError:
            tk.messagebox.showerror("Virheellinen päivämäärä", "Anna päivämäärä muodossa MM-DD.")

def delete_event(selected_month, events_listbox, kuukaudet_suomeksi, update_events):
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
                
def edit_event(selected_month, events_listbox, event_name_entry, event_date_entry, event_description_entry, kuukaudet_suomeksi, current_year, update_events):
    if selected_month is None:
        tk.messagebox.showerror("Virhe", "Valitse kuukausi ennen tapahtuman muokkaamista.")
        return
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

                # Pop up koodi on tässä
                popup = tk.Toplevel()
                popup.title("Muokkaa tapahtumaa")
                popup.geometry("500x500")
                popup.configure(bg="#A7D8DE")

                # Nimi
                tk.Label(popup, text="Tapahtuman nimi:", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=5)
                popup_event_name_entry = tk.Entry(popup, font=("Arial", TEXT_FONT_SIZE))
                popup_event_name_entry.pack(pady=5, fill="x", padx=10)
                popup_event_name_entry.insert(0, event_name)

                # Aika
                tk.Label(popup, text="Tapahtuman päivämäärä (MM-DD):", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=5)
                popup_event_date_entry = tk.Entry(popup, font=("Arial", TEXT_FONT_SIZE))
                popup_event_date_entry.pack(pady=5, fill="x", padx=10)
                popup_event_date_entry.insert(0, event_date[5:])

                # Kuvaus
                tk.Label(popup, text="Tapahtuman kuvaus:", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=5)
                popup_event_description_entry = tk.Text(popup, font=("Arial", TEXT_FONT_SIZE), height=8, wrap="word")  # Set height to 8 for larger input
                popup_event_description_entry.pack(pady=5, fill="x", padx=10)
                popup_event_description_entry.insert("1.0", event_description)  # Insert text at the beginning

                def save_changes():
                    new_event_name = popup_event_name_entry.get()
                    new_event_date = popup_event_date_entry.get().replace(" ", "-")
                    new_event_description = popup_event_description_entry.get("1.0", "end").strip()  # Get multi-line input
                    if new_event_name and new_event_date:
                        try:
                            month, day = map(int, new_event_date.split("-"))
                            year = current_year
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