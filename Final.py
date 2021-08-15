'''
Author: Frank Zihong Wang: Create connect four game and make GUI for it
        Kiana Duo Xu: Design features and implement them
        Rivoc Puyang Xu: Design scoring function, global score and frame up structures for AB pruning algorithm
        Bryan Yiran Qiu: Do implementation of AB pruning

2021.8
'''

import numpy as np
import pygame
import sys
import math

# global variables
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

rows = 6
columns = 7

DISC_size = 126
length = columns * DISC_size
SQUARE_size = (length, length)
radius = 55

# create an empty board
def create_board(rows, columns):
    board = np.zeros((rows, columns))
    return board

# print the board
def print_board(board):
    print(np.flip(board, 0))

# print the board on pygame window
def pygame_board(board):
    for col in range(columns):
        for row in range(rows):
            pygame.draw.rect(screen, BLUE, (col * DISC_size, row * DISC_size + DISC_size, DISC_size, DISC_size))
            pygame.draw.circle(screen, GRAY, (int(col * DISC_size + DISC_size / 2), int(row * DISC_size + DISC_size + DISC_size / 2)), radius)

    for col in range(columns):
        for row in range(rows):
            if board[row][col] == 1:
                pygame.draw.circle(screen, RED, (
                    int(col * DISC_size + DISC_size / 2), length - int(row * DISC_size + DISC_size / 2)), radius)
            elif board[row][col] == -1:
                pygame.draw.circle(screen, YELLOW, (
                    int(col * DISC_size + DISC_size / 2), length - int(row * DISC_size + DISC_size / 2)), radius)
    pygame.display.update()


# check if we can drop a disc in col
def valid_column(board, col):
    print("r", rows - 1, "c", col)
    if board[rows - 1][col] != 0:
        return False
    return True



# drop a disc
def drop_disc(board, col, disc):
    for row in range(rows):
        if board[row][col] == 0:
            board[row][col] = disc
            break


# AI algorithm for playing
def AI_step(board):
    # 这部分加入feature和algorithm的设计，让AI选择下放的column
    for col in range(columns - 1):
        if valid_column(board, col):
            return col
    return columns - 1


# check if any player win
def check_win(board, disc):
    # vertical check
    for col in range(columns):
        for row in range(rows - 3):
            if board[row][col] == disc:
                if board[row + 1][col] == board[row + 2][col] == board[row + 3][col] == disc:
                    return True

    # horizontal check
    for col in range(columns - 3):
        for row in range(rows):
            if board[row][col] == disc:
                if board[row][col + 1] == board[row][col + 2] == board[row][col + 3] == disc:
                    return True

    # diagnol check
    for row in range(rows - 3):
        for col in range(columns - 3):
            if board[row][col] == disc:
                if board[row + 1][col + 1] == board[row + 2][col + 2] == board[row + 3][col + 3] == disc:
                    return True

    return False

# ----------------------------Scoring formula-----------------------------------
# l：The length of the chess string ；d1，d2：The degree of C liberty
def chessvalue(l, d1, d2):
    if l < 4 and d1 == d2 == 0: return 0
    value = 10 ** (l + 2)
    k1 = d1 * d2
    k2 = d1 + d2

    v1 = 0 if d1 == 0 else 10 ** (l + 1) / d1 ** 3
    v2 = 0 if d2 == 0 else 10 ** (l + 1) / d2 ** 3
    value += v1 + v2
    if k1 > 0:
        value += (10 ** (l + 1) / k1 ** 1.5)
    if k2 > 0:
        value += (10 ** (l) / k2)
    # value *= 100
    return int(value)

# ----------------------------Global Score-----------------------------------
def cur_score(board):
    cslist = [[], []]  # List of player cslist[0]，List of AI cslist[1]
    direc = [[0, 1], [1, 1], [1, 0], [1, -1]]  # right, bottom right, below and bottom left for every point

    bd = board
    for x in range(0, 6):  # every col
        for y in range(0, 7):  # every row
            po = bd[x][y]  # cur status, 0: no chess, 1: player chess, -1: AI chess
            if po != 0:  # not no chess position
                for d in direc:  # right, bottom right, below and bottom left
                    fx, fy = x - d[0], y - d[1]  # compute possible former chess
                    if 0 <= fx < 6 and 0 <= fy < 7:  # judge if in board
                        if bd[fx][fy] == po:  # if exist former chess, end loop(confirm no repeat)
                            continue
                    step = 0
                    chess = []
                    chess.append((x, y))  # as the first point of the string
                    xn, yn = x, y
                    # ----- compute d1-----
                    d1 = 0
                    fx, fy = x - d[0], y - d[1]
                    if 0 <= fx < 6 and 0 <= fy < 7:
                        if bd[fx][fy] == 0:
                            k = [a[fy] for a in bd][::-1][:len(bd) - fx]
                            d1 = len(list(filter(lambda x: x == 0, k)))

                    # -----------------------

                    for s in range(3):  # At most 3(len=4 means winner)
                        xn, yn = xn + d[0], yn + d[1]  # compute the next position
                        if 0 <= xn < 6 and 0 <= yn < 7:  # judge if in board
                            if bd[xn][yn] == po:
                                chess.append((xn, yn))
                                step += 1
                            else:
                                break
                        else:
                            break
                    # ----- compute d2--------
                    d2 = 0
                    # xn,yn = xn+d[0],yn+d[1]
                    if 0 <= xn < 6 and 0 <= yn < 7:
                        if bd[xn][yn] == 0:
                            k = [a[yn] for a in bd][::-1][:len(bd) - xn]
                            d2 = len(list(filter(lambda x: x == 0, k)))
                    # -----------------------

                    # record the string
                    '''if step == 0:  # len=1, maybe repeat
                        for v in cslist[0]:
                            if chess == v[0]:  # if repeat, end loop, do not record
                                break'''
                    # player chess string
                    if po == 1:
                        value = chessvalue(len(chess), d1, d2)
                        cslist[0].append([chess, [len(chess), d1, d2], value])

                    # AI chess string
                    if po == -1:
                        value = chessvalue(len(chess), d1, d2)
                        cslist[1].append([chess, [len(chess), d1, d2], value])

    # compute global score for cur board
    # because in the position of AI, player score should have negative influence on the global score
    plsum = 0
    for pl in cslist[0]:
        plsum += pl[2]
    aisum = 0
    for ai in cslist[1]:
        aisum += pl[2]
    totalscore =  aisum - plsum
    print(cslist)
    return totalscore



# -----------------------------Alpha Beta Pruning--------------------------------
import math
import copy


# move board
def moveAndCopy(board, col, player):
    b = copy.deepcopy(board)
    b[col][b[col].tolist().index(0)] = (1 if player else -1)
    return b


# whether or not next move available
def moveAble(board):
    for i in range(0, 7):
        if board[i][5] == 0:
            return True
    return False


def flip90_right(arr):
    new_arr = arr[::-1]
    new_arr = np.transpose(new_arr)
    return new_arr
def flip90_left(arr):
    new_arr = np.transpose(arr)
    new_arr = new_arr[::-1]
    return new_arr
# board: chessboard, depth: search depth in tree, a: alpha, b: beta, initial: need return the col which AI choose?
def abp(board, depth=3, player=False, a=-math.inf, b=math.inf, initial=True):
    # end condition(deep enough or cannot move)
    # -1 repersent the AI, 1 repersent player
    if depth == 0 or not moveAble(board):
        return cur_score(flip90_left(board))
    s = 0  # temp score
    choose = 0  # choose col
    if not player:
        s = -math.inf # initial score (badest situation)
        for num in [n for n in list(range(0, 7)) if board[n][5] == 0]: # recursive each tree node
            # on this node, the best choose score
            s = max(s, abp(moveAndCopy(board, num, player), depth - 1, not player, a, b, False))
            if s >= b:
                # if alpha >= beta, give up
                break
            # if better
            if a < s:
                a = s
                if initial:
                    # the better score choose
                    choose = num
    else:
        s = math.inf # initial score, (badest situation for AI)
        for num in [n for n in list(range(0, 7)) if board[n][5] == 0]: # recursive each tree node
            # on this node, the best choose score(more harmful for AI)
            s = min(s, abp(moveAndCopy(board, num, player), depth - 1, not player, a, b, False))
            if a >= s:
                # if alpha >= beta, give up
                break
            # get lowest point
            b = min(s, b)
    if initial:
        # return choose for player
        return choose
    return s

# at the beginning of the game
board = create_board(rows, columns)
print_board(board)

# start the game
have_winner = False
turn = 1
rounds = 0

pygame.init()
screen = pygame.display.set_mode(SQUARE_size)
pygame_board(board)
pygame.display.update()
myfont = pygame.font.SysFont("monospace", 75)

while not have_winner:

    if turn == 1:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, length, DISC_size))
                posx = event.pos[0]
                pygame.draw.circle(screen, RED, (posx, int(DISC_size / 2)), radius)

            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, length, DISC_size))
                posx = event.pos[0]
                col = int(math.floor(posx / DISC_size))

                if not valid_column(board, col):
                    rounds += 0
                    turn += 0
                else:
                    drop_disc(board, col, turn)
                    pygame_board(board)
                    rounds += 1

                    if check_win(board, turn):
                        print("\nWe got a winner")
                        label = myfont.render("You beat the AI!!!", 1, RED)
                        screen.blit(label, (40, 10))
                        have_winner = True

                    print("\nBoard after round", rounds, end='\n')
                    print_board(board)
                    pygame_board(board)
                    turn = 0 - turn
    else:
        boardt = np.flip(flip90_right(board))[::-1]
        col = abp(boardt, initial = True)
        print("c2", col)
        # if we don't drop a disc, let the player put again
        if not valid_column(board, col):
            label = myfont.render("AI made a mistake!", 1, RED)
            screen.blit(label, (40, 10))
            pygame.time.wait(3000)
            rounds += 0
            turn += 0

        # else switch player
        else:
            drop_disc(board, col, turn)
            pygame_board(board)
            rounds += 1

            if check_win(board, turn):
                print("\nWe got a winner")
                label = myfont.render("You lose to AI", 1, YELLOW)
                screen.blit(label, (120, 10))
                have_winner = True

            print("\nBoard after round", rounds, end='\n')
            print_board(board)
            pygame_board(board)
            turn = 0 - turn

        if rounds == 42:
            print("\nDraw, no winner")
            break

    if have_winner:
        pygame.time.wait(3000)
# one round ends