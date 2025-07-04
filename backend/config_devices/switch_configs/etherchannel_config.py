from backend.task_engine import establish_connection
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException


def creating_etherchannel():

    eth_type = input('\nPlease enter the type of EtherChannel (LACP or PAgP): ').strip().lower()
    while eth_type not in ("lacp", "pagp"):
        eth_type = input("Invalid type. Please enter LACP or PAgP: ").strip().lower()

    interfaces = input('\nPlease enter the interfaces (e.g., Gi0/1-2, Gi0/3): ').strip()

    commands = [
        f"interface range {interfaces}",
        "channel-group 1 mode active" if eth_type == "lacp" else "channel-group 1 mode desirable"
    ]
    return commands


def configure_etherchannel(device_name, device_config):

    try:
        print(f"\n🔌 Connecting to {device_name} ({device_config['ip']})")
        net_connect = establish_connection(device_config)

        config = creating_etherchannel()
        net_connect.send_config_set(config)

        print(f"\n✅ EtherChannel configured successfully on {device_name}")

        net_connect.disconnect()

    except NetmikoTimeoutException:
        print(f"⛔ {device_name} - Host unreachable!")
    except NetmikoAuthenticationException:
        print(f"⛔ {device_name} - Authentication failed!")
    except Exception as e:
        print(f"⛔ {device_name} - Unexpected error: {str(e)}")
