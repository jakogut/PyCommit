import os
from ctypes import *

from enum import Enum


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
                                                
        def InsUpdRec(self):
                CmtInsUpdRec(self.appName, table_id, data_buff, map_buff, flag, tbd, rec_id_buff_size,
                             error_codes_buff_size, err_msg_buff_size,rec_id_buff, err_codes_buff,
                             err_msg_buff, status)

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
        
