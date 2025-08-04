from backend.task_engine import load_device_configs, establish_connection, extract_netmiko_config
from backend.net_monitor.notifier import send_telegram_alert

def check_ospf_neighbors():
    devices = load_device_configs()
    for name, config in devices.items():
        try:
            netmiko_config = extract_netmiko_config(config)
            conn = establish_connection(netmiko_config)

            ospf_output = conn.send_command("show ip ospf neighbor")

            conn.disconnect()

            if "FULL" not in ospf_output:
                send_telegram_alert(f"⚠️ {name} OSPF is not working properly.")
            else:
                send_telegram_alert(f"✅ OSPF is working properly on router {name}!")

        except Exception as e:
            send_telegram_alert(f"❌ Failed to connect to {name}: {e}")

if __name__ == "__main__":
    check_ospf_neighbors()
