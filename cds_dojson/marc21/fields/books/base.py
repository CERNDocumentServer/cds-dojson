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

import datetime
import re

import pycountry
from dateutil import parser
from dojson.errors import IgnoreKey
from dojson.utils import filter_values, flatten, for_each_value, force_list

from cds_dojson.marc21.fields.books.errors import MissingRequiredField, \
    UnexpectedValue
from cds_dojson.marc21.fields.books.values_mapping import ACQUISITION_METHOD, \
    ARXIV_CATEGORIES, COLLECTION, DOCUMENT_TYPE, EXTERNAL_SYSTEM_IDENTIFIERS, \
    EXTERNAL_SYSTEM_IDENTIFIERS_TO_IGNORE, MATERIALS, MEDIUM_TYPES, \
    SUBJECT_CLASSIFICATION_EXCEPTIONS, mapping
from cds_dojson.marc21.fields.utils import ManualMigrationRequired, \
    build_contributor_books, clean_email, clean_pages_range, clean_val, \
    filter_list_values, get_week_start, out_strip, related_url, \
    replace_in_result
from cds_dojson.marc21.models.books.base import model

from .utils import extract_parts, is_excluded


@model.over('acquisition_source', '(^916__)|(^859__)|(^595__)')
@filter_values
def acquisition_source(self, key, value):
    """Translates acquisition source field."""
    _acquisition_source = self.get('acquisition_source', {})
    if key == '916__':
        date = clean_val('w', value, int, regex_format=r'\d{4}$')
        if date:
            year, week = str(date)[:4], str(date)[4:]
            date = get_week_start(int(year), int(week))
        _acquisition_source.update(
            {'datetime': str(date),
             'method': mapping(ACQUISITION_METHOD,
                               clean_val('s', value, str))})
    elif key == '859__' and 'f' in value:
        _acquisition_source.update(
            {'email': clean_email(clean_val('f', value, str))})
    elif key == '595__':
        try:
            sub_a = clean_val('a', value, str,
                              regex_format=r'[A-Z]{3}[0-9]{6}$')
            if sub_a:
                source = sub_a[:3]
                year, month = int(sub_a[3:7]), int(sub_a[7:])
                if 'datetime' in _acquisition_source:
                    raise ManualMigrationRequired(subfield='a')
                _acquisition_source.update(
                    {'datetime': datetime.date(year, month, 1).isoformat(),
                     'source': source})
        except UnexpectedValue as e:
            e.subfield = 'a'
            self['_private_notes'] = private_notes(self, key, value)
            raise IgnoreKey('acquisition_source')

    return _acquisition_source


@model.over('_private_notes', '^595__')
@filter_list_values
def private_notes(self, key, value):
    """Translates private notes field."""
    _priv_notes = self.get('_private_notes', [])

    for v in force_list(value):
        note = {'value': clean_val('a', v, str, req=True),
                'source': clean_val('9', v, str),
                }
        _priv_notes.append(note)
    return _priv_notes


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
        val_a = doc_type_mapping(clean_val('a', v, str))
        val_b = doc_type_mapping(clean_val('b', v, str))
        if val_a not in _doc_type:
            _doc_type.append(val_a)
        if val_b not in _doc_type:
            _doc_type.append(val_b)
        if 'a' in v and not val_a:
            raise UnexpectedValue(subfield='a')
        if 'b' in v and not val_b:
            raise UnexpectedValue(subfield='b')
    return _doc_type


@model.over('authors', '(^100__)|(^700__)')
@filter_list_values
def authors(self, key, value):
    """Translates the authors field."""
    _authors = self.get('authors', [])
    item = build_contributor_books(value)
    if item and item not in _authors:
        _authors.append(item)

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


@model.over('corporate_authors', '(^110)|(^710_[a_]+)')
@out_strip
def corporate_authors(self, key, value):
    """Translates the corporate authors field."""
    _corporate_authors = self.get('corporate_authors', [])

    for v in force_list(value):
        if key == '710__':
            if 'a' in v:
                _corporate_authors.append(clean_val('a', v, str))
            else:
                self['collaborations'] = collaborations(self, key, value)
                raise IgnoreKey('corporate_authors')
        else:
            _corporate_authors.append(clean_val('a', v, str))
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
        pages = clean_pages_range('c', v)
        if pages:
            temp_info.update(pages)
        temp_info.update({
            'journal_issue': clean_val('n', v, str),
            'journal_title': clean_val('p', v, str),
            'journal_volume': clean_val('v', v, str),
            'cnum': clean_val('w', v, str,
                              regex_format=r'^C\d\d-\d\d-\d\d(\.\d+)?$'),
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
        pages = clean_pages_range('k', v)
        if pages:
            temp_info.update(pages)
        rel_recid = clean_val('b', v, str)
        if rel_recid:
            temp_info.update(
                {'parent_record': {'$ref': related_url(rel_recid)}})
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
        if key == '775__':
            e.subfield = 'b or c'
        else:
            e.subfield = 'i'
        raise e
    return {'record': {
        '$ref': related_url(clean_val('w', value, str, req=True))}}


@model.over('accelerator_experiments', '^693__')
@filter_list_values
@for_each_value
def accelerator_experiments(self, key, value):
    """Translates accelerator_experiments field."""
    return {'accelerator': clean_val('a', value, str),
            'experiment': clean_val('e', value, str),
            }


# TODO - discuss how we would like to keep links to holdings (files and ebooks)
@model.over('urls', '^8564_')
@for_each_value
@filter_values
def urls(self, key, value):
    """Translates urls field."""
    try:
        clean_val('y', value, str, manual=True)
    except ManualMigrationRequired as e:
        e.subfield = 't'
        raise e
    url = clean_val('u', value, str, req=True)
    if 'cds.cern.ch' not in url:
        return {'value': url}
    # TODO: instead of IgnoreKey if link starts with cds.cern.ch it should be
    # linked as files to the record, issue #200
    raise IgnoreKey('urls')


@model.over('isbns', '^020__')
@filter_list_values
def isbns(self, key, value):
    """Translates isbns fields."""
    _isbns = self.get('isbns', [])
    for v in force_list(value):
        subfield_u = clean_val('u', v, str)
        isbn = {'value': clean_val('a', v, str) or clean_val('z', v, str)}
        if not isbn['value']:
            raise ManualMigrationRequired(subfield='a or z')
        if subfield_u:
            volume = re.search(r'(\(*v[.| ]*\d+.*\)*)', subfield_u)

            if volume:
                volume = volume.group(1)
                subfield_u = subfield_u.replace(volume, '').strip()
                existing_volume = self.get('volume')
                if existing_volume:
                    raise ManualMigrationRequired(subfield='u')
                self['volume'] = volume
            if subfield_u.upper() in MEDIUM_TYPES:
                isbn.update({'medium': subfield_u})
            else:
                isbn.update({'description': subfield_u})
        # TODO subfield C
        if isbn not in _isbns:
            _isbns.append(isbn)
    return _isbns


@model.over('standard_numbers', '^021__')
@for_each_value
@filter_values
def standard_numbers(self, key, value):
    """Translates standard numbers values."""
    a = clean_val('a', value, str)
    b = clean_val('b', value, str)
    sn = a or b
    if sn:
        return {'value': sn,
                'hidden': True if b else False}
    raise MissingRequiredField(subfield='a or b')


@model.over('external_system_identifiers', '(^0247_)|(^035__)|(^036__)')
@for_each_value
@filter_values
def external_system_identifiers(self, key, value):
    """Translates external_system_identifiers fields."""
    field_type = clean_val('2', value, str)
    sub_a = clean_val('a', value, str, req=True)
    system_id = {}

    if key == '0247_':
        if field_type and field_type.lower() == 'doi':
            self['dois'] = dois(self, key, value)
            raise IgnoreKey('external_system_identifiers')
        elif field_type and field_type.lower() == 'asin':
            system_id.update({'value': sub_a,
                              'schema': 'ASIN'})
        else:
            raise UnexpectedValue(subfield='2')
    if key == '035__':
        sub_9 = clean_val('9', value, str, req=True)
        if sub_9.upper() == 'INSPIRE-CNUM':
            _conference_info = self.get('conference_info', {})
            _conference_info.update({'inspire_cnum': sub_a})
            self['conference_info'] = _conference_info
            raise IgnoreKey('external_system_identifiers')
        elif sub_9.upper() in EXTERNAL_SYSTEM_IDENTIFIERS:
            system_id.update({'value': sub_a,
                              'schema': sub_9})
        elif sub_9.upper() in EXTERNAL_SYSTEM_IDENTIFIERS_TO_IGNORE:
            raise IgnoreKey('external_system_identifiers')
        else:
            raise UnexpectedValue(subfield='9')
    if key == '036__':
        system_id.update({'value': sub_a,
                          'schema': clean_val('9', value, str, req=True)})
    return system_id


@model.over('dois', '^0247_')
@filter_list_values
def dois(self, key, value):
    """Translates dois fields.

    This is holding specific. To move to holding.py
    """
    _dois = self.get('dois', [])
    for v in force_list(value):
        material = mapping(MATERIALS,
                           clean_val('q', v, str, transform='lower'),
                           raise_exception=True)

        _dois.append({'value': clean_val('a', v, str, req=True),
                      'material': material,
                      'source': clean_val('9', v, str),
                      })
    return _dois


@model.over('report_numbers', '(^037__)|(^088__)')
@for_each_value
@filter_values
def report_numbers(self, key, value):
    """Translates report_numbers fields."""
    def get_value_rn(f_a, f_z, f_9, rn_obj):
        f.update({'value': f_a or f_z or f_9})
        if f_z or f_9:
            rn_obj.update({'hidden': True})

    f = {}
    sub_9 = clean_val('9', value, str)
    sub_a = clean_val('a', value, str)
    sub_z = clean_val('z', value, str)

    if not (sub_z or sub_a or sub_9):
        raise MissingRequiredField(subfield='9 or a or z')

    if key == '037__':
        if sub_9 == 'arXiv':
            self['arxiv_eprints'] = arxiv_eprints(self, key, value)
            raise IgnoreKey('report_numbers')
        else:
            get_value_rn(sub_a, sub_z, sub_9, f)

    if key == '088__':
        get_value_rn(sub_a, sub_z, sub_9, f)

    return f


@model.over('arxiv_eprints', '(^037__)|(^695__)')
@filter_list_values
def arxiv_eprints(self, key, value):
    """Translates arxiv_eprints fields."""
    def check_category(field, val):
        category = clean_val(field, val, str)
        if category:
            if category in ARXIV_CATEGORIES:
                return category
            raise UnexpectedValue(subfield=field)

    if key == '037__':
        _arxiv_eprints = self.get('arxiv_eprints', [])
        for v in force_list(value):
            eprint_id = clean_val('a', v, str, req=True)
            duplicated = [
                elem
                for i, elem in enumerate(_arxiv_eprints)
                if elem['value'] == eprint_id
            ]
            category = check_category('c', v)
            if not duplicated:
                eprint = {'value': eprint_id}
                if category:
                    eprint.update({'categories': [category]})
                _arxiv_eprints.append(eprint)
            else:
                duplicated[0]['categories'].append(category)
        return _arxiv_eprints

    if key == '695__':
        _arxiv_eprints = self.get('arxiv_eprints', [])
        category = check_category('a', value)
        if not _arxiv_eprints:
            raise ManualMigrationRequired(message='037__ is missing')
        if clean_val('9', value, str) != 'LANL EDS':
            raise UnexpectedValue(subfield='9')
        _entry = _arxiv_eprints[0]
        if category in _entry['categories']:
            raise IgnoreKey('arxiv_eprints')
        _entry['categories'].append(category)
        return _arxiv_eprints


@model.over('languages', '^041__')
@for_each_value
@out_strip
def languages(self, key, value):
    """Translates languages fields."""
    lang = clean_val('a', value, str).lower()
    try:
        return pycountry.languages.lookup(lang).alpha_2
    except (KeyError, AttributeError, LookupError):
        raise UnexpectedValue(subfield='a')


@model.over('subject_classification',
            '(^050_4)|(^080__)|(^08204)|(^084__)|(^082__)')
@for_each_value
@out_strip
def subject_classification(self, key, value):
    """Translates subject classification field."""
    _subject_classification = {'value': clean_val('a', value, str, req=True)}
    if key == '080__':
        _subject_classification.update({'schema': 'UDC'})
    elif key == '08204' or key == '082__':
        _subject_classification.update({'schema': 'Dewey'})
    elif key == '084__':
        sub_2 = clean_val('2', value, str)
        if sub_2 and sub_2.upper() in SUBJECT_CLASSIFICATION_EXCEPTIONS:
            self['keywords'] = keywords(self, key, value)
            raise IgnoreKey('subject_classification')
        else:
            _subject_classification.update({'schema': 'ICS'})
    elif key == '050_4':
        _subject_classification.update({'schema': 'LoC'})

    return _subject_classification


@model.over('keywords', '(^084__)|(^6531_)')
@filter_list_values
def keywords(self, key, value):
    """Keywords."""
    _keywords = self.get('keywords', [])
    for v in force_list(value):
        if key == '084__':
            sub_2 = clean_val('2', value, str)
            if sub_2 and sub_2 == 'PACS':
                _keywords.append({
                    'name': clean_val('a', v, str, req=True),
                    'provenance': 'PACS',
                })
            else:
                raise IgnoreKey('keywords')
        elif key == '6531_':
            _keywords.append({
                'name': clean_val('a', value, str),
                'provenance': value.get('9') or value.get('g'),  # Easier to solve here
            })

    return _keywords


@model.over('conference_info', '(^111__)|(^270__)|(^711__)')
@filter_values
def conference_info(self, key, value):
    """Translates conference info."""
    _conference_info = self.get('conference_info', {})
    for v in force_list(value):
        if key == '111__':
            try:
                opening_date = parser.parse(clean_val('9', v, str, req=True))
                closing_date = parser.parse(clean_val('z', v, str, req=True))
            except ValueError:
                raise UnexpectedValue(subfield='9 or z')
            country_code = clean_val('w', v, str)
            if country_code:
                try:
                    country_code = str(pycountry.countries.get(
                        alpha_2=country_code).alpha_2)
                except (KeyError, AttributeError):
                    raise UnexpectedValue(subfield='w')

            _conference_info.update({
                'title': clean_val('a', v, str, req=True),
                'place': clean_val('c', v, str, req=True),
                'opening_date': opening_date.date().isoformat(),
                'closing_date': closing_date.date().isoformat(),
                'cern_conference_code': clean_val('g', v, str),
                'series_number': clean_val('n', v, int),
                'country_code': country_code,
            })
        elif key == '270__':
            contact = clean_email(clean_val('m', v, str))
            if contact and _conference_info:
                _conference_info.update({'contact': contact})
            else:
                raise MissingRequiredField(subfield='m')
        else:
            _conference_info.update({
                'conference_acronym': clean_val('a', v, str)})
    return _conference_info


@model.over('title_translations', '^242__')
@for_each_value
@filter_values
def title_translations(self, key, value):
    """Translates title translations."""
    return {
        'title': clean_val('a', value, str, req=True),
        'language': 'en',
        'subtitle': clean_val('b', value, str),
    }


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


@model.over('editions', '^250__')
@out_strip
@for_each_value
def editions(self, key, value):
    """Translates editions fields."""
    return clean_val('a', value, str)


@model.over('imprints', '^260__')
@for_each_value
@filter_values
def imprints(self, key, value):
    """Translates imprints fields."""
    reprint = clean_val('g', value, str)
    if reprint:
        reprint = reprint.lower().replace('repr.', '').strip()

    return {
        'date': clean_val('c', value, str),
        'place': clean_val('a', value, str),
        'publisher': clean_val('b', value, str),
        'reprint': reprint,
    }


@model.over('preprint_date', '^269__')     # item, RDM?!
@out_strip
def preprint_date(self, key, value):
    """Translates preprint_date fields."""
    date = clean_val('c', value, str)
    if date:
        try:
            date = parser.parse(date)
            return date.date().isoformat()
        except (ValueError, AttributeError):
            raise ManualMigrationRequired(subfield='c')
    else:
        raise IgnoreKey('preprint_date')


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


@model.over('book_series', '^490__')
@for_each_value
@filter_values
def book_series(self, key, value):
    """Translates book series field."""
    return {
        'title': clean_val('a', value, str),
        'volume': clean_val('v', value, str),
        'issn': clean_val('x', value, str),
    }


@model.over('public_notes', '^500__')
@for_each_value
@filter_values
def public_notes(self, key, value):
    """Translates public notes."""
    return {
        'value': clean_val('a', value, str, req=True),
        'source': clean_val('9', value, str)
    }


@model.over('abstracts', '^520__')
@for_each_value
@filter_values
def abstracts(self, key, value):
    """Translates abstracts fields."""
    return {
        'value': clean_val('a', value, str, req=True),
        'source': clean_val('9', value, str)
    }


@model.over('funding_info', '^536__')
@for_each_value
@filter_values
def funding_info(self, key, value):
    """Translates funding_info fields."""
    openaccess = clean_val('r', value, str)
    if openaccess and openaccess.lower() == 'openaccess':
        openaccess = True
    elif openaccess and openaccess.lower() != 'openaccess':
        raise UnexpectedValue(subfield='r')
    else:
        openaccess = None

    return {'agency': clean_val('a', value, str),
            'grant_number': clean_val('c', value, str),
            'project_number': clean_val('f', value, str),
            'openaccess': openaccess,
            }


@model.over('licenses', '^540__')
@for_each_value
@filter_values
def licenses(self, key, value):
    """Translates license fields."""
    material = mapping(MATERIALS,
                       clean_val('3', value, str, transform='lower'),
                       raise_exception=True)

    return {
        'material': material,
        'license': clean_val('a', value, str),
        'imposing': clean_val('b', value, str),
        'url': clean_val('u', value, str),
        'funder': clean_val('f', value, str),
        'admin_info': clean_val('g', value, str),
    }


@model.over('copyrights', '^542__')
@for_each_value
@filter_values
def copyright(self, key, value):
    """Translates copyright fields."""
    material = mapping(MATERIALS,
                       clean_val('3', value, str, transform='lower'),
                       raise_exception=True)

    return {
        'material': material,
        'holder': clean_val('d', value, str),
        'statement': clean_val('f', value, str),
        'year': clean_val('g', value, int),
        'url': clean_val('u', value, str),
    }


@model.over('table_of_content', '(^505__)|(^5050_)')
@out_strip
@flatten
@for_each_value
def table_of_content(self, key, value):
    """Translates table of content field."""
    text = '{0} -- {1}'.format(
        clean_val('a', value, str) or '',
        clean_val('t', value, str) or '').strip()
    if text != '--':
        chapters = re.split(r'; | -- |--', text)
        return chapters
    else:
        raise UnexpectedValue(subfield='a or t')
