import pygame
import math

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
            dragged_piece_type = game_state[dragged[0]][dragged[1]]
            if min(event.pos) > 0 and max(event.pos) < 1000:
                new_row, new_column = math.floor(event.pos[1] / 125), math.floor(event.pos[0] / 125)

                # some useful values
                highest, lowest = min(dragged[0], new_row), max(dragged[0], new_row)
                leftmost, rightmost = min(dragged[1], new_column), max(dragged[1], new_column)

                # positive for moving down/right, negative for moving up/left
                row_difference, column_difference = new_row - dragged[0], new_column - dragged[1]

                # determines if move is legal through process of elimination
                legal = True

                # piece must be the right colour
                if (turn not in dragged_piece_type
                        # destination can't be occupied by friendly piece
                        or turn in game_state[new_row][new_column]):
                    legal = False

                # initialises variables based on piece colour (mostly for pawns and checks)
                if "white" in dragged_piece_type:
                    direction, starting_row, enemy = -1, 6, "black"
                else:
                    direction, starting_row, enemy = 1, 1, "white"

                # conditions for pawns
                if "pawn" in dragged_piece_type:
                    # must stay in the same column unless taking
                    if ((column_difference != 0
                         # square in front of pawn must be emtpy
                         or (game_state[dragged[0] + direction][dragged[1]] != "empty"
                             # can only move forward two squares if on second row and destination is empty
                             or ((row_difference != 2 * direction or dragged[0] != starting_row
                                  or game_state[dragged[0] + 2 * direction][dragged[1]] != "empty")
                                 # pawns not on the second row can only move forward one square
                                 and row_difference != direction)))
                            # must be moving diagonally one square only when taking
                            and (abs(column_difference) != 1
                                 or row_difference != direction or enemy not in game_state[new_row][new_column])):
                        legal = False

                # conditions for knights
                if "knight" in dragged_piece_type:
                    # movement must be in an L shape
                    if ((abs(row_difference) != 1 or abs(column_difference) != 2)
                            and (abs(row_difference) != 2 or abs(column_difference) != 1)):
                        legal = False

                # horizontal or vertical movement
                linear = True
                for row in range(highest, lowest + 1):
                    for column in range(leftmost, rightmost + 1):
                        if ((game_state[row][column] != "empty"
                             and [row, column] not in [dragged, [new_row, new_column]])
                                or min(abs(row_difference), abs(column_difference)) != 0):
                            linear = False

                # diagonal movement
                diagonal = True
                if row_difference == column_difference:
                    for distance in range(1, abs(row_difference)):
                        if game_state[highest + distance][leftmost + distance] != "empty":
                            diagonal = False
                elif abs(row_difference) == abs(column_difference):
                    for distance in range(1, abs(row_difference)):
                        if game_state[highest + distance][rightmost - distance] != "empty":
                            diagonal = False
                else:
                    diagonal = False

                # rooks must move horizontally or vertically
                if (("rook" in dragged_piece_type and not linear)
                        # bishops must move diagonally
                        or ("bishop" in dragged_piece_type and not diagonal)
                        # queens must move diagonally or horizontally or vertically
                        or ("queen" in dragged_piece_type and (not linear and not diagonal))):
                    legal = False

                # conditions for king
                if "king" in dragged_piece_type:
                    # movement must be within one row and column
                    if max(abs(row_difference), abs(column_difference)) > 1:
                        legal = False

                # temporarily making move to see if player would be in check
                location_piece_type = game_state[new_row][new_column]
                game_state[new_row][new_column] = dragged_piece_type
                game_state[dragged[0]][dragged[1]] = "empty"

                # locating king
                king_row, king_column = 0, 0
                for row in range(8):
                    for column in range(8):
                        if game_state[row][column] == turn + " king":
                            king_row, king_column = row, column

                # pawn checks
                for x in [-1, 1]:
                    if 7 >= king_row + direction >= 0 and 7 >= king_column + x >= 0:
                        if game_state[king_row + direction][king_column + x] == enemy + " pawn":
                            legal = False

                # horizontal/vertical checks
                linear_movers = [enemy + " rook", enemy + " queen"]
                for x in range(1, king_column + 1):
                    if game_state[king_row][king_column - x] in linear_movers:
                        legal = False
                    elif game_state[king_row][king_column - x] != "empty":
                        break
                for x in range(1, 8 - king_column):
                    if game_state[king_row][king_column + x] in linear_movers:
                        legal = False
                    elif game_state[king_row][king_column + x] != "empty":
                        break
                for y in range(1, king_row + 1):
                    if game_state[king_row - y][king_column] in linear_movers:
                        legal = False
                    elif game_state[king_row - y][king_column] != "empty":
                        break
                for y in range(1, 8 - king_row):
                    if game_state[king_row + y][king_column] in linear_movers:
                        legal = False
                    elif game_state[king_row + y][king_column] != "empty":
                        break

                # diagonal checks
                diagonal_movers = [enemy + " bishop", enemy + " queen"]
                for up_left in range(1, min(king_row, king_column) + 1):
                    if game_state[king_row - up_left][king_column - up_left] in diagonal_movers:
                        legal = False
                    elif game_state[king_row - up_left][king_column - up_left] != "empty":
                        break
                for up_right in range(1, min(king_row, 7 - king_column) + 1):
                    if game_state[king_row - up_right][king_column + up_right] in diagonal_movers:
                        legal = False
                    elif game_state[king_row - up_right][king_column + up_right] != "empty":
                        break
                for down_left in range(1, min(7 - king_row, king_column) + 1):
                    if game_state[king_row + down_left][king_column - down_left] in diagonal_movers:
                        legal = False
                    elif game_state[king_row + down_left][king_column - down_left] != "empty":
                        break
                for down_right in range(1, min(7 - king_row, 7 - king_column) + 1):
                    if game_state[king_row + down_right][king_column + down_right] in diagonal_movers:
                        legal = False
                    elif game_state[king_row + down_right][king_column + down_right] != "empty":
                        break

                # knight checks
                for y, x in zip([-2, -2, -1, -1, 1, 1, 2, 2], [-1, 1, -2, 2, -2, 2, -1, 1]):
                    if 7 >= king_row + y >= 0 and 7 >= king_column + x >= 0:
                        if game_state[king_row + y][king_column + x] == enemy + " knight":
                            legal = False

                # king checks
                for x in [-1, 0, 1]:
                    for y in [-1, 0, 1]:
                        if 7 >= king_row + y >= 0 and 7 >= king_column + x >= 0:
                            if game_state[king_row + y][king_column + x] == enemy + " king":
                                legal = False

                # undo temporary move after looking for checks
                game_state[dragged[0]][dragged[1]] = dragged_piece_type
                game_state[new_row][new_column] = location_piece_type

                # if the move is legal the piece is moved
                if legal:
                    game_state[new_row][new_column] = dragged_piece_type
                    game_state[dragged[0]][dragged[1]] = "empty"
                    if turn == "white":
                        turn = "black"
                    else:
                        turn = "white"
            dragged = None

        # stops the game if user closes the window
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
