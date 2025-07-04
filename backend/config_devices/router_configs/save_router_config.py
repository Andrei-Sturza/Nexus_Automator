#This function is used for simply saving the config of the device because the function from Netmiko doesn't work properly

from backend.task_engine import establish_connection
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

def save_device_config(device_name, device_config):

    #Simple prompt
    print(f"\n#### Connecting to {device_name} ({device_config['ip']}) ####")

    #Used it with error checking
    try:

        #Connecting to the device
        net_connect = establish_connection(device_config)

        #Sending the actual command to the router
        output = net_connect.send_command("write memory")  # or just 'write'

        #Prompting a success message
        print(f"✅ {device_name}: Configuration saved successfully.")
        print(f"Output:\n{output}\n")

        #Disconnecting from the router
        net_connect.disconnect()

    except NetmikoTimeoutException:
        print(f"❌ {device_name} - Host unreachable!")
    except NetmikoAuthenticationException:
        print(f"❌ {device_name} - Authentication failed!")
    except Exception as e:
        print(f"❌ {device_name} - Unexpected error: {e}")
