# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
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
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.
"""Book fields tests."""

from cds_dojson.marc21.models.books.book import model
from cds_dojson.marc21.utils import create_record


marcxml = ("""<collection xmlns="http://www.loc.gov/MARC21/slim">"""
           """<record>{0}</record></collection>""")


def check_transformation(marcxml_body, json_body):
    blob = create_record(marcxml.format(marcxml_body))
    record = model.do(blob)
    expected = {
        '$schema': {
            '$ref': ('records/books/book/book-v.0.0.1.json')
        }
    }
    expected.update(**json_body)
    assert record == expected


def test_document_type_field(app):

    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">BOOK</subfield></datafield>
            """, {
                'document_type': 'BOOK',
            })