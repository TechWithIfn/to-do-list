import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

class AdvancedToDoList:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced To-Do List")
        self.master.geometry("800x600")

        self.conn = sqlite3.connect("todo_list.db")
        self.create_table()

        self.create_widgets()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks
        (id INTEGER PRIMARY KEY,
         task TEXT,
         priority TEXT,
         category TEXT,
         due_date TEXT,
         completed INTEGER)
        ''')
        self.conn.commit()

    def create_widgets(self):
        # Task input
        input_frame = ttk.Frame(self.master, padding="10")
        input_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(input_frame, text="Task:").grid(row=0, column=0, sticky="w")
        self.task_entry = ttk.Entry(input_frame, width=40)
        self.task_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Priority:").grid(row=0, column=2, sticky="w")
        self.priority_combobox = ttk.Combobox(input_frame, values=["Low", "Medium", "High"], width=10)
        self.priority_combobox.grid(row=0, column=3, padx=5)
        self.priority_combobox.set("Medium")

        ttk.Label(input_frame, text="Category:").grid(row=1, column=0, sticky="w")
        self.category_entry = ttk.Entry(input_frame, width=20)
        self.category_entry.grid(row=1, column=1, padx=5)

        ttk.Label(input_frame, text="Due Date:").grid(row=1, column=2, sticky="w")
        self.due_date_entry = ttk.Entry(input_frame, width=12)
        self.due_date_entry.grid(row=1, column=3, padx=5)
        self.due_date_entry.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))

        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(row=1, column=4, padx=5)

        # Task list
        list_frame = ttk.Frame(self.master, padding="10")
        list_frame.grid(row=1, column=0, sticky="nsew")

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Task", "Priority", "Category", "Due Date", "Completed"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Completed", text="Completed")
        self.tree.column("ID", width=50)
        self.tree.column("Task", width=200)
        self.tree.column("Priority", width=100)
        self.tree.column("Category", width=100)
        self.tree.column("Due Date", width=100)
        self.tree.column("Completed", width=100)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Buttons
        button_frame = ttk.Frame(self.master, padding="10")
        button_frame.grid(row=2, column=0, sticky="ew")

        ttk.Button(button_frame, text="Mark Completed", command=self.mark_completed).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Edit Task", command=self.edit_task).grid(row=0, column=2, padx=5)

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)

        self.load_tasks()

    def add_task(self):
        task = self.task_entry.get()
        priority = self.priority_combobox.get()
        category = self.category_entry.get()
        due_date = self.due_date_entry.get()

        if task and priority and category and due_date:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO tasks (task, priority, category, due_date, completed) VALUES (?, ?, ?, ?, ?)",
                           (task, priority, category, due_date, 0))
            self.conn.commit()
            self.load_tasks()
            self.clear_inputs()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    def load_tasks(self):
        self.tree.delete(*self.tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY due_date")
        for row in cursor.fetchall():
            completed = "Yes" if row[5] else "No"
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], completed))

    def clear_inputs(self):
        self.task_entry.delete(0, tk.END)
        self.priority_combobox.set("Medium")
        self.category_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))

    def mark_completed(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            task_id = item['values'][0]
            current_status = item['values'][5]
            
            new_status = 0 if current_status == "Yes" else 1
            status_text = "Yes" if new_status == 1 else "No"
            
            cursor = self.conn.cursor()
            cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
            self.conn.commit()
            
            self.tree.item(selected_item, values=(item['values'][0], item['values'][1], item['values'][2], 
                                                  item['values'][3], item['values'][4], status_text))
        else:
            messagebox.showwarning("Selection Error", "Please select a task to mark as completed.")

    def delete_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_id = self.tree.item(selected_item)['values'][0]
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            self.tree.delete(selected_item)
        else:
            messagebox.showwarning("Selection Error", "Please select a task to delete.")

    def edit_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_id = self.tree.item(selected_item)['values'][0]
            task = self.tree.item(selected_item)['values'][1]
            priority = self.tree.item(selected_item)['values'][2]
            category = self.tree.item(selected_item)['values'][3]
            due_date = self.tree.item(selected_item)['values'][4]

            edit_window = tk.Toplevel(self.master)
            edit_window.title("Edit Task")

            ttk.Label(edit_window, text="Task:").grid(row=0, column=0, sticky="w")
            task_entry = ttk.Entry(edit_window, width=40)
            task_entry.grid(row=0, column=1, padx=5)
            task_entry.insert(0, task)

            ttk.Label(edit_window, text="Priority:").grid(row=1, column=0, sticky="w")
            priority_combobox = ttk.Combobox(edit_window, values=["Low", "Medium", "High"], width=10)
            priority_combobox.grid(row=1, column=1, padx=5)
            priority_combobox.set(priority)

            ttk.Label(edit_window, text="Category:").grid(row=2, column=0, sticky="w")
            category_entry = ttk.Entry(edit_window, width=20)
            category_entry.grid(row=2, column=1, padx=5)
            category_entry.insert(0, category)

            ttk.Label(edit_window, text="Due Date:").grid(row=3, column=0, sticky="w")
            due_date_entry = ttk.Entry(edit_window, width=12)
            due_date_entry.grid(row=3, column=1, padx=5)
            due_date_entry.insert(0, due_date)

            def save_changes():
                new_task = task_entry.get()
                new_priority = priority_combobox.get()
                new_category = category_entry.get()
                new_due_date = due_date_entry.get()

                cursor = self.conn.cursor()
                cursor.execute("UPDATE tasks SET task = ?, priority = ?, category = ?, due_date = ? WHERE id = ?",
                               (new_task, new_priority, new_category, new_due_date, task_id))
                self.conn.commit()
                self.load_tasks()
                edit_window.destroy()

            ttk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=4, column=0, columnspan=2, pady=10)
        else:
            messagebox.showwarning("Selection Error", "Please select a task to edit.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedToDoList(root)
    root.mainloop()