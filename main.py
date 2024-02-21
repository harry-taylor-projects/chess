import pygame
import math

# initialise game
pygame.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
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
dragged_piece = None

# run the game
run = True
while run:

    # drawing the board
    screen.blit(board, (0, 0))

    # drawing the pieces
    for row in range(8):
        for column in range(8):

            # draws pieces according to the board state
            if game_state[row][column] != "empty" and dragged_piece != [column, row]:
                piece_image = pygame.image.load("assets/"+game_state[row][column]+".png")
                piece_image = pygame.transform.scale(piece_image, (150, 150))
                screen.blit(piece_image, [125 * column - 15, 125 * row - 15])

    # draws the dragged piece at the location of the mouse
    if dragged_piece is not None and game_state[dragged_piece[1]][dragged_piece[0]] != "empty":
        piece_image = pygame.image.load("assets/" + game_state[dragged_piece[1]][dragged_piece[0]] + ".png")
        piece_image = pygame.transform.scale(piece_image, (150, 150))
        screen.blit(piece_image, (pygame.mouse.get_pos()[0] - 75, pygame.mouse.get_pos()[1] - 75))

    # check for player interactions
    for event in pygame.event.get():

        # player left clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragged_piece = [math.floor(event.pos[0] / 125), math.floor(event.pos[1] / 125)]

        # player releases the mouse
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if game_state[dragged_piece[1]][dragged_piece[0]] != "empty":
                if min(event.pos) > 0 and max(event.pos) < 1000:
                    new_column = math.floor(event.pos[0] / 125)
                    new_row = math.floor(event.pos[1] / 125)

                    # moves the dragged piece to the new square
                    if dragged_piece != [new_column, new_row]:
                        game_state[new_row][new_column] = game_state[dragged_piece[1]][dragged_piece[0]]
                        game_state[dragged_piece[1]][dragged_piece[0]] = "empty"
                dragged_piece = None

        # stops the game if user closes the window
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
