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

"""Base classes for CDS DoJSON."""

from dojson.overdo import Overdo as DoJSONOverdo

from .matcher import matcher


class OverdoBase(DoJSONOverdo):
    """Base entry class."""

    def __init__(
            self, bases=None, entry_point_group=None, entry_point_models=None):
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
