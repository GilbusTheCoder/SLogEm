##? Swinburne COS30049 (21/08/2026)
##? A program to print log statements we can use for neural network training data
##? Thomas Horsley (103071494)

import ipaddress
from enum import Enum

class DeviceType(Enum):
    UNRECOGNIZED = 0
    HOST_DEVICE = 1
    OTHER_SERVER = 2
    HOME_SERVER = 3
    HOME_ROUTER = 4    

class Device:
    def __init__(self, deviceType: DeviceType, deviceIP: ipaddress.IPv4Address) -> None:
        self.type: DeviceType = deviceType
        self.ipv4: ipaddress.IPv4Address = deviceIP
