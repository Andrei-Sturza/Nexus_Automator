import mysql.connector
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException


def extract_netmiko_config(config):
    return {
        "device_type": config["device_type"],
        "ip": config["ip"],
        "username": config["username"],
        "password": config["password"],
        "secret": config["secret"]
    }


# Load device configs from the MySQL database
def load_device_configs(
    host="localhost", user="root", passwd="Steaua1986", database="Devices"
):
    try:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=database
        )
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM RouterSwitches")
        devices_list = mycursor.fetchall()

        # Convert list to dictionary using device_name as the key
        devices_dict = {device["device_name"]: device for device in devices_list}
        return devices_dict

    except mysql.connector.Error as err:
        print(f"MySQL error: {err}")
        return {}

    finally:
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals():
            mydb.close()

# Establish Netmiko connection to a single device
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
