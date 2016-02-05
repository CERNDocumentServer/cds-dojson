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

"""CDS Image MARC 21 field definitions."""

from dojson import utils

from cds_dojson.to_marc21.models.image import model as to_marc21


@to_marc21.over('774', '^album_parent$', override=True)
@utils.reverse_for_each_value
@utils.filter_values
def album_parent(self, key, value):
    """Album ID which contains this photo"""
    return {
        'a': value.get('dump_album'),
        'r': value.get('album_id')
    }


@to_marc21.over('856', '^image_url$', override=True)
@utils.reverse_for_each_value
@utils.filter_values
def image_url(self, key, value):
    """Image URL.

    Contains the URL to the concrete image file and information about the
    format.
    """
    indicator_map1 = {
        "Dial-up": "3",
        "Email": "0",
        "FTP": "1",
        "HTTP": "4",
        "Method specified in subfield $2": "7",
        "No information provided": "_",
        "Remote login (Telnet)": "2"}
    indicator_map2 = {
        "No display constant generated": "8",
        "No information provided": "_",
        "Related resource": "2",
        "Resource": "0",
        "Version of resource": "1"}
    return {
        's': value.get('size'),
        'd': value.get('path'),
        'g': value.get('qelectronic_format_type'),
        'u': value.get('uri'),
        'y': value.get('link_text'),
        'z': value.get('public_note'),
        'x': value.get('subformat'),
        '8': value.get('photo_id'),
        '$ind1': indicator_map1.get(value.get('access_method'), '7'),
        '$ind2': indicator_map2.get(value.get('relationship'), '_'),
    }
