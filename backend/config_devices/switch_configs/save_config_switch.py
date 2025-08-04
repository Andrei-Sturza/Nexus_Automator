from backend.task_engine import establish_connection, extract_netmiko_config
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

def save_switch_config(device_name, device_config):
    print(f"\n#### Connecting to {device_name} ({device_config['ip']}) ####")

    try:
        # Extract Netmiko-compatible fields
        netmiko_config = extract_netmiko_config(device_config)

        # Connect to the switch
        net_connect = establish_connection(netmiko_config)

        # Send command to save configuration
        output = net_connect.send_command("write memory")  # or just 'write'

        print(f"✅ {device_name}: Configuration saved successfully.")
        print(f"Output:\n{output}\n")

        net_connect.disconnect()

    except NetmikoTimeoutException:
        print(f"❌ {device_name} - Host unreachable!")
    except NetmikoAuthenticationException:
        print(f"❌ {device_name} - Authentication failed!")
    except Exception as e:
        print(f"❌ {device_name} - Unexpected error: {e}")
