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

from cds_dojson.marc21.models.default import model as marc21


@marc21.over('index_term_uncontrolled', '^653[10_2][_1032546]', override=True)
@utils.for_each_value
@utils.filter_values
def index_term_uncontrolled(self, key, value):
    """Index Term-Uncontrolled."""
    indicator_map1 = {
        "#": "No information provided",
        "0": "No level specified",
        "1": "Primary",
        "2": "Secondary"}
    indicator_map2 = {
        "#": "No information provided",
        "0": "Topical term",
        "1": "Personal name",
        "2": "Corporate name",
        "3": "Meeting name",
        "4": "Chronological term",
        "5": "Geographic name",
        "6": "Genre/form term"}
    return {
        'uncontrolled_term': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': utils.force_list(
            value.get('8')
        ),
        'linkage': value.get('6'),
        'institute_of_the_uncontrolled_term': value.get('9'),
        'level_of_index_term': indicator_map1.get(key[3]),
        'type_of_term_or_name': indicator_map2.get(key[4]),
    }


@marc21.over('subject_indicator', '^69[07]C_')
@utils.for_each_value
def subject_indicator(self, key, value):
    """Subject Indicator."""
    return value.get('a')


@marc21.over('observation', '^691__')
def observation(self, key, value):
    """Observation."""
    return value.get('a')


@marc21.over('accelerator_experiment', '^693__')
@utils.for_each_value
@utils.filter_values
def accelerator_experiment(self, key, value):
    """Experiment."""
    return {
        'accelerator': value.get('a'),
        'experiment': value.get('e'),
        'facility': value.get('f'),
        'subfield_s': value.get('s'),
    }


@marc21.over('classification_terms', '^694__')
@utils.for_each_value
@utils.filter_values
def classification_terms(self, key, value):
    """Classification terms."""
    return {
        'uncontrolled_term': value.get('a'),
        'institute': value.get('9'),
    }


@marc21.over('thesaurus_terms', '^695__')
@utils.for_each_value
@utils.filter_values
def thesaurus_terms(self, key, value):
    """Thesaurus term."""
    return {
        'uncontrolled_term': value.get('a'),
        'institute': value.get('9'),
    }
