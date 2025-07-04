#This is what I used to handle the connectivity to the router, it's a bit easier,
#and the code is clearer, handling in one file, and not for any functionality

import json
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

#I used the absolute path to be sure that if I want to access the json file anywhere in the project, this actually works
def load_device_configs(json_path='/home/americanu/PycharmProjects/Automation/backend/devices/devices.json'):

    try:
        with open(json_path) as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading device configs: {e}")
        return {}

#Connection function
def establish_connection(config):
    try:
        net_connect = ConnectHandler(**config)
        net_connect.enable()
        return net_connect
    except NetmikoTimeoutException:
        raise ConnectionError(f"Connection timeout for device {config.get('ip')}")
    except NetmikoAuthenticationException:
        raise PermissionError(f"Authentication failed for device {config.get('ip')}")
    except Exception as e:
        raise RuntimeError(f"Connection error for device {config.get('ip')}: {e}")
