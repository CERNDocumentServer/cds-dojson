# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2016, 2017 CERN.
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

"""CLI additions to ``dojson``."""

from __future__ import absolute_import, print_function

import json
import os

import click

from .schemas.transform import compile_schema as _compile_schema


@click.group()
def cli():
    """CDS dojson CLI."""


@cli.command()
@click.argument('schema', type=click.Path(exists=True))
def compile_schema(schema):
    """Compile ``$ref`` and ``allOf`` key from the given JSON schema."""
    with open(schema) as f:
        schema_json = json.load(f)

    base_uri = 'file://{0}/'.format(os.path.dirname(os.path.abspath(schema)))

    click.echo(json.dumps(_compile_schema(schema_json, base_uri), indent=2))
