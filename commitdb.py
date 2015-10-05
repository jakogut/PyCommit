import os
from ctypes import *

from enum import Enum

class CommitRecord:
        def __init__(tableID, dataBuff, mapBuff, recIDBuff, errMsgBuff = None):
                self.tableID            = create_string_buffer(tableID)
                self.dataBuff           = create_string_buffer(dataBuff)
                self.mapBuff            = create_string_buffer(mapBuff)

                self.errMsgBuff         = create_string_buffer(self.errMsgBuffSize)
                self.errMsgBuffSize     = 1024
                self.recIDBuff          = create_string_buffer(self.recIDBuffSize)
                self.recIDBuffSize      = 64
                self.errCodesBuff       = create_string_buffer(self.errCodesBuffSize)
                self.errCodesBuffSize   = 64
class CommitDB:        
        def __init__(self, appName = 'CommitAgent', CRMPath = r'C:\CommitCRM'):
                self.CRMPath = CRMPath
                self.serverPath = CRMPath + r'\Server'
                self.DBPath = CRMPath + r'\Db'
                self.DBPath_bytes = create_string_buffer(bytes(self.DBPath, 'UTF-8'))
                self.appName = appName

                os.environ['PATH'] = self.serverPath + ';' + os.environ['PATH']
                self.CmDBEngDll = windll.LoadLibrary(self.serverPath + r'\cmtdbeng.dll')
                self.CmDBQryDll = windll.LoadLibrary(self.serverPath + r'\cmtdbqry.dll')

                self.status = c_int()                

        def InitDbEngDll(self):
                self.CmDBEngDll.CmtInitDbEngDll(self.appName, self.DBPath_bytes, byref(self.status))

        def InitDbQryDll(self):
                self.CmDBQryDll.CmtInitDbQryDll(self.appName, self.DBPath, byref(self.status))
                                                
        def InsUpdRec(self, record):
                flag = 1
                tbd = 0
                CmtInsUpdRec(self.appName, record.tableID, record.dataBuff, record.mapBuff, flag, tbd, record.recIDBuffSize,
                             record.errCodesBuffSize, record.errMsgBuffSize, record.recIDBuff, record.errCodesBuff,
                             record.errorMsgBuff, byref(self.status))

        def GetQueryRecIds(self, xml_request_buff, xml_request_buff_len,
                xml_response_data_buff, xml_response_data_buff_len, status):
                pass
        
        def GetRecordDataByRecId(self, xml_request_buff, xml_request_buff_len,
                xml_response_data_buff, xml_response_data_buff_len, status):
                pass
                
        def GetFieldAttributesByRecId(self, xml_request_buff,
                xml_request_buff_len, xml_response_data_buff,
                xml_response_data_buff_len, status):
                pass
                
        def TerminateDbEngDll(self):
                self.CmDBEngDll.CmtTerminateDbEngDll()

        def TerminateDbQryDll(self):
                self.CmDBEngDll.CmtTerminateDbQryDll()
                
        def GetDescriptionByCode(self, code, desc_size, desc):
                pass
                
        def GetDescriptionByStatus(self):
                pass

        CommitAppEntityDict = {
                "Account"       : "10",
                "Opportunitie"  : "20",
                "Document"      : "30",
                "Charge"        : "40",
                "Event"         : "50",
                "HistoryNote"   : "60",
                "Ticket"        : "70",
                "Item"          : "80",
                "Asset"         : "90",
                "KBArticle"     : "100"
        }
                
if __name__ == '__main__':
        db = CommitDB()
        db.InitDbEngDll()
        print(db.status)
        db.TerminateDbEngDll()
        print(db.status)
        
