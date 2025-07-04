#This is a function that allows the user to autoconfig the device with a link-local ipv6 address

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

#Function used for retrieving the up interfaces, the actual interfaces where we can apply an ipv6 address
def get_up_interfaces(net_connect):

    #Retriving the data
    output = net_connect.send_command("show ip int brief")

    #Creating a list where we store the up interfaces
    up_int = []

    for line in output.splitlines():
        #If statement
        if 'unassigned' in line or 'down' in line:
            continue
        parts = line.split()

        #Ignoring the first line output
        if parts and parts[0] != 'Interface':
            up_int.append(parts[0])
    return up_int

#Configuring the devices
def configure_ipv6_autoconfig(device_config):

    try:
        print(f"[{device_config['ip']}] Connecting...")
        net_connect = ConnectHandler(**device_config)
        net_connect.enable()

        interfaces = get_up_interfaces(net_connect)

        if not interfaces:
            print(f"[{device_config['ip']}] No active interfaces found. Skipping.")
            net_connect.disconnect()
            return

        #Starting by enabling the ipv6 for the device
        commands = ['ipv6 unicast-routing']

        #Appending to the list the commands that we want to apply (entering the interface mode, autoconfig the ipv6 address)
        for interface in interfaces:
            commands.extend([
                f"interface {interface}",
                "ipv6 address autoconfig"
            ])

        print(f"[{device_config['ip']}] Applying IPv6 autoconfig to: {', '.join(interfaces)}")
        net_connect.send_config_set(commands)

        print(f"[{device_config['ip']}] Verifying IPv6 configuration...")
        print(net_connect.send_command("show ipv6 interface brief"))

        net_connect.disconnect()

    except NetmikoTimeoutException:
        print(f"{device_config['ip']} - Host unreachable!")
    except NetmikoAuthenticationException:
        print(f"{device_config['ip']} - Authentication failed!")
    except Exception as e:
        print(f"{device_config['ip']} - Unexpected error: {e}")
