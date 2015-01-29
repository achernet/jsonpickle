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
from cpython.ref cimport PyObject
cdef extern from 'Python.h':
    bint PyClass_Check(object obj)
    bint PyFile_Check(object obj)
from cpython.type cimport PyType_Check
from cpython.function cimport PyFunction_Check
from cpython.method cimport PyMethod_Check
from cpython.object cimport PyObject_IsInstance, PyObject_HasAttr
from cpython.long cimport PyLong_Check
from cpython.int cimport PyInt_Check
from cpython.float cimport PyFloat_Check
from cpython.string cimport PyString_CheckExact
from cpython.unicode cimport PyUnicode_CheckExact
from cpython.set cimport PyAnySet_CheckExact, PyAnySet_Check
from cpython.tuple cimport PyTuple_Check, PyTuple_CheckExact
from cpython.list cimport PyList_Check, PyList_CheckExact
from cpython.dict cimport PyDict_Check, PyDict_CheckExact, PyDict_Contains
from cpython.module cimport PyModule_Check, PyImport_GetModuleDict

from base64 import b64encode, b64decode
from _io import _IOBase
import operator
import time

from UserDict import UserDict
from jsonpickle import tags


cdef inline bint _is_type(object obj):
    """
    Returns True if obj is a reference to a type.
    """
    if PyType_Check(obj):
        return True
    if PyClass_Check(obj):
        return True
    return False


cpdef bint is_type(object obj):
    """
    Returns True is obj is a reference to a type.
    """
    return _is_type(obj)


cdef inline bint _is_object(object obj):
    """
    Returns True is obj is a reference to an object instance.
    """
    if PyType_Check(obj):
        return False
    if PyFunction_Check(obj):
        return False
    return True


cpdef bint is_object(object obj):
    """
    Returns True is obj is a reference to an object instance.
    """
    return _is_object(obj)


cdef inline bint _is_primitive(object obj):
    """
    Helper method to see if the object is a basic data type. Strings,
    integers, longs, floats, booleans, and None are considered primitive
    and will return True when passed into *is_primitive()*
    """
    if obj is None:
        return True
    # TODO: PyNumber_Check(obj)
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


cpdef bint is_primitive(object obj):
    """
    Helper method to see if the object is a basic data type. Strings,
    integers, longs, floats, booleans, and None are considered primitive
    and will return True when passed into *is_primitive()*
    """
    return _is_primitive(obj)


cdef inline bint _is_dictionary(object obj):
    """
    Helper method for testing if the object is a dictionary.
    """
    return PyDict_CheckExact(obj)


cpdef bint is_dictionary(object obj):
    """
    Helper method for testing if the object is a dictionary.
    """
    return _is_dictionary(obj)


cdef inline bint _is_sequence(object obj):
    """
    Helper method to see if the object is a sequence (list, set, or tuple).
    """
    if _is_list(obj):
        return True
    if _is_tuple(obj):
        return True
    if _is_set(obj):
        return True
    return False


cpdef bint is_sequence(object obj):
    """
    Helper method to see if the object is a sequence (list, set, or tuple).
    """
    return _is_sequence(obj)


cdef inline bint _is_list(object obj):
    """
    Helper method to see if the object is a Python list.
    """
    return PyList_CheckExact(obj)


cpdef bint is_list(object obj):
    """
    Helper method to see if the object is a Python list.
    """
    return _is_list(obj)


cdef inline bint _is_set(object obj):
    """
    Helper method to see if the object is a Python set.
    """
    return PyAnySet_CheckExact(obj)


cpdef bint is_set(object obj):
    """
    Helper method to see if the object is a Python set.
    """
    return _is_set(obj)


cdef inline bint _is_tuple(object obj):
    """
    Helper method to see if the object is a Python tuple.
    """
    return PyTuple_CheckExact(obj)


cpdef bint is_tuple(object obj):
    """
    Helper method to see if the object is a Python tuple.
    """
    return _is_tuple(obj)


cpdef bint is_dictionary_subclass(object obj):
    """
    Returns True if *obj* is a subclass of the dict type. *obj* must be
    a subclass and not the actual builtin dict.
    """
    if _is_dictionary(obj):
        return False
    # TODO: support PyMapping_Check(obj)
    if PyDict_Check(obj):
        return True
    if PyObject_IsInstance(obj, UserDict):
        return True
    return False


cpdef bint is_sequence_subclass(object obj):
    """
    Returns True if *obj* is a subclass of list, set or tuple.

    *obj* must be a subclass and not the actual builtin, such
    as list, set, tuple, etc.
    """
    if PyList_Check(obj):
        return not _is_list(obj)
    if PyTuple_Check(obj):
        return not _is_tuple(obj)
    if PyAnySet_Check(obj):
        return not _is_set(obj)
    # TODO: Support PySequence_Check(obj)
    if _is_list_like(obj):
        return True
    return False


cpdef bint is_noncomplex(object obj):
    """
    Returns True if *obj* is a special (weird) class, that is more complex
    than primitive data types, but is not a full object. Including:

        * :class:`~time.struct_time`
    """
    return PyObject_IsInstance(obj, time.struct_time)


cpdef bint is_function(object obj):
    """
    Returns True if passed a function, otherwise returns False.
    """
    if PyFunction_Check(obj):
        return True
    if PyMethod_Check(obj):
        return True
    # only True for old-style classes without a '__class__' property
    if PyClass_Check(obj):
        return False
    cdef object obj_class = obj.__class__
    if obj_class.__module__ not in ('__builtin__', 'exceptions', 'builtins'):
        return False
    cdef object name = obj_class.__name__
    return name in ('function', 'builtin_function_or_method', 'instancemethod', 'method-wrapper')


cpdef bint is_module_function(object obj):
    """
    Return True if `obj` is a module-global function.
    """
    # only True for old-style classes without a '__class__' property
    if PyClass_Check(obj):
        return False
    if not PyFunction_Check(obj):
        return False
    if obj.__name__ == '<lambda>':
        return False
    return True


cpdef bint is_module(object obj):
    """
    Returns True if passed a module.
    """
    return PyModule_Check(obj)


cpdef bint is_picklable(object name, object value):
    """
    Return True if an object can be pickled.
    """
    if name in tags.RESERVED:
        return False
    if is_module_function(value):
        return True
    if is_function(value):
        return False
    return True


cdef bint _is_loaded(object module):
    cdef object sys_modules = <object>PyImport_GetModuleDict()
    return PyDict_Contains(sys_modules, module)


cpdef bint is_installed(object module):
    """
    Tests to see if :attr:`module` is available on :attr:`sys.path`.
    """
    if _is_loaded(module):
        return True
    try:
        __import__(module)
        return True
    except ImportError:
        return False


cdef inline bint _is_list_like(object obj):
    """
    Return True if :attr:`obj` has methods '__getitem__' and 'append',
    otherwise return False.
    """
    if not PyObject_HasAttr(obj, '__getitem__'):
        return False
    if PyObject_HasAttr(obj, 'append'):
        return True
    return False


cdef inline bint _is_coll_iterator(object obj):
    if not PyObject_HasAttr(obj, '__iter__'):
        return False
    if not PyObject_HasAttr(obj, 'next'):
        return False  # M
    return True


cpdef bint is_iterator(object obj):
    if not _is_coll_iterator(obj):
        return False
    if PyFile_Check(obj):
        return False  # M
    if PyObject_IsInstance(obj, _IOBase):
        return False  # M
    return True


cpdef bint is_reducible(object obj):
    """
    Returns false if of a type which have special casing, and should not have their
    __reduce__ methods used
    """
    if obj is object:  # this seems to be the most common case
        return False
    if _is_sequence(obj):  # checks is_tuple(obj) and is_set(obj)
        return False  # M
    if _is_primitive(obj):
        return False  # M
    if _is_dictionary(obj):
        return False  # M
    if is_module(obj):
        return False
    if is_dictionary_subclass(obj):
        return False
    if is_sequence_subclass(obj):  # checks is_list_like(obj)
        return False
    if is_noncomplex(obj):
        return False
    if is_function(obj):
        return False  # M
    if type(obj) is object:
        return False
    if not _is_type(obj):
        return True
    if obj.__module__ == 'datetime':
        return False
    return True


cdef bint _in_dict(object obj, object key):
    """
    If `obj.__dict__` exists and `obj.__dict__` contains :attr:`key`, return
    True; otherwise, return False.
    """
    if not PyObject_HasAttr(obj, '__dict__'):
        return False
    return key in obj.__dict__


cdef bint _in_slots(object obj, object key):
    """
    If `obj.__slots__` exists and `obj.__slots__` contains :attr:`key`, return
    True; otherwise, return False.
    """
    if not PyObject_HasAttr(obj, '__slots__'):
        return False
    return key in obj.__slots__


cdef bint _has_reduce_attr(object obj, bint reduce_ex):
    cdef object reduce_attr
    if not reduce_ex:
        reduce_attr = '__reduce__'
    else:
        reduce_attr = '__reduce_ex__'
    cdef bint has_reduce = _in_dict(obj, reduce_attr)
    if not has_reduce:
        has_reduce = _in_slots(obj, reduce_attr)
    cdef tuple base_types = type(obj).__mro__
    for base in base_types:
        if not is_reducible(base):
            continue
        if _in_dict(base, reduce_attr):
            return True
    return False


cpdef tuple has_reduce(object obj):
    """
    Tests if __reduce__ or __reduce_ex__ exists in the object dict or
    in the class dicts of every class in the MRO *except object*.

    Returns a tuple of booleans (has_reduce, has_reduce_ex)
    """
    if _is_type(obj):
        return False, False  # M
    if not is_reducible(obj):
        return False, False

    cdef bint has_reduce = _has_reduce_attr(obj, False)
    cdef bint has_reduce_ex = _has_reduce_attr(obj, True)
    return has_reduce, has_reduce_ex


cpdef object translate_module_name(object module):
    """Rename builtin modules to a consistent (Python2) module name

    This is used so that references to Python's `builtins` module can
    be loaded in both Python 2 and 3.  We remap to the "__builtin__"
    name and unmap it when importing.

    See untranslate_module_name() for the reverse operation.

    """
    if module == 'exceptions':
        return '__builtin__'
    return module


cpdef object untranslate_module_name(object module):
    """Rename module names mention in JSON to names that we can import

    This reverses the translation applied by translate_module_name() to
    a module name available to the current version of Python.

    """
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


cpdef unicode itemgetter(object obj, object getter=None):
    if getter is None:
        getter = operator.itemgetter(0)
    return unicode(getter(obj))
