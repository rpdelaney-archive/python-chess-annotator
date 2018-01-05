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


class test_winning_chances(unittest.TestCase):

    def test_zero(self):
        score = 0
        result = round(annotator.winning_chances(score))
        self.assertEqual(result, 50)

    def test_one(self):
        score = 100
        result = round(annotator.winning_chances(score))
        self.assertEqual(result, 60)

    def test_four(self):
        score = 400
        result = round(annotator.winning_chances(score))
        self.assertEqual(result, 83)

    def test_negative_one(self):
        score = -100
        result = round(annotator.winning_chances(score))
        self.assertEqual(result, 40)

    def test_negative_four(self):
        score = -400
        result = round(annotator.winning_chances(score))
        self.assertEqual(result, 17)


class test_needs_annotation(unittest.TestCase):

    def test_high(self):
        judgment = {}
        judgment["besteval"] = 200
        judgment["playedeval"] = 100
        result = annotator.needs_annotation(judgment)
        self.assertTrue(result)

    def test_low(self):
        judgment = {}
        judgment["besteval"] = 5
        judgment["playedeval"] = 0
        result = annotator.needs_annotation(judgment)
        self.assertFalse(result)

    def test_negative(self):
        judgment = {}
        judgment["besteval"] = 0
        judgment["playedeval"] = 100
        result = annotator.needs_annotation(judgment)
        self.assertFalse(result)

    def test_zero(self):
        judgment = {}
        judgment["besteval"] = 0
        judgment["playedeval"] = 0
        result = annotator.needs_annotation(judgment)
        self.assertFalse(result)

    def test_low_fraction(self):
        judgment = {}
        judgment["besteval"] = 5.333333
        judgment["playedeval"] = 0
        result = annotator.needs_annotation(judgment)
        self.assertFalse(result)

    def test_high_fraction(self):
        judgment = {}
        judgment["besteval"] = 500.33333
        judgment["playedeval"] = 0
        result = annotator.needs_annotation(judgment)
        self.assertTrue(result)

    def test_small_error_big_advantage(self):
        judgment = {}
        judgment["besteval"] = 600
        judgment["playedeval"] = 500
        result = annotator.needs_annotation(judgment)
        self.assertFalse(result)

    def test_small_error_big_disadvantage(self):
        judgment = {}
        judgment["besteval"] = -500
        judgment["playedeval"] = -600
        result = annotator.needs_annotation(judgment)
        self.assertFalse(result)

    def test_big_error_huge_advantage(self):
        judgment = {}
        judgment["besteval"] = 9998
        judgment["playedeval"] = 1000
        result = annotator.needs_annotation(judgment)
        self.assertFalse(result)

    def test_big_error_huge_disadvantage(self):
        judgment = {}
        judgment["besteval"] = -1000
        judgment["playedeval"] = -9998
        result = annotator.needs_annotation(judgment)
        self.assertFalse(result)

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


class test_truncate_pv(unittest.TestCase):

    def test_long_mating_pv(self):
        """ A long pv that ends the game should not be truncated """

        board = chess.Board('1Q3bk1/5p2/2p3p1/1p1bN2p/4n2P/8/r5PK/8 b - - 1 34')
        line = [chess.Move.from_uci('g8g7'), chess.Move.from_uci('e5f7'), chess.Move.from_uci('d5f7'), chess.Move.from_uci('b8e5'),
                chess.Move.from_uci('e4f6'), chess.Move.from_uci('h2h3'), chess.Move.from_uci('b5b4'), chess.Move.from_uci('g2g4'),
                chess.Move.from_uci('f8d6'), chess.Move.from_uci('e5d6'), chess.Move.from_uci('h5g4'), chess.Move.from_uci('h3g3'),
                chess.Move.from_uci('f6e4'), chess.Move.from_uci('g3f4'), chess.Move.from_uci('e4d6'), chess.Move.from_uci('f4e5'),
                chess.Move.from_uci('b4b3'), chess.Move.from_uci('e5d6'), chess.Move.from_uci('b3b2'), chess.Move.from_uci('h4h5'),
                chess.Move.from_uci('g6h5'), chess.Move.from_uci('d6d7'), chess.Move.from_uci('b2b1q'), chess.Move.from_uci('d7c7'),
                chess.Move.from_uci('b1b4'), chess.Move.from_uci('c7c6'), chess.Move.from_uci('a2c2'), chess.Move.from_uci('c6d7'),
                chess.Move.from_uci('b4b8'), chess.Move.from_uci('d7e7'), chess.Move.from_uci('b8c7')]
        result = annotator.truncate_pv(board, line)
        self.assertEqual(result, line)

    def test_long_non_mating_pv(self):
        """ A long pv that does not end the game should be truncated to 10 moves """

        board = chess.Board('1Q3bk1/5p2/2p3p1/1p1bN2p/4n2P/8/r5PK/8 b - - 1 34')
        line = [chess.Move.from_uci('g8g7'), chess.Move.from_uci('e5f7'), chess.Move.from_uci('d5f7'), chess.Move.from_uci('b8e5'),
                chess.Move.from_uci('e4f6'), chess.Move.from_uci('h2h3'), chess.Move.from_uci('b5b4'), chess.Move.from_uci('g2g4'),
                chess.Move.from_uci('f8d6'), chess.Move.from_uci('e5d6'), chess.Move.from_uci('h5g4'), chess.Move.from_uci('h3g3'),
                chess.Move.from_uci('f6e4'), chess.Move.from_uci('g3f4'), chess.Move.from_uci('e4d6'), chess.Move.from_uci('f4e5'),
                chess.Move.from_uci('b4b3'), chess.Move.from_uci('e5d6'), chess.Move.from_uci('b3b2'), chess.Move.from_uci('h4h5'),
                chess.Move.from_uci('g6h5'), chess.Move.from_uci('d6d7'), chess.Move.from_uci('b2b1q'), chess.Move.from_uci('d7c7'),
                chess.Move.from_uci('b1b4'), chess.Move.from_uci('c7c6'), chess.Move.from_uci('a2c2'), chess.Move.from_uci('c6d7'),
                chess.Move.from_uci('b4b8'), chess.Move.from_uci('d7e7')]
        target = [chess.Move.from_uci('g8g7'), chess.Move.from_uci('e5f7'), chess.Move.from_uci('d5f7'), chess.Move.from_uci('b8e5'),
                  chess.Move.from_uci('e4f6'), chess.Move.from_uci('h2h3'), chess.Move.from_uci('b5b4'), chess.Move.from_uci('g2g4'),
                  chess.Move.from_uci('f8d6'), chess.Move.from_uci('e5d6')]
        result = annotator.truncate_pv(board, line)
        self.assertEqual(result, target)


class test_get_nags(unittest.TestCase):

    def test_zero(self):
        judgment = {'playedeval': 0, 'besteval': 0}
        result = annotator.get_nags(judgment)
        self.assertEqual(result, [])

    def test_negative(self):
        judgment = {'playedeval': 0, 'besteval': -10}
        result = annotator.get_nags(judgment)
        self.assertEqual(result, [])

    def test_float(self):
        judgment = {'playedeval': 0.001, 'besteval': -10.05}
        result = annotator.get_nags(judgment)
        self.assertEqual(result, [])

    def test_blunder(self):
        judgment = {'playedeval': 0, 'besteval': 350}
        result = annotator.get_nags(judgment)
        self.assertEqual(result, [chess.pgn.NAG_BLUNDER])

    def test_mistake(self):
        judgment = {'playedeval': 0, 'besteval': 200}
        result = annotator.get_nags(judgment)
        self.assertEqual(result, [chess.pgn.NAG_MISTAKE])

    def test_dubious(self):
        judgment = {'playedeval': 0, 'besteval': 100}
        result = annotator.get_nags(judgment)
        self.assertEqual(result, [chess.pgn.NAG_DUBIOUS_MOVE])

    def test_typeerror(self):
        judgment = {'playedeval': 0, 'besteval': 'foo'}
        self.assertRaises(TypeError, annotator.get_nags, judgment)


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
