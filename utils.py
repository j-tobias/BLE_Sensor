#This is a working prototype. DO NOT USE IT IN LIVE PROJECTS
import sys
import struct
import bluetooth._bluetooth as bluez
from datetime import datetime, timedelta
import time
import json
import numpy as np




OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_ENABLE=0x000C

def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)

def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

def packetToString(packet):
    """
    Returns the string representation of a raw HCI packet.
    """
    if sys.version_info > (3, 0):
        return ''.join('%02x' % struct.unpack("B", bytes([x]))[0] for x in packet)
    else:
        return ''.join('%02x' % struct.unpack("B", x)[0] for x in packet)

def parse_events(sock, loop_count=100):
    # old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    results = []
    for i in range(0, loop_count):
        packet = sock.recv(255)
        scan_time = datetime.now().time()
        # ptype, event, plen = struct.unpack("BBB", packet[:3])
        packetOffset = 0
        dataString = packetToString(packet)
        """
        If the bluetooth device is an beacon then show the beacon.
        """
        #print (dataString)
        if (dataString[34:42] == '0303aafe') and (dataString[44:50] == '16AAFE'):
            """
            Selects parts of the bluetooth packets.
            """
            broadcastType = dataString[50:52]
            if broadcastType == '00' :
                type = "Eddystone UID"
                namespace = dataString[54:74].upper()
                instance = dataString[74:86].upper()
                resultsArray = [
                {"type": type, "namespace": namespace, "instance": instance}]
                return resultsArray

            elif broadcastType == '10':
                type = "Eddystone URL"
                urlprefix = dataString[54:56]
                if urlprefix == '00':
                    prefix = 'http://www.'
                elif urlprefix == '01':
                    prefix = 'https://www.'
                elif urlprefix == '02':
                    prefix = 'http://'
                elif urlprefix == '03':
                    prefix = 'https://'
                hexUrl = dataString[56:][:-2]
                if sys.version_info[0] == 3:
                    url = prefix + bytes.fromhex(hexUrl).decode('utf-8')
                    rssi, = struct.unpack("b", bytes([packet[packetOffset-1]]))
                # else:
                #    url = prefix + hexUrl.decode("hex")
                #    rssi, = struct.unpack("b", packet[packetOffset-1])
                resultsArray = [{"type": type, "url": url}]
                return resultsArray

            elif broadcastType == '20':
                type = "Eddystone TLM"
                resultsArray = [{"type": type}]
                return resultsArray

            elif broadcastType == '30':
                type = "Eddystone EID"
                resultsArray = [{"type": type}]
                return resultsArray

            elif broadcastType == '40':
                type = "Eddystone RESERVED"
                resultsArray = [{"type": type}]
                return resultsArray

        if dataString[38:46] == '4c000215':
            """
            Selects parts of the bluetooth packets.
            """
            type = "iBeacon"
            uuid = dataString[46:54] + "-" + dataString[54:58] + "-" + dataString[58:62] + "-" + dataString[62:66] + "-" + dataString[66:78]
            major = dataString[78:82]
            minor = dataString[82:86]
            majorVal = int("".join(major.split()[::-1]), 16)
            minorVal = int("".join(minor.split()[::-1]), 16)
            """
            Organises Mac Address to display properly
            """
            scrambledAddress = dataString[14:26]
            fixStructure = iter("".join(reversed([scrambledAddress[i:i+2] for i in range(0, len(scrambledAddress), 2)])))
            macAddress = ':'.join(a+b for a,b in zip(fixStructure, fixStructure))
            if sys.version_info[0] == 3:
                rssi, = struct.unpack("b", bytes([packet[packetOffset-1]]))
            # else:
            #    rssi, = struct.unpack("b", packet[packetOffset-1])

            resultsArray = {"type": type, "uuid": uuid, "major": majorVal, "minor": minorVal, "rssi": rssi, "macAddress": macAddress, "Time": scan_time}

            return resultsArray

    return results

#definitions
enable = 0x01
num_scans = 1000

#bluetooth socket
sock = bluez.hci_open_dev(0)

#hci_enable_le_scan
cmd_pkt = struct.pack("<BB", enable, 0x00)
bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)


def scan ():
    return parse_events(sock, 20)




def get_distance (rssi: int,measured_power: int,n: int):
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



class Scanner:

    def __init__ (self, N_samples: int, max_timedelta: float = 5.0):
        """
        N_samples defines the Number of scans in the Queue
        """

        # define the Bluetooth Socket
        self.sock = bluez.hci_open_dev(0)

        # make N_samples globaly
        self.N_samples = N_samples

        # create a List with all Collectors
        self.Collectors = {}

        # useage indicator
        self.usage = {}

        # maximum unused time before mac_address get deleted
        self.timedelta = max_timedelta

    def _parse_events (self, loop_count: int = 100):
        """
        Scans the Bluetooth Socket

        returns for iBeacon

        {"type", "uuid", "major", "minor", "rssi", "macAddress", "Time"}
        """
        return parse_events(self.sock, loop_count)

    
    def scan (self, sleep: float = 0, loop_count: int = 100, n_times: int = 5):
        """
        Scans n_times
        """
        counter = 0
        while counter <= n_times:
            # get a scan
            scan_ = self._parse_events(loop_count)
            # if the scan is not empty
            if scan_ != None:
                # get the ID or "MAC ADDRESS" of the scanned iBeacon
                mac_address = scan_.get("macAddress")
                # get the appropriate Collector for the found MAC ADDRESS
                Collector_ = self.Collectors.get(mac_address)
                # check if a Collector was found
                if Collector_ != None:
                    # add scan to the Collector
                    Collector_.add_scan(scan_.get("rssi"))
                    # update usage indicator
                    self.usage[mac_address] = datetime.now()

                else:
                    # create new Collector
                    Collector_ = Collector(mac_address, self.N_samples)
                    # add scan to the Collector
                    Collector_.add_scan(scan_.get("rssi"))
                    # update the Collectors dict
                    self.Collectors.update({mac_address: Collector_})
                    # initiate a usage indicator for this new mac adress
                    self.usage.update({mac_address: datetime.now()})

            #sleep for a given time
            time.sleep(sleep)

            counter += 1
    
    def get_data (self, filename: str = "data.json"):
        """
        returns the full amount of Data
        """
        # create an empty Data Holder
        data = {}
        # go through all the Collector Objects
        for mac_adress in self.Collectors.keys():
            #check usage
            last_used = self.usage.get(mac_adress)
            #check the difference between the usages
            if float(timedelta.total_seconds(abs(datetime.now() - last_used))) <= self.timedelta:
                # update the data holder
                data.update({mac_adress: np.mean(self.Collectors.get(mac_adress).scans)})
            # otherwise delete the Collector
            else:
                self.Collectors.pop(mac_adress)

        with open(filename, mode= "w") as f:
            json.dump(data, f)

        


class Collector:

    def __init__ (self, id: str, N_samples: int):
        """
        The Collector collects all samples for a given id

        The id will ususally be the MAC ADDRESS but it could also be anything else
        """
        # the Unique Identifier
        self.id = id

        # make N_samples globaly
        self.N_samples = N_samples

        # last N scans
        self.scans = []

    def add_scan (self, scan):
        """
        Adds a Scan to the List
        """
        if len(self.scans) < self.N_samples:
            self.scans.append(scan)
        else:
            self.scans.append(scan)
            self.scans = self.scans[1:]