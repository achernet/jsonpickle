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
cpdef bint is_type(object obj)
cpdef bint is_object(object obj)
cpdef bint is_primitive(object obj)
cpdef bint is_dictionary(object obj)
cpdef bint is_sequence(object obj)
cpdef bint is_list(object obj)
cpdef bint is_set(object obj)
cpdef bint is_tuple(object obj)
cpdef bint is_dictionary_subclass(object obj)
cpdef bint is_sequence_subclass(object obj)
cpdef bint is_noncomplex(object obj)
cpdef bint is_function(object obj)
cpdef bint is_module_function(object obj)
cpdef bint is_module(object obj)
cpdef bint is_picklable(object name, object value)
cpdef bint is_installed(object module)
cpdef bint is_iterator(object obj)
cpdef bint is_reducible(object obj)
cpdef tuple has_reduce(object obj)
cpdef object translate_module_name(object module)
cpdef object untranslate_module_name(object module)
cpdef inline str importable_name(object cls)
cpdef unicode itemgetter(object obj, object getter=?)
