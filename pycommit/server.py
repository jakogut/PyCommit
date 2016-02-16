from . import commit, entities

import xmlrpc
from xmlrpc.server import SimpleXMLRPCServer

import sys

class AmbiguousValue(Exception):
    pass

class CommitRemoteInterface(object):
    def __init__(self, crm_path):
        self.crm_db = commit.DBInterface(CRMPath=crm_path)

    def get_recids(self, entity, search_criteria):
        query = 'FROM {} SELECT * WHERE {} = "{}" '

        search_keys = list(search_criteria.keys())

        key = search_keys.pop()
        query = query.format(entity, key, search_criteria.pop(key))

        for _, _ in search_criteria.items():
            key = search_keys.pop()
            query += 'AND {} = "{}" '.format(key, search_criteria[key])

        req = commit.RecIDRequest(query.format(entity=entity, **search_criteria))

        try:
            rec_ids = self.crm_db.query_recids(req)
        except commit.QueryError as e:
            print(e)
            return

        return rec_ids

    def find_record(self, entity, value, fields):
        for f in fields:
            req = commit.RecIDRequest(
                query='FROM {} SELECT * WHERE {} = "{}"'.format(
                    entity, f, value))
            
            try:
                rec_ids = self.crm_db.query_recids(req)
            except commit.QueryError as e:
                print(e)
                return
            
            if rec_ids is not None: return rec_ids[0]

    def get_field(self, recid, field):
        req = commit.RecordDataRequest(
            query = "FROM {} SELECT ({})".format(
                recid, field))

        try:
            data = self.crm_db.get_rec_data_by_recid(req)
        except commit.QueryError as e:
            print(e)
            return ''

        if data is None: return
        return data[field]

    def update_record_from_dict(self, entity, data):
        if (entity is None) or (data is None):
            return
        
        data_str, map_str = '', "'\n,\n"
        
        for key, value in data.items():
            data_str += "'{}',".format(value)
            map_str += "{}\n".format(key)

        rec = commit.DBRecord(entity, data_str, map_str)

        try:
            self.crm_db.update_rec(rec)
        except commit.QueryError as e:
            print(e)
            return
        
        return rec.getRecID()

    # Named arguments don't work with built-in XML-RPC
    def update_record(self, entity, **kwargs):
        return update_record_from_dict(entity, kwargs)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='CommitCRM Remote Interface Server')
    parser.add_argument('-l', '--listen-address', action='store', dest='ip', default='0.0.0.0')
    parser.add_argument('-p', '--port', action='store', dest='port', default=8000, type=int)
    parser.add_argument('--crm-path', action='store', dest='crm_path', default='C:\CommitCRM')
    args = parser.parse_args()

    addr = (args.ip, args.port)
    server = SimpleXMLRPCServer(addr, allow_none = True, logRequests = False)
    server.register_instance(CommitRemoteInterface(args.crm_path))

    try:
        print('Serving XML-RPC on: {}'.format(addr))
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, exiting.')
        server.server_close()
        sys.exit()
