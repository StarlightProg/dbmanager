import os
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, Toplevel, Frame, OptionMenu, StringVar, simpledialog

class DatabaseManagementSystem:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def create_database(self, db_name):
        """Создает новую базу данных."""
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        print(f"База данных '{db_name}' создана.")

    def execute_query(self, query):
        """Выполняет SQL-запрос."""
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Запрос выполнен успешно.")
        except sqlite3.Error as e:
            print(f"Ошибка: {e}")

    def import_data(self, file_path):
        """Импортирует данные из файла."""
        ext = os.path.splitext(file_path)[1]
        if ext == '.csv':
            data = pd.read_csv(file_path)
        elif ext == '.xls' or ext == '.xlsx':
            data = pd.read_excel(file_path)
        elif ext == '.txt':
            data = pd.read_table(file_path)
        else:
            raise ValueError("Формат файла не поддерживается.")

        return data

    def export_data(self, data, file_path):
        """Экспортирует данные в файл."""
        ext = os.path.splitext(file_path)[1]
        if ext == '.csv':
            data.to_csv(file_path, index=False)
        elif ext == '.xls' or ext == '.xlsx':
            data.to_excel(file_path, index=False)
        elif ext == '.txt':
            data.to_csv(file_path, sep='\t', index=False)
        else:
            raise ValueError("Формат файла не поддерживается.")

        print(f"Данные сохранены в {file_path}.")

    def save_sql(self, sql_statements, file_path):
        """Сохраняет SQL-запросы в файл."""
        with open(file_path, 'w') as f:
            f.write(sql_statements)
        print(f"SQL-запросы сохранены в файл {file_path}.")

    def visualize_data(self, query):
        """Визуализирует данные из SQL-запроса."""
        try:
            data = pd.read_sql_query(query, self.connection)
            data.plot(kind='bar', figsize=(10, 5))
            plt.title("Визуализация данных")
            plt.show()
        except Exception as e:
            print(f"Ошибка при визуализации: {e}")

    def get_table_structure(self):
        """Получает структуру всех таблиц в базе данных."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        table_info = {}
        for table in tables:
            table_name = table[0]
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            columns = self.cursor.fetchall()
            table_info[table_name] = columns
        return table_info

class GUI:
    def __init__(self, root):
        self.dbms = DatabaseManagementSystem()
        self.root = root
        self.root.title("Система управления базами данных")

        Label(root, text="Выберите действие:").pack(pady=10)

        Button(root, text="Создать базу данных", command=self.open_create_database_window).pack(pady=5)
        Button(root, text="Импортировать данные", command=self.import_data).pack(pady=5)
        Button(root, text="Экспортировать данные", command=self.export_data).pack(pady=5)
        Button(root, text="Визуализировать структуру таблиц", command=self.visualize_structure).pack(pady=5)

    def open_create_database_window(self):
        db_name = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite DB", "*.db")])
        if db_name:
            self.dbms.create_database(db_name)
            self.open_create_table_window()

    def open_create_table_window(self):
        table_window = Toplevel(self.root)
        table_window.title("Создать таблицы")

        Label(table_window, text="Добавление таблиц").grid(row=0, column=0, columnspan=3, pady=10)

        tables_frame = Frame(table_window)
        tables_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        def add_field_entry(field_frame):
            row = len(field_frame.grid_slaves()) // 3
            Label(field_frame, text=f"Поле {row + 1}").grid(row=row, column=0, padx=5, pady=5)

            field_name_entry = Entry(field_frame)
            field_name_entry.grid(row=row, column=1, padx=5, pady=5)

            field_type_var = StringVar(value="TEXT")
            field_type_menu = OptionMenu(field_frame, field_type_var, "TEXT", "INTEGER", "REAL", "BLOB")
            field_type_menu.grid(row=row, column=2, padx=5, pady=5)

            return field_name_entry, field_type_var

        def add_table_entry():
            table_frame = Frame(tables_frame, relief="groove", borderwidth=2)
            table_frame.pack(padx=10, pady=10, fill="x", expand=True)

            Label(table_frame, text="Название таблицы:").grid(row=0, column=0, padx=5, pady=5)
            table_name_entry = Entry(table_frame)
            table_name_entry.grid(row=0, column=1, padx=5, pady=5)

            Label(table_frame, text="Поля:").grid(row=1, column=0, columnspan=2, pady=5)

            fields_frame = Frame(table_frame)
            fields_frame.grid(row=2, column=0, columnspan=2)

            add_field_entry(fields_frame)

            Button(table_frame, text="Добавить поле", command=lambda: add_field_entry(fields_frame)).grid(row=3, column=0, columnspan=2, pady=5)

            return table_name_entry, fields_frame

        def create_tables():
            sql_statements = ""
            for table_frame in tables_frame.pack_slaves():
                table_name = table_frame.grid_slaves(row=0, column=1)[0].get().strip()
                fields_frame = table_frame.grid_slaves(row=2, column=0)[0]

                fields = []
                for row in range(len(fields_frame.grid_slaves()) // 3):
                    field_name = fields_frame.grid_slaves(row=row, column=1)[0].get().strip()
                    field_type = fields_frame.grid_slaves(row=row, column=2)[0].cget("text")
                    if field_name:
                        fields.append(f"{field_name} {field_type}")

                if table_name and fields:
                    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(fields)});"
                    sql_statements += query + "\n"
                    self.dbms.execute_query(query)

            sql_file_path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL Files", "*.sql")])
            if sql_file_path:
                self.dbms.save_sql(sql_statements, sql_file_path)

            messagebox.showinfo("Успех", "Все таблицы успешно созданы.")
            table_window.destroy()

        Button(table_window, text="Добавить таблицу", command=add_table_entry).grid(row=2, column=0, padx=5, pady=5)
        Button(table_window, text="Создать таблицы", command=create_tables).grid(row=2, column=1, padx=5, pady=5)
        add_table_entry()

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Все файлы", "*.*"), ("CSV", "*.csv"), ("Excel", "*.xls;*.xlsx"), ("Текстовые файлы", "*.txt")])
        if file_path:
            try:
                data = self.dbms.import_data(file_path)
                # Импортируем все найденные таблицы
                for table_name in data.keys():
                    data[table_name].to_sql(table_name, self.dbms.connection, if_exists='replace', index=False)
                messagebox.showinfo("Успех", f"Данные из файла '{file_path}' импортированы во все таблицы.")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def export_data(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("CSV", "*.csv"), ("Excel", "*.xls;*.xlsx"), ("Текстовые файлы", "*.txt")])
        if file_path:
            try:
                # Экспортируем все таблицы
                for table_name in self.dbms.get_table_structure().keys():
                    query = f"SELECT * FROM {table_name}"
                    data = pd.read_sql_query(query, self.dbms.connection)
                    self.dbms.export_data(data, file_path)
                messagebox.showinfo("Успех", f"Данные из всех таблиц сохранены в файл '{file_path}'.")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def visualize_structure(self):
        """Отображает структуру всех таблиц в базе данных."""
        try:
            table_info = self.dbms.get_table_structure()
            structure_window = Toplevel(self.root)
            structure_window.title("Структура таблиц")

            for idx, (table_name, columns) in enumerate(table_info.items()):
                Label(structure_window, text=f"Таблица: {table_name}").grid(row=idx * 6, column=0, pady=10)
                for i, column in enumerate(columns):
                    Label(structure_window, text=f"Поле {i+1}: {column[1]} ({column[2]})").grid(row=idx * 6 + i + 1, column=0)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    root = Tk()
    gui = GUI(root)
    root.mainloop()
