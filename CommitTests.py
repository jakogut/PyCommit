from CommitDB import CommitDB, CommitRecord
from CommitEntities import *
from CommitQuery import *

class CommitTests:
    def __init__(self):
        self.db = CommitDB()
        self.db.InitDbEngDll()
        self.db.InitDbQryDll()

        self.rec = None

    def __del__(self):
        self.db.TerminateDbEngDll()
        self.db.TerminateDbQryDll()
    
    def createRec(self):
        # Add an account to the database
        dataStr = "'Bart De Hantsetters','Hantsetters'"
        mapStr = "'\n,\n" + CommitAccountFields["FileAs"] + "\n" + CommitAccountFields["Contact"]
        
        self.rec = CommitRecord(tableID = CommitEntity["Account"],
                           dataBuff = dataStr,
                           mapBuff = mapStr)
        
        # db.status should be 1 if operation was successful
        self.db.InsUpdRec(self.rec)
        print("Insert status: ", self.db.status)
        print("RecID: ", self.rec.getRecID())

    def updRec(self):
        # Update the existing record
        if self.rec == None:
            print("Record for updating does not exist.")
            return
        
        dataStr = "'De Hantsetters','" + self.rec.getRecID() + "'"
        mapStr = "'\n,\n" + CommitAccountFields["LastName"]
        mapStr += '\n'    + CommitAccountFields["AccountRecID"]

        self.rec = CommitRecord(tableID = CommitEntity["Account"],
                           dataBuff = dataStr,
                           mapBuff = mapStr)

        self.db.InsUpdRec(self.rec)
        print("Update status: ", self.db.status)

    def qryDB(self):        
        req = CommitQueryDataRequest(dataKind = "ACCOUNT", query = 'FROM ASSET SELECT FLDTKTCARDID WHERE FLDCRDCONTACT = "JOHN DOE"')
        recIds = self.db.GetQueryRecIds(req)

        req.printDomTree()

        print(recIds)

    def runAll(self):
        self.createRec()
        self.updRec()
        self.qryDB()
        
