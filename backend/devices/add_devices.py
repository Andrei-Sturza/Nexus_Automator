import mysql.connector

host = "localhost"
user = "root"
passwd = "Steaua1986"
database = "Devices"

mydb = mysql.connector.connect(
    host=host,
    user=user,
    passwd=passwd,
    database=database
)

def insert_new_device():

    mycursor = mydb.cursor()

    devicename = input("Please provide the device name you want to use: ")
    devicetype = "cisco_ios"
    IP = input("Please provide the ip address that you want to use for remote connections: ")
    user = input("Username used for the local user database: ")
    pas = input("Password used for the local user database: ")
    sec = input("Enable secret password used: ")

    sql = """
    INSERT INTO RouterSwitches (device_name, device_type, ip, username, password, secret)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (devicename, devicetype, IP, user, pas, sec)

    mycursor.execute(sql, values)
    mydb.commit()

    print("Values inserted with success")

    mycursor.close()
    mydb.close()