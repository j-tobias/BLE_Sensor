from typing import Union
from classes import Scanner

from fastapi import FastAPI

app = FastAPI()

# initiate Sensor Objects and save them
global Sensor_dict
Sensor_dict = {
    "0001": Scanner()
    }

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    print('Hello World')
    return {"item_id": item_id, "q": q}

@app.get("/{sensor_id}/status")
def status(sensor_id: int):
    #---------------------
    #Get the STATUS of the SENSOR
    #---------------------
    Scanner_ = Sensor_dict.get(str(sensor_id))
    status = {
        "40:C7:11:7A:86:60" :{
            "rssi": 70,
            "uuid": 1234567898765432,
            "timestamp": 123456789
        }
    }
    return {"sensor_id": sensor_id, "Status": status}

#get List of Mac-Adresses
@app.get("/{sensor_id}/mac-adress-list")
def mac_adress_list (sensor_id: int):
    #---------------------
    #Get the MAC ADRESS LIST of the SENSOR
    #---------------------
    Scanner_ = Sensor_dict.get(str(sensor_id))
    mac_adresses = Scanner_.get_mac_adresses()
    return {'MAC Adresses': mac_adresses}

#get List of Mac-Adresses with a rssi value below x or above x
@app.get("/{sensor_id}/mac-adress-list/min-{min}-max-{max}")
def mac_adress_list (sensor_id: int, min: int = None, max: int = None):
    #---------------------
    #Get the MAC ADRESS LIST of the SENSOR
    #Iterate through List and delete unwanted values
    #---------------------
    Scanner_ = Sensor_dict.get(str(sensor_id))
    scan = Scanner_._scan()
    mac_adresses = []
    for value in scan:
        if min == None and max != None:
            if value.get("rssi") < max:
                mac_adresses.append(value.get("macAddress"))

        
        elif min != None and max == None:
            if value.get("rssi") > min:
                mac_adresses.append(value.get("macAddress"))

        elif min == None and max == None:
            mac_adresses = "ERROR NOT MIN AND NO MAX GIVEN"

        else:
            if value.get("rssi") > min and value.get("rssi") < max:
                mac_adresses.append(value.get("macAddress"))

    return {'MAC Adresses': mac_adresses}

#collect data for p seconds and return values
@app.get("/{sensor_id}/scan/{period}")
def scan (sensor_id: int, period: int):
    #---------------------
    #Get a scan of the Sensor over a given period
    #later Scanner.scan is used
    #---------------------
    Scanner_ = Sensor_dict.get(str(sensor_id))
    scan_ = Scanner_._scan(period)
    return scan_

@app.get("/{sensor_id}/rssi/mac_adress-{mac_adress}-period-{period}-mean-{mean}")
def rssi (sensor_id: int, mac_adress: str, period: int, mean: bool = True):
    #---------------------
    #Get a scan of the Sensor over a given period
    #later Scanner.scan is used
    #---------------------
    Scanner_ = Sensor_dict.get(str(sensor_id))
    rssi_ = Scanner_.get_rssi(mac_adress, period, mean)
    return {"rssi": rssi_}


# WWWAYYY Later !!!
# Plan is to plug in multiple sensors into 1 RaspberryPi
# But then all different sensors have to be available over the API by the 1 RaspberryPi
# Therefore every Sensor gets an ID and then will be called by the API over this ID

if __name__ == "__main__":
    import uvicorn
    import socket

    uvicorn.run(app, host=str(socket.gethostbyname(socket.gethostname())), port=5000)


    

