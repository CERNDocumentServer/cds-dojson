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


About
=====



Installation
============
  `python setup.py install`

Usage
=====
  > Attention! The deposit schemas, inherit from the record schemas.
   First build `schemas/records/videos...` and then `schemas/deposits/records...`

  Schemas are generated from their `*_src.json` file, navigate to src path and execute

  `$ cds-dojson compile_schema project_src-v1.0.0.json > project-v1.0.0.json`


Documentation
=============

Documentation can be built using Sphinx: ::

  pip install cds-dojson[docs]
  python setup.py build_sphinx

Testing
=======

Running the test suite is as simple as: ::

  python setup.py test
