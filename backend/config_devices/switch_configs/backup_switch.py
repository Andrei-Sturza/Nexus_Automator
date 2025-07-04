#This functions are used to backup the configuration of the device

import os
import datetime
from backend.task_engine import load_device_configs, establish_connection

#Backup for one device
def backup_switch(name, config):

    #Timestamp used
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #Creating a directory for backup storing
    os.makedirs("switch_backups", exist_ok=True)

    try:

        #Connecting to the device
        net_connect = establish_connection(config)

        #Retriving the running configuration
        output = net_connect.send_command("show running-config")

        #Disconnecting from the device
        net_connect.disconnect()

        #Naming the file using the timestamp and the name of the router + ip to better access the backup
        filename = f"switch_backups/{name}_{config['ip']}_{timestamp}.txt"
        with open(filename, "w") as f:
            #Writing in file
            f.write(output)
        print(f"[SUCCESS] Backup saved: {filename}")
    except Exception as e:
        print(f"[ERROR] Could not backup {name}: {e}")

#Backup for all devices using the function above
def backup_all_devices():

    devices = load_device_configs()
    if not devices:
        print("No devices found to backup.")
        return

    print(f"\n=== Starting Backup for {len(devices)} Devices ===")
    for name, config in devices.items():
        backup_switch(name, config)
