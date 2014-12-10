# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Jason R. Coombs <jaraco@jaraco.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import doctest
import jsonpickle
import jsonpickle.handlers
import unittest2
from unittest2.case import TestCase
from unittest2.loader import makeSuite
from unittest2.suite import TestSuite


class CustomObject(object):

    "A class to be serialized by a custom handler"

    def __init__(self, name=None, creator=None):
        self.name = name
        self.creator = creator

    def __eq__(self, other):
        return self.name == other.name


class NullHandler(jsonpickle.handlers.BaseHandler):

    def flatten(self, obj, data):
        data['name'] = obj.name
        return data

    def restore(self, obj):
        return CustomObject(obj['name'], creator=NullHandler)


class HandlerTestCase(TestCase):

    def setUp(self):
        jsonpickle.handlers.register(CustomObject, NullHandler)

    def tearDown(self):
        jsonpickle.handlers.unregister(CustomObject)

    def roundtrip(self, ob):
        encoded = jsonpickle.encode(ob)
        decoded = jsonpickle.decode(encoded)
        self.assertEqual(decoded, ob)
        return decoded

    def test_custom_handler(self):
        """Ensure that the custom handler is indeed used"""
        expect = CustomObject('hello')
        encoded = jsonpickle.encode(expect)
        actual = jsonpickle.decode(encoded)
        self.assertEqual(expect.name, actual.name)
        self.assertTrue(expect.creator is None)
        self.assertTrue(actual.creator is NullHandler)

    def test_references(self):
        """
        Ensure objects handled by a custom handler are properly dereferenced.
        """
        ob = CustomObject()
        # create a dictionary which contains several references to ob
        subject = dict(a=ob, b=ob, c=ob)
        # ensure the subject can be roundtripped
        new_subject = self.roundtrip(subject)
        self.assertEqual(new_subject['a'], new_subject['b'])
        self.assertEqual(new_subject['b'], new_subject['c'])
        self.assertTrue(new_subject['a'] is new_subject['b'])
        self.assertTrue(new_subject['b'] is new_subject['c'])


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(HandlerTestCase))
    suite.addTest(doctest.DocTestSuite(jsonpickle.handlers))
    return suite


if __name__ == '__main__':
    unittest2.main(defaultTest='suite')
