# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2016 CERN.
#
# CERN Document Server is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# CERN Document Server is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CERN Document Server; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.
"""Test cds-dojson CLI and jsonschema compiler."""

from __future__ import absolute_import

import json
import os
import pkg_resources
import pytest
from click.testing import CliRunner

from cds_dojson.cli import compile_schema, convert_yaml2json
from click.testing import CliRunner


@pytest.mark.parametrize('src, compiled', [
    ('records/videos/video/video_src-v1.0.0.json',
     'records/videos/video/video-v1.0.0.json'),
    ('records/videos/project/project_src-v1.0.0.json',
     'records/videos/project/project-v1.0.0.json'),
    ('deposits/records/videos/video/video_src-v1.0.0.json',
     'deposits/records/videos/video/video-v1.0.0.json'),
    ('deposits/records/videos/project/project_src-v1.0.0.json',
     'deposits/records/videos/project/project-v1.0.0.json'),
    ('records/books/book/document_src-v0.0.1.json',
     'records/books/book/document-v0.0.1.json'),
])
def test_cli(src, compiled):
    """Test cds-dojson CLI."""
    runner = CliRunner()

    result = runner.invoke(compile_schema, [
        pkg_resources.resource_filename('cds_dojson.schemas', src)
    ])
    assert 0 == result.exit_code
    compiled_schema_result = json.loads(result.output)
    with open(
            pkg_resources.resource_filename('cds_dojson.schemas',
                                            compiled), 'r') as f:
        compile_schema_expected = json.load(f)
    assert compile_schema_expected == compiled_schema_result


@pytest.mark.parametrize('source, destination', [
    ('./tests/fixtures/books/ymls/', './tests/fixtures/books/results/')
])
def test_cli_convert_yaml2json(source, destination):
    """Test cds-dojson CLI 'convert_yaml2json' command"""
    runner = CliRunner()

    result = runner.invoke(convert_yaml2json, [source, destination])

    assert 0 == result.exit_code

    with open('./tests/fixtures/books/books_title_mock.json') as s:
        # read the mock JSON file
        json_mock = json.load(s)

    with open(os.path.join(destination, 'books_title.json')) as s:
        # read the newly created JSON file
        json_converted = json.load(s)

    assert json_mock == json_converted
