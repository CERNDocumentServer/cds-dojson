# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2015 CERN.
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

"""CDS special/custom tags."""

from dojson import utils

from ...models.default import model as to_marc21


@to_marc21.over('901', '^affiliation_at_conversion$')
@utils.reverse_for_each_value
def affiliation_at_conversion(self, key, value):
    """Affiliation at conversion."""
    return {
        'u': value.get('name_of_institute'),
    }


@to_marc21.over('903', '^approval_status_history$|^grey_book$')
@utils.reverse_for_each_value
@utils.filter_values
def approval_status_history(self, key, value):
    """Approval status history."""
    if any(k in value for k in ('approval', 'beam', 'status_week')):
        return {
            'a': value.get('approval'),
            'b': value.get('beam'),
            'd': value.get('status_date'),
            's': value.get('status'),
        }
    else:
        return {
            'a': value.get('description'),
            'b': value.get('report_number'),
            'c': value.get('category'),
            'd': value.get('date'),
            'e': value.get('deadline'),
            'f': value.get('e-mail'),
            's': value.get('status'),
            '$ind1': '1',
        }


@to_marc21.over('905', '^spokesman$')
@utils.reverse_for_each_value
@utils.filter_values
def spokesman(self, key, value):
    """Spokesman."""
    return {
        'a': value.get('address'),
        'k': value.get('telephone'),
        'l': value.get('fax'),
        'm': value.get('e-mail'),
        'p': value.get('personal_name'),
        'q': value.get('private_address'),
    }


@to_marc21.over('906', '^referee$')
@utils.reverse_for_each_value
@utils.filter_values
def referee(self, key, value):
    """Referee."""
    return {
        'a': value.get('address'),
        'k': value.get('telephone'),
        'l': value.get('fax'),
        'm': value.get('e-mail'),
        'p': value.get('personal_name'),
        'q': value.get('private_address'),
        'u': value.get('affiliation'),
    }


@to_marc21.over('910', '^fsgo$')
@utils.reverse_for_each_value
@utils.filter_values
def fsgo(self, key, value):
    """FSGO."""
    return {
        'f': value.get('personal_name'),
        '9': value.get('alternate_abbreviated_title'),
    }


@to_marc21.over('913', '^citation$')
@utils.reverse_for_each_value
@utils.filter_values
def citation(self, key, value):
    """Citation."""
    return {
        'c': value.get('citation'),
        'p': value.get('unformatted_reference'),
        't': value.get('title_abbreviation'),
        'u': value.get('uniform_resource_identifier'),
        'v': value.get('volume'),
        'y': value.get('year'),
    }


@to_marc21.over('916', '^status_week$')
@utils.reverse_for_each_value
@utils.filter_values
def status_week(self, key, value):
    """The status week."""
    return {
        'a': value.get('acquisition_of_proceedings_code'),
        'd': value.get('display_period_for_books'),
        'e': value.get('number_of_copies_bought_by_cern'),
        's': value.get('status_of_record'),
        'w': value.get('status_week'),
        'y': value.get('year_for_annual_list'),
    }


@to_marc21.over('925', '^dates$')
@utils.reverse_for_each_value
@utils.filter_values
def dates(self, key, value):
    """Dates."""
    return {
        'a': value.get('opening'),
        'b': value.get('closing')
    }


@to_marc21.over('927', '^file_number$')
@utils.reverse_for_each_value
def file_number(self, key, value):
    """File Number."""
    return {'a': value}


@to_marc21.over('937', '^peri_internal_note$')
@utils.reverse_for_each_value
@utils.filter_values
def peri_internal_note(self, key, value):
    """Peri: internal note."""
    return {
        'a': value.get('internal_note'),
        'c': value.get('modification_date'),
        's': value.get('responsible_of_the_modification'),
    }


@to_marc21.over('960', '^base$')
@utils.reverse_for_each_value
def base(self, key, value):
    """Base."""
    return {'a': value}


@to_marc21.over('961', '^cat$')
@utils.reverse_for_each_value
@utils.filter_values
def cat(self, key, value):
    """CAT."""
    return {
        'a': value.get('cataloger'),
        'b': value.get('cataloger_level'),
        'c': value.get('modification_date'),
        'l': value.get('library'),
        'h': value.get('hour'),
        'x': value.get('creation_date'),
    }


@to_marc21.over('962', '^aleph_linking_field$')
@utils.reverse_for_each_value
@utils.filter_values
def aleph_linking_field(self, key, value):
    """ALEPH linking field."""
    return {
        'a': value.get('link_type'),
        'b': value.get('sysno'),
        'l': value.get('library'),
        'n': value.get('down_record_link_note'),
        'm': value.get('up_record_link_note'),
        'y': value.get('year_link'),
        'v': value.get('volume_link'),
        'p': value.get('part_link'),
        'i': value.get('issue_link'),
        'k': value.get('pages_link'),
        't': value.get('base'),
    }


# We are squashing this field, because it might contain duplicates
# (even though it shouldn't) and we don't want to lose data
@to_marc21.over('963', '^owner$')
@utils.filter_values
def owner(self, key, value):
    """Owner."""
    return {
        'a': value.get('owner'),
        'b': value.get('status')
    }


@to_marc21.over('964', '^item$')
def item(self, key, value):
    """Item."""
    return {
        'a': value.get('owner'),
    }


# We are squashing this field, because it might contain duplicates
# (even though it shouldn't) and we don't want to lose data
@to_marc21.over('970', '^sysno$')
@utils.filter_values
def sysno(self, key, value):
    """System number taken from AL500 SYS."""
    return {
        'a': value.get('sysno'),
        'd': value.get('surviver'),
    }


@to_marc21.over('980', '^collections$', override=True)
@utils.reverse_for_each_value
@utils.filter_values
def collections(record, key, value):
    """Parse custom MARC tag 980."""
    return {
        'a': value.get('primary'),
        'b': value.get('secondary'),
        'c': value.get('deleted'),
    }


@to_marc21.over('981', '^system_number_of_deleted_double_records$')
@utils.reverse_for_each_value
def system_number_of_deleted_double_records(self, key, value):
    """System number of deleted double records."""
    return {'a': value}


@to_marc21.over('993', '^additional_subject_added_entry_topical_term$')
@utils.reverse_for_each_value
@utils.filter_values
def additional_subject_added_entry_topical_term(self, key, value):
    """Additional subject added entry- topical term."""
    return {
        'q': value.get('processes'),
        'r': value.get('accelerator_physics'),
        't': value.get('technology'),
    }


@to_marc21.over('999', '^references$|^refextract_references$|^record_type$')
@utils.reverse_for_each_value
@utils.filter_values
def references(self, key, value):
    """References."""
    if 'refextract_info' in value:
        return {
            'a': value.get('refextract_info'),
            '$ind1': 'C',
            '$ind2': '6',
        }
    elif 'record_type' in value:
        return {
            'a': value.get('record_type'),
            '9': value.get('dump'),
        }
    else:
        return {
            'a': value.get('doi'),
            'h': value.get('authors'),
            'm': utils.reverse_force_list(
                value.get('miscellaneous')
            ),
            'n': value.get('issue_number'),
            'o': value.get('order_number'),
            'p': value.get('page'),
            'r': value.get('report_number'),
            's': value.get('journal_publication_note'),
            't': value.get('journal_title_abbreviation'),
            'u': value.get('uniform_resource_identifier'),
            'v': value.get('volume'),
            'y': value.get('year'),
            '$ind1': 'C',
            '$ind2': '5',
        }
