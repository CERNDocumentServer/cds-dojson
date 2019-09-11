# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017 CERN.
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
"""Base models for common fields."""
from __future__ import unicode_literals

from dojson._compat import iteritems
from dojson.errors import IgnoreKey, MissingRule
from dojson.utils import GroupableOrderedDict

from ....overdo import OverdoJSONSchema
from ..base import model as cds_base


COMMON_IGNORE_FIELDS = {
    '003',
    '005',
    '020__q',
    '0248_a',
    '0248_p',
    '041__h',  # 206 cds-dojson
    '035__z',
    '050__b',
    '050_4b',
    '082002',
    '082042',
    '0820_2',
    '082__2',
    '111__d',
    '111__f',
    '269__a',  # preprint info
    '269__b',  # preprint info
    '269__c',  # preprint date
    '300__b',  # 206 cds-dojson
    '340__a',
    '440_3a',  # 206 cds-dojson
    '541__9',
    '541__h',
    '502__a',  # thesis_info/defense_date
    '502__b',  # thesis_info/degree_type
    '502__c',  # thesis_info/institutions
    '502__d',  # thesis_info/date (publication)
    '5208_a',  # 206 cds-dojson
    '650172',
    '65017a',
    '650272',
    '65027a',
    '690__c',  # 206 cds-dojson
    '694__9',
    '694__a',
    '773__r',  # publication_info/parent_report_number
    '773__z',  # publication_info/parent_isbn
    '852__c',
    '852__h',
    '900__s',  # 206 cds-dojson
    '900__u',  # 206 cds-dojson
    '900__y',  # 206 cds-dojson
    '901__a',  # record affiliation
    '901__u',
    '916__d',
    '916__e',
    '916__y',
    '940__u',
    '961__c',
    '961__h',
    '961__l',
    '961__x',
    '962__b',
    '962__n',
    '963__a',
    '964__a',
    '970__a',
    '981__a',
}


class CDSOverdoBookBase(OverdoJSONSchema):
    """Translation base Index for CDS Books."""

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Translate blob values and instantiate new model instance.

        Raises ``MissingRule`` when no rule matched and ``ignore_missing``
        is ``False``.

        :param blob: ``dict``-like object on which the matching rules are
                     going to be applied.
        :param ignore_missing: Set to ``False`` if you prefer to raise
                               an exception ``MissingRule`` for the first
                               key that it is not matching any rule.
        :param exception_handlers: Give custom exception handlers to take care
                                   of non-standard codes that are installation
                                   specific.

        .. versionchanged:: 1.0.0

           ``ignore_missing`` allows to specify if the function should raise
           an exception.

        .. versionchanged:: 1.1.0

           ``exception_handlers`` allows to set custom handlers for
           non-standard MARC codes.
        """
        handlers = {IgnoreKey: None}
        handlers.update(exception_handlers or {})

        def clean_missing(exc, output, key, value):
            order = output.get('__order__')
            if order:
                order.remove(key)

        if ignore_missing:
            handlers.setdefault(MissingRule, clean_missing)

        output = {}

        if self.index is None:
            self.build()
        if isinstance(blob, GroupableOrderedDict):
            items = blob.iteritems(repeated=True, with_order=False)
        else:
            items = iteritems(blob)
        for key, value in items:
            try:
                result = self.index.query(key)
                if not result:
                    raise MissingRule(key)

                name, creator = result
                data = creator(output, key, value)
                if getattr(creator, '__extend__', False):
                    existing = output.get(name, [])
                    existing.extend(data)
                    output[name] = existing
                else:
                    output[name] = data
            except Exception as exc:
                if exc.__class__ in handlers:
                    handler = handlers[exc.__class__]
                    if handler is not None:
                        handler(exc, output, key, value)
                else:
                    raise
        return output


class BooksBase(OverdoJSONSchema):
    """Base model conversion MARC21 to JSON."""


model = BooksBase(bases=(),
                  entry_point_group='cds_dojson.marc21.books')
