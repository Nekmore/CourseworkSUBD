import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson.objectid import ObjectId

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

def update_master(master_id, first_name, last_name, middle_name, grade, specialization):
    db.masters.update_one({"_id": ObjectId(master_id)}, {"$set": {
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "grade": grade,
        "specialization": specialization
    }})
    messagebox.showinfo("Успех", "Данные мастера обновлены.")

def delete_master(master_id):
    db.masters.delete_one({"_id": ObjectId(master_id)})
    messagebox.showinfo("Успех", "Мастер удален.")

def add_car(brand, year, registration_number):
    car = {
        "brand": brand,
        "year": year,
        "registration_number": registration_number
    }
    db.cars.insert_one(car)
    messagebox.showinfo("Успех", f"Автомобиль {brand} с регистрационным номером {registration_number} добавлен.")

def update_car(car_id, brand, year, registration_number):
    db.cars.update_one({"_id": ObjectId(car_id)}, {"$set": {
        "brand": brand,
        "year": year,
        "registration_number": registration_number
    }})
    messagebox.showinfo("Успех", "Данные автомобиля обновлены.")

def delete_car(car_id):
    db.cars.delete_one({"_id": ObjectId(car_id)})
    messagebox.showinfo("Успех", "Автомобиль удален.")

def add_work(car_registration_number, master_id, hours_worked, hourly_rate, problem_description, work_description):
    masterfl = master_id.split()
    master = db.masters.find_one({"first_name": masterfl[0], "last_name": masterfl[1]})
    if not master:
        messagebox.showerror("Ошибка", "Мастера с такиим именем не существует.")
        return
    car = db.cars.find_one({"registration_number": car_registration_number})
    if not car:
        messagebox.showerror("Ошибка", "Автомобиль с таким регистрационным номером не найден.")
        return

    work = {
        "car_id": car["_id"],
        "master_id": master["_id"],
        "hours_worked": int(hours_worked),
        "hourly_rate": int(hourly_rate),
        "problem_description": problem_description,
        "work_description": work_description
    }
    db.works.insert_one(work)
    messagebox.showinfo("Успех", "Работа успешно добавлена.")

def update_work(work_id, car_registration_number, master_id, problem_description, work_description, hours_worked, hourly_rate):
    masterfl = master_id.split()
    master = db.masters.find_one({"first_name": masterfl[0], "last_name": masterfl[1]})
    if not master:
        messagebox.showerror("Ошибка", "Мастера с такиим именем не существует.")
        return
    car = db.cars.find_one({"registration_number": car_registration_number})
    if not car:
        messagebox.showerror("Ошибка", "Автомобиль с таким регистрационным номером не найден.")
        return
    db.works.update_one({"_id": ObjectId(work_id)}, {"$set": {
        "master_id": master["_id"],
        "car_id": car["_id"],
        "hours_worked": int(hours_worked),
        "hourly_rate": int(hourly_rate),
        "problem_description": problem_description,
        "work_description": work_description
    }})
#    entry_work_id.get(),
 #       entry_work_car.get(),
 #       entry_work_master.get(),
 #       entry_work_problem.get(),
 #       entry_work_description.get(),
#        entry_work_hours.get(),
  #      entry_work_rate.get()
    messagebox.showinfo("Успех", "Данные работы обновлены.")

def delete_work(work_id):
    db.works.delete_one({"_id": ObjectId(work_id)})
    messagebox.showinfo("Успех", "Работа удалена.")

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

# Функции обновления интерфейса
def update_masters_view():
    for row in tree_masters.get_children():
        tree_masters.delete(row)
    masters = db.masters.find()
    for master in masters:
        tree_masters.insert("", "end", values=(master["_id"], master["first_name"], master["last_name"], master["middle_name"], master["grade"], master["specialization"]))

def update_cars_view():
    for row in tree_cars.get_children():
        tree_cars.delete(row)
    cars = db.cars.find()
    for car in cars:
        tree_cars.insert("", "end", values=(car["_id"], car["brand"], car["year"], car["registration_number"]))

def update_works_view():
    for row in tree_works.get_children():
        tree_works.delete(row)
    works = db.works.find()
    for work in works:
        car = db.cars.find_one({"_id": work["car_id"]})
        master = db.masters.find_one({"_id": work["master_id"]})
        tree_works.insert("", "end", values=(work["_id"], car["registration_number"] if car else "Не найдено", master["first_name"] + " " + master["last_name"] if master else "Не найдено", work["problem_description"], work["work_description"], work["hours_worked"], work["hourly_rate"], work["hours_worked"] * work["hourly_rate"]))
#

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

tk.Label(frame_add_work, text="Мастер:").grid(row=1, column=0)
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
        entry_work_hours.get(),
        entry_work_rate.get(),
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
tree_masters = ttk.Treeview(frame_masters_view, columns=("ID", "Имя", "Фамилия", "Отчество", "Разряд", "Специализация"), show="headings", yscrollcommand=scrollbar_masters.set)
scrollbar_masters.config(command=tree_masters.yview)
scrollbar_masters.pack(side="right", fill="y")

tree_masters.heading("ID", text="ID")
tree_masters.heading("Имя", text="Имя")
tree_masters.heading("Фамилия", text="Фамилия")
tree_masters.heading("Отчество", text="Отчество")
tree_masters.heading("Разряд", text="Разряд")
tree_masters.heading("Специализация", text="Специализация")
tree_masters.pack(fill="both", expand=True)

frame_edit_master = ttk.Labelframe(frame_masters, text="Изменение/Удаление мастера")
frame_edit_master.pack(fill="x", padx=10, pady=5)

tk.Label(frame_edit_master, text="ID мастера:").grid(row=0, column=0)
entry_master_id = ttk.Entry(frame_edit_master)
entry_master_id.grid(row=0, column=1)

tk.Label(frame_edit_master, text="Имя:").grid(row=1, column=0)
entry_edit_first_name = ttk.Entry(frame_edit_master)
entry_edit_first_name.grid(row=1, column=1)

tk.Label(frame_edit_master, text="Фамилия:").grid(row=2, column=0)
entry_edit_last_name = ttk.Entry(frame_edit_master)
entry_edit_last_name.grid(row=2, column=1)

tk.Label(frame_edit_master, text="Отчество:").grid(row=3, column=0)
entry_edit_middle_name = ttk.Entry(frame_edit_master)
entry_edit_middle_name.grid(row=3, column=1)

tk.Label(frame_edit_master, text="Разряд:").grid(row=4, column=0)
entry_edit_grade = ttk.Entry(frame_edit_master)
entry_edit_grade.grid(row=4, column=1)

tk.Label(frame_edit_master, text="Специализация:").grid(row=5, column=0)
entry_edit_specialization = ttk.Entry(frame_edit_master)
entry_edit_specialization.grid(row=5, column=1)

def submit_update_master():
    update_master(entry_master_id.get(), entry_edit_first_name.get(), entry_edit_last_name.get(), entry_edit_middle_name.get(), int(entry_edit_grade.get()), entry_edit_specialization.get())
    update_masters_view()

def submit_delete_master():
    delete_master(entry_master_id.get())
    update_masters_view()

btn_update_master = ttk.Button(frame_edit_master, text="Изменить", command=submit_update_master)
btn_update_master.grid(row=6, column=0, pady=5)

btn_delete_master = ttk.Button(frame_edit_master, text="Удалить", command=submit_delete_master)
btn_delete_master.grid(row=6, column=1, pady=5)

# Элементы для просмотра автомобилей
tree_cars = ttk.Treeview(frame_cars, columns=("ID", "Марка", "Год", "Регистрационный номер"), show="headings")
tree_cars.heading("ID", text="ID")
tree_cars.heading("Марка", text="Марка")
tree_cars.heading("Год", text="Год")
tree_cars.heading("Регистрационный номер", text="Регистрационный номер")
tree_cars.pack(fill="both", expand=True)

frame_edit_car = ttk.Labelframe(frame_cars, text="Изменение/Удаление автомобиля")
frame_edit_car.pack(fill="x", padx=10, pady=5)

tk.Label(frame_edit_car, text="ID автомобиля:").grid(row=0, column=0)
entry_car_id = ttk.Entry(frame_edit_car)
entry_car_id.grid(row=0, column=1)

tk.Label(frame_edit_car, text="Марка:").grid(row=1, column=0)
entry_car_brand = ttk.Entry(frame_edit_car)
entry_car_brand.grid(row=1, column=1)

tk.Label(frame_edit_car, text="Год:").grid(row=2, column=0)
entry_car_year = ttk.Entry(frame_edit_car)
entry_car_year.grid(row=2, column=1)

tk.Label(frame_edit_car, text="Регистрационный номер:").grid(row=3, column=0)
entry_car_number = ttk.Entry(frame_edit_car)
entry_car_number.grid(row=3, column=1)


def submit_update_car():
    update_car(entry_car_id.get(), entry_car_brand.get(), entry_car_year.get(), entry_car_number.get())
    update_cars_view()

def submit_delete_car():
    delete_car(entry_car_id.get())
    update_cars_view()

btn_update_car = ttk.Button(frame_edit_car, text="Изменить", command=submit_update_car)
btn_update_car.grid(row=4, column=0, pady=5)

btn_delete_car = ttk.Button(frame_edit_car, text="Удалить", command=submit_delete_car)
btn_delete_car.grid(row=4, column=1, pady=5)

# Элементы для просмотра работ
frame_works_view = ttk.Frame(frame_works)
frame_works_view.pack(fill="both", expand=True, padx=10, pady=5)

scrollbar_works = ttk.Scrollbar(frame_works_view, orient="vertical")
tree_works = ttk.Treeview(frame_works_view, columns=("Id работы", "Номер машины", "Мастер", "Описание проблемы", "Описание работы", "Часы", "Ставка"), show="headings", yscrollcommand=scrollbar_works.set)
scrollbar_works.config(command=tree_works.yview)
scrollbar_works.pack(side="right", fill="y")

tree_works.heading("Id работы", text="Id работы")
tree_works.heading("Номер машины", text="Номер машины")
tree_works.heading("Мастер", text="Мастер")
tree_works.heading("Описание проблемы", text="Описание проблемы")
tree_works.heading("Описание работы", text="Описание работы")
tree_works.heading("Часы", text="Часы")
tree_works.heading("Ставка", text="Ставка")
tree_works.pack(fill="both", expand=True)

# Элементы для просмотра работ с возможностью изменения и удаления
frame_edit_work = ttk.Labelframe(frame_works, text="Изменение/Удаление работы")
frame_edit_work.pack(fill="x", padx=10, pady=5)

# Поля для ввода данных о работе
tk.Label(frame_edit_work, text="ID работы:").grid(row=0, column=0)
entry_work_id = ttk.Entry(frame_edit_work)
entry_work_id.grid(row=0, column=1)

# Поля для изменения данных

# Машина
tk.Label(frame_edit_work, text="Машина:").grid(row=1, column=0)
entry_work_car = ttk.Entry(frame_edit_work)
entry_work_car.grid(row=1, column=1)

# Мастер
tk.Label(frame_edit_work, text="Мастер:").grid(row=2, column=0)
entry_work_master = ttk.Entry(frame_edit_work)
entry_work_master.grid(row=2, column=1)

# Описание проблемы
tk.Label(frame_edit_work, text="Описание проблемы:").grid(row=3, column=0)
entry_work_problem = ttk.Entry(frame_edit_work)
entry_work_problem.grid(row=3, column=1)

# Описание работы
tk.Label(frame_edit_work, text="Описание работы:").grid(row=4, column=0)
entry_work_description = ttk.Entry(frame_edit_work)
entry_work_description.grid(row=4, column=1)

# Часы работы
tk.Label(frame_edit_work, text="Часы:").grid(row=5, column=0)
entry_work_hours = ttk.Entry(frame_edit_work)
entry_work_hours.grid(row=5, column=1)

# Ставка
tk.Label(frame_edit_work, text="Ставка:").grid(row=6, column=0)
entry_work_rate = ttk.Entry(frame_edit_work)
entry_work_rate.grid(row=6, column=1)

# Функции для обработки изменений и удаления
def submit_update_work():
    update_work(
        entry_work_id.get(),
        entry_work_car.get(),
        entry_work_master.get(),
        entry_work_problem.get(),
        entry_work_description.get(),
        entry_work_hours.get(),
        entry_work_rate.get()
    )
    update_works_view()

def submit_delete_work():
    delete_work(entry_work_id.get())
    update_works_view()

# Кнопки для изменения и удаления работы
btn_update_work = ttk.Button(frame_edit_work, text="Изменить", command=submit_update_work)
btn_update_work.grid(row=7, column=0, pady=5)

btn_delete_work = ttk.Button(frame_edit_work, text="Удалить", command=submit_delete_work)
btn_delete_work.grid(row=7, column=1, pady=5)

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
