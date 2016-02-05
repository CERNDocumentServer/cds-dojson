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

"""CDS Album MARC 21 field definitions."""

from dojson import utils

from cds_dojson.to_marc21.models.album import model as to_marc21


@to_marc21.over('774', 'images', override=True)
@utils.reverse_for_each_value
@utils.filter_values
def images(self, key, value):
    """Images contained in this album"""
    reference = None
    try:
        reference = value.get(
            '$ref').replace('http://cds.cern.ch/record/', '')
    except AttributeError:
        reference = None
    return {
        'r': reference,
        'a': value.get('record_type'),
        'n': value.get('relation')
    }


@to_marc21.over('923', '^place_of_photo$')
@utils.reverse_for_each_value
@utils.filter_values
def place_of_photo(self, key, value):
    """Place of photo where it was taken and requester info"""
    return {
        'p': value.get('place'),
        'r': value.get('requester')
    }


@to_marc21.over('924', '^photolab$')
@utils.reverse_for_each_value
@utils.filter_values
def photolab(self, key, value):
    """Photolab"""
    return {
        'a': value.get('tirage'),
        'b': value.get('photolab_1'),
        't': value.get('photolab_2'),
    }
