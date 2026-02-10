import customtkinter as ctk
import psutil
import os
import threading
import time
import unicodedata
from tkinter import messagebox

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def normalize_text(text):
    """Removes accents and converts to lowercase for fuzzy matching."""
    if not text: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(text))
                   if unicodedata.category(c) != 'Mn').lower()

class ProcessRow(ctk.CTkFrame):
    def __init__(self, master, proc, kill_callback, is_alternate=False, **kwargs):
        # Alternating row colors for readability
        fg_color = "gray20" if is_alternate else "transparent"
        super().__init__(master, fg_color=fg_color, corner_radius=6, **kwargs)
        self.proc = proc
        self.kill_callback = kill_callback
        self.grid_columnconfigure(1, weight=1)

        # PID
        self.lbl_pid = ctk.CTkLabel(self, text=str(proc['pid']), width=50, anchor="w", font=("Roboto Medium", 12))
        self.lbl_pid.grid(row=0, column=0, padx=10, pady=8)

        # Name
        self.lbl_name = ctk.CTkLabel(self, text=proc['name'], anchor="w", font=("Roboto Medium", 13))
        self.lbl_name.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        # Type Badge
        is_service = proc['custom_type'] == "Service"
        type_text = "SERVICE" if is_service else "APP"
        type_fg = "#f39c12" if is_service else "#2ecc71"
        
        self.lbl_type = ctk.CTkLabel(self, text=type_text, width=70, text_color=type_fg, font=("Roboto", 11, "bold"))
        self.lbl_type.grid(row=0, column=2, padx=10, pady=8)

        # User
        user = proc['username'] or "-"
        if len(user) > 12: user = user[:10] + "..."
        self.lbl_user = ctk.CTkLabel(self, text=user, width=100, anchor="w", text_color="gray70")
        self.lbl_user.grid(row=0, column=3, padx=10, pady=8)

        # Memory
        mem_mb = proc['memory_mb']
        self.lbl_mem = ctk.CTkLabel(self, text=f"{mem_mb:.1f} MB", width=80, anchor="e", text_color="gray70")
        self.lbl_mem.grid(row=0, column=4, padx=10, pady=8)

        # Kill Button
        self.btn_kill = ctk.CTkButton(self, text="End Task", width=80, height=28, 
                                      fg_color="#c0392b", hover_color="#e74c3c", 
                                      font=("Roboto", 11, "bold"),
                                      command=self.on_kill)
        self.btn_kill.grid(row=0, column=5, padx=10, pady=8)

    def on_kill(self):
        self.kill_callback(self.proc)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Process Manager Elite")
        self.geometry("1000x700")
        
        # Grid Layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Data
        self.all_processes = []
        self.active_category = "All" # All, Apps, Services
        self.is_scanning = False

        # Icon
        try:
            self.iconbitmap("icon.ico")
        except:
            pass # Fallback if icon missing during dev

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

    def get_process_type(self, p):
        # Optimized categorization
        try:
            name = p.name().lower()
            
            # Fast Check: Typical Service Names
            system_procs = ['svchost.exe', 'csrss.exe', 'winlogon.exe', 'services.exe', 'lsass.exe', 'smss.exe', 'system', 'registry']
            if name in system_procs:
                return "Service"

            # Slow Check: Session ID (Only scan if necessary)
            if os.name == 'nt':
                try:
                    # Accessing p.info triggers a call. Using direct methods can be safer or try/except block.
                    # We will use p.as_dict to get all safe info at once in the thread.
                    pass 
                except:
                    pass
            
            return "App" # Default assumption for unknown, filter logic will refine
        except:
            return "Service"

    def start_scan_thread(self):
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.statusbar.configure(text="Scanning in background...")
        self.btn_refresh.configure(state="disabled")
        
        thread = threading.Thread(target=self.scan_processes_logic, daemon=True)
        thread.start()

    def scan_processes_logic(self):
        results = []
        try:
            for p in psutil.process_iter():
                try:
                    # Fetch essentials + cmdline
                    p_info = p.as_dict(attrs=['pid', 'name', 'username', 'memory_info', 'cmdline'])
                    
                    # Store joined cmdline for easier searching
                    cmd_list = p_info.get('cmdline', [])
                    p_info['cmdline_str'] = " ".join(cmd_list) if cmd_list else ""

                    if os.name == 'nt':
                        try:
                            # Direct check for session 0
                            if p.pid == 0 or p.pid == 4: # System Idle & System
                                p_info['custom_type'] = "Service"
                            else:
                                sess_id = getattr(p, 'session_id', None)
                                if sess_id is None:
                                    pass
                        except:
                            pass
                            
                    # Manual Logic for Type
                    user = p_info.get('username', '')
                    if not user: user = ""
                    
                    is_service = False
                    if user.lower() in ['nt authority\\system', 'nt authority\\local service', 'nt authority\\network service']:
                        is_service = True
                    elif p_info['name'].lower() in ['svchost.exe', 'csrss.exe', 'wininit.exe', 'services.exe']:
                        is_service = True
                        
                    p_info['custom_type'] = "Service" if is_service else "App"
                    p_info['memory_mb'] = p_info['memory_info'].rss / (1024 * 1024)
                    
                    results.append(p_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Scan Error: {e}")

        # Sort: Services at bottom, High memory at top
        results.sort(key=lambda x: (x['custom_type'] == "Service", -x['memory_mb']))
        
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
            if self.active_category == "Apps" and p['custom_type'] != "App": continue
            if self.active_category == "Services" and p['custom_type'] != "Service": continue
            
            # Search Filter (Deep: Name OR Cmdline OR PID)
            if query:
                p_name_norm = normalize_text(p['name'])
                p_cmd_norm = normalize_text(p['cmdline_str'])
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
        ptype = proc_data['custom_type']
        
        msg = f"Are you sure you want to terminate:\n{name} (PID: {pid})?"
        icon = "warning"
        if ptype == "Service":
            msg += "\n\n⚠️ CRITICAL WARNING: This is a System Service.\nTerminating it may crash Windows!"
            icon = "error"
            
        if messagebox.askyesno("Confirm Action", msg, icon=icon):
            try:
                # Re-acquire process object to kill it
                p = psutil.Process(pid)
                p.terminate()
                self.after(500, self.start_scan_thread)
            except psutil.NoSuchProcess:
                messagebox.showwarning("Error", "Process no longer exists!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = App()
    app.mainloop()
