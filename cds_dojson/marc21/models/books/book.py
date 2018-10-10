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
"""Book model."""

from cds_dojson.overdo import OverdoJSONSchema
from cds_dojson.marc21.fields.base import model as cds_base
from dojson._compat import iteritems
from dojson.errors import IgnoreKey, MissingRule
from dojson.utils import GroupableOrderedDict


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


class CDSBook(CDSOverdoBookBase):
    """Translation Index for CDS Books."""

    __query__ = '980__:BOOK | 960__:21 -980__:DELETED -980__:PROCEEDINGS ' \
                '-960__:42 -960__:43'

    __schema__ = 'records/books/book/book-v.0.0.1.json'

    __ignore_keys__ = {

        '003',
        '005',
        '020__q',
        '0248_',
        '035',
        '340',
        '852',
        '916',
        '940',
        '961',
        '963',
        '964',
        '981',

        # '65017a',
        # '961__l',
        # '650172',
        # '961__h',
        # '0248_p',
        # '961__c',
        # '964__a',
        # '963__a',
        # '961__x',
        # '0248_a',
        # '080__a',
        # '084__a',
        # '852__c',
        # '340__a',
        # '852__h',
        # '490__a',
        # '490__v',
    }

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Set schema after translation depending on the model."""
        json = super(CDSBook, self).do(
            blob=blob,
            ignore_missing=ignore_missing,
            exception_handlers=exception_handlers)
        json['$schema'] = {'$ref': self.__class__.__schema__}
        return json


model = CDSBook(
    bases=(cds_base, ), entry_point_group='cds_dojson.marc21.book')
