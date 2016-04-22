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


@to_marc21.over('653', '^index_term_uncontrolled$', override=True)
@utils.reverse_for_each_value
@utils.filter_values
def reverse_index_term_uncontrolled(self, key, value):
    """Reverse - Index Term-Uncontrolled."""
    indicator_map1 = {
        "No information provided": "_",
        "No level specified": "0",
        "Primary": "1",
        "Secondary": "2"}
    indicator_map2 = {
        "Chronological term": "4",
        "Corporate name": "2",
        "Genre/form term": "6",
        "Geographic name": "5",
        "Meeting name": "3",
        "No information provided": "_",
        "Personal name": "1",
        "Topical term": "0"}
    return {
        'a': utils.reverse_force_list(
            value.get('uncontrolled_term')
        ),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '6': value.get('linkage'),
        '9': value.get('institute_of_the_uncontrolled_term'),
        '$ind1': indicator_map1.get(value.get('level_of_index_term'), '_'),
        '$ind2': indicator_map2.get(value.get('type_of_term_or_name'), '_'),
    }


@to_marc21.over('690', '^subject_indicator$')
@utils.reverse_for_each_value
def subject_indicator(self, key, value):
    """Subject Indicator."""
    return {
        'a': value,
        '$ind1': 'C',
    }


@to_marc21.over('691', '^observation$')
def observation(self, key, value):
    """Observation."""
    return {'a': value}


@to_marc21.over('693', '^accelerator_experiment$')
@utils.reverse_for_each_value
@utils.filter_values
def accelerator_experiment(self, key, value):
    """Experiment."""
    return {
        'a': value.get('accelerator'),
        'e': value.get('experiment'),
        'f': value.get('facility'),
        's': value.get('subfield_s'),
    }


@to_marc21.over('694', '^classification_terms$')
@utils.reverse_for_each_value
@utils.filter_values
def classification_terms(self, key, value):
    """Classification terms."""
    return {
        'a': value.get('uncontrolled_term'),
        '9': value.get('institute'),
    }


@to_marc21.over('695', '^thesaurus_terms$')
@utils.reverse_for_each_value
@utils.filter_values
def thesaurus_terms(self, key, value):
    """The thesaurus term."""
    return {
        'a': value.get('uncontrolled_term'),
        '9': value.get('institute'),
    }
