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
"""Define Books flavour exceptions."""
from dojson.errors import DoJSONException


class UnexpectedValue(DoJSONException):
    """The corresponding value is unexpected."""

    message = '[UNEXPECTED INPUT VALUE]'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self.subfield = kwargs.get('subfield', None)
        super(UnexpectedValue, self).__init__(*args)


class MissingRequiredField(DoJSONException):
    """The corresponding value is required."""

    message = '[MISSING REQUIRED FIELD]'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self.subfield = kwargs.get('subfield', None)
        super(MissingRequiredField, self).__init__(*args)


class ManualMigrationRequired(DoJSONException):
    """The corresponding field should be manually migrated."""

    message = '[MANUAL MIGRATION REQUIRED]'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self.subfield = kwargs.get('subfield', None)
        super(ManualMigrationRequired, self).__init__(*args)
