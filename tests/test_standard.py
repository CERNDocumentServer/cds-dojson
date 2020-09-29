# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
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

from __future__ import absolute_import, print_function, unicode_literals

from copy import deepcopy

from cds_dojson.marc21.models.books.base import get_migration_dict
from cds_dojson.marc21.models.books.standard import model
from cds_dojson.marc21.utils import create_record

marcxml = ("""<collection xmlns="http://www.loc.gov/MARC21/slim">"""
           """<record>{0}</record></collection>""")


def check_transformation(marcxml_body, json_body):
    blob = create_record(marcxml.format(marcxml_body))
    record = {'_migration': {**get_migration_dict()}}

    record.update(**model.do(blob, ignore_missing=False))
    expected = {
        '$schema': 'https://127.0.0.1:5000/schemas/documents/document-v1.0.0.json',
        '_migration': {**get_migration_dict()}
    }
    expected.update(**json_body)
    assert record == expected


def test_title(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Incoterms 2010</subfield>
                <subfield code="b">les règles de l'ICC</subfield>
            </datafield>
            """,
            {

                'title': 'Incoterms 2010',
                'alternative_titles': [
                    {'value': "les règles de l'ICC", 'type': 'SUBTITLE'},
                ]
            }
        )
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">STANDARD</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Test</subfield>
                <subfield code="b">Subtitle</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">Water quality — sampling</subfield>
                <subfield code="b">
                part 15: guidance on the preservation and handling of sludge
            </subfield>
            </datafield>
            """,
            {
                'document_type': 'STANDARD',
                'title': 'Test',
                'alternative_titles': [
                    {'value': 'Subtitle', 'type': 'SUBTITLE'},
                    {'value': 'Water quality — sampling',
                     'type': 'TRANSLATED_TITLE',
                     'language': 'fr',
                     },
                    {
                        'type': 'TRANSLATED_SUBTITLE',
                        'value': u"""part 15: guidance on the preservation and handling of sludge""",
                        'language': 'fr',
                    }
                ],
            }
        )
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">STANDARD</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Test</subfield>
                <subfield code="b">Subtitle</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">Water quality — sampling</subfield>
                <subfield code="b">
                part 15: guidance on the preservation and handling of sludge
            </subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">373 p</subfield>
            </datafield>
            """, {
                'document_type': 'STANDARD',
                'title': 'Test',
                'alternative_titles': [
                    {'value': 'Subtitle', 'type': 'SUBTITLE'},
                    {'value': 'Water quality — sampling',
                     'type': 'TRANSLATED_TITLE',
                     'language': 'fr',
                     },
                    {
                        'type': 'TRANSLATED_SUBTITLE',
                        'value': u"""part 15: guidance on the preservation and handling of sludge""",
                        'language': 'fr',
                    }
                ],
                'number_of_pages': 373,
            })
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">STANDARD</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Test</subfield>
                <subfield code="b">Subtitle</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">Water quality — sampling</subfield>
                <subfield code="b">
                part 15: guidance on the preservation and handling of sludge
            </subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">mult. p</subfield>
            </datafield>
            """, {
                'document_type': 'STANDARD',
                'title': 'Test',

                'alternative_titles': [
                    {'value': 'Subtitle', 'type': 'SUBTITLE'},
                    {'value': 'Water quality — sampling',
                     'type': 'TRANSLATED_TITLE',
                     'language': 'fr',
                     },
                    {
                        'type': 'TRANSLATED_SUBTITLE',
                        'value': u"""part 15: guidance on the preservation and handling of sludge""",
                        'language': 'fr',
                    }
                ],
            })
