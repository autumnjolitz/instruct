Instruct
==========

Attempt to serve multiple masters:

    - Strictly-typed ability to define fixed data objects
    - Ability to drop all of the above type checks
    - Track changes made to the object as well as reset
    - Native support of pickle/json

Callgraph Performance
-----------------------

.. class:: no-web

    .. image:: https://raw.githubusercontent.com/autumnjolitz/Instruct/master/callgraph.png
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