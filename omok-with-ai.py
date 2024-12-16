# ------------------------ FILL HERE ----------------------------
## Using Negamax(4) 
from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax, SSS

class GameController(TwoPlayerGame):
    def __init__(self, players, board):
        self.players = players
        self.board = board
        self.current_player = 1 
        self.last_move = None  

    def possible_moves(self):
        moves = set()
        for i in range(15):
            for j in range(15):
                if self.board[i, j] > 0:
                    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < 15 and 0 <= nj < 15 and self.board[ni, nj] == 0:
                            moves.add((ni, nj))

        # Order moves based on the number of adjacent occupied cells
        def adjacent_count(cell):
            i, j = cell
            return sum(
                1 for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                if 0 <= i + dx < 15 and 0 <= j + dy < 15 and self.board[i + dx, j + dy] > 0
            )

        ordered_moves = sorted(list(moves), key=adjacent_count, reverse=True)
        return ordered_moves


    def make_move(self, action):
        x, y = action
        # Check if the move is in an empty space before making it
        if self.board[x, y] == 0:
            self.board[x, y] = self.current_player
            self.last_move = (x, y)
        print("last move: ",self.last_move)

    def unmake_move(self, action):
        self.board[action[0], action[1]] = 0
        self.last_move = None  

    def is_over(self):
         # Check if there's a winner using the last move or if the board is full
        return (self.last_move is not None and self.loss_condition()) or game_over(self.board)

    def loss_condition(self):
        if self.last_move is None:
            return False

        i, j = self.last_move
        directions = [
            (0, 1), (1, 0), (1, 1), (1, -1)  # Horizontal, vertical, diagonal
        ]

        for dx, dy in directions:
            count = 1
            for step in range(1, 5):
                ni, nj = i + step * dx, j + step * dy
                if 0 <= ni < 15 and 0 <= nj < 15 and self.board[ni, nj] == self.opponent_index:
                    count += 1
                else:
                    break
            for step in range(1, 5):
                ni, nj = i - step * dx, j - step * dy
                if 0 <= ni < 15 and 0 <= nj < 15 and self.board[ni, nj] == self.opponent_index:
                    count += 1
                else:
                    break
            if count >= 5:
                return True

        return False

    
    def scoring(self):
        return -100 if self.loss_condition() else 0  
    
# ---------------------------------------------------------------
import pygame, sys
pygame.init()

import random
import numpy as np

# global variables
WIDTH, HEIGHT = 750, 750
MESSAGE_MARGIN = 40
yellow = (255, 227, 56)
green = (0, 128, 0)
white = (255, 255, 255)
black = (0, 0, 0)
gray = (80, 80, 80)
boardcolor = pygame.Color("lightcyan3")
linecolor = pygame.Color("mistyrose4")
playercolor = [ None, black, white ]
font = pygame.font.SysFont("comicsans",24)

# create window
screen = pygame.display.set_mode((WIDTH, HEIGHT+MESSAGE_MARGIN))
pygame.display.set_caption("OMOK")

# player
# 1: black player 1 (or human player), who moves first
# 2: white player 2 (or AI)

# game state
state = np.zeros((15, 15), dtype=np.int16)
# the first move by player 1 on the center
#state[7, 7] = 1

# player turn (1 or 2)
current_player = 1

# selected cell
selected_cell = None

# create a surface object, image is drawn on it.
CELL_WIDTH, CELL_HEIGHT = WIDTH/15, HEIGHT/15
RADIUS = CELL_WIDTH * 0.5 - 1

def _message_margin(txt, backgr, textcol):
    rect = pygame.Rect( (0, HEIGHT), (WIDTH, MESSAGE_MARGIN) )
    pygame.draw.rect(screen, backgr, rect)
    pos_text = font.render(txt, True, textcol)
    pos_rect = pos_text.get_rect()
    pos_rect.center = ( WIDTH/2, HEIGHT + MESSAGE_MARGIN/2 )
    screen.blit(pos_text, pos_rect)

# show the message (turn, win, tie) on the bottom of screen
def show_msg():
    if is_gameover:
        if tie:
            txt = "Tie!"
        else:
            if winner == 1: # turn of yellow
                txt = "Black Wins!"
            else:
                txt = "White Wins!"

    else:
        if current_player == 1: # turn of yellow
            txt = "Black's Turn"
        else:
            txt = "White's Turn"
    _message_margin(txt, black, white)

def draw_board(surf, state):
    surf.fill(boardcolor)

    for i in range(15): # index of row
        # locate a line at i-th col
        x = CELL_WIDTH/2 + CELL_WIDTH * i
        pygame.draw.line(surf, linecolor, (x, CELL_HEIGHT/2), (x, HEIGHT-CELL_HEIGHT/2), width=2)

    for i in range(15): # index of row
        # locate a line at i-th row
        y = CELL_HEIGHT/2 + CELL_HEIGHT * i
        pygame.draw.line(surf, linecolor, (CELL_WIDTH/2, y), (WIDTH-CELL_WIDTH/2, y), width=2)

    for i in range(15): # index of row
        for j in range(15): # index of col
            if state[i, j] == 0:
                continue
            center = (j * CELL_WIDTH + CELL_WIDTH/2, i * CELL_HEIGHT + CELL_HEIGHT/2)
            pygame.draw.circle(surf, playercolor[state[i, j]], center, RADIUS, width=0)

def cell_coord(pos):
    # get row and col & return
    # note that y -> row number, x -> col number
    return (int(pos[1] / CELL_HEIGHT), int(pos[0] / CELL_WIDTH))

adjcells = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1)
]

# return all possible actions that player can takes
def possible_moves(player, state):
    ret = list()
    
    for i in range(15):
        for j in range(15):
            # the cell is a valid action if any adjacent cell is occupied
            if any([ True if state[i, j] == 0 and i + adj[0] >= 0 and i + adj[0] < 15  and j + adj[1] >=0 and j + adj[1] < 15 and state[i+adj[0], j+adj[1]] > 0 else False for adj in adjcells ]):
                ret.append((i, j))
    random.shuffle(ret)
    return ret

def make_move(player, state, action):
    state[action[0], action[1]] = player

# examine if the board is full
def game_over(state):
    return state.min() > 0

# return true if player wins by the last move
def win(player, state, last_move):
    x, y = last_move

    # horizontal: to right
    cnt = 1
    for i in range(1, 5):
        if y + i < 15 and state[x, y + i] == player:
            cnt += 1
        else:
            break
    # horizontal: to left
    for i in range(1, 5):
        if y - i >= 0 and state[x, y - i] == player:
            cnt += 1
        else:
            break

    if cnt >= 5:
        return True
    
    # vertical: to down
    cnt = 1
    for i in range(1, 5):
        if x + i < 15 and state[x + i, y] == player:
            cnt += 1
        else:
            break
    # horizontal: to up
    for i in range(1, 5):
        if x - i >= 0 and state[x - i, y] == player:
            cnt += 1
        else:
            break

    if cnt >= 5:
        return True

    # diagonal: to down right
    cnt = 1
    for i in range(1, 5):
        if y + i < 15 and x + i < 15 and state[x + i, y + i] == player:
            cnt += 1
        else:
            break
    # horizontal: to up left
    for i in range(1, 5):
        if y - i >= 0 and x - i >= 0 and state[x - i, y - i] == player:
            cnt += 1
        else:
            break

    if cnt >= 5:
        return True

    # diagonal: to up right
    cnt = 1
    for i in range(1, 5):
        if y + i < 15 and x - i >= 0 and state[x - i, y + i] == player:
            cnt += 1
        else:
            break
    # horizontal: to down left
    for i in range(1, 5):
        if y - i >= 0 and x + i < 15 and state[x + i, y - i] == player:
            cnt += 1
        else:
            break

    if cnt >= 5:
        return True
    
    return False

is_gameover = False
winner = 0
tie = False
running = True
first_turn = True

gc = GameController([Human_Player(), AI_Player(Negamax(4))], state)

while running:
    pygame.time.delay(200)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not is_gameover:
            # calculate the clicked piece
            idx = cell_coord(pygame.mouse.get_pos())
            #print(idx)
            #print(possible_moves(current_player, state))

            # clicked out of board such as message box
            if (idx[0] <  0 or idx[0] >= 15) or (idx[1] < 0 or idx[1] >= 15):
                break

            # idx is a move
            if first_turn or idx in possible_moves(current_player, state):
                first_turn = False
                # human player's move
                gc.play_move(idx)
                print("Human move:\n",state )
                print("\n")

                # examine if human player wins and game is over
                if win(current_player, state, idx):
                    is_gameover = True
                    winner = current_player
                    break
                # if no more empty cell
                elif game_over(state):
                    is_gameover = True
                    tie = True
                    break

                current_player = 3 - current_player
                draw_board(screen, state)
                show_msg()
                pygame.display.update()

                if gc.current_player == 2: # AI's turn (actually, don't need to check if)
                    ai_move = gc.get_move()
                    if state[ai_move] > 0:
                        print("error!")
                    print(ai_move)
                    gc.play_move(ai_move)
                    print(state)
                    
                    # examine if ai player wins and game is over
                    if win(current_player, state, ai_move):
                        is_gameover = True
                        winner = current_player
                        break
                    # if no more empty cell
                    elif game_over(state):
                        is_gameover = True
                        tie = True
                        break

                    current_player = 3 - current_player


    draw_board(screen, state)
    show_msg()
    pygame.display.update()


pygame.quit()
sys.exit()