import os
from ctypes import *

os.environ['PATH'] = 'C:\CommitCRM\Server' + ';' + os.environ['PATH']

CmDBDLL = windll.LoadLibrary("c:\commitcrm\server\cmtdbeng.dll")

class CommitDB:
	def __init__(self, appName = 'CommitAgent', CRMPath = r'C:/CommitCRM/Db'):
		self.CRMPath = CRMPath
		self.appName = appName

		self.status = c_int()
		print(self.status)
	
		os.environ['PATH'] = CRMPath + ';' + os.environ['PATH']
		
	def InitDbQryDll(self):
		print(CmDBDLL.CmtInitDbEngDll)
		CmDBDLL.CmtInitDbEngDll(self.appName, self.CRMPath, byref(self.status)) 
		
	def GetQueryRecIds(self, xml_request_buff, xml_request_buff_len,
		xml_response_data_buff, xml_response_data_buff_len, status):
		pass
	
	def GetRecordDataByRecId(self, xml_request_buff, xml_request_buff_len,
		xml_response_data_buff, xml_response_data_buff_len, status):
		pass
		
	def CmtGetFieldAttributesByRecId(self, xml_request_buff,
		xml_request_buff_len, xml_response_data_buff,
		xml_response_data_buff_len, status):
		pass
		
	def CmtTerminateDbQryDll(self):
		pass
		
	def CmtGetDescriptionByCode(self, code, desc_size, desc):
		pass
		
	def CmtGetDescriptionByStatus(self):
		pass
		
if __name__ == '__main__':
	db = CommitDB()
	print(db.InitDbQryDll())
	print(db.status)
	
