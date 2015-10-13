from CommitEntities import *

from xml.etree.cElementTree import ElementTree, Element, SubElement, Comment, tostring, fromstring
from xml.dom import minidom

import untangle

class SimpleSQLQuery:
    def __init__(self, q_from, q_select, q_where, q_op, q_value):
        _query = [(q_from, q_select, q_where, q_op, q_value)]

    def add_statement(self, q_link_op, q_from, q_select, q_where, q_op, q_value):
        _query.append((q_link_op, q_from, q_select, q_where, q_op, q_value))

    def get_query():
        return _query

    def is_multi_statement():
        if len(_query) > 1: return True
        else: return False

class CommitQueryDataRequest:
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

class CommitGetRecordDataRequest:
    def __init__(recId, fieldsList):
        pass

class CommitQueryDataResponse:
    def __init__(self, response):
        self.response_str = response
        self.doc = untangle.parse(self.response_str)

    def getRecIds(self):
        self.recIds = []
        for data in self.doc.CommitCRMQueryDataResponse.RecordData:
            self.recIds.append(data.get_elements()[0].cdata)

        return self.recIds
    
