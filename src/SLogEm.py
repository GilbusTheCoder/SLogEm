import ipaddress
import random

from enum import Enum
from dataclasses import dataclass
from pathlib import Path

##* EmulatedUTCTime
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
        cls.mo:int = random.randint(1, 11) # No December, no need to wrap
        cls.dd:int = random.randint(1, 31)
        cls.hh:int = random.randint(0, 24)
        cls.mi:int = random.randint(0, 60)
        cls.ss:int = random.randint(0, 60)
                
    # Sure there's a nicer solution but idc
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



##* Logging Stuff
class LogType(Enum):
    ACCESS = 0
    SECURITY = 1
    SYSTEM = 2

class LogStatus(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4

class WrnMsg(Enum):
    ATTEMPTED_ACCESS = "attempted access to"
    REMOTE_ACCESS_DETECTED = "attempted remote access"


class ErrMsg(Enum):
    TIMEOUT = "connection timeout for datarequest"
    INVALID_CREDENTIALS = "invalid credentials for filepath"
    DATA_INVALID = "data is invalid or corrupted at"
    ACCESS_VIOLATION = "access violation"
    CONNECTION_FAILED = "connection has failed"
    


#? Take context from the LogAction, transcribing it to logs and saving when done
class NetLogger:
    def __init__(self):
        self._logPath:Path = (Path.cwd() / "logs/").resolve()
        self._logFile = open(self._GenLogID(), "w")
    
        self._lType:LogType
        self._lStatus:LogStatus
        self._fDevice:Device
        self._tDevice:Device
        self._DoReqResponse:bool = False

    def SetSLog(self, logType:LogType, logStatus:LogStatus, fromDevice:Device, 
                toDevice:Device = None, reqResponse:bool = False):
        self._lType = logType
        self._lStatus = logStatus
        self._fDevice = fromDevice
        if toDevice == None: self._tDevice = self._fDevice
        else: self._tDevice = toDevice
        self._DoReqResponse = reqResponse

    #? Derives the appropriate context of the log line based on the log type and status
    def SLogIt(self):# Just a state machine
        log:str = ""
        match self._lType:
            case LogType.ACCESS: log = self._SLogAccess()
            case LogType.SECURITY: log = self._SLogSecurity()
            case LogType.SYSTEM: log = self._SLogSystem()

        print(log, file=self._logFile)
        UTCTime.Increment()

    #Access requires a handshake therefore responses are created in logs aswell
    def _SLogAccess(self) -> str: 
        message:str = f"{self._fDevice.ipv4} to {self._tDevice.name} {self._tDevice.ipv4}"
        additionalInfo:str = ""

        # Shouldn't be a thing, turn debugs into info
        match self._lStatus:
            case LogStatus.WARN:
                additionalInfo = f"{WrnMsg.ATTEMPTED_ACCESS.value} {self._tDevice.ipv4}"
            case LogStatus.ERROR: 
                additionalInfo = ErrMsg.CONNECTION_FAILED.value
            case LogStatus.FATAL: 
                self._lStatus = LogStatus.ERROR
                additionalInfo = ErrMsg.CONNECTION_FAILED.value
            case _: pass
        return f"[{UTCTime.GetTime()}] {LogType.ACCESS.name} {self._lStatus.name} | {message} {additionalInfo}"

        
    def _SLogSecurity(self) -> str: 
        message:str = f"{self._fDevice.ipv4} to {self._tDevice.name} {self._tDevice.ipv4}"
        additionalInfo:str = ""
    
        # Only error and fatal status's are required
        match self._lStatus:
            case LogStatus.ERROR: 
                additionalInfo = f"{ErrMsg.INVALID_CREDENTIALS.name} {self._logPath}"
            case LogStatus.FATAL: 
                additionalInfo = f"{ErrMsg.ACCESS_VIOLATION.name} {self._logPath}"
            case _: pass
        return f"[{UTCTime.GetTime()}] {LogType.SECURITY.name} {self._lStatus.name} | {message} {additionalInfo}"
        
        
    def _SLogSystem(self): pass

    def _GenLogID(self)-> Path:
        logFileName:str = f"{UTCTime.GetTime(True)}.txt"
        return(self._logPath / logFileName)



##* Device and Network Emulation
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

#? Manipulates the LogAction for network emulation, tells the logger to do its thing
class NetworkManager:
    def __init__(self):
        self._netIP = ipaddress.ip_network('144.44.8.0/24')
        self._devices: list[Device] = self._InitDevices()
        self._netLog = NetLogger()

    def SLogEm(self, maxSLogs:int = 10):
        currentSLog:int = 0

        while currentSLog < maxSLogs:
            NetLogger.SetSLog(self._netLog, LogType.ACCESS, random.choice(list(LogStatus)),
                              random.choice(self._devices), random.choice(self._devices), False)
            NetLogger.SLogIt(self._netLog)
            currentSLog +=1

    #if anomolous, add some other devices to the list for the netmanager to do stuff with
    def _InitDevices(self, numDevices:int = 5) -> list[Device]:
        possibleAddresses = tuple(self._netIP.hosts())
        deviceID:int = 0
        deviceType = DeviceType.UNRECOGNIZED

        devices:list[Device] = []
        for address in possibleAddresses:
            if deviceID >= numDevices: break
            match deviceID:
                case 0: deviceType = DeviceType.HOME_ROUTER
                case 1: deviceType = DeviceType.HOME_SERVER
                case _: deviceType = DeviceType.HOST_DEVICE

            devices.append(Device(deviceType, deviceID, address))
            deviceID +=1

        return devices