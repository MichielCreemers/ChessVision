from stockfish import Stockfish
import chess.svg
import chess
import re
from IPython.display import SVG

# Load the stockfish engine
# ...

def determineFEN(pieceplacement, turnof):
    p = re.compile('^.*/')
    rank1 = p.sub("", pieceplacement)
    p = re.compile('/.*$')
    rank8 = p.sub("", pieceplacement)

    print(rank1)
    print(rank8)
    
    blackQ = re.search('^r(3|2.|.2|1..|.1.|..1|...)k',rank8)
    blackK = re.search('k(2|1.|.1|..)r$',rank8)
    whiteQ = re.search('^R(3|2.|.2|1..|.1.|..1|...)K',rank1)
    whiteK = re.search('K(2|1.|.1|..)R$',rank1)


    if(blackQ == None):
        bQ = ''
    else:
        bQ = 'q'
    if(blackK == None):
        bK = ''
    else:
        bK = 'k'
    if(whiteQ == None):
        wQ = ''
    else:
        wQ = 'Q'
    if(whiteK == None):
        wK = ''
    else:
        wK = 'K'

    castleinformation = wK + wQ + bK + bQ
    if castleinformation == '':
        castleinformation = '-'
    print(castleinformation)
    FEN = pieceplacement + " " + turnof + " " + castleinformation + " - 0 0"
    print(FEN)
    return FEN

def is_valid_fen(fen):
    return re.match(r'^[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+ [bw] [KQkq-]+ [a-h1-8-]* \d+ \d+$', fen) is not None


def determine_best_move(fen, stockfish):
    if is_valid_fen(fen):
        stockfish.set_fen_position(fen)
        best_move = stockfish.get_best_move()
        if best_move:
            best_move_from = best_move[:2]
            best_move_to = best_move[2:]
            return (best_move_from, best_move_to)
        return None
    else:
        return None
    
def output_board_best_move(fen, stockfish):
    move = determine_best_move(fen, stockfish)
    if move:
        board = chess.Board(fen)
        move_from = chess.parse_square(move[0])
        move_to = chess.parse_square(move[1])
        arrows = [chess.svg.Arrow(move_from, move_to, color="#0000cccc")]
        svg = chess.svg.board(board=board, arrows=arrows, size=350)
        return SVG(svg)
    else:
        return None
    


