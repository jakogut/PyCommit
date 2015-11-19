from commit import *
from entities import *


class CommitTests:

    def __init__(self):
        self.db = DBInterface()
        self.rec = None

    def create_rec_test(self):
        # Add an account to the database
        dataStr = "'Bart De Hantsetters','Hantsetters'"
        mapStr = "'\n,\n" + \
            AccountFields["FileAs"] + "\n" + AccountFields["Contact"]

        self.rec = DBRecord(
            tableID=Entity["Account"],
            dataBuff=dataStr,
            mapBuff=mapStr)

        self.db.update_rec(self.rec)

        print("Insert completed successfully.")
        print("RecID: {}".format(self.rec.getRecID()))

    def update_rec_test(self):
        # Update the existing record
        if self.rec is None:
            print("Record for updating does not exist.")
            return

        dataStr = "'De Hantsetters','" + self.rec.getRecID() + "'"
        mapStr = "'\n,\n" + AccountFields["LastName"]
        mapStr += '\n' + AccountFields["AccountRecID"]

        self.rec = DBRecord(tableID=Entity["Account"],
                            dataBuff=dataStr,
                            mapBuff=mapStr)

        self.db.update_rec(self.rec)

        print("DB record update completed successfully")

    def query_db_test(self):
        req = DataRequest(
            query='FROM ACCOUNT SELECT {} WHERE {} = "{}" AND {} = "{}"'.format(
                AccountFields['AccountRecID'],
                AccountFields['Contact'],
                'Hantsetters',
                AccountFields['LastName'],
                'De Hantsetters'
            )
        )

        recIds = self.db.query_recids(req)

        print("RecID Query completed successfully.\n", recIds)

        req = FieldAttributesRequest(
            query='FROM {RECID} SELECT ({F0},{F1},{F2})'.format(
                RECID=recIds[0],
                F0=AccountFields['AccountRecID'],
                F1=AccountFields['Contact'],
                F2=AccountFields['CompanyName'],
            )
        )

        data = self.db.get_rec_data_by_recid(req)
        print('Data Query completed successfully.')
        print(data)

    def run_all(self):
        tests = [
            self.create_rec_test,
            self.update_rec_test,
            self.query_db_test]
        for t in tests:
            run = t()
