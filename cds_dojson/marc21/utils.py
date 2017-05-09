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

"""Utilities for converting MARC21."""

from lxml import etree
from six import StringIO, iteritems, string_types
from dojson.contrib.marc21.utils import split_stream, MARC21_DTD


def create_record(marcxml, correct=False, keep_singletons=True):
    """Create a record object using the LXML parser.
    If correct == 1, then perform DTD validation
    If correct == 0, then do not perform DTD validation
    """
    if isinstance(marcxml, string_types):
        parser = etree.XMLParser(dtd_validation=correct, recover=True)

        if correct:
            marcxml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                       '<!DOCTYPE collection SYSTEM "file://{0}">\n'
                       '<collection>\n{1}\n</collection>'.format(
                           MARC21_DTD, marcxml))

        tree = etree.parse(StringIO(marcxml), parser)
    else:
        tree = marcxml
    record = {}
    field_position_global = 0

    controlfield_iterator = tree.iter(tag='{*}controlfield')
    for controlfield in controlfield_iterator:
        tag = controlfield.attrib.get('tag', '!')  # .encode("UTF-8")
        ind1 = ' '
        ind2 = ' '
        text = controlfield.text
        if text is None:
            text = ''
        else:
            text = text  # .encode("UTF-8")
        subfields = []
        if text or keep_singletons:
            field_position_global += 1
            record.setdefault(tag, []).append((subfields, ind1, ind2, text,
                                               field_position_global))

    datafield_iterator = tree.iter(tag='{*}datafield')
    for datafield in datafield_iterator:
        tag = datafield.attrib.get('tag', '!')  # .encode("UTF-8")
        ind1 = datafield.attrib.get('ind1', '!')  # .encode("UTF-8")
        ind2 = datafield.attrib.get('ind2', '!')  # .encode("UTF-8")
        # ind1, ind2 = _wash_indicators(ind1, ind2)
        if ind1 in ('', '_'):
            ind1 = ' '
        if ind2 in ('', '_'):
            ind2 = ' '
        subfields = []
        subfield_iterator = datafield.iter(tag='{*}subfield')
        for subfield in subfield_iterator:
            code = subfield.attrib.get('code', '!')  # .encode("UTF-8")
            text = subfield.text
            if text is None:
                text = ''
            else:
                text = text  # .encode("UTF-8")
            if text or keep_singletons:
                subfields.append((code, text))
        if subfields or keep_singletons:
            text = ''
            field_position_global += 1
            record.setdefault(tag, []).append((subfields, ind1, ind2, text,
                                               field_position_global))

    class RecTree(dict):
        def __setitem__(self, key, value):
            """Set key making a list if already present."""
            if key in self:
                current_value = self.get(key)
                if not isinstance(current_value, list):
                    current_value = [current_value]
                current_value.append(value)
                value = current_value
            super(RecTree, self).__setitem__(key, value)

    rec_tree = RecTree()

    for key, values in iteritems(record):
        if key < '010' and key.isdigit():
            rec_tree[key] = [value[3] for value in values]
        else:
            for value in values:
                field = RecTree()
                for subfield in value[0]:
                    field[subfield[0]] = subfield[1]
                rec_tree[(key + value[1] + value[2]).replace(' ', '_')] = field

    return dict(rec_tree)


def load(source):
    """Load MARC XML and return Python dict."""
    for data in split_stream(source):
        yield create_record(data)
