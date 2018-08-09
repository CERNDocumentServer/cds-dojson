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
from dojson.utils import force_list, filter_values, for_each_value

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
