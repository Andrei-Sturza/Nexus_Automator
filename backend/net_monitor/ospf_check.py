#This is the function used for checking if any neighbor is down in the Ospf process

from backend.task_engine import load_device_configs, establish_connection
from  backend.net_monitor.notifier import send_telegram_alert

def check_ospf_neighbors():

    devices = load_device_configs()
    for name, config in devices.items():
        try:
            #Connecting to the device
            conn = establish_connection(config)

            #Retriving the datas used to determine if Ospf is working
            ospf = conn.send_command("show ip ospf neighbor")

            #Disconnecting from the router
            conn.disconnect()

            #Checking if a neighbor is in any other state then FULL (Meaning that is down)
            if "FULL" not in ospf:
                #Sending the alert using the name of the router
                send_telegram_alert(f"⚠️ {name} OSPF is not working properly.")
            else:
                #Sending a message that everything works properly
                send_telegram_alert(f"✅ Ospf is working properly on router {name}!")
        except Exception as e:
            send_telegram_alert(f"❌ Failed to connect to {name}: {e}")

