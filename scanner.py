from utils import Scanner
import json
import requests
from datetime import datetime, timedelta


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


# initiate the Scanner
Scanner_ = Scanner(len_value_list, max_timedelta)

# initiate the Timers
update_timer = datetime.now()
send_timer   = datetime.now()

# START THE ENDLESS LOOP
while True:


    #check if the config needs to be updated
    if float(timedelta(abs(datetime.now() - update_timer))) >= Frequency_Update_Config:
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
        #create an new Scanner Object
        Scanner_ = Scanner(len_value_list, max_timedelta)
        # update the update_timer
        update_timer = datetime.now()
    
    #check if the current scan has to be sent
    if float(timedelta(abs(datetime.now() - send_timer))) >= Frequency_Send:

        #Load the current Data
        with open(filename_current_data, mode = "r") as f:
            data = json.load(f)

        # define payload
        payload = {id : data}

        print(payload)
        # send the Data
        try:
            requests.post(f"http://{IP_Adress}:{Port}/{api_command}", json= payload)
        except:
            pass

        # update the send_timer
        send_timer = datetime.now()

    print("Started scanning")
    # continouisly scan
    Scanner.scan(sleep_between_scans, loop_count, 10)
    Scanner.get_data(filename_current_data)




    




