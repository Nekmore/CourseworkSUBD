import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient

# Подключение к базе данных MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["autoservice"]

# Функции для работы с базой данных
def add_master(first_name, last_name, middle_name, grade, specialization):
    master = {
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "grade": grade,
        "specialization": specialization
    }
    db.masters.insert_one(master)
    messagebox.showinfo("Успех", f"Мастер {first_name} {last_name} добавлен.")

def add_car(brand, year, registration_number):
    car = {
        "brand": brand,
        "year": year,
        "registration_number": registration_number
    }
    db.cars.insert_one(car)
    messagebox.showinfo("Успех", f"Автомобиль {brand} с регистрационным номером {registration_number} добавлен.")

def add_work(car_registration_number, master_id, hours_worked, hourly_rate, problem_description, work_description):
    car = db.cars.find_one({"registration_number": car_registration_number})
    if not car:
        messagebox.showerror("Ошибка", "Автомобиль с таким регистрационным номером не найден.")
        return

    work = {
        "car_id": car["_id"],
        "master_id": master_id,
        "hours_worked": hours_worked,
        "hourly_rate": hourly_rate,
        "problem_description": problem_description,
        "work_description": work_description
    }
    db.works.insert_one(work)
    messagebox.showinfo("Успех", "Работа успешно добавлена.")

def generate_report(car_registration_number):
    # Поиск автомобиля по регистрационному номеру
    car = db.cars.find_one({"registration_number": car_registration_number})
    if not car:
        messagebox.showerror("Ошибка", "Автомобиль с таким регистрационным номером не найден.")
        return

    car_id = car["_id"]
    works = db.works.find({"car_id": car_id})

    report = {}
    total_earnings = 0  # Общая сумма заработка
    work_details = []   # Список для хранения деталей работ

    for work in works:
        master_id = work["master_id"]
        earnings = work["hours_worked"] * work["hourly_rate"]
        total_earnings += earnings  # Добавляем к общей сумме заработка

        # Детали выполненной работы
        work_details.append({
            "problem_description": work["problem_description"],
            "work_description": work["work_description"],
            "earnings": earnings
        })

        # Группировка заработка по мастерам
        if master_id not in report:
            master = db.masters.find_one({"_id": master_id})
            if not master:
                continue
            report[master_id] = {
                "name": f"{master['first_name']} {master['last_name']}",
                "total_earnings": 0
            }

        report[master_id]["total_earnings"] += earnings

    # Формирование текста отчета
    report_text = f"Отчет по автомобилю {car_registration_number}:\n\n"

    # Детализация выполненных работ
    report_text += "Детали выполненных работ:\n"
    for detail in work_details:
        report_text += (
            f"- Проблема: {detail['problem_description']}, "
            f"Решение: {detail['work_description']}, "
            f"Стоимость: {detail['earnings']} руб.\n"
        )

    # Итог по мастерам
    report_text += "\nЗаработок мастеров:\n"
    for master_id, data in report.items():
        report_text += f"Мастер: {data['name']}, Сумма заработка: {data['total_earnings']} руб.\n"

    # Общая сумма заработка
    report_text += f"\nОбщая сумма заработка по автомобилю: {total_earnings} руб."

    # Вывод отчета
    if report or work_details:
        messagebox.showinfo("Отчет", report_text)
    else:
        messagebox.showinfo("Отчет", "Работы с этим автомобилем не найдены.")

def update_masters_view():
    for row in tree_masters.get_children():
        tree_masters.delete(row)

    masters = db.masters.find()
    for master in masters:
        tree_masters.insert("", "end", values=(master["first_name"], master["last_name"], master["middle_name"], master["grade"], master["specialization"]))

def update_cars_view():
    for row in tree_cars.get_children():
        tree_cars.delete(row)

    cars = db.cars.find()
    for car in cars:
        tree_cars.insert("", "end", values=(car["brand"], car["year"], car["registration_number"]))

def update_works_view():
    for row in tree_works.get_children():
        tree_works.delete(row)

    works = db.works.find()
    for work in works:
        car = db.cars.find_one({"_id": work["car_id"]})
        master = db.masters.find_one({"_id": work["master_id"]})

        car_reg = car["registration_number"] if car else "Не найдено"
        master_name = f"{master['first_name']} {master['last_name']}" if master else "Не найдено"
        
        tree_works.insert("", "end", values=(
            car_reg,
            master_name,
            work["problem_description"],
            work["work_description"],
            work["hours_worked"],
            work["hourly_rate"],
            work["hours_worked"] * work["hourly_rate"]
        ))

# Создание графического интерфейса
root = tk.Tk()
root.title("Система управления автосервисом")
root.geometry("800x600")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Вкладка добавления данных
frame_add = ttk.Frame(notebook)
notebook.add(frame_add, text="Добавить данные")

# Вкладка отчета
frame_report = ttk.Frame(notebook)
notebook.add(frame_report, text="Отчет")

# Вкладка просмотра мастеров
frame_masters = ttk.Frame(notebook)
notebook.add(frame_masters, text="Мастера")

# Вкладка просмотра автомобилей
frame_cars = ttk.Frame(notebook)
notebook.add(frame_cars, text="Автомобили")

# Вкладка просмотра работ
frame_works = ttk.Frame(notebook)
notebook.add(frame_works, text="Работы")

# Элементы для добавления данных
frame_add_master = ttk.Labelframe(frame_add, text="Добавить мастера")
frame_add_master.pack(fill="x", padx=10, pady=5)

tk.Label(frame_add_master, text="Имя:").grid(row=0, column=0)
entry_first_name = ttk.Entry(frame_add_master)
entry_first_name.grid(row=0, column=1)

tk.Label(frame_add_master, text="Фамилия:").grid(row=1, column=0)
entry_last_name = ttk.Entry(frame_add_master)
entry_last_name.grid(row=1, column=1)

tk.Label(frame_add_master, text="Отчество:").grid(row=2, column=0)
entry_middle_name = ttk.Entry(frame_add_master)
entry_middle_name.grid(row=2, column=1)

tk.Label(frame_add_master, text="Разряд:").grid(row=3, column=0)
entry_grade = ttk.Entry(frame_add_master)
entry_grade.grid(row=3, column=1)

tk.Label(frame_add_master, text="Специализация:").grid(row=4, column=0)
entry_specialization = ttk.Entry(frame_add_master)
entry_specialization.grid(row=4, column=1)

def submit_master():
    add_master(entry_first_name.get(), entry_last_name.get(), entry_middle_name.get(), int(entry_grade.get()), entry_specialization.get())
    update_masters_view()

btn_add_master = ttk.Button(frame_add_master, text="Добавить", command=submit_master)
btn_add_master.grid(row=5, columnspan=2, pady=5)

frame_add_car = ttk.Labelframe(frame_add, text="Добавить автомобиль")
frame_add_car.pack(fill="x", padx=10, pady=5)

tk.Label(frame_add_car, text="Марка:").grid(row=0, column=0)
entry_brand = ttk.Entry(frame_add_car)
entry_brand.grid(row=0, column=1)

tk.Label(frame_add_car, text="Год выпуска:").grid(row=1, column=0)
entry_year = ttk.Entry(frame_add_car)
entry_year.grid(row=1, column=1)

tk.Label(frame_add_car, text="Регистрационный номер:").grid(row=2, column=0)
entry_registration_number = ttk.Entry(frame_add_car)
entry_registration_number.grid(row=2, column=1)

def submit_car():
    add_car(entry_brand.get(), int(entry_year.get()), entry_registration_number.get())
    update_cars_view()

btn_add_car = ttk.Button(frame_add_car, text="Добавить", command=submit_car)
btn_add_car.grid(row=3, columnspan=2, pady=5)



frame_add_work = ttk.Labelframe(frame_add, text="Добавить выполненную работу")
frame_add_work.pack(fill="x", padx=10, pady=5)

tk.Label(frame_add_work, text="Регистрационный номер машины:").grid(row=0, column=0)
entry_work_car_reg = ttk.Entry(frame_add_work)
entry_work_car_reg.grid(row=0, column=1)

tk.Label(frame_add_work, text="ID мастера:").grid(row=1, column=0)
entry_work_master_id = ttk.Entry(frame_add_work)
entry_work_master_id.grid(row=1, column=1)

tk.Label(frame_add_work, text="Часы работы:").grid(row=2, column=0)
entry_work_hours = ttk.Entry(frame_add_work)
entry_work_hours.grid(row=2, column=1)

tk.Label(frame_add_work, text="Ставка за час:").grid(row=3, column=0)
entry_work_rate = ttk.Entry(frame_add_work)
entry_work_rate.grid(row=3, column=1)

tk.Label(frame_add_work, text="Описание проблемы:").grid(row=4, column=0)
entry_work_problem = ttk.Entry(frame_add_work)
entry_work_problem.grid(row=4, column=1)

tk.Label(frame_add_work, text="Описание работы:").grid(row=5, column=0)
entry_work_description = ttk.Entry(frame_add_work)
entry_work_description.grid(row=5, column=1)

def submit_work():
    add_work(
        entry_work_car_reg.get(),
        entry_work_master_id.get(),
        float(entry_work_hours.get()),
        float(entry_work_rate.get()),
        entry_work_problem.get(),
        entry_work_description.get()
    )
    update_works_view()

btn_add_work = ttk.Button(frame_add_work, text="Добавить работу", command=submit_work)
btn_add_work.grid(row=6, columnspan=2, pady=5)


# Элементы для просмотра мастеров
frame_masters_view = ttk.Frame(frame_masters)
frame_masters_view.pack(fill="both", expand=True, padx=10, pady=5)

scrollbar_masters = ttk.Scrollbar(frame_masters_view, orient="vertical")
tree_masters = ttk.Treeview(frame_masters_view, columns=("Имя", "Фамилия", "Отчество", "Разряд", "Специализация"), show="headings", yscrollcommand=scrollbar_masters.set)
scrollbar_masters.config(command=tree_masters.yview)
scrollbar_masters.pack(side="right", fill="y")

tree_masters.heading("Имя", text="Имя")
tree_masters.heading("Фамилия", text="Фамилия")
tree_masters.heading("Отчество", text="Отчество")
tree_masters.heading("Разряд", text="Разряд")
tree_masters.heading("Специализация", text="Специализация")
tree_masters.pack(fill="both", expand=True)

# Элементы для просмотра автомобилей
frame_cars_view = ttk.Frame(frame_cars)
frame_cars_view.pack(fill="both", expand=True, padx=10, pady=5)

scrollbar_cars = ttk.Scrollbar(frame_cars_view, orient="vertical")
tree_cars = ttk.Treeview(frame_cars_view, columns=("Марка", "Год", "Регистрационный номер"), show="headings", yscrollcommand=scrollbar_cars.set)
scrollbar_cars.config(command=tree_cars.yview)
scrollbar_cars.pack(side="right", fill="y")

tree_cars.heading("Марка", text="Марка")
tree_cars.heading("Год", text="Год")
tree_cars.heading("Регистрационный номер", text="Регистрационный номер")
tree_cars.pack(fill="both", expand=True)

# Элементы для просмотра работ
frame_works_view = ttk.Frame(frame_works)
frame_works_view.pack(fill="both", expand=True, padx=10, pady=5)

scrollbar_works = ttk.Scrollbar(frame_works_view, orient="vertical")
tree_works = ttk.Treeview(frame_works_view, columns=("Машина", "Мастер", "Описание проблемы", "Описание работы", "Часы", "Ставка", "Стоимость"), show="headings", yscrollcommand=scrollbar_works.set)
scrollbar_works.config(command=tree_works.yview)
scrollbar_works.pack(side="right", fill="y")

tree_works.heading("Машина", text="Машина")
tree_works.heading("Мастер", text="Мастер")
tree_works.heading("Описание проблемы", text="Описание проблемы")
tree_works.heading("Описание работы", text="Описание работы")
tree_works.heading("Часы", text="Часы")
tree_works.heading("Ставка", text="Ставка")
tree_works.heading("Стоимость", text="Стоимость")
tree_works.pack(fill="both", expand=True)

# Элементы для формирования отчета
frame_generate_report = ttk.Labelframe(frame_report, text="Создать отчет по автомобилю")
frame_generate_report.pack(fill="x", padx=10, pady=5)

tk.Label(frame_generate_report, text="Регистрационный номер:").grid(row=0, column=0, padx=5, pady=5)
entry_report_car_number = ttk.Entry(frame_generate_report)
entry_report_car_number.grid(row=0, column=1, padx=5, pady=5)

def submit_report():
    generate_report(entry_report_car_number.get())

btn_generate_report = ttk.Button(frame_generate_report, text="Создать отчет", command=submit_report)
btn_generate_report.grid(row=1, columnspan=2, pady=10)


# Начальная загрузка данных
update_masters_view()
update_cars_view()
update_works_view()

root.mainloop()
