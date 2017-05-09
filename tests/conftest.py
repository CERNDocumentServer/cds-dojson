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

import os

import pkg_resources
import pytest
from flask import Flask
from invenio_jsonschemas import InvenioJSONSchemas

from cds_dojson.marc21.utils import create_record


@pytest.fixture()
def app():
    """Flask application fixture."""
    app_ = Flask(__name__)
    app_.config.update(TESTING=True)
    InvenioJSONSchemas(app_)
    return app_


@pytest.fixture()
def marcxml_to_json(app, request):
    """Load marcxml file and return the JSON."""
    file_, model = request.param

    marcxml = pkg_resources.resource_string(__name__,
                                            os.path.join('fixtures', file_))
    with app.app_context():
        return model.do(create_record(marcxml))
