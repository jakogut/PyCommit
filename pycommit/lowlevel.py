"""API Reference: http://www.commitcrm.com/wiki/API_Reference_Manual#API_Functions"""

import os
import _ctypes, ctypes

from lxml.etree import ElementTree, Element, SubElement, Comment, tostring, fromstring
from xml.dom import minidom

import Pyro4
import multiprocessing
import untangle
import logging

from pyparsing import *

class RecIDRequest:
    declaration = b'<?commitcrmxmlqueryrequest version="1.0" ?>'
    
    def __init__(self, query = None, maxRecordCnt = 255, name = "CommitAgent"):
        """Object containing data for record ID requests
        Args:
            query (str): SQL-like query, formatted like so:
                "FROM [table] SELECT * WHERE [column] = [value]"
            name (optional[str]): String that identifies the app/user making the request
            maxRecordCnt (int): Maximum number of results to return
        Returns: None
        """
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
        
        _val = QuotedString('"', escQuote="'", escChar='\\')
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
                    
                    newElement.text = ' ' + exp + ' '
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

    def get_dom_tree_str(self, pretty=True):
        """Return generated XML request
        Args:
            pretty (bool): Format XMl before returning, defaults to True
        """
        dom_str = self.declaration + tostring(self.tree)

        if pretty:
            reparsed = minidom.parseString(dom_str)
            dom_str = reparsed.toprettyxml(indent='    ')

        return dom_str.encode('UTF-8')

class RecIDResponse:
    def __init__(self, response):
        """Parses and formats the XMl response returned by Commit
        Args:
            response (bytes): bytes object containing XML response
        """
        self.response_str = response
        self.doc = untangle.parse(self.response_str)

    def get_recids(self):
        """Returns list of record IDs from parsed XML response"""
        try:
                RecordData = self.doc.CommitCRMQueryDataResponse.RecordData
        except IndexError:
                return
        except AttributeError:
            return
            
        self.recIds = []
        for data in RecordData:
            self.recIds.append(data.get_elements()[0].cdata)

        return self.recIds

class RecordDataRequest:
    declaration = b'<?commitcrmxmlgetrecorddatarequest version="1.0" ?>'

    def __init__(self, query = None, maxRecordCnt = 255, name = "CommitAgent"):
        """Object containing request for record data
        Args:
            query (str): SQL-like query, formatted like so:
                "FROM [table] SELECT * WHERE [column] = [value]"
            name (optional[str]): String that identifies the app/user making the request
            maxRecordCnt (int): Maximum number of results to return
        Returns: None
        """
        self.query = self._query_to_dict(query)
        
        self.extAppName = name
        self.maxRecordCnt = maxRecordCnt

        self._create_dom_tree()

    def _query_to_dict(self, query):
        from pyparsing import Word, alphas, alphanums, oneOf
        from pyparsing import delimitedList, Suppress
        
        operator = oneOf("= > >= < <= like not not like")
        
        _from = Suppress('FROM') + Word(alphanums)
        _select = Suppress('SELECT') + Suppress('(') + delimitedList(Word(alphanums)) + Suppress(')')

        d = {}

        try:
            d['FROM'] = _from.searchString(query)[0][0]
            d['SELECT'] = _select.searchString(query)[0]
        except IndexError:
            return

        return d

    def _create_dom_tree(self):
        if self.query is None: return
        
        self.tree = Element('CommitCRMGetRecordDataRequest')
        self.nameElement = SubElement(self.tree, 'ExternalApplicationName')
        self.nameElement.text = self.extAppName
        self.recidElement = SubElement(self.tree, 'GetRecordByRecId')
        self.recidElement.text = self.query['FROM']
        self.selectFieldsElement = SubElement(self.tree, 'SelectFieldsList')
        self.selectFieldsElement.text = ', '.join(self.query['SELECT'])

    def get_dom_tree_str(self, pretty=True):
        if self.query is None: return None
        dom_str = self.declaration + tostring(self.tree)

        if pretty:
            reparsed = minidom.parseString(dom_str)
            dom_str = reparsed.toprettyxml(indent='    ')

        return dom_str.encode('UTF-8')

class RecordDataResponse:
    def __init__(self, response):
        """Parses and formats XML response"""
        self.response_str = response
        self.doc = untangle.parse(self.response_str)

    def get_dictionary(self):
        """Returns dictionary from parsed XML response"""
        try:
                RecordData = self.doc.CommitCRMGetRecordDataResponse.RecordData
        except IndexError:
                return
            
        elements = RecordData.get_elements()

        _dict = {}
        for e in elements:
            if 'CmtRawData' not in e._attributes:
                _dict[e._name] = e.cdata
            else:
                _dict[e._name] = e['CmtRawData']

        return _dict
                
class DBWorker(multiprocessing.Process):
        def __init__(self, appName = 'PyCommit', CRMPath = r'C:\CommitCRM'):
            """Initialize the low level interface to Commit's API
            Args:
                appName (str): The string used to identify the user
                    responsible for changes inside Commit
                
                CRMPath: (str): Path to CommitCRM installation, defaults
                    to default installation path on volume C:

            Returns: None
            """
            super().__init__()

            self.daemon = True
            
            self.CRMPath = CRMPath
            self.serverPath = CRMPath + r'\Server'
            self.DBPath = CRMPath + r'\Db'
            self.appName = appName
            self.logger = logging.getLogger()

            os.environ['PATH'] = self.serverPath + ';' + os.environ['PATH']
            
        def run(self):
            self.CmDBEngDll = ctypes.windll.LoadLibrary(self.serverPath + r'\cmtdbeng.dll')
            self.CmDBQryDll = ctypes.windll.LoadLibrary(self.serverPath + r'\cmtdbqry.dll')

            self.status = ctypes.c_int()

            self.DBPath_bytes = ctypes.create_string_buffer(self.DBPath.encode('UTF-8'))
            self._init_db_eng_dll()
            self._init_db_qry_dll()
            
            Pyro4.Daemon.serveSimple(
                {self: 'lowlevel.DBInterface'},
                port=8001, ns=False, verbose=False)

        def __del__(self):
            """Unload the Commit API DLL, and free up the memory"""
            self._terminate_db_eng_dll()
            self._terminate_db_qry_dll()
            
        def _init_db_eng_dll(self):
            self.CmDBEngDll.CmtInitDbEngDll(self.appName, self.DBPath_bytes, ctypes.byref(self.status))

            if self.status.value != 1: raise Exception(
                    "DB not initialized for writing. Error code {}".format(self.status))

        def _init_db_qry_dll(self):
            self.CmDBQryDll.CmtInitDbQryDll(self.appName, self.DBPath_bytes, ctypes.byref(self.status))

            if self.status.value != 1: raise Exception(
                    "DB not initialized for queries. Error code {}".format(self.status))

        def _terminate_db_eng_dll(self):
            if hasattr(self, 'CmDBEngDll'):
                self.CmDBEngDll.CmtTerminateDbEngDll()

        def _terminate_db_qry_dll(self):
            if hasattr(self, 'CmDBQryDll'):
                self.CmDBQryDll.CmtTerminateDbQryDll()

        def update_rec(self, tableID, data, map):
            """Update a record in the CommitCRM database

            Args:
                tableID (int): ID of table to update
                data (str): Values to insert into fields, delimited by commas
                map (str): Field map for data arg, delimited by newlines
            Returns:
                None
            Raises:
                QueryError: If status != 1
            """
            errCodesBuffSize   = 64
            errMsgBuffSize     = 1024
            recIDBuffSize      = 20
            errCodesBuff       = ctypes.create_string_buffer(errCodesBuffSize)
            errMsgBuff         = ctypes.create_string_buffer(errMsgBuffSize)
            recIDBuff          = ctypes.create_string_buffer(recIDBuffSize)
            flag, tbd = 1, 0

            self.CmDBEngDll.CmtInsUpdRec(
                 ctypes.create_string_buffer(self.appName.encode('UTF-8')),
                 tableID,
                 ctypes.create_string_buffer(data.encode('UTF-8')),
                 ctypes.create_string_buffer(map.encode('UTF-8')),
                 flag, tbd,
                 recIDBuffSize,
                 errCodesBuffSize,
                 errMsgBuffSize,
                 recIDBuff,
                 errCodesBuff,
                 errMsgBuff,
                 ctypes.byref(self.status)
            )

            if self.status.value != 1: raise Exception(
                "DB insertion failed with code {}: {}\n\n{}".format(
                    self.status,
                    self.get_desc_by_code(self.status),
                                'data: ' + data + '\n' + \
                                'map: ' + map
                )
            )

            return recIDBuff.raw.decode('UTF-8')

        def query_recids(self, query, maxRecordCnt=255):
            """Request a list of record IDs matching the specified criteria

            Args:
                req (RecIDRequest): Object containing criteria for selection
            Returns: list of record ids
            Raises: QueryError if status != 1
            """
            req = RecIDRequest(query, maxRecordCnt)
            req_str = req.get_dom_tree_str()
            
            respBuffSize = req.maxRecordCnt * 32
            respBuff = ctypes.create_string_buffer(respBuffSize)
            
            self.CmDBQryDll.CmtGetQueryRecIds(
                ctypes.create_string_buffer(req_str),
                len(req_str),
                respBuff,
                respBuffSize,
                ctypes.byref(self.status))

            if self.status.value != 1: raise Exception(
                "Record ID query failed with code {}: {}\n\nRequest:\n{}\n\n".format(
                    self.status,
                    self.get_desc_by_code(self.status),
                    req.get_dom_tree_str().decode('UTF-8')
                )
            )

            resp = RecIDResponse(respBuff.value.decode('UTF-8'))
            respBuff = None
            
            return resp.get_recids()

        def get_rec_data_by_recid(self, query, maxRecordCnt=255):
            """Get record data from a record specified by record ID
            Args:
                req (RecordDataRequest): Object containing query for record data
            Returns:
                dictionary containing requested fields from record
            Raises:
                QueryError: If status != 1
            """
            req = RecordDataRequest(query, maxRecordCnt)
            req_str = req.get_dom_tree_str()
            if req_str is None: return

            respBuffSize = 16384
            respBuff = ctypes.create_string_buffer(respBuffSize)

            self.CmDBQryDll.CmtGetRecordDataByRecId(
                ctypes.create_string_buffer(req_str),
                len(req_str),
                respBuff,
                respBuffSize,
                ctypes.byref(self.status)
            )

            if self.status.value != 1: raise Exception(
                "Record data query failed with code {}: {}\n\nRequest:\n{}".format(
                    self.status,
                    self.get_desc_by_code(self.status),
                    req.get_dom_tree_str().decode('UTF-8')
                )
            )

            resp = RecordDataResponse(respBuff.value.decode('UTF-8'))
            respBuff = None

            return resp.get_dictionary()

        def get_desc_by_code(self, code):
            """Get English status text from Commit
            Args:
                code (int): status code
            Returns:
                bytes: bytre string containing status text
            """
            size = 1024
            buffer = ctypes.create_string_buffer(size)

            self.CmDBQryDll.CmtGetDescriptionByStatus(
                code,
                size,
                buffer
            )

            return bytes(buffer.value).strip()
                
        def get_status(self):
            return self.status.value
