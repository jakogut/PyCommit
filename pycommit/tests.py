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
            query = 'FROM ACCOUNT SELECT {} WHERE {} = "Hantsetters"'.format(
                AccountFields['AccountRecID'],
                AccountFields['Contact']
            )
        )
        
        recIds = self.db.query_recids(req)

        print("RecID Query completed successfully.")

        req = FieldAttributesRequest(
            query = 'FROM {RECID} SELECT ({F0},{F1},{F2})'.format(
                RECID = 'CRDGBX99GRPAC8RH0Y9Z',
                F0 = AccountFields['AccountRecID'],
                F1 = AccountFields['Contact'],
                F2 = AccountFields['CompanyName'],
            )
        )

        data = self.db.get_rec_data_by_recid(req)
        print('Data Query completed successfully.')
            

    def run_all(self):
        tests = [self.create_rec_test, self.update_rec_test, self.query_db_test]
        for t in tests: run = t()
        
