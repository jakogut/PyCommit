from . import commit, entities

import xmlrpc
from xmlrpc.server import SimpleXMLRPCServer

import sys

crm_db = commit.DBInterface(CRMPath='E:\COMMIT\CommitCRM')

class AmbiguousValue(Exception):
    pass

def get_field(recid, field):
    req = commit.FieldAttributesRequest(
        query = "FROM {} SELECT ({})".format(
            recid,
            field
        )
    )

    data = crm_db.get_rec_data_by_recid(req)

    if data is None: return
    return data[field][0]

def update_record_from_dict(entity, data):
    update_record(entity, **data)

def update_record(entity, **kwargs):
    if (entity is None) or (kwargs is None):
        return
    
    data_str = ''
    map_str = "'\n,\n"
    
    for key, value in kwargs.items():
        data_str += "'{}',".format(value)
        map_str += "{}\n".format(key)

    rec = commit.DBRecord(entity, data_str, map_str)

    crm_db.update_rec(rec)
    return rec.getRecID()

class CommitRemoteInterface:        
    class account:
        @staticmethod
        def fingerprint():
            pass

        @staticmethod
        def update(**kwargs):
            update_record(entities.Entity['Account'], **kwargs)

        @staticmethod        
        def recid_list():
            print('Entering function')
            
            req = commit.DataRequest(
                query = 'FROM ACCOUNT SELECT * WHERE {} ! ""'.format(
                    entities.AccountFields['AccountRecID']
                ),
                maxRecordCnt = 10000
            )

            rec_ids = crm_db.query_recids(req)
            if rec_ids is not None: return rec_ids
        
        @staticmethod
        def find(search_str, fields=None):
            if fields:
                search_fields = fields
            else:
                search_fields = [
                    entities.AccountFields['Contact'],
                    entities.AccountFields['CompanyName'],
                    entities.AccountFields['Dear']
                ]

            for f in search_fields:
                req = commit.DataRequest(
                    query='FROM ACCOUNT SELECT * WHERE {} = "{}"'.format(
                        f,
                        search_str
                    )
                )

                # TODO: Handle multiple recids in an intelligible fashion
                rec_ids = crm_db.query_recids(req)
                if rec_ids is not None: return rec_ids[0]

        @staticmethod
        def find_by_email(email):
            return CommitRemoteInterface.account.find(
                email,
                [ entities.AccountFields['Email1'],
                  entities.AccountFields['Email2'] ]
            )

        @staticmethod
        def get_contact(recid):
            return get_field(
                recid,
                entities.AccountFields['Contact']
            )

        @staticmethod
        def find_employee(search_str):            
            req = commit.DataRequest(
                query='FROM ACCOUNT SELECT * WHERE {} = "{}"'.format(
                    entities.AccountFields['AccountType'],
                    '4'
                )
            )

            rec_ids = crm_db.query_recids(req)

            employees = {}
            for _id in rec_ids:
                req = commit.FieldAttributesRequest(
                    query = "FROM {} SELECT ({})".format(
                        _id,
                        entities.AccountFields['Contact']
                    )
                )

                data = crm_db.get_rec_data_by_recid(req)
                contact = data[entities.AccountFields['Contact']][0]
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
            return CommitRemoteInterface.ticket.get_desc(tktno)

        @staticmethod
        def update(**kwargs):
            return update_record(entities.Entity['Ticket'], **kwargs)

        @staticmethod
        def create(acct_recid, desc, mgr=''):
            return CommitRemoteInterface.ticket.update(
                **{
                    entities.TicketFields['AccountRecID'] : acct_recid,
                    entities.TicketFields['Description'] : desc,
                    entities.TicketFields['EmpRecID'] : mgr
                }
            )

        def update_desc(tktno, desc):
            return CommitRemoteInterface.ticket.update(
                **{
                    entities.TicketFields['TicketNumber'] : tktno,
                    entities.TicketFields['Description'] : desc
                }
            )

        @staticmethod
        def get_acctrecid(tktno):
            tktrecid = CommitRemoteInterface.ticket.get_recid(tktno)
            return get_field(tktrecid, entities.TicketFields['AccountRecID'])

        @staticmethod
        def get_recid(tktno):
            req = commit.DataRequest(
                query = 'FROM TICKET SELECT * WHERE {} = "{}"'.format(
                    entities.TicketFields['TicketNumber'],
                    tktno
                )
            )

            recid = None
            
            try:
                recid = crm_db.query_recids(req)
            except:
                pass

            if not recid: return

            if len(recid) > 1:
                raise AmbiguousValue

            return recid[0]

        @staticmethod
        def get_desc(tktno):
            recid = CommitRemoteInterface.ticket.get_recid(tktno)            
            return get_field(recid, entities.TicketFields['Description'])

        @staticmethod
        def get_assetrecid(tktno):
            recid = CommitRemoteInterface.ticket.get_recid(tktno)
            return get_field(recid, entities.TicketFields['AssetRecID'])

        @staticmethod
        def link_asset(tktno, asset_recid):
            data_str = "'{}','{}'".format(tktno, asset_recid)

            map_str = "'\n,\n{}\n{}".format(
                entities.TicketFields['TicketNumber'],
                entities.TicketFields['AssetRecID'],
            )

            rec = commit.DBRecord(
                tableID = entities.Entity['Ticket'],
                dataBuff = data_str,
                mapBuff = map_str,
            )

            crm_db.update_rec(rec)

    class history:
        @staticmethod
        def insert_note(tkt, msg, employee_id):
            return update_record(
                entities.Entity['HistoryNote'],
                **{entities.HistoryNoteFields['LinkRecID'] : tkt,
                entities.HistoryNoteFields['Employee'] : employee_id,
                entities.HistoryNoteFields['Description'] : msg}
            )

    class asset:
        @staticmethod
        def update(**kwargs):
            return update_record(
                entities.Entity['Asset'],
                **kwargs
            )

        @staticmethod
        def create(acct, name, desc, status = 'A', _type = 'H'):
            return CommitRemoteInterface.asset.update(
                **{
                    entities.AssetFields['AccountRecID'] : acct,
                    entities.AssetFields['Name'] : name,
                    entities.AssetFields['Description'] : desc,
                    entities.AssetFields['Status'] : status,
                    entities.AssetFields['Type'] : _type
                }
            )

        @staticmethod
        def update_desc(recid, desc):
            return CommitRemoteInterface.asset.update(
                **{
                    entities.AssetFields['RecordID'] : recid,
                    entities.AssetFields['Description'] : desc
                }
            )

        @staticmethod
        def find(uuid, acct):
            req = commit.DataRequest(
                query = 'FROM ASSET SELECT {} WHERE {} = "{}" \
                         AND {} = "{}" AND {} = "{}"'.format(
                    entities.AssetFields['RecordID'],
                    entities.AssetFields['Name'],
                    uuid,
                    entities.AssetFields['Status'],
                    'A',
                    entities.AssetFields['AccountRecID'],
                    acct
                )
            )

            recid = crm_db.query_recids(req)

            if not recid: return
            
            if len(recid) > 1:
                raise AmbiguousValue

            return recid[0]

if __name__ == '__main__':
    addr = ('0.0.0.0', 8000)
    server = SimpleXMLRPCServer(addr, allow_none = True)

    #server.register_introspection_functions()
    server.register_instance(CommitRemoteInterface(), allow_dotted_names=True)
    server.register_function(get_field)
    server.register_function(update_record_from_dict)
    
    print('Serving XML-RPC on: {}'.format(addr))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, exiting.')
        server.server_close()
        sys.exit()
