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
"""Base classes for CDS DoJSON."""

import pkg_resources
from dojson.overdo import Overdo as DoJSONOverdo

from .matcher import matcher
from .utils import not_accessed_keys

try:
    pkg_resources.get_distribution('flask')
    from flask import current_app
except (pkg_resources.DistributionNotFound, RuntimeError) as e:
    HAS_FLASK = False
else:
    HAS_FLASK = True


class OverdoBase(DoJSONOverdo):
    """Base entry class."""

    def __init__(self,
                 bases=None,
                 entry_point_group=None,
                 entry_point_models=None):
        """Init."""
        super(OverdoBase, self).__init__(bases, entry_point_group)
        self.entry_point_models = entry_point_models

    def over(self, *args, **kwargs):
        """Not to be used in this class."""
        raise NotImplementedError()

    def do(self, blob, **kwargs):
        """Translate blob values and instantiate new model instance."""
        return matcher(blob, self.entry_point_models).do(blob, **kwargs)

    def missing(self, blob, **kwargs):
        """Translate blob values and instantiate new model instance."""
        return matcher(blob, self.entry_point_models).missing(blob, **kwargs)


class Overdo(DoJSONOverdo):
    """Translation index base."""

    __query__ = ''
    """To be used by the matcher to find the proper model."""

    __ignore_keys__ = set()
    """List of keys which don't need transformation."""

    def over(self, name, *source_tags, **kwargs):
        """Register creator rule.

        :param kwargs:
            * override: boolean, overrides the rule if either the `name` or the
              regular expression in `source_tags` are equal to the current
              ones.
        """
        def override(rule):
            if name == rule[1][0]:
                return True
            for field in source_tags:
                if field == rule[0]:
                    return True
            return False

        if kwargs.get('override', False):
            self.rules[:] = [rule for rule in self.rules if not override(rule)]

        return super(Overdo, self).over(name, *source_tags)

    def missing(self, blob, **kwargs):
        """Return keys with missing rules."""
        return not_accessed_keys(blob) - self.__class__.__ignore_keys__


class OverdoJSONSchema(Overdo):
    """Translation index which adds $schema key."""

    __schema__ = ''
    """Name of the schema to be added to the final JSON."""

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Set schema after translation depending on the model."""
        json = super(OverdoJSONSchema, self).do(
            blob=blob,
            ignore_missing=ignore_missing,
            exception_handlers=exception_handlers)
        if HAS_FLASK:
            json_schema = current_app.extensions['invenio-jsonschemas']
            json['$schema'] = {
                '$ref': json_schema.path_to_url(self.__class__.__schema__)
            }
        else:
            json['$schema'] = {'$ref': self.__class__.__schema__}

        return json
