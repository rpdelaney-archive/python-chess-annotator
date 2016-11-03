#!/usr/bin/env python3

import unittest

import annotator


class test_eval_absolute(unittest.TestCase):

    def test_white_unpadded(self):
        result = annotator.eval_absolute(10.01, True)
        self.assertEqual(result, 10.01)

    def test_white_padded(self):
        result = annotator.eval_absolute(10, True)
        self.assertEqual(result, 10.00)

    def test_black(self):
        result = annotator.eval_absolute(10.00, False)
        self.assertEqual(result, -10.00)


class test_needs_annotation(unittest.TestCase):

    def test_high(self):
        result = annotator.needs_annotation(100)
        self.assertTrue(result)

    def test_low(self):
        result = annotator.needs_annotation(5)
        self.assertFalse(result)

    def test_negative(self):
        result = annotator.needs_annotation(-100)
        self.assertFalse(result)


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
