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

from cds_dojson.to_marc21.models.video import model as to_marc21


@to_marc21.over('300', '^physical_description$', override=True)
@utils.reverse_for_each_value
@utils.filter_values
def physical_description(self, key, value):
    """Physical Description."""
    return {
        'a': utils.reverse_force_list(
            value.get('extent')
        ),
        'c': utils.reverse_force_list(
            value.get('dimensions')
        ),
        'b': value.get('other_physical_details'),
        'd': value.get('maximum_resolution'),
        'e': value.get('accompanying_material'),
        'g': utils.force_list(
            value.get('size_of_unit')
        ),
        'f': utils.reverse_force_list(
            value.get('type_of_unit')
        ),
        '3': value.get('materials_specified'),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
    }
