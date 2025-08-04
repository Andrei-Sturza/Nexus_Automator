from backend.task_engine import establish_connection, extract_netmiko_config
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

def build_vtp_config():
    config = []

    domain = input("\n🔧 Enter the VTP domain name: ").strip()
    config.append(f"vtp domain {domain}")

    mode = input("🔁 Select VTP mode (server, client, transparent): ").strip().lower()
    while mode not in ['server', 'client', 'transparent']:
        mode = input("❌ Invalid. Choose: server, client, or transparent: ").strip().lower()
    config.append(f"vtp mode {mode}")

    print("\n📌 NOTE: In VTP mode, you typically create VLANs only on the **server** switch.")
    return config

def configure_vtp(device_name, device_config):
    try:
        # Extract Netmiko-specific configuration
        netmiko_config = extract_netmiko_config(device_config)

        print(f"\n🔌 Connecting to {device_name} ({device_config['ip']})...")
        net_connect = establish_connection(netmiko_config)

        config = build_vtp_config()
        net_connect.send_config_set(config)

        output = net_connect.send_command("show vtp status")
        print("\n✅ VTP configured successfully.")
        print("\n🔧 Output:\n", output)

        net_connect.disconnect()

    except NetmikoTimeoutException:
        print(f"⛔ {device_name} - Host unreachable!")
    except NetmikoAuthenticationException:
        print(f"⛔ {device_name} - Authentication failed!")
    except Exception as e:
        print(f"⛔ {device_name} - Unexpected error: {str(e)}")
