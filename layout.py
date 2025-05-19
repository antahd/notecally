import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from calendar import monthrange
import sqlite3
import os  
from database_actions import (
    initialize_database,
    add_event,
    delete_event,
    edit_event,
)

# Kuukaudet suomeksi
kuukaudet_suomeksi = [
    "Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu", "Toukokuu", "Kesäkuu",
    "Heinäkuu", "Elokuu", "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu"
]
nykyinen_kuukausi = kuukaudet_suomeksi[datetime.now().month - 1]

selected_month = None  # Tarvitaan

current_year = datetime.now().year
#Fontit
TITLE_FONT_SIZE = 16
TEXT_FONT_SIZE = 14

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
            font=("Arial", TEXT_FONT_SIZE),
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

        year = current_year
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
                font=("Arial", TEXT_FONT_SIZE),
                width=2,
                command=lambda d=day: highlight_events(month_index, d)
            )
            date_button.grid(row=row, column=col, padx=5, pady=5)

        update_events(selected_month, events_listbox, kuukaudet_suomeksi)

    def highlight_events(month_index, selected_day):
        events_listbox.delete(0, tk.END)
        year = current_year
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

    def update_events(selected_month, events_listbox, kuukaudet_suomeksi):
        events_label.config(text=f"Tapahtumat kuukaudelle {selected_month}")
        events_listbox.delete(0, tk.END)

        month_index = kuukaudet_suomeksi.index(selected_month) + 1
        events = fetch_events_for_month(month_index)
        for event in events:
            event_date, event_name, event_description = event
            events_listbox.insert(tk.END, f"{event_date}: {event_name} - {event_description}")

    right_frame = tk.Frame(root, bg="#2a7f8e", width=600, height=400)  
    right_frame.pack(side="top", fill="both", expand=True)

    background_image_path = os.path.join(os.getcwd(), "background.png")
    if not os.path.exists(background_image_path):
        raise FileNotFoundError(f"Background image not found at {background_image_path}")

    background_image = tk.PhotoImage(file=background_image_path)

    
    events_label = tk.Label(
        right_frame,
        text=f"Tapahtumat kuukaudelle {nykyinen_kuukausi}",
        bg="#2a7f8e",  
        fg="#000000",
        font=("Arial", TITLE_FONT_SIZE),
        image=background_image,
        compound="center" 
    )
    events_label.image = background_image  
    events_label.pack(pady=10)

    events_listbox = tk.Listbox(right_frame, bg="#2a7f8e", fg="#000000", font=("Arial", TEXT_FONT_SIZE), height=20) 
    events_listbox.pack(fill="both", expand=True, padx=10, pady=10)

    bottom_frame = tk.Frame(root, bg="#A7D8DE", height=200) 
    bottom_frame.pack(side="bottom", fill="x")

    add_button = tk.Button(
        bottom_frame,
        text="Lisää tapahtuma",
        bg="#E0FFFF",
        fg="#000000",
        font=("Arial", TEXT_FONT_SIZE),
        command=lambda: add_event(
            selected_month,
            events_listbox,
            kuukaudet_suomeksi,
            current_year,
            update_events
        )
    )
    add_button.grid(row=1, column=2, rowspan=2, padx=10, pady=5, sticky="ns")

    edit_button = tk.Button(
        bottom_frame,
        text="Muokkaa tapahtumaa",
        bg="#E0FFFF",
        fg="#000000",
        font=("Arial", TEXT_FONT_SIZE),
        command=lambda: edit_event(
            selected_month,
            events_listbox,
            None,  # No longer needed
            None,
            None,
            kuukaudet_suomeksi,
            current_year,
            update_events
        )
    )
    edit_button.grid(row=4, column=1, padx=10, pady=5, sticky="ns")

    delete_button = tk.Button(
        bottom_frame,
        text="Poista tapahtuma",
        bg="#E0FFFF",
        fg="#000000",
        font=("Arial", TEXT_FONT_SIZE),
        command=lambda: delete_event(
            selected_month,
            events_listbox,
            kuukaudet_suomeksi,
            update_events
        )
    )
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
