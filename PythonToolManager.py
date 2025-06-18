import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Menu
import subprocess
import sys
import os
import threading
import ctypes
from ttkthemes import ThemedTk

# --- Konfiguration & Sprachpakete ---

POPULAR_MODULES = sorted([
    'requests', 'numpy', 'pandas', 'matplotlib', 'scipy', 'seaborn', 
    'beautifulsoup4', 'lxml', 'Pillow', 'pygame', 'flask', 'django', 
    'fastapi', 'pyqt6', 'kivy', 'opencv-python', 'tensorflow', 'torch',
    'scikit-learn', 'pyinstaller', 'wxpython', 'pytest', 'poetry'
])

LANGUAGES = {
    "en": {
        "title": "Python Tool Manager",
        "tab_modules": "Module Management",
        "tab_tools": "System Tools",
        "menu_file": "File",
        "menu_language": "Language",
        "menu_quit": "Quit",
        "menu_help": "Help",
        "menu_about": "About",
        
        "label_select_python": "Select Python Version:",
        "label_search_modules": "Search Popular Modules:",
        "label_module_name": "Module Name:",
        "label_output": "Output Log:",

        "btn_install": "Install",
        "btn_uninstall": "Uninstall",
        "btn_update": "Update",
        "btn_list_installed": "List Installed",
        "btn_open_shell": "Open Python Shell",
        "btn_open_admin_ps": "Open Admin PowerShell",
        "btn_clear_log": "Clear Log",

        "tooltip_module_entry": "Enter module name here or select from list",
        "tooltip_python_select": "The selected Python will be used for all pip commands",

        "msg_no_module_title": "Input Missing",
        "msg_no_module_text": "Please enter a module name.",
        "msg_no_python_found_title": "No Python Found",
        "msg_no_python_found_text": "Could not find any Python installations via 'py.exe'.\nPlease ensure the Python Launcher is installed and in your PATH.",
        "msg_about_title": "About Python Tool Manager",
        "msg_about_text": "A user-friendly GUI for managing Python modules and versions on Windows.\nCreated to simplify the Python experience."
    },
    "de": {
        "title": "Python Tool Manager",
        "tab_modules": "Modul-Verwaltung",
        "tab_tools": "System-Werkzeuge",
        "menu_file": "Datei",
        "menu_language": "Sprache",
        "menu_quit": "Beenden",
        "menu_help": "Hilfe",
        "menu_about": "Über",

        "label_select_python": "Python-Version auswählen:",
        "label_search_modules": "Populäre Module suchen:",
        "label_module_name": "Modulname:",
        "label_output": "Ausgabe-Log:",

        "btn_install": "Installieren",
        "btn_uninstall": "Deinstallieren",
        "btn_update": "Aktualisieren",
        "btn_list_installed": "Installierte auflisten",
        "btn_open_shell": "Python-Shell öffnen",
        "btn_open_admin_ps": "Admin-PowerShell öffnen",
        "btn_clear_log": "Log leeren",

        "tooltip_module_entry": "Modulnamen hier eingeben oder aus der Liste wählen",
        "tooltip_python_select": "Das ausgewählte Python wird für alle pip-Befehle verwendet",

        "msg_no_module_title": "Eingabe fehlt",
        "msg_no_module_text": "Bitte geben Sie einen Modulnamen ein.",
        "msg_no_python_found_title": "Kein Python gefunden",
        "msg_no_python_found_text": "Es konnten keine Python-Installationen mittels 'py.exe' gefunden werden.\nBitte stellen Sie sicher, dass der Python Launcher installiert und im PATH ist.",
        "msg_about_title": "Über den Python Tool Manager",
        "msg_about_text": "Eine benutzerfreundliche GUI zur Verwaltung von Python-Modulen und -Versionen unter Windows.\nErstellt, um die Arbeit mit Python zu vereinfachen."
    }
}

class ToolTip:
    def __init__(self, widget, text_key):
        self.widget = widget
        self.text_key = text_key
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        # The app instance is stored in the root window
        app = self.widget.winfo_toplevel().app_instance
        text = app.texts.get(self.text_key, "Tooltip not found")
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=text, background="#ffffe0", relief='solid', borderwidth=1, wraplength=200)
        label.pack(ipadx=1)

    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class PythonToolManager:
    def __init__(self, root):
        self.root = root
        self.root.app_instance = self # Make app instance accessible
        self.python_installations = {}
        self.active_python_executable = sys.executable
        self.current_lang = "de" # Default language
        self.texts = LANGUAGES[self.current_lang]

        self.setup_ui()
        self.find_python_installations()
        self.update_ui_texts()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Tab 1: Module Management ---
        self.module_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.module_tab, text=self.texts["tab_modules"])
        
        # --- Tab 2: System Tools ---
        self.tools_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tools_tab, text=self.texts["tab_tools"])

        self.create_menu()
        self.create_module_widgets(self.module_tab)
        self.create_tools_widgets(self.tools_tab)

    def create_menu(self):
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.lang_menu = Menu(self.file_menu, tearoff=0)
        self.lang_menu.add_command(label="Deutsch", command=lambda: self.switch_language("de"))
        self.lang_menu.add_command(label="English", command=lambda: self.switch_language("en"))
        self.file_menu.add_cascade(label=self.texts["menu_language"], menu=self.lang_menu)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=self.texts["menu_quit"], command=self.root.quit)
        self.menu_bar.add_cascade(label=self.texts["menu_file"], menu=self.file_menu)

        # Help Menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label=self.texts["menu_about"], command=self.show_about)
        self.menu_bar.add_cascade(label=self.texts["menu_help"], menu=self.help_menu)

    def create_module_widgets(self, parent):
        # Left side for lists
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right side for controls and output
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # --- Left Frame Content ---
        self.search_label = ttk.Label(left_frame, text=self.texts["label_search_modules"])
        self.search_label.pack(anchor="w")
        
        self.search_entry = ttk.Entry(left_frame)
        self.search_entry.pack(fill=tk.X, pady=(2, 5))
        self.search_entry.bind("<KeyRelease>", self.filter_module_list)

        self.module_listbox = tk.Listbox(left_frame, exportselection=False, height=15)
        self.module_listbox.pack(expand=True, fill=tk.BOTH)
        self.module_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)
        
        for module in POPULAR_MODULES:
            self.module_listbox.insert(tk.END, module)

        # --- Right Frame Content ---
        controls_frame = ttk.Frame(right_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        self.module_name_label = ttk.Label(controls_frame, text=self.texts["label_module_name"])
        self.module_name_label.grid(row=0, column=0, sticky="w", padx=(0, 5))

        self.module_entry = ttk.Entry(controls_frame, width=40)
        self.module_entry.grid(row=1, column=0, sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1)
        ToolTip(self.module_entry, "tooltip_module_entry")

        btn_frame = ttk.Frame(controls_frame)
        btn_frame.grid(row=1, column=1, sticky="e", padx=(10, 0))
        
        self.install_button = ttk.Button(btn_frame, text=self.texts["btn_install"], command=self.install_module)
        self.install_button.pack(side=tk.LEFT)
        self.uninstall_button = ttk.Button(btn_frame, text=self.texts["btn_uninstall"], command=self.uninstall_module)
        self.uninstall_button.pack(side=tk.LEFT, padx=5)
        self.update_button = ttk.Button(btn_frame, text=self.texts["btn_update"], command=self.update_module)
        self.update_button.pack(side=tk.LEFT)

        self.output_label = ttk.Label(right_frame, text=self.texts["label_output"])
        self.output_label.pack(anchor="w", pady=(10, 2))
        
        self.output_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state=tk.DISABLED, height=15)
        self.output_text.pack(expand=True, fill=tk.BOTH)

        bottom_btn_frame = ttk.Frame(right_frame)
        bottom_btn_frame.pack(fill=tk.X, pady=(5,0))
        self.list_button = ttk.Button(bottom_btn_frame, text=self.texts["btn_list_installed"], command=self.list_modules)
        self.list_button.pack(side=tk.LEFT)
        self.clear_log_button = ttk.Button(bottom_btn_frame, text=self.texts["btn_clear_log"], command=self.clear_log)
        self.clear_log_button.pack(side=tk.RIGHT)

    def create_tools_widgets(self, parent):
        tools_container = ttk.LabelFrame(parent, text=self.texts["label_select_python"], padding=10)
        tools_container.pack(fill=tk.X, pady=10)
        
        self.python_select_combo = ttk.Combobox(tools_container, state="readonly", width=80)
        self.python_select_combo.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,10))
        self.python_select_combo.bind("<<ComboboxSelected>>", self.on_python_select)
        ToolTip(self.python_select_combo, "tooltip_python_select")

        self.open_shell_button = ttk.Button(tools_container, text=self.texts["btn_open_shell"], command=self.open_python_shell)
        self.open_shell_button.pack(side=tk.LEFT)
        
        admin_container = ttk.LabelFrame(parent, text="Admin Actions", padding=10)
        admin_container.pack(fill=tk.X, pady=10)
        
        self.open_admin_ps_button = ttk.Button(admin_container, text=self.texts["btn_open_admin_ps"], command=self.open_admin_powershell)
        self.open_admin_ps_button.pack(anchor="w")

    # --- Backend & Logic ---

    def find_python_installations(self):
        self.log_output("Searching for Python installations...\n")
        try:
            # 'py -0p' is the most reliable way to find installed pythons on Windows
            result = subprocess.run(['py', '-0p'], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            lines = result.stdout.strip().split('\n')
            
            installations = {}
            for line in lines:
                if '-V:' in line:
                    parts = line.strip().split()
                    version = parts[0]
                    path = parts[-1]
                    # Create a more descriptive label
                    arch = " (64-bit)" if "amd64" in path.lower() else " (32-bit)"
                    label = f"Python {version.replace('-64', '').replace('-32', '')}{arch}  -  {path}"
                    installations[label] = path
            
            self.python_installations = installations
            
            if not self.python_installations:
                raise FileNotFoundError("No installations found in 'py -0p' output.")
            
            self.python_select_combo['values'] = list(self.python_installations.keys())
            self.python_select_combo.set(list(self.python_installations.keys())[0]) # Select first one
            self.on_python_select() # Set initial active python
            self.log_output(f"Found {len(self.python_installations)} Python installation(s).\n")

        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            self.log_output(f"Error finding Python: {e}\n")
            messagebox.showerror(self.texts["msg_no_python_found_title"], self.texts["msg_no_python_found_text"])
            self.python_select_combo['values'] = [self.texts["msg_no_python_found_text"]]
            self.python_select_combo.set(self.texts["msg_no_python_found_text"])
            self.python_select_combo.config(state=tk.DISABLED)

    def on_python_select(self, event=None):
        selected_label = self.python_select_combo.get()
        self.active_python_executable = self.python_installations.get(selected_label, sys.executable)
        self.log_output(f"Active Python set to: {self.active_python_executable}\n")

    def run_pip_command(self, command):
        if not self.active_python_executable:
            messagebox.showerror("Error", "No active Python executable selected.")
            return
            
        self.set_ui_state(tk.DISABLED)
        self.log_output(f"\n--- Running: pip {' '.join(command)} ---\n")
        
        full_command = [self.active_python_executable, "-m", "pip"] + command
        
        thread = threading.Thread(target=self._execute_command, args=(full_command,))
        thread.start()

    def _execute_command(self, command, on_finish=None):
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
            
            for line in iter(process.stdout.readline, ''):
                self.log_output(line)
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.log_output("\n--- ERROR ---\n")
                self.log_output(stderr)
            else:
                self.log_output("\n--- Command finished successfully ---\n")
            
            if on_finish:
                self.root.after(0, on_finish)
                
        except Exception as e:
            self.log_output(f"\n--- CRITICAL ERROR ---\n{e}\n")
        finally:
            self.root.after(100, lambda: self.set_ui_state(tk.NORMAL))

    def log_output(self, message):
        def append():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, message)
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        self.root.after(0, append)
    
    def clear_log(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.config(state=tk.DISABLED)

    def set_ui_state(self, state):
        for widget in [self.install_button, self.uninstall_button, self.update_button, self.list_button, self.module_entry, self.python_select_combo]:
            widget.config(state=state)

    def install_module(self):
        module_name = self.module_entry.get().strip()
        if not module_name:
            messagebox.showwarning(self.texts["msg_no_module_title"], self.texts["msg_no_module_text"])
            return
        self.run_pip_command(["install", module_name])

    def uninstall_module(self):
        module_name = self.module_entry.get().strip()
        if not module_name:
            messagebox.showwarning(self.texts["msg_no_module_title"], self.texts["msg_no_module_text"])
            return
        self.run_pip_command(["uninstall", "-y", module_name])

    def update_module(self):
        module_name = self.module_entry.get().strip()
        if not module_name:
            messagebox.showwarning(self.texts["msg_no_module_title"], self.texts["msg_no_module_text"])
            return
        self.run_pip_command(["install", "--upgrade", module_name])

    def list_modules(self):
        self.run_pip_command(["list"])

    def open_python_shell(self):
        self.log_output(f"Opening shell for {self.active_python_executable}...\n")
        subprocess.Popen(['start', 'cmd', '/k', self.active_python_executable], shell=True)

    def open_admin_powershell(self):
        if not ctypes.windll.shell32.IsUserAnAdmin():
             self.log_output("Admin rights needed. Requesting elevation...\n")
             ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
             self.root.quit()
        else:
            self.log_output("Opening PowerShell as Administrator...\n")
            subprocess.Popen(['powershell', '-Command', 'Start-Process PowerShell -Verb RunAs'], creationflags=subprocess.CREATE_NO_WINDOW)

    def filter_module_list(self, event=None):
        search_term = self.search_entry.get().lower()
        self.module_listbox.delete(0, tk.END)
        for module in POPULAR_MODULES:
            if search_term in module.lower():
                self.module_listbox.insert(tk.END, module)

    def on_listbox_select(self, event=None):
        selections = self.module_listbox.curselection()
        if selections:
            selected_module = self.module_listbox.get(selections[0])
            self.module_entry.delete(0, tk.END)
            self.module_entry.insert(0, selected_module)

    def switch_language(self, lang_code):
        self.current_lang = lang_code
        self.texts = LANGUAGES[lang_code]
        self.update_ui_texts()
        
    def update_ui_texts(self):
        self.root.title(self.texts["title"])
        self.notebook.tab(self.module_tab, text=self.texts["tab_modules"])
        self.notebook.tab(self.tools_tab, text=self.texts["tab_tools"])
        
        # Menu
        self.file_menu.entryconfig(0, label=self.texts["menu_language"])
        self.file_menu.entryconfig(2, label=self.texts["menu_quit"])
        self.menu_bar.entryconfig(self.texts["menu_file"], label=self.texts["menu_file"])
        self.help_menu.entryconfig(0, label=self.texts["menu_about"])
        self.menu_bar.entryconfig(self.texts["menu_help"], label=self.texts["menu_help"])
        
        # Module Tab
        self.search_label.config(text=self.texts["label_search_modules"])
        self.module_name_label.config(text=self.texts["label_module_name"])
        self.install_button.config(text=self.texts["btn_install"])
        self.uninstall_button.config(text=self.texts["btn_uninstall"])
        self.update_button.config(text=self.texts["btn_update"])
        self.output_label.config(text=self.texts["label_output"])
        self.list_button.config(text=self.texts["btn_list_installed"])
        self.clear_log_button.config(text=self.texts["btn_clear_log"])
        
        # Tools Tab
        self.tools_tab.winfo_children()[0].config(text=self.texts["label_select_python"])
        self.open_shell_button.config(text=self.texts["btn_open_shell"])
        self.open_admin_ps_button.config(text=self.texts["btn_open_admin_ps"])

    def show_about(self):
        messagebox.showinfo(self.texts["msg_about_title"], self.texts["msg_about_text"])

if __name__ == "__main__":
    # ThemedTk anstelle von tk.Tk() für das moderne Design
    root = ThemedTk(theme="arc") # Andere Themes: "plastik", "clearlooks", "radiance"
    root.title("Python Tool Manager")
    root.geometry("850x600")
    app = PythonToolManager(root)
    root.mainloop()