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

import re

from dojson.errors import IgnoreKey
from dojson.utils import force_list

from cds_dojson.marc21.fields.books.values_mapping import mapping, \
    DOCUMENT_TYPE, AUTHOR_ROLE, COLLECTION
from cds_dojson.marc21.fields.utils import clean_email, filter_list_values, \
    out_strip, UnexpectedValue, clean_val, \
    ManualMigrationRequired, replace_in_result

from cds_dojson.marc21.fields.utils import get_week_start
from ...models.books.book import model


@model.over('acquisition_source', '(^916__)|(^859__)')
def acquisition_source(self, key, value):
    """Translates acquisition source field"""
    _acquisition_source = self.get('acquisition_source', {})
    if key == '916__':
        date_num = clean_val('w', value, int, regex_format=r'\d{4}$')
        year, week = str(date_num)[:4], str(date_num)[4:]
        datetime = get_week_start(int(year), int(week))
        _acquisition_source.update({'datetime': str(datetime)})
    elif key == '859__' and 'f' in value:
        _acquisition_source.update(
            {'email': clean_email(clean_val('f', value, str))})
    return _acquisition_source


@model.over('_collections', '(^980__)|(^690C_)|(^697C_)')
@out_strip
def collection(self, key, value):
    """ Translates collection field - WARNING - also document type field """

    _collections = self.get('_collections', [])

    def collection_mapping(val):
        if val:
            return mapping(COLLECTION, val)

    for v in force_list(value):
        result_a = collection_mapping(clean_val('a', v, str))
        result_b = collection_mapping(clean_val('b', v, str))
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
    """Translates document type field"""
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
    _authors = self.get('authors', [])
    for v in force_list(value):
        _authors.append({'full_name': clean_val('a', v, str, req=True),
                         'role': mapping(AUTHOR_ROLE,
                                         clean_val('e', v, str)),
                         'affiliation': clean_val('u', v, str),
                         })
    return _authors


@model.over('corporate_authors', '^710_[a_]+')
@out_strip
def corporate_authors(self, key, value):
    _corporate_authors = self.get('corporate_authors', [])
    for v in force_list(value):
        if 'a' in v:
            _corporate_authors.append(clean_val('a', v, str))
        else:
            self['collaborations'] = collaborations(self, key, value)
            raise IgnoreKey('corporate_authors')
    return _corporate_authors


@model.over('collaborations', '^(710__)')
@replace_in_result('Collaboration', '', key='value')
@filter_list_values
def collaborations(self, key, value):
    _collaborations = self.get('collaborations', [])
    for v in force_list(value):
        if 'g' in v:
            _collaborations.append({'value': clean_val('g', v, str)})
        elif '5' in v:
            _collaborations.append({'value': clean_val('5', v, str)})
    return _collaborations


# TODO not sure yet if x and o can happen in the same time and if
# TODO the text is a concatenation of those two
@model.over('publication_info', '^773__')
@filter_list_values
def publication_info(self, key, value):
    _publication_info = self.get('publication_info', [])
    for v in force_list(value):
        temp_info = {}
        pages_val = clean_val('c', v, str,
                              regex_format='\d+(?:[\-‐‑‒–—―⁻₋−﹘﹣－]\d+)+')
        if pages_val:
            pages = re.split('[\-‐‑‒–—―⁻₋−﹘﹣－]+',
                             str(v.get('c', '')))
            if len(pages) != 2:
                raise UnexpectedValue
            temp_info.update({'page_start': int(pages[0]),
                              'page_end': int(pages[1])})

        temp_info.update({
            'journal_issue': clean_val('n', v, str),
            'journal_title': clean_val('p', v, str),
            'cnum': clean_val('w', v, str),
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


@model.over('related_records', '(^775__)|(^787__)')
@filter_list_values
def related_records(self, key, value):
    _related_records = self.get('related_records', [])
    for v in force_list(value):
        try:
            if key == '775__':
                clean_val('b', v, str, manual=True)
                clean_val('c', v, str, manual=True)
            if key == '787__':
                clean_val('i', v, str, manual=True)
        except ManualMigrationRequired:
            # TODO log
            pass
        _related_records.append(
            {'record': clean_val('w', v, str, req=True)})
    return _related_records


@model.over('accelerator_experiments', '^693__')
@filter_list_values
def accelerator_experiments(self, key, value):
    _acc_exp = self.get('accelerator_experiments', [])
    for v in force_list(value):
        _acc_exp.append({'accelerator': clean_val('a', v, str),
                         'experiment': clean_val('e', v, str)
                         })
    return _acc_exp


# TODO - discuss how we would like to keep links to holdings (files and ebooks)
# TODO maybe regex for links?
@model.over('urls', '^8564_')
@filter_list_values
def urls(self, key, value):
    _urls = self.get('urls', [])
    for v in force_list(value):
        _urls.append({'value': clean_val('u', v, str, req=True)})
        try:
            clean_val('y', v, str, manual=True)
        except ManualMigrationRequired:
            # TODO log
            pass
    return _urls


