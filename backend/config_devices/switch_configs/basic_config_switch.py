from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from getpass import getpass
from backend.task_engine import establish_connection, extract_netmiko_config

def get_confirmation(prompt):
    while True:
        response = input(prompt).strip().upper()
        if response in ('Y', 'N'):
            return response
        print("Invalid input. Please enter Y or N")

def configure_basic_switch(device_name, device_config):
    print(f"\n#### Connecting to {device_name} ({device_config['ip']}) ####")

    try:
        # Extract Netmiko-specific config
        netmiko_config = extract_netmiko_config(device_config)

        # Establish connection
        net_connect = establish_connection(netmiko_config)

        config_commands = []

        print(f"\n=== Configuration for {device_name} ({device_config['ip']}) ===")

        # Hostname
        hostname = input(f"Enter hostname for {device_name}: ").strip()
        config_commands.append(f"hostname {hostname}")

        # Enable password
        if get_confirmation("Configure enable password? (Y/N): ") == 'Y':
            if get_confirmation("Use secret password (more secure)? (Y/N): ") == 'Y':
                password = getpass("Enter secret password: ")
                config_commands.append(f"enable secret {password}")
            else:
                password = getpass("Enter enable password: ")
                config_commands.append(f"enable password {password}")

        # Disable DNS lookup
        if get_confirmation("Disable DNS lookup? (Y/N): ") == 'Y':
            config_commands.append("no ip domain-lookup")

        # Console access
        if get_confirmation("Configure console access? (Y/N): ") == 'Y':
            username = input("Enter console username: ").strip()
            console_pass = getpass("Enter console password: ")
            config_commands.extend([
                f"username {username} password {console_pass}",
                "line console 0",
                "login local",
                "exit"
            ])

        # Send config commands
        output = net_connect.send_config_set(config_commands)
        print("\n✅ Configuration sent to device.")
        print("🔧 Output:\n", output)

        net_connect.disconnect()

    except NetmikoTimeoutException:
        print(f"❌ {device_name} - Host unreachable!")
    except NetmikoAuthenticationException:
        print(f"❌ {device_name} - Authentication failed!")
    except Exception as e:
        print(f"❌ {device_name} - Unexpected error: {e}")
