from jsonpickle.compat import PY2, PY3, PY32, unicode
from unittest2.case import TestCase
from unittest2.loader import makeSuite
from unittest2.suite import TestSuite
from warnings import warn
import jsonpickle
import unittest2


class Thing(object):

    def __init__(self, name):
        self.name = name
        self.child = None


SAMPLE_DATA = {'things': [Thing('data')]}


class BackendBase(TestCase):

    def _is_installed(self, backend):
        if not jsonpickle.util.is_installed(backend):
            if hasattr(self, 'skipTest'):
                doit = self.skipTest
            else:
                doit = self.fail
            doit('{0} not available; please install'.format(backend))

    def set_backend(self, *args):
        backend = args[0]

        self._is_installed(backend)

        jsonpickle.load_backend(*args)
        jsonpickle.set_preferred_backend(backend)

    def set_preferred_backend(self, backend):
        self._is_installed(backend)
        jsonpickle.set_preferred_backend(backend)

    def tearDown(self):
        # always reset to default backend
        jsonpickle.set_preferred_backend('json')

    def assertEncodeDecode(self, json_input):
        expect = SAMPLE_DATA
        actual = jsonpickle.decode(json_input)
        self.assertEqual(expect['things'][0].name, actual['things'][0].name)
        self.assertEqual(expect['things'][0].child, actual['things'][0].child)

        pickled = jsonpickle.encode(SAMPLE_DATA)
        actual = jsonpickle.decode(pickled)
        self.assertEqual(expect['things'][0].name, actual['things'][0].name)
        self.assertEqual(expect['things'][0].child, actual['things'][0].child)

    def test_None_dict_key(self):
        """Ensure that backends produce the same result for None dict keys"""
        data = {None: None}
        expect = {'null': None}
        pickle = jsonpickle.encode(data)
        actual = jsonpickle.decode(pickle)
        self.assertEqual(expect, actual)


class JsonTestCase(BackendBase):

    def setUp(self):
        self.set_preferred_backend('json')

    def test_backend(self):
        expected_pickled = (
            '{{"things": [{{'
            '"py/object": "{0}.Thing",'
            ' "name": "data",'
            ' "child": null}}'
            ']}}').format(self.__module__)
        self.assertEncodeDecode(expected_pickled)


class SimpleJsonTestCase(BackendBase):

    def setUp(self):
        if PY32:
            return
        self.set_preferred_backend('simplejson')

    def test_backend(self):
        if PY32:
            self.skipTest('no simplejson for python3.2')
            return
        expected_pickled = (
            '{{"things": [{{'
            '"py/object": "{0}.Thing",'
            ' "name": "data",'
            ' "child": null}}'
            ']}}').format(self.__module__)
        self.assertEncodeDecode(expected_pickled)


def has_module(module):
    try:
        __import__(module)
    except ImportError:
        warn(module + ' module not available for testing, '
             'consider installing')
        return False
    return True


class DemjsonTestCase(BackendBase):

    def setUp(self):
        if PY2:
            self.set_preferred_backend('demjson')

    def test_backend(self):
        if PY3:
            self.skipTest('no demjson for python3')
            return
        expected_pickled = unicode(
            '{{"things":[{{'
            '"child":null,'
            '"name":"data",'
            '"py/object":"{0}.Thing"}}'
            ']}}').format(self.__module__)
        self.assertEncodeDecode(expected_pickled)


class JsonlibTestCase(BackendBase):

    def setUp(self):
        if PY2:
            self.set_preferred_backend('jsonlib')

    def test_backend(self):
        if PY3:
            self.skipTest('no jsonlib for python3')
            return
        expected_pickled = (
            '{{"things":[{{'
            '"py\/object":"{0}.Thing",'
            '"name":"data","child":null}}'
            ']}}').format(self.__module__)
        self.assertEncodeDecode(expected_pickled)


class YajlTestCase(BackendBase):

    def setUp(self):
        if PY2:
            self.set_preferred_backend('yajl')

    def test_backend(self):
        if PY3:
            self.skipTest('no yajl for python3')
            return
        expected_pickled = (
            '{{"things":[{{'
            '"py/object":"{0}.Thing",'
            '"name":"data","child":null}}'
            ']}}').format(self.__module__)
        self.assertEncodeDecode(expected_pickled)


class UJsonTestCase(BackendBase):

    def setUp(self):
        self.set_preferred_backend('ujson')

    def test_backend(self):
        expected_pickled = (
            '{{"things":[{{'
            '"py\/object":"{0}.Thing",'
            '"name":"data","child":null}}'
            ']}}').format(self.__module__)
        self.assertEncodeDecode(expected_pickled)


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(JsonTestCase))
    suite.addTest(makeSuite(UJsonTestCase))
    if not PY32:
        suite.addTest(makeSuite(SimpleJsonTestCase))
    if PY2:
        if has_module('demjson'):
            suite.addTest(makeSuite(DemjsonTestCase))
        if has_module('yajl'):
            suite.addTest(makeSuite(YajlTestCase))
        if has_module('jsonlib'):
            suite.addTest(makeSuite(JsonlibTestCase))
    return suite


if __name__ == '__main__':
    unittest2.main(defaultTest='suite')
