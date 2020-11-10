Instruct
==========

A compact, fast object system that can serve as the basis for a DAO model.

To that end, instruct uses ``__slots__`` to prevent new attribute addition, properties to control types, event listeners and historical changes, and a Jinja2-driven codegen to keep a pure-Python implementation as fast and as light as possible.

I want to basically have a form of strictly typed objects that behave like C structs but can handle automatically coercing incoming values correctly, have primitive events and have fast ``__iter__``, ``__eq__`` while also allowing for one to override it in the final class (and even call super!)

This girl asks for a lot but I like taking metaclassing as far as it can go without diving into using macropy. 😉


Attempt to serve multiple masters:

    - Support multiple inheritance, chained fields and ``__slots__`` [Done]
    - Support type coercions (via ``_coerce__``) [Done]
    - Strictly-typed ability to define fixed data objects [Done]
    - Ability to drop all of the above type checks [Done]
    - Track changes made to the object as well as reset [Done]
    - Fast ``__iter__`` [Done]
    - Native support of pickle [Done]/json [Done]
    - Support List[type] declarations and initializations [Done]
    - ``CStruct``-Base class that operates on an ``_cvalue`` cffi struct.
    - Cython compatibility
    - optionally data class annotation-like behavior [Done]
    - ``_asdict``, ``_astuple``, ``_aslist`` functions like in a NamedTuple [Done]
    - ``get``, ``keys``, ``values``, ``item`` functions available in the module and in a mixin named ``mapping=True``
        + This effectively allows access like other packages e.g. ``attrs.keys(item_instance)``
    - ``bytes``/``bytearray`` are urlsafe base64 encoded by default, can override per field via a class level ``BINARY_JSON_ENCODERS = {key: encoding_function}`` [Done]
    - Allow ``__coerce__`` to have a tuple of field names to avoid repetition on ``__coerce__`` definitions [Done]

Next Goals:
    - Allow subtraction of properties like ``(F - {"a", "b"}).keys() == F_without_a_b.keys()``
        + This will allow one to slim down a class to a restricted subtype, like for use in a DAO system to load/hold less data.
    - Allow subtration of properties via an inclusive list like ``(F & {"a", "b"}).keys() == F_with_only_a_and_b.keys()``
    - Allow subtration to propagate to embedded Instruct classes like ``(F - {"a.b", "a.c"}).a.keys() == (F_a.keys() - {"b", "c"))``
        + This would really allow for complex trees of properties to be rendered down to thin SQL column selects, thus reducing data load.
    - Allow Generics i.e. ``class F(instruct.Base, T): ...`` -> ``F[str](...)``
        + Would be able to allow specialized subtypes
    - Allow use of Annotated i.e. ``field: Annotated[int, NoJSON, NoPickle]`` and have ``to_json`` and ``pickle.dumps(...)`` skip "field"
        + Would grant a more powerful interface to controlling code-gen'ed areas


Design Goal
-------------

This comes out of my experience of doing multiple object systems mean to represent database relations and business rules. One thing that has proven an issue is the requirements for using as little memory as possible, as little CPU as possible yet prevent the developer from trying to stick a string where a integer belongs.

Further complicating this model is that desire to "correct" data as it comes in. Done correctly, it is possible to feed an ``instruct.Base``-derived class fields that are not of the correct data type but are eligible for being coerced (converted) into the right type with a function. With some work, it'll be possible to inline a ``lambda val: ...`` expression directly into the setter function code.

Finally, multiple inheritance is a must. Sooner or later, you end up making a single source implementation for a common behavior shared between objects. Being able to share business logic between related implementations is a wonderful thing.


Wouldn't it be nice to define a heirachy like this:

.. code-block:: python

    class Member(Base):
        __slots__ = {
            'first_name': str,
            'last_name': str,
            'id': str,
        }
        def __init__(self, **kwargs):
            self.first_name = self.last_name = ''
            self.id = -1
            super().__init__(**kwargs)

    class Organization(Base, history=True):
        # ARJ: Note how we can also use the dataclass/typing.NamedTuple
        # definition format and it behaves just like the ``__slots__`` example
        # above!
        name: str
        id: int
        members: List[Member]
        created_date: datetime.datetime
        secret: Annotated[str, NoJSON, NoPickle, NoIterable]

        __coerce__ = {
            'created_date': (str, lambda obj: datetime.datetime.strptime('%Y-%m-%d', obj))
        }

        def __init__(self, **kwargs):
            self.name = ''
            self.id = -1
            self.members = []
            self.created_date = datetime.datetime.utcnow()
            super().__init__(**kwargs)

And have it work like this?

.. code-block:: python

    data = {
        "name": "An Org",
        "id": 123,
        "members": [
            {
                "id": 551,
                "first_name": "Jinja",
                "last_name": "Ninja",
            }
        ]
    }
    org = Organization(secret="my secret", **data)
    assert org.members[0].first_name == 'Jinja'
    assert org.secret == "my secret"
    org.name = "New Name"
    org.history()
    assert not any(y == "my secret" for y in tuple(org))
    assert Organization.to_json(org) == data


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

    .. image:: https://raw.githubusercontent.com/autumnjolitz/Instruct/master/callgraph.png
        :alt: Callgraph of project
        :width: 100%
        :align: center


.. class:: no-web no-pdf

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
