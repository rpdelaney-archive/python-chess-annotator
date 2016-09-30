#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
© Copyright 2016 Ryan Delaney. All rights reserved.
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import argparse
import json
import logging
import chess
import chess.pgn
import chess.uci


# Initiate Logging Module
logger = logging.getLogger(__name__)
if not logger.handlers:
    ch = logging.StreamHandler()
    logger.addHandler(ch)


def parse_args():
    """
    Define an argument parser and return the parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog='annotator.py',
        description='takes a chess game in a PGN file and prints annotations to standard output')
    parser.add_argument("--file", "-f", help="input PGN file", required=True, metavar="FILE.pgn")
    parser.add_argument("--engine", "-e", help="analysis engine", default="stockfish")
    parser.add_argument("--time", "-t", help="how long to spend on analysis", default="1", type=float, metavar="MINUTES")
    parser.add_argument("--verbose", "-v", help="increase verbosity", action="count")

    return parser.parse_args()


def setup_logging(args):
    """
    Sets logging module verbosity according to runtime arguments
    """
    if args.verbose:
        if args.verbose >= 3:
            # EVERYTHING TO LOG FILE
            # fill this in later
            logger.setLevel(logging.DEBUG)
        elif args.verbose == 2:
            # DEBUG TO STDERR
            logger.setLevel(logging.DEBUG)
        elif args.verbose == 1:
            # INFO TO STDERR
            logger.setLevel(logging.INFO)


def eval_numeric(info_handler):
    """
    Returns a numeric evaluation of the position, even if depth-to-mate was
    found. This facilitates comparing numerical evaluations with depth-to-mate
    evaluations
    """
    dtm = info_handler.info["score"][1].mate
    cp = info_handler.info["score"][1].cp

    if dtm is not None:
        # We have depth-to-mate (dtm), so translate it into a numerical
        # evaluation. This number needs to be just big enough to guarantee that
        # it is always greater than a non-dtm evaluation.

        max_score = 10000

        if dtm >= 1:
            return max_score - dtm
        else:
            return -(max_score - dtm)

    elif cp is not None:
        # We don't have depth-to-mate, so return the numerical evaluation (in centipawns)
        return cp

    # If we haven't returned yet, then the info_handler had garbage in it
    raise RuntimeError("Evaluation found in the info_handler was unintelligible")


def eval_human(board, info_handler, invert):
    """
    Returns a human-readable evaluation of the position:
        If depth-to-mate was found, return plain-text mate announcement (e.g. "Mate in 4")
        If depth-to-mate was not found, return an absolute numeric evaluation
    """
    dtm = info_handler.info["score"][1].mate
    cp = info_handler.info["score"][1].cp

    if dtm is not None:
        return "Mate in {}".format(abs(dtm))
    elif cp is not None:
        # We don't have depth-to-mate, so return the numerical evaluation (in pawns)
        if invert:
            return eval_absolute(cp / -100, board.turn)
        else:
            return eval_absolute(cp / 100, board.turn)

    # If we haven't returned yet, then the info_handler had garbage in it
    raise RuntimeError("Evaluation found in the info_handler was unintelligible")


def eval_absolute(number, white_to_move):
    """
    Accepts a relative evaluation (from the point of view of the player to
    move) and returns an absolute evaluation (from the point of view of white)
    """

    if not white_to_move:
        number = -number

    # Humans are used to evaluations padded with zeroes
    return '{:.2f}'.format(number)


def needs_annotation(delta):
    """
    Returns a boolean indicating whether a node with the given evaluations
    should have an annotation added
    """

    return delta > 50


def judge_move(board, played_move, engine, info_handler, searchtime_s):
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
    """

    # Calculate the search time in milliseconds
    searchtime_ms = searchtime_s * 1000

    judgment = {}

    # First, get the engine bestmove and evaluation
    engine.position(board)
    engine.go(movetime=searchtime_ms / 2)

    judgment["bestmove"] = engine.bestmove
    judgment["besteval"] = eval_numeric(info_handler)
    judgment["pv"] = info_handler.info["pv"][1]

    # Annotate the best move
    judgment["bestcomment"] = eval_human(board, info_handler, False)

    # If the played move matches the engine bestmove, we're done
    if played_move == engine.bestmove:
        judgment["playedeval"] = judgment["besteval"]
    else:
        # get the engine evaluation of the played move
        board.push(played_move)                # Put the played move on the board
        engine.position(board)                 # Set the engine position to the board position
        engine.go(movetime=searchtime_ms / 2)  # Run a search on the engine position

        # Store the numeric evaluation.
        # We invert the sign since we're now evaluating from the opponent's perspective
        judgment["playedeval"] = -eval_numeric(info_handler)

        # Take the played move off the stack (reset the board)
        board.pop()

    # Annotate the played move
    judgment["playedcomment"] = eval_human(board, info_handler, True)

    return judgment


def get_nags(judgment):
    """
    Returns a Numeric Annotation Glyph (NAG) according to how much worse the
    played move was vs the best move
    """

    delta = judgment["playedeval"] - judgment["besteval"]

    if delta < -300:
        return [chess.pgn.NAG_BLUNDER]
    elif delta < -150:
        return [chess.pgn.NAG_MISTAKE]
    elif delta < -75:
        return [chess.pgn.NAG_DUBIOUS_MOVE]
    else:
        return []


def var_end_comment(node, score):
    """
    Return a human-readable annotation explaining the board state (if the game
    is over) or a numerical evaluation (if it is not)
    """
    board = node.board()

    if board.is_stalemate():
        return "Stalemate"
    elif board.is_insufficient_material():
        return "Insufficient material to mate"
    elif board.can_claim_fifty_moves():
        return "Fifty move rule"
    elif board.can_claim_threefold_repetition():
        return "Three-fold repetition"
    elif board.is_checkmate():
        # checkmate speaks for itself
        return None
    else:
        return str(score)


def add_annotation(node, judgment):
    """
    Add evaluations and the engine's primary variation as annotations to a node
    """
    prev_node = node.parent

    # Add the engine evaluation
    if judgment["bestmove"] != node.move:
        node.comment = judgment["playedcomment"]

    # Add the engine's primary variation (PV) as an annotation
    # We truncate the PV to 10 moves because engine variations tend to get silly near the end
    prev_node.add_main_variation(judgment["bestmove"])
    var_node = prev_node.variation(judgment["bestmove"])

    for move in judgment["pv"][:10]:
        if var_node.move != move:
            var_node.add_main_variation(move)
            var_node = var_node.variation(move)

    # Add a comment to the end of the variation explaining the game state
    var_node.comment = var_end_comment(var_node, judgment["bestcomment"])

    # We added the variation as the main line, so now it has to be demoted
    # (This is done so that variations can be added to the final node)
    prev_node.demote(judgment["bestmove"])

    # Add a Numeric Annotation Glyph (NAG) according to how weak the played move was
    node.nags = get_nags(judgment)


def classify_opening(fen, ecodb):
    """
    Searches a JSON file with Encyclopedia of Chess Openings (ECO) data to
    check if the given FEN matches an existing opening record

    Returns a classification

    A classfication is a dictionary containing the following elements:
        "code":         The ECO code of the matched opening
        "desc":         The long description of the matched opening
        "path":         The main variation of the opening
    """
    classification = {}
    classification["code"] = ""
    classification["desc"] = ""
    classification["path"] = ""

    for opening in ecodb:
        if opening['f'] == fen:
            classification["code"] = opening['c']
            classification["desc"] = opening['n']
            classification["path"] = opening['m']

    return classification


def eco_fen(node):
    """
    Takes a board position and returns a FEN string formatted for matching with eco.json
    """
    board_fen = node.board().board_fen()
    castling_fen = node.board().castling_xfen()

    if node.board().turn:  # If white to move
        to_move = 'w'
    else:
        to_move = 'b'

    fen = board_fen + " " + to_move + " " + castling_fen
    return fen


def debug_print(node, judgment):
    """
    Prints some debugging info about a position that was just analyzed
    """

    logger.debug(node.board())
    logger.debug(node.board().fen())
    logger.debug("Played move: %s", format(node.parent.board().san(node.move)))
    logger.debug("Best move: %s", format(node.parent.board().san(judgment["bestmove"])))
    logger.debug("Best eval: %s", format(judgment["besteval"]))
    logger.debug("Best comment: %s", format(judgment["bestcomment"]))
    logger.debug("PV: %s", format(node.parent.board().variation_san(judgment["pv"])))
    logger.debug("Played eval: %s", format(judgment["playedeval"]))
    logger.debug("Played comment: %s", format(judgment["playedcomment"]))
    logger.debug("Delta: %s", format(judgment["besteval"] - judgment["playedeval"]))
    logger.debug("")


def cpl(string):
    """
    Centipawn Loss
    Takes a string and returns an integer representing centipawn loss of the move
    We put a ceiling on this value so that big blunders don't skew the acpl too much
    """

    cpl = int(string)
    max_cpl = 1000

    if cpl > max_cpl:
        return max_cpl
    else:
        return cpl


def acpl(cpl_list):
    """
    Average Centipawn Loss
    Takes a list of integers and returns an average of the list contents
    """
    return round(sum(cpl_list) / float(len(cpl_list)), 2)


def main():
    """
    Main function

    - Initialize and handle the UCI analysis engine
    - Attempt to classify the opening with ECO and identify the root node
        * The root node is the position immediately after the ECO classification
        * This allows us to skip analysis of moves that have an ECO classification
    - Analyze the game, adding annotations where appropriate
    - Print the game with the annotations
    """
    args = parse_args()
    setup_logging(args)

    ###########################################################################
    # Initialize the engine
    ###########################################################################
    enginepath = args.engine
    try:
        engine = chess.uci.popen_engine(enginepath)
    except FileNotFoundError:
        errormsg = "Engine '{}' was not found. Aborting...".format(enginepath)
        logger.critical(errormsg)
        raise
    except PermissionError:
        errormsg = "Engine '{}' could not be executed. Aborting...".format(enginepath)
        logger.critical(errormsg)
        raise

    engine.uci()
    info_handler = chess.uci.InfoHandler()
    engine.info_handlers.append(info_handler)

    ###########################################################################
    # Open a PGN file
    ###########################################################################
    pgnfile = args.file
    try:
        with open(pgnfile) as pgn:
            game = chess.pgn.read_game(pgn)
    except PermissionError:
        errormsg = "Input file not readable. Aborting..."
        logger.critical(errormsg)
        raise

    # Check for PGN parsing errors and abort if any were found
    # This prevents us from burning up CPU time on nonsense positions
    if game.errors:
        logger.critical("There were errors parsing the PGN game:")
        for error in game.errors:
            logger.critical(error)
        logger.critical("Aborting...")
        sys.exit(1)

    # Start keeping track of the root node
    # This will change if we successfully classify the opening
    root_node = game.end()
    node = root_node

    # Try to verify that the PGN file was readable
    if node.parent is None:
        errormsg = "Could not render the board. Is the file legal PGN? Aborting..."
        logger.critical(errormsg)
        raise RuntimeError(errormsg)

    ###########################################################################
    # Clear existing comments and variations
    ###########################################################################
    while not node == game.root():
        prev_node = node.parent

        node.comment = None
        for variation in node.variations:
            if not variation.is_main_variation():
                node.remove_variation(variation)

        node = prev_node

    ###########################################################################
    # Attempt to classify the opening and calculate the game length
    ###########################################################################
    node = root_node
    logger.info("Classifying the opening...")

    ecodata = json.load(open('eco/eco.json', 'r'))
    ply_count = 0

    while not node == game.root():
        prev_node = node.parent

        fen = eco_fen(node)
        classification = classify_opening(fen, ecodata)

        if classification["code"] != "":
            # Add some comments classifying the opening
            node.root().headers["ECO"] = classification["code"]
            node.root().headers["Opening"] = classification["desc"]
            node.comment = classification["code"] + " " + classification["desc"]
            # Remember this position so we don't analyze the moves preceding it later
            root_node = node
            # Break (don't classify previous positions)
            break

        ply_count += 1
        node = prev_node

    node = game.end()

    ###########################################################################
    # Perform game analysis
    ###########################################################################

    # Calculate how many seconds we have to accomplish this
    # The parameter is priced in minutes so we convert to seconds
    budget = float(args.time) * 60
    logger.debug("Total budget is {} seconds".format(budget))

    # First pass:
    #
    #   - Performs a shallow-depth search to the root node
    #   - Leaves annotations showing the centipawn loss of each move
    #
    # These annotations form the basis of the second pass, which will analyze
    # those moves that had a high centipawn loss (mistakes)

    # We have a fraction of the total budget to finish the first pass
    pass1_budget = budget / 10

    time_per_move = float(pass1_budget) / float(ply_count)

    logger.debug("Pass 1 budget is %i seconds, with %f seconds per move", pass1_budget, time_per_move)

    # Loop through the game doing shallow analysis
    logger.info("Performing first pass...")

    # Count the number of mistakes that will have to be annotated later
    error_count = 0

    node = game.end()
    while not node == root_node:
        # Remember where we are
        prev_node = node.parent

        # Get the engine judgment of the played move in this position
        judgment = judge_move(prev_node.board(), node.move, engine, info_handler, time_per_move)
        delta = judgment["besteval"] - judgment["playedeval"]

        # Record the delta, to be referenced in the second pass
        node.comment = str(delta)

        # Count the number of mistakes that will have to be annotated later
        if needs_annotation(delta):
            error_count += 1

        # Print some debugging info
        debug_print(node, judgment)

        # Go to the previous node
        node = prev_node

    # Calculate the average centipawn loss (ACPL) for each player
    white_cpl = []
    black_cpl = []

    node = game.end()
    while not node == root_node:
        prev_node = node.parent

        if node.board().turn:
            black_cpl.append(cpl(node.comment))
        else:
            white_cpl.append(cpl(node.comment))

        node = prev_node

    node.root().headers["White ACPL"] = acpl(white_cpl)
    node.root().headers["Black ACPL"] = acpl(black_cpl)

    # Second pass:
    #
    #   - Iterate through the comments looking for moves with high centipawn
    #   loss
    #   - Leaves annotations on those moves showing what the player could have
    #   done instead
    #

    # We use the rest of the budgeted time to perform the second pass
    pass2_budget = budget - pass1_budget
    logger.debug("Pass 2 budget is %i seconds", pass2_budget)

    try:
        time_per_move = pass2_budget / error_count
    except ZeroDivisionError:
        logger.debug("No errors found on first pass!")
        # There were no mistakes in the game, so deeply analyze all the moves
        time_per_move = pass2_budget / ply_count
        node = game.end()
        while not node == root_node:
            prev_node = node.parent
            # Reset the comments to a value high enough to ensure that they all get analyzed
            node.comment = '8593'
            node = prev_node

    # Loop through the game doing deep analysis on the flagged moves
    logger.info("Performing second pass...")

    node = game.end()
    while not node == root_node:
        # Remember where we are
        prev_node = node.parent

        delta = int(node.comment)

        if needs_annotation(delta):
            # Get the engine judgment of the played move in this position
            judgment = judge_move(prev_node.board(), node.move, engine, info_handler, time_per_move)

            # Verify that the engine still dislikes the played move
            delta = judgment["besteval"] - judgment["playedeval"]
            if needs_annotation(delta):
                add_annotation(node, judgment)
            else:
                node.comment = None

            # Print some debugging info
            debug_print(node, judgment)
        else:
            node.comment = None

        # Go to the previous node
        node = prev_node

    ###########################################################################

    annotator = engine.name
    node.root().comment = annotator
    node.root().headers["Annotator"] = annotator

    # Print out the PGN with all the annotations we've added
    print(node.root())

if __name__ == "__main__":
    main()

# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
