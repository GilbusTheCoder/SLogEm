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
    startPositions: list[str] = ["a0"]
    tl_sys_transitions:list[list[str]] = [["a1"],["a2"],["a3"],["a4"],
                                ["a5-12", "a14-16", "a20-22", "b0"],            # DEBUG_CHECK_PASS
                                ["a0"], ["a30"], ["a4"], ["a4"],                # FC_SUCCESS
                                ["a4"], ["a4"], ["a4"], ["a13", "a24"],         # SYNC_START
                                ["a4"], ["a4"], ["a4"], ["a17", "a18"],         # PROG_STARTED 
                                ["a4"], ["a17", "a25-29"], ["a4-6"],            # REBOOT_4_CHANGES
                                ["a4"], ["a4"], ["a4"], ["a6"], ["a6"],         # SYNC_FAILED
                                ["a6"], ["a27"], ["a6"], ["a6"], ["a30"],       # DRIVER_FAULT
                                ["a0"]]

    tl_acc_transitions:list[list[str]] = [["b1", "b8", "b11-13"],           # CONNECTION_ATTEMPT
                                              ["a4", "b2-3", "b6", "c1", "c4"], # CONNECTION_ALLOWED
                                              ["a4", "b0"],                     # CONNECTION_DROPPED
                                              ["b4", "b9", "c3-4"],             # REQ_ENCRYPTED_DISK_ACC
                                              ["a4", "b2", "b5-6", "c4"],       # ENCRYPTED_DISK_ACC_ACC
                                              ["a4", "b2","b6"],                # ENCRYPTED_DISK_ACCESS
                                              ["b7", "b10-13"],                 # FT_REQ
                                              ["a4", "b2", "b6"],               # FT_ALLOWED
                                              ["b11", "b13", "c0"],             # CONNECTION_INVALID
                                              ["b11-12", "c0-1", "c3"],         # ENCRYPTED_DISC_ACCESS_FAILED
                                              ["b11-12", "c0", "c3"],           # FT_DENIED
                                              ["b2", "c0-1", "c3"],             # CONNECTION_FAILED
                                              ["b2", "c0-1", "c3"],             # REQUEST_TIMEOUT
                                              ["b2"]]                          # BAD_HANDSHAKE


    tl_sec_transitions:list[list[str]] = [["a4"],                           # BAD_PERMISSIONS
                                              ["a4"],                           # ACCESS_VIOLATION
                                              ["a4"],                           # AV_FLAGGED
                                              ["a4"],                           # ACCESS_LOCKOUT
                                              ["a4"]]                          # ROOT_ACCESS_GRANTED

    xtraAccInfoTransitions:list[list[str]] = []
    xtraSysInfoTransitions:list[list[str]] = []
    xtraSecInfoTransitions:list[list[str]] = []

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
    FT_ALLOWED                  = "file transfer allowed... complete"
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
    def SLogIt(self, maxLogs:int):# Just a state machine
        logSequence:list[tuple[LogType, int]] = self._DetSLogSequence(maxLogs)
        log:str = ""

        for logTuple in logSequence:
            lType, lID = logTuple
            log = self._TranslateToLog(lType.name, lID)
            print(log, file=self._logFile)
            UTCTime.Increment()

    #TODO: FIX SEQUENCING IT DONT WORK
    #TODO: Add context and some rules to make it look more natural
    #TODO: Add anomolous ruleset
    #TODO: Test and if it sucks go find some logs
    #? Should return a sequence of tuples(type, log id) which allows messages to be printed
    def _DetSLogSequence(self, maxSLogs:int) -> list[tuple[LogType, int]]:
        start:str = random.choice(LogTree.startPositions)
        sequence:list[tuple[LogType, int]] = [[self._PullLogType(start), int(start[1:])]] 
        logCount:int = 0

        while logCount < maxSLogs:
            nextLog:str = self._GetNextLog(sequence[logCount])
            sequence.append((self._PullLogType(nextLog), int(nextLog[1:])))
            logCount +=1
        return sequence


    def _TranslateToLog(self, logType:LogType, logID:int) -> str:
        baseMsg:str = self._GetLogBase(logType, logID)
        return f"{UTCTime.GetTime()} {logType} {LogStatus.WARN.name} | {baseMsg}"


    def _GetLogBase(self, logType:LogType, logID:int) -> str:
        match logType:
            case LogType.ACCESS.name: return list(AccMsg)[logID].value
            case LogType.SYSTEM.name: return list(SysMsg)[logID].value
            case LogType.SECURITY.name: return list(SecMsg)[logID].value


    def _GetNextLog(self, currentLog:tuple[LogType, int]) -> str:
        valid_transitions:list[str] = []
        top_level_transitions:list[str] = []

        match currentLog[0]:
            case LogType.ACCESS: top_level_transitions = LogTree.tl_acc_transitions[currentLog[1]] 
            case LogType.SYSTEM: top_level_transitions = LogTree.tl_sys_transitions[currentLog[1]]            
            case LogType.SECURITY: top_level_transitions = LogTree.tl_sec_transitions[currentLog[1]]

        for transition_node in top_level_transitions:
            valid_transitions.extend(self._ExtractRange(transition_node))

        return random.choice(valid_transitions)


    def _ExtractRange(self, range:str) -> list[str]:
        if len(range) <= 3: return [range]    #if there's only 1 option

        valid_transitions:list[str] = []
        top_level_transition:chr = range[0]

        code_range_min:int = -1
        code_range_max:int = -1
        code_range_val_as_str:str = ""

        for character in range[1:]:
            if character.isdigit(): code_range_val_as_str += character
            else:
                code_range_min = int(code_range_val_as_str)
                code_range_val_as_str = ""

        if (len(code_range_val_as_str) > 0): code_range_max = int(code_range_val_as_str)

        current_code_val:int = code_range_min
        while (current_code_val <= code_range_max):
            valid_transitions.append(f"{top_level_transition}{current_code_val}")
            current_code_val +=1

        return valid_transitions

    def _PullLogType(self, idStr:str) -> LogType:
        match idStr[0]:
            case 'a': return LogType.SYSTEM
            case 'b': return LogType.ACCESS
            case 'c': return LogType.SECURITY

    #? If given a range of hyphenated values, this function will randomly chose within the alotted range
    def _PullIntIDRange(self, idStr:str) -> tuple[int, int]:
        idNumRange:str = idStr[1:]

        if(len(idNumRange) == 1): return int(idNumRange)

        idRange:list[int] = []
        idRangeElements:list[chr] = []

        for element in idNumRange:
            if element.isdigit(): idRangeElements.append(str(element))
            else:
                value:int = int("".join(str(x) for x in idRangeElements))
                idRange.append(value)
                idRangeElements.clear()

        if len(idRange) == 1: return idRange[0]
        return random.randint(idRange[0], idRange[1])

    def _MatchTypeAndID(self, logChrIDElement:chr, logNumIDElement:int) -> tuple[LogType, int]:
        match logChrIDElement:
            case 'a': return (LogType.ACCESS, logNumIDElement)
            case 'b': return (LogType.SYSTEM, logNumIDElement)
            case 'c': return (LogType.SECURITY, logNumIDElement)
            case _: return ()

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
        self._netLog.SLogIt(maxSLogs)
        
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