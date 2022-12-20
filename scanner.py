from utils import Scanner
import json
import requests
from datetime import datetime, timedelta

print("Setting up ...")
# get an Initiating Config
with open("CONFIG.json", mode = "r") as f:
    config = json.load(f)

# Define Constants
IP_Adress                   = config.get("IP Address")
Port                        = config.get("Port")
max_timedelta               = config.get("max_timedelta")
loop_count                  = config.get("loop_count")
Frequency_Send              = config.get("Frequency_Send")
Frequency_Update_Config     = config.get("Frequency_Update_Config")
sleep_between_scans         = config.get("sleep_between_scans")
len_value_list              = config.get("len_value_list")
filename_current_data       = config.get("filename_current_data")
api_command                 = config.get("api_command")
id                          = config.get("ID")
Measured_Powers             = config.get("Measured Powers")

print("Variables defined")

# initiate the Scanner
Scanner_ = Scanner(len_value_list, max_timedelta)
print("Scanner set up")
# initiate the Timers
update_timer = datetime.now()
send_timer   = datetime.now()
print("START ENDLESS PROCESS")
# START THE ENDLESS LOOP
while True:

    print("{: <20} {:<30}".format("Step 1", "check if the config needs to be updated"))
    #check if the config needs to be updated
    if float(timedelta.total_seconds(abs(datetime.now() - update_timer))) >= Frequency_Update_Config:
        print("{: <20} {:<30}".format("Step 1.1", "Load Config"))
        # --------------------------------------------------------------------------
        # UPDATE ALL VARIABLES FROM THE CONFIG
        with open("CONFIG.json", mode = "r") as f:
            config = json.load(f)

        # Define Constants
        IP_Adress                   = config.get("IP Address")
        Port                        = config.get("Port")
        max_timedelta               = config.get("max_timedelta")
        loop_count                  = config.get("loop_count")
        Frequency_Send              = config.get("Frequency_Send")
        Frequency_Update_Config     = config.get("Frequency_Update_Config")
        sleep_between_scans         = config.get("sleep_between_scans")
        len_value_list              = config.get("len_value_list")
        filename_current_data       = config.get("filename_current_data")
        api_command                 = config.get("api_command")
        id                          = config.get("ID")
        Measured_Powers             = config.get("Measured Powers")
        # --------------------------------------------------------------------------
        print("{: <20} {:<30}".format("Step 1.2", "create an new Scanner Object"))
        # create an new Scanner Object
        Scanner_ = Scanner(len_value_list, max_timedelta)
        print("{: <20} {:<30}".format("Step 1.3", "update the update_timer"))
        # update the update_timer
        update_timer = datetime.now()
    
    print("{: <20} {:<30}".format("Step 2", "check if the current scan has to be sent"))
    #check if the current scan has to be sent
    if float(timedelta.total_seconds(abs(datetime.now() - send_timer))) >= Frequency_Send:
        print("{: <20} {:<30}".format("Step 2.1", "Load the current Data"))
        #Load the current Data
        with open(filename_current_data, mode = "r") as f:
            data = json.load(f)
        print("{: <20} {:<30}".format("Step 2.2", "define payload"))
        # define payload
        payload = {id : data}

        print(payload)
        # send the Data
        try:
            print("{: <20} {:<30}".format("Step 2.3", "send the Data"))
            requests.post(f"http://{IP_Adress}:{Port}/{api_command}", json= payload)
        except:
            pass
        print("{: <20} {:<30}".format("Step 2.4", "update the send_timer"))
        # update the send_timer
        send_timer = datetime.now()

    print("{: <20} {:<30}".format("Step 3", "start a scan"))
    # scan
    Scanner.scan(sleep_between_scans, loop_count, 10)
    print("{: <20} {:<30}".format("Step 4", "write scanned data to a file"))
    Scanner.get_data(filename_current_data)




    




