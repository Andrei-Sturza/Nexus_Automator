from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

def collect_dhcp_config():
    network_address = input("Enter the network address that DHCP will use: ").strip()
    subnet_mask = input("Enter the subnet mask of the network: ").strip()
    default_gateway = input("Enter the default gateway for DHCP: ").strip()
    pool_name = input("Enter DHCP pool name: ").strip()

    domain_name = 'gns3.local'
    dns_server = '8.8.8.8'

    commands = [f'ip dhcp excluded-address {default_gateway}']

    exclude = input("Exclude additional IPs? (Y/N): ").strip().upper()
    if exclude == "Y":
        start = input("Start IP to exclude: ").strip()
        end = input("End IP to exclude: ").strip()
        commands.append(f'ip dhcp excluded-address {start} {end}')

    commands.extend([
        f'ip dhcp pool {pool_name}',
        f' network {network_address} {subnet_mask}',
        f' default-router {default_gateway}',
        f' dns-server {dns_server}',
        f' domain-name {domain_name}'
    ])

    return commands

def configure_dhcp(full_config):
    # Helper to extract only relevant fields for Netmiko connection
    def extract_netmiko_config(config):
        return {
            "device_type": config.get("device_type"),
            "ip": config.get("ip"),
            "username": config.get("username"),
            "password": config.get("password"),
            "secret": config.get("secret")
        }

    device_config = extract_netmiko_config(full_config)

    try:
        net_connect = ConnectHandler(**device_config)
        net_connect.enable()

        print(f"\n[{device_config['ip']}] Starting DHCP configuration...")
        commands = collect_dhcp_config()
        net_connect.send_config_set(commands)

        print(f"\n[{device_config['ip']}] DHCP Configuration Applied:")
        print(net_connect.send_command("show running-config | section dhcp"))

        net_connect.disconnect()

    except NetmikoTimeoutException:
        print(f"{device_config['ip']} - Host unreachable!")
    except NetmikoAuthenticationException:
        print(f"{device_config['ip']} - Authentication failed!")
    except Exception as e:
        print(f"{device_config['ip']} - Error: {e}")
