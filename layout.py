import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from calendar import monthrange
import sqlite3
import os  
import sys  # Sys tarvittiin pyinstalleria varten

from database_actions import kannan_otto

def conf_check():
    with open("nt_cally.cfg", 'rt') as file:
        config_str = file.read()
    config_internal = config_str.split("\n")
    for item in config_internal:
        var = item.split("=")
        if var[0] == "sqlite_enabled":
            global kanta
            if var[1] == "yes":
                kanta = "sqlite"
            elif var[1] == "ask":
                kanta = "sqlite"
            elif var[1] == "no":
                kanta = "binary"
            #print(f"[layout] conf_check: kanta set to {kanta}")

conf_check()
#print(f"[layout] Before kannan_otto: kanta is {kanta}")
kannan_otto(kanta)
#print(f"[layout] After kannan_otto: kanta is {kanta}")
if kanta == "binary":
    try:
        with open("nt_index.dat", 'rb') as file:
            file.close()
    except:
        with open("nt_index.dat", 'wb') as file:
            file.close()

from database_actions import (
    initialize_database,
    add_event,
    delete_event,
    edit_event,
    fetch_events_for_month#,
    #kanta
)

def resource_path(relative_path):
    
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Kuukaudet suomeksi
kuukaudet_suomeksi = [
    "Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu", "Toukokuu", "Kesäkuu",
    "Heinäkuu", "Elokuu", "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu"
]
nykyinen_kuukausi = kuukaudet_suomeksi[datetime.now().month - 1]

selected_month = None  # Tarvitaan

current_year = [datetime.now().year]
#Fontit
TITLE_FONT_SIZE = 16
TEXT_FONT_SIZE = 14

def create_layout():
    # Luo pääikkuna
    root = tk.Tk()
    root.title("Kalenterinäkymä")
    root.geometry("1200x800")
    root.configure(bg="#5CA4A9")  

    left_frame = tk.Frame(root, bg="#A7D8DE", width=300, height=600)  
    left_frame.pack(side="left", fill="y")

    # Lisää vierityspalkki ja canvas vasemmalle kehykselle
    canvas = tk.Canvas(left_frame, bg="#5CA4A9", width=300, height=600, highlightthickness=0)  
    scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#5CA4A9", width=300)  

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

    for index, month in enumerate(kuukaudet_suomeksi, start=1):
        button = create_month_button(month, index)
        button.pack(pady=10, fill="x")

    def toggle_month_view(month_index, month_name, month_button):
        global selected_month
        selected_month = month_name

        for widget in scrollable_frame.winfo_children():
            if getattr(widget, "is_calendar", False):
                widget.destroy()

        dates_frame = tk.Frame(scrollable_frame, bg="#5CA4A9", width=260)
        dates_frame.is_calendar = True
        dates_frame.pack(fill="x", pady=5, after=month_button)

        year = current_year[0]
        _, num_days = monthrange(year, month_index)

        events = fetch_events_for_month(month_index, year)
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
        year = current_year[0]
        selected_date = f"{year}-{month_index:02d}-{selected_day:02d}"

        events = fetch_events_for_month(month_index, year)
        for event in events:
            event_date, event_name, event_description = event
            if event_date == selected_date:
                events_listbox.insert(tk.END, f"{event_date}: {event_name} - {event_description}")
                events_listbox.itemconfig(tk.END, bg="#FFCCCC")
            else:
                events_listbox.insert(tk.END, f"{event_date}: {event_name} - {event_description}")

    def update_events(selected_month, events_listbox, kuukaudet_suomeksi):
        events_label.config(text=f"Tapahtumat kuukaudelle {selected_month}")
        events_listbox.delete(0, tk.END)

        month_index = kuukaudet_suomeksi.index(selected_month) + 1
        year = current_year[0]
        events = fetch_events_for_month(month_index, year)
        for event in events:
            events_listbox.insert(tk.END, f"{event[0]}: {event[1]} - {event[2]}")

    right_frame = tk.Frame(root, bg="#2a7f8e", width=600, height=400)  
    right_frame.pack(side="top", fill="both", expand=True)

    
    current_date_str = datetime.now().strftime("%d.%m.%Y")
    date_label = tk.Label(
        right_frame,
        text=f"Tänään: {current_date_str}",
        bg="#2a7f8e",
        fg="#ffffff",
        font=("Arial", 12, "bold"),
        anchor="e"
    )
    date_label.pack(side="top", anchor="ne", padx=20, pady=5)

   
    def change_year_popup():
        popup = tk.Toplevel()
        popup.title("Vaihda vuosi")
        popup.geometry("300x150")
        popup.configure(bg="#A7D8DE")

        tk.Label(popup, text="Anna uusi vuosi:", bg="#A7D8DE", font=("Arial", TEXT_FONT_SIZE)).pack(pady=10)
        year_entry = tk.Entry(popup, font=("Arial", TEXT_FONT_SIZE))
        year_entry.pack(pady=5)

        def set_year():
            new_year = year_entry.get().strip()
            if new_year.isdigit() and 1900 <= int(new_year) <= 2100:
                current_year[0] = int(new_year)
                current_year_label.config(text=f"Vuosi: {current_year[0]}")  # Päivitä vuosi
                popup.destroy()
                # Päivitä kuukausi
                if selected_month:
                    update_events(selected_month, events_listbox, kuukaudet_suomeksi)
            else:
                tk.messagebox.showerror("Virhe", "Syötä kelvollinen vuosi (1900-2100).")

        tk.Button(popup, text="Aseta vuosi", command=set_year, bg="#E0FFFF", font=("Arial", TEXT_FONT_SIZE)).pack(pady=10)

    # Lataa kuvat
    vuosi_img_path = resource_path("vuosi.png")
    poisto_img_path = resource_path("poisto.png")
    vuosi_img = tk.PhotoImage(file=vuosi_img_path)
    poisto_img = tk.PhotoImage(file=poisto_img_path)

    change_year_button = tk.Button(
        right_frame,
        text="Vaihda vuosi",
        bg="#2a7f8e",  
        activebackground="#2a7f8e",
        highlightthickness=0,
        bd=0,
        fg="#000000",
        font=("Arial", TEXT_FONT_SIZE),
        command=change_year_popup,
        image=vuosi_img,
        compound="center"
    )
    change_year_button.image = vuosi_img
    change_year_button.pack(pady=(0, 10), anchor="ne", padx=20)

    current_year_label = tk.Label(
        right_frame,
        text=f"Vuosi: {current_year[0]}",
        bg="#2a7f8e",
        highlightthickness=0,
        fg="#ffffff",
        font=("Arial", 14, "bold")
    )
    current_year_label.pack(pady=(0, 10), anchor="ne", padx=20)

    def delete_config():
        try:
            os.remove("nt_cally.cfg")
            messagebox.showinfo("Poistettu", "Asetustiedosto poistettu. Käynnistä sovellus uudelleen.")
        except FileNotFoundError:
            messagebox.showwarning("Ei löydy", "Asetustiedostoa ei löytynyt.")
        except Exception as e:
            messagebox.showerror("Virhe", f"Tiedostoa ei voitu poistaa: {e}")

    delete_config_button = tk.Button(
        right_frame,
        text="Poista asetukset",
        bg="#2a7f8e",  
        activebackground="#2a7f8e",
        highlightthickness=0,
        bd=0,
        fg="#ffffff",
        font=("Arial", TEXT_FONT_SIZE),
        command=delete_config,
        image=poisto_img,
        compound="center"
    )
    delete_config_button.image = poisto_img
    delete_config_button.pack(pady=(0, 20), anchor="ne", padx=20)

    background_image_path = resource_path("background.png")
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
            current_year[0],
            update_events
        )
    )
    add_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    if kanta != "binary":
        edit_button = tk.Button(
            bottom_frame,
            text="Muokkaa tapahtumaa",
            bg="#E0FFFF",
            fg="#000000",
            font=("Arial", TEXT_FONT_SIZE),
            command=lambda: edit_event(
                selected_month,
                events_listbox,
                None,
                None,
                None,
                kuukaudet_suomeksi,
                current_year[0],
                update_events
            )
        )
        edit_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    
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
    delete_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

    
    bottom_frame.grid_columnconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure(1, weight=1)
    bottom_frame.grid_columnconfigure(2, weight=1)

    # Valitse nykyinen kuukausi tärkeä

    current_month_index = datetime.now().month
    for button, month_index, month_name in month_buttons:
        if month_index == current_month_index:
            toggle_month_view(month_index, month_name, button)
            break

    root.mainloop()

# Suorita layout

initialize_database()
create_layout()
