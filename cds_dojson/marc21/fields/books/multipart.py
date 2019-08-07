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
from dojson.utils import for_each_value, filter_values, force_list

from cds_dojson.marc21.fields.books.errors import UnexpectedValue, \
    MissingRequiredField
from cds_dojson.marc21.fields.books.utils import extract_parts
from cds_dojson.marc21.fields.utils import clean_val, out_strip
from cds_dojson.marc21.models.books.multipart import model


@model.over('legacy_recid', '^001')
def recid(self, key, value):
    """Record Identifier."""
    return int(value)


@model.over('isbns', '^020__')
@out_strip
@for_each_value
def isbns(self, key, value):
    """Translates isbns stored in the record."""
    _migration = self.get('_migration', {'volumes': []})
    _isbns = self.get('isbns', [])

    val_u = clean_val('u', value, str)
    val_a = clean_val('a', value, str)

    if val_u:
        volume_search = \
            re.search('(.*?)\(((v\.*|vol\.*|volume\.*|part)(\d+))\)', val_u)
        # if set found it means that the isbn is for the whole multipart
        set_search = re.search('(.*?)\(set\.*\)', val_u)
        if volume_search:
            print('FOUND volumes...')
            try:
                volume_obj = {'volume': int(volume_search.group(4)),
                              'isbn': clean_val('a', value, str),
                              'physical_description':
                                  volume_search.group(1).strip()
                              }

                _migration['volumes'].append(volume_obj)
                self['_migration'] = _migration
            except ValueError:
                raise UnexpectedValue(subfield='u',
                                      message=' volume index not a number')
        if set_search:
            self['physical_description'] = set_search.group(1).strip()
            return val_a if val_a not in _isbns else None  # monograph isbn
        if not volume_search:
            self['physical_description'] = val_u
            return val_a if val_a not in _isbns else None
        if not set_search and not volume_search:
            self['physical_description'] = val_u
            return val_a if val_a not in _isbns else None
    elif not val_u and val_a:
        # if I dont have volume info but only isbn
        return val_a if val_a not in _isbns else None
    else:
        raise UnexpectedValue(subfield='a', message=' isbn not provided')


@model.over('title', '^245__')
@filter_values
def title(self, key, value):
    """Translates book series title."""
    # assume that is goes by order of fields and check 245 first
    return {'title': clean_val('a', value, str),
            'subtitle': clean_val('b', value, str),
            }


@model.over('_migration', '^246__')
def migration(self, key, value):
    """Translates volumes titles."""
    _series_title = self.get('title', None)

    # I added this in the model, I'm sure it's there
    _migration = self.get('_migration', {'volumes': []})

    for v in force_list(value):
        # check if it is a multipart monograph
        val_n = clean_val('n', v, str)
        val_p = clean_val('p', v, str)
        if not val_n and not val_p:
            raise UnexpectedValue(
                subfield='n', message=' this record is probably not a series')

        volume_index = re.findall(r'\d+', val_n) if val_n else None
        if volume_index and len(volume_index) > 1:
            raise UnexpectedValue(subfield='n',
                                  message=' volume has more than one digit ')
        else:
            volume_obj = {'title': val_p,
                          'volume': int(volume_index[0]) if volume_index else None,
                          }
            _migration['volumes'].append(volume_obj)
    if not _series_title:
        raise MissingRequiredField(
            subfield='a', message=' this record is missing a main title')

    # series created

    return _migration


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
    if not parsed_a["number_of_pages"] and ('v' in val_a or 'vol' in val_a):
        _volumes = re.findall(r'\d+', val_a)
        if _volumes:
            return _volumes[0]
    raise IgnoreKey('number_of_volumes')
