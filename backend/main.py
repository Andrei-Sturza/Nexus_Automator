from backend.config_devices.router_configs.basic_config_router import get_device_config, configure_device
from backend.config_devices.router_configs.ospf import configure_ospf
from backend.config_devices.router_configs.backup_router import *
from backend.config_devices.router_configs.dhcp import configure_dhcp
from backend.config_devices.router_configs.ipv6_local_config import *
from backend.config_devices.switch_configs.basic_config_switch import configure_basic_switch
from backend.net_monitor.interface_check import check_interfaces
from backend.config_devices.router_configs.save_router_config import save_device_config
from net_monitor.ospf_check import check_ospf_neighbors
from backend.task_engine import load_device_configs, establish_connection
from backend.config_devices.switch_configs.vlan_config import configure_vlans
from backend.config_devices.switch_configs.etherchannel_config import configure_etherchannel
from backend.config_devices.switch_configs.spanning_tree import configure_stp
from backend.config_devices.switch_configs.vtp_config import configure_vtp
from backend.config_devices.switch_configs.save_config_switch import save_switch_config
from backend.config_devices.switch_configs.backup_switch import backup_switch


#First menu for choosing between the network configuration or network monitoring or switch configuration
def top_menu():
    print("\n=== Network Automation Toolkit ===")
    print("1. Configure a Router")
    print("2. Configure a Switch")
    print("3. Network Monitoring")
    print("4. Exit")
    return input("Choose an option (1-4): ").strip()


#Menu for router configuration
def router_menu():
    print("\n--- Router Configuration ---")
    print("1. Configure basic router settings")
    print("2. Configure OSPF")
    print("3. Configure DHCP")
    print("4. Configure IPv6 autoconfig")
    print("5. Backup device config")
    print("6. Save running-config to startup-config")
    print("7. Back to main menu")
    return input("Choose an option (1-7): ").strip()

#Menu for switch configuration
def switch_menu():
    print("\n--- Switch Configuration ---")
    print("1. Configure basic switch settings")
    print("2. Configure VLANs")
    print("3. Configure VTP")
    print("4. Save running-config to startup-config ")
    print("5. Configure EtherChannel")
    print("6. Configure Spanning Tree")
    print("7. Backup device config")
    print("8. Back to main menu")
    return input("Choose an option (1-8): ").strip()


#Menu for network monitoring (tried it with implementing a bot that sends notifications)
def monitor_menu():
    print("\n--- Network Monitoring ---")
    print("1. Check interface status")
    print("2. Check OSPF neighbors")
    print("3. Run all checks")
    print("4. Back to main menu")
    return input("Choose an option (1-4): ").strip()


#Select function
def select_device(devices):
    names = list(devices.keys())
    print("\nAvailable Devices:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")

    #Error checking
    try:
        choice = int(input("Select a device by number: ").strip())
        return names[choice - 1]
    except (IndexError, ValueError):
        print("Invalid selection.")
        return None

#Function for base config
def run_router_workflow(device_name, config):
    device_ip = config.get('ip')
    cli_config = get_device_config(device_ip)
    print("\n--- Configuration Preview ---")
    print("\n".join(cli_config['commands']))
    if input("Apply this configuration? (Y/N): ").strip().upper() == 'Y':
        configure_device(device_ip, cli_config)
    else:
        print("Configuration cancelled.")

#Function for ospf config
def run_ospf_workflow(device_name, config):
    try:
        net_connect = establish_connection(config)
        print("Configuring OSPF...\n")
        print(configure_ospf(net_connect))
        print("\n--- OSPF Verification ---")
        print(net_connect.send_command("show run | section ospf"))
        print(net_connect.send_command("show ip ospf neighbor"))
        net_connect.disconnect()
    except Exception as e:
        print(f"[ERROR] {device_name}: {e}")

#Main
def main():
    devices = load_device_configs()
    if not devices:
        print("No devices found.")
        return

    while True:
        section = top_menu()
        if section == '1':  # Router config
            while True:
                choice = router_menu()
                if choice == '7':
                    break
                device_name = select_device(devices)
                if not device_name:
                    continue
                config = devices[device_name]

                if choice == '1':
                    run_router_workflow(device_name, config)
                elif choice == '2':
                    run_ospf_workflow(device_name, config)
                elif choice == '3':
                    configure_dhcp(config)
                elif choice == '4':
                    configure_ipv6_autoconfig(config)
                elif choice == '5':
                    backup_device(device_name, config)
                elif choice == '6':
                    save_device_config(device_name, config)

        elif section == '2':  # Switch config
            while True:
                choice = switch_menu()
                if choice == '8':
                    break
                device_name = select_device(devices)
                if not device_name:
                    continue
                config = devices[device_name]

                if choice == '1':
                    configure_basic_switch(device_name, config)
                elif choice == '2':
                    configure_vlans(device_name, config)
                elif choice == '3':
                    configure_vtp(device_name, config)
                elif choice == '4':
                    save_switch_config(device_name, config)
                elif choice == '5':
                    configure_etherchannel(device_name, devices[device_name])
                elif choice == '6':
                    configure_stp(device_name, devices[device_name])
                elif choice == '7':
                    backup_switch(device_name, config)

        elif section == '3':  # Monitoring
            while True:
                choice = monitor_menu()
                if choice == '4':
                    break
                elif choice == '1':
                    check_interfaces()
                elif choice == '2':
                    check_ospf_neighbors()
                elif choice == '3':
                    check_interfaces()
                    check_ospf_neighbors()
                else:
                    print("Invalid option. Try again.")
        elif section == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
