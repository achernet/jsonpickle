from unittest2.case import TestCase
from jsonpickle.pickler import Pickler, _mktyperef
from jsonpickle import tags


class TestPickler(TestCase):

    def test_flatten(self):
        pickler = Pickler()
        self.assertEquals(pickler.flatten('hello world'), 'hello world')
        self.assertEquals(pickler.flatten(49), 49)
        self.assertEquals(pickler.flatten(350.0), 350.0)
        self.assertIs(pickler.flatten(True), True)
        self.assertIs(pickler.flatten(False), False)
        self.assertIsNone(pickler.flatten(None))
        self.assertEquals(pickler.flatten([1, 2, 3, 4]), [1, 2, 3, 4])
        self.assertEquals(pickler.flatten((1, 2,))[tags.TUPLE], [1, 2])
        self.assertEquals(pickler.flatten({'key': 'value'}), {'key': 'value'})

    def test_mktyperef(self):
        exp = {'py/type': '__builtin__.AssertionError'}
        self.assertEquals(_mktyperef(AssertionError), exp)
