#!/usr/bin/env python3

"""
© Copyright 2016 Ryan Delaney. All rights reserved.

Reads a chess game in PGN format (https://en.wikipedia.org/wiki/Portable_Game_Notation)
Uses an engine (stockfish) to evaluate the quality of play and add annotations (https://github.com/official-stockfish/Stockfish)
Prints PGN data with the added annotations

TODO:
  Don't hardcode the engine and PGN inputs - read them from somewhere (args? STDIN?) (check out argparse)
  Don't truncate a PV that ends in mate
  Try to cut down on the "magic numbers" somehow (dictionary?)
  Time-based analysis limits: instead of specifying a searchdepth, give a time limit on how long to spend analyzing the game
  Don't annotate positions where one side has an overwhelming advantage: build extra logic into needs_annotation()
"""

import chess
import chess.uci
import chess.pgn


class Evaluation(object):

    def __init__(self, info_handler):
        self.info_handler = info_handler
        # Let's just pass the score, since that's all this function needs
        self.numeric = self.get_numeric(info_handler['score'][1].cp)
        # For this function, we'll let it use the class member
        self.human_eval = self.get_human_eval()

    # The static method decorator means this function does not get the
    # standard first argument passed to any instance method of a class: self
    # self is the instance in question
    # Whether it makes sense to have this as a separate function or just roll
    # it into __init__ is sort of a testability/style thing
    @staticmethod
    def numeric(info_handler):
        """
        Returns a numeric evaluation of the position, even if depth-to-mate was
        found. This facilitates comparing numerical evaluations with depth-to-mate
        evaluations
        """
        if info_handler.info["score"][1].mate is not None:
            # We have depth-to-mate (dtm), so translate it into a numerical
            # evaluation. This number needs to be just big enough to guarantee that
            # it is always greater than a non-dtm evaluation.

            max_score = 10000
            dtm = info_handler.info["score"][1].mate

            if dtm >= 1:
                result = max_score-dtm
            else:
                result = -(max_score-dtm)

        elif info_handler.info["score"][1].cp is not None:
            # We don't have depth-to-mate, so return the numerical evaluation (in centipawns)
            result = info_handler.info["score"][1].cp

        return result

    # As an alternative, instead of using a static method, we can use a
    # normal instance method, and let the method access the instance's
    # info_handler member
    def human(info_handler):
        """
        Returns a human-readable evaluation of the position:
            If depth-to-mate was found, return plain-text mate announcement (e.g. "White mates in 4")
            If depth-to-mate was not found, return an absolute numeric evaluation
        """
        # Get the score, what we really care about
        if info_handler.info["score"][1].mate is not None:
            return "Mate in ", score.mate
        elif info_handler.info["score"][1].cp is not None:
            # We don't have depth-to-mate, so return the numerical evaluation (in pawns)
            return str(info_handler.info["score"][1].cp / 100)


    def absolute(number, white_to_move):
        """
        Accepts a relative evaluation (from the point of view of the player to
        move) and returns an absolute evaluation (from the point of view of white)
        """

        if not white_to_move:
            number = -number

        # Humans are used to evaluations padded with zeroes
        return '{:.2f}'.format(number)


def needs_annotation(judgment):
    """
    Returns a boolean indicating whether a node with the given evaluations
    should have an annotation added
    """
    delta = judgment["playedeval"] - judgment["besteval"]

    return delta < -50


def judge_move(board, played_move, engine, info_handler, searchdepth):
    """
     Evaluate the strength of a given move by comparing it to engine's best
     move and evaluation at a given depth, in a given board context

     Returns a judgment

     A judgment is a dictionary containing the following elements:
           "bestmove":     The best move in the position, according to the engine
           "besteval":     A numeric evaluation of the position after the best move is played
           "pv":           The engine's primary variation including the best move
           "playedeval":   A numeric evaluation of the played move
    """

    judgment = {}

    # First, get the engine bestmove and evaluation
    engine.position(board)
    engine.go(depth=searchdepth)

    judgment["bestmove"] = engine.bestmove
    judgment["besteval"] = Evaluation.numeric(info_handler)
    judgment["pv"] = info_handler.info["pv"][1]

    # If the played move matches the engine bestmove, we're done
    if played_move == engine.bestmove:
        judgment["playedeval"] = judgment["besteval"]
    else:
        # get the engine evaluation of the played move
        board.push(played_move)                             # Put the played move on the board
        engine.position(board)                              # Set the engine position to the board position
        engine.go(depth=searchdepth)                        # Run a search on the engine position to depth = searchdepth

        judgment["playedeval"] = -Evaluation.numeric(info_handler)  # Store the numeric evaluation. We invert the sign since we're now evaluating from the opponent's perspective

        # Take the played move off the stack (reset the board)
        board.pop()

    return judgment


def get_nags(judgment):
    """
    Returns a Numeric Annotation Glyph (NAG) according to how much worse the
    played move was vs the best move
    """

    delta = judgment["playedeval"] - judgment["besteval"]

    nags = []

    if delta < -300:
        nags = [chess.pgn.NAG_BLUNDER]
    elif delta < -150:
        nags = [chess.pgn.NAG_MISTAKE]
    elif delta < -75:
        nags = [chess.pgn.NAG_DUBIOUS_MOVE]

    # If the played move retains an overwhelming advantage, then it can't be a mistake or blunder
    if judgment["playedeval"] > 800:
        nags = []

    # If the best move still gets an overwhelming disadvantage, then the played move can't be a mistake or a blunder
    if judgment["besteval"] < -800:
        nags = []

    return nags


def var_end_comment(node, score):
    """
    Return a human-readable annotation explaining the board state (if the game
    is over) or a numerical evaluation (if it is not)
    """
    if node.board().is_stalemate():
        return "Stalemate"
    elif node.board().is_insufficient_material():
        return "Insufficient material to mate"
    elif node.board().can_claim_fifty_moves():
        return "Fifty move rule"
    elif node.board().can_claim_threefold_repetition():
        return "Three-fold repetition"
    elif node.board().is_checkmate():
        # checkmate speaks for itself
        return ""
    else:
        return score


def add_annotation(node, handler, judgment, searchdepth):
    """
    Add evaluations and the engine's primary variation as annotations to a node
    """
    prev_node = node.parent

    # Calculate absolute scores in pawns rather than centipawns (these are easier for humans to read)
    human_played_score = Evaluation.absolute(judgment["playedeval"] / 100, node.parent.board().turn)
    human_best_score = Evaluation.absolute(judgment["besteval"] / 100, node.parent.board().turn)

    # Add the engine evaluation
    if judgment["bestmove"] != node.move:
        node.comment = str(human_played_score)

    # Add the engine's primary variation (PV) as an annotation
    # We truncate the PV to one half the search depth because engine variations tend to get silly near the end
    prev_node.add_main_variation(judgment["bestmove"])
    var_node = prev_node.variation(judgment["bestmove"])
    max_var_length = searchdepth // 2

    for move in judgment["pv"][:max_var_length]:
        if var_node.move != move:
            var_node.add_main_variation(move)
            var_node = var_node.variation(move)

    # Add a comment to the end of the variation explaining the game state
    var_node.comment = var_end_comment(var_node, human_best_score)

    # We added the variation as the main line, so now it has to be demoted
    # (This is done so that variations can be added to the final node)
    prev_node.demote(judgment["bestmove"])

    # Add a Numeric Annotation Glyph (NAG) according to how weak the played move was
    node.nags = get_nags(judgment)


def main():
    # Initialize the engine
    engine = chess.uci.popen_engine("/usr/bin/stockfish")
    engine.uci()
    info_handler = chess.uci.InfoHandler()
    engine.info_handlers.append(info_handler)
    depth = 15

    # Open a PGN file
   #pgnfile = "/home/ryan/game.pgn"
   #pgnfile = "/home/ryan/mini.pgn"
    pgnfile = "foo.pgn"
   #pgnfile = "karpov.pgn"
   #pgnfile = "zugswang.pgn"
   #pgnfile = "giri-ding.pgn"
   #pgnfile = "bird.pgn"
   #pgnfile = "stale.pgn"
    with open(pgnfile) as pgn:
        game = chess.pgn.read_game(pgn)

    # Advance to the end of the game
    node = game.end()

    # Analyze the final position
    if node.board().is_game_over():
        node.comment = var_end_comment(node, "")
    else:
        judgment = judge_move(node.parent.board(), node.move, engine, info_handler, depth)
        add_annotation(node, info_handler, judgment, depth)
    node = node.parent

    # We start at the end of the game and go backward so that the engine can
    # make use of its cache when evaluating positions
    while not node == game.root():
        # Remember where we are
        prev_node = node.parent

        # Print some debugging info
        print(node.board())
        print(node.board().fen())
        print("Played move: ", prev_node.board().san(node.move))

        # Get the engine judgment of the played move in this position
        judgment = judge_move(prev_node.board(), node.move, engine, info_handler, depth)

        if needs_annotation(judgment):
            add_annotation(node, info_handler, judgment, depth)

        # Print some debugging info
        print("Best move: ",      prev_node.board().san(judgment["bestmove"]))
        print("Best eval: ",      str(judgment["besteval"]))
        print("PV: ",             prev_node.board().variation_san(judgment["pv"]))
        print("Played eval: ",    str(judgment["playedeval"]))
        print("Delta: ",          str(judgment["playedeval"] - judgment["besteval"]))
        print("")

        node = prev_node

    node.comment = engine.name + " Depth: " + str(depth)

    # Print out the PGN with all the annotations we've added
    print(node)

if __name__ == "__main__":
    main()
