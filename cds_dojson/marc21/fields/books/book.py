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

import pycountry
from dateutil import parser
import datetime
from dojson.errors import IgnoreKey

import re
from dojson.utils import force_list, for_each_value, filter_values, flatten

from cds_dojson.marc21.fields.books.errors import UnexpectedValue, \
    MissingRequiredField
from cds_dojson.marc21.fields.books.values_mapping import mapping, \
    DOCUMENT_TYPE, AUTHOR_ROLE, COLLECTION, ACQUISITION_METHOD, MEDIUM_TYPES, \
    ARXIV_CATEGORIES, MATERIALS
from cds_dojson.marc21.fields.utils import clean_email, filter_list_values, \
    out_strip, clean_val, \
    ManualMigrationRequired, replace_in_result, rel_url, clean_pages

from cds_dojson.marc21.fields.utils import get_week_start
from ...models.books.book import model


@model.over('acquisition_source', '(^916__)|(^859__)|(^595__)')
@filter_values
def acquisition_source(self, key, value):
    """Translates acquisition source field."""
    _acquisition_source = self.get('acquisition_source', {})
    if key == '916__':
        date_num = clean_val('w', value, int, regex_format=r'\d{4}$')
        year, week = str(date_num)[:4], str(date_num)[4:]
        acq_date = get_week_start(int(year), int(week))
        _acquisition_source.update(
            {'datetime': str(acq_date),
             'method': mapping(ACQUISITION_METHOD,
                               clean_val('s', value, str))})
    elif key == '859__' and 'f' in value:
        _acquisition_source.update(
            {'email': clean_email(clean_val('f', value, str))})
    elif key == '595__':
        try:
            sub_a = clean_val('a', value, str,
                              regex_format=r'[A-Z]{3}[0-9]{6}$')
            source = sub_a[:3]
            year, month = int(sub_a[3:7]), int(sub_a[7:])
            if 'datetime' in _acquisition_source:
                raise ManualMigrationRequired
            _acquisition_source.update(
                {'datetime': datetime.date(year, month, 1).isoformat(),
                 'source': source or clean_val('9', value, str)})
        except UnexpectedValue as e:
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
        _doc_type.append(doc_type_mapping(clean_val('a', v, str)))
        _doc_type.append(doc_type_mapping(clean_val('b', v, str)))
    return _doc_type


@model.over('authors', '(^100__)|(^700__)')
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
@for_each_value
@filter_values
def urls(self, key, value):
    """Translates urls field."""
    try:
        clean_val('y', value, str, manual=True)
    except ManualMigrationRequired as e:
        raise e
    return {'value': clean_val('u', value, str, req=True)}


@model.over('isbns', '^020__')
@filter_list_values
def isbns(self, key, value):
    """Translates isbns fields."""
    _isbns = self.get('isbns', [])
    for v in force_list(value):
        subfield_u = clean_val('u', v, str)
        isbn = {'value': clean_val('a', v, str) or clean_val('z', v, str)}
        if not isbn['value']:
            raise ManualMigrationRequired
        if subfield_u:
            volume = re.search(r'(\(*v[.| ]*\d+.*\)*)', subfield_u)

            if volume:
                volume = volume.group(1)
                subfield_u = subfield_u.replace(volume, '').strip()
                existing_volume = self.get('volume')
                if existing_volume:
                    raise ManualMigrationRequired
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
                'hidden': True if b else None}
    raise MissingRequiredField


@model.over('external_system_identifiers', '(^0247_)|(^035__)|(^036__)')
@for_each_value
@filter_values
def external_system_identifiers(self, key, value):
    """Translates external_system_identifiers fields."""
    field_type = clean_val('2', value, str)

    system_id = {}
    if key == '0247_':
        if field_type and field_type.lower() == 'doi':
            self['dois'] = dois(self, key, value)
            raise IgnoreKey('external_system_identifiers')
        elif field_type and field_type.lower() == 'asin':
            system_id.update({'value': clean_val('a', value, str, req=True),
                              'schema': clean_val('9', value, str, req=True),
                              })
        else:
            raise UnexpectedValue
    if key == '035__':
        sub_9 = clean_val('9', value, str, req=True)
        sub_a = clean_val('a', value, str, req=True)
        if 'inspire-cnum' == sub_9.lower() or 'inspirecnum' == sub_9.lower():
            # TODO check this
            self['inspire_cnum'] = sub_a
            raise IgnoreKey('external_system_identifiers')
        elif 'CERCER' not in sub_9:
            system_id.update({'value': sub_a,
                              'schema': sub_9})
        else:
            # TODO check with CDS
            raise ManualMigrationRequired
    if key == '036__':
        system_id.update({'value': clean_val('a', value, str, req=True),
                          'schema': clean_val('9', value, str, req=True),
                          })
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
        raise MissingRequiredField

    if key == '037__':
        if sub_9 == 'arXiv':
            self['arxiv_eprints'] = arxiv_eprints(self, key, value)
            raise IgnoreKey('report_numbers')
        else:
            get_value_rn(sub_a, sub_z, sub_9, f)

    if key == '088__':
        get_value_rn(sub_a, sub_z, sub_9, f)

    return f


@model.over('arxiv_eprints', '^037__')
@filter_list_values
def arxiv_eprints(self, key, value):
    """Translates arxiv_eprints fields."""
    def check_category(v):
        sub_c = clean_val('c', v, str)
        if sub_c:
            if sub_c in ARXIV_CATEGORIES:
                return sub_c
            else:
                raise UnexpectedValue

    _arxiv_eprints = self.get('arxiv_eprints', [])
    for v in force_list(value):
        eprint_id = clean_val('a', v, str, req=True)
        duplicated = [elem for i, elem in enumerate(_arxiv_eprints)
                      if elem['value'] == eprint_id]
        if not duplicated:
            eprint = {'value': eprint_id}
            sub_c = check_category(v)
            if sub_c:
                eprint.update({'categories': [sub_c]})
            _arxiv_eprints.append(eprint)
        else:
            sub_c = check_category(v)
            duplicated[0]['categories'].append(sub_c)

    return _arxiv_eprints


@model.over('languages', '^041__')
@for_each_value
@out_strip
def languages(self, key, value):
    """Translates languages fields."""
    lang = clean_val('a', value, str).lower()
    try:
        iso_lang = pycountry.languages.get(alpha_3=lang).alpha_2
    except (KeyError, AttributeError):
        raise UnexpectedValue

    return iso_lang


@model.over('conference_info', '(^111__)|(^270__)')
@filter_list_values
def conference_info(self, key, value):
    """Translates conference info."""
    _conference_info = self.get('conference_info', [])
    for v in force_list(value):
        if key == '111__':
            try:
                opening_date = parser.parse(clean_val('9', v, str, req=True))
                closing_date = parser.parse(clean_val('z', v, str, req=True))
            except ValueError:
                raise UnexpectedValue
            country_code = clean_val('w', v, str)
            if country_code:
                try:
                    country_code = str(pycountry.countries.get(
                        alpha_2=country_code).alpha_2)
                except (KeyError, AttributeError):
                    raise UnexpectedValue

            _conference_info.append({
                'title': clean_val('a', v, str, req=True),
                'place': clean_val('c', v, str, req=True),
                'opening_date': opening_date.date().isoformat(),
                'closing_date': closing_date.date().isoformat(),
                'cern_conference_code': clean_val('g', v, str),
                'series_number': clean_val('n', v, int),
                'country_code': country_code,
            })
        else:
            contact = clean_email(clean_val('m', v, str))
            if contact and _conference_info:
                _conference_info[-1].update({'contact': contact})
            else:
                raise MissingRequiredField
    return _conference_info


@model.over('title_translations', '(^242__)|(^246__)')
@for_each_value
@filter_values
def title_translations(self, key, value):
    """Translates title translations."""
    # TODO n, p of 246 subfields will be migrated as books series references
    return {
        'title': clean_val('a', value, str, req=True),
        'language': 'en',
        'subtitle': clean_val('b', value, str),
    }


@model.over('titles', '^245__')
@for_each_value
@filter_values
def titles(self, key, value):
    """Translates titles."""
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


@model.over('preprint_date', '^269__')
@out_strip
def preprint_date(self, key, value):
    """Translates preprint_date fields."""
    date = clean_val('c', value, str)
    if date:
        try:
            date = parser.parse(date)
            return date.date().isoformat()
        except (ValueError, AttributeError):
            raise ManualMigrationRequired
    else:
        raise IgnoreKey('preprint_date')


@model.over('number_of_pages', '^300__')
def number_of_pages(self, key, value):
    """Translates number_of_pages fields."""
    pages = clean_val('a', value, str)
    if not pages:
        raise IgnoreKey('number_of_pages')
    pages = re.search('(^[0-9]+) *p', pages)
    if pages:
        pages = int(pages.group(1))
        return pages
    raise UnexpectedValue


@model.over('public_notes', '^500__')
@for_each_value
@out_strip
def public_notes(self, key, value):
    """Translates public notes."""
    return clean_val('a', value, str)


@model.over('abstracts', '^520__')
@for_each_value
@out_strip
def abstracts(self, key, value):
    """Translates abstracts fields."""
    return clean_val('a', value, str)


@model.over('funding_info', '^536__')
@for_each_value
@filter_values
def funding_info(self, key, value):
    """Translates funding_info fields."""
    openaccess = clean_val('r', value, str)
    if openaccess and openaccess.lower() == 'openaccess':
        openaccess = True
    elif openaccess and openaccess.lower() != 'openaccess':
        raise UnexpectedValue
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
        raise UnexpectedValue
