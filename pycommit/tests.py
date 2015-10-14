from commit import DBInterface, DBRecord, DataRequest, DataResponse
from entities import *

class CommitTests:  
    def __init__(self):
        self.db = DBInterface()
        self.rec = None
    
    def create_rec_test(self):      
        # Add an account to the database
        dataStr = "'Bart De Hantsetters','Hantsetters'"
        mapStr = "'\n,\n" + AccountFields["FileAs"] + "\n" + AccountFields["Contact"]
        
        self.rec = DBRecord(
                            tableID = Entity["Account"],
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
        mapStr = "'\n,\n" + AccountFields["LastName"]
        mapStr += '\n'    + AccountFields["AccountRecID"]

        self.rec = DBRecord(tableID = Entity["Account"],
                           dataBuff = dataStr,
                           mapBuff = mapStr)

        self.db.update_rec(self.rec)
        
        print("DB record update completed successfully")

    def query_db_test(self):       
        req = DataRequest(
            q_from = "ACCOUNT",
            q_select = AccountFields['AccountRecID'],
            q_where = AccountFields['Contact'],
            q_op = '=',
            q_value = 'John Doe')

        print("Request: ")
        req.printDomTree()
        
        recIds = self.db.query_recids(req)

        print("Query completed successfully.")
        print(recIds)

    def run_all(self):
        tests = [self.create_rec_test, self.update_rec_test, self.query_db_test]
        for t in tests: run = t()
        