import os
from ctypes import *

from CommitEntities import *

class CommitRecord:
        def __init__(self, tableID, dataBuff, mapBuff, recID = ""):
                self.tableID            = tableID
                self.dataBuff           = create_string_buffer(bytes(dataBuff, "ascii"))
                self.mapBuff            = create_string_buffer(bytes(mapBuff, "ascii"))

                self.recIDBuffSize      = 20
                self.errCodesBuffSize   = 64
                self.errMsgBuffSize     = 1024

                self.recIDBuff          = create_string_buffer(bytes(recID, "ascii"), self.recIDBuffSize)
                self.errCodesBuff       = create_string_buffer(self.errCodesBuffSize)
                self.errMsgBuff         = create_string_buffer(self.errMsgBuffSize)

        def getRecID(self):
                return str(self.recIDBuff.raw, encoding='ascii')
                
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

        def GetQueryRecIds(self, reqBuff):
                respBuffSize = 65535
                respBuff = create_string_buffer(respBuffSize)
                
                CmDBQryDll.CmtGetQueryRecIds(create_string_buffer(bytes(xml_request_buff, "ascii"),
                                             len(reqBuff)),
                                             respBuff,
                                             respBuffSize,
                                             byref(self.status))

                return str(respBuff.raw, encoding = "ascii")
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
        # db.status should be 1 if library initialized properly
        db = CommitDB()
        db.InitDbEngDll()

        # Add an account to the database
        dataStr = "'Bart De Hantsetters','Hantsetters'"
        mapStr = "'\n,\n" + CommitAccountFields["FileAs"] + "\n" + CommitAccountFields["Contact"]
        
        rec = CommitRecord(tableID = CommitEntity["Account"],
                           dataBuff = dataStr,
                           mapBuff = mapStr)

        # db.status should be 1 if operation was successful
        db.InsUpdRec(rec)
        print("Insert status: ", db.status)
        print("RecID: ", rec.getRecID())

        # Update the existing record
        dataStr = "'De Hantsetters','" + rec.getRecID() + "'"
        mapStr = "'\n,\n" + CommitAccountFields["LastName"] + '\n' + CommitAccountFields["AccountRecID"]

        rec = CommitRecord(tableID = CommitEntity["Account"],
                           dataBuff = dataStr,
                           mapBuff = mapStr)
        
        db.InsUpdRec(rec)
        print("Update status: ", db.status)
        
        db.TerminateDbEngDll()
        
