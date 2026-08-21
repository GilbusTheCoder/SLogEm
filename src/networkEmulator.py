import ipaddress
import random

from enum import Enum
from pathlib import Path


class DeviceType(Enum):
    UNRECOGNIZED = 0
    HOST_DEVICE = 1
    OTHER_SERVER = 2
    HOME_SERVER = 3
    HOME_ROUTER = 4    


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


class UTCTime:
    yyyy:int = 2026
    mo:int = random.randint(1, 11) ##* No December...
    dd:int = random.randint(1, 31)
    hh:int = random.randint(0, 24)
    mi:int = random.randint(0, 60)
    ss:int = random.randint(0, 60)

    @staticmethod
    def GetTime() -> str:
        return f"{UTCTime.yyyy}:{UTCTime.mo:02d}:{UTCTime.dd:02d}--{UTCTime.hh:02d}:{UTCTime.mi:02d}:{UTCTime.ss:02d}"

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
        if(ss < 60):
            ss += 1
            return
        else: ss = 0

        if(mi < 60):
            mi += 1
            return
        else: mi = 0

        if(hh < 24):
            hh += 1
            return
        else: hh = 0

        if(dd < 31):
            dd += 1
            return  
        else: dd = 1
        mo += 1




class Device:
    def __init__(self, deviceType: DeviceType, deviceIP: ipaddress.IPv4Address) -> None:
        self.type: DeviceType = deviceType
        self.ipv4: ipaddress.IPv4Address = deviceIP


class LogAction:
    ##* If fromDevice and toDevice are the same then it's inferred that this is an internal device log
    def __init__(self, time:UTCTime, type:LogType, status:LogStatus, fromDevice:Device, toDevice:Device):
        pass


class ServerLogger:
    currentTime = UTCTime()

    _logPath:Path = (Path.cwd() / "../logs/").resolve()

    def __init__(self, logStartup:bool = False, logShutdown:bool = False):
        ## Create a log file with a name + time created
        
        ## Define and Run a startup procedure for the home network
        if(logStartup): self._StartupLog()

        ## Log it
        self.SLogEm() ##? Guys I said the thing...
        if(logShutdown): self._ShutdownLog()

        ## Log stuff and increment time so it looks real
        ## Save the log and check
        pass
    
    def SLogEm(self) -> None:
        pass


    #TODO: Writes network loading loags
    def _StartupLog(self) -> None:
        pass

    #TODO: Writes network shutdown logs
    def _ShutdownLog(self) -> None:
        pass


##TODO: Right now it just creates a list of devices with no functionality
class NetworkManager:
    _networkIp = ipaddress.IPv4Address('144.44.8.0/28')
    _possibleHosts = tuple(_networkIp.hosts())

    _isAnomalous:bool = False
    _devices = []
    _logger:ServerLogger = None

    def __init__(self, isAnomolous:bool = False) -> None:
        self._isAnomalous = isAnomolous

        self.__CreateDevices()
        pass

    ##TODO: Add the sussy
    def __CreateDevices(self, numConnectedHosts:int = 2) -> None:
        self._devices.append(Device(DeviceType.HOME_ROUTER, '144.44.8.1'))
        self._devices.append(Device(DeviceType.HOME_SERVER, '144.44.8.2'))

        initializedHosts = 1

        while(initializedHosts <= initializedHosts + numConnectedHosts):
            self._devices.append(DeviceType.HOST_DEVICE, random.choice(self._possibleHosts))
