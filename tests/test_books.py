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
    record = model.do(blob, ignore_missing=False)
    expected = {
        '$schema': {
            '$ref': ('records/books/book/book-v.0.0.1.json')
        }
    }
    expected.update(**json_body)
    assert record == expected


def test_acquisition(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="916" ind1=" " ind2=" ">
                <subfield code="s">h</subfield>
                <subfield code="w">201829</subfield>
                </datafield>
            """, {
                'acquisition_source': {'datetime': '2018-07-16'},
            })


def test_collections(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">LEGSERLIB</subfield>
            </datafield>
            """, {
                '_collections': ['LEGSERLIB'],
            })
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            """, {
                '_collections': ['LEGSERLIB'],
            })


def test_document_type(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            """, {
                'document_type': 'BOOK',
            })
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">21</subfield>
            </datafield>
            """, {
                'document_type': 'BOOK',
            })
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">42</subfield>
            </datafield>
            """, {
                'document_type': 'PROCEEDINGS',
            })
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">43</subfield>
            </datafield>
            """, {
                'document_type': 'PROCEEDINGS',
            })


def test_document_type_collection(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">LEGSERLIB</subfield>
            </datafield>
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            """, {
                '_collections': ['LEGSERLIB'],
                'document_type': 'BOOK',
            })
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">BOOK</subfield>
            </datafield>
            """, {
                '_collections': ['LEGSERLIB'],
                'document_type': 'BOOK',
            })


def test_urls(app):
    with app.app_context():
        # TODO
        # check_transformation(
        #     """
        #     <datafield tag="960" ind1=" " ind2=" ">
        #         <subfield code="a">42</subfield>
        #     </datafield>
        #     """, {
        #         'document_type': 'PROCEEDINGS',
        #         'urls': ['cds.cern.ch'],
        #     })
        check_transformation(
            """
            <datafield tag="8564" ind1=" " ind2=" ">
                <subfield code="u">cds.cern.ch</subfield>
            </datafield>
            """, {
                'urls': ['cds.cern.ch'],
            })


def test_acquisition_email(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="859" ind1=" " ind2=" ">
                <subfield code="f">karolina.przerwa@cern.ch</subfield>
            </datafield>
            """, {
                'acquisition_source': {'email': 'karolina.przerwa@cern.ch'},
            })
        check_transformation(
            """
            <datafield tag="916" ind1=" " ind2=" ">
                <subfield code="s">h</subfield>
                <subfield code="w">201829</subfield>
            </datafield>
            <datafield tag="859" ind1=" " ind2=" ">
                <subfield code="f">karolina.przerwa@cern.ch</subfield>
            </datafield>
            """, {
                'acquisition_source': {'datetime': '2018-07-16',
                                       'email': 'karolina.przerwa@cern.ch'},
            })


def test_authors(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Frampton, Paul H</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Glashow, Sheldon Lee</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Van Dam, Hendrik</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            """, {
                'authors': [{'full_name': 'Frampton, Paul H',
                             'role': 'editor'},
                            {'full_name': 'Glashow, Sheldon Lee',
                             'role': 'editor'},
                            {'full_name': 'Van Dam, Hendrik',
                             'role': 'editor'},
                            ],
            })


# better example to be provided
def test_corporate_author(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="710" ind1=" " ind2=" ">
                <subfield code="a"> Springer</subfield>
            </datafield>
            """, {
                'corporate_authors': 'Springer',
            })


def test_collaborations(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="710" ind1=" " ind2=" ">
                <subfield code="5">PH-EP</subfield>
            </datafield>
            <datafield tag="710" ind1=" " ind2=" ">
                <subfield code="g">ATLAS Collaboration</subfield>
            </datafield> 
                """,
            {'collaborations': ['PH-EP', 'ATLAS']}
        )


# def test_publication_info(app):
#     with app.app_context():
#         check_transformation(
#             """
#             <datafield tag="773" ind1=" " ind2=" ">
#                 <subfield code="c">1692-1695</subfield>
#                 <subfield code="n">10</subfield>
#                 <subfield code="y">2007</subfield>
#                 <subfield code="p">Radiat. Meas.</subfield>
#                 <subfield code="v">42</subfield>
#             </datafield>
#             """
#         )
