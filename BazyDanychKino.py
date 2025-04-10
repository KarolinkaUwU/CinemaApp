import fdb
import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import re
from datetime import datetime

# ---- DODATKOWE IMPORTY DO RAPORTU Z WYKRESEM ----
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# =================================================
# ============== RAPORTY Z DWOMA FILTRAMI =========
# =================================================

# 1) RAPORT Z WYKRESEM
def open_chart_filter_window():
    """Okno z dwoma filtrami (data od/do), po potwierdzeniu generuje wykres."""
    filter_win = tk.Toplevel()
    filter_win.title("Filtry - Raport z wykresem")

    tk.Label(filter_win, text="Data od (RRRR-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
    start_date_entry = tk.Entry(filter_win)
    start_date_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filter_win, text="Data do (RRRR-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    end_date_entry = tk.Entry(filter_win)
    end_date_entry.grid(row=1, column=1, padx=5, pady=5)

    def generate_report():
        data_od = start_date_entry.get()
        data_do = end_date_entry.get()
        filter_win.destroy()
        generate_chart_report(data_od, data_do)

    tk.Button(filter_win, text="Generuj", command=generate_report).grid(row=2, column=0, columnspan=2, pady=10)

def generate_chart_report(data_od, data_do):
    """
    Raport z wykresem: liczy liczbę seansów dla każdej daty (DATA) w zadanym zakresie.
    Wykorzystuje tabelę SEANS i jej kolumny: DATA.
    """
    conn = fdb.connect(
        dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
        user='SYSDBA',
        password='karkap000'
    )
    cursor = conn.cursor()

    # Budujemy klauzulę WHERE w zależności od wypełnionych filtrów
    where_clauses = []
    params = []

    if data_od:
        where_clauses.append("DATA >= ?")
        params.append(data_od)
    if data_do:
        where_clauses.append("DATA <= ?")
        params.append(data_do)

    where_str = ""
    if where_clauses:
        where_str = " WHERE " + " AND ".join(where_clauses)

    query = f"""
        SELECT DATA, COUNT(*) AS LiczbaSeansow
        FROM SEANS
        {where_str}
        GROUP BY DATA
        ORDER BY DATA
    """

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    if not results:
        messagebox.showinfo("Brak danych", "Brak wyników dla wybranych filtrów.")
        return

    # Przygotuj dane do wykresu
    dates = [str(row[0]) for row in results]  # row[0] to DATA (date)
    counts = [row[1] for row in results]      # row[1] to LiczbaSeansow (int)

    # Tworzymy okno na wykres
    chart_win = tk.Toplevel()
    chart_win.title("Raport z wykresem")

    fig = Figure(figsize=(7, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(dates, counts, color='blue')
    ax.set_title("Liczba seansów w zadanym zakresie dat")
    ax.set_xlabel("Data seansu")
    ax.set_ylabel("Liczba seansów")
    ax.tick_params(axis='x', rotation=45)

    canvas = FigureCanvasTkAgg(fig, master=chart_win)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    tk.Button(chart_win, text="Zamknij", command=chart_win.destroy).pack()

# 2) RAPORT W FORMIE FORMULARZA
def open_form_filter_window():
    """Okno z dwoma filtrami (imię zawiera..., nazwisko zawiera...), generuje listę klientów."""
    form_win = tk.Toplevel()
    form_win.title("Filtry - Raport w formie formularza")

    tk.Label(form_win, text="Imię zawiera:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(form_win)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form_win, text="Nazwisko zawiera:").grid(row=1, column=0, padx=5, pady=5)
    surname_entry = tk.Entry(form_win)
    surname_entry.grid(row=1, column=1, padx=5, pady=5)

    def generate_report():
        imie_filter = name_entry.get()
        nazwisko_filter = surname_entry.get()
        form_win.destroy()
        generate_form_report(imie_filter, nazwisko_filter)

    tk.Button(form_win, text="Generuj", command=generate_report).grid(row=2, column=0, columnspan=2, pady=10)

def generate_form_report(imie_filter, nazwisko_filter):
    """
    Raport w formie formularza:
    - Wyświetla listę klientów z tabeli KLIENT, filtrując po imieniu i nazwisku (LIKE).
    """
    conn = fdb.connect(
        dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
        user='SYSDBA',
        password='karkap000'
    )
    cursor = conn.cursor()

    where_clauses = []
    params = []

    if imie_filter:
        where_clauses.append("IMIE LIKE ?")
        params.append(f"%{imie_filter}%")
    if nazwisko_filter:
        where_clauses.append("NAZWISKO LIKE ?")
        params.append(f"%{nazwisko_filter}%")

    where_str = ""
    if where_clauses:
        where_str = " WHERE " + " AND ".join(where_clauses)

    query = f"SELECT EMAIL, IMIE, NAZWISKO, NR_TEL FROM KLIENT {where_str}"
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    if not results:
        messagebox.showinfo("Brak danych", "Brak klientów pasujących do filtrów.")
        return

    result_win = tk.Toplevel()
    result_win.title("Raport w formie formularza")

    for row in results:
        # row = (EMAIL, IMIE, NAZWISKO, NR_TEL)
        info_str = f"Email: {row[0]}, Imię: {row[1]}, Nazwisko: {row[2]}, Tel: {row[3]}"
        tk.Label(result_win, text=info_str, anchor="w").pack()

    tk.Button(result_win, text="Zamknij", command=result_win.destroy).pack(pady=10)

# 3) RAPORT Z GRUPOWANIEM
def open_group_filter_window():
    """Okno z dwoma filtrami (data od/do, minimalna liczba seansów),
       generuje raport grupujący seanse po NIP."""
    group_win = tk.Toplevel()
    group_win.title("Filtry - Raport z grupowaniem")

    tk.Label(group_win, text="Data od (RRRR-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
    start_date_entry = tk.Entry(group_win)
    start_date_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(group_win, text="Data do (RRRR-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    end_date_entry = tk.Entry(group_win)
    end_date_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(group_win, text="Minimalna liczba seansów:").grid(row=2, column=0, padx=5, pady=5)
    min_count_entry = tk.Entry(group_win)
    min_count_entry.grid(row=2, column=1, padx=5, pady=5)

    def generate_report():
        data_od = start_date_entry.get()
        data_do = end_date_entry.get()
        min_count = min_count_entry.get()
        group_win.destroy()
        generate_group_report(data_od, data_do, min_count)

    tk.Button(group_win, text="Generuj", command=generate_report).grid(row=3, column=0, columnspan=2, pady=10)

def generate_group_report(data_od, data_do, min_count):
    """
    Raport z grupowaniem:
    - Zlicza liczbę seansów na każdy NIP kina (SEANS.NIP) w danym zakresie dat,
      filtruje kina mające co najmniej 'min_count' seansów.
    """
    conn = fdb.connect(
        dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
        user='SYSDBA',
        password='karkap000'
    )
    cursor = conn.cursor()

    if not min_count:
        min_count = 0

    where_clauses = []
    params = []

    if data_od:
        where_clauses.append("DATA >= ?")
        params.append(data_od)
    if data_do:
        where_clauses.append("DATA <= ?")
        params.append(data_do)

    where_str = ""
    if where_clauses:
        where_str = " WHERE " + " AND ".join(where_clauses)

    query = f"""
        SELECT NIP, COUNT(*) AS LiczbaSeansow
        FROM SEANS
        {where_str}
        GROUP BY NIP
        HAVING COUNT(*) >= ?
        ORDER BY NIP
    """
    params.append(int(min_count))

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    if not results:
        messagebox.showinfo("Brak danych", "Brak kin spełniających podane kryteria.")
        return

    result_win = tk.Toplevel()
    result_win.title("Raport z grupowaniem")

    for row in results:
        # row = (NIP, LiczbaSeansow)
        info_str = f"Kino NIP: {row[0]}, liczba seansów: {row[1]}"
        tk.Label(result_win, text=info_str).pack()

    tk.Button(result_win, text="Zamknij", command=result_win.destroy).pack(pady=10)


def initialize_db():
    conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                       user='SYSDBA', password='karkap000')
    cursor = conn.cursor()
    conn.commit()
    conn.close()

def get_user_name():
    global cinema_nip
    conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                       user='SYSDBA', password='karkap000')
    cursor = conn.cursor()
    cursor.execute("SELECT NIP FROM KINO WHERE NAZWA = ?", (chosen_cinema,))
    cinema_nip = cursor.fetchone()
    conn.close()

def register_user(email, phone, name, surname):
    conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                       user='SYSDBA', password='karkap000')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO KLIENT (EMAIL, NR_TEL, IMIE, NAZWISKO) VALUES (?, ?, ?, ?)",
                       (email, phone, name, surname))
        conn.commit()
        messagebox.showinfo("Sukces", "Zarejestrowano użytkownika!")
    except fdb.DatabaseError:
        messagebox.showerror("Error", "Użytkownik już istnieje!")
    conn.close()

def login_user(email):
    conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                       user='SYSDBA', password='karkap000')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM KLIENT WHERE EMAIL = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        messagebox.showinfo("Success", "Login successful!")
        return user
    else:
        messagebox.showerror("Error", "Invalid credentials!")
        return None

def delete_user_account(email):
    conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                       user='SYSDBA', password='karkap000')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM KLIENT WHERE EMAIL = ?", (email,))
        conn.commit()
        messagebox.showinfo("Sukces", "Właśnie usunięto Twoje konto!")
    except fdb.DatabaseError as e:
        messagebox.showerror("Error", f"Error while deleting account: {e}")
    conn.close()

def display_cinemas():
    conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                       user='SYSDBA', password='karkap000')
    cursor = conn.cursor()
    cursor.execute("SELECT NAZWA FROM KINO")
    cinemas = cursor.fetchall()
    conn.close()
    return cinemas

def display_sessions(selected_date):
    try:
        conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                           user='SYSDBA', password='karkap000')
        cursor = conn.cursor()
        if chosen_cinema == "Kino Kotkowe":
            cursor.execute("SELECT GODZINA, TYTUL_FILMU FROM SEANS WHERE DATA = ? AND NIP = 6057890321",
                           (selected_date,))
            results = cursor.fetchall()
            if not results:
                print("Brak seansów dla wybranej daty.")
                return []
            return results
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return []
    finally:
        conn.close()

def add_to_cart_ticket(quantity, transaction_id):
    conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                       user='SYSDBA', password='karkap000')
    cursor = conn.cursor()
    for _ in range(quantity):
        cursor.execute("INSERT INTO BILET_TRANZAKCJA (ID_TRANZAKCJI, ID_BILETU) VALUES (?)", (transaction_id,))
    conn.commit()
    conn.close()

def make_purchase(user_id, details):
    conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                       user='SYSDBA', password='karkap000')
    cursor = conn.cursor()
    #cursor.execute("INSERT INTO Transactions (user_id, details) VALUES (?, ?)", (user_id, details))
    conn.commit()
    messagebox.showinfo("Success", "Purchase successful!")
    conn.close()

def get_snacks_from_db():
    conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                       user='SYSDBA', password='karkap000')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PRODUKTY")
    snacks = cursor.fetchall()
    conn.close()
    return snacks

def register_window():
    def register():
        email = email_entry.get()
        phone = phone_entry.get()
        name = name_entry.get()
        surname = surname_entry.get()

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            messagebox.showerror("Error", "Invalid email format!")
            return

        phone_regex = r'^\d{9}$'
        if not re.match(phone_regex, phone):
            messagebox.showerror("Error", "Invalid phone format!")
            return

        name_regex = r'^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$'
        if not re.match(name_regex, name):
            messagebox.showerror("Error", "Invalid name format!")
            return

        if not re.match(name_regex, surname):
            messagebox.showerror("Error", "Invalid surname format!")
            return

        register_user(email, phone, name, surname)

    register_win = tk.Toplevel()
    register_win.title("Register")

    tk.Label(register_win, text="E-mail:").grid(row=0, column=0)
    email_entry = tk.Entry(register_win)
    email_entry.grid(row=0, column=1)

    tk.Label(register_win, text="Nr. Tel.:").grid(row=1, column=0)
    phone_entry = tk.Entry(register_win)
    phone_entry.grid(row=1, column=1)

    tk.Label(register_win, text="Imię:").grid(row=2, column=0)
    name_entry = tk.Entry(register_win)
    name_entry.grid(row=2, column=1)

    tk.Label(register_win, text="Nazwisko:").grid(row=3, column=0)
    surname_entry = tk.Entry(register_win)
    surname_entry.grid(row=3, column=1)

    tk.Button(register_win, text="Register", command=register).grid(row=4, column=0, columnspan=2)

def login_window():
    def login():
        email = email_entry.get()
        selected_cinema = 0
        user = login_user(email)
        if user:
            user_menu(email, selected_cinema)

    login_win = tk.Toplevel()
    login_win.title("Login")

    tk.Label(login_win, text="E-mail:").grid(row=0, column=0)
    email_entry = tk.Entry(login_win)
    email_entry.grid(row=0, column=1)

    tk.Button(login_win, text="Zaloguj", command=login).grid(row=2, column=0, columnspan=2)

def user_menu(email, selected_cinema):
    transaction_id = 1
    global chosen_cinema
    chosen_cinema = selected_cinema

    def get_user_name(email):
        conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                           user='SYSDBA', password='karkap000')
        cursor = conn.cursor()
        cursor.execute("SELECT IMIE FROM KLIENT WHERE EMAIL = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_user_surname(email):
        conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                           user='SYSDBA', password='karkap000')
        cursor = conn.cursor()
        cursor.execute("SELECT NAZWISKO FROM KLIENT WHERE EMAIL = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_user_phone(email):
        conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                           user='SYSDBA', password='karkap000')
        cursor = conn.cursor()
        cursor.execute("SELECT NR_TEL FROM KLIENT WHERE EMAIL = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    user_name = get_user_name(email)
    user_surname = get_user_surname(email)
    user_phone = get_user_phone(email)

    def konto(email, name, surname, phone):
        edit_win = tk.Toplevel()
        edit_win.title("Twoje Konto")

        tk.Label(edit_win, text="E-mail:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        email_var = tk.StringVar()
        email_var.set(email)
        email_entry = tk.Entry(edit_win, textvariable=email_var, width=30)
        email_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        tk.Label(edit_win, text="Imię:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        name_var = tk.StringVar()
        name_var.set(name)
        name_entry = tk.Entry(edit_win, textvariable=name_var, width=30)
        name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        tk.Label(edit_win, text="Nazwisko:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        surname_var = tk.StringVar()
        surname_var.set(surname)
        surname_entry = tk.Entry(edit_win, textvariable=surname_var, width=30)
        surname_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        tk.Label(edit_win, text="Nr. Tel.:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        phone_var = tk.StringVar()
        phone_var.set(phone)
        phone_entry = tk.Entry(edit_win, textvariable=phone_var, width=30)
        phone_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        def edit_name():
            new_name = name_var.get()
            conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                               user='SYSDBA', password='karkap000')
            cursor = conn.cursor()
            name_regex = r'^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$'
            if not re.match(name_regex, new_name):
                messagebox.showerror("Error", "Invalid name format!")
                return
            try:
                cursor.execute("UPDATE KLIENT SET IMIE = ? WHERE EMAIL = ?", (new_name, email))
                conn.commit()
                messagebox.showinfo("Sukces", "Imię zostało zaktualizowane!")
                # update welcome label
                update_welcome_label()
            except fdb.DatabaseError as e:
                messagebox.showerror("Błąd", f"Nie udało się zaktualizować imienia: {e}")
            conn.close()

        def edit_surname():
            new_surname = surname_var.get()
            conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                               user='SYSDBA', password='karkap000')
            cursor = conn.cursor()
            name_regex = r'^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$'
            if not re.match(name_regex, new_surname):
                messagebox.showerror("Error", "Invalid surname format!")
                return
            try:
                cursor.execute("UPDATE KLIENT SET NAZWISKO = ? WHERE EMAIL = ?", (new_surname, email))
                conn.commit()
                messagebox.showinfo("Sukces", "Nazwisko zostało zaktualizowane!")
            except fdb.DatabaseError as e:
                messagebox.showerror("Błąd", f"Nie udało się zaktualizować nazwiska: {e}")
            conn.close()

        def edit_phone():
            new_phone = phone_var.get()
            conn = fdb.connect(dsn=r'C:\Users\ciast\OneDrive\Dokumenty\Projekt Bazy Danych\KINO.FDB',
                               user='SYSDBA', password='karkap000')
            cursor = conn.cursor()
            phone_regex = r'^\d{9}$'
            if not re.match(phone_regex, new_phone):
                messagebox.showerror("Error", "Invalid phone format!")
                return
            try:
                cursor.execute("UPDATE KLIENT SET NR_TEL = ? WHERE EMAIL = ?", (new_phone, email))
                conn.commit()
                messagebox.showinfo("Sukces", "Nr. Tel. zostało zaktualizowane!")
            except fdb.DatabaseError as e:
                messagebox.showerror("Błąd", f"Nie udało się zaktualizować numeru telefonu: {e}")
            conn.close()

        tk.Button(edit_win, text="Edytuj", width=20, command=edit_name).grid(row=1, column=2, padx=10, pady=10)
        tk.Button(edit_win, text="Edytuj", width=20, command=edit_surname).grid(row=2, column=2, padx=10, pady=10)
        tk.Button(edit_win, text="Edytuj", width=20, command=edit_phone).grid(row=3, column=2, padx=10, pady=10)

        tk.Button(edit_win, text="Usuń konto", width=20, bg="red",
                  command=lambda: delete_user_account(email)).grid(row=4, column=0, columnspan=3, pady=20)
        tk.Button(edit_win, text="Cofnij", width=20, command=edit_win.destroy).grid(row=5, column=0, columnspan=3, pady=10)

    def view_cinemas():
        cinemas = display_cinemas()
        cinema_win = tk.Toplevel()
        cinema_win.title("Kino")

        cinema_listbox = tk.Listbox(cinema_win)
        cinema_listbox.pack()

        for cinema in cinemas:
            cinema_listbox.insert(tk.END, cinema[0])

        def select_cinema():
            selected_cinema_index = cinema_listbox.curselection()
            if selected_cinema_index:
                selected_cinema_name = cinema_listbox.get(selected_cinema_index)
                global chosen_cinema
                chosen_cinema = selected_cinema_name
                cinema_win.destroy()
                update_welcome_label()
                enable_view_sessions_button()

        def enable_view_sessions_button(*args):
            if chosen_cinema != 0 and chosen_cinema != "brak":
                seans.config(state="normal")
                snacks.config(state="normal")
            else:
                seans.config(state="disabled")
                snacks.config(state="disabled")

        tk.Button(cinema_win, text="Wybierz kino", command=select_cinema).pack()

    def update_welcome_label():
        global chosen_cinema
        if chosen_cinema == 0:
            chosen_cinema_name = "brak"
            u_name = get_user_name(email) or "Gość"
            welcome_label.config(text=f"Witaj {u_name}!\nAktualnie wybrane kino: {chosen_cinema_name}")
        else:
            chosen_cinema_name = chosen_cinema
            u_name = get_user_name(email) or "Gość"
            welcome_label.config(text=f"Witaj {u_name}!\nAktualnie wybrane kino: {chosen_cinema_name}")

    def view_sessions(selected_cinema):
        session_win = tk.Toplevel()
        session_win.title("Wybierz datę seansu")

        cal = Calendar(session_win, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(pady=10, padx=10)

        def get_selected_date():
            selected_date = cal.get_date()
            sessions = display_sessions(selected_date)
            sessions_win = tk.Toplevel()
            sessions_win.title("Seanse")

            if not sessions:
                messagebox.showinfo("Brak seansów", f"Brak seansów dla wybranego dnia: {selected_date}")
                return

            ticket_vars = []
            for session in sessions:
                time_obj = session[0]
                formatted_time = time_obj.strftime("%H:%M")
                session_info = f"{formatted_time} {session[1]}"
                tk.Label(sessions_win, text=session_info).pack()
                ticket_var = tk.IntVar(value=0)
                ticket_vars.append(ticket_var)
                tk.Entry(sessions_win, textvariable=ticket_var, width=5).pack()

            tk.Button(sessions_win, text="Dodaj do koszyka",
                      command=lambda: add_to_cart_ticket(sum(var.get() for var in ticket_vars), transaction_id)
                      ).pack(pady=10)

            tk.Button(sessions_win, text="Cofnij", command=sessions_win.destroy).pack(pady=10)

        tk.Button(session_win, text="Zobacz seanse", command=get_selected_date).pack(pady=10)

    def view_snacks():
        snacks_data = get_snacks_from_db()

        def add_to_cart():
            for snack, entry in zip(snacks_data, quantity_entries):
                quantity = entry.get()
                if quantity:
                    print(f"Dodano do koszyka: {snack[1]} x {quantity} szt.")

        def go_back():
            snack_win.destroy()

        snack_win = tk.Toplevel()
        snack_win.title("Przekąski")

        tk.Label(snack_win, text="Nazwa").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(snack_win, text="Cena").grid(row=0, column=1, padx=10, pady=5)
        tk.Label(snack_win, text="Rozmiar").grid(row=0, column=2, padx=10, pady=5)
        tk.Label(snack_win, text="Ilość").grid(row=0, column=3, padx=10, pady=5)

        quantity_entries = []
        for index, snack in enumerate(snacks_data, start=1):
            tk.Label(snack_win, text=snack[1]).grid(row=index, column=0, padx=10, pady=5)
            tk.Label(snack_win, text=f"${snack[2]:.2f}").grid(row=index, column=1, padx=10, pady=5)
            tk.Label(snack_win, text=snack[3]).grid(row=index, column=2, padx=10, pady=5)
            quantity_entry = tk.Entry(snack_win)
            quantity_entry.grid(row=index, column=3, padx=10, pady=5)
            quantity_entries.append(quantity_entry)

        tk.Button(snack_win, text="Dodaj do koszyka", command=add_to_cart).grid(
            row=len(snacks_data)+1, column=0, columnspan=2, pady=10
        )
        tk.Button(snack_win, text="Cofnij", command=go_back).grid(
            row=len(snacks_data)+1, column=2, columnspan=2, pady=10
        )

    def view_transactions():
        # jeżeli masz implementację display_transactions, możesz tutaj dać
        # transakcje = display_transactions(user_id)
        # ...
        messagebox.showinfo("Koszyk", "Tutaj wyświetl transakcje lub koszyk :)")

    user_win = tk.Toplevel()
    user_win.title("User Menu")

    if selected_cinema == 0:
        selected_cinema = "brak"

    welcome_label = tk.Label(
        user_win,
        text=f"Witaj {user_name}!\nAktualnie wybrane kino: {selected_cinema}",
        font=("Arial", 16)
    )
    welcome_label.pack(pady=10)

    tk.Button(user_win, text="Konto", command=lambda: konto(email, user_name, user_surname, user_phone)).pack()
    tk.Button(user_win, text="Przeglądaj kina", command=view_cinemas).pack()
    seans = tk.Button(user_win, text="Przeglądaj seanse", state="disabled", command=lambda: view_sessions(selected_cinema))
    seans.pack()
    snacks = tk.Button(user_win, text="Przeglądaj przekąski", state="disabled", command=view_snacks)
    snacks.pack()
    tk.Button(user_win, text="Zobacz swój koszyk", command=view_transactions).pack()

initialize_db()
root = tk.Tk()
root.title("Kino")

welcome_label = tk.Label(root, text="Witaj!", font=("Arial", 16))
welcome_label.pack()

register_button = tk.Button(root, text="Załóż konto", command=register_window)
register_button.pack()

login_button = tk.Button(root, text="Zaloguj się", command=login_window)
login_button.pack()

# --- DODAJEMY TRZY PRZYCISKI DO RAPORTÓW ---
report_chart_button = tk.Button(root, text="Raport z wykresem (filtry)", command=open_chart_filter_window)
report_chart_button.pack()

report_form_button = tk.Button(root, text="Raport w formie formularza (filtry)", command=open_form_filter_window)
report_form_button.pack()

report_group_button = tk.Button(root, text="Raport z grupowaniem (filtry)", command=open_group_filter_window)
report_group_button.pack()

exit_button = tk.Button(root, text="Wyjdź", command=root.quit)
exit_button.pack()

root.mainloop()
