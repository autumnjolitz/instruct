Instruct
==========

A compact, fast object system that can serve as the basis for a DAO model.

To that end, instruct uses ``__slots__`` to prevent new attribute addition, properties to control types, event listeners and historical changes, and a Jinja2-driven codegen to keep a pure-Python implementation as fast and as light as possible.

I want to basically have a form of strictly typed objects that behave like C structs but can handle automatically coercing incoming values correctly, have primitive events and have fast ``__iter__``, ``__eq__`` while also allowing for one to override it in the final class (and even call super!)

This girl asks for a lot but I like taking metaclassing as far as it can go without diving into using macropy. 😉


Current Capabilities:

    - Support multiple inheritance, chained fields and ``__slots__`` [Done]
    - Support type coercions (via ``_coerce__``) [Done]
    - Strictly-typed ability to define fixed data objects [Done]
    - Ability to drop all of the above type checks [Done]
    - Track changes made to the object as well as reset [Done]
    - Fast ``__iter__`` [Done]
    - Native support of pickle [Done]/json [Done]
    - Support List[type] declarations and initializations [Done]
    - optionally data class annotation-like behavior [Done]
    - ``_asdict``, ``_astuple``, ``_aslist`` functions like in a NamedTuple [Done]
    - ``get``, ``keys``, ``values``, ``item`` functions available in the module and in a mixin named ``mapping=True``
        + This effectively allows access like other packages e.g. ``attrs.keys(item_instance)``
    - ``bytes``/``bytearray`` are urlsafe base64 encoded by default, can override per field via a class level ``BINARY_JSON_ENCODERS = {key: encoding_function}`` [Done]
    - Allow ``__coerce__`` to have a tuple of field names to avoid repetition on ``__coerce__`` definitions [Done]
    - Allow use of ``Literal`` in the type (exact match of a value to a vector of values) [Done]
    - Allow subtraction of properties like ``(F - {"a", "b"}).keys() == F_without_a_b.keys()`` [Done]
        + This will allow one to slim down a class to a restricted subtype, like for use in a DAO system to load/hold less data.
    - Allow subtraction of properties like ``(F - {"a": {"b"}).keys() == F_a_without_b.keys()`` [Done]
        + This allows for one to remove fields that are unused prior to class initialization.
    - Allow subtraction of properties via an inclusive list like ``(F & {"a", "b"}).keys() == F_with_only_a_and_b.keys()`` [Done]
    - Allow subtraction to propagate to embedded Instruct classes like ``(F - {"a.b", "a.c"}).a.keys() == (F_a.keys() - {"b", "c"))`` [Done]
        + This would really allow for complex trees of properties to be rendered down to thin SQL column selects, thus reducing data load.
    - Replace references to an embedded class in a ``__coerce__`` function with the subtracted form in case of embedded property subtractions [Done]
    - Allow use of Annotated i.e. ``field: Annotated[int, NoJSON, NoPickle]`` and have ``to_json`` and ``pickle.dumps(...)`` skip "field" [Done]
        + Would grant a more powerful interface to controlling code-gen'ed areas via ``cls._annotated_metadata`` (maps field -> what's inside the ``Annotation``)

Next Goals:
    - Allow Generics i.e. ``class F(instruct.Base, T): ...`` -> ``F[str](...)``
        + Would be able to allow specialized subtypes
    - ``CStruct``-Base class that operates on an ``_cvalue`` cffi struct.
    - Cython compatibility


Design Goal
-------------

This comes out of my experience of doing multiple object systems mean to represent database relations and business rules. One thing that has proven an issue is the requirements for using as little memory as possible, as little CPU as possible yet prevent the developer from trying to stick a string where a integer belongs.

Further complicating this model is that desire to "correct" data as it comes in. Done correctly, it is possible to feed an ``instruct.Base``-derived class fields that are not of the correct data type but are eligible for being coerced (converted) into the right type with a function. With some work, it'll be possible to inline a ``lambda val: ...`` expression directly into the setter function code.

Finally, multiple inheritance is a must. Sooner or later, you end up making a single source implementation for a common behavior shared between objects. Being able to share business logic between related implementations is a wonderful thing.


Wouldn't it be nice to define a heirachy like this:

.. code-block:: python

    import pickle
    import datetime
    from typing import List

    try:
        from typing import Annotated
    except ImportError:
        from typing_extensions import Annotated
    from instruct import Base, NoJSON, NoIterable, NoPickle, NoHistory


    class Member(Base):
        __slots__ = {"first_name": str, "last_name": str, "id": int}

        def _set_defaults(self):
            self.first_name = self.last_name = ""
            self.id = -1
            super()._set_defaults()


    class Organization(Base, history=True):
        # ARJ: Note how we can also use the dataclass/typing.NamedTuple
        # definition format and it behaves just like the ``__slots__`` example
        # above!
        name: str
        id: int
        members: List[Member]
        created_date: datetime.datetime
        secret: Annotated[str, NoJSON, NoPickle, NoIterable, NoHistory]

        __coerce__ = {
            "created_date": (str, lambda obj: datetime.datetime.strptime("%Y-%m-%d", obj)),
            "members": (List[dict], lambda values: [Member(**value) for value in values]),
        }

        def _set_defaults(self):
            self.name = ""
            self.id = -1
            self.members = []
            self.created_date = datetime.datetime.utcnow()
            super()._set_defaults()


And have it work like this?

.. code-block:: python

    data = {
        "name": "An Org",
        "id": 123,
        "members": [{"id": 551, "first_name": "Jinja", "last_name": "Ninja"}],
    }
    org = Organization(secret="my secret", **data)
    assert org.members[0].first_name == "Jinja"
    assert org.secret == "my secret"
    org.name = "New Name"
    org.created_date = datetime.datetime(2018, 10, 23)
    print(tuple(org.list_changes()))
    # Returns
    # (
    #     LoggedDelta(timestamp=1652412832.7408261, key='name', delta=Delta(state='default', old=Undefined, new='', index=0)), 
    #     LoggedDelta(timestamp=1652412832.7408261, key='id', delta=Delta(state='default', old=Undefined, new=-1, index=0)), 
    #     LoggedDelta(timestamp=1652412832.7408261, key='members', delta=Delta(state='default', old=Undefined, new=[], index=0)), 
    #     LoggedDelta(timestamp=1652412832.7408261, key='created_date', delta=Delta(state='default', old=Undefined, new=datetime.datetime(2022, 5, 13, 3, 33, 52, 740650), index=0)), 
    #     LoggedDelta(timestamp=1652412832.740923, key='id', delta=Delta(state='initialized', old=-1, new=123, index=4)), 
    #     LoggedDelta(timestamp=1652412832.741002, key='members', delta=Delta(state='initialized', old=[], new=[<__main__.Member._Member object at 0x104364640>], index=5)), 
    #     LoggedDelta(timestamp=1652412832.741009, key='name', delta=Delta(state='initialized', old='', new='An Org', index=6)), 
    #     LoggedDelta(timestamp=1652412832.741021, key='name', delta=Delta(state='update', old='An Org', new='New Name', index=7)), 
    #     LoggedDelta(timestamp=1652412832.741031, key='created_date', delta=Delta(state='update', old=datetime.datetime(2022, 5, 13, 3, 33, 52, 740650), new=datetime.datetime(2018, 10, 23, 0, 0), index=8))
    # )

    assert not any(y == "my secret" for y in tuple(org))
    assert Organization.to_json(org) == {
        "created_date": "2018-10-23T00:00:00",
        "id": 123,
        "members": [{"first_name": "Jinja", "id": 551, "last_name": "Ninja"}],
        "name": "New Name",
    }
    org2 = pickle.loads(pickle.dumps(org))
    assert org2.secret is None
    assert org2.to_json() == {
        "created_date": "2018-10-23T00:00:00",
        "id": 123,
        "members": [{"first_name": "Jinja", "id": 551, "last_name": "Ninja"}],
        "name": "New Name",
    }


Example Usage
^^^^^^^^^^^^^^^

.. code-block:: pycon

    >>> from instruct import Base
    >>>
    >>> class MyClass(Base):
    ...     foo: int
    ...     bar: Optional[str]
    ...     baz: Union[Dict[str, str], int]
    ...     def __eq__(self, other):
    ...         if isinstance(other, tuple) and len(other) == 3:
    ...            # Cast the tuple to this type!
    ...            other = MyClass(*other)
    ...         return super().__eq__(other)
    ...
    >>> instance = MyClass(1, None, baz={"a": "a"})
    >>> assert instance.foo == 1
    >>> assert instance.bar is None
    >>> instance.bar = "A String!"
    >>>
    >>> assert instance == (1, "A String!", {"a": "a"})
    >>>
    >>> instance.foo = 'I should not be allowed'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<getter-setter>", line 36, in _set_foo
    TypeError: Unable to set foo to 'I should not be allowed' (str). foo expects a int
    >>>


Instruct adds a ``Range`` type for use in ``Annotated[...]`` type definitions.

Range
^^^^^^^^

.. code-block:: python

        class Range(lower, upper, flags: RangeFlags = <RangeFlags.CLOSED_OPEN: 4>, *, type_restrictions: Tuple[Type, ...]=())
            ...

``lower`` and ``upper`` can be anything that supports ``__lt__``, ``__gt__``, ``__eq__``.

``type_restrictions`` can be used to apply a Range constraint to some value types.

``flags`` can be used to set the `interval type <https://en.wikipedia.org/wiki/Interval_(mathematics)>`_. Default is closed-open [).

.. code-block:: pycon

    >>> from typing import Tuple, type
    >>> from instruct import Range, RangeFlags, RangeError
    >>> lower, upper = 0, 255
    >>> r = Range(lower, upper, flags: RangeFlags = RangeFlags.CLOSED_OPEN)
    >>> 10 in r
    True
    >>> 0 in r
    True
    >>> 256 in r
    False

When used inside an ``instruct``-derived class, an attempt to assign a value that doesn't satisfy a tuple of ranges will throw a RangeError (inherits from ValueError and TypeError).

Inside is the ``value`` (what was rejected) and a copy of the ranges at ``ranges`` that were tried (and failed). If the ``type_restrictions`` are specified in a range, it will not be tried if the value type isn't applicable.

.. code-block:: python

        class RangeError(value: Any, ranges: Tuple[Range, ...], message: str="")
            ...


Example:

.. code-block:: pycon

    >>> from instruct import SimpleBase, Range
    >>> from typing_extensions import Annotated
    >>> from typing import Union
    >>> class Planet(SimpleBase):
    ...     mass_kg: Annotated[Union[float, int], Range(600 * (10**18), 1.899e27)]
    ...     radius_km: Annotated[Union[float, int], Range(2439.766, 142_800)]
    ...
    >>>
    >>> mercury = Planet(3.285 * (10**23), 2439.766)
    >>> mars = Planet(0.64169 * (10**24), 3376.2)
    >>>
    >>> pluto = Planet(1.30900 * (10**22), 1188.30742)
    Traceback (most recent call last):
      File "/Users/autumn/software/instruct/instruct/__init__.py", line 2113, in __init__
        setattr(self, key, value)
      File "<getter-setter>", line 30, in _set_radius_km
      File "/Users/autumn/software/instruct/instruct/typedef.py", line 40, in __instancecheck__
        return func(instance)
      File "/Users/autumn/software/instruct/instruct/typedef.py", line 227, in test_func
        raise RangeError(value, failed_ranges)
    instruct.exceptions.RangeError: ('Unable to fit 1188.30742 into [2439.766, 142800)', 1188.30742, (Range(2439.766, 142800, flags=CLOSED_OPEN, type_restrictions=()),))

    The above exception was the direct cause of the following exception:

    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/autumn/software/instruct/instruct/__init__.py", line 2128, in __init__
        self._handle_init_errors(errors, errored_keys, unrecognized_keys)
      File "/Users/autumn/software/instruct/instruct/__init__.py", line 2094, in _handle_init_errors
        ) from errors[0]
    instruct.exceptions.ClassCreationFailed: ('Unable to construct Planet, encountered 1 error', RangeError('Unable to fit 1188.30742 into [2439.766, 142800)', 1188.30742, (Range(2439.766, 142800, flags=CLOSED_OPEN, type_restrictions=()),)))
    >>> 


Comparison to Pydantic
-------------------------

Pydantic is a much larger project with many more eyes. Instruct was designed from the beginning to support multiple-inheritance and ``__slot__`` specialization. Pydantic does much the same as Instruct. Pydantic is much more feature-filled and infinitely more popular. Instruct is a one-woman crew.

Instruct was a reflexive response to years of dealing with needing to handle Object-Relational impedance mismatch in MySQL/Postgres. It was meant as a building block for enabling templated SQL writing in a controlled manner without resorting to ORMs (more akin to DAO approach). As such, its design and evolution reflects that.

Instruct is not better. Nor is it worse. Instruct simply does what it's designed to do and no more.

I suggest you use Pydantic if you're interested in a far bigger, far more lively, far better supported library. Instruct has different ambitions and does not intend to replace or compete with Pydantic.

Instruct was designed in October 7, 2017 but was released in Dec 9, 2018.

Pydantic's earliest release (0.1.0) is in 2017-06-03.

Design differences between the two:

- Instruct attempts to **NOT** provide functions/attributes that may be clobbered via ``SimpleBase`` and remapping the public variables to ``_{{varname}}_``
    + Pydantic allows one to override the remapping, but does occupy names like ``dict``, ``json``, etc,.
- Pydantic provides ``Model`` properties like ``dict()``, ``json()``, ``copy()``, etc
    + Instruct ``Base`` (via ``JSONSerializable``) provides ``to_json``, ``__json__``, ``from_json``, ``from_many_json``
    + If you use ``SimpleBase``, you can access similar properties ONLY on the class itself (we do not attach it to the class instance to avoid clobbering)
- Instruct is shifting to a paradigm of using free-functions like ``asdict``, ``astuple``, ``keys``, ``items``, ``values``, etc instead of clobbering fields on an object
    + we want to allow as many user-specified names as possible
- Instruct wants to remain small
- Instruct wants to support ``CStruct``s and possible basis for using a ``bytearray`` as the underlying memory for enabling rich types while allowing a near ``memcpy``.

Things Instruct can do that Pydantic doesn't:

- Class subtraction and masking
    + You can subtract out a field by a string represetation, multiple by subtracting out an ``Iterable[str]``, or even apply such via a nested dict (where the values are ``None`` or another mapping to apply to a sub-object)
    + You can ``cls & {"field"}`` or ``cls & {"field": {"keep_this"}}`` and get a class with only ``field`` and ``field.keep_this``
- Allows unsupported types by fields to call functions to parse/coerce it into a valid value (``__coerce__``)
    + Pydantic suggests you use ``Data bind`` to handle weirdies
    + Pydantic does a lot of conversions for you automatically
    + Instruct demands you make them explicit in your handling functions.
- Instruct creates custom types representing complex, nested data structures such it does an effect ``isinstance(value, ComplexType)`` to verify if a complex, nested tree of objects does match.
    + The types are meant only for an ``isinstance`` check.

Things Pydantic does that Instruct doesn't:

- Discriminated Unions (Current approach in Instruct is to add the common class into the Union and specialize after ``__init__`` or do it in the ``__coerce__`` phase)
- Type/Callable/Generator attribute assignment
- Generics (on my todo)
- validation (instruct is used to provide the building blocks for validation, not doing it by itself. That might change.)
- actual mypy, vscode, pycharm, etc integration
- schema export
- aliases (Instruct expects you to just add a ``@property`` that gets/sets the true field)
- lots more little goodies



Design
----------

Solving the multiple-inheritance and ``__slots__`` problem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Consider the following graph::

    Base1    Base2
         \  /
       Class A

If both defined ``__slots__ = ()``, Class A would be able to declare ``__slots__`` to hold variables. For now on, we shall consider both Base's to have ``__slots__ = ()`` for simplicity.

However, consider this case::

    Base1    Base2
         \  /
       Class A     Class B
              \    /
              Class C

Now this isn't possible if Class A has non-empty ``__slots__``.

But what if we could change the rules. What if, somehow, when you ``__new__`` ed a class, it really gave you a specialized form of the class with non-empty ``__slots__``?

Such a graph may look like this::

    Base1    Base2
         \  /
       Class A     Class B
          |  \    /     |
    Class _A  Class C  Class _B
                |
              Class _C

Now it is possible for any valid multiple-inheritance chain to proceed, provided it respects the above constraints - there are either support classes or data classes (denoted with an underscore in front of their class name). Support classes may be inherited from, data classes cannot.


Solving the Slowness issue
*****************************

I've noticed that there are constant patterns of writing setters/getters and other related functions. Using Jinja2, we can rely on unhygenic macros while preserving some semblance of approachability. It's more likely a less experienced developer could handle blocks of Jinja-fied Python than AST synthesis/traversal.

Callgraph Performance
-----------------------

.. class:: no-web

    .. image:: https://raw.githubusercontent.com/benjolitz/Instruct/master/callgraph.png
        :alt: Callgraph of project
        :width: 100%
        :align: center


.. class:: no-web no-pdf

Release Process
-----------------

::

    $ rm -rf dist/* && python -m pytest tests/ && python setup.py sdist bdist_wheel && twine upload dist/*


Benchmark
--------------


Latest benchmark run:::

    (python) Fateweaver:~/software/instruct [master]$ python --version
    Python 3.7.7
    (python) Fateweaver:~/software/instruct [master]$ python -m instruct benchmark
    Overhead of allocation, one field, safeties on: 19.53us
    Overhead of allocation, one field, safeties off: 19.50us
    Overhead of setting a field:
    Test with safeties: 0.27 us
    Test without safeties: 0.17 us
    Overhead of clearing/setting
    Test with safeties: 0.75 us
    Test without safeties: 0.65 us
    (python) Fateweaver:~/software/instruct [master]$




Before additions of coercion, event-listeners, multiple-inheritance

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

After additions of those. Safety is expensive.

::

    $ python -m instruct benchmark
    Overhead of allocation, one field, safeties on: 19.25us
    Overhead of allocation, one field, safeties off: 18.98us
    Overhead of setting a field:
    Test with safeties: 0.36 us
    Test without safeties: 0.22 us
    Overhead of clearing/setting
    Test with safeties: 1.29 us
    Test without safeties: 1.14 us
