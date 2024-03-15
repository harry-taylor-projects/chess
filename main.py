from copy import deepcopy
import pygame
import math


def move(temp_board, move_from, move_to):

    # manipulate a copy of the board
    move_board = deepcopy(temp_board)
    piece = move_board[move_from[0]][move_from[1]]
    destination_piece = move_board[move_to[0]][move_to[1]]

    # moves piece to its destination
    move_board[move_from[0]][move_from[1]] = "empty"
    move_board[move_to[0]][move_to[1]] = piece

    # moving for en passant and pawn promotion
    if "pawn" in piece:
        if move_to[1] != move_from[1] and destination_piece == "empty":
            move_board[move_from[0]][move_to[1]] = "empty"
        if move_to[0] == 0:
            move_board[move_to[0]][move_to[1]] = "white queen"
        elif move_to[0] == 7:
            move_board[move_to[0]][move_to[1]] = "black queen"

    # moving for castling
    elif "king" in piece:
        for edge, side in zip([0, 7], ["black", "white"]):
            for empty, king, rook in zip([0, 7], [2, 6], [3, 5]):
                if move_from == [edge, 4] and move_to == [edge, king]:
                    move_board[edge][empty], move_board[edge][rook] = "empty", side + " rook"

    return move_board


def check(check_board, check_turn):
    # useful variables
    direction = -1 if check_turn == "white" else 1
    enemy = "black" if check_turn == "white" else "white"

    # locating king
    king_row, king_column = 0, 0
    for y in range(8):
        for x in range(8):
            if check_board[y][x] == check_turn + " king":
                king_row, king_column = y, x

    # checks in a straight line
    linear_movers = [enemy + " rook", enemy + " queen"]
    diagonal_movers = [enemy + " bishop", enemy + " queen"]
    # sign represents the eight different directions the king can be checked from
    for sign in [0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]:
        for distance in range(1, 8):
            if 7 >= king_row + (sign[0] * distance) >= 0 and 7 >= king_column + (sign[1] * distance) >= 0:
                check_position = check_board[king_row + (sign[0] * distance)][king_column + (sign[1] * distance)]
                # rooks and queens
                if ((check_position in linear_movers and abs(sign[0]) + abs(sign[1]) == 1)
                        # bishops and queens
                        or (check_position in diagonal_movers and abs(sign[0]) + abs(sign[1]) == 2)
                        # kings
                        or (check_position == enemy + " king" and distance == 1)
                        # pawns
                        or (check_position == enemy + " pawn" and sign[0] == direction
                            and abs(sign[1]) == 1 and distance == 1)):
                    return True
                elif check_position != "empty":
                    break

    # knight checks
    for y, x in zip([-2, -2, -1, -1, 1, 1, 2, 2], [-1, 1, -2, 2, -2, 2, -1, 1]):
        if 7 >= king_row + y >= 0 and 7 >= king_column + x >= 0:
            if check_board[king_row + y][king_column + x] == enemy + " knight":
                return True

    return False


def legal(legal_board, legal_turn, legal_from, legal_to, legal_castle, legal_en_passant):
    # some useful variables
    board_copy = deepcopy(legal_board)
    piece = legal_board[legal_from[0]][legal_from[1]]
    highest, lowest = min(legal_from[0], legal_to[0]), max(legal_from[0], legal_to[0])
    leftmost, rightmost = min(legal_from[1], legal_to[1]), max(legal_from[1], legal_to[1])

    # positive for moving down/right, negative for moving up/left
    row_difference, column_difference = legal_to[0] - legal_from[0], legal_to[1] - legal_from[1]

    # initialises variables based on piece colour (mostly for pawns and checks)
    if "white" in piece:
        direction, starting_row, enemy, en_passant_row = -1, 6, "black", 3
    else:
        direction, starting_row, enemy, en_passant_row = 1, 1, "white", 4

    # piece must be the right colour
    if (legal_turn not in piece
            # destination can't be occupied by friendly piece
            or legal_turn in legal_board[legal_to[0]][legal_to[1]]):
        return False

    # conditions for pawns
    if "pawn" in piece:
        # must stay in the same column unless taking
        if ((column_difference != 0
             # square in front of pawn must be emtpy
             or (legal_board[legal_from[0] + direction][legal_from[1]] != "empty"
                 # can only move forward two squares if on second row and destination is empty
                 or ((row_difference != 2 * direction or legal_from[0] != starting_row
                      or legal_board[legal_from[0] + 2 * direction][legal_from[1]] != "empty")
                     # pawns not on the second row can only move forward one square
                     and row_difference != direction)))
                # must be moving diagonally one square only when taking
                and (abs(column_difference) != 1
                     or row_difference != direction or
                     (enemy not in legal_board[legal_to[0]][legal_to[1]]
                      and (legal_en_passant != legal_to[1] or en_passant_row != legal_from[0])))):
            return False

    # conditions for knights
    if "knight" in piece:
        # movement must be in an L shape
        if ((abs(row_difference) != 1 or abs(column_difference) != 2)
                and (abs(row_difference) != 2 or abs(column_difference) != 1)):
            return False

    # horizontal or vertical movement
    linear = True
    for y in range(highest, lowest + 1):
        for x in range(leftmost, rightmost + 1):
            if ((legal_board[y][x] != "empty"
                 and [y, x] not in [legal_from, legal_to])
                    or min(abs(row_difference), abs(column_difference)) != 0):
                linear = False

    # diagonal movement
    diagonal = True
    if row_difference == column_difference:
        for distance in range(1, abs(row_difference)):
            if legal_board[highest + distance][leftmost + distance] != "empty":
                diagonal = False
    elif abs(row_difference) == abs(column_difference):
        for distance in range(1, abs(row_difference)):
            if legal_board[highest + distance][rightmost - distance] != "empty":
                diagonal = False
    else:
        diagonal = False

    # rooks must move horizontally or vertically
    if (("rook" in piece and not linear)
            # bishops must move diagonally
            or ("bishop" in piece and not diagonal)
            # queens must move diagonally or horizontally or vertically
            or ("queen" in piece and not linear and not diagonal)):
        return False

    # conditions for king
    if "king" in piece:
        # movement must be within one row and column unless castling
        if max(abs(row_difference), abs(column_difference)) > 1:
            # can't castle when in check
            if check(legal_board, legal_turn):
                return False
            # must be on the right square
            if (turn != "black" or legal_from != [0, 4]) and (turn != "white" or legal_from != [7, 4]):
                return False
            for back_row, castle_turn, i in zip([0, 7], ["black", "white"], [0, 2]):
                if turn == castle_turn and legal_from == [back_row, 4]:
                    if ((legal_to != [back_row, 2] or not legal_castle[i] or legal_board[back_row][1] != "empty"
                         or legal_board[back_row][2] != "empty" or legal_board[back_row][3] != "empty"
                            or check(move(board_copy, [back_row, 4], [back_row, 3]), legal_turn))
                            and (legal_to != [back_row, 6] or not legal_castle[i + 1] or
                                 legal_board[back_row][6] != "empty" or legal_board[back_row][5] != "empty"
                                 or check(move(board_copy, [back_row, 4], [back_row, 5]), legal_turn))):
                        return False

    board_copy = deepcopy(legal_board)
    in_check = check(move(board_copy, legal_from, legal_to), legal_turn)
    return False if in_check else True


# initialise game
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# load/scale image for the board
board_image = pygame.image.load('assets/board.png')
board_image = pygame.transform.scale(board_image, (1000, 1000))

# initialise the state of the board
board = [["black rook", "black knight", "black bishop", "black queen",
          "black king", "black bishop", "black knight", "black rook"],
         ["black pawn", "black pawn", "black pawn", "black pawn",
          "black pawn", "black pawn", "black pawn", "black pawn"],
         ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
         ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
         ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
         ["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
         ["white pawn", "white pawn", "white pawn", "white pawn",
          "white pawn", "white pawn", "white pawn", "white pawn"],
         ["white rook", "white knight", "white bishop", "white queen",
          "white king", "white bishop", "white knight", "white rook"]]

# used to drag pieces around
location = None
# black queen side, black king side, white queen side, white king side castling rights
castle = [True, True, True, True]
# used to keep track of en passant
en_passant = None

# whose turn it is
turn = "white"

# run the game
run = True
while run:
    # drawing the board
    screen.blit(board_image, (0, 0))

    # drawing the pieces
    for row in range(8):
        for column in range(8):
            # draws pieces according to the board state
            if board[row][column] != "empty" and location != [row, column]:
                piece_image = pygame.image.load("assets/" + board[row][column] + ".png")
                piece_image = pygame.transform.scale(piece_image, (150, 150))
                screen.blit(piece_image, [125 * column - 15, 125 * row - 15])

    # draws the dragged piece at the location of the mouse
    if location is not None and board[location[0]][location[1]] != "empty":
        piece_image = pygame.image.load("assets/" + board[location[0]][location[1]] + ".png")
        piece_image = pygame.transform.scale(piece_image, (150, 150))
        screen.blit(piece_image, (pygame.mouse.get_pos()[0] - 75, pygame.mouse.get_pos()[1] - 75))

    # check for player interactions
    for event in pygame.event.get():
        # player left clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            location = [math.floor(event.pos[1] / 125), math.floor(event.pos[0] / 125)]

        # player releases left click
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if min(event.pos) > 0 and max(event.pos) < 1000:
                destination = [math.floor(event.pos[1] / 125), math.floor(event.pos[0] / 125)]

                # if the move is legal the move is made
                if legal(board, turn, location, destination, castle, en_passant):
                    board = move(board, location, destination)

                    # update en passant
                    en_passant = location[1] if abs(destination[0] - location[0]) == 2 else None

                    # update castling rights
                    count = 0
                    for row, colour in zip([0, 7], ["black", "white"]):
                        for column in [0, 7]:
                            if board[row][column] != colour + " rook" or board[row][4] != colour + " king":
                                castle[count] = False
                            count += 1

                    # swap turns
                    turn = "white" if turn == "black" else "black"

                    # search for checkmate and stalemate
                    available_move = False
                    for from_row in range(8):
                        for from_column in range(8):
                            if turn in board[from_row][from_column]:
                                for to_row in range(8):
                                    for to_column in range(8):
                                        if legal(board, turn, [from_row, from_column],
                                                 [to_row, to_column], castle, en_passant):
                                            available_move = True
                                            break
                    if not available_move:
                        print(turn + " has been checkmated.") if check(board, turn) else "Draw by stalemate."

            location = None

        # stops the game if user closes the window
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
