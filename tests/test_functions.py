#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock

import annotator


class test_eval_absolute(unittest.TestCase):

    def test_white_unpadded(self):
        result = annotator.eval_absolute(10.01, True)
        self.assertEqual(result, '10.01')

    def test_white_padded(self):
        result = annotator.eval_absolute(10, True)
        self.assertEqual(result, '10.00')

    def test_black(self):
        result = annotator.eval_absolute(10.00, False)
        self.assertEqual(result, '-10.00')


class test_eval_numeric(unittest.TestCase):

    def test_raises_runtimeerror(self):
        score = MagicMock()
        score.mate = None
        score.cp = None
        info_handler = MagicMock()
        info_handler.info = {'score': [None, score]}
        self.assertRaises(RuntimeError, annotator.eval_numeric, info_handler)
