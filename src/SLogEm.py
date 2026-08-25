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
    ACCESS  = 0
    SECURITY= 1
    SYSTEM  = 2

class LogStatus(Enum):
    DEBUG   = 0
    INFO    = 1
    WARN    = 2
    ERROR   = 3
    FATAL   = 4

class LogTree:
    topLevelTransitions:list[list[str]] = [["a1"],["a2"],["a3"],["a4"],
                                ["a5-12", "a14-16", "a20-22"],            #DEBUG_CHECK_PASS
                                ["a0"], ["a30"], ["a4"], ["a4"],          #FC_SUCCESS
                                ["a4"], ["a4"], ["a4"], ["a13", "a24"],   #SYNC_START
                                ["a4"], ["a4"], ["a4"], ["a17", "a18"],   #PROG_STARTED 
                                ["a4"], ["a17", "a25-29"], ["a4-6"],      #REBOOT_4_CHANGES
                                ["a4"], ["a4"], ["a4"], ["a6"], ["a6"],   #SYNC_FAILED
                                ["a6"], ["a27"], ["a6"], ["a6"], ["a30"], #DRIVER_FAULT
                                ["a0"]]

class SysMsg(Enum):                                                 #a
    #Debug / Info
    BOOTING                     = "system booting"                  #0
    LOADING_DATA                = "loading data"                    
    PORT_STATUS_TO_UP           = "all access ports up"             
    PROC_FINISHED               = "process finished"                #3
    DEBUG_CHECK_PASS            = "system normal"                   
    REBOOTING                   = "system rebooting"                
    SHUTDOWN                    = "system shutdown"                 #6
    FT_SUCCESS                  = "file transfer successful"
    FC_SUCCESS                  = "file copy successful"
    FD_SUCCESS                  = "file deleted"                    #9
    FR_SUCCESS                  = "file renamed"
    FM_SUCCESS                  = "file modification synced"
    SYNC_STARTED                = "net sync started"                #12
    SYNC_SUCCESS                = "net sync successful"
    PROG_INSTALLED              = "install complete"
    PROG_REMOVED                = "uninstall complete"              #15
    PROG_STARTED                = "program started"
    PROG_ENDED                  = "program terminated"
    #Warnings
    PROG_STALLED                = "program stalled... waiting..."   #18
    REBOOT_4_CHANGES            = "changes require systems restart" 
    REG_CREATED                 = "new local registry entry"
    REG_MOD                     = "local registry entry modified"   #21
    REG_DEL                     = "local registry entry deleted"
    #Errors & Fatalities
    INVALID_PATH                = "path invalid"
    SYNC_FAILED                 = "net sync failed"                 #24
    DATA_INVALID                = "data is invalid or corrupted" 
    RESOURCE_LEAK               = "resource leak"          
    OUT_OF_MEM                  = "out of memory"                   #27
    MEM_ACCESS_VIOLATION        = "memory access violation"
    DRIVER_FAULT                = "system driver fault"             
    END_LOG                     = "goodbye..."                      #30

class AccMsg(Enum):                                                                     #b
    #Debug / Info
    CONNECTION_ATTEMPT          = "remote connection attempted verifying connection..." #0
    CONNECTION_VALID            = "connection allowed"
    CONNECTION_DROPPED          = "remote user disconnected"
    REQ_ENCRYPTED_DISK_ACC      = "encrypted disk access requested verifying user..."   #3
    ENCRYPTED_DISK_ACC_ACC      = "disk access accepted"
    ENCRYPTED_DISK_ACCESS       = "encrypted storage accessed"
    FT_REQ                      = "file transfer request"                               #6
    FT_ALLOWED                  = "file transfer allowed...\ncomplete"
    #Warnings
    CONNECTION_INVALID          = "connection denied invalid credentials"
    ENCRYPTED_DISK_ACCESS_FAILED= "disk access denied"                                  #9
    FT_DENIED                   = "file transfer denied"
    #Errors & Fatalities
    CONNECTION_FAILED           = "connection failed"
    REQUEST_TIMEOUT             = "connection timeout for data request"                 #12
    BAD_HANDSHAKE               = "bad handshake"
    
class SecMsg(Enum):                                                 #c
    BAD_PERMISSIONS             = "permission invalid"              #0
    ACCESS_VIOLATION            = "access violation"
    AV_FLAGGED                  = "flagged by AV"
    ACCESS_LOCKOUT              = "access restricted"               #3
    ROOT_ACCESS_GRANTED         = "root access granted"
    
class Paths(Enum):                              #x
    ROOT        = "C://"                        #0                      
    DOCUMENTS   = "C://Server/Documents/"
    DESKTOP     = "C://Server/Desktop/"
    VIDEOS      = "C://Server/Media/Videos/"    #3
    MUSIC       = "C://Server/Media/Music/"
    PROGRAMS    = "C://Programs/"
    
    SECURE_DRIVE= "F://"                        #6
    PASSWORDS   = "F://Admin/Pwd/"
    FINANCES    = "F://Admin/Finances/"         #8

class Programs(Enum):                           #y
    CMD     = "cmd.exe"                         #0
    SHELL   = "windows_powershell.exe"  
    WORD    = "word.exe"                
    SOLITARE= "solitare.exe"                    #3
    NOTEPAD = "notepad.exe"
    CHROME  = "chrome.exe"
    TASKMAN = "taskmanager.exe"                 #6
    REGEDIT = "regedit.exe"
    DISCORD = "discord.exe"
    EXCEL   = "excel.exe"                       #9

    M_WORD  = "w0rd.exe"
    
class Files(Enum):                              #z
    CAT_PICTURE = "cute cat.jpg"                #0
    DOG_PICTURE = "cute dog.png"
    PASSWORDS   = "pwd.txt"
    FINANCES_25 = "2025_Financials.xlsx"        #3
    FINANCES_26 = "2026_Financials.xlsx"
    ASSIGNMENT1 = "COS30049_Assignment1.docx"
    SLOGEM      = "SLogEm.py"                   #6
    WD_S1_E1    = "The Walking Dead S1 E1"      
    G_BRAAAAAAP = "Gilli - Braaaaaap.mp3"
    G_PISSED    = "Gilli - Pissed.wav"          #9     




#? Take context from the LogAction, transcribing it to logs and saving when done
#TODO: Create a

class NetLogger:
    def __init__(self):
        self._logPath:Path = (Path.cwd() / "logs/").resolve()
        self._logFile = open(self._GenLogID(), "w")
    
        self._lType:LogType
        self._lStatus:LogStatus
        self._fDevice:Device
        self._tDevice:Device
        self._DoReqResponse:bool = False

    def SetSLog(self,logStatus:LogStatus, fromDevice:Device, toDevice:Device = None, 
                logType:LogType = LogType.SYSTEM, reqResponse:bool = False):
        self._lStatus = logStatus
        self._fDevice = fromDevice

        if toDevice == None: 
            self._lType = LogType.SYSTEM
            self._tDevice = self._fDevice
            self._DoReqResponse = False

        else: 
            self._lType = logType
            self._tDevice = toDevice
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

    def _SLogAccess(self) -> str: 
        message:str = f"{self._fDevice.ipv4} to {self._tDevice.name} {self._tDevice.ipv4}"
        additionalInfo:str = ""

        match self._lStatus:
            case LogStatus.WARN:    additionalInfo = AccMsg.FT_DENIED.value
            case LogStatus.ERROR:   additionalInfo = AccMsg.CONNECTION_FAILED.value
            case LogStatus.FATAL:   additionalInfo = AccMsg.ENCRYPTED_DISK_ACCESS_FAILED.value
            case _:                 additionalInfo = AccMsg.CONNECTION_VALID.value
        return f"[{UTCTime.GetTime()}] {LogType.ACCESS.name} {self._lStatus.name} | {message} {additionalInfo}"

    def _SLogSecurity(self) -> str: 
        message:str = f"{self._fDevice.ipv4} to {self._tDevice.name} {self._tDevice.ipv4}"
        additionalInfo:str = ""
    
        match self._lStatus:
            case LogStatus.WARN:  additionalInfo = SecMsg.ROOT_ACCESS_GRANTED.value
            case LogStatus.ERROR: additionalInfo = SecMsg.BAD_PERMISSIONS.value
            case LogStatus.FATAL: additionalInfo = SecMsg.ACCESS_LOCKOUT.value
            case _:               additionalInfo = SecMsg.BAD_PERMISSIONS.value
        return f"[{UTCTime.GetTime()}] {LogType.SECURITY.name} {self._lStatus.name} | {message} {additionalInfo}"

    def _SLogSystem(self) ->str:
        message:str = f"{self._fDevice.name} {self._fDevice.ipv4}"
        additionalInfo:str = ""
        match self._lStatus:
            case LogStatus.DEBUG: additionalInfo = f"{SysMsg.LOADING_DATA.value}"
            case LogStatus.INFO:  additionalInfo = f"{SysMsg.FT_SUCCESS.value}"
            case LogStatus.WARN:  additionalInfo = f"{SysMsg.MEM_ACCESS_VIOLATION.value}"
            case LogStatus.ERROR: additionalInfo = f"{SysMsg.OUT_OF_MEM.value}"
            case LogStatus.FATAL: additionalInfo = f"{SysMsg.DRIVER_FAULT.value}"

        return f"[{UTCTime.GetTime()}] {LogType.SYSTEM.name} {self._lStatus.name} | {message} {additionalInfo}"

    def _GenLogID(self)-> Path:
        logFileName:str = f"{UTCTime.GetTime(True)}.txt"
        return(self._logPath / logFileName)


##* Device and Network Emulation
class DeviceType(Enum):
    UNRECOGNIZED = 0
    HOST_DEVICE = 1
    OTHER_SERVER = 2
    HOME_SERVER = 3

class DevicePrivilege(Enum):
    UNRECOGNIZED = 0
    GUEST = 1
    USER = 2
    ROOT = 3

class Device:
    def __init__(self, deviceType: DeviceType, deviceID:int, deviceIP: ipaddress.IPv4Address,
                 devicePrivilege: DevicePrivilege = 0) -> None:
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

    def SLogEm(self, maxSLogs:int = 100):
        currentSLog:int = 0

        while currentSLog < maxSLogs:
            NetLogger.SetSLog(self._netLog, random.choice(list(LogStatus)), random.choice(self._devices), 
                              random.choice(self._devices), random.choice(list(LogType)))
            NetLogger.SLogIt(self._netLog)
            currentSLog +=1

    #if anomolous, add some other devices to the list for the netmanager to do stuff with
    def _InitDevices(self, numDevices:int = 4) -> list[Device]:
        possibleAddresses = tuple(self._netIP.hosts())
        deviceID:int = 0
        deviceType = DeviceType.UNRECOGNIZED
        devices:list[Device] = []

        for address in possibleAddresses:
            if deviceID >= numDevices: break
            match deviceID:
                case 0: deviceType = DeviceType.HOME_SERVER
                case _: deviceType = DeviceType.HOST_DEVICE

            devices.append(Device(deviceType, deviceID, address))
            deviceID +=1

        return devices