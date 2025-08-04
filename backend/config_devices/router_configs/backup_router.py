import os
import datetime
from backend.task_engine import establish_connection, extract_netmiko_config, load_device_configs


# Backup for one device
def backup_device(name, config):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("router_backups", exist_ok=True)

    try:
        # Extract only Netmiko relevant config
        netmiko_config = extract_netmiko_config(config)

        # Establish connection with cleaned config
        net_connect = establish_connection(netmiko_config)

        # Retrieve running configuration
        output = net_connect.send_command("show running-config")

        # Disconnect
        net_connect.disconnect()

        # File naming
        filename = f"router_backups/{name}_{netmiko_config['ip']}_{timestamp}.txt"
        with open(filename, "w") as f:
            f.write(output)
        print(f"[SUCCESS] Backup saved: {filename}")

    except Exception as e:
        print(f"[ERROR] Could not backup {name}: {e}")

# Backup all devices
def backup_all_devices():
    devices = load_device_configs()
    if not devices:
        print("No devices found to backup.")
        return

    print(f"\n=== Starting Backup for {len(devices)} Devices ===")
    for name, config in devices.items():
        backup_device(name, config)
