import pygame
import math

# initialise game
pygame.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# load/scale images for the board and pieces
board = pygame.image.load('assets/board.png')
board = pygame.transform.scale(board, (1000, 1000))
white_pawn = pygame.image.load('assets/white pawn.png')
white_pawn = pygame.transform.scale(white_pawn, (150, 150))
white_rook = pygame.image.load('assets/white rook.png')
white_rook = pygame.transform.scale(white_rook, (150, 150))
white_knight = pygame.image.load('assets/white knight.png')
white_knight = pygame.transform.scale(white_knight, (150, 150))
white_bishop = pygame.image.load('assets/white bishop.png')
white_bishop = pygame.transform.scale(white_bishop, (150, 150))
white_queen = pygame.image.load('assets/white queen.png')
white_queen = pygame.transform.scale(white_queen, (150, 150))
white_king = pygame.image.load('assets/white king.png')
white_king = pygame.transform.scale(white_king, (150, 150))
black_pawn = pygame.image.load('assets/black pawn.png')
black_pawn = pygame.transform.scale(black_pawn, (150, 150))
black_rook = pygame.image.load('assets/black rook.png')
black_rook = pygame.transform.scale(black_rook, (150, 150))
black_knight = pygame.image.load('assets/black knight.png')
black_knight = pygame.transform.scale(black_knight, (150, 150))
black_bishop = pygame.image.load('assets/black bishop.png')
black_bishop = pygame.transform.scale(black_bishop, (150, 150))
black_queen = pygame.image.load('assets/black queen.png')
black_queen = pygame.transform.scale(black_queen, (150, 150))
black_king = pygame.image.load('assets/black king.png')
black_king = pygame.transform.scale(black_king, (150, 150))

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
active_piece = None

# run the game
run = True
while run:

    # drawing the board
    screen.blit(board, (0, 0))

    # drawing the pieces
    for row in range(8):
        for column in range(8):

            # if the piece is being dragged then it's drawn at the cursor
            if active_piece == [column, row]:
                draw_position = [pygame.mouse.get_pos()[0] - 75, pygame.mouse.get_pos()[1] - 75]
            else:
                draw_position = [125 * column - 15, 125 * row - 15]

            # draws pieces according to the board state
            match game_state[row][column]:
                case "black pawn":
                    screen.blit(black_pawn, draw_position)
                case "white pawn":
                    screen.blit(white_pawn, draw_position)
                case "black rook":
                    screen.blit(black_rook, draw_position)
                case "black knight":
                    screen.blit(black_knight, draw_position)
                case "black bishop":
                    screen.blit(black_bishop, draw_position)
                case "white rook":
                    screen.blit(white_rook, draw_position)
                case "white knight":
                    screen.blit(white_knight, draw_position)
                case "white bishop":
                    screen.blit(white_bishop, draw_position)
                case "black queen":
                    screen.blit(black_queen, draw_position)
                case "black king":
                    screen.blit(black_king, draw_position)
                case "white queen":
                    screen.blit(white_queen, draw_position)
                case "white king":
                    screen.blit(white_king, draw_position)

    # check for player interactions
    for event in pygame.event.get():

        # player left clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            active_piece = [math.floor(event.pos[0] / 125), math.floor(event.pos[1] / 125)]

        # player releases the mouse
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if game_state[active_piece[1]][active_piece[0]] != "empty":
                new_column = math.floor(event.pos[0] / 125)
                new_row = math.floor(event.pos[1] / 125)

                # moves the dragged piece to the new square
                if active_piece != [new_column, new_row]:
                    game_state[new_row][new_column] = game_state[active_piece[1]][active_piece[0]]
                    game_state[active_piece[1]][active_piece[0]] = "empty"
                active_piece = None

        # stops the game if user closes the window
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
