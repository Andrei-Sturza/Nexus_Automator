#Function for checking if an interface is down

from backend.task_engine import load_device_configs, establish_connection
from backend.net_monitor.notifier import send_telegram_alert  # Fixed import path

def check_interfaces():

    devices = load_device_configs()

    for name, config in devices.items():
        try:

            #connecting to the device
            conn = establish_connection(config)

            #Retriving the data necessary for checking if an interface is down
            output = conn.send_command("show ip int brief")

            #Disconnecting
            conn.disconnect()

            #Initalizing a list for saving the down interfaces
            down_interfaces = []

            for line in output.splitlines():

                #We skip the first line
                if "Interface" in line:
                    continue
                parts = line.split()
                if len(parts) < 6:
                    continue
                intf_name = parts[0]

                #Making it lower for easier checking
                status = parts[4].lower()
                protocol = parts[5].lower()

                #Checking if an interface is down or administratively-down
                if status != "up" or protocol != "up":
                    down_interfaces.append(intf_name)

            if down_interfaces:
                msg = (
                    f"⚠️ {name} ({config['ip']}) has interface(s) down:\n"
                    + "\n".join(f"🔻 {intf}" for intf in down_interfaces)
                ) #List comprehension

                #Sending the actual message for the bot to display in Telegram
                send_telegram_alert(msg)
            else:
                print(f"[{name}] ✅ All interfaces that are administratively enabled are up.")

        except Exception as e:
            send_telegram_alert(f"❌ Failed to check interfaces on {name}: {e}")

if __name__ == "__main__":
    check_interfaces()
