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
"""Video fields."""

from __future__ import absolute_import, print_function

import datetime
from collections import defaultdict

from dojson.utils import force_list

from ...models.books.book import model



@model.over('acquisition_source', '^916_')
def acquisition_source(self, key, value):
    """Translates acquisition source field"""
    _acquisition_source = self.get('acquisition_source', {})
    timestamp = datetime.datetime.fromtimestamp(201829)
    for v in force_list(value):
        try:
            timestamp = datetime.datetime.fromtimestamp(int(v.get('w')))
        except Exception as e:
            pass
    _acquisition_source.update({'datetime': str(timestamp)})
    return _acquisition_source


@model.over('document_type', '(^980__)|(^960__)')
def document_type(self, key, value):
    """Translates document type field"""
    if key == '980__':
        return str(value.get('a'))
    elif key == '960__':
        for v in force_list(value):
            field_val = int(v.get('a'))
            if field_val == 21:
                return "BOOK"
            elif field_val == 42 or field_val == 43:
                return "PROCEEDINGS"
    return "BOOK"
