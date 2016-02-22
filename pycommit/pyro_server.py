from pycommit import highlevel

import Pyro4

Pyro4.config.COMPRESSION = True
Pyro4.config.SERVERTYPE = 'multiplex'

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='CommitCRM Remote Interface Server')
    parser.add_argument('-l', '--listen-address', action='store', dest='ip', default='0.0.0.0')
    parser.add_argument('-p', '--port', action='store', dest='port', default=8000, type=int)
    parser.add_argument('--crm-path', action='store', dest='crm_path', default='C:\CommitCRM')
    args = parser.parse_args()

    addr = (args.ip, args.port)
    hl_dbi = highlevel.DBInterface(args.crm_path)
    
    try:
        daemon = Pyro4.Daemon.serveSimple({hl_dbi: 'highlevel.DBInterface'},
                                  host = args.ip,
                                  port = args.port,
                                  ns = True)
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, exiting.')
        daemon.close()
        sys.exit()
