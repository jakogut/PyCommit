import os
from ctypes import *

from xml.etree.cElementTree import ElementTree, Element, SubElement, Comment, tostring, fromstring
from xml.dom import minidom

import untangle

from pycommit.entities import *

class DBRecord:
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

class DataRequest:
    declaration = bytes('<?commitcrmxmlqueryrequest version="1.0" ?>', "ascii")
    
    def __init__(
            self, q_from, q_select, q_where, q_op, q_value,
            name = "CommitAgent", maxRecordCnt = 255):

        self.q_from = q_from
        self.q_select = q_select
        self.q_where = q_where
        self.q_op = q_op
        self.q_value = q_value
        
        self.extAppName = name
        self.maxRecordCnt = maxRecordCnt

        self.__createDomTree()
        
    def __createDomTree(self):
        self.tree = Element('CommitCRMQueryDataRequest')
        self.nameElement = SubElement(self.tree, 'ExternalApplicationName')
        self.nameElement.text = self.extAppName
        self.dataKindElement = SubElement(self.tree, 'Datakind')
        self.dataKindElement.text = self.q_from
        self.recordCountElement = SubElement(self.tree, 'MaxRecordCount')
        self.recordCountElement.text = str(self.maxRecordCnt)

        self.queryElement = SubElement(self.tree, 'Query')
        self.whereElement = SubElement(self.queryElement, 'Where')
        
        self.queryContentElement = SubElement(self.whereElement, self.q_where, {"op" : self.q_op})
        self.queryContentElement.text = self.q_value

        self.orderElement = SubElement(self.queryElement, 'Order')

    def getDomTreeStr(self):
        return self.declaration + tostring(self.tree)

    def printDomTree(self):
        print(self.__prettify(self.getDomTreeStr()))

    def __prettify(self, dom_str):
        reparsed = minidom.parseString(dom_str)
        return reparsed.toprettyxml(indent="    ")

class DataResponse:
    def __init__(self, response):
        self.response_str = response
        self.doc = untangle.parse(self.response_str)

    def getRecIds(self):
        try:
                RecordData = self.doc.CommitCRMQueryDataResponse.RecordData
        except IndexError:
                return
            
        self.recIds = []
        for data in RecordData:
            self.recIds.append(data.get_elements()[0].cdata)

        return self.recIds
                
class DBInterface:        
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

                self._init_db_eng_dll()
                self._init_db_qry_dll()

        def __del__(self):
                self._terminate_db_eng_dll()
                self._terminate_db_qry_dll()

        def _init_db_eng_dll(self):
                self.CmDBEngDll.CmtInitDbEngDll(self.appName, self.DBPath_bytes, byref(self.status))

                if self.status.value != 1: raise RuntimeError(
                        "DB not initialized for writing. Error code {}".format(self.status))

        def _init_db_qry_dll(self):
                self.CmDBQryDll.CmtInitDbQryDll(self.appName, self.DBPath_bytes, byref(self.status))

                if self.status.value != 1: raise RuntimeError(
                        "DB not initialized for queries. Error code {}".format(self.status))
                
        def update_rec(self, record):            
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

                if self.status.value != 1: raise RuntimeError(
                        "DB insertion failed with code {}.".format(self.status))

        def query_recids(self, req):
                req_str = req.getDomTreeStr()
                
                respBuffSize = 16384
                respBuff = create_string_buffer(respBuffSize)
                
                self.CmDBQryDll.CmtGetQueryRecIds(
                                                create_string_buffer(req_str),
                                                len(req_str),
                                                respBuff,
                                                respBuffSize,
                                                byref(self.status))

                if self.status.value != 1: raise RuntimeError(
                        "DB query failed with code {}.".format(self.status))

                resp = DataResponse(str(respBuff.value, encoding = "ascii"))
                return resp.getRecIds()
        
        def get_rec_data_by_recid(self, req):
                req_str = req.getDomTreeStr()

                respBufferSize = 16384
                respBuffer = create_string_buffer(respBufferSize)

                self.CmDBQryDll.CmtGetRecordDataByRecId(create_string_buffer(req_str),
                                                        len(req_str),
                                                        respBuff,
                                                        respBuffSize,
                                                        byref(self.status))

        def get_field_attribs_by_recid(self, req):
                req_str = req.getDomTreeStr()

                respBufferSize = 16384
                respBuffer = create_string_buffer(respBufferSize)

                self.CmDBQryDll.CmtGetRecordDataByRecId(create_string_buffer(req_str),
                                                        len(req_str),
                                                        respBuff,
                                                        respBuffSize,
                                                        byref(self.status))
                
        def _terminate_db_eng_dll(self):
                self.CmDBEngDll.CmtTerminateDbEngDll()

        def _terminate_db_qry_dll(self):
                self.CmDBEngDll.CmtTerminateDbQryDll()
                
        def get_desc_by_code(self, code, desc_size, desc):
                pass
                
        def get_desc_by_status(self):
                pass

        def get_status(self):
                return self.status.value
                
if __name__ == '__main__':
        from tests import CommitTests
        tests = CommitTests()
        tests.run_all()
