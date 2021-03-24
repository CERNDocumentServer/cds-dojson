========
 DoJSON
========

.. image:: https://img.shields.io/travis/CERNDocumentServer/cds-dojson.svg
        :target: https://travis-ci.org/CERNDocumentServer/cds-dojson

.. image:: https://img.shields.io/coveralls/CERNDocumentServer/cds-dojson.svg
        :target: https://coveralls.io/r/CERNDocumentServer/cds-dojson

.. image:: https://img.shields.io/github/tag/CERNDocumentServer/cds-dojson.svg
        :target: https://github.com/CERNDocumentServer/cds-dojson/releases

.. image:: https://coveralls.io/repos/CERNDocumentServer/cds-dojson/badge.svg?branch=master&service=github
        :target: https://coveralls.io/github/CERNDocumentServer/cds-dojson?branch=master

.. image:: https://img.shields.io/github/license/CERNDocumentServer/cds-dojson.svg
        :target: https://github.com/CERNDocumentServer/cds-dojson/blob/master/LICENSE


Development
===========
Install your checked out code: ::

  pip install -e .[all]

Do your desired changes in the **yml** files.
Build using a python 3.6 or greater to avoid shuffling properties.
Keep the trailing slashes on the commands below.

Build the source schemas from yml files: ::

  cds-dojson convert-yaml2json <path_to_yml_source_folder>/ <path_to_json_destination_folder>/

Build the final schemas from definitions: ::

  cds-dojson compile-schema <path_to_-src-_schema>/ > output_file.json

Installation
============


Documentation
=============
Documentation can be built using Sphinx: ::

  pip install cds-dojson[docs]
  python setup.py build_sphinx


Testing
=======

Running the test suite is as simple as: ::

  python setup.py test
