# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 John Paulett (john -at- paulett.org)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""Helper functions for pickling and unpickling.  Most functions assist in
determining the type of an object.
"""
from cpython.type cimport PyType_Check
from cpython.function cimport PyFunction_Check
from cpython.method cimport PyMethod_Check
from cpython.object cimport PyObject_IsInstance, PyObject_HasAttrString, \
    PyCallable_Check, PyObject_GetAttrString, PyObject_TypeCheck, \
    PyObject_Type
from cpython.long cimport PyLong_Check
from cpython.int cimport PyInt_Check
from cpython.float cimport PyFloat_Check
from cpython.string cimport PyString_Check, PyString_CheckExact
from cpython.unicode cimport PyUnicode_Check, PyUnicode_CheckExact
from cpython.set cimport PyAnySet_CheckExact, PyAnySet_Check
from cpython.tuple cimport PyTuple_Check, PyTuple_CheckExact
from cpython.list cimport PyList_Check, PyList_CheckExact
from cpython.dict cimport PyDict_Check, PyDict_CheckExact
from cpython.mapping cimport PyMapping_Check
from cpython.module cimport PyModule_Check
from cpython.version cimport PY_MAJOR_VERSION
cdef extern from 'Python.h':
    bint PyClass_Check(object obj)
    bint PyFile_Check(object obj)

from base64 import b64encode, b64decode
import collections
from io import IOBase
import operator
import time
import types
import sys

from UserDict import UserDict
from jsonpickle.compat import set, unicode, long, PY3
from jsonpickle import tags


cpdef inline bint is_type(object obj):
    """Returns True is obj is a reference to a type.

    >>> is_type(1)
    False

    >>> is_type(object)
    True

    >>> class Klass: pass
    >>> is_type(Klass)
    True
    """
    if PyType_Check(obj):
        return True
    if PyClass_Check(obj):
        return True
    return False


cpdef inline bint is_object(object obj):
    """Returns True is obj is a reference to an object instance.

    >>> is_object(1)
    True

    >>> is_object(object())
    True

    >>> is_object(lambda x: 1)
    False
    """
    if PyType_Check(obj):
        return False
    if PyFunction_Check(obj):
        return False
    if not PyObject_IsInstance(obj, object):
        return False
    return True


cpdef inline bint is_primitive(object obj):
    """Helper method to see if the object is a basic data type. Strings,
    integers, longs, floats, booleans, and None are considered primitive
    and will return True when passed into *is_primitive()*

    >>> is_primitive(3)
    True
    >>> is_primitive([4,4])
    False
    """
    if obj is None:
        return True
    if PyInt_Check(obj):
        return True
    if PyFloat_Check(obj):
        return True
    if PyLong_Check(obj):
        return True
    if PyString_CheckExact(obj):
        return True
    if PyUnicode_CheckExact(obj):
        return True
    return False


cpdef inline bint is_dictionary(object obj):
    """Helper method for testing if the object is a dictionary.

    >>> is_dictionary({'key':'value'})
    True

    """
    return PyDict_CheckExact(obj)


cpdef inline bint is_sequence(object obj):
    """Helper method to see if the object is a sequence (list, set, or tuple).

    >>> is_sequence([4])
    True

    """
    if is_list(obj):
        return True
    if is_tuple(obj):
        return True
    if is_set(obj):
        return True
    return False


cpdef inline bint is_list(object obj):
    """Helper method to see if the object is a Python list.

    >>> is_list([4])
    True
    """
    return PyList_CheckExact(obj)


cpdef inline bint is_set(object obj):
    """Helper method to see if the object is a Python set.

    >>> is_set(set())
    True
    """
    return PyAnySet_CheckExact(obj)


cpdef inline bint is_tuple(object obj):
    """Helper method to see if the object is a Python tuple.

    >>> is_tuple((1,))
    True
    """
    return PyTuple_CheckExact(obj)


cpdef inline bint is_dictionary_subclass(object obj):
    """Returns True if *obj* is a subclass of the dict type. *obj* must be
    a subclass and not the actual builtin dict.

    >>> class Temp(dict): pass
    >>> is_dictionary_subclass(Temp())
    True
    """
    if is_dictionary(obj):
        return False
    if PyDict_Check(obj):
        return True
    if PyObject_IsInstance(obj, UserDict):
        return True
    return False


cpdef inline bint is_sequence_subclass(object obj):
    """Returns True if *obj* is a subclass of list, set or tuple.

    *obj* must be a subclass and not the actual builtin, such
    as list, set, tuple, etc..

    >>> class Temp(list): pass
    >>> is_sequence_subclass(Temp())
    True
    """
    if PyList_Check(obj):
        return not is_list(obj)
    if PyTuple_Check(obj):
        return not is_tuple(obj)
    if PyAnySet_Check(obj):
        return not is_set(obj)
    if is_list_like(obj):
        return True
    return False


cpdef inline bint is_noncomplex(object obj):
    """Returns True if *obj* is a special (weird) class, that is more complex
    than primitive data types, but is not a full object. Including:

        * :class:`~time.struct_time`
    """
    return PyObject_IsInstance(obj, time.struct_time)


cpdef inline bint is_function(object obj):
    """Returns true if passed a function

    >>> is_function(lambda x: 1)
    True

    >>> is_function(locals)
    True

    >>> def method(): pass
    >>> is_function(method)
    True

    >>> is_function(1)
    False
    """
    if PyFunction_Check(obj):
        return True
    if PyMethod_Check(obj):
        return True
    # only True for old-style classes without a '__class__' property
    if PyClass_Check(obj):
        return False
    obj_class = obj.__class__
    if obj_class.__module__ not in ('__builtin__', 'exceptions', 'builtins'):
        return False
    name = obj_class.__name__
    return name in ('function', 'builtin_function_or_method', 'instancemethod', 'method-wrapper')


cpdef inline bint is_module_function(object obj):
    """
    Return True if `obj` is a module-global function.

    >>> import os
    >>> is_module_function(os.path.exists)
    True

    >>> is_module_function(lambda: None)
    False
    """
    # only True for old-style classes without a '__class__' property
    if PyClass_Check(obj):
        return False
    if not PyFunction_Check(obj):
        return False
    if not PyObject_HasAttrString(obj, '__module__'):
        return False
    if obj.__name__ == '<lambda>':
        return False
    return True


cpdef inline bint is_module(object obj):
    """Returns True if passed a module

    >>> import os
    >>> is_module(os)
    True

    """
    return PyModule_Check(obj)


cpdef bint is_picklable(object name, object value):
    """Return True if an object can be pickled

    >>> import os
    >>> is_picklable('os', os)
    True

    >>> def foo(): pass
    >>> is_picklable('foo', foo)
    True

    >>> is_picklable('foo', lambda: None)
    False

    """
    if name in tags.RESERVED:
        return False
    if is_module_function(value):
        return True
    if is_function(value):
        return False
    return True


cpdef bint is_installed(str module):
    """Tests to see if ``module`` is available on the sys.path

    >>> is_installed('sys')
    True
    >>> is_installed('hopefullythisisnotarealmodule')
    False

    """
    if module in sys.modules:
        return True
    try:
        __import__(module)
        return True
    except ImportError:
        return False


cpdef inline bint is_list_like(object obj):
    if not PyObject_HasAttrString(obj, '__getitem__'):
        return False
    return PyObject_HasAttrString(obj, 'append')


cpdef bint is_iterator(object obj):
    if not PyObject_IsInstance(obj, collections.Iterator):
        return False
    if PyFile_Check(obj):
        return False
    if PyObject_IsInstance(obj, IOBase):
        return False
    return True


cpdef bint is_reducible(object obj):
    """
    Returns false if of a type which have special casing, and should not have their
    __reduce__ methods used
    """
    if is_list(obj):
        return False
    if is_list_like(obj):
        return False
    if is_primitive(obj):
        return False
    if is_dictionary(obj):
        return False
    if is_sequence(obj):
        return False
    if is_set(obj):
        return False
    if is_tuple(obj):
        return False
    if is_dictionary_subclass(obj):
        return False
    if is_sequence_subclass(obj):
        return False
    if is_noncomplex(obj):
        return False
    if is_function(obj):
        return False
    if is_module(obj):
        return False
    if obj is object:
        return False
    if type(obj) is object:
        return False
    if is_type(obj) and obj.__module__ == 'datetime':
        return False
    return True


cpdef bint in_dict(object obj, object key, bint default=False):
    """
    Returns true if key exists in obj.__dict__; false if not in.
    If obj.__dict__ is absent, return default
    """
    cdef object obj_dict
    if not PyObject_HasAttrString(obj, '__dict__'):
        return default
    obj_dict = PyObject_GetAttrString(obj, '__dict__')
    return key in obj_dict


cpdef bint in_slots(object obj, object key, bint default=False):
    """
    Returns true if key exists in obj.__slots__; false if not in.
    If obj.__slots__ is absent, return default
    """
    cdef object obj_slots
    if not PyObject_HasAttrString(obj, '__slots__'):
        return default
    obj_slots = PyObject_GetAttrString(obj, '__slots__')
    return key in obj_slots


cpdef tuple has_reduce(object obj):
    """
    Tests if __reduce__ or __reduce_ex__ exists in the object dict or
    in the class dicts of every class in the MRO *except object*.

    Returns a tuple of booleans (has_reduce, has_reduce_ex)
    """
    if is_type(obj):
        return (False, False)
    if not is_reducible(obj):
        return (False, False)

    cdef tuple base_types = type(obj).__mro__
    cdef bint has_reduce = False
    cdef bint has_reduce_ex = False
    cdef str REDUCE = '__reduce__'
    cdef str REDUCE_EX = '__reduce_ex__'

    has_reduce = in_dict(obj, REDUCE)
    has_reduce_ex = in_dict(obj, REDUCE_EX)
    if not has_reduce:
        has_reduce = has_reduce or in_slots(obj, REDUCE)
        has_reduce_ex = has_reduce_ex or in_slots(obj, REDUCE_EX)
    for base in base_types:
        if is_reducible(base):
            has_reduce = has_reduce or in_dict(base, REDUCE)
            has_reduce_ex = has_reduce_ex or in_dict(base, REDUCE_EX)
        if has_reduce and has_reduce_ex:
            return (True, True)

    return (has_reduce, has_reduce_ex)


cpdef object translate_module_name(object module):
    """Rename builtin modules to a consistent (Python2) module name

    This is used so that references to Python's `builtins` module can
    be loaded in both Python 2 and 3.  We remap to the "__builtin__"
    name and unmap it when importing.

    See untranslate_module_name() for the reverse operation.

    """
    if module == 'exceptions':
        return '__builtin__'
    if module == 'builtins' and PY_MAJOR_VERSION == 3:
        return '__builtin__'
    return module


cpdef object untranslate_module_name(object module):
    """Rename module names mention in JSON to names that we can import

    This reverses the translation applied by translate_module_name() to
    a module name available to the current version of Python.

    """
    if PY_MAJOR_VERSION != 3:
        return module
    if module in ('__builtin__', 'exceptions'):
        return 'builtins'
    return module


cpdef inline str importable_name(object cls):
    """
    >>> class Example(object):
    ...     pass

    >>> ex = Example()
    >>> importable_name(ex.__class__)
    'jsonpickle.util.Example'

    >>> importable_name(type(25))
    '__builtin__.int'

    >>> importable_name(None.__class__)
    '__builtin__.NoneType'

    >>> importable_name(False.__class__)
    '__builtin__.bool'

    >>> importable_name(AttributeError)
    '__builtin__.AttributeError'

    """
    cdef str name = cls.__name__
    cdef str module = translate_module_name(cls.__module__)
    return '{0}.{1}'.format(module, name)


cpdef object itemgetter(object obj, object getter=None):
    if getter is None:
        getter = operator.itemgetter(0)
    return unicode(getter(obj))
