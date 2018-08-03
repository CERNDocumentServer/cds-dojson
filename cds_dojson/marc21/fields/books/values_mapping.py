DOCUMENT_TYPE = {
        'PROCEEDINGS': ['PROCEEDINGS', '42', '43'],
        'BOOK': ['BOOK', '21'],
        'REPORT': ['REPORT']
}

AUTHOR_ROLE = {
    'editor': ['ed.', 'ed'],
    'supervisor': ['dir.', 'dir'],
    'ilustrator': ['ill.', 'ill'],
}

COLLECTION = {
    'BOOK SUGGESTION': ['BOOKSUGGESTION'],
    'LEGSERLIB': ['LEGSERLIB'],
    'YELLOW REPORT': ['YELLOW REPORT'],
    'CERN': ['CERN'],
    'DESIGN REPORT': ['DESIGN REPORT', 'Design Report'],
    'BOOKSHOP': ['BOOKSHOP'],
    'LEGSERLIBINTLAW': ['LEGSERLIBINTLAW'],
    'LEGSERLIBCIVLAW': ['LEGSERLIBCIVLAW'],
    'LEGSERLIBLEGRES': ['LEGSERLIBLEGRES']
}


def mapping(field_map, val):
    if isinstance(val, str):
        val = val.strip()
    if val:
        for k, v in field_map.iteritems():
            if val in v:
                return k
