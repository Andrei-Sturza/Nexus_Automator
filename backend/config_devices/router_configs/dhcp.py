#This is a more complex function, used for configuring a dhcp pool

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

def collect_dhcp_config():

    #Network address needed for dhcp pool and striping for eliminating any blank spaces
    network_address = input("Enter the network address that DHCP will use: ").strip()

    #Subnet mask needed for dhcp pool and striping for eliminating any blank spaces
    subnet_mask = input("Enter the subnet mask of the network: ").strip()

    #Default-gateway needed for dhcp pool and striping for eliminating any blank spaces
    default_gateway = input("Enter the default gateway for DHCP: ").strip()

    #Name of the pool
    pool_name = input("Enter DHCP pool name: ").strip()

    #The domain name that is preconfigured
    domain_name = 'gns3.local'

    #Google's dns server ip address for better and faster address translation
    dns_server = '8.8.8.8'

    #Excluding the default-gateway from the pool
    commands = [f'ip dhcp excluded-address {default_gateway}']

    #Ask for the range of addresses that needs to be excluded
    exclude = input("Exclude additional IPs? (Y/N): ").strip().upper()

    #Simple if statement
    if exclude == "Y":
        start = input("Start IP to exclude: ").strip()
        end = input("End IP to exclude: ").strip()
        commands.append(f'ip dhcp excluded-address {start} {end}')

    #Adding the commands in the command list
    commands.extend([
        f'ip dhcp pool {pool_name}',
        f' network {network_address} {subnet_mask}',
        f' default-router {default_gateway}',
        f' dns-server {dns_server}',
        f' domain-name {domain_name}'
    ])

    return commands

def configure_dhcp(device_config):

    #Apply DHCP config to the given device.
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
