# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 John Paulett (john -at- paulett.org)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
from UserDict import UserDict
from UserList import UserList
from collections import namedtuple
from jsonpickle import util
from unittest2.case import TestCase
from unittest2.loader import makeSuite
from unittest2.suite import TestSuite
import doctest
import jsonpickle.util
import time
import unittest2

TupleSubclass = namedtuple('TupleSubclass', ())


class Thing(object):

    def __init__(self, name):
        self.name = name
        self.child = None


def get_thing(name):
    return Thing(name)


class Foo(object):

    def method(self):
        pass

    @staticmethod
    def staticmethod():
        pass

    @classmethod
    def classmethod(cls):
        pass


class DictSubclass(dict):
    pass


class UserDictSubclass(UserDict):
    pass


class ListSubclass(list):
    pass


class UserListSubclass(UserList):
    pass


class SetSubclass(set):
    pass


class OldKlass:
    pass


class UtilTestCase(TestCase):

    def test_is_type(self):
        self.assertFalse(util.is_type(1))
        self.assertTrue(util.is_type(object))
        self.assertTrue(util.is_type(OldKlass))

    def test_is_object(self):
        self.assertTrue(util.is_object(1))
        self.assertTrue(util.is_object(object()))
        self.assertFalse(util.is_object(object))
        self.assertFalse(util.is_object(lambda x: 1))

    def test_is_primitive(self):
        self.assertTrue(util.is_primitive(3))
        self.assertFalse(util.is_primitive([4, 4]))
        self.assertTrue(util.is_primitive(0))
        self.assertTrue(util.is_primitive(-3))
        self.assertTrue(util.is_primitive(0.0))
        self.assertTrue(util.is_primitive(3.5))
        self.assertTrue(util.is_primitive(-3.5))
        self.assertTrue(util.is_primitive(3.0))
        self.assertTrue(util.is_primitive(3L))
        self.assertTrue(util.is_primitive(True))
        self.assertTrue(util.is_primitive(False))
        self.assertTrue(util.is_primitive(None))
        self.assertTrue(util.is_primitive('hello'))
        self.assertTrue(util.is_primitive(''))
        self.assertTrue(util.is_primitive(u'hello'))
        self.assertTrue(util.is_primitive(u''))
        self.assertFalse(util.is_primitive([]))
        self.assertFalse(util.is_primitive({'key': 'value'}))
        self.assertFalse(util.is_primitive({}))
        self.assertFalse(util.is_primitive((1, 3)))
        self.assertFalse(util.is_primitive((1,)))
        self.assertFalse(util.is_primitive(set([1, 3])))
        self.assertFalse(util.is_primitive(Thing('test')))
        self.assertFalse(util.is_primitive(OldKlass()))

    def test_is_dictionary(self):
        self.assertTrue(util.is_dictionary({'key': 'value'}))
        self.assertTrue(util.is_dictionary({}))
        self.assertFalse(util.is_dictionary([]))
        self.assertFalse(util.is_dictionary(set()))
        self.assertFalse(util.is_dictionary(tuple()))
        self.assertFalse(util.is_dictionary(int()))
        self.assertFalse(util.is_dictionary(None))
        self.assertFalse(util.is_dictionary(str()))

    def test_is_sequence(self):
        self.assertTrue(util.is_sequence([]))
        self.assertTrue(util.is_sequence(tuple()))
        self.assertTrue(util.is_sequence(set()))
        self.assertFalse(util.is_sequence({}))
        self.assertTrue(util.is_sequence([4]))

    def test_is_list(self):
        self.assertTrue(util.is_list([4]))
        self.assertTrue(util.is_list([1, 2]))
        self.assertFalse(util.is_list({'key': 'value'}))
        self.assertFalse(util.is_list(1))

    def test_is_set(self):
        self.assertTrue(util.is_set(set()))
        self.assertTrue(util.is_set(set([1, 2])))
        self.assertFalse(util.is_set({'key': 'value'}))
        self.assertFalse(util.is_set(1))

    def test_is_list_tuple(self):
        self.assertTrue(util.is_tuple((1, )))
        self.assertTrue(util.is_tuple((1, 2)))
        self.assertFalse(util.is_tuple({'key': 'value'}))
        self.assertFalse(util.is_tuple(1))

    def test_is_dictionary_subclass(self):
        self.assertFalse(util.is_dictionary_subclass({}))
        self.assertTrue(util.is_dictionary_subclass(DictSubclass()))
        self.assertTrue(util.is_dictionary_subclass(UserDictSubclass()))

    def test_is_sequence_subclass(self):
        self.assertFalse(util.is_sequence_subclass([]))
        self.assertFalse(util.is_sequence_subclass(set()))
        self.assertFalse(util.is_sequence_subclass(tuple()))
        self.assertTrue(util.is_sequence_subclass(ListSubclass()))
        self.assertTrue(util.is_sequence_subclass(SetSubclass()))
        self.assertTrue(util.is_sequence_subclass(TupleSubclass()))
        self.assertTrue(util.is_sequence_subclass(UserListSubclass()))

    def test_is_noncomplex(self):
        t = time.struct_time('123456789')
        self.assertTrue(util.is_noncomplex(t))
        self.assertFalse(util.is_noncomplex('a'))

    def test_is_function(self):
        self.assertTrue(util.is_function(lambda x: 1))
        self.assertTrue(util.is_function(lambda: False))
        self.assertTrue(util.is_function(locals))
        self.assertTrue(util.is_function(globals))
        self.assertFalse(util.is_function(Thing))
        self.assertFalse(util.is_function(Thing('thing')))
        self.assertFalse(util.is_function(OldKlass()))
        self.assertFalse(util.is_function(OldKlass))
        self.assertTrue(util.is_function(get_thing))
        self.assertTrue(util.is_function(Foo.method))
        self.assertTrue(util.is_function(Foo.staticmethod))
        self.assertTrue(util.is_function(Foo.classmethod))
        self.assertTrue(util.is_function(Foo().method))
        self.assertTrue(util.is_function(Foo().staticmethod))
        self.assertTrue(util.is_function(Foo().classmethod))
        self.assertFalse(util.is_function(1))

    def test_itemgetter(self):
        expect = '0'
        actual = util.itemgetter((0, 'zero'))
        self.assertEqual(expect, actual)


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(UtilTestCase))
    suite.addTest(doctest.DocTestSuite(jsonpickle.util))
    return suite


if __name__ == '__main__':
    unittest2.main(defaultTest='suite')
