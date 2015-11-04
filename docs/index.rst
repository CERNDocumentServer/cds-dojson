..
  This file is part of cds_dojson
  Copyright (C) 2015 CERN.

  cds_dojson is free software; you can redistribute it and/or
  modify it under the terms of the Revised BSD License; see LICENSE
  file for more details.

========
 cds_dojson
========
.. currentmodule:: cds_dojson

.. raw:: html

    <p style="height:22px; margin:0 0 0 2em; float:right">
        <a href="https://travis-ci.org/inveniosoftware/cds_dojson">
            <img src="https://travis-ci.org/inveniosoftware/cds_dojson.png?branch=master"
                 alt="travis-ci badge"/>
        </a>
        <a href="https://coveralls.io/r/inveniosoftware/cds_dojson">
            <img src="https://coveralls.io/repos/inveniosoftware/cds_dojson/badge.png?branch=master"
                 alt="coveralls.io badge"/>
        </a>
    </p>

cds_dojson is a simple Pythonic JSON to JSON converter.

Installation
============

cds_dojson is on PyPI so all you need is:

.. code-block:: console

    $ pip install cds_dojson

Example
=======

A simple example on how to convert MARCXML to JSON:

.. code:: python

    from dojson.contrib.marc21.utils import create_record, split_blob
    from dojson.contrib.marc21 import marc21
    [marc21.do(create_record(data)) for data in split_blob(open('/tmp/data.xml', 'r').read())]


API
===

.. automodule:: cds_dojson
    :members:


Contrib
-------

.. automodule:: dojson.marc21
    :members:

.. include:: ../CHANGES.rst

.. include:: ../CONTRIBUTING.rst

.. include:: ../AUTHORS.rst

License
=======

.. include:: ../LICENSE
