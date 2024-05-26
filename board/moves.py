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
    
def flip_fen(fen):
    # Split the FEN string into parts (position, side to move, castling, en passant, halfmove clock, fullmove number)
    parts = fen.split(' ')
    # Only flip the board position part, which is the first element in the parts list
    position = parts[0]
    
    # Reverse the order of ranks in the position part
    flipped_position = '/'.join(position.split('/')[::-1])
    
    # Replace the original position with the flipped one
    parts[0] = flipped_position
    
    # Reconstruct the full FEN string
    flipped_fen = ' '.join(parts)
    return flipped_fen

def correct_fen_for_black_top(fen):
    parts = fen.split(' ')
    position = parts[0]
    ranks = position.split('/')
    
    # Reverse the order of ranks
    flipped_ranks = ranks[::-1]
    
    # Reverse the order of files within each rank
    flipped_files_ranks = [rank[::-1] for rank in flipped_ranks]
    
    # Reassemble the full FEN string
    parts[0] = '/'.join(flipped_files_ranks)
    corrected_fen = ' '.join(parts)
    return corrected_fen

def mirror_fen(fen):
    parts = fen.split(' ')
    position = parts[0]
    ranks = position.split('/')
    
    # Reverse the order of ranks and reverse the order of files within each rank
    mirrored_ranks = ['/'.join(rank[::-1] for rank in ranks)][::-1]
    
    # Reassemble the full FEN string
    parts[0] = '/'.join(mirrored_ranks)
    mirrored_fen = ' '.join(parts)
    return mirrored_fen
     
# def output_board_best_move(fen, stockfish):
#     move = determine_best_move(fen, stockfish)
#     if move:
#         board = chess.Board(fen)
#         move_from = chess.parse_square(move[0])
#         move_to = chess.parse_square(move[1])
#         arrows = [chess.svg.Arrow(move_from, move_to, color="#0000cccc")]
#         svg = chess.svg.board(board=board, arrows=arrows, size=350)
#         return SVG(svg)
#     else:
#         return None

def output_board_best_move(fen, stockfish, white_or_black_top='black'):
    move = determine_best_move(fen, stockfish)
    if move:
        board = chess.Board(fen)
        # Set the orientation based on the parameter passed
        if white_or_black_top == 'white':
            board.turn = chess.WHITE
        else:
            board.turn = chess.BLACK
            
        move_from = chess.parse_square(move[0])
        move_to = chess.parse_square(move[1])
        arrows = [chess.svg.Arrow(move_from, move_to, color="#0000cccc")]
        
        # Generate the SVG with the specified orientation
        svg = chess.svg.board(board=board, arrows=arrows, size=350, orientation=chess.WHITE if white_or_black_top == 'black' else chess.BLACK)
        return SVG(svg)
    else:
        return None
    



