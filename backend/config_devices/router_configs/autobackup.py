#Not actually used

import schedule
import time
from backup_router import backup_all_devices

schedule.every().day.at("02:00").do(backup_all_devices)

while True:
    schedule.run_pending()
    time.sleep(60)
