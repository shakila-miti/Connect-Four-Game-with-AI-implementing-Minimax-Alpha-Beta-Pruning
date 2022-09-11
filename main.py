import numpy as np
import random
import pygame
import sys
import math

TEAL = (0,128,128)
BLACK = (0,0,0)
PURPLE = (128,0,128)
GOLDEN = (254,208,0)

RCOUNT = 6
CCOUNT = 7

P = 0
AI = 1

NULL = 0
P_PIECE = 1
AI_PIECE = 2

WL = 4

def init_board():
	board = np.zeros((RCOUNT,CCOUNT))
	return board

def drop(board, row, col, piece):
	board[row][col] = piece

def val_loc(board, col):
	return board[RCOUNT-1][col] == 0

def gnext_openRow(board, col):
	for r in range(RCOUNT):
		if board[r][col] == 0:
			return r

def p_board(board):
	print(np.flip(board, 0))

def win_mv(board, piece):
	#HORIZONTAL
	for c in range(CCOUNT-3):
		for r in range(RCOUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	#VERTICAL
	for c in range(CCOUNT):
		for r in range(RCOUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# DIAGONALS
	for c in range(CCOUNT-3):
		for r in range(RCOUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	for c in range(CCOUNT-3):
		for r in range(3, RCOUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def cal_window(window, piece):
	score = 0
	opp_piece = P_PIECE
	if piece == P_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 110
	elif window.count(piece) == 3 and window.count(NULL) == 1:
		score += 10
	elif window.count(piece) == 2 and window.count(NULL) == 2:
		score += 7

	if window.count(opp_piece) == 3 and window.count(NULL) == 1:
		score -= 9

	return score

def score(board, piece):
	score = 0

	#CENTER
	center_array = [int(i) for i in list(board[:, CCOUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	#HORIZONTAL
	for r in range(RCOUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(CCOUNT-3):
			window = row_array[c:c+WL]
			score += cal_window(window, piece)

	#VERTICAL
	for c in range(CCOUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(RCOUNT-3):
			window = col_array[r:r+WL]
			score += cal_window(window, piece)

	#DIAGONAL
	for r in range(RCOUNT-3):
		for c in range(CCOUNT-3):
			window = [board[r+i][c+i] for i in range(WL)]
			score += cal_window(window, piece)

	for r in range(RCOUNT-3):
		for c in range(CCOUNT-3):
			window = [board[r+3-i][c+i] for i in range(WL)]
			score += cal_window(window, piece)

	return score

def isNodeEnd(board):
	return win_mv(board, P_PIECE) or win_mv(board, AI_PIECE) or len(gValidLoc(board)) == 0

def minimax(board, depth, a, b, maximizingP):
	validLoc = gValidLoc(board)
	is_terminal = isNodeEnd(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if win_mv(board, AI_PIECE):
				return (None, 100000000000000)
			elif win_mv(board, P_PIECE):
				return (None, -10000000000000)
			else: 
				return (None, 0)
		else: 
			return (None, score(board, AI_PIECE))
	if maximizingP:
		value = -math.inf
		column = random.choice(validLoc)
		for col in validLoc:
			row = gnext_openRow(board, col)
			b_copy = board.copy()
			drop(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth-1, a, b, False)[1]
			if new_score > value:
				value = new_score
				column = col
			a = max(a, value)
			if a >= b:
				break
		return column, value

	else:
		value = math.inf
		column = random.choice(validLoc)
		for col in validLoc:
			row = gnext_openRow(board, col)
			b_copy = board.copy()
			drop(b_copy, row, col, P_PIECE)
			new_score = minimax(b_copy, depth-1, a, b, True)[1]
			if new_score < value:
				value = new_score
				column = col
			b = min(b, value)
			if a >= b:
				break
		return column, value

def gValidLoc(board):
	validLoc = []
	for col in range(CCOUNT):
		if val_loc(board, col):
			validLoc.append(col)
	return validLoc

def draw_board(board):
	for c in range(CCOUNT):
		for r in range(RCOUNT):
			pygame.draw.rect(screen, TEAL, (c*sqSize, r*sqSize+sqSize, sqSize, sqSize))
			pygame.draw.circle(screen, BLACK, (int(c*sqSize+sqSize/2), int(r*sqSize+sqSize+sqSize/2)), radius)
	
	for c in range(CCOUNT):
		for r in range(RCOUNT):		
			if board[r][c] == P_PIECE:
				pygame.draw.circle(screen, PURPLE, (int(c*sqSize+sqSize/2), height-int(r*sqSize+sqSize/2)), radius)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, GOLDEN, (int(c*sqSize+sqSize/2), height-int(r*sqSize+sqSize/2)), radius)
	pygame.display.update()

board = init_board()
p_board(board)
game_over = False

pygame.init()

sqSize = 100

width = CCOUNT * sqSize
height = (RCOUNT+1) * sqSize

size = (width, height)

radius = int(sqSize/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 74)

turn = random.randint(P, AI)

while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, BLACK, (0,0, width, sqSize))
			posx = event.pos[0]
			if turn == P:
				pygame.draw.circle(screen, PURPLE, (posx, int(sqSize/2)), radius)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, width, sqSize))
			if turn == P:
				posx = event.pos[0]
				col = int(math.floor(posx/sqSize))

				if val_loc(board, col):
					row = gnext_openRow(board, col)
					drop(board, row, col, P_PIECE)

					if win_mv(board, P_PIECE):
						label = myfont.render("Player-1 Won!!", 1, PURPLE)
						screen.blit(label, (40,10))
						game_over = True

					turn += 1
					turn = turn % 2

					p_board(board)
					draw_board(board)


	
	if turn == AI and not game_over:				
		col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

		if val_loc(board, col):
			row = gnext_openRow(board, col)
			drop(board, row, col, AI_PIECE)

			if win_mv(board, AI_PIECE):
				label = myfont.render("Player-2 Won!!", 1, GOLDEN)
				screen.blit(label, (40,10))
				game_over = True

			p_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2

	if game_over:
		pygame.time.wait(4000)
