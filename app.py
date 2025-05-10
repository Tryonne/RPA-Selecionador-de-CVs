import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from cv_organizer import CVOrganizer
import json
import os
import shutil
from job_scraper import JobScraper
import webbrowser
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class CVManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de CVs")
        self.root.geometry("1500x600")

        # Initialize CV Organizer and job scraper
        self.input_dir = "bau_dos_cvs"
        self.output_dir = "cvs_organizados"
        self.cv_organizer = CVOrganizer(self.input_dir, self.output_dir)
        self.job_scraper = JobScraper()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create CV Manager tab
        self.cv_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cv_frame, text="CV Manager")

        # Create Job Search tab
        self.job_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.job_frame, text="Job Search")

        # Initialize both tabs
        self.create_cv_manager_tab()
        self.create_job_search_tab()

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def create_cv_manager_tab(self):
        # Department frame
        dept_frame = ttk.LabelFrame(self.cv_frame, text="Departamentos", padding="5")
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

        # Unorganized CVs frame
        unorg_frame = ttk.LabelFrame(self.cv_frame, text="CVs não organizados", padding="5")
        unorg_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.unorg_listbox = tk.Listbox(unorg_frame)
        self.unorg_listbox.pack(fill=tk.BOTH, expand=True)

        # Organized CVs frame
        cv_frame = ttk.LabelFrame(self.cv_frame, text="CVs organizados", padding="5")
        cv_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.cv_listbox = tk.Listbox(cv_frame)
        self.cv_listbox.pack(fill=tk.BOTH, expand=True)

        # Button frame
        btn_frame = ttk.Frame(self.cv_frame, padding="5")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Buttons
        organize_btn = ttk.Button(btn_frame, text="Organizar CVs", command=self.organize_cvs)
        organize_btn.pack(side=tk.LEFT, padx=5)

        refresh_btn = ttk.Button(btn_frame, text="Atualizar", command=self.refresh_lists)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        import_btn = ttk.Button(btn_frame, text="Importar CVs", command=self.import_cvs)
        import_btn.pack(side=tk.LEFT, padx=5)

        # Configure grid weights for cv_frame
        self.cv_frame.columnconfigure(1, weight=1)
        self.cv_frame.rowconfigure(1, weight=1)

    def create_job_search_tab(self):
        # Search frame
        search_frame = ttk.Frame(self.job_frame, padding="5")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left frame for TreeView
        left_frame = ttk.Frame(self.job_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right frame for charts
        right_frame = ttk.Frame(self.job_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        # Charts frame
        charts_frame = ttk.LabelFrame(right_frame, text="Gráficos", padding="5")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create figures for charts
        self.fig_location = Figure(figsize=(4, 3))
        self.fig_company = Figure(figsize=(4, 3))
        
        # Create canvas for charts
        self.canvas_location = FigureCanvasTkAgg(self.fig_location, master=charts_frame)
        self.canvas_company = FigureCanvasTkAgg(self.fig_company, master=charts_frame)
        
        # Pack canvas
        self.canvas_location.get_tk_widget().pack(pady=5)
        self.canvas_company.get_tk_widget().pack(pady=5)
        
        # Department selection
        ttk.Label(search_frame, text="Department:").pack(side=tk.LEFT)
        self.dept_var = tk.StringVar()
        dept_combo = ttk.Combobox(search_frame, textvariable=self.dept_var)
        dept_combo['values'] = list(self.cv_organizer.departments.keys())
        dept_combo.pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn = ttk.Button(search_frame, text="Search Jobs", 
                              command=lambda: self.search_jobs(self.dept_var.get()))
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.Frame(left_frame, padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview
        self.jobs_tree = ttk.Treeview(results_frame, columns=('title', 'company', 'location', 'description'), show='headings')
        
        # Define column headings
        self.jobs_tree.heading('title', text='Título')
        self.jobs_tree.heading('company', text='Empresa')
        self.jobs_tree.heading('location', text='Localização')
        self.jobs_tree.heading('description', text='Breve Descrição')
        
        # Configure column widths
        self.jobs_tree.column('title', width=200)
        self.jobs_tree.column('company', width=150)
        self.jobs_tree.column('location', width=150)
        self.jobs_tree.column('description', width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.jobs_tree.yview)
        self.jobs_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.jobs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind single-click event instead of double-click
        self.jobs_tree.bind('<ButtonRelease-1>', self.open_job_link)
        
        # Store jobs data
        self.jobs_data = []

    def update_charts(self, jobs):
        # Clear previous charts
        self.fig_location.clear()
        self.fig_company.clear()
        
        # Count locations
        locations = {}
        for job in jobs:
            loc = job['location']
            locations[loc] = locations.get(loc, 0) + 1
        
        # Count companies
        companies = {}
        for job in jobs:
            company = job['company']
            companies[company] = companies.get(company, 0) + 1
        
        # Create location pie chart
        ax1 = self.fig_location.add_subplot(111)
        ax1.pie(locations.values(), labels=locations.keys(), autopct='%1.1f%%')
        ax1.set_title('Localizações')
        
        # Create company pie chart
        ax2 = self.fig_company.add_subplot(111)
        ax2.pie(companies.values(), labels=companies.keys(), autopct='%1.1f%%')
        ax2.set_title('Empresas')
        
        # Update canvas
        self.canvas_location.draw()
        self.canvas_company.draw()

    def search_jobs(self, department):
        # Clear previous results
        for item in self.jobs_tree.get_children():
            self.jobs_tree.delete(item)
        
        # Search for jobs
        jobs, count = self.job_scraper.search_jobs(department)
        
        # Clear previous jobs data
        self.jobs_data = []
        
        # Update treeview with new results
        for job in jobs:
            self.jobs_tree.insert('', tk.END, values=(
                job['title'],
                job['company'],
                job['location'],
                job['description'][:100] + '...' if len(job['description']) > 100 else job['description']
            ))
            self.jobs_data.append(job)
        
        # Update charts
        self.update_charts(jobs)
    
    def import_cvs(self):
        file_paths = filedialog.askopenfilenames(
            title="Selecionar CV(s)",
            filetypes=(("PDF files", "*.pdf"), ("Word files", "*.docx;*.doc"))
        )
        for file_path in file_paths:
            try:
                shutil.copy(file_path, self.input_dir)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar o CV: {str(e)}")
        if file_paths:
            messagebox.showinfo("Sucesso", "CV(s) importados com sucesso!")
            self.refresh_lists()

    def open_job_link(self, event):
        selection = self.jobs_tree.selection()
        if selection:
            item = selection[0]
            idx = self.jobs_tree.index(item)
            if idx < len(self.jobs_data):
                job = self.jobs_data[idx]
                if 'link' in job:
                    webbrowser.open(f"https://expressoemprego.pt{job['link']}")

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