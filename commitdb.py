import os
from ctypes import *

CommitEntityDict = {
        "Account"       : 10,
        "Opportunitie"  : 20,
        "Document"      : 30,
        "Charge"        : 40,
        "Event"         : 50,
        "HistoryNote"   : 60,
        "Ticket"        : 70,
        "Item"          : 80,
        "Asset"         : 90,
        "KBArticle"     : 100
}

class CommitRecord:
        def __init__(self, tableID, dataBuff, mapBuff):
                self.tableID            = tableID
                self.dataBuff           = create_string_buffer(bytes(dataBuff, "ascii"))
                self.mapBuff            = create_string_buffer(bytes(mapBuff, "ascii"))

                self.recIDBuffSize      = 21
                self.errCodesBuffSize   = 64
                self.errMsgBuffSize     = 1024

                self.recIDBuff          = create_string_buffer(self.recIDBuffSize)
                self.errCodesBuff       = create_string_buffer(self.errCodesBuffSize)
                self.errMsgBuff         = create_string_buffer(self.errMsgBuffSize)
                
class CommitDB:        
        def __init__(self, appName = 'CommitAgent', CRMPath = r'C:\CommitCRM'):
                self.CRMPath = CRMPath
                self.serverPath = CRMPath + r'\Server'
                self.DBPath = CRMPath + r'\Db'
                self.DBPath_bytes = create_string_buffer(bytes(self.DBPath, 'ascii'))
                self.appName = appName

                os.environ['PATH'] = self.serverPath + ';' + os.environ['PATH']
                self.CmDBEngDll = windll.LoadLibrary(self.serverPath + r'\cmtdbeng.dll')
                self.CmDBQryDll = windll.LoadLibrary(self.serverPath + r'\cmtdbqry.dll')

                self.status = c_int()

        def InitDbEngDll(self):
                self.CmDBEngDll.CmtInitDbEngDll(self.appName, self.DBPath_bytes, byref(self.status))

        def InitDbQryDll(self):
                self.CmDBQryDll.CmtInitDbQryDll(self.appName, self.DBPath_bytes, byref(self.status))
                                                
        def InsUpdRec(self, record):            
                flag = 1
                tbd = 0

                self.CmDBEngDll.CmtInsUpdRec(create_string_buffer(bytes(self.appName, "ascii")),
                                             record.tableID,
                                             record.dataBuff,
                                             record.mapBuff,
                                             flag, tbd,
                                             record.recIDBuffSize,
                                             record.errCodesBuffSize,
                                             record.errMsgBuffSize,
                                             record.recIDBuff,
                                             record.errCodesBuff,
                                             record.errMsgBuff,
                                             byref(self.status))

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
                
if __name__ == '__main__':
        db = CommitDB()
        db.InitDbEngDll()

        print('Init status: ', db.status)
        
        rec = CommitRecord(tableID = CommitEntityDict["Account"],
                           dataBuff = "'Bart De Hantsetters','De Hantsetters','Hantsetters'",
                           mapBuff = "'\n,\nFLDCRDFULLNAME\nFLDCRDDEAR\nFLDCRDCONTACT")

        db.InsUpdRec(rec)

        print('Write status: ', db.status)
        print(rec.tableID, rec.dataBuff.value, rec.mapBuff.value, rec.recIDBuff.raw)
        
        db.TerminateDbEngDll()
        
