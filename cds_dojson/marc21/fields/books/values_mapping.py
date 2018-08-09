# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017, 2018 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Book values mapping."""

DOCUMENT_TYPE = {
    'PROCEEDINGS': ['PROCEEDINGS', '42', '43'],
    'BOOK': ['BOOK', '21'],
    'REPORT': ['REPORT']
}

AUTHOR_ROLE = {
    'editor': ['ED.', 'ED'],
    'supervisor': ['DIR.', 'DIR'],
    'ilustrator': ['ILL.', 'ILL'],
}

COLLECTION = {
    'BOOK SUGGESTION': ['BOOKSUGGESTION'],
    'LEGSERLIB': ['LEGSERLIB'],
    'YELLOW REPORT': ['YELLOW REPORT', 'YELLOWREPORT'],
    'CERN': ['CERN'],
    'DESIGN REPORT': ['DESIGN REPORT', 'DESIGNREPORT'],
    'BOOKSHOP': ['BOOKSHOP'],
    'LEGSERLIBINTLAW': ['LEGSERLIBINTLAW'],
    'LEGSERLIBCIVLAW': ['LEGSERLIBCIVLAW'],
    'LEGSERLIBLEGRES': ['LEGSERLIBLEGRES']
}

ACQUISITION_METHOD = {
    'submitter': ['h'],
    'batchuploader': ['n', 'm'],
}


def mapping(field_map, val):
    """
    Maps the old value to a new one according to the map.

    important: the maps values must be uppercase, in order to catch all the
    possible values in the field
    :param field_map: one of the maps specified
    :param val: old value
    :return: output value matched in map
    """
    if isinstance(val, str):
        val = val.strip()
    if val:
        for k, v in field_map.items():
            if val.upper() in v:
                return k
