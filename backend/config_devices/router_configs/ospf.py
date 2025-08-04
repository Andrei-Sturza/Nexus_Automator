from backend.task_engine import establish_connection, extract_netmiko_config

def get_ospf_networks(net_connect):
    output = net_connect.send_command("show ip int brief")
    networks = set()

    for line in output.splitlines():
        if 'unassigned' in line or 'down' in line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue

        interface, ip_address = parts[0], parts[1]

        if ip_address == 'unassigned':
            continue

        # Determine network statement based on IP address range
        if ip_address.startswith('10.'):
            networks.add("network 10.0.0.0 0.255.255.255 area 0")
        elif ip_address.startswith('192.168.'):
            networks.add("network 192.168.0.0 0.0.255.255 area 0")
        elif ip_address.startswith('172.16.'):
            networks.add("network 172.16.0.0 0.15.255.255 area 0")
        else:
            octets = ip_address.split('.')
            if len(octets) == 4:
                networks.add(f"network {octets[0]}.{octets[1]}.{octets[2]}.0 0.0.0.255 area 0")

    return list(networks)


def configure_ospf(net_connect, process_id='1'):
    try:
        # Check for Loopback0 to use as router-id
        show_loopback = net_connect.send_command("show ip int brief | include Loopback0")
        router_id_cmd = ""
        if show_loopback and 'up' in show_loopback:
            loopback_ip = show_loopback.split()[1]
            router_id_cmd = f"router-id {loopback_ip}"

        network_commands = get_ospf_networks(net_connect)
        if not network_commands:
            return "No suitable interfaces found for OSPF configuration"

        config_commands = [f"router ospf {process_id}"]
        if router_id_cmd:
            config_commands.append(router_id_cmd)
        config_commands.extend(network_commands)

        output = net_connect.send_config_set(config_commands)
        return output

    except Exception as e:
        return f"OSPF configuration error: {str(e)}"


def run_ospf_workflow(device_name, config):
    try:
        net_connect = establish_connection(extract_netmiko_config(config))
        print(f"Configuring OSPF on device {device_name}...\n")
        output = configure_ospf(net_connect)
        print(output)
        print("\n--- OSPF Verification ---")
        print(net_connect.send_command("show run | section ospf"))
        print(net_connect.send_command("show ip ospf neighbor"))
        net_connect.disconnect()
    except Exception as e:
        print(f"[ERROR] {device_name}: {e}")
