#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Python 3.6.5
#
__author__ = "Ryan Delaney (ryan DOT delaney AT gmail DOT com)"
__date__ = "2018-06-05"
__copyright__ = """© Copyright 2018 Ryan Delaney. All rights reserved.
 This work is distributed WITHOUT ANY WARRANTY whatsoever; without even the
 implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 See the README file for additional terms and conditions on your use of this
 software.
"""

import chess
import math


class evaluation:
    MAX_SCORE = 10000

    def __init__(self, info_handler, white_to_move):
        self.dtm = info_handler.info["score"][1].mate
        self.cp = info_handler.info["score"][1].cp
        if self.dtm is None and self.cp is None:
            raise RuntimeError("Evaluation found in the info_handler was unintelligible")

        self.engine = self.eval_engine()
        self.absolute = self.eval_absolute(white_to_move)
        self.human = self.eval_human(white_to_move)
        self.numeric = self.eval_numeric()

    def eval_engine(self):
        """ Determine if the evaluation is dtm or cp and return whichever exists """
        if self.dtm is not None and self.cp is None:
            return self.dtm
        elif self.cp is not None and self.dtm is None:
            # We don't have depth-to-mate, so return the cp evaluation
            return self.cp
        return None

    def eval_absolute(self, wtm):
        """
        Accepts a relative evaluation (from the point of view of the player to
        move) and returns an absolute evaluation (from the point of view of white)
        """
        number = self.engine

        if not wtm:
            number = -number

        return number

    def eval_human(self, white_to_move):
        """
        Returns a human-readable evaluation of the position:
            If depth-to-mate was found, return plain-text mate announcement (e.g. "Mate in 4")
            If depth-to-mate was not found, return an absolute numeric evaluation
        """
        if self.dtm is not None:
            return "Mate in {}".format(abs(self.dtm))
        elif self.cp is not None:
            # We don't have depth-to-mate, so return the numerical evaluation (in pawns)
            return "{:.2f}".format(self.absolute / 100)

    def eval_numeric(self):
        """
        Returns a numeric evaluation of the position, even if depth-to-mate was
        found. This facilitates comparing numerical evaluations with depth-to-mate
        evaluations
        """
        if self.dtm is not None:
            # We have depth-to-mate (dtm), so translate it into a numerical
            # evaluation. This number needs to be just big enough to guarantee that
            # it is always greater than a non-dtm evaluation.

            if self.dtm >= 1:
                return self.MAX_SCORE - self.dtm
            else:
                return -(self.MAX_SCORE + self.dtm)

        elif self.cp is not None:
            # We don't have depth-to-mate, so return the numerical evaluation (in centipawns)
            return self.cp


class judgment:

    THRESHOLD = {
        "BLUNDER": -300,
        "MISTAKE": -150,
        "DUBIOUS": -75}

    def __init__(self, board, played_move, engine, info_handler, searchtime_s):
        """
        Evaluate the strength of a given move by comparing it to engine's best
        move and evaluation at a given depth, in a given board context

        Returns a judgment

        A judgment is a dictionary containing the following elements:
            "bestmove":      The best move in the position, according to the engine
            "besteval":      A numeric evaluation of the position after the best move is played
            "bestcomment":   A plain-text comment appropriate for annotating the best move
            "pv":            The engine's primary variation including the best move
            "playedeval":    A numeric evaluation of the played move
            "playedcomment": A plain-text comment appropriate for annotating the played move
            "depth":         Search depth in plies
            "nodes":         Number nodes searched
        """

        self.played_move = played_move

        # Calculate the search time in milliseconds
        searchtime_ms = searchtime_s * 1000

        # First, get the engine bestmove and evaluation
        engine.position(board)
        engine.go(movetime=searchtime_ms / 2)
        self.bestmove_evaluation = evaluation(info_handler, board.turn)

        self.bestmove = info_handler.info["pv"][1][0]
        self.besteval = self.bestmove_evaluation.numeric
        self.pv = info_handler.info["pv"][1]
        self.depth = info_handler.info["depth"]
        self.nodes = info_handler.info["nodes"]

        # Annotate the best move
        self.bestcomment = self.bestmove_evaluation.human

        # If the played move matches the engine bestmove, we're done
        if played_move == self.bestmove:
            judgment["playedeval"] = judgment["besteval"]
            # Annotate the played move
            judgment["playedcomment"] = self.bestmove_evaluation.human
        else:
            # get the engine evaluation of the played move
            board.push(played_move)
            engine.position(board)
            engine.go(movetime=searchtime_ms / 2)
            played_evaluation = evaluation(info_handler, board.turn)

            # Store the numeric evaluation.
            # We invert the sign since we're now evaluating from the opponent's perspective
            judgment["playedeval"] = -played_evaluation.numeric

            # Take the played move off the stack (reset the board)
            board.pop()

            # Annotate the played move
            judgment["playedcomment"] = played_evaluation.human

        return judgment

    def needs_annotation(self):
        """
        Returns a boolean indicating whether a node with the given evaluations
        should have an annotation added
        """
        best = self.winning_chances(self.besteval)
        played = self.winning_chances(self.playedeval)
        delta = best - played

        return delta > 7.5

    def winning_chances(self):
        """
        Takes an evaluation in centipawns and returns an integer value estimating the
        chance the player to move will win the game

        winning chances = 50 + 50 * (2 / (1 + e^(-0.004 * centipawns)) - 1)
        """
        return 50 + 50 * (2 / (1 + math.exp(-0.004 * centipawns)) - 1)

    def get_nags(self):
        """
        Returns a Numeric Annotation Glyph (NAG) according to how much worse the
        played move was vs the best move
        """

        delta = judgment["playedeval"] - judgment["besteval"]

        if delta < self.THRESHOLD["BLUNDER"]:
            return [chess.pgn.NAG_BLUNDER]
        elif delta < self.THRESHOLD["MISTAKE"]:
            return [chess.pgn.NAG_MISTAKE]
        elif delta < self.THRESHOLD["DUBIOUS"]:
            return [chess.pgn.NAG_DUBIOUS_MOVE]
        else:
            return []

    def var_end_comment(self):
        """
        Return a human-readable annotation explaining the board state (if the game
        is over) or a numerical evaluation (if it is not)
        """
        score = self.bestcomment
        depth = self.depth

        if self.board.is_stalemate():
            string = "Stalemate"
        elif self.board.is_insufficient_material():
            string = "Insufficient material to mate"
        elif self.board.can_claim_fifty_moves():
            string = "Fifty move rule"
        elif self.board.can_claim_threefold_repetition():
            string = "Three-fold repetition"
        elif self.board.is_checkmate():
            # checkmate speaks for itself
            string = ""
        else:
            string = "{}/{}".format(str(score), str(depth))

        return string


if __name__ == "__main__":
    pass

# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
