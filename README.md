[![Build Status](https://travis-ci.org/nicwest/indj.svg?branch=master)](https://travis-ci.org/nicwest/indj)
[![Coverage Status](https://coveralls.io/repos/nicwest/indj/badge.svg)](https://coveralls.io/r/nicwest/indj)
indj
====

command line lookup for django objects

Tests
-----

Run tests with py.test or tox:

```
pip install pytest pytest-cov
pip install -e .
py.test --cov indj
```

Or:

```
pip install tox
tox
```

Indj is tested with python 2.7 and 3.4 and against djangp 1.5, 1.6, 1.7 and 1.8
