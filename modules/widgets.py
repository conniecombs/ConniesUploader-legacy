# modules/widgets.py
import customtkinter as ctk
import tkinter as tk

class ScrollableFrame(ctk.CTkScrollableFrame):
    """
    Wrapper for CTkScrollableFrame to match the existing API.
    CustomTkinter handles scrolling natively.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Use 'self' directly as the frame to pack into
        self.scrollable_frame = self 

class CollapsibleGroupFrame(ctk.CTkFrame):
    def __init__(self, parent, title="Group"):
        super().__init__(parent)
        self.parent = parent
        self.title = title
        self.is_collapsed = False
        self.is_completed = False
        self.gallery_id = ""
        self.files = [] 
        
        # --- Header ---
        self.header = ctk.CTkFrame(self, height=30, corner_radius=6)
        self.header.pack(fill="x", pady=(2,0), ipadx=5, ipady=2)
        
        self.btn_toggle = ctk.CTkButton(self.header, text="-", width=20, height=20, command=self.toggle)
        self.btn_toggle.pack(side="left", padx=5)
        
        self.lbl_title = ctk.CTkLabel(self.header, text=title, font=("Segoe UI", 13, "bold"))
        self.lbl_title.pack(side="left", padx=5)
        
        self.lbl_counts = ctk.CTkLabel(self.header, text="(0 files)", text_color="gray")
        self.lbl_counts.pack(side="left", padx=5)

        # Group Progress Bar
        self.prog = ctk.CTkProgressBar(self.header, width=150)
        self.prog.set(0)
        self.prog.pack(side="right", padx=10)
        
        # --- Content Area ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="x", expand=True, padx=10, pady=5)
        
    def toggle(self):
        if self.is_collapsed:
            self.content_frame.pack(fill="x", expand=True, padx=10, pady=5)
            self.btn_toggle.configure(text="-")
        else:
            self.content_frame.pack_forget()
            self.btn_toggle.configure(text="+")
        self.is_collapsed = not self.is_collapsed

    def add_file(self, filepath):
        """
        Adds a file path to the internal list and updates the counter label.
        This was missing in the previous version, causing the crash.
        """
        self.files.append(filepath)
        self.lbl_counts.configure(text=f"({len(self.files)} files)")

    def mark_complete(self):
        """Visual cue that group is done."""
        self.is_completed = True
        self.lbl_title.configure(text_color="#34C759") # Green
        self.lbl_counts.configure(text="(Completed)", text_color="#34C759")
        self.prog.configure(progress_color="#34C759")

class LogWindow(ctk.CTkToplevel):
    def __init__(self, parent, initial_logs=[]):
        super().__init__(parent)
        self.title("Event Log")
        self.geometry("700x300")
        
        self.log_text = ctk.CTkTextbox(self, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        for line in initial_logs:
            self.append_log(line)
            
    def append_log(self, message):
        self.log_text.insert("end", message)
        self.log_text.see("end")

class MouseWheelComboBox(ctk.CTkComboBox):
    """
    A ComboBox that allows cycling through options with the mouse wheel
    while hovering over the widget.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<MouseWheel>", self._on_mouse_wheel)
        # Linux support (Button-4/5)
        self.bind("<Button-4>", lambda e: self._on_mouse_wheel(e, 120))
        self.bind("<Button-5>", lambda e: self._on_mouse_wheel(e, -120))

    def _on_mouse_wheel(self, event, linux_delta=None):
        if self._state == "disabled": return
        
        values = self._values
        if not values: return
        
        # Calculate direction
        delta = linux_delta if linux_delta else event.delta
        
        try:
            current_val = self.get()
            current_idx = values.index(current_val)
        except ValueError:
            current_idx = 0

        # Determine next index (Scroll UP = Previous, Scroll DOWN = Next)
        step = -1 if delta > 0 else 1
        new_idx = max(0, min(len(values) - 1, current_idx + step))
        
        if new_idx != current_idx:
            new_val = values[new_idx]
            self.set(new_val)
            if self._command:
                self._command(new_val)