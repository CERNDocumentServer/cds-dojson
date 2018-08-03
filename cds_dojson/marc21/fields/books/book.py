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
import re
from collections import defaultdict

from dojson.utils import force_list, for_each_value, filter_values

from ...models.books.book import model


class UnexpectedValue(Exception):
    message = "The value in the input data is not allowed"


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

    def doc_type_maping(val):
        val = str(val).strip()
        if val in ['PROCEEDINGS', "42", "43"]:
            return 'PROCEEDINGS'
        elif val in ['BOOK', "21"]:
            return 'BOOK'
        else:
            return val
        # elif value in ['LEGSERLIB']:
        #     _collections = self.get('_collection', {})
        #     _collections.update({'_collection':  val})
        # else:
        #     raise UnexpectedValue
    doc_type = {}
    if key == '980__':
        if 'a' in value:
            doc_type = doc_type_maping(value.get('a'))
        elif 'b' in value:
            doc_type = doc_type_maping(value.get('b'))
    elif key == '960__':
        doc_type = doc_type_maping(value.get('a'))
    return doc_type


@model.over('isbns', '^020__')
@for_each_value
@filter_values
def isbns(self, key, value):
    """Translates isbns fields."""

    f = {}
    medium_types = [
        'electronic version',
        'print version',
        'print version, hardback',
        'print version, paperback',
        'print version, spiral-bound',
        'CD-ROM',
        'audiobook',
        'DVD',
    ]
    u = value.get('u')

    if 'a' in value:
        f['value'] = value.get('a')
    else:
        raise ValueError('Value not provided for a required field.', key, 'a')

    if 'b' in value:
        f['medium'] = value.get('b')

    if u in medium_types:
        medium = f.get('medium')
        if medium and medium != u:
            raise ValueError(
                'Trying to override <medium> field with a different value.',
                key, 'b')
        else:
            f['medium'] = u
    else:
        f['description'] = u

    return f


@model.over('report_numbers', '(^021__)|(^037__)')
@for_each_value
@filter_values
def report_numbers(self, key, value):
    """Translates report_numbers fields."""

    if key == '035__' and value.get('9') == 'arXiv':
        return

    f = {}
    if 'a' in value:
        f['value'] = value.get('a')
    else:
        raise ValueError('Value not provided for a required field.', key, 'a')

    return f


@model.over('dois', '^0247_')
@for_each_value
@filter_values
def dois(self, key, value):
    """Translates dois fields."""

    f = {}
    material_types = [
        'addendum',
        'additional material',
        'data',
        'erratum',
        'editorial note',
        'preprint',
        'publication',
        'reprint',
        'software',
        'translation',
    ]
    q = value.get('q')

    if 'a' in value:
        f['value'] = value.get('a')
    else:
        raise ValueError('Value not provided for a required field.', key, 'a')

    if q and q in material_types:
        f['material'] = value.get('q')
    else:
        raise ValueError('This field is not matching the data model.', key, 'q')

    f['source'] = value.get('9')

    return f


@model.over('external_system_identifiers', '(^035__)|(^036__)')
@for_each_value
@filter_values
def external_system_identifiers(self, key, value):
    """Translates external_system_identifiers fields."""
    f = {}

    # FIXME when CERCER 035__a
    if '9' in value:
        f['schema'] = value.get('9')
    else:
        raise ValueError('Value not provided for a required field.', key, '9')

    if 'a' in value:
        f['value'] = value.get('a')
    else:
        raise ValueError('Value not provided for a required field.', key, 'a')

    return f


@model.over('arxiv_eprints', '^037__')
def arxiv_eprints(self, key, value):
    """Translates arxiv_eprints fields."""

    if value.get('9') != 'arXiv':
        return

    f = {}
    _categories = value.get('categories', [])

    if 'a' in value:
        f['value'] = value.get('a')
    else:
        raise ValueError('Value not provided for a required field.', key, 'a')

    if 'c' in value:
        _categories.append(value.get('c'))

    f['categories'] = _categories

    return f


@model.over('languages', '^041__')
def languages(self, key, value):
    """Translates languages fields."""

    f = {}
    _languages = value.get('languages', [])

    if 'a' in value:
        _languages.append(value.get('a'))

    f['languages'] = _languages

    return f


# @model.over('subject_classification', '^(050)|(080)|(082)(084)__')
# def subject_classification(self, key, value):
#     """Translates subject_classification fields."""

#     f = {}
#     return f


@model.over('corporate_author', '^110__')
def corporate_author(self, key, value):
    """Translates corporate_author fields."""

    f = {}
    _corporate_author = value.get('corporate_author', [])

    if 'a' in value:
        _corporate_author.append(value.get('a'))

    f['corporate_author'] = _corporate_author

    return f


# @model.over('conference_info', '^111__')
# def conference_info(self, key, value):
#     """Translates conference_info fields."""

#     f = {}
#     return f


# @model.over('title_translations', '^242__')
# def title_translations(self, key, value):
#     """Translates title_translations fields."""

#     f = {}
#     return f


@model.over('editions', '^250__')
def editions(self, key, value):
    """Translates editions fields."""

    f = {}
    _editions = value.get('editions', [])

    if 'a' in value:
        _editions.append(value.get('a'))

    f['editions'] = _editions

    return f


@model.over('imprints', '^260__')
def imprints(self, key, value):
    """Translates imprints fields."""

    _imprints = self.get('imprints', {})

    if 'a' in value:
        _imprints.update({'place': str(value.get('a'))})

    if 'b' in value:
        _imprints.update({'publisher': str(value.get('b'))})

    if 'c' in value:
        _imprints.update({'date': str(value.get('c'))})

    if 'g' in value:
        _imprints.update({'reprint': str(value.get('g'))})

    return _imprints


@model.over('preprint_date', '^269__')
def preprint_date(self, key, value):
    """Translates preprint_date fields."""

    _preprint_date = self.get('preprint_date', {})

    if 'c' in value:
        _preprint_date.update({'date': str(value.get('c'))})

    return _preprint_date


@model.over('number_of_pages', '^300__')
def number_of_pages(self, key, value):
    """Translates number_of_pages fields."""

    f = {}
    if 'b' in value:
        # remove non numeric characters and cast it to int
        f['number_of_pages'] = int(re.sub('[^0-9]', '', value.get('b')))

    return f


@model.over('book_series', '^490__')
def book_series(self, key, value):
    """Translates book_series fields."""

    f = {}

    if 'a' in value:
        f['title'] = value.get('a')
    else:
        raise ValueError('Value not provided for a required field.', key, 'a')

    if 'v' in value:
        f['volume'] = value.get('v')

    if 'x' in value:
        f['issn'] = value.get('x')

    return f


# @model.over('thesis_info', '^502__')
# def thesis_info(self, key, value):
#     """Translates thesis_info fields."""

#     f = {}
#     return f


# @model.over('table_of_content', '^505')
# def table_of_content(self, key, value):
#     """Translates table_of_content fields."""

#     f = {}
#     return f


@model.over('abstracts', '^520__')
def abstracts(self, key, value):
    """Translates abstracts fields."""

    _abstracts = self.get('abstracts', [])

    if 'a' in value:
        _abstracts.append(value.get('a'))

    return _abstracts


@model.over('funding_info', '^536__')
def funding_info(self, key, value):
    """Translates funding_info fields."""

    f = {}
    _funding_info = self.get('funding_info', [])

    if 'a' in value:
        f['agency'] = value.get('a')
    if 'c' in value:
        f['grant_number'] = value.get('c')
    if 'f' in value:
        f['project_number'] = value.get('f')

    _funding_info.append(f)

    return _funding_info


@model.over('license', '^540__')
@for_each_value
@filter_values
def license(self, key, value):
    """Translates license fields."""
    return {
        'material': value.get('3'),
        'license': value.get('a'),
        'imposing': value.get('b'),
        'url': value.get('u'),
    }


@model.over('copyright', '^542__')
@for_each_value
@filter_values
def copyright(self, key, value):
    """Translates copyright fields."""
    return {
        'material': value.get('3'),
        'holder': value.get('d'),
        'statement': value.get('f'),
        'year': value.get('g'),
        'url': value.get('u'),
    }
