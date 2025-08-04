def run_basic_router_configuration(device_name, config):
    from netmiko import ConnectHandler
    from getpass import getpass

    print(f"\n=== Basic Router Configuration: {device_name} ({config['ip']}) ===")
    cli_config = {'commands': []}

    # Hostname
    hostname = input(f"Enter hostname for {device_name}: ").strip()
    cli_config['commands'].append(f"hostname {hostname}")

    # Password encryption
    cli_config['commands'].append("service password-encryption")

    # Enable password
    use_enable = input("Configure enable password? (Y/N): ").strip().upper()
    if use_enable == 'Y':
        if input("Use secret? (Y/N): ").strip().upper() == 'Y':
            password = getpass("Enter secret password: ")
            cli_config['commands'].append(f"enable secret {password}")
        else:
            password = getpass("Enter enable password: ")
            cli_config['commands'].append(f"enable password {password}")

    # Disable DNS lookup
    if input("Disable DNS lookup? (Y/N): ").strip().upper() == 'Y':
        cli_config['commands'].append("no ip domain-lookup")

    # Console access
    if input("Configure console access? (Y/N): ").strip().upper() == 'Y':
        username = input("Console username: ").strip()
        console_pass = getpass("Console password: ")
        cli_config['commands'].extend([
            f"username {username} password {console_pass}",
            "line console 0",
            "login local",
            "exit"
        ])

    # Confirm and apply
    print("\n🔧 Configuration Preview:")
    print("\n".join(cli_config['commands']))
    confirm = input("\nApply this configuration? (Y/N): ").strip().upper()
    if confirm != 'Y':
        print("❌ Configuration cancelled.")
        return

    # Apply configuration
    try:
        connection_params = {
            "device_type": config["device_type"],
            "host": config["ip"],
            "username": config["username"],
            "password": config["password"],
            "secret": config["secret"]
        }

        with ConnectHandler(**connection_params) as net_connect:
            net_connect.enable()
            output = net_connect.send_config_set(cli_config['commands'])
            print("\n✅ Configuration applied:")
            print(output)

            print("\n📄 Verification:")
            print(net_connect.send_command("show run | include hostname|enable|username|line con"))

    except Exception as e:
        print(f"⛔ Error configuring {device_name}: {e}")
