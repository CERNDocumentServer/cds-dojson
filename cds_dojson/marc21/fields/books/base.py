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
from dateutil.parser import ParserError
from dojson.errors import IgnoreKey
from dojson.utils import filter_values, flatten, for_each_value, force_list

from cds_dojson.marc21.fields.books.errors import MissingRequiredField, \
    UnexpectedValue
from cds_dojson.marc21.fields.books.utils import extract_volume_number
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


@model.over('legacy_recid', '^001')
def recid(self, key, value):
    """Record Identifier."""
    return int(value)


@model.over('agency_code', '^003')
def agency_code(self, key, value):
    """Control number identifier."""
    return 'SzGeCERN'


@model.over('created_by', '^859__')
@filter_values
def created_by(self, key, value):
    """Translates created_by to find submitter."""
    return {'_email': clean_email(clean_val('f', value, str)), 'type': "user"}


@model.over('_created', '(^916__)|(^595__)')
@out_strip
def created(self, key, value):
    """Translates created information to fields."""
    _created_by = self.get('created_by', {})

    if key == '916__':
        if 's' in value:
            _created_by.update(
                {'type': mapping(ACQUISITION_METHOD,
                                 clean_val('s', value, str))})
            self['created_by'] = _created_by
        date = clean_val('w', value, int, regex_format=r'\d{4}$')
        if date:
            year, week = str(date)[:4], str(date)[4:]
            date = get_week_start(int(year), int(week))
            return date.isoformat()
    elif key == '595__':
        try:
            sub_a = clean_val('a', value, str,
                              regex_format=r'[A-Z]{3}[0-9]{6}$')
            if sub_a:
                source = sub_a[:3]
                self["source"] = source
                year, month = int(sub_a[3:7]), int(sub_a[7:])
                return datetime.date(year, month, 1).isoformat()
        except UnexpectedValue as e:
            e.subfield = 'a'
            self['internal_notes'] = internal_notes(self, key, value)
            raise IgnoreKey('_created')

    raise IgnoreKey('_created')


@model.over('internal_notes', '^595__')
@filter_list_values
def internal_notes(self, key, value):
    """Translates private notes field."""
    _internal_notes = self.get('internal_notes', [])

    for v in force_list(value):
        note = {'value': clean_val('a', v, str, req=True),
                # TODO, waiting for an answer
                'source': clean_val('9', v, str),
                }
        _internal_notes.append(note)
    return _internal_notes


# TODO convert to tags
@model.over('_migration', '(^980__)|(^690C_)|(^697C_)')
@out_strip
def collection(self, key, value):
    """Translates collection field - WARNING - also document type field."""
    _migration = self.get('_migration', {})
    _tags = _migration.get('tags', [])

    for v in force_list(value):
        result_a = mapping(COLLECTION, clean_val('a', v, str))
        result_b = mapping(COLLECTION, clean_val('b', v, str))
        if result_a:
            _tags.append(result_a)
            _migration['has_tags'] = True
        if result_b:
            _tags.append(result_b)
            _migration['has_tags'] = True
        if not result_a and not result_b:
            self['document_type'] = document_type(self, key, value)
            raise IgnoreKey('_migration')
    _migration['tags'] = _tags
    return _migration


@model.over('document_type', '(^980__)|(^960__)|(^690C_)')
@out_strip
def document_type(self, key, value):
    """Translates document type field."""
    _doc_type = self.get('document_type', {})

    def doc_type_mapping(val):
        if val:
            return mapping(DOCUMENT_TYPE, val)

    for v in force_list(value):
        val_a = doc_type_mapping(clean_val('a', v, str))
        val_b = doc_type_mapping(clean_val('b', v, str))

        if not val_a and not val_b and not _doc_type:
            raise UnexpectedValue(subfield='a')

        if val_a and val_b and (val_a != val_b != _doc_type):
            raise ManualMigrationRequired(subfield='a or b - '
                                                   'inconsistent doc type')
        if val_a:
            if _doc_type and _doc_type != val_a:
                raise ManualMigrationRequired(subfield='a'
                                                       'inconsistent doc type')
            _doc_type = val_a
        if val_b:
            if _doc_type and _doc_type != val_a:
                raise ManualMigrationRequired(subfield='b'
                                                       'inconsistent doc type')
            _doc_type = val_b
    return _doc_type


@model.over('authors', '(^100__)|(^700__)')
@filter_list_values
def authors(self, key, value):
    """Translates the authors field."""
    _authors = self.get('authors', [])
    item = build_contributor_books(value)
    if item and item not in _authors:
        _authors.append(item)
    try:
        if 'u' in value:
            other = ['et al.', 'et al']
            val_u = list(force_list(value.get('u')))
            if [i for i in other if i in val_u]:
                self['other_authors'] = True
    except UnexpectedValue:
        pass
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


@model.over('authors', '(^110)|(^710_[a_]+)')
@filter_list_values
def corporate_authors(self, key, value):
    """Translates the corporate authors field."""
    _corporate_authors = self.get('authors', [])

    for v in force_list(value):
        if key == '710__':
            if 'a' in v:
                _corporate_authors.append({'full_name': clean_val('a', v, str),
                                           'type': 'ORGANISATION'})
            else:
                self['authors'] = collaborations(self, key, value)
                raise IgnoreKey('corporate_authors')
        else:
            _corporate_authors.append({'full_name': clean_val('a', v, str),
                                       'type': 'ORGANISATION'})
    return _corporate_authors


@model.over('authors', '^710__')
@replace_in_result('Collaboration', '', key='full_name')
@filter_list_values
def collaborations(self, key, value):
    """Translates collaborations."""
    _authors = self.get('authors', [])
    for v in force_list(value):
        if 'g' in v:
            _authors.append({'full_name': clean_val('g', v, str),
                             'type': 'ORGANISATION'})
        elif '5' in v:
            _authors.append({'full_name': clean_val('5', v, str),
                             'type': 'ORGANISATION'})
    return _authors


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
            'year': clean_val('y', v, int),
        })

        text = '{0} {1}'.format(
            clean_val('o', v, str) or '',
            clean_val('x', v, str) or '').strip()
        if text:
            temp_info.update({'note': text})
        if temp_info:
            _publication_info.append(temp_info)
    return _publication_info


@model.over('publication_info', '^962__')
def publication_additional(self, key, value):
    """Translates additional publication info."""
    _publication_info = self.get('publication_info', [])
    _migration = self.get("_migration", {})
    empty = not bool(_publication_info)
    for i, v in enumerate(force_list(value)):
        temp_info = {}
        pages = clean_pages_range('k', v)
        if pages:
            temp_info.update(pages)
        rel_recid = clean_val('b', v, str)
        if rel_recid:
            _migration["journal_record_legacy_recid"] = rel_recid
            _migration["has_journal"] = True
            # assume that if we have a parent journal
            # then the doc is a periodical issue
            self['document_type'] = 'PERIODICAL_ISSUE'
            self['_migration'] = _migration
        n_subfield = clean_val('n', v, str)
        if n_subfield.upper() == 'BOOK':
            temp_info.update({'material': 'BOOK'})
        else:
            _conference_info = self.get('conference_info', {})
            _identifiers = _conference_info.get('identifiers', [])
            conf_id = {"scheme": "CERN_CODE", "value": n_subfield}
            _identifiers.append(conf_id)
            _conference_info["identifiers"] = _identifiers
            self["conference_info"] = _conference_info
        if not empty and i < len(_publication_info):
            _publication_info[i].update(temp_info)
        else:
            _publication_info.append(temp_info)

    return _publication_info


# cleaning data, later
@model.over('_migration', '(^775__)|(^787__)')
@out_strip
def related_records(self, key, value):
    """Translates related_records field.

    RELATED records
    """
    _migration = self.get('_migration', {})
    _related = _migration.get('related', [])
    relation_type = 'other'
    try:
        if key == '775__' and 'b' in value:
            relation_type = clean_val('b', value, str)
        if key == '787__' and 'i' in value:
            clean_val('i', value, str, manual=True)
        _related.append({'related_recid': clean_val('w', value, str, req=True),
                         'relation_type': relation_type
                         })
        _migration.update({'related': _related, 'has_related': True})
        return _migration
    except ManualMigrationRequired as e:
        if key == '775__':
            e.subfield = 'b or c'
        else:
            e.subfield = 'i'
        raise e


@model.over('extensions', '^693__')
@filter_list_values
@for_each_value
def accelerator_experiments(self, key, value):
    """Translates accelerator_experiments field."""
    return {'unit:accelerator': clean_val('a', value, str),
            'unit:experiment': clean_val('e', value, str),
            'unit:project': clean_val('p', value, str)
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


@model.over('identifiers', '^020__', )
@filter_list_values
def isbns(self, key, value):
    """Translates isbns fields."""
    _isbns = self.get('identifiers', [])
    for v in force_list(value):
        subfield_u = clean_val('u', v, str)
        isbn = {'value': clean_val('a', v, str) or clean_val('z', v, str),
                'scheme': 'ISBN',
                }
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
                # TODO volume --> when splitting to series
                self['volume'] = volume
            if subfield_u.upper() in MEDIUM_TYPES:
                isbn.update({'medium': subfield_u})
            else:
                isbn.update({'description': subfield_u})
        # TODO subfield C
        if isbn not in _isbns:
            _isbns.append(isbn)
    return _isbns


@model.over('identifiers', '^021__')
@filter_list_values
def standard_numbers(self, key, value):
    """Translates standard numbers values."""
    _identifiers = self.get('identifiers', [])
    a = clean_val('a', value, str)
    b = clean_val('b', value, str)
    sn = a or b
    if sn:
        _identifiers.append({'value': sn,
                             'scheme': 'STANDARD_NUMBER',
                             'hidden': True if b else False})
        return _identifiers
    raise MissingRequiredField(subfield='a or b')


@model.over('alternative_identifiers', '(^0247_)|(^035__)|(^036__)')
@for_each_value
@filter_values
def alternative_identifiers(self, key, value):
    """Translates external_system_identifiers fields."""
    field_type = clean_val('2', value, str)
    sub_a = clean_val('a', value, str, req=True)
    indentifier_entry = {}
    if key == '0247_':
        if field_type and field_type.lower() == 'doi':
            # if 0247__2 == doi it is a DOI identifier
            self['identifiers'] = dois(self, key, value)
            raise IgnoreKey('alternative_identifiers')
        elif field_type and field_type.lower() == 'asin':
            indentifier_entry.update({'value': sub_a,
                                      'scheme': 'ASIN'})
        else:
            raise UnexpectedValue(subfield='2')
    if key == '035__':
        sub_9 = clean_val('9', value, str, req=True)

        # conference_info.identifiers mixed data
        if sub_9.upper() == 'INSPIRE-CNUM':
            _conference_info = self.get('conference_info', {})
            _prev_identifiers = _conference_info.get('identifiers', [])
            _prev_identifiers.append(
                {'scheme': 'INSPIRE_CNUM', 'value': sub_a})
            _conference_info.update({'identifiers': _prev_identifiers})
            self['conference_info'] = _conference_info
            raise IgnoreKey('external_system_identifiers')

        elif sub_9.upper() in EXTERNAL_SYSTEM_IDENTIFIERS:
            indentifier_entry.update({'value': sub_a,
                                      'scheme': sub_9})
        elif sub_9.upper() in EXTERNAL_SYSTEM_IDENTIFIERS_TO_IGNORE:
            raise IgnoreKey('external_system_identifiers')
        else:
            raise UnexpectedValue(subfield='9')
    if key == '036__':
        indentifier_entry.update({
            'value': sub_a, 'scheme': clean_val('9', value, str, req=True)})
    return indentifier_entry


@model.over('identifiers', '^0247_')
@filter_list_values
def dois(self, key, value):
    """Translates dois fields."""
    # TODO might be moved to item level or prefixed _migration,
    # decision pending
    _identifiers = self.get('identifiers', [])
    for v in force_list(value):
        material = mapping(MATERIALS,
                           clean_val('q', v, str, transform='lower'),
                           raise_exception=True)

        _identifiers.append(
            {
                'value': clean_val('a', v, str, req=True),
                'material': material,
                'source': clean_val('9', v, str),  # TODO sources
                'scheme': 'DOI',
            }
        )
    return _identifiers


@model.over('identifiers', '(^037__)|(^088__)')
@filter_list_values
def report_numbers(self, key, value):
    """Translates report_numbers fields."""

    def get_value_rn(f_a, f_z, f_9, rn_obj):
        rn_obj.update({'value': f_a or f_z or f_9, 'scheme': 'REPORT_NUMBER'})
        if f_z or f_9:
            rn_obj.update({'hidden': True})

    _identifiers = self.get('identifiers', [])

    sub_9 = clean_val('9', value, str)
    sub_a = clean_val('a', value, str)
    sub_z = clean_val('z', value, str)

    all_empty = not (sub_z or sub_a or sub_9)

    if key == '037__':
        entry = {}
        if all_empty:
            raise MissingRequiredField(subfield='9 or a or z')

        if sub_9 == 'arXiv':
            arxiv_eprints(self, key, value)
            raise IgnoreKey('identifiers')
        else:
            get_value_rn(sub_a, sub_z, sub_9, entry)
        _identifiers.append(entry)

    if key == '088__':
        entry = {}
        if 'n' in value or 'x' in value:
            barcodes(self, key, value)

        if all_empty and 'n' not in value and 'x' not in value:
            raise MissingRequiredField(subfield='9 or a or z or n or x')

        get_value_rn(sub_a, sub_z, sub_9, entry)
        _identifiers.append(entry)
    return _identifiers


@model.over('barcodes', '^088__')
@for_each_value
def barcodes(self, key, value):
    """Match barcodes of items to volumes."""
    val_n = clean_val('n', value, str)
    val_x = clean_val('x', value, str)

    _migration = self.get('_migration', {'volumes': []})
    _migration['volumes'].append(dict(
        volume=extract_volume_number(
            val_n,
            raise_exception=True,
            subfield='n'
        ),
        barcode=val_x
    ))
    self['_migration'] = _migration
    raise IgnoreKey('barcodes')


@model.over('subjects', '(^037__)')
@filter_list_values
def arxiv_eprints(self, key, value):
    """Translates arxiv_eprints fields.

    output:
    {
      'alternative_identifiers': [{'scheme': 'arXiv', 'value': `037__a`}],
    }
    """

    def check_category(field, val):
        category = clean_val(field, val, str)
        if category:
            if category in ARXIV_CATEGORIES:
                return category
            raise UnexpectedValue(subfield=field)

    if key == '037__':
        _alternative_identifiers = self.get('alternative_identifiers', [])
        for v in force_list(value):
            eprint_id = clean_val('a', v, str, req=True)
            duplicated = [
                elem
                for i, elem in enumerate(_alternative_identifiers)
                if elem['value'] == eprint_id and elem['scheme'] == 'arXiv'
            ]
            category = check_category('c', v)
            if not duplicated:
                eprint = {'value': eprint_id, 'scheme': 'arXiv'}
                _alternative_identifiers.append(eprint)
                self['alternative_identifiers'] = _alternative_identifiers
            if category:
                _subjects = self.get('subjects', [])
                subject = {'scheme': 'arXiv', 'value': category}
                _subjects.append(subject) if subject not in _subjects else None
                self['subjects'] = _subjects
        raise IgnoreKey('subjects')


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


@model.over('subjects',
            '(^050)|(^080__)|(^08204)|(^084__)|(^082__)')
@for_each_value
@out_strip
def subject_classification(self, key, value):
    """Translates subject classification field."""
    prev_subjects = self.get('subjects', [])
    _subject_classification = {'value': clean_val('a', value, str, req=True)}
    if key == '080__':
        _subject_classification.update({'scheme': 'UDC'})
    elif key.startswith('082'):
        _subject_classification.update({'scheme': 'Dewey'})
    elif key == '084__':
        sub_2 = clean_val('2', value, str)
        if sub_2 and sub_2.upper() in SUBJECT_CLASSIFICATION_EXCEPTIONS:
            keywords(self, key, value)
            raise IgnoreKey('subjects')
        else:
            _subject_classification.update({'scheme': 'ICS'})
    elif key.startswith('050'):
        _subject_classification.update({'scheme': 'LoC'})
    if _subject_classification not in prev_subjects:
        return _subject_classification
    else:
        raise IgnoreKey('subjects')


@model.over('keywords', '(^6531_)')
@for_each_value
@filter_values
def keywords(self, key, value):
    """Keywords."""
    return {
        'value': clean_val('a', value, str),
        'source': value.get('9') or value.get('g'),
    }


@model.over('conference_info', '(^111__)|(^711__)')
@filter_values
def conference_info(self, key, value):
    """Translates conference info."""
    _conference_info = self.get('conference_info', {})
    for v in force_list(value):
        if key == '111__':
            try:
                opening_date = parser.parse(clean_val('9', v, str, req=True))
                closing_date = parser.parse(clean_val('z', v, str, req=True))
                dates = "{0} - {1}".format(opening_date.date().isoformat(),
                                           closing_date.date().isoformat())
            except ValueError:
                raise UnexpectedValue(subfield='9 or z')
            country_code = clean_val('w', v, str)
            if country_code:
                try:
                    country_code = str(pycountry.countries.get(
                        alpha_2=country_code).alpha_2)
                except (KeyError, AttributeError):
                    raise UnexpectedValue(subfield='w')

            try:
                series_number = clean_val('n', v, int)
            except TypeError:
                raise UnexpectedValue('n', message=' series number not an int')

            _prev_identifiers = _conference_info.get('identifiers', [])
            _prev_identifiers.append(
                {'scheme': 'CERN_CODE', 'value': clean_val('g', v, str)})

            _conference_info.update({
                'title': clean_val('a', v, str, req=True),
                'place': clean_val('c', v, str, req=True),
                'dates': dates,
                'identifiers': _prev_identifiers,
                'series': {'number': series_number},
                'country': country_code,
            })
        else:
            _conference_info.update({
                'acronym': clean_val('a', v, str)})
    return _conference_info


@model.over('alternative_titles', '^242__')
@filter_list_values
def alternative_titles(self, key, value):
    """Translates title translations."""
    _alternative_titles = self.get('alternative_titles', [])
    if 'a' in value:
        _alternative_titles.append({
            'value': clean_val('a', value, str, req=True),
            'type': 'TRANSLATED_TITLE',
            'language': 'en',
        })
    if 'b' in value:
        _alternative_titles.append({
            'value': clean_val('b', value, str, req=True),
            'type': 'TRANSLATED_SUBTITLE',
            'language': 'en',
        })
    return _alternative_titles


@model.over('edition', '^250__')
@out_strip
def edition(self, key, value):
    """Translates edition indicator field."""
    return clean_val('a', value, str)


@model.over('imprint', '^260__')
@filter_values
def imprint(self, key, value):
    """Translates imprints fields."""
    reprint = clean_val('g', value, str)
    if reprint:
        reprint = reprint.lower().replace('repr.', '').strip()
    try:
        date = parser.parse(clean_val('c', value, str, req=True))
    except ParserError:
        raise UnexpectedValue(subfield='c')
    self['publication_year'] = str(date.date().year)
    return {
        'date': clean_val('c', value, str, req=True),
        'place': clean_val('a', value, str),
        'publisher': clean_val('b', value, str),
        'reprint': reprint,
    }


@model.over('book_series', '^490__')
@for_each_value
def book_series(self, key, value):
    """Match barcodes to volumes."""
    val_n = clean_val('n', value, str)
    val_x = clean_val('x', value, str)

    _migration = self.get('_migration', {})
    if 'serials' not in _migration:
        _migration['serials'] = []
    _migration['serials'].append({
        'title': clean_val('a', value, str),
        'volume': clean_val('v', value, str),
        'issn': clean_val('x', value, str),
    })
    _migration['has_serial'] = True
    self['_migration'] = _migration
    raise IgnoreKey('book_series')


@model.over('note', '^500__')
@out_strip
def note(self, key, value):
    """Translates public notes."""
    # merge all found notes
    _note = self.get('note', "")
    if _note:
        _note = \
            "{0} / {1}".format(_note, clean_val('a', value, str, req=True))
    else:
        _note = clean_val('a', value, str, req=True)

    return _note


@model.over('alternative_abstracts', '^520__')
@for_each_value
@out_strip
def alternative_abstracts(self, key, value):
    """Translates abstracts fields."""
    abstract = self.get('abstract', None)
    _alternative_abstracts = self.get('alternative_abstracts', [])
    if not abstract:
        # takes first abstract as main
        self["abstract"] = clean_val('a', value, str, req=True)
        raise IgnoreKey('alternative_abstracts')
    new_abstract = clean_val('a', value, str, req=True)
    return new_abstract if new_abstract not in _alternative_abstracts else None


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
