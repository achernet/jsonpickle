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
cdef extern from 'Python.h':
    bint PyClass_Check(object obj)
    bint PyFile_Check(object obj)

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

from base64 import b64encode, b64decode
from _io import _IOBase
import operator
import time
import types
import sys
from UserDict import UserDict
from jsonpickle import tags

cpdef inline bint is_type(object obj)
cpdef inline bint is_object(object obj)
cpdef inline bint is_primitive(object obj)
cpdef inline bint is_dictionary(object obj)
cpdef inline bint is_sequence(object obj)
cpdef inline bint is_list(object obj)
cpdef inline bint is_set(object obj)
cpdef inline bint is_tuple(object obj)
cpdef inline bint is_dictionary_subclass(object obj)
cpdef inline bint is_sequence_subclass(object obj)
cpdef inline bint is_noncomplex(object obj)
cpdef inline bint is_function(object obj)
cpdef inline bint is_module_function(object obj)
cpdef inline bint is_module(object obj)
cpdef bint is_picklable(object name, object value)
cpdef bint is_installed(str module)
cpdef inline bint is_list_like(object obj)
cdef inline bint _is_coll_iterator(object obj)
cpdef bint is_iterator(object obj)
cpdef bint is_reducible(object obj)
cpdef inline bint in_dict(object obj, object key, bint default=?)
cpdef inline bint in_slots(object obj, object key, bint default=?)
cpdef tuple has_reduce(object obj)
cpdef object translate_module_name(object module)
cpdef object untranslate_module_name(object module)
cpdef inline str importable_name(object cls)
cpdef inline unicode itemgetter(object obj, object getter=?)
