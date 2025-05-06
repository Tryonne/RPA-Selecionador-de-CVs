import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from cv_organizer import CVOrganizer
import json
import os
import shutil

class CVManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de CVs")
        self.root.geometry("800x600")

        # Initialize CV Organizer
        self.input_dir = "bau_dos_cvs"
        self.output_dir = "cvs_organizados"
        self.cv_organizer = CVOrganizer(self.input_dir, self.output_dir)

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create department list
        self.create_department_list()

        # Create CV list
        self.create_cv_list()

        # Create buttons
        self.create_buttons()

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

    def create_department_list(self):
        # Department frame
        dept_frame = ttk.LabelFrame(self.main_frame, text="Departamentos", padding="5")
        dept_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        # Department listbox
        self.dept_listbox = tk.Listbox(dept_frame, width=30)
        self.dept_listbox.pack(fill=tk.BOTH, expand=True)

        # Load departments
        departments = list(self.cv_organizer.departments.keys())
        departments.append("Não Classificado")
        for dept in sorted(departments):
            self.dept_listbox.insert(tk.END, dept)

        self.dept_listbox.bind('<<ListboxSelect>>', self.on_department_select)

    def create_cv_list(self):
        # Unorganized CVs frame
        unorg_frame = ttk.LabelFrame(self.main_frame, text="CVs não organizados", padding="5")
        unorg_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.unorg_listbox = tk.Listbox(unorg_frame)
        self.unorg_listbox.pack(fill=tk.BOTH, expand=True)

        # Organized CVs frame
        cv_frame = ttk.LabelFrame(self.main_frame, text="CVs organizados", padding="5")
        cv_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.cv_listbox = tk.Listbox(cv_frame)
        self.cv_listbox.pack(fill=tk.BOTH, expand=True)

    def create_buttons(self):
        # Button frame
        btn_frame = ttk.Frame(self.main_frame, padding="5")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Organize button
        organize_btn = ttk.Button(btn_frame, text="Organizar CVs", command=self.organize_cvs)
        organize_btn.pack(side=tk.LEFT, padx=5)

        # Refresh button
        refresh_btn = ttk.Button(btn_frame, text="Atualizar", command=self.refresh_lists)
        refresh_btn.pack(side=tk.LEFT, padx=5)

    def on_department_select(self, event):
        selection = self.dept_listbox.curselection()
        if selection:
            department = self.dept_listbox.get(selection[0])
            self.update_cv_list(department)

    def update_cv_list(self, department):
        self.cv_listbox.delete(0, tk.END)
        department_path = Path(self.output_dir) / department
        if department_path.exists():
            for cv_file in department_path.glob("*.*"):
                self.cv_listbox.insert(tk.END, cv_file.name)

    def organize_cvs(self):
        try:
            self.cv_organizer.organize_cvs()
            messagebox.showinfo("Sucesso", "CVs organizados com sucesso!")
            self.refresh_lists()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao organizar CVs: {str(e)}")

    def refresh_lists(self):
        # Update unorganized CVs list
        self.unorg_listbox.delete(0, tk.END)
        input_path = Path(self.input_dir)
        if input_path.exists():
            for cv_file in input_path.glob("*.*"):
                if cv_file.suffix.lower() in [".pdf", ".docx", ".doc"]:
                    self.unorg_listbox.insert(tk.END, cv_file.name)

        # Update organized CVs list
        selection = self.dept_listbox.curselection()
        if selection:
            department = self.dept_listbox.get(selection[0])
            self.update_cv_list(department)

def main():
    root = tk.Tk()
    app = CVManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()