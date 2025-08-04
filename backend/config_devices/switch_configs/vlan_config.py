from backend.task_engine import establish_connection, extract_netmiko_config
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

def creating_vlans(n, config):
    for _ in range(n):
        number = input("\nVLAN ID: ").strip()
        config.append(f"vlan {number}")

        name = input("VLAN Name: ").strip()
        config.append(f"name {name}")

        conf = input("Do you want to configure an IP for the VLAN? (Y/N): ").strip().upper()
        if conf == 'Y':
            ip_address = input("IP address: ").strip()
            net_mask = input("Subnet mask: ").strip()
            config.extend([
                f"interface vlan {number}",
                f"ip address {ip_address} {net_mask}",
                "no shutdown"
            ])

def configure_vlans(device_name, device_config):
    try:
        # Extract Netmiko-ready config
        netmiko_config = extract_netmiko_config(device_config)

        print(f"\n🔌 Connecting to {device_name} ({device_config['ip']})...")
        net_connect = establish_connection(netmiko_config)

        config = []
        vlan_count = int(input(f"\nHow many VLANs do you want to create on {device_name}? "))
        creating_vlans(vlan_count, config)

        print(f"\n📤 Sending configuration to {device_name}...")
        output = net_connect.send_config_set(config)

        print("\n✅ VLANs configured successfully.")
        print("\n🔧 Output:\n", output)

        net_connect.disconnect()

    except NetmikoTimeoutException:
        print(f"❌ {device_name} - Host unreachable!")
    except NetmikoAuthenticationException:
        print(f"❌ {device_name} - Authentication failed!")
    except Exception as e:
        print(f"❌ {device_name} - Unexpected error: {e}")
