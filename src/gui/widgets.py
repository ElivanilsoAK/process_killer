import customtkinter as ctk

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
        is_service = proc.get('custom_type') == "Service"
        type_text = "SERVICE" if is_service else "APP"
        type_fg = "#f39c12" if is_service else "#2ecc71"
        
        self.lbl_type = ctk.CTkLabel(self, text=type_text, width=70, text_color=type_fg, font=("Roboto", 11, "bold"))
        self.lbl_type.grid(row=0, column=2, padx=10, pady=8)

        # User
        user = proc.get('username') or "-"
        if len(user) > 12: user = user[:10] + "..."
        self.lbl_user = ctk.CTkLabel(self, text=user, width=100, anchor="w", text_color="gray70")
        self.lbl_user.grid(row=0, column=3, padx=10, pady=8)

        # Memory
        mem_mb = proc.get('memory_mb', 0)
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
