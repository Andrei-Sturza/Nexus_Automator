from backend.task_engine import establish_connection, extract_netmiko_config
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

def build_stp_config():
    config = []

    vlan_id = input("\n📥 Enter VLAN ID to configure STP on: ").strip()
    config.append(f"spanning-tree vlan {vlan_id}")
    config.append(f"spanning-tree vlan {vlan_id} mode pvst")

    manual_priority = input("\nSet priority manually? (Y/N): ").strip().lower()
    if manual_priority == 'y':
        priority = input("Enter priority value (0–61440, multiple of 4096): ").strip()
        config.append(f"spanning-tree vlan {vlan_id} priority {priority}")
    else:
        is_root = input("Make this switch root bridge? (Y/N): ").strip().lower()
        if is_root == 'y':
            config.append(f"spanning-tree vlan {vlan_id} root primary")
        else:
            config.append(f"spanning-tree vlan {vlan_id} root secondary")

    return config

def configure_stp(device_name, device_config):
    try:
        print(f"\n🔌 Connecting to {device_name} ({device_config['ip']})...")

        # Extract Netmiko-ready configuration
        netmiko_config = extract_netmiko_config(device_config)

        net_connect = establish_connection(netmiko_config)

        config = build_stp_config()
        net_connect.send_config_set(config)

        output = net_connect.send_command("show spanning-tree")
        print("\n✅ STP configured successfully.")
        print("\n🔧 Output:\n", output)

        net_connect.disconnect()

    except NetmikoTimeoutException:
        print(f"⛔ {device_name} - Host unreachable!")
    except NetmikoAuthenticationException:
        print(f"⛔ {device_name} - Authentication failed!")
    except Exception as e:
        print(f"⛔ {device_name} - Unexpected error: {str(e)}")
