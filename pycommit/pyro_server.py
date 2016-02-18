from . import highlevel

import Pyro4

import argparse
parser = argparse.ArgumentParser(description='CommitCRM Remote Interface Server')
parser.add_argument('-l', '--listen-address', action='store', dest='ip', default='0.0.0.0')
parser.add_argument('-p', '--port', action='store', dest='port', default=8000, type=int)
parser.add_argument('--crm-path', action='store', dest='crm_path', default='C:\CommitCRM')
args = parser.parse_args()

if __name__ == '__main__':
    addr = (args.ip, args.port)
    hl_dbi = DBInterface()
    
    try:
        Pyro4.Daemon.serveSimple({hl_dbi: 'highlevel.DBInterface',
                                  ns = True})
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, exiting.')
        server.server_close()
        sys.exit()
