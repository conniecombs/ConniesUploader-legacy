# modules/gallery_manager.py
import customtkinter as ctk
from tkinter import messagebox
import pyperclip
import threading
from bs4 import BeautifulSoup
from . import config, api

class GalleryManager(ctk.CTkToplevel):
    def __init__(self, parent, creds, callback=None):
        super().__init__(parent)
        self.creds = creds
        self.callback = callback 
        self.title("Unified Gallery Manager")
        self.geometry("500x450")
        
        # Center window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (500 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (450 // 2)
        self.geometry(f"+{x}+{y}")
        self.transient(parent)
        self.grab_set()

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add("imx.to")
        self.tabview.add("vipr.im")
        
        self._setup_imx(self.tabview.tab("imx.to"))
        self._setup_vipr(self.tabview.tab("vipr.im"))

    def _setup_imx(self, parent):
        ctk.CTkLabel(parent, text="Create New Gallery", font=("", 14, "bold")).pack(pady=(10, 5))
        self.entry_imx_name = ctk.CTkEntry(parent, placeholder_text="Gallery Name")
        self.entry_imx_name.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(parent, text="Create Gallery", command=self.create_imx).pack(pady=10)
        
        ctk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=10, pady=15)
        
        ctk.CTkLabel(parent, text="Rename Gallery", font=("", 14, "bold")).pack(pady=(5, 5))
        self.entry_imx_id = ctk.CTkEntry(parent, placeholder_text="Existing Gallery ID")
        self.entry_imx_id.pack(fill="x", padx=20, pady=5)
        self.entry_imx_newname = ctk.CTkEntry(parent, placeholder_text="New Name")
        self.entry_imx_newname.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(parent, text="Rename", command=self.rename_imx, fg_color="orange").pack(pady=10)

    def _setup_vipr(self, parent):
        ctk.CTkLabel(parent, text="Create New Folder/Gallery", font=("", 14, "bold")).pack(pady=(10, 5))
        self.entry_vipr_name = ctk.CTkEntry(parent, placeholder_text="Folder Name")
        self.entry_vipr_name.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(parent, text="Create Folder", command=self.create_vipr).pack(pady=10)

    # --- Logic ---

    def create_imx(self):
        name = self.entry_imx_name.get().strip()
        if not name: return messagebox.showerror("Error", "Name required")
        
        def _task():
            client = api.create_resilient_client()
            try:
                gid = api.create_imx_gallery(self.creds['imx_user'], self.creds['imx_pass'], name, client)
                if gid:
                    self.after(0, lambda: self._success("imx.to", gid, f"Gallery Created: {gid}"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", "Failed to create IMX gallery"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                client.close()
        threading.Thread(target=_task, daemon=True).start()

    def rename_imx(self):
        gid = self.entry_imx_id.get().strip()
        new_name = self.entry_imx_newname.get().strip()
        if not gid or not new_name: return messagebox.showerror("Error", "ID and Name required")
        
        def _task():
            client = api.create_resilient_client()
            try:
                # 1. Login
                login_data = {"usr_email": self.creds['imx_user'], "pwd": self.creds['imx_pass'], "remember": "1", "doLogin": "Login"}
                client.post(config.IMX_LOGIN_URL, data=login_data, follow_redirects=True)
                
                # 2. Get the Edit Page
                edit_url = f"{config.IMX_GALLERY_EDIT_URL}?id={gid}"
                r_get = client.get(edit_url)
                
                # 3. Parse hidden tokens
                soup = BeautifulSoup(r_get.text, 'html.parser')
                data = {"id": gid, "gallery_name": new_name, "submit_new_gallery_name": "Rename Gallery"}
                
                target_form = None
                for form in soup.find_all('form'):
                    if form.find('input', {'name': 'gallery_name'}):
                        target_form = form
                        break
                
                if target_form:
                    for hidden in target_form.find_all('input', type='hidden'):
                        name = hidden.get('name')
                        val = hidden.get('value')
                        if name and val:
                            data[name] = val

                # 4. Post with Referer Header + FOLLOW REDIRECTS
                headers = {"Referer": edit_url}
                r = client.post(config.IMX_GALLERY_EDIT_URL, data=data, headers=headers, follow_redirects=True)

                if r.status_code == 200:
                    self.after(0, lambda: messagebox.showinfo("Success", "Gallery Renamed"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", f"Rename failed: {r.status_code}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                client.close()
        threading.Thread(target=_task, daemon=True).start()

    def create_vipr(self):
        name = self.entry_vipr_name.get().strip()
        if not name: return messagebox.showerror("Error", "Name required")
        
        def _task():
            client = api.create_resilient_client()
            try:
                if api.vipr_login(self.creds['vipr_user'], self.creds['vipr_pass'], client):
                    gid = api.create_vipr_gallery(client, name)
                    if gid:
                        self.after(0, lambda: self._success("vipr.im", gid, f"Folder Created: {gid}"))
                    else:
                        self.after(0, lambda: messagebox.showerror("Error", "Failed to create folder"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", "Vipr Login Failed"))
            finally:
                client.close()
        threading.Thread(target=_task, daemon=True).start()

    def _success(self, service, gid, msg):
        pyperclip.copy(gid)
        messagebox.showinfo("Success", msg)
        if self.callback:
            self.callback(service, gid)