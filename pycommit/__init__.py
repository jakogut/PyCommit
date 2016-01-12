from . import commit, entities
from .commit import DBInterface, DBRecord
from .commit import DataRequest, DataResponse
from .commit import FieldAttributesRequest, FieldAttributesResponse
from .entities import Entity, AccountFields, AssetFields, ChargeFields
from .entities import HistoryNoteFields, ItemFields, TicketFields
    
def parse(dom_str):
    '''Untangle by default accepts a filename, URL, or string as input.
    However, upon passing a long enough string to untangle.parse(),
    it will raise an exception upon trying to stat() the string as a file,
    because it's too long to be a filename. Here we patcb that behavior.'''
    import os
    from xml.sax import make_parser, handler
    from untangle import Handler
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
        
    parser = make_parser()
    sax_handler = Handler()
    parser.setContentHandler(sax_handler)
    
    if hasattr(dom_str, 'read'):
        parser.parse(dom_str)
    else:
        parser.parse(StringIO(dom_str))

    return sax_handler.root

import untangle
untangle.parse = parse
