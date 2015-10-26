import pycommit

import xmlrpc
from xmlrpc.server import SimpleXMLRPCServer

import sys

crm_db = pycommit.DBInterface()

class CommitRemoteInterface:
    class account:
        @staticmethod
        def fingerprint():
            pass
        
        @staticmethod
        def find_account(search_str, fields=None):
            if fields:
                search_fields = fields
            else:
                search_fields = [
                    pycommit.AccountFields['Contact'],
                    pycommit.AccountFields['CompanyName'],
                    pycommit.AccountFields['Dear']
                ]

            for f in search_fields:
                req = pycommit.DataRequest(
                    query='FROM ACCOUNT SELECT {} WHERE {} = "{}"'.format(
                        pycommit.AccountFields['AccountRecID'],
                        f,
                        acct_name
                    )
                )

                # TODO: Handle multiple recids in an intelligible fashion
                rec_ids = self.crm_db.query_recids(req)
                if rec_ids is not None: return rec_ids[0]

        @staticmethod
        def find_employee(search_str):
            req = pycommit.DataRequest(
                query='FROM ACCOUNT SELECT {} WHERE {} = "{}"'.format(
                    pycommit.AccountFields['AccountRecID'],
                    pycommit.AccountFields['AccountType'],
                    '4'
                )
            )

            rec_ids = crm_db.query_recids(req)

            employees = {}
            for _id in rec_ids:
                req = pycommit.FieldAttributesRequest(
                    query = "FROM {} SELECT ({})".format(
                        _id,
                        pycommit.AccountFields['Contact']
                    )
                )

                data = crm_db.get_rec_data_by_recid(req)
                contact = data[pycommit.AccountFields['Contact']][0]
                employees[_id] = contact

            for (key, value) in employees.items():
                fname, lname = value.lower().split(' ')
                if fname[0] + lname == search_str:
                    return key               

    class ticket:
        @staticmethod
        def fingerprint(tktno):
            recid = CommitRemoteInterface.ticket.tktrecid_from_tktno(tktno)            
            req = pycommit.FieldAttributesRequest(
                query = "FROM {} SELECT ({},{})".format(
                    recid,
                    pycommit.TicketFields['Description'],
                    pycommit.TicketFields['ContactRecID']
                )
            )

            data = crm_db.get_rec_data_by_recid(req)
            print(data)
            
            return data[pycommit.TicketFields['Description']][0]

        @staticmethod
        def acctrecid_from_tktno(tktno):
            req = pycommit.DataRequest(
                query = 'FROM TICKET SELECT {} WHERE {} = "{}"'.format(
                    pycommit.TicketFields['AccountRecID'],
                    pycommit.TicketFields['TicketNumber'],
                    tktno
                )
            )
            
            recid = crm_db.query_recids(req)

            if not recid: return
            assert len(recid) == 1

            return recid[0]

        @staticmethod
        def tktrecid_from_tktno(tktno):
            req = pycommit.DataRequest(
                query = 'FROM TICKET SELECT {} WHERE {} = "{}"'.format(
                    pycommit.TicketFields['TicketNumber'],
                    pycommit.TicketFields['TicketNumber'],
                    tktno
                )
            )
            
            recid = crm_db.query_recids(req)

            if not recid: return
            assert len(recid) == 1

            return recid[0]

        @staticmethod
        def tktdesc_from_tktno(tktno):
            pass

    class history:
        @staticmethod
        def insert_note(tkt, msg, employee_id):
            data_str = "'{tktno}','{employee}','{desc}'".format(
                tktno = tkt,
                employee = employee_id,
                desc = msg,
            )

            map_str = "'\n,\n{}\n{}\n{}".format(
                pycommit.HistoryNoteFields['LinkRecID'],
                pycommit.HistoryNoteFields['Employee'],
                pycommit.HistoryNoteFields['Description'],
            )

            rec = pycommit.DBRecord(
                pycommit.Entity['HistoryNote'],
                data_str,
                map_str
            )

            crm_db.update_rec(rec)
            return rec.getRecID()
            

if __name__ == '__main__':
    addr = ('localhost', 8000)
    server = SimpleXMLRPCServer(addr, allow_none = True)

    server.register_introspection_functions()
    server.register_instance(CommitRemoteInterface(), allow_dotted_names=True)
    
    print('Serving XML-RPC on: {}'.format(addr))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, exiting.')
        server.server_close()
        sys.exit()
