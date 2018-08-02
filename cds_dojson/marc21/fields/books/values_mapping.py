DOCUMENT_TYPE = {
        'PROCEEDINGS': ['PROCEEDINGS', '42', '43'],
        'BOOK': ['BOOK', '21']
}

AUTHOR_ROLE = {
    'editor': ['ed.', 'ed'],
    'supervisor': ['dir.', 'dir'],
    'ilustrator': ['ill.', 'ill'],
}


def mapping(field_map, val):
    if isinstance(val, str):
        val = val.strip()
    if val:
        for k, v in field_map.iteritems():
            if val in v:
                return k
