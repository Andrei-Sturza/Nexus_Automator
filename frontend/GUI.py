import tkinter as tk
from tkinter import ttk, messagebox
from backend.task_engine import load_device_configs, establish_connection
from backend.config_devices.switch_configs import vlan_config
from backend.config_devices.switch_configs import save_config_switch



class NetworkAutomationDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("NetAutomate Pro")
        self.root.geometry("1200x800")

        self.selected_device = None
        self.active_tab = "dashboard"
        self.config_type = "basic"

        self.devices = [
            {"id": name, "name": name, "ip": cfg['ip'], "type": "Router" if 'ospf' in name.lower() else "Switch",
             "status": "online", "location": "Unknown"}
            for name, cfg in load_device_configs().items()
        ]

        self.automation_tasks = [
            {"id": "1", "name": "Daily Config Backup", "status": "completed", "lastRun": "2 hours ago",
             "nextRun": "22 hours"},
            {"id": "2", "name": "OSPF Configuration", "status": "running", "lastRun": "Running now",
             "nextRun": "On-demand"},
            {"id": "3", "name": "DHCP Pool Setup", "status": "completed", "lastRun": "1 day ago", "nextRun": "Manual"}
        ]

        self.create_main_ui()

    def create_main_ui(self):
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill=tk.X)

        ttk.Label(header, text="NetAutomate Pro", font=("Arial", 16, "bold")).pack(side=tk.LEFT)

        nav_buttons = ["Dashboard", "Devices", "Switch Config", "Backup"]
        for name in nav_buttons:
            ttk.Button(header, text=name, command=lambda n=name: self.switch_tab(n)).pack(side=tk.LEFT, padx=5)

        self.main_frame = ttk.Notebook(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.tabs = {}
        self.create_dashboard_tab()
        self.create_devices_tab()
        self.create_switch_config_tab()
        self.create_backup_tab()

    def switch_tab(self, name):
        self.main_frame.select(self.tabs[name])

    def create_dashboard_tab(self):
        tab = ttk.Frame(self.main_frame)
        self.main_frame.add(tab, text="Dashboard")
        self.tabs["Dashboard"] = tab

        ttk.Label(tab, text="Welcome to NetAutomate Pro", font=("Arial", 14)).pack(pady=20)

    def create_devices_tab(self):
        tab = ttk.Frame(self.main_frame)
        self.main_frame.add(tab, text="Devices")
        self.tabs["Devices"] = tab

        for device in self.devices:
            frame = ttk.Frame(tab, padding=10, relief=tk.RIDGE)
            frame.pack(fill=tk.X, pady=2)

            ttk.Label(frame, text=f"{device['name']} ({device['ip']}) - {device['type']}").pack(side=tk.LEFT)
            ttk.Button(frame, text="Configure", command=lambda d=device: self.configure_device(d)).pack(side=tk.RIGHT)

    def configure_device(self, device):
        result = messagebox.askyesno("Confirm", f"Configure basic settings for {device['name']}?")
        if result:
            try:
                configure_basic_switch(device['name'], {
                    'device_type': 'cisco_ios',
                    'ip': device['ip'],
                    'username': 'admin',
                    'password': 'cisco',
                    'secret': 'cisco'
                })
                messagebox.showinfo("Success", f"{device['name']} configured successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def create_switch_config_tab(self):
        tab = ttk.Frame(self.main_frame)
        self.main_frame.add(tab, text="Switch Config")
        self.tabs["Switch Config"] = tab

        ttk.Label(tab, text="Switch Configuration", font=("Arial", 14)).pack(pady=10)

        ttk.Button(tab, text="Configure VLANs", command=self.configure_vlans_ui).pack(pady=5)

    def configure_vlans_ui(self):
        win = tk.Toplevel(self.root)
        win.title("VLAN Configurator")

        ttk.Label(win, text="Select Device").pack()
        device_names = [d['name'] for d in self.devices if d['type'] == 'Switch']
        device_var = tk.StringVar()
        device_menu = ttk.Combobox(win, values=device_names, textvariable=device_var)
        device_menu.pack()

        ttk.Button(win, text="Configure VLANs", command=lambda: self.run_vlan_config(device_var.get())).pack(pady=5)

    def run_vlan_config(self, device_name):
        devices = load_device_configs()
        if device_name in devices:
            try:
                configure_vlans(device_name, devices[device_name])
                messagebox.showinfo("Success", f"VLANs configured on {device_name}.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def create_backup_tab(self):
        tab = ttk.Frame(self.main_frame)
        self.main_frame.add(tab, text="Backup")
        self.tabs["Backup"] = tab

        ttk.Label(tab, text="Backup Device Configuration", font=("Arial", 14)).pack(pady=10)

        ttk.Button(tab, text="Backup All", command=self.backup_all).pack(pady=5)

    def backup_all(self):
        devices = load_device_configs()
        for name, config in devices.items():
            try:
                save_device_config(name, config)
            except Exception as e:
                print(f"Failed to backup {name}: {e}")
        messagebox.showinfo("Backup Complete", "All configurations saved.")


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkAutomationDashboard(root)
    root.mainloop()
