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

from __future__ import absolute_import, print_function

from dojson.errors import IgnoreKey

import re
from dojson.utils import force_list, for_each_value, filter_values

from cds_dojson.marc21.fields.books.values_mapping import mapping, \
    DOCUMENT_TYPE, AUTHOR_ROLE, COLLECTION, ACQUISITION_METHOD
from cds_dojson.marc21.fields.utils import clean_email, filter_list_values, \
    out_strip, clean_val, \
    ManualMigrationRequired, replace_in_result, rel_url, clean_pages

from cds_dojson.marc21.fields.utils import get_week_start
from ...models.books.book import model


@model.over('acquisition_source', '(^916__)|(^859__)')
@filter_values
def acquisition_source(self, key, value):
    """Translates acquisition source field."""
    _acquisition_source = self.get('acquisition_source', {})
    if key == '916__':
        date_num = clean_val('w', value, int, regex_format=r'\d{4}$')
        year, week = str(date_num)[:4], str(date_num)[4:]
        datetime = get_week_start(int(year), int(week))
        _acquisition_source.update(
            {'datetime': str(datetime),
             'method': mapping(ACQUISITION_METHOD,
                               clean_val('s', value, str))})
    elif key == '859__' and 'f' in value:
        _acquisition_source.update(
            {'email': clean_email(clean_val('f', value, str))})
    return _acquisition_source


@model.over('_collections', '(^980__)|(^690C_)|(^697C_)')
@out_strip
def collection(self, key, value):
    """Translates collection field - WARNING - also document type field."""
    _collections = self.get('_collections', [])

    for v in force_list(value):
        result_a = mapping(COLLECTION, clean_val('a', v, str))
        result_b = mapping(COLLECTION, clean_val('b', v, str))
        if result_a or result_b:
            _collections.append(result_a)
            _collections.append(result_b)
        else:
            self['document_type'] = document_type(self, key, value)
            raise IgnoreKey('_collections')
    return _collections


@model.over('document_type', '(^980__)|(^960__)|(^690C_)')
@out_strip
def document_type(self, key, value):
    """Translates document type field."""
    _doc_type = self.get('document_type', [])

    def doc_type_mapping(val):
        if val:
            return mapping(DOCUMENT_TYPE, val)

    for v in force_list(value):
        _doc_type.append(doc_type_mapping(clean_val('a', v, str)))
        _doc_type.append(doc_type_mapping(clean_val('b', v, str)))
    return _doc_type


@model.over('authors', '^700__')
@filter_list_values
def authors(self, key, value):
    """Translates the authors field."""
    _authors = self.get('authors', [])
    for v in force_list(value):
        temp_author = {'full_name': clean_val('a', v, str, req=True),
                       'role': mapping(AUTHOR_ROLE, clean_val('e', v, str)),
                       'affiliation': clean_val('u', v, str),
                       }
        _authors.append(temp_author)
    return _authors


@model.over('authors', '^720__')
@filter_list_values
def alt_authors(self, key, value):
    """Translates the alternative authors field."""
    _authors = self.get('authors', [])
    if _authors:
        for i, v in enumerate(force_list(value)):
            _authors[i].update({'alternative_names': clean_val('a', v, str)})
    return _authors


@model.over('corporate_authors', '^710_[a_]+')
@out_strip
def corporate_authors(self, key, value):
    """Translates the corporate authors field."""
    _corporate_authors = self.get('corporate_authors', [])
    for v in force_list(value):
        if 'a' in v:
            _corporate_authors.append(clean_val('a', v, str))
        else:
            self['collaborations'] = collaborations(self, key, value)
            raise IgnoreKey('corporate_authors')
    return _corporate_authors


@model.over('collaborations', '^710__')
@replace_in_result('Collaboration', '', key='value')
@filter_list_values
def collaborations(self, key, value):
    """Translates collaborations."""
    _collaborations = self.get('collaborations', [])
    for v in force_list(value):
        if 'g' in v:
            _collaborations.append({'value': clean_val('g', v, str)})
        elif '5' in v:
            _collaborations.append({'value': clean_val('5', v, str)})
    return _collaborations


@model.over('publication_info', '(^773__)')
@filter_list_values
def publication_info(self, key, value):
    """Translates publication_info field.

    if x and o subfields are present simultaneously
    it concatenates the text
    """
    _publication_info = self.get('publication_info', [])
    for v in force_list(value):
        temp_info = {}
        pages = clean_pages('c', v)
        if pages:
            temp_info.update(pages)
        temp_info.update({
            'journal_issue': clean_val('n', v, str),
            'journal_title': clean_val('p', v, str),
            'journal_volume': clean_val('v', v, str),
            'cnum': clean_val('w', v, str,
                              regex_format='^C\d\d-\d\d-\d\d(\.\d+)?$'),
            'year': clean_val('y', v, int),
        })

        text = '{0} {1}'.format(
            clean_val('o', v, str) or '',
            clean_val('x', v, str) or '').strip()
        if text:
            temp_info.update({'pubinfo_freetext': text})
        if temp_info:
            _publication_info.append(temp_info)
    return _publication_info


@model.over('publication_info', '^962__')
def publication_additional(self, key, value):
    """Translates additional publication info."""
    _publication_info = self.get('publication_info', [])
    empty = not bool(_publication_info)
    for i, v in enumerate(force_list(value)):
        temp_info = {}
        pages = clean_pages('k', v)
        if pages:
            temp_info.update(pages)
        rel_recid = clean_val('b', v, str)
        if rel_recid:
            temp_info.update(
                {'parent_record': {'$ref': rel_url(rel_recid)}})
        n_subfield = clean_val('n', v, str)
        if n_subfield.upper() == 'BOOK':
            temp_info.update({'material': 'BOOK'})
        else:
            temp_info.update({'cern_conference_code': n_subfield})
        if not empty and i < len(_publication_info):
            _publication_info[i].update(temp_info)
        else:
            _publication_info.append(temp_info)

    return _publication_info


@model.over('related_records', '(^775__)|(^787__)')
@filter_list_values
@for_each_value
def related_records(self, key, value):
    """Translates related_records field."""
    try:
        if key == '775__':
            clean_val('b', value, str, manual=True)
            clean_val('c', value, str, manual=True)
        if key == '787__':
            clean_val('i', value, str, manual=True)
    except ManualMigrationRequired as e:
        # TODO logs
        raise e
    return {'record': {'$ref': rel_url(clean_val('w', value, str, req=True))}}


@model.over('accelerator_experiments', '^693__')
@filter_list_values
@for_each_value
def accelerator_experiments(self, key, value):
    """Translates accelerator_experiments field."""
    return {'accelerator': clean_val('a', value, str),
            'experiment': clean_val('e', value, str),
            }


# TODO - discuss how we would like to keep links to holdings (files and ebooks)
# TODO maybe regex for links?
@model.over('urls', '^8564_')
@filter_list_values
@for_each_value
def urls(self, key, value):
    """Translates urls field."""
    try:
        clean_val('y', value, str, manual=True)
    except ManualMigrationRequired as e:
        raise e
    return {'value': clean_val('u', value, str, req=True)}


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


@model.over('dois', '^0247_')
@for_each_value
@filter_values
def dois(self, key, value):
    """Translates dois fields."""

    field_type = value.get('2')
    if field_type and field_type.lower() != 'doi':
        return

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
        raise ValueError('Field not matching the data model.', key, 'q')

    f['source'] = value.get('9')

    return f


@model.over('external_system_identifiers', '^0247_')
@for_each_value
@filter_values
def external_system_identifiers(self, key, value):
    """Translates external_system_identifiers fields."""

    field_type = value.get('2')
    if field_type and field_type.lower() != 'asin':
        return
    # FIXME schema, value required but for asin we dont have a schema
    # MOVE BELOW??
    return {
        'value': value.get('a'),
    }


@model.over('external_system_identifiers', '(^035__)|(^036__)')
@for_each_value
@filter_values
def external_system_identifiers(self, key, value):
    """Translates external_system_identifiers fields."""
    f = {}

    if key == '035__':
        field_type = value.get('9')
        if field_type and field_type.lower() == 'cercer':
            # FIXME no info provided for this
            return

    if '9' in value:
        f['schema'] = value.get('9')
    else:
        raise ValueError('Value not provided for a required field.', key, '9')

    if 'a' in value:
        f['value'] = value.get('a')
    else:
        raise ValueError('Value not provided for a required field.', key, 'a')

    return f


@model.over('report_numbers', '(^037__)(^088__)')
@for_each_value
@filter_values
def report_numbers(self, key, value):
    """Translates report_numbers fields."""

    f = {}

    if key == '037__':
        if value.get('9') == 'arXiv':
            return
        else:
            f['value'] = value.get('z')
            f['hidden'] = True

    if key == '088__':
        f['value'] = value.get('9')
        f['hidden'] = True

    if 'a' in value:
        f['value'] = value.get('a')
        f['hidden'] = True
    else:
        raise ValueError('Value not provided for a required field.', key, 'a')

    return f


@model.over('arxiv_eprints', '^037__')
@for_each_value
@filter_values
def arxiv_eprints(self, key, value):
    """Translates arxiv_eprints fields."""

    field_type = value.get('9')
    if field_type and field_type.lower() != 'arxiv':
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
@for_each_value
@filter_values
def languages(self, key, value):
    """Translates languages fields."""

    # FIXME add languages enum?
    f = {}
    _languages = value.get('languages', [])

    if 'a' in value:
        _languages.append(value.get('a'))

    f['languages'] = _languages

    return f


# @model.over('subject_classification', '(^050__)|(^080__)|(^082__)(^084__)')
# def subject_classification(self, key, value):
#     """Translates subject_classification fields."""
#     # FIXME check what is going on here
#     f = {}
#     return f


# @model.over('keywords', '^(084)__')
# def keywords(self, key, value):
#     """Translates keywords fields."""
#     # FIXME check what is going on here
#     f = {}
#     return f


@model.over('corporate_author', '^110__')
@for_each_value
@filter_values
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
# @for_each_value
# @filter_values
# def title_translations(self, key, value):
#     """Translates title_translations fields."""

#     f = {}

#     # FIXME there is no example with language. Should this be required?
#     if 'a' in value:
#         f['language'] = value.get('a')
#     else:
#         raise ValueError('Value not provided for a required field.', key, 'a')

#     if 'a' in value:
#         f['title'] = value.get('a')
#     else:
#         raise ValueError('Value not provided for a required field.', key, 'a')

#     # FIXME there is no example with source and subtitle
#     # f['source'] = value.get('a')
#     # f['subtitle'] = value.get('a')

#     return f


@model.over('editions', '^250__')
@for_each_value
@filter_values
def editions(self, key, value):
    """Translates editions fields."""

    f = {}
    _editions = value.get('editions', [])

    if 'a' in value:
        _editions.append(value.get('a'))

    f['editions'] = _editions

    return f


@model.over('imprints', '^260__')
@for_each_value
@filter_values
def imprints(self, key, value):
    """Translates imprints fields."""

    return {
        'date': value.get('c'),
        'place': value.get('a'),
        'publisher': value.get('b'),
        'reprint': value.get('g'),
    }


@model.over('preprint_date', '^269__')
@filter_values
def preprint_date(self, key, value):
    """Translates preprint_date fields."""

    return {
        'preprint_date': value.get('c'),
    }


@model.over('number_of_pages', '^300__')
@filter_values
def number_of_pages(self, key, value):
    """Translates number_of_pages fields."""

    # remove non numeric characters and cast it to int
    return {
        'number_of_pages': int(re.sub('[^0-9]', '', value.get('b'))),
    }


@model.over('book_series', '^490__')
@filter_values
def book_series(self, key, value):
    """Translates book_series fields."""

    f = {}

    if 'a' in value:
        f['title'] = value.get('a')
    else:
        raise ValueError('Value not provided for a required field.', key, 'a')

    f['volume'] = value.get('v')
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

