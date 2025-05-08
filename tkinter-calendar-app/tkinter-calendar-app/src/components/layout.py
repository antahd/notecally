import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from calendar import monthrange
import sqlite3
import os  

# Kuukaudet suomeksi
kuukaudet_suomeksi = [
    "Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu", "Toukokuu", "Kesäkuu",
    "Heinäkuu", "Elokuu", "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu"
]
nykyinen_kuukausi = kuukaudet_suomeksi[datetime.now().month - 1]

selected_month = None  # Tämä aikoinaan tarvittiin.

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

def create_layout():
    # Luo pääikkuna
    root = tk.Tk()
    root.title("Kalenterinäkymä")
    root.geometry("1200x800")
    root.configure(bg="#5CA4A9")  

    left_frame = tk.Frame(root, bg="#A7D8DE", width=200, height=600)  
    left_frame.pack(side="left", fill="y")

    # Lisää vierityspalkki ja canvas vasemmalle kehykselle
    canvas = tk.Canvas(left_frame, bg="#5CA4A9", width=280, height=600, highlightthickness=0)  
    scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#5CA4A9", width=280)  

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def on_mouse_wheel(event):
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Lisää painikkeet kaikille kuukausille
    month_buttons = []

    def create_month_button(month, month_index):
        button = tk.Button(
            scrollable_frame,
            text=f"{month}",
            bg="#A7D8DE",  
            fg="#000000",
            font=("Arial", 14),
            width=24,
            command=lambda: toggle_month_view(month_index, month, button)
        )
        month_buttons.append((button, month_index, month))
        return button

    def toggle_month_view(month_index, month_name, month_button):
        global selected_month
        selected_month = month_name

        for widget in scrollable_frame.winfo_children():
            if getattr(widget, "is_calendar", False):
                widget.destroy()

        dates_frame = tk.Frame(scrollable_frame, bg="#5CA4A9", width=260) 
        dates_frame.is_calendar = True
        dates_frame.pack(fill="x", pady=5, after=month_button)

        year = 2025
        _, num_days = monthrange(year, month_index)

        events = fetch_events_for_month(month_index)
        event_days = {int(event[0].split("-")[2]) for event in events}

        for day in range(1, num_days + 1):
            row = (day - 1) // 7
            col = (day - 1) % 7
            has_event = day in event_days
            date_button = tk.Button(
                dates_frame,
                text=f"{day}",
                bg="#FFCCCC" if has_event else "#FFFFFF",
                fg="#000000",
                font=("Arial", 12),
                width=2,
                command=lambda d=day: highlight_events(month_index, d)
            )
            date_button.grid(row=row, column=col, padx=5, pady=5)

        update_events(month_name)

    def highlight_events(month_index, selected_day):
        events_listbox.delete(0, tk.END)
        year = 2025
        selected_date = f"{year}-{month_index:02d}-{selected_day:02d}"

        events = fetch_events_for_month(month_index)
        for event in events:
            event_date, event_name, event_description = event
            if event_date == selected_date:
                events_listbox.insert(tk.END, f"{event_date}: {event_name} - {event_description}")
                events_listbox.itemconfig(tk.END, bg="#FFCCCC")
            else:
                events_listbox.insert(tk.END, f"{event_date}: {event_name} - {event_description}")

    for index, month in enumerate(kuukaudet_suomeksi, start=1):
        button = create_month_button(month, index)
        button.pack(pady=10, fill="x")

    def update_events(selected_month):
        events_label.config(text=f"Tapahtumat kuukaudelle {selected_month}")
        events_listbox.delete(0, tk.END)

        month_index = kuukaudet_suomeksi.index(selected_month) + 1
        events = fetch_events_for_month(month_index)
        for event in events:
            event_date, event_name, event_description = event
            events_listbox.insert(tk.END, f"{event_date}: {event_name} - {event_description}")

    right_frame = tk.Frame(root, bg="#2a7f8e", width=600, height=400)  
    right_frame.pack(side="top", fill="both", expand=True)

    # Load the background image
    background_image_path = os.path.join(os.getcwd(), "background.png")
    if not os.path.exists(background_image_path):
        raise FileNotFoundError(f"Background image not found at {background_image_path}")

    background_image = tk.PhotoImage(file=background_image_path)

    
    events_label = tk.Label(
        right_frame,
        text=f"Tapahtumat kuukaudelle {nykyinen_kuukausi}",
        bg="#2a7f8e",  
        fg="#000000",
        font=("Arial", 18),
        image=background_image,
        compound="center" 
    )
    events_label.image = background_image  
    events_label.pack(pady=10)

    events_listbox = tk.Listbox(right_frame, bg="#2a7f8e", fg="#000000", font=("Arial", 14), height=20) 
    events_listbox.pack(fill="both", expand=True, padx=10, pady=10)

    bottom_frame = tk.Frame(root, bg="#A7D8DE", height=200) 
    bottom_frame.pack(side="bottom", fill="x")

    event_name_label = tk.Label(bottom_frame, text="Tapahtuman nimi:", bg="#A7D8DE", font=("Arial", 12))  
    event_name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    
    input_image_path = os.path.join(os.getcwd(), "input.png")
    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input image not found at {input_image_path}")

    input_image = tk.PhotoImage(file=input_image_path)

   
    event_name_bg = tk.Label(bottom_frame, image=input_image, bg="#a7d8de")
    event_name_bg.image = input_image  
    event_name_bg.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    
    def position_event_name_entry():
        event_name_entry.place(
            x=event_name_bg.winfo_x() + 10,
            y=event_name_bg.winfo_y() + 5,
            width=event_name_bg.winfo_width() - 20,
            height=event_name_bg.winfo_height() - 10
        )

    event_name_entry = tk.Entry(bottom_frame, bg="#95acac", bd=0, highlightthickness=0, font=("Arial", 12))
    bottom_frame.after(100, position_event_name_entry)

    event_date_label = tk.Label(bottom_frame, text="Tapahtuman päivämäärä (MM-DD):", bg="#a7d8de", font=("Arial", 12))
    event_date_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    event_date_bg = tk.Label(bottom_frame, image=input_image, bg="#a7d8de")
    event_date_bg.image = input_image
    event_date_bg.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    def position_event_date_entry():
        event_date_entry.place(
            x=event_date_bg.winfo_x() + 10,
            y=event_date_bg.winfo_y() + 5,
            width=event_date_bg.winfo_width() - 20,
            height=event_date_bg.winfo_height() - 10
        )

    event_date_entry = tk.Entry(bottom_frame, bg="#95acac", bd=0, highlightthickness=0, font=("Arial", 12))
    bottom_frame.after(100, position_event_date_entry)

    event_description_label = tk.Label(bottom_frame, text="Tapahtuman kuvaus:", bg="#a7d8de", font=("Arial", 12))
    event_description_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

    event_description_bg = tk.Label(bottom_frame, image=input_image, bg="#a7d8de")
    event_description_bg.image = input_image
    event_description_bg.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    def position_event_description_entry():
        event_description_entry.place(
            x=event_description_bg.winfo_x() + 10,
            y=event_description_bg.winfo_y() + 5,
            width=event_description_bg.winfo_width() - 20,
            height=event_description_bg.winfo_height() - 10
        )

    event_description_entry = tk.Entry(bottom_frame, bg="#95acac", bd=0, highlightthickness=0, font=("Arial", 12))
    bottom_frame.after(100, position_event_description_entry)

    def add_event():
        event_name = event_name_entry.get()
        event_date = event_date_entry.get().replace(" ", "-")
        event_description = event_description_entry.get()
        if event_name and event_date:
            try:
                month, day = map(int, event_date.split("-"))
                year = 2025
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
                    update_events(selected_month)

                event_name_entry.delete(0, tk.END)
                event_date_entry.delete(0, tk.END)
                event_description_entry.delete(0, tk.END)
            except ValueError:
                tk.messagebox.showerror("Virheellinen päivämäärä", "Anna päivämäärä muodossa MM-DD.")

    def delete_event():
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

                    update_events(selected_month)

    def edit_event():
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

                    # Kuvaukset
                    event_name_entry.delete(0, tk.END)
                    event_name_entry.insert(0, event_name)

                    event_date_entry.delete(0, tk.END)
                    event_date_entry.insert(0, event_date[5:])  # Kuukausi ja pvm tarvitaan älä unohda älä poista

                    event_description_entry.delete(0, tk.END)
                    event_description_entry.insert(0, event_description)

                    def save_changes():
                        new_event_name = event_name_entry.get()
                        new_event_date = event_date_entry.get().replace(" ", "-")
                        new_event_description = event_description_entry.get()

                        if new_event_name and new_event_date:
                            try:
                                month, day = map(int, new_event_date.split("-"))
                                year = 2025
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
                                    update_events(selected_month)

                                # Tyhjennä näkym
                                event_name_entry.delete(0, tk.END)
                                event_date_entry.delete(0, tk.END)
                                event_description_entry.delete(0, tk.END)

                                tk.messagebox.showinfo("Onnistui", "Tapahtuma päivitetty onnistuneesti.")
                            except ValueError:
                                tk.messagebox.showerror("Virheellinen päivämäärä", "Anna päivämäärä muodossa MM-DD.")

                    # Tallenna nappula ei ole väliaikainen se pitää korjata
                    save_button = tk.Button(bottom_frame, text="Tallenna muutokset", bg="#E0FFFF", fg="#000000", font=("Arial", 12), command=save_changes)
                    save_button.grid(row=4, column=2, padx=10, pady=5, sticky="ns")

    edit_button = tk.Button(bottom_frame, text="Muokkaa tapahtumaa", bg="#E0FFFF", fg="#000000", font=("Arial", 12), command=edit_event)
    edit_button.grid(row=4, column=1, padx=10, pady=5, sticky="ns")

    add_button = tk.Button(bottom_frame, text="Lisää tapahtuma", bg="#E0FFFF", fg="#000000", font=("Arial", 12), command=add_event)
    add_button.grid(row=1, column=2, rowspan=2, padx=10, pady=5, sticky="ns")

    delete_button = tk.Button(bottom_frame, text="Poista tapahtuma", bg="#E0FFFF", fg="#000000", font=("Arial", 12), command=delete_event)
    delete_button.grid(row=3, column=2, padx=10, pady=5, sticky="ns")

    # Valitse nykyinen kuukausi tärkeä

    current_month_index = datetime.now().month
    for button, month_index, month_name in month_buttons:
        if month_index == current_month_index:
            toggle_month_view(month_index, month_name, button)
            break

    root.mainloop()

# Suorita layout
if __name__ == "__main__":
    initialize_database()
    create_layout()
