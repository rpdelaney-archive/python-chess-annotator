#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock
import random

import chess
import annotator.__main__ as annotator


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


class test_eval_numeric(unittest.TestCase):

    def test_raises_runtimeerror(self):
        score = MagicMock()
        score.mate = None
        score.cp = None
        info_handler = MagicMock()
        info_handler.info = {'score': [None, score]}
        self.assertRaises(RuntimeError, annotator.eval_numeric, info_handler)

    def test_dtm_positive(self):
        score = MagicMock()
        score.mate = 5
        score.cp = None
        info_handler = MagicMock()
        info_handler.info = {'score': [None, score]}

        result = annotator.eval_numeric(info_handler)
        self.assertEqual(result, 9995)

    def test_dtm_negative(self):
        score = MagicMock()
        score.mate = -5
        score.cp = None
        info_handler = MagicMock()
        info_handler.info = {'score': [None, score]}

        result = annotator.eval_numeric(info_handler)
        self.assertEqual(result, -9995)

    def test_cp_positive(self):
        score = MagicMock()
        score.mate = None
        score.cp = 5
        info_handler = MagicMock()
        info_handler.info = {'score': [None, score]}

        result = annotator.eval_numeric(info_handler)
        self.assertEqual(result, 5)

    def test_cp_negative(self):
        score = MagicMock()
        score.mate = None
        score.cp = -5
        info_handler = MagicMock()
        info_handler.info = {'score': [None, score]}

        result = annotator.eval_numeric(info_handler)
        self.assertEqual(result, -5)


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

    def test_zero(self):
        result = annotator.needs_annotation(0)
        self.assertFalse(result)

    def test_low_fraction(self):
        result = annotator.needs_annotation(5.3333333)
        self.assertFalse(result)

    def test_high_fraction(self):
        result = annotator.needs_annotation(500.33333)
        self.assertTrue(result)

    def test_raises_typeerror(self):
        self.assertRaises(TypeError, annotator.needs_annotation, 'a')


class test_cpl(unittest.TestCase):

    def test_int(self):
        result = annotator.cpl(5)
        self.assertEqual(result, 5)

    def test_string(self):
        result = annotator.cpl('5')
        self.assertEqual(result, 5)

    def test_bigstring(self):
        result = annotator.cpl('2001')
        self.assertEqual(result, 2000)

    def test_negativestring(self):
        result = annotator.cpl('-2001')
        self.assertEqual(result, -2001)


class test_acpl(unittest.TestCase):

    def test_list(self):
        testlist = [1, 2, 3, 4, 5, 6]
        result = annotator.acpl(testlist)
        self.assertEqual(result, 3.5)


class test_eco_fen(unittest.TestCase):

    def test_board(self):
        board = chess.Board('Q4R2/3kr3/1q3n1p/2p1p1p1/1p1bP1P1/1B1P3P/2PBK3/8 w - - 1 0')
        result = annotator.eco_fen(board)
        self.assertEqual(result, 'Q4R2/3kr3/1q3n1p/2p1p1p1/1p1bP1P1/1B1P3P/2PBK3/8 w -')


class test_get_total_budget(unittest.TestCase):

    def test_is_float(self):
        result = annotator.get_total_budget(random.random())
        self.assertIsInstance(result, float)

    def test_math(self):
        seed = random.random()
        result = annotator.get_total_budget(seed)
        self.assertEqual(result, seed * 60)

# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
