

============================
 Testing and Specifications
============================


.. toctree::
   :maxdepth: 2

   unit-and-functional
   spec-by-example
   naming-conventions



Overview
========

We have a quite big test suite inside of :file:`rhodecode/tests` which is a mix
of unit tests and functional or integration tests. More details are in
:ref:`test-unit-and-functional`.


Apart from that we start to apply "Specification by Example" and maintain a
collection of such specifications together with an implementation so that it can
be validated in an automatic way. The files can be found in
:file:`acceptance_tests`. More details are in :ref:`test-spec-by-example`.
