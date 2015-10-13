from CommitDB import CommitDB, CommitRecord
from CommitEntities import *
from CommitQuery import *

class CommitTests:  
    def __init__(self):
        self.db = CommitDB()
        
        db_init = [self.db.InitDbEngDll, self.db.InitDbQryDll]
        for init in db_init: init()

        self.rec = None

    def __del__(self):
        self.db.TerminateDbEngDll()
        self.db.TerminateDbQryDll()
    
    def create_rec(self):      
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

            
    def update_rec(self):      
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

    def query_db(self):       
        req = CommitQueryDataRequest(dataKind = "ACCOUNT", query = 'FROM ASSET SELECT FLDTKTCARDID WHERE FLDCRDCONTACT = "JOHN DOE"')
        recIds = self.db.GetQueryRecIds(req)

        req.printDomTree()

        print(recIds)

    def run_all(self):
        tests = [self.create_rec, self.update_rec, self.query_db]
        for t in tests: run = t()
        
