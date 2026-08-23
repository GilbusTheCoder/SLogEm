import ipaddress
import random

from enum import Enum
from pathlib import Path


class UTCTime:
    yyyy:int = 2026
    mo:int = random.randint(1, 11) ##* No December...
    dd:int = random.randint(1, 31)
    hh:int = random.randint(0, 24)
    mi:int = random.randint(0, 60)
    ss:int = random.randint(0, 60)

    @staticmethod
    def GetTime(isFileNameAppropriate:bool = False) -> str:
        if(not isFileNameAppropriate):
            return f"{UTCTime.yyyy}:{UTCTime.mo:02d}:{UTCTime.dd:02d}--{UTCTime.hh:02d}:{UTCTime.mi:02d}:{UTCTime.ss:02d}"

        return f"{UTCTime.yyyy}{UTCTime.mo:02d}{UTCTime.dd:02d}--{UTCTime.hh:02d}-{UTCTime.mi:02d}-{UTCTime.ss:02d}"

    @classmethod
    def ResetTime(cls) -> None:
        cls.yyyy:int = 2026
        cls.mo:int = random.randint(1, 11) ##* No December...
        cls.dd:int = random.randint(1, 31)
        cls.hh:int = random.randint(0, 24)
        cls.mi:int = random.randint(0, 60)
        cls.ss:int = random.randint(0, 60)
                
    ##* I'm sure there's a nicer solution but idc
    @classmethod
    def Increment(cls) -> None:
        if(cls.ss < 59):
            cls.ss += 1
            return
        else: cls.ss = 0

        if(cls.mi < 59):
            cls.mi += 1
            return
        else: cls.mi = 0

        if(cls.hh < 23):
            cls.hh += 1
            return
        else: cls.hh = 0

        if(cls.dd < 30):
            cls.dd += 1
            return  
        else: cls.dd = 1
        cls.mo += 1




class DeviceType(Enum):
    UNRECOGNIZED = 0
    HOST_DEVICE = 1
    OTHER_SERVER = 2
    HOME_SERVER = 3
    HOME_ROUTER = 4    

class DevicePrivilege(Enum):
    UNRECOGNIZED = 0
    GUEST = 1
    USER = 2
    ROOT = 3

class Device:
    def __init__(self, deviceType: DeviceType, deviceID:int, deviceIP: ipaddress.IPv4Address, devicePrivilege: DevicePrivilege = 0) -> None:
        self.type:DeviceType = deviceType
        self.did: int = deviceID
        self.name:str = f"{DeviceType(deviceType).name} {self.did}"
        self.ipv4:ipaddress.IPv4Address = deviceIP
        self.privilege:DevicePrivilege = devicePrivilege 



class LogType(Enum):
    ACCESS = 0
    ERROR = 1
    SECURITY = 2
    SYSTEM = 3


class LogStatus(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4

class LogAction:
    actionType:LogType = LogType(0)
    actionStatus:LogStatus = LogStatus(0)
    fromDevice:Device = None
    toDevice:Device = None

    @classmethod
    def GetLog(cls) -> str:
        if(cls.fromDevice == None or cls.toDevice == None): pass
        return f"[{UTCTime.GetTime()}] {cls.actionType.name} {cls.actionStatus.name} | {cls.toDevice.name} - {cls.fromDevice.name}"

    @classmethod
    def SetLog(cls, typeID:int, statusID:int, fDevice:Device, tDevice:Device):
        cls.actionType = LogType(typeID)
        cls.actionStatus = LogStatus(statusID)
        cls.fromDevice = fDevice
        cls.toDevice = tDevice

    @classmethod
    def __Elaborate() -> str:
        pass

##? As there is only one instance of the LogAction, The ActionManipulator is designed to provide
##? the context for the LogAction for each Action.
class LogActionManager:
    actionInstance = LogAction()
    maxActions:int = 20
    logTypeRange:tuple = (0, 3)
    logStatusRange:tuple = (0, 3)
    networkDevices = []

    @classmethod
    def Init(cls, devices, isAnomolous):
        cls.networkDevices = devices
        cls.__LogRandom()

    @classmethod
    def __LogRandom(cls):
        currentActions:int = 0
        while currentActions < cls.maxActions:
            cls.actionInstance.SetLog(random.choice(cls.logTypeRange), random.choice(cls.logStatusRange), random.choice(cls.networkDevices), random.choice(cls.networkDevices))
            print(LogAction().GetLog())
            currentActions +=1
            UTCTime.Increment()

    
    @classmethod
    def __AccessAction(cls):
        pass

    @classmethod
    def __ErrorAction(cls):
        pass

    @classmethod
    def __SecurityAction(cls):
        pass

    @classmethod
    def __SystemAction(cls):
        pass

class ServerLogger:
    _logPath:Path = (Path.cwd() / "logs/").resolve()

    def Init(self, networkDevices, isAnomolous:bool):
        ## Create a log file with a name + time created
        self._logFileName:str = f"{UTCTime.GetTime(True)}.txt"
        self._logID = self._logPath / self._logFileName
        self._logFile = open(self._logID, "w")

        self._actionManager = LogActionManager()
        self._actionManager.Init(networkDevices, isAnomolous)
        ## Log stuff and increment time so it looks real

        ## Save the log and check
        pass
    
    def SLogEm(self) -> None:
        pass


##TODO: Right now it just creates a list of devices with no functionality
class NetworkManager:
    _networkIp = ipaddress.ip_network('144.44.8.0/24')
    _possibleHosts = tuple(_networkIp.hosts())

    _loggedDevices = [] #First device is home router, followed by the home server, then local hosts and others come last
    _logger = ServerLogger()

    def __init__(self, isAnomolous:bool = False) -> None:
        self.__CreateDevices()
        self._logger.Init(self._loggedDevices, isAnomolous)


    def DisplayDevices(self):
        for device in self._loggedDevices:
            print(f"[{UTCTime.GetTime()}] {LogType(0).name} {LogStatus(0).name} | {device.name} - {device.ipv4}")

    ##TODO: Add the sussy
    def __CreateDevices(self, numLocalHosts:int = 3) -> None:
        self._loggedDevices.append(Device(DeviceType.HOME_ROUTER, 0, '144.44.8.1', 3))
        self._loggedDevices.append(Device(DeviceType.HOME_SERVER, 1, '144.44.8.2', 3))

        initializedHosts = 0
        while(initializedHosts < numLocalHosts):
            self._loggedDevices.append(self.__CreateDevice((initializedHosts+2), random.choice(self._possibleHosts)))
            initializedHosts +=1

    def __CreateDevice(self, did: int, dip:ipaddress.IPv4Address):
        return Device(DeviceType.HOST_DEVICE, did, dip, 1)