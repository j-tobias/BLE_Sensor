import sys
import struct
import bluetooth._bluetooth as bluez
import utils as ScanUtility
import time

#definitions
OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_ENABLE=0x000C
enable = 0x01
num_scans = 1000

#bluetooth socket
sock = bluez.hci_open_dev(0)

#hci_enable_le_scan
cmd_pkt = struct.pack("<BB", enable, 0x00)
bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)


def scan ():
    return ScanUtility.parse_events(sock, 20)