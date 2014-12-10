# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 John Paulett (john -at- paulett.org)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from path import Path
from unittest2.case import TestCase
from unittest2.loader import makeSuite
from unittest2.suite import TestSuite
import feedparser
import jsonpickle
import unittest2


def find_rss_doc():
    cur_path = Path(__file__)
    while True:
        next_dir = cur_path.dirname()
        if 'jsonpickle' not in next_dir:
            break
        cur_path = next_dir
    return cur_path.joinpath('jsonpickleJS', 'doc.rss').text()

RSS_DOC = find_rss_doc()


class FeedParserTestCase(TestCase):

    def setUp(self):
        self.doc = feedparser.parse(RSS_DOC)

    def test(self):
        pickled = jsonpickle.encode(self.doc)
        unpickled = jsonpickle.decode(pickled)
        self.assertEqual(self.doc['feed']['title'], unpickled['feed']['title'])


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(FeedParserTestCase, 'test'))
    return suite


if __name__ == '__main__':
    unittest2.main(defaultTest='suite')
