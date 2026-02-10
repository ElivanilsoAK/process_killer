import customtkinter as ctk
import threading
import unicodedata
from tkinter import messagebox
import os

from src.core.engine import ProcessEngine
from src.gui.widgets import ProcessRow

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def normalize_text(text):
    """Removes accents and converts to lowercase for fuzzy matching."""
    if not text: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(text))
                   if unicodedata.category(c) != 'Mn').lower()

class GUIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Process Manager Elite")
        self.geometry("1000x700")
        
        self.engine = ProcessEngine()
        
        # Grid Layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Data
        self.all_processes = []
        self.active_category = "All" # All, Apps, Services
        self.is_scanning = False

        # Icon
        icon_path = os.path.join("assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except:
                pass
        elif os.path.exists("icon.ico"): # Fallback for dev root
             try:
                 self.iconbitmap("icon.ico")
             except:
                 pass

        self.create_sidebar()
        self.create_main_area()
        
        # Initial Load - Start Thread
        self.after(500, self.start_scan_thread)

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1) # maximize spacer

        self.logo_lbl = ctk.CTkLabel(self.sidebar, text="Process\nManager", font=("Roboto", 24, "bold"))
        self.logo_lbl.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_all = ctk.CTkButton(self.sidebar, text="ALL PROCESSES", height=40, corner_radius=6,
                                     command=lambda: self.change_category("All"))
        self.btn_all.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_apps = ctk.CTkButton(self.sidebar, text="USER APPS", height=40, corner_radius=6, 
                                      fg_color="transparent", border_width=2, text_color=("gray10", "gray90"),
                                      command=lambda: self.change_category("Apps"))
        self.btn_apps.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_services = ctk.CTkButton(self.sidebar, text="SERVICES", height=40, corner_radius=6, 
                                          fg_color="transparent", border_width=2, text_color=("gray10", "gray90"),
                                          command=lambda: self.change_category("Services"))
        self.btn_services.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Spacer
        self.spacer = ctk.CTkLabel(self.sidebar, text="", height=50)
        self.spacer.grid(row=4, column=0)

        self.btn_refresh = ctk.CTkButton(self.sidebar, text="REFRESH", height=40, fg_color="#27ae60", hover_color="#2ecc71",
                                         command=self.start_scan_thread)
        self.btn_refresh.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Search Bar
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.search_frame.pack(fill="x", pady=(0, 10))
        
        self.lbl_header = ctk.CTkLabel(self.search_frame, text="All Processes", font=("Roboto", 20, "bold"))
        self.lbl_header.pack(side="left")

        self.entry_search = ctk.CTkEntry(self.search_frame, placeholder_text="Search Process Name or PID...", width=300)
        self.entry_search.pack(side="right")
        self.entry_search.bind("<KeyRelease>", self.filter_list)

        # Header Row
        self.header_row = ctk.CTkFrame(self.main_frame, height=35, fg_color="gray30")
        self.header_row.pack(fill="x")
        self.header_row.grid_columnconfigure(1, weight=1)

        labels = [("PID", 55), ("NAME", 0), ("TYPE", 80), ("USER", 110), ("MEMORY", 90), ("ACTION", 100)]
        for i, (txt, w) in enumerate(labels):
            lbl = ctk.CTkLabel(self.header_row, text=txt, font=("Roboto", 11, "bold"), text_color="gray90")
            if w > 0: lbl.configure(width=w)
            lbl.grid(row=0, column=i, padx=10, pady=5, sticky="ew" if i==1 else "")

        # List Area
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scroll_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Status Bar
        self.statusbar = ctk.CTkLabel(self.main_frame, text="Ready", anchor="e", text_color="gray50")
        self.statusbar.pack(fill="x", pady=(5,0))

    def change_category(self, category):
        self.active_category = category
        self.lbl_header.configure(text=f"{category} Processes")
        
        # Update sidebar button styles
        bg_active = ["#1f6aa5", "#1f6aa5"] # default ctk color
        bg_inactive = "transparent"
        
        self.btn_all.configure(fg_color=bg_active if category=="All" else bg_inactive)
        self.btn_apps.configure(fg_color=bg_active if category=="Apps" else bg_inactive)
        self.btn_services.configure(fg_color=bg_active if category=="Services" else bg_inactive)

        self.filter_list()

    def start_scan_thread(self):
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.statusbar.configure(text="Scanning in background...")
        self.btn_refresh.configure(state="disabled")
        
        thread = threading.Thread(target=self.scan_processes_logic, daemon=True)
        thread.start()

    def scan_processes_logic(self):
        results = self.engine.scan_processes()
        
        # Pass data back to UI thread
        self.after(0, lambda: self.finish_scan(results))

    def finish_scan(self, results):
        self.all_processes = results
        self.is_scanning = False
        self.btn_refresh.configure(state="normal")
        self.statusbar.configure(text=f"Total: {len(results)}")
        self.filter_list()

    def filter_list(self, event=None):
        query = normalize_text(self.entry_search.get())
        
        matching = []
        for p in self.all_processes:
            # Category Filter
            current_type = p.get('custom_type', 'App')
            if self.active_category == "Apps" and current_type != "App": continue
            if self.active_category == "Services" and current_type != "Service": continue
            
            # Search Filter (Deep: Name OR Cmdline OR PID)
            if query:
                p_name_norm = normalize_text(p['name'])
                p_cmd_norm = normalize_text(p.get('cmdline_str',''))
                p_pid_str = str(p['pid'])
                
                # Check ALL fields
                if (query not in p_name_norm and 
                    query not in p_cmd_norm and 
                    not p_pid_str.startswith(query)):
                    continue
            
            matching.append(p)

        self.update_ui_list(matching)

    def update_ui_list(self, processes):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Limit to 60 for performance
        display = processes[:60]
        
        for i, p in enumerate(display):
            row = ProcessRow(self.scroll_frame, p, self.confirm_kill, is_alternate=(i%2==0))
            row.pack(fill="x", pady=1, padx=2)
            
        if len(processes) > 60:
            self.statusbar.configure(text=f"Showing top 60 of {len(processes)} results...")

    def confirm_kill(self, proc_data):
        name = proc_data['name']
        pid = proc_data['pid']
        ptype = proc_data.get('custom_type')
        
        msg = f"Are you sure you want to terminate:\n{name} (PID: {pid})?"
        icon = "warning"
        if ptype == "Service":
            msg += "\n\n⚠️ CRITICAL WARNING: This is a System Service.\nTerminating it may crash Windows!"
            icon = "error"
            
        if messagebox.askyesno("Confirm Action", msg, icon=icon):
            try:
                # Use engine to kill
                result = self.engine.kill_process(pid)
                if result['success']:
                     self.after(500, self.start_scan_thread)
                else:
                     messagebox.showwarning("Error", result['message'])
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = GUIApp()
    app.mainloop()
