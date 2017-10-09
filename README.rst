Instruct
==========

Attempt to serve multiple masters:

    - Support multiple inheritance, chained fields and ``__slots__`` [Done]
    - Support type coercions (via ``_coerce__``) [Done]
    - Strictly-typed ability to define fixed data objects [Done]
    - Ability to drop all of the above type checks [Done]
    - Track changes made to the object as well as reset [Done]
    - Fast ``__iter__`` [Done]
    - Native support of pickle [Done]/json [Partial]
    - ``CStruct``-Base class that operates on an ``_cvalue`` cffi struct.


Callgraph Performance
-----------------------

.. class:: no-web

    .. image:: https://raw.githubusercontent.com/benjolitz/Instruct/master/callgraph.png
        :alt: Callgraph of project
        :width: 100%
        :align: center


.. class:: no-web no-pdf

Benchmark
--------------

::

    $ python -m instruct benchmark
    Overhead of allocation, one field, safeties on: 6.52us
    Overhead of allocation, one field, safeties off: 6.13us
    Overhead of setting a field:
    Test with safeties: 0.40 us
    Test without safeties: 0.22 us
    Overhead of clearing/setting
    Test with safeties: 1.34 us
    Test without safeties: 1.25 us