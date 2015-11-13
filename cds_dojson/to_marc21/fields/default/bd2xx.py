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


@to_marc21.over('245', '^title_statement$', override=True)
@utils.filter_values
def title_statement(self, key, value):
    """Title Statement."""
    indicator_map1 = {"No added entry": "0", "Added entry": "1"}
    indicator_map2 = {
        "No nonfiling characters": "0",
        "Number of nonfiling characters": "1",
        "Number of nonfiling characters": "2",
        "Number of nonfiling characters": "3",
        "Number of nonfiling characters": "4",
        "Number of nonfiling characters": "5",
        "Number of nonfiling characters": "6",
        "Number of nonfiling characters": "7",
        "Number of nonfiling characters": "8",
        "Number of nonfiling characters": "9",
    }
    return {
        'a': value.get('title'),
        'c': value.get('statement_of_responsibility'),
        'b': value.get('remainder_of_title'),
        'g': value.get('bulk_dates'),
        'f': value.get('inclusive_dates'),
        'h': value.get('medium'),
        'k': utils.reverse_force_list(
            value.get('form')
        ),
        'n': utils.reverse_force_list(
            value.get('number_of_part_section_of_a_work')
        ),
        'p': utils.reverse_force_list(
            value.get('name_of_part_section_of_a_work')
        ),
        's': value.get('version'),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '$ind1': indicator_map1.get(
            value.get('title_added_entry'), '_'
        ),
        '$ind2': indicator_map2.get(
            value.get('nonfiling_characters'), '_'
        ),
    }


@to_marc21.over('269', '^imprint$')
@utils.reverse_for_each_value
@utils.filter_values
def imprint(self, key, value):
    """Pre-publication, distribution, etc.

    NOTE: Don't use the following lines for CER base=14,2n,41-45
    NOTE: Don't use for THESES
    """
    return {
        'a': value.get('place_of_publication'),
        'b': value.get('name_of_publication'),
        'c': value.get('complete_date'),
    }
