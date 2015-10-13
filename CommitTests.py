from CommitDB import CommitDB, CommitRecord
from CommitEntities import *
from CommitQuery import *

class CommitTests:  
    def __init__(self):
        self.db = CommitDB()
        self.rec = None
    
    def create_rec_test(self):      
        # Add an account to the database
        dataStr = "'Bart De Hantsetters','Hantsetters'"
        mapStr = "'\n,\n" + CommitAccountFields["FileAs"] + "\n" + CommitAccountFields["Contact"]
        
        self.rec = CommitRecord(
                            tableID = CommitEntity["Account"],
                            dataBuff = dataStr,
                            mapBuff = mapStr)
        
        self.db.update_rec(self.rec)

        print("Insert completed successfully.")
        print("RecID: {}".format(self.rec.getRecID()))
            
    def update_rec_test(self):      
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

        self.db.update_rec(self.rec)
        
        print("DB record update completed successfully")

    def query_db_test(self):       
        req = CommitQueryDataRequest(dataKind = "ACCOUNT", query = 'FROM ASSET SELECT FLDTKTCARDID WHERE FLDCRDCONTACT = "JOHN DOE"')
        recIds = self.db.query_recids(req)

        req.printDomTree()

        print("Query completed successfully.")
        print(recIds)

    def run_all(self):
        tests = [self.create_rec_test, self.update_rec_test, self.query_db_test]
        for t in tests: run = t()
        
