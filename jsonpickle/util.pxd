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
from cpython.object cimport PyObject_IsInstance
from cpython.number cimport PyNumber_Check
from cpython.string cimport PyString_Check, PyString_CheckExact
from cpython.unicode cimport PyUnicode_Check, PyUnicode_CheckExact
from cpython.set cimport PyAnySet_CheckExact
from cpython.tuple cimport PyTuple_Check, PyTuple_CheckExact
from cpython.list cimport PyList_Check, PyList_CheckExact
from cpython.dict cimport PyDict_CheckExact
from jsonpickle import tags

cdef extern from 'Python.h':
    bint PyClass_Check(object obj)

cpdef tuple SEQUENCES = (list, set, tuple)

cpdef inline bint is_type(object obj)

cpdef inline bint is_object(object obj)

cpdef inline bint is_primitive(object obj)

cpdef inline bint is_dictionary(object obj)

cpdef inline bint is_sequence(object obj)

cpdef inline bint is_list(object obj)

cpdef inline bint is_set(object obj)

cpdef inline bint is_tuple(object obj)

# cpdef bint is_dictionary_subclass(obj)
# 
# cpdef bint is_sequence_subclass(obj)
# 
# cpdef bint is_noncomplex(obj)
# 
# cpdef bint is_function(obj)
# 
# cpdef bint is_module_function(obj)
# 
# cpdef bint is_module(obj)
# 
# cpdef bint is_picklable(name, value)
# 
# cpdef bint is_installed(module)
# 
# cpdef bint is_list_like(obj)
# 
# cpdef bint is_iterator(obj)
# 
# cpdef bint is_reducible(obj)
# 
# cpdef bint in_dict(obj, key, bint default=?)
# 
# cpdef bint in_slots(obj, key, bint default=?)
# 
# cpdef bint has_reduce(obj)
# 
# cpdef translate_module_name(module)
# 
# cpdef untranslate_module_name(module)
# 
# cpdef importable_name(cls)
# 
# cpdef b64encode(data)
# 
# cpdef b64decode(payload)
# 
# cpdef itemgetter(obj, getter)
