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


if __name__ == "__main__":
    pass

# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
