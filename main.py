import pygame
import math


def check(position, check_turn):
    if check_turn == "white":
        direction, enemy = -1, "black"
    else:
        direction, enemy = 1, "white"
    # locating king
    king_row, king_column = 0, 0
    for y in range(8):
        for x in range(8):
            if position[y][x] == check_turn + " king":
                king_row, king_column = y, x

    # pawn checks
    for x in [-1, 1]:
        if 7 >= king_row + direction >= 0 and 7 >= king_column + x >= 0:
            if position[king_row + direction][king_column + x] == enemy + " pawn":
                return True

    # horizontal/vertical checks
    linear_movers = [enemy + " rook", enemy + " queen"]
    for x in range(1, king_column + 1):
        if position[king_row][king_column - x] in linear_movers:
            return True
        elif position[king_row][king_column - x] != "empty":
            break
    for x in range(1, 8 - king_column):
        if position[king_row][king_column + x] in linear_movers:
            return True
        elif position[king_row][king_column + x] != "empty":
            break
    for y in range(1, king_row + 1):
        if position[king_row - y][king_column] in linear_movers:
            return True
        elif position[king_row - y][king_column] != "empty":
            break
    for y in range(1, 8 - king_row):
        if position[king_row + y][king_column] in linear_movers:
            return True
        elif game_state[king_row + y][king_column] != "empty":
            break

    # diagonal checks
    diagonal_movers = [enemy + " bishop", enemy + " queen"]
    for up_left in range(1, min(king_row, king_column) + 1):
        if position[king_row - up_left][king_column - up_left] in diagonal_movers:
            return True
        elif position[king_row - up_left][king_column - up_left] != "empty":
            break
    for up_right in range(1, min(king_row, 7 - king_column) + 1):
        if position[king_row - up_right][king_column + up_right] in diagonal_movers:
            return True
        elif position[king_row - up_right][king_column + up_right] != "empty":
            break
    for down_left in range(1, min(7 - king_row, king_column) + 1):
        if position[king_row + down_left][king_column - down_left] in diagonal_movers:
            return True
        elif position[king_row + down_left][king_column - down_left] != "empty":
            break
    for down_right in range(1, min(7 - king_row, 7 - king_column) + 1):
        if position[king_row + down_right][king_column + down_right] in diagonal_movers:
            return True
        elif position[king_row + down_right][king_column + down_right] != "empty":
            break

    # knight checks
    for y, x in zip([-2, -2, -1, -1, 1, 1, 2, 2], [-1, 1, -2, 2, -2, 2, -1, 1]):
        if 7 >= king_row + y >= 0 and 7 >= king_column + x >= 0:
            if position[king_row + y][king_column + x] == enemy + " knight":
                return True

    # king checks
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            if 7 >= king_row + y >= 0 and 7 >= king_column + x >= 0:
                if position[king_row + y][king_column + x] == enemy + " king":
                    return True

    return False


def legal(board_state, side, location, destination, castle, en_pass):
    # some useful variables
    piece_type = board_state[location[0]][location[1]]
    highest, lowest = min(location[0], destination[0]), max(location[0], destination[0])
    leftmost, rightmost = min(location[1], destination[1]), max(location[1], destination[1])

    # positive for moving down/right, negative for moving up/left
    row_difference, column_difference = destination[0] - location[0], destination[1] - location[1]

    # piece must be the right colour
    if (side not in piece_type
            # destination can't be occupied by friendly piece
            or side in board_state[destination[0]][destination[1]]):
        return False

    # initialises variables based on piece colour (mostly for pawns and checks)
    if "white" in piece_type:
        direction, starting_row, enemy, en_passant_row = -1, 6, "black", 3
    else:
        direction, starting_row, enemy, en_passant_row = 1, 1, "white", 4

    # conditions for pawns
    if "pawn" in piece_type:
        # must stay in the same column unless taking
        if ((column_difference != 0
             # square in front of pawn must be emtpy
             or (board_state[location[0] + direction][location[1]] != "empty"
                 # can only move forward two squares if on second row and destination is empty
                 or ((row_difference != 2 * direction or location[0] != starting_row
                      or board_state[location[0] + 2 * direction][location[1]] != "empty")
                     # pawns not on the second row can only move forward one square
                     and row_difference != direction)))
                # must be moving diagonally one square only when taking
                and (abs(column_difference) != 1
                     or row_difference != direction or
                     (enemy not in board_state[destination[0]][destination[1]]
                      and (en_pass != destination[1] or en_passant_row != location[0])))):
            return False

        # all this code is just so you can't en passant into check
        if destination[1] != location[1] and board_state[destination[0]][destination[1]] == "empty":
            board_state[destination[0]][destination[1]] = side + "pawn"
            board_state[location[0]][location[1]], board_state[en_passant_row][en_pass] = "empty", "empty"
            if check(board_state, side):
                board_state[destination[0]][destination[1]] = "empty"
                board_state[location[0]][location[1]] = side + " pawn"
                board_state[en_passant_row][en_pass] = enemy + " pawn"
                return False
            else:
                board_state[destination[0]][destination[1]] = "empty"
                board_state[location[0]][location[1]] = side + " pawn"
                board_state[en_passant_row][en_pass] = enemy + " pawn"

    # conditions for knights
    if "knight" in piece_type:
        # movement must be in an L shape
        if ((abs(row_difference) != 1 or abs(column_difference) != 2)
                and (abs(row_difference) != 2 or abs(column_difference) != 1)):
            return False

    # horizontal or vertical movement
    linear = True
    for y in range(highest, lowest + 1):
        for x in range(leftmost, rightmost + 1):
            if ((board_state[y][x] != "empty"
                 and [y, x] not in [location, destination])
                    or min(abs(row_difference), abs(column_difference)) != 0):
                linear = False

    # diagonal movement
    diagonal = True
    if row_difference == column_difference:
        for distance in range(1, abs(row_difference)):
            if board_state[highest + distance][leftmost + distance] != "empty":
                diagonal = False
    elif abs(row_difference) == abs(column_difference):
        for distance in range(1, abs(row_difference)):
            if board_state[highest + distance][rightmost - distance] != "empty":
                diagonal = False
    else:
        diagonal = False

    # rooks must move horizontally or vertically
    if (("rook" in piece_type and not linear)
            # bishops must move diagonally
            or ("bishop" in piece_type and not diagonal)
            # queens must move diagonally or horizontally or vertically
            or ("queen" in piece_type and not linear and not diagonal)):
        return False

    # conditions for king
    if "king" in piece_type:
        # movement must be within one row and column unless castling
        if max(abs(row_difference), abs(column_difference)) > 1:
            # can't castle when in check
            if check(board_state, side):
                return False
            # black castling
            elif turn == "black" and location == [0, 4]:
                # queen side castling
                if (destination == [0, 2] and castle[0] and board_state[0][1] == "empty"
                        and board_state[0][2] == "empty" and board_state[0][3] == "empty"):
                    # can't castle through check
                    board_state[0][3], board_state[0][4] = "black king", "empty"
                    if check(board_state, side):
                        board_state[0][3], board_state[0][4] = "empty", "black king"
                        return False
                    else:
                        board_state[0][3], board_state[0][4] = "empty", "black king"
                # king side castling
                elif (destination == [0, 6] and castle[1] and board_state[0][6] == "empty"
                      and board_state[0][5] == "empty"):
                    # can't castle through check
                    board_state[0][4], board_state[0][5] = "empty", "black king"
                    if check(board_state, side):
                        board_state[0][4], board_state[0][5] = "black king", "empty"
                        return False
                    else:
                        board_state[0][4], board_state[0][5] = "black king", "empty"
                else:
                    return False
            # white castling
            elif turn == "white" and location == [7, 4]:
                # queen side castling
                if (destination == [7, 2] and castle[2] and board_state[7][1] == "empty"
                        and board_state[7][2] == "empty" and board_state[7][3] == "empty"):
                    # can't castle through check
                    board_state[7][3], board_state[7][4] = "white king", "empty"
                    if check(board_state, side):
                        board_state[7][3], board_state[7][4] = "empty", "white king"
                        return False
                    else:
                        board_state[7][3], board_state[7][4] = "empty", "white king"
                # king side castling
                elif (destination == [7, 6] and castle[3] and board_state[7][6] == "empty"
                      and board_state[7][5] == "empty"):
                    # can't castle through check
                    board_state[7][4], board_state[7][5] = "empty", "white king"
                    if check(board_state, side):
                        board_state[7][4], board_state[7][5] = "white king", "empty"
                        return False
                    else:
                        board_state[7][4], board_state[7][5] = "white king", "empty"
                else:
                    return False
            else:
                return False

    # see if player would be in check after the move
    destination_piece = board_state[destination[0]][destination[1]]
    board_state[destination[0]][destination[1]] = piece_type
    board_state[location[0]][location[1]] = "empty"

    if check(board_state, side):
        board_state[destination[0]][destination[1]] = destination_piece
        board_state[location[0]][location[1]] = piece_type
        return False
    else:
        board_state[destination[0]][destination[1]] = destination_piece
        board_state[location[0]][location[1]] = piece_type
        return True


# initialise game
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# load/scale image for the board
board = pygame.image.load('assets/board.png')
board = pygame.transform.scale(board, (1000, 1000))

# initialise the state of the board
game_state = [["black rook", "black knight", "black bishop", "black queen",
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
dragged = None

# black queen side, black king side, white queen side, white king side castling rights
castling = [True, True, True, True]

# used to keep track of en passant
en_passant = None

# whose turn it is
turn = "white"

# run the game
run = True
while run:
    # drawing the board
    screen.blit(board, (0, 0))

    # drawing the pieces
    for row in range(8):
        for column in range(8):
            # draws pieces according to the board state
            if game_state[row][column] != "empty" and dragged != [row, column]:
                piece_image = pygame.image.load("assets/" + game_state[row][column] + ".png")
                piece_image = pygame.transform.scale(piece_image, (150, 150))
                screen.blit(piece_image, [125 * column - 15, 125 * row - 15])

    # draws the dragged piece at the location of the mouse
    if dragged is not None and game_state[dragged[0]][dragged[1]] != "empty":
        piece_image = pygame.image.load("assets/" + game_state[dragged[0]][dragged[1]] + ".png")
        piece_image = pygame.transform.scale(piece_image, (150, 150))
        screen.blit(piece_image, (pygame.mouse.get_pos()[0] - 75, pygame.mouse.get_pos()[1] - 75))

    # check for player interactions
    for event in pygame.event.get():
        # player left clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragged = [math.floor(event.pos[1] / 125), math.floor(event.pos[0] / 125)]

        # player releases left click
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if min(event.pos) > 0 and max(event.pos) < 1000:
                new_row, new_column = math.floor(event.pos[1] / 125), math.floor(event.pos[0] / 125)

                # if the move is legal the piece is moved
                dragged_piece = game_state[dragged[0]][dragged[1]]
                if legal(game_state, turn, dragged, [new_row, new_column], castling, en_passant):
                    en_passant = None
                    if "pawn" in dragged_piece:
                        if new_column != dragged[1] and game_state[new_row][new_column] == "empty":
                            game_state[dragged[0]][new_column] = "empty"
                        if abs(new_row - dragged[0]) == 2:
                            en_passant = dragged[1]
                        if turn == "white" and new_row == 0:
                            game_state[new_row][new_column] = "white queen"
                        elif turn == "black" and new_row == 7:
                            game_state[new_row][new_column] = "black queen"
                        else:
                            game_state[new_row][new_column] = dragged_piece
                    elif "king" in dragged_piece:
                        if dragged == [0, 4] and [new_row, new_column] == [0, 2]:
                            game_state[0][0], game_state[0][2], game_state[0][3] = "empty", "black king", "black rook"
                        elif dragged == [0, 4] and [new_row, new_column] == [0, 6]:
                            game_state[0][5], game_state[0][6], game_state[0][7] = "black rook", "black king", "empty"
                        elif dragged == [7, 4] and [new_row, new_column] == [7, 2]:
                            game_state[7][0], game_state[7][2], game_state[7][3] = "empty", "white king", "white rook"
                        elif dragged == [7, 4] and [new_row, new_column] == [7, 6]:
                            game_state[7][5], game_state[7][6], game_state[7][7] = "white rook", "white king", "empty"
                        else:
                            game_state[new_row][new_column] = dragged_piece
                    else:
                        game_state[new_row][new_column] = dragged_piece
                    game_state[dragged[0]][dragged[1]] = "empty"

                    # update castling rights
                    count = 0
                    for row, colour in zip([0, 7], ["black", "white"]):
                        for column in [0, 7]:
                            if game_state[row][column] != colour + " rook" or game_state[row][4] != colour + " king":
                                castling[count] = False

                    # swap turns
                    if turn == "white":
                        turn = "black"
                    else:
                        turn = "white"

                    # search for legal move for checkmate and stalemate
                    available_move = False
                    for from_row in range(8):
                        for from_column in range(8):
                            if turn in game_state[from_row][from_column]:
                                for to_row in range(8):
                                    for to_column in range(8):
                                        if legal(game_state, turn, [from_row, from_column],
                                                 [to_row, to_column], castling, en_passant):
                                            available_move = True
                                            break
                    if not available_move:
                        if check(game_state, turn):
                            print(turn + " has been checkmated.")
                        else:
                            print("The game is a draw by stalemate.")

            dragged = None

        # stops the game if user closes the window
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
