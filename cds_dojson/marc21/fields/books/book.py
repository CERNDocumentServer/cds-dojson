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
"""Books fields."""

from __future__ import absolute_import, print_function, unicode_literals

from dojson.errors import IgnoreKey
from dojson.utils import filter_values, for_each_value

from cds_dojson.marc21.fields.books.errors import ManualMigrationRequired, \
    UnexpectedValue
from cds_dojson.marc21.fields.books.utils import is_excluded, extract_parts
from cds_dojson.marc21.fields.utils import clean_val
from cds_dojson.marc21.models.books.book import model


@model.over('alternative_titles', '^246__')
@for_each_value
@filter_values
def alternative_titles(self, key, value):
    """Alternative titles."""
    if 'n' in value:
        self['volume'] = volume(self, key, value)
    if 'p' in value:
        # if series detected
        if self.get('volumes', None):
            val_p = clean_val('p', value, str)
            self['volumes_titles'].append(
                {'title': val_p, 'volume': volume(self, key, value)}
            ) if val_p else None
        else:
            self['volumes_titles'] = []
        return {}
    else:
        return {
            'title': clean_val('a', value, str, req=True),
            'subtitle': clean_val('b', value, str),
            'source': clean_val('i', value, str),
        }


@model.over('volume', '^246__')
@for_each_value
def volume(self, key, value):
    """Translates volumes index in series."""
    _volume = self.get('volume', None)
    val_n = clean_val('n', value, str, req=True)
    if _volume and _volume != val_n:
        raise ManualMigrationRequired(subfield='n')
    return val_n


@model.over('number_of_pages', '^300__')   # item
def number_of_pages(self, key, value):
    """Translates number_of_pages fields."""
    val = clean_val('a', value, str)
    if is_excluded(val):
        raise IgnoreKey('number_of_pages')

    parts = extract_parts(val)
    if parts['has_extra']:
        raise UnexpectedValue(subfield='a')
    if parts['physical_description']:
        self['physical_description'] = parts['physical_description']
    if parts['number_of_pages']:
        return parts['number_of_pages']
    raise UnexpectedValue(subfield='a')


@model.over('title', '^245__')
@filter_values
def title(self, key, value):
    """Translates title."""
    if 'title' in self:
        raise UnexpectedValue()

    return {
        'title': clean_val('a', value, str, req=True),
        'subtitle': clean_val('b', value, str),
    }
