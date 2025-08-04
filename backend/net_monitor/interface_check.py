from backend.task_engine import load_device_configs, establish_connection, extract_netmiko_config
from backend.net_monitor.notifier import send_telegram_alert  # Fixed import path


def check_interfaces():
    devices = load_device_configs()

    for name, config in devices.items():
        try:
            # Use only Netmiko-relevant config fields for connection
            netmiko_config = extract_netmiko_config(config)
            conn = establish_connection(netmiko_config)

            output = conn.send_command("show ip int brief")

            conn.disconnect()

            down_interfaces = []

            for line in output.splitlines():
                if "Interface" in line:
                    continue
                parts = line.split()
                if len(parts) < 6:
                    continue
                intf_name = parts[0]
                status = parts[4].lower()
                protocol = parts[5].lower()

                if status != "up" or protocol != "up":
                    down_interfaces.append(intf_name)

            if down_interfaces:
                msg = (
                    f"⚠️ {name} ({config['ip']}) has interface(s) down:\n"
                    + "\n".join(f"🔻 {intf}" for intf in down_interfaces)
                )
                send_telegram_alert(msg)
            else:
                print(f"[{name}] ✅ All interfaces that are administratively enabled are up.")

        except Exception as e:
            send_telegram_alert(f"❌ Failed to check interfaces on {name}: {e}")


if __name__ == "__main__":
    check_interfaces()
