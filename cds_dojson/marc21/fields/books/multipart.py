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
import re

from dojson.errors import IgnoreKey

from cds_dojson.marc21.fields.books.errors import UnexpectedValue, \
    MissingRequiredField
from cds_dojson.marc21.fields.books.utils import extract_parts
from cds_dojson.marc21.fields.utils import clean_val, out_strip
from cds_dojson.marc21.models.books.multipart import model


@model.over('title', '^245__')
def title(self, key, value):
    """Translates book series title."""
    _series_title = self.get('title', None)
    # assume that is goes by order of fields and check 245 first
    return {'title': clean_val('a', value, str),
            'subtitle': clean_val('b', value, str),
            }


@model.over('volumes', '^246__')
def volumes(self, key, value):
    _series_title = self.get('title', None)

    # check if it is a multipart monograph
    val_n = clean_val('n', value, str)
    val_p = clean_val('p', value, str)
    if not val_n and not val_p:
        raise UnexpectedValue(subfield='a',
                              message=' this record is probably not a series')
    if not _series_title:
        raise MissingRequiredField(
            subfield='a', message=' this record is missing a main title')

    val_n = clean_val('n', value, str)

    # if __n matches the pattern it is isbn if not it is a volume index
    # of the document within this series
    if re.match(r'^\d*[0-9X]$', val_n):
        self['isbn'] = val_n
    # series created
    self['mode_of_issuance'] = 'multipart_monograph'
    raise IgnoreKey('volumes')


@model.over('number_of_volumes', '^300__')
@out_strip
def number_of_volumes(self, key, value):
    """Translates number of volumes."""
    _series_title = self.get('title', None)
    if not _series_title:
        raise MissingRequiredField(
            subfield='a', message=' this record is missing a main title')
    val_a = clean_val('a', value, str)
    parsed_a = extract_parts(val_a)
    if not parsed_a["number_of_pages"] and 'v' in val_a:
        return re.findall(r'\d+', val_a)[0]
    raise UnexpectedValue(subfield='a')
