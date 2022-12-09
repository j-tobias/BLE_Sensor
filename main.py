import requests
from datetime import datetime, timedelta
import json
from scanner import scan
#from test import scan
from time import sleep

#################
##CONFIGURATION##
#################

with open("CONFIG.json", mode = "r") as f:
    config = json.load(f)

#defines the Frequency in which the Rssi Value is uploaded to the Server
frequency = config["Frequency"]
#defines the IP Adress of the Server
IP_Adress = config["IP Adress"]
#defines the Port of the Server
Port = config["Port"]
#defines the Length of the List the Mean is calculated from
len_value_list = config["len_value_list"]
#load the ID of the Sensor
Id = config["ID"]

#is the base url which will always be called to send Data to the Server
base_url = f"http://{IP_Adress}:{Port}/"

previous_time = datetime.now()

#dict with current mac adresses and their current statuses
body = {
    "MAC Adress 1": "current RSSI",
    "MAC Adress 2": "current RSSI",
    "MAC Adress 3": "current RSSI",
    "     ...    ": "current RSSI",
}

####################
##ACTUAL ALGORITHM##
####################

#continously scan for BLE
while True:
    
    current_time = datetime.now()
    
    #execute every given seconds 
    if float(timedelta.total_seconds(abs(current_time - previous_time))) >= frequency:

        requests.post(base_url+ f"{Id}/recieve_scan", body)
        previous_time = current_time

    
    ## SCAN BLE
    ## SORT BY MAC ADRESS
    ## add new values to value list

    scan_ = scan()

    if [] not in scan_:
        #[
        #[{'type': 'None', 'uuid': 'None', 'major': 0, 'minor': 0, 'rssi': 0, 'macAddress': 'None', 'Time': 'None'}]
        #[{'type': 'None', 'uuid': 'None', 'major': 0, 'minor': 0, 'rssi': 0, 'macAddress': 'None', 'Time': 'None'}]
        #[{'type': 'None', 'uuid': 'None', 'major': 0, 'minor': 0, 'rssi': 0, 'macAddress': 'None', 'Time': 'None'}]
        #]
        body_temp = {}

        for sample in scan_:
            #[{'type': 'None', 'uuid': 'None', 'major': 0, 'minor': 0, 'rssi': 0, 'macAddress': 'None', 'Time': 'None'}]
            sample = dict(sample[0])
            #{'type': 'None', 'uuid': 'None', 'major': 0, 'minor': 0, 'rssi': 0, 'macAddress': 'None', 'Time': 'None'}
            mac_address = sample.get("macAddress")

            #get lists or Nones of current MAC Adress
            list_1 = body_temp.get(mac_address)
            list_2 = body.get(mac_address)
            #get current rssi
            rssi = sample.get("rssi")

            if body_temp.get(mac_address) != None:
                
                list_ = list_1.append(rssi)
                body_temp.update({mac_address:list_[1:]})

            #in case the Mac Adress is newly detected by the Sensor
            #and the Mac Adress is in no Body
            elif list_2 == None and list_1 == None:

                #intialize an empty list of required length
                list_ = list([0] * len_value_list)

                #add the rssi value
                list_.append(sample.get("rssi"))

                #update bodies with cropped list
                body_temp.update({mac_address:list_[1:]})

            #in case the Mac Adress is already given in the Body but not in the temp Body
            elif body.get(mac_address) != None and body_temp.get(mac_address) == None:

                #get list from body
                list_ = body.get(mac_address)

                #add rssi value
                list_.append(sample.get("rssi"))

                #update to new body with required length
                body_temp.update({mac_address:list_[1:]})

        body = body_temp
        sleep(0.5)



