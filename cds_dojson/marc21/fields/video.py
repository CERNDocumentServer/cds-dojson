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

from cds_dojson.marc21.models.video import model as marc21


@marc21.over('physical_description', '^300..', override=True)
@utils.for_each_value
@utils.filter_values
def physical_description(self, key, value):
    """Physical Description."""
    return {
        'extent': utils.force_list(
            value.get('a')
        ),
        'dimensions': utils.force_list(
            value.get('c')
        ),
        'other_physical_details': value.get('b'),
        'maximum_resolution': value.get('d'),
        'accompanying_material': value.get('e'),
        'size_of_unit': utils.force_list(
            value.get('g')
        ),
        'type_of_unit': utils.force_list(
            value.get('f')
        ),
        'materials_specified': value.get('3'),
        'linkage': value.get('6'),
        'field_link_and_sequence_number': utils.force_list(
            value.get('8')
        ),
    }
