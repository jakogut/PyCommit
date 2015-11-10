import os
from ctypes import *

from xml.etree.cElementTree import ElementTree, Element, SubElement, Comment, tostring, fromstring
from xml.dom import minidom

import untangle

from pycommit.entities import *
from pyparsing import *

class QueryError(Exception):
    pass

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
    
    def __init__(self, query = None, name = "CommitAgent", maxRecordCnt = 255):

        self.query = self._parse_query(query)
        
        self.extAppName = name
        self.maxRecordCnt = maxRecordCnt

        self._create_dom_tree()

    def _parse_query(self, query):
        operator = oneOf("= > >= < <= ~ ! !~")
        joiner = oneOf('AND OR')
        
        _from = Suppress(Literal('FROM')) + Word(printables)
        _from = _from.setResultsName('FROM')
        
        _select = Suppress(Literal('SELECT')) + Word(printables)
        _select = _select.setResultsName('SELECT')
        
        _val = QuotedString('"')
        _val = _val.setResultsName('VAL')
        
        _conditional = Word(printables) + operator + _val
        _conditional = _conditional.setResultsName('COND')
        
        lparen, rparen = Literal('('), Literal(')')
        _where = Suppress(Literal('WHERE')) + ZeroOrMore(lparen) + OneOrMore(Group(_conditional) + ZeroOrMore(joiner)) + ZeroOrMore(rparen)
        _where = _where.setResultsName('WHERE')

        _query = _from + _select + _where
    
        self.parsed_query = _query.parseString(query, parseAll=True)

    def _create_dom_tree(self):
        self.tree = Element('CommitCRMQueryDataRequest')
        self.nameElement = SubElement(self.tree, 'ExternalApplicationName')
        self.nameElement.text = self.extAppName
        self.dataKindElement = SubElement(self.tree, 'Datakind')
        self.dataKindElement.text = self.parsed_query.FROM[0]
        self.recordCountElement = SubElement(self.tree, 'MaxRecordCount')
        self.recordCountElement.text = str(self.maxRecordCnt)

        self.queryElement = SubElement(self.tree, 'Query')
        self.whereElement = SubElement(self.queryElement, 'Where')
        self.queryContentElements = []

        operator_map = {'~' : 'LIKE', '!' : 'NOT', '!~' : 'NOT LIKE'}

        for exp in self.parsed_query.WHERE:
            if isinstance(exp, str):
                if exp in ['AND', 'OR']:
                    tag = 'Link'
                    newElement = SubElement(
                        self.whereElement,
                        tag
                    )
                    
                    newElement.text = exp
                    self.queryContentElements.append(newElement)        
            elif isinstance(exp, ParseResults):
                if exp[1] in operator_map:
                    op_str = operator_map[exp[1]]
                else:
                    op_str = exp[1]
                    
                newElement = SubElement(
                    self.whereElement,
                    exp[0],
                    {"op" : op_str}
                )

                newElement.text = exp[2]
                self.queryContentElements.append(newElement)
        
        self.orderElement = SubElement(self.queryElement, 'Order')

    def get_dom_tree_str(self):
        return self.declaration + tostring(self.tree)

    def print_dom_tree(self):
        print(self._prettify(self.get_dom_tree_str()))

    def _prettify(self, dom_str):
        reparsed = minidom.parseString(dom_str)
        return reparsed.toprettyxml(indent="    ")

class DataResponse:
    def __init__(self, response):
        self.response_str = response
        self.doc = untangle.parse(self.response_str)

    def get_recids(self):
        try:
                RecordData = self.doc.CommitCRMQueryDataResponse.RecordData
        except IndexError:
                return
            
        self.recIds = []
        for data in RecordData:
            self.recIds.append(data.get_elements()[0].cdata)

        return self.recIds

class FieldAttributesRequest:
    declaration = bytes('<?commitcrmxmlgetrecorddatarequest version="1.0" ?>', "ascii")
    def __init__(self, query = None, name = "CommitAgent", maxRecordCnt = 255):

        self.query = self._query_to_dict(query)
        
        self.extAppName = name
        self.maxRecordCnt = maxRecordCnt

        self._create_dom_tree()

    def _query_to_dict(self, query):
        from pyparsing import Word, alphas, alphanums, oneOf
        from pyparsing import delimitedList, Suppress
        
        operator = oneOf("= > >= < <= like not not like")
        
        _from = Suppress('FROM') + Word(alphanums)
        _select = Suppress('SELECT') + Suppress('(') + delimitedList(Word(alphas)) + Suppress(')')

        d = {}
        d['FROM'] = _from.searchString(query)[0][0]
        d['SELECT'] = _select.searchString(query)[0]

        return d

    def _create_dom_tree(self):
        self.tree = Element('CommitCRMGetRecordDataRequest')
        self.nameElement = SubElement(self.tree, 'ExternalApplicationName')
        self.nameElement.text = self.extAppName
        self.recidElement = SubElement(self.tree, 'GetRecordByRecId')
        self.recidElement.text = self.query['FROM']
        self.selectFieldsElement = SubElement(self.tree, 'SelectFieldsList')
        self.selectFieldsElement.text = ', '.join(self.query['SELECT'])

    def get_dom_tree_str(self):
        return self.declaration + tostring(self.tree)

    def print_dom_tree(self):
        print(self._prettify(self.get_dom_tree_str()))

    def _prettify(self, dom_str):
        reparsed = minidom.parseString(dom_str)
        return reparsed.toprettyxml(indent="    ")

class FieldAttributesResponse:
    def __init__(self, response):
        self.response_str = response
        self.doc = untangle.parse(self.response_str)

    def get_dictionary(self):
        try:
                RecordData = self.doc.CommitCRMGetRecordDataResponse.RecordData
        except IndexError:
                return
            
        elements = RecordData.get_elements()

        _dict = {}
        for e in elements:
            if e._name not in _dict:
                _dict[e._name] = [e.cdata]
            else:
                _dict[e.name].append(e.cdata)

        return _dict
                
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

                if self.status.value != 1: raise QueryError(
                        "DB not initialized for writing. Error code {}".format(self.status))

        def _init_db_qry_dll(self):
                self.CmDBQryDll.CmtInitDbQryDll(self.appName, self.DBPath_bytes, byref(self.status))

                if self.status.value != 1: raise QueryError(
                        "DB not initialized for queries. Error code {}".format(self.status))
                
        def update_rec(self, record):            
                flag = 1
                tbd = 0

                self.CmDBEngDll.CmtInsUpdRec(
                    create_string_buffer(bytes(self.appName, "ascii")),
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
                     byref(self.status)
                )

                if self.status.value != 1: raise QueryError(
                        "DB insertion failed with code {}.".format(self.status))

        def query_recids(self, req):
                req_str = req.get_dom_tree_str()
                
                respBuffSize = 16384
                respBuff = create_string_buffer(respBuffSize)
                
                self.CmDBQryDll.CmtGetQueryRecIds(
                    create_string_buffer(req_str),
                    len(req_str),
                    respBuff,
                    respBuffSize,
                    byref(self.status))

                if self.status.value != 1: raise QueryError(
                    "DB query failed with code {}.".format(self.status))

                resp = DataResponse(str(respBuff.value, encoding = "ascii"))
                return resp.get_recids()
        
        def get_rec_data_by_recid(self, req):
                req_str = req.get_dom_tree_str()

                respBuffSize = 16384
                respBuff = create_string_buffer(respBuffSize)

                self.CmDBQryDll.CmtGetRecordDataByRecId(
                    create_string_buffer(req_str),
                    len(req_str),
                    respBuff,
                    respBuffSize,
                    byref(self.status)
                )

                if self.status.value != 1: raise QueryError(
                    "DB query failed with code {}.".format(self.status))

                resp = FieldAttributesResponse(str(respBuff.value, encoding = "ascii"))
                return resp.get_dictionary()

        def get_field_attribs_by_recid(self, req):
                req_str = req.get_dom_tree_str()

                respBufferSize = 16384
                respBuffer = create_string_buffer(respBufferSize)

                self.CmDBQryDll.CmtGetRecordDataByRecId(
                    create_string_buffer(req_str),
                    len(req_str),
                    respBuff,
                    respBuffSize,
                    byref(self.status))
                
        def _terminate_db_eng_dll(self):
                self.CmDBEngDll.CmtTerminateDbEngDll()

        def _terminate_db_qry_dll(self):
                self.CmDBQryDll.CmtTerminateDbQryDll()
                
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
