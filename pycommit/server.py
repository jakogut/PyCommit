import pycommit

import xmlrpc
from xmlrpc.server import SimpleXMLRPCServer

import sys

crm_db = pycommit.DBInterface()

class AmbiguousReference(Exception):
    pass

class CommitRemoteInterface:
    @staticmethod
    def _get_field(recid, field):
        req = pycommit.FieldAttributesRequest(
            query = "FROM {} SELECT ({})".format(
                recid,
                field
            )
        )

        data = crm_db.get_rec_data_by_recid(req)
        return data[field][0]
        
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
                rec_ids = crm_db.query_recids(req)
                if rec_ids is not None: return rec_ids[0]

        @staticmethod
        def contact(recid):
            return CommitRemoteInterface._get_field(
                recid,
                pycommit.AccountFields['Contact']
            )

        @staticmethod
        def find_employee(search_str):            
            req = pycommit.DataRequest(
                query='FROM ACCOUNT SELECT * WHERE {} = "{}"'.format(
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
                try:
                    fname, lname = value.lower().split(' ')
                except ValueError:
                    continue
                if fname[0] + lname == search_str:
                    return key               

    class ticket:
        @staticmethod
        def fingerprint(tktno):
            return CommitRemoteInterface.ticket.tktdesc_from_tktno(tktno)

        @staticmethod
        def acctrecid_from_tktno(tktno):
            tktrecid = CommitRemoteInterface.ticket.tktrecid_from_tktno(tktno)
            return CommitRemoteInterface._get_field(tktrecid, pycommit.TicketFields['AccountRecID'])

        @staticmethod
        def tktrecid_from_tktno(tktno):
            req = pycommit.DataRequest(
                query = 'FROM TICKET SELECT * WHERE {} = "{}"'.format(
                    pycommit.TicketFields['TicketNumber'],
                    tktno
                )
            )
            
            recid = crm_db.query_recids(req)

            if not recid: return

            if len(recid) > 1:
                raise AmbiguousReference

            return recid[0]

        @staticmethod
        def tktdesc_from_tktno(tktno):
            recid = CommitRemoteInterface.ticket.tktrecid_from_tktno(tktno)            
            return CommitRemoteInterface._get_field(recid, pycommit.TicketFields['Description'])

        @staticmethod
        def assetrecid_from_tktno(tktno):
            recid = CommitRemoteInterface.ticket.tktrecid_from_tktno(tktno)
            return CommitRemoteInterface._get_field(recid, pycommit.TicketFields['AssetRecID'])

        @staticmethod
        def link_asset(tktno, asset_recid):
            data_str = "'{}','{}'".format(tktno, asset_recid)

            map_str = "'\n,\n{}\n{}".format(
                pycommit.TicketFields['TicketNumber'],
                pycommit.TicketFields['AssetRecID'],
            )

            rec = pycommit.DBRecord(
                tableID = pycommit.Entity['Ticket'],
                dataBuff = data_str,
                mapBuff = map_str,
            )

            crm_db.update_rec(rec)

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

    class asset:
        @staticmethod
        def update(acct, name, desc, status = 'A', _type = 'H'):
            data_str = "'{}','{}','{}','{}','{}'".format(
                acct, name, desc, status, _type
            )

            map_str = "'\n,\n{}\n{}\n{}\n{}\n{}".format(
                pycommit.AssetFields['AccountRecID'],
                pycommit.AssetFields['Name'],
                pycommit.AssetFields['Description'],
                pycommit.AssetFields['Status'],
                pycommit.AssetFields['Type'],
            )

            rec = pycommit.DBRecord(
                pycommit.Entity['Asset'],
                data_str,
                map_str
            )

            crm_db.update_rec(rec)

        @staticmethod
        def find(uuid, acct):
            req = pycommit.DataRequest(
                query = 'FROM ASSET SELECT {} WHERE {} = "{}" AND {} = "{}" AND {} = "{}"'.format(
                    pycommit.AssetFields['RecordID'],
                    pycommit.AssetFields['Name'],
                    uuid,
                    pycommit.AssetFields['Status'],
                    'A',
                    pycommit.AssetFields['AccountRecID'],
                    acct
                )
            )

            recid = crm_db.query_recids(req)

            if not recid: return
            
            if len(recid) > 1:
                raise AmbiguousReference

            return recid[0]

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
