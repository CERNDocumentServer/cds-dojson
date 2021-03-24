# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2015, 2017 CERN.
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

from dojson.contrib.marc21.utils import MARC21_DTD, split_stream
from lxml import etree
from six import StringIO, binary_type, text_type

from ..utils import MementoDict


def create_record(marcxml, correct=False, keep_singletons=True):
    """Create a record object using the LXML parser.

    If correct == 1, then perform DTD validation
    If correct == 0, then do not perform DTD validation
    """
    if isinstance(marcxml, binary_type):
        marcxml = marcxml.decode('utf-8')

    if isinstance(marcxml, text_type):
        parser = etree.XMLParser(dtd_validation=correct, recover=True)

        if correct:
            marcxml = (u'<?xml version="1.0" encoding="UTF-8"?>\n'
                       u'<!DOCTYPE collection SYSTEM "file://{0}">\n'
                       u'<collection>\n{1}\n</collection>'.format(
                           MARC21_DTD, marcxml))

        tree = etree.parse(StringIO(marcxml), parser)
    else:
        tree = marcxml
    record = []

    leader_iterator = tree.iter(tag='{*}leader')
    for leader in leader_iterator:
        text = leader.text or ''
        record.append(('leader', text))

    controlfield_iterator = tree.iter(tag='{*}controlfield')
    for controlfield in controlfield_iterator:
        tag = controlfield.attrib.get('tag', '!')
        text = controlfield.text or ''
        if text or keep_singletons:
            record.append((tag, text))

    datafield_iterator = tree.iter(tag='{*}datafield')
    for datafield in datafield_iterator:
        tag = datafield.attrib.get('tag', '!')
        ind1 = datafield.attrib.get('ind1', '!')
        ind2 = datafield.attrib.get('ind2', '!')
        if ind1 in ('', '#'):
            ind1 = '_'
        if ind2 in ('', '#'):
            ind2 = '_'
        ind1 = ind1.replace(' ', '_')
        ind2 = ind2.replace(' ', '_')

        fields = []
        subfield_iterator = datafield.iter(tag='{*}subfield')
        for subfield in subfield_iterator:
            code = subfield.attrib.get('code', '!')  # .encode("UTF-8")
            text = subfield.text or ''
            if text or keep_singletons:
                fields.append((code, text))

        if fields or keep_singletons:
            key = '{0}{1}{2}'.format(tag, ind1, ind2)
            record.append((key, MementoDict(fields)))

    return MementoDict(record)


def load(source):
    """Load MARC XML and return Python dict."""
    for data in split_stream(source):
        yield create_record(data)
