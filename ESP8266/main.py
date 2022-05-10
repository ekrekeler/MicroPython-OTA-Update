import program
from config import Config
from wifi_manager import WifiManager
from updater import Updater


# Load settings
conf = Config()

# Connect to Wi-Fi
wm = WifiManager(sys.platform.upper(), '')
wm.connect()

# Syncronize RTC with NTP server
try:
    ntptime.settime()
except OSError:
    print('Warning: Error while updating time from NTP server.')

# Run the program and updater in a loop
# The program must return the time in seconds it wants to sleep before running again
# If deep-sleep is desired instead then the while loop is not needed
while True:
    if time() > conf.get('last_checked') + conf.get('update_interval'):
        # Check for and perform updates
        try:
            updated = Updater.main(conf)
            conf.set('last_checked', time())
        except Exception as e:
            print(e.args[0])
        else:
            if updated:
                print('Software updated, going down for reset.')
                sleep(5)
                machine.reset()
            else:
                print('No update available at this time.')
    # Run the program
    sleep_sec = program.main()
    print(f'Sleeping {sleep_sec} seconds...')
    sleep(sleep_sec)
