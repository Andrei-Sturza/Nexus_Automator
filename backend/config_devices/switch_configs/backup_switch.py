import os
import datetime
from backend.task_engine import load_device_configs, establish_connection, extract_netmiko_config

# Backup a single switch
def backup_switch(device_name, device_config):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("switch_backups", exist_ok=True)

    try:
        # Extract only Netmiko-relevant fields
        netmiko_config = extract_netmiko_config(device_config)

        # Establish connection
        net_connect = establish_connection(netmiko_config)

        # Retrieve running configuration
        output = net_connect.send_command("show running-config")

        # Disconnect
        net_connect.disconnect()

        # Save to file
        filename = f"switch_backups/{device_name}_{netmiko_config['ip']}_{timestamp}.txt"
        with open(filename, "w") as f:
            f.write(output)

        print(f"[SUCCESS] Backup saved: {filename}")

    except Exception as e:
        print(f"[ERROR] Could not backup {device_name}: {e}")

# Backup all switches
def backup_all_switches():
    devices = load_device_configs()
    if not devices:
        print("No devices found to backup.")
        return

    print(f"\n=== Starting Backup for {len(devices)} Devices ===")
    for device_name, device_config in devices.items():
        backup_switch(device_name, device_config)
