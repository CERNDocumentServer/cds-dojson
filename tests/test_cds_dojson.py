# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
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
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.

"""General CDS DoJSON Tests."""

from __future__ import absolute_import, print_function

import pytest


def test_version():
    """Test version import."""
    from cds_dojson import __version__
    assert __version__


def test_wrong_model():
    """Test cds_marc21 should not be used for `over`."""
    from cds_dojson.marc21 import marc21
    with pytest.raises(NotImplementedError):
        @marc21.over('test', '...')
        def test(self, key, value):
            """Testing function."""
            return {'a': 'b'}
