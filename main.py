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
            # dragged[0] is the row
            # dragged[1] is the column

        # player releases left click
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragged_piece_type = game_state[dragged[0]][dragged[1]]
            if dragged_piece_type != "empty" and min(event.pos) > 0 and max(event.pos) < 1000:
                new_row, new_column = math.floor(event.pos[1] / 125), math.floor(event.pos[0] / 125)

                # checks if move is legal through process of elimination
                legal = True

                # can't move wrong coloured piece
                if turn not in dragged_piece_type:
                    legal = False

                # can't move to a square occupied by friendly piece
                if turn in game_state[new_row][new_column]:
                    legal = False

                # some useful values
                highest, lowest = min(dragged[0], new_row), max(dragged[0], new_row)
                leftmost, rightmost = min(dragged[1], new_column), max(dragged[1], new_column)

                # positive for moving down/right, negative for moving up/left
                row_difference, column_difference = new_row - dragged[0], new_column - dragged[1]

                # conditions for pawns
                if "pawn" in dragged_piece_type:
                    # determines which direction pawns can move depending on colour
                    if "white" in dragged_piece_type:
                        direction = -1
                    else:
                        direction = 1
                    # must stay in the same column if you aren't taking
                    if column_difference == 0:
                        # square in front of pawn must be emtpy
                        if game_state[dragged[0] + direction][dragged[1]] != "empty":
                            legal = False
                        # can only move forward two squares if on second row and destination is empty
                        if row_difference == 2 * direction:
                            if game_state[dragged[0] + (2 * direction)][dragged[1]] == "empty":
                                # funky way of mapping 1 to 1 and -1 to 6
                                if dragged[0] != 3.5 - (2.5 * direction):
                                    legal = False
                            else:
                                legal = False
                        # pawns not on the second row can only move forward one square
                        elif row_difference != 1 * direction:
                            legal = False
                    # must be moving diagonally one square only when taking
                    elif abs(column_difference) == 1:
                        if row_difference == 1 * direction:
                            if "white" in dragged_piece_type:
                                if "black" not in game_state[new_row][new_column]:
                                    legal = False
                            else:
                                if "white" not in game_state[new_row][new_column]:
                                    legal = False
                        else:
                            legal = False
                    else:
                        legal = False

                # conditions for rooks
                if "rook" in dragged_piece_type:
                    # movement must be horizontal or vertical with empty squares inbetween
                    if row_difference == 0:
                        for column in range(leftmost + 1, rightmost):
                            if game_state[dragged[0]][column] != "empty":
                                legal = False
                    elif column_difference == 0:
                        for row in range(highest + 1, lowest):
                            if game_state[row][dragged[1]] != "empty":
                                legal = False
                    else:
                        legal = False

                # conditions for knights
                if "knight" in dragged_piece_type:
                    # movement must be in an L shape
                    if abs(row_difference) != 1 or abs(column_difference) != 2:
                        if abs(row_difference) != 2 or abs(column_difference) != 1:
                            legal = False

                # conditions for bishops
                if "bishop" in dragged_piece_type:
                    # movement must be diagonal with empty squares inbetween
                    if row_difference == column_difference:
                        for distance in range(1, abs(row_difference)):
                            if game_state[highest + distance][leftmost + distance] != "empty":
                                legal = False
                    elif abs(row_difference) == abs(column_difference):
                        for distance in range(1, abs(row_difference)):
                            if game_state[highest + distance][rightmost - distance] != "empty":
                                legal = False
                    else:
                        legal = False

                # conditions for queens
                if "queen" in dragged_piece_type:
                    # movement must be diagonal/horizontal/vertical with empty square inbetween
                    if row_difference == 0:
                        for column in range(leftmost + 1, rightmost):
                            if game_state[dragged[0]][column] != "empty":
                                legal = False
                    elif column_difference == 0:
                        for row in range(highest + 1, lowest):
                            if game_state[row][dragged[1]] != "empty":
                                legal = False
                    elif row_difference == column_difference:
                        for distance in range(1, abs(row_difference)):
                            if game_state[highest + distance][leftmost + distance] != "empty":
                                legal = False
                    elif abs(row_difference) == abs(column_difference):
                        for distance in range(1, abs(row_difference)):
                            if game_state[highest + distance][rightmost - distance] != "empty":
                                legal = False
                    else:
                        legal = False

                # conditions for king
                if "king" in dragged_piece_type:
                    # movement must be within one row and column
                    if max(abs(row_difference), abs(column_difference)) > 1:
                        legal = False

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
