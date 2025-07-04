#Here, I am doing the basic configuration for a router, ena sec pass, console configuration, user and pass
#I should add the service password encryption command to

import json
import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from getpass import getpass


def extract_ip():

    try:
        json_path = 'devices.json'
        if not os.path.exists(json_path):
            # Try devices subdirectory
            json_path = 'devices/devices.json'
            if not os.path.exists(json_path):
                raise FileNotFoundError("devices.json not found in current directory or devices/ subdirectory")

        with open(json_path) as f:
            data = json.load(f)
            return [router['ip'] for router in data.values()]
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in devices.json")
        return []
    except Exception as e:
        print(f"Error loading devices: {str(e)}")
        return []


def get_confirmation(prompt):

    while True:
        response = input(prompt).upper()
        if response in ('Y', 'N'):
            return response
        print("Invalid input. Please enter Y or N")


def connect_to_device(ip):

    return {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': 'admin',
        'password': 'cisco',
        'secret': 'cisco',
        'timeout': 15
    }


def configure_device(ip, device_config):

    print(f"\n==== Configuring device {ip} ====")

    device = connect_to_device(ip)

    try:
        with ConnectHandler(**device) as net_connect:
            net_connect.enable()

            output = net_connect.send_config_set(device_config['commands'])
            print("\nConfiguration Output:")
            print(output)

            # Verification commands
            print("\nVerification Output:")
            print(net_connect.send_command("show running-config | include hostname|enable|username|line con"))
        return True
    except NetmikoTimeoutException:
        print(f"Error: Host {ip} unreachable!")
    except NetmikoAuthenticationException:
        print(f"Error: Authentication failed for {ip}!")
    except Exception as e:
        print(f"Error configuring {ip}: {str(e)}")

    return False


def get_device_config(ip):

    print(f"\n=== Configuration for {ip} ===")
    config = {'commands': []}

    # Hostname configuration
    hostname = input(f"Enter hostname for {ip}: ").strip()
    config['commands'].append(f"hostname {hostname}")

    # Password configuration
    if get_confirmation(f"\nConfigure enable password for {ip}? (Y/N): ") == 'Y':
        if get_confirmation("Use secret password (more secure)? (Y/N): ") == 'Y':
            password = getpass("Enter secret password: ")
            config['commands'].append(f"enable secret {password}")
        else:
            password = getpass("Enter enable password: ")
            config['commands'].append(f"enable password {password}")

    # DNS configuration
    if get_confirmation(f"\nDisable DNS lookup on {ip}? (Y/N): ") == 'Y':
        config['commands'].append("no ip domain-lookup")

    # Console configuration
    if get_confirmation(f"\nConfigure console access on {ip}? (Y/N): ") == 'Y':
        username = input("Enter console username: ").strip()
        console_pass = getpass("Enter console password: ")
        config['commands'].extend([
            f"username {username} password {console_pass}",
            "line console 0",
            "login local",
            "exit"
        ])

    return config


def main():

    print("=== Cisco Device Configuration Tool ===")

    devices = extract_ip()
    if not devices:
        print("No devices available for configuration.")
        return

    device_configs = {}
    for ip in devices:
        device_configs[ip] = get_device_config(ip)

        # Show configuration summary
        print(f"\n=== Configuration Summary for {ip} ===")
        print("\n".join(device_configs[ip]['commands']))

        if get_confirmation("\nApply this configuration? (Y/N): ") == 'N':
            print(f"Configuration for {ip} cancelled!")
            device_configs[ip] = None

    # Apply configurations
    for ip, config in device_configs.items():
        if config:
            configure_device(ip, config)


if __name__ == "__main__":
    main()

