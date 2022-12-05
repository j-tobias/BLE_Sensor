#This File will contain the class which will be used by the RaspberryPi
from datetime import time
import time as TIME
from scanner import scan as search

"""
def search () -> dict:
    scan = {
        'type': 'iBeacon', 
        'uuid': '366a03db-7f03-40b2-b90a-b70e429f05d6', 
        'major': 10, 
        'minor': 0, 
        'rssi': -42, 
        'macAddress': '46:04:16:0e:06:1d', 
        'Time': 'datetime.time(20, 24, 47, 992459)'
        }
    return scan

"""

class Scanner:

    def __init__ (self):

        self.current_mac_adresses = []
        pass

    def get_mac_adresses (self, period:int = 1):
        """
        Returns a List of all MAC Adresses currently detected by the BLE Sensor
        """
        #scan for a given period
        scans = self._scan(period)
        #initiate the MAC Adress list
        mac_adresses = []
        #Iterate through the Scans
        for scan in scans:
            #Select the MAC Adress from the scan and append it to the list
            mac_adresses.append(scan.get('macAddress'))
        #Filter out doubles
        mac_adresses = list(set(mac_adresses))
        #Update global MAC Adress List
        self.current_mac_adresses = mac_adresses
        #Return dict
        return {"MAC Adresses": mac_adresses}

    def get_rssi (self, mac_adress: str, period: int, mean: bool = True):
        """
        Returns the RSSI value of a given MAC Adress computed with the given method (MEAN or MEDIAN)
        """
        #scan for a given period
        scans = self._scan(period)
        #initiate rssi List
        rssi_list = []
        #iterate through scans
        for scan in scans:
            #select scans with the given MAC Adress
            if scan.get('macAddress') == mac_adress:
                #Select the RSSI from the scan and append it to the list
                rssi_list.append(scan.get('rssi'))

        if mean:
            return sum(rssi_list)/len(rssi_list)
        else:
            #Case 1 it's even
            if len(rssi_list) % 2 == 0:
                index_1 = int(len(rssi_list)/2)
                index_2 = index_1 + 1

                median = (rssi_list[index_1] + rssi_list[index_2])/2
                return median
            #Case 2 it's uneven
            else:

                median = rssi_list[int(len(rssi_list)/2)+1]
                return median
            
    def get_distance (self,rssi: int,measured_power: int,n: int):
        """
        Returns the Distance [m] for a given MAC Adress
        Distance = 10 ^ ((Measured Power -RSSI)/(10 * N))

        1. Distance
        2. Measured Power
        3. RSSI
        4. N (Constant depends on the Environmental factor. Range 2–4, low to-high strength as explained above)
        """        
        distance = 10 ** ((measured_power - rssi)/(10 * n))

        return distance

    #HELPER METHODS
    def _scan (self, period: int = 5) -> list:

        scan_list = []

        end = TIME.time() + period
        while time.time() < end:
            scan_list.append(search())

        return scan_list


