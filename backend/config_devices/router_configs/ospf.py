#Here, I handle the ospf configuration for the router that is selected
def get_ospf_networks(net_connect):

    output = net_connect.send_command("show ip int brief")
    networks = []

    for line in output.splitlines():
        if 'unassigned' in line or 'down' in line:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1].count('.') == 3:
            interface, ip_address, *_ = parts
            if ip_address == 'unassigned':
                continue

            #This 3 ranges of addresses are private and usually used in configuring the devices, I decided to add them like this
            #in the network command
            if ip_address.startswith('10.'):
                networks.append("network 10.0.0.0 0.255.255.255 area 0")
            elif ip_address.startswith('192.168.'):
                networks.append("network 192.168.0.0 0.0.255.255 area 0")
            elif ip_address.startswith('172.16.'):
                networks.append('172.16.0.0 0.15.255.255 area 0')
            else:
                #Spliting the address to be easier to write the network command
                octets = ip_address.split('.')
                networks.append(f"network {octets[0]}.{octets[1]}.{octets[2]}.0 0.0.0.255 area 0")

    seen = set()
    #List comprehension
    return [cmd for cmd in networks if not (cmd in seen or seen.add(cmd))]

#Sending the commands to the router
def configure_ospf(net_connect, process_id='1'):
    try:
        router_id_cmd = ""
        show_loopback = net_connect.send_command("show ip int brief | include Loopback0")

        #If I have a loopback address, I configure it as the router-id of the ospf
        if show_loopback and 'up' in show_loopback:
            loopback_ip = show_loopback.split()[1]
            router_id_cmd = f"router-id {loopback_ip}"

        #Calling the function above to retrieve the necessary commands
        network_commands = get_ospf_networks(net_connect)
        if not network_commands:
            return "No suitable interfaces found for OSPF configuration"

        config_commands = [f"router ospf {process_id}"]
        if router_id_cmd:
            config_commands.append(router_id_cmd)
        config_commands.extend(network_commands)

        #Sending the commands by ssh
        output = net_connect.send_config_set(config_commands)

        return output

    except Exception as e:
        return f"OSPF configuration error: {str(e)}"