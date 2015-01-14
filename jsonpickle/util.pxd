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

cdef inline bint _is_type(object obj)
cpdef bint is_type(object obj)
cdef inline bint _is_object(object obj)
cpdef bint is_object(object obj)
cdef inline bint _is_primitive(object obj)
cpdef bint is_primitive(object obj)
cdef inline bint _is_dictionary(object obj)
cpdef bint is_dictionary(object obj)
cdef inline bint _is_sequence(object obj)
cpdef bint is_sequence(object obj)
cdef inline bint _is_list(object obj)
cpdef bint is_list(object obj)
cdef inline bint _is_set(object obj)
cpdef bint is_set(object obj)
cdef inline bint _is_tuple(object obj)
cpdef bint is_tuple(object obj)
cpdef bint is_dictionary_subclass(object obj)
cpdef bint is_sequence_subclass(object obj)
cpdef bint is_noncomplex(object obj)
cpdef bint is_function(object obj)
cpdef bint is_module_function(object obj)
cpdef bint is_module(object obj)
cpdef bint is_picklable(object name, object value)
cpdef bint is_installed(object module)
cdef inline bint _is_list_like(object obj)
cpdef bint is_list_like(object obj)
cdef inline bint _is_coll_iterator(object obj)
cdef inline bint _is_file(object obj)
cpdef bint is_file(object obj)
cpdef bint is_iterator(object obj)
cpdef bint is_reducible(object obj)
cdef inline bint _in_dict(object obj, object key, bint default)
cpdef bint in_dict(object obj, object key, bint default=?)
cdef inline bint _in_slots(object obj, object key, bint default)
cpdef bint in_slots(object obj, object key, bint default=?)
cpdef tuple has_reduce(object obj)
cpdef object translate_module_name(object module)
cpdef object untranslate_module_name(object module)
cpdef inline str importable_name(object cls)
cpdef unicode itemgetter(object obj, object getter=?)
