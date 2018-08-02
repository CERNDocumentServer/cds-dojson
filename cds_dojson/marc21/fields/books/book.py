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

from dojson.errors import IgnoreKey
from dojson.utils import force_list, filter_values, ignore_value

from cds_dojson.marc21.fields.books.values_mapping import mapping, \
    DOCUMENT_TYPE, AUTHOR_ROLE
from cds_dojson.marc21.fields.utils import clean_email, filter_list_values, \
    out_strip, replace_in_list

from cds_dojson.marc21.fields.utils import get_week_start
from ...models.books.book import model


class UnexpectedValue(Exception):
    message = "The value in the input data is not allowed"


class UnexpectedSubfield(Exception):
    message = "This subfield is not expected"


@model.over('acquisition_source', '(^916__)|(^859__)')
def acquisition_source(self, key, value):
    """Translates acquisition source field"""
    _acquisition_source = self.get('acquisition_source', {})
    if key == '916__':
        try:
            year, week = str(value.get('w'))[:4], str(value.get('w'))[4:]
            datetime = get_week_start(int(year), int(week))
        except Exception as e:
            raise e
        _acquisition_source.update({'datetime': str(datetime)})
    elif key == '859__' and 'f' in value:
        _acquisition_source.update({'email': clean_email(value.get('f'))})
    return _acquisition_source


@model.over('_collections', '^980__')
def collection(self, key, value):
    """ Translates collection field - WARNING - also document type field """
    _collections = self.get('_collections', [])
    for v in force_list(value):
        if (str(v.get('a', '')).strip() == 'LEGSERLIB' or
                str(v.get('b', '')).strip() == 'LEGSERLIB'):
            _collections.append('LEGSERLIB')
        else:
            self['document_type'] = document_type(self, key, value)
            raise IgnoreKey('_collections')
    return _collections


@model.over('document_type', '(^980__)|(^960__)')
def document_type(self, key, value):
    """Translates document type field"""

    def doc_type_maping(val):
        val = str(val).strip()
        result = mapping(DOCUMENT_TYPE, val)
        if not result:
            raise UnexpectedValue
        return result

    doc_type = {}
    if key == '980__':
        if 'a' in value:
            doc_type = doc_type_maping(value.get('a'))
        elif 'b' in value:
            doc_type = doc_type_maping(value.get('b'))
        else:
            return UnexpectedValue
    elif key == '960__':
        doc_type = doc_type_maping(value.get('a'))
    else:
        return UnexpectedValue
    return doc_type


@model.over('authors', '^700__')
@filter_list_values
def authors(self, key, value):
    _authors = self.get('authors', [])
    for v in force_list(value):
        if value.get('a'):
            _authors.append({'full_name': v.get('a').strip(),
                             'role': mapping(AUTHOR_ROLE, v.get('e')),
                             'affiliation': v.get('u', None),
                            })
        else:
            raise UnexpectedValue
    return _authors


@model.over('corporate_authors', '^710__')
@ignore_value
@out_strip
def corporate_authors(self, key, value):
    _corporate_authors = self.get('corporate_authors', [])
    for v in force_list(value):
        if 'a' in v:
            return v.get('a')
        else:
            self['collaborations'] = collaborations(self, key, value)
            if not _corporate_authors:
                raise IgnoreKey('corporate_authors')


@model.over('collaborations', '^710__')
@replace_in_list('Collaboration', '')
def collaborations(self, key, value):
    _collaborations = self.get('collaborations', [])
    for v in force_list(value):
        if 'g' in v:
            _collaborations.append(v.get('g'))
        elif '5' in v:
            _collaborations.append(v.get('5'))
        else:
            raise UnexpectedSubfield
    return _collaborations


# TODO - discuss how we would like to keep links to holdings (files and ebooks)
@model.over('urls', '^8564_')
def urls(self, key, value):
    _urls = self.get('urls', [])
    return ['cds.cern.ch']


