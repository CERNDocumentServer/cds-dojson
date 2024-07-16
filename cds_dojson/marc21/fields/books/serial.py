# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017-2019 CERN.
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
"""Books fields."""
from dojson.utils import for_each_value

from cds_dojson.marc21.fields.books.multipart import isbns as multipart_identifiers
from cds_dojson.marc21.fields.utils import clean_val, filter_list_values, out_strip
from cds_dojson.marc21.models.books.serial import model


@model.over('legacy_recid', '^001')
def recid(self, key, value):
    """Record Identifier."""
    return int(value)


@model.over('title', '^490__')
@for_each_value
@out_strip
def title(self, key, value):
    """Translates book series title."""
    _identifiers = self.get('identifiers', [])
    issn = clean_val('x', value, str)
    if issn:
        _identifiers.append({'scheme': 'ISSN', 'value': issn})
        self['identifiers'] = _identifiers
    self['mode_of_issuance'] = 'SERIAL'
    return clean_val('a', value, str, req=True)


@model.over('identifiers', '^020__')
@filter_list_values
def identifiers(self, key, value):
    """Translates identifiers fields."""
    return multipart_identifiers(self, key, value)
