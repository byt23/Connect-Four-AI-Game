import numpy as np
import random
import pygame
import sys
import math

# --- RENKLER ---
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)
GREEN = (0, 200, 0)

# --- OYUN AYARLARI ---
ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4
SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)

# --- TEMEL FONKSİYONLAR ---
def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Yatay
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Dikey
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Pozitif Diyagonal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Negatif Diyagonal
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False

# --- AI MANTIĞI (MINIMAX) ---
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0
    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score positive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    ## Score negative sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))
            
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

# --- GÖRSEL FONKSİYONLAR ---
def reset_game():
    new_board = create_board()
    screen.blit(game_bg_image , (0,0))
    draw_board(new_board)
    pygame.display.update()
    new_turn = random.randint(PLAYER, AI)
    return new_board, False, new_turn

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):      
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

# --- PYGAME BAŞLATMA ---
pygame.init()
pygame.mixer.init()

# Sesler
try:
    pygame.mixer.music.load("sounds/connect_4_music.mpeg.ogg")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    drop_sound = pygame.mixer.Sound("sounds/drop.wav")
except:
    print("Müzik veya ses dosyaları bulunamadı.")

# Fontlar
myfont = pygame.font.SysFont("monospace", 75)
button_font = pygame.font.SysFont("monospace", 30)
menu_font = pygame.font.SysFont("monospace", 60)
win_font = pygame.font.SysFont("monospace", 50)
top_button_font = pygame.font.SysFont("monospace", 22)

screen = pygame.display.set_mode(size, pygame.SCALED)
pygame.display.set_caption("Connect 4 AI")

# Görseller
try:
    bg_image = pygame.image.load("images/bg_image_jpg.jpeg").convert()
    bg_image = pygame.transform.scale(bg_image, (width,height))
    game_bg_image = pygame.image.load("images/bg_image_gameplay.jpeg").convert()
    game_bg_image = pygame.transform.scale(game_bg_image, (width,height))
except:
    bg_image = pygame.Surface(size)
    bg_image.fill((20, 20, 20))
    game_bg_image = pygame.Surface(size)

# Başlangıç Durumu
state = "MENU"
volume_level = 0.2
fullscreen = False
board, game_over, turn = reset_game()

# --- ANA DÖNGÜ ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.SCALED)
                else:
                    screen = pygame.display.set_mode(size , pygame.SCALED)
                if state == "PLAYING":
                    draw_board(board)

        # 1. MENU
        if state == "MENU":
            screen.blit(bg_image , (0,0))
            title = menu_font.render("CONNECT 4 AI", 1, BLUE)
            screen.blit(title, (width/2 - title.get_width()/2, 80))
            
            # PLAY
            pygame.draw.rect(screen, RED, (width/2 - 120, 220, 240, 60), border_radius=10)
            play_text = button_font.render("PLAY", 1, BLACK)
            screen.blit(play_text, (width/2 - play_text.get_width()/2, 235))
            
            # SETTINGS
            pygame.draw.rect(screen, YELLOW, (width/2 - 120, 310, 240, 60), border_radius=10)
            set_text = button_font.render("SETTINGS", 1, BLACK)
            screen.blit(set_text, (width/2 - set_text.get_width()/2, 325))

            # ABOUT (Yeni Buton)
            pygame.draw.rect(screen, GREEN, (width/2 - 120, 400, 240, 60), border_radius=10)
            about_btn_text = button_font.render("ABOUT", 1, BLACK)
            screen.blit(about_btn_text, (width/2 - about_btn_text.get_width()/2, 415))
            
            # QUIT
            pygame.draw.rect(screen, (100, 100, 100), (width/2 - 120, 490, 240, 60), border_radius=10)
            quit_text = button_font.render("QUIT", 1, BLACK)
            screen.blit(quit_text, (width/2 - quit_text.get_width()/2, 505))
            
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                posx, posy = event.pos
                if (width/2 - 120 <= posx <= width/2 + 120):
                    if (220 <= posy <= 280): 
                        board, game_over, turn = reset_game()
                        state = "PLAYING"
                    elif (310 <= posy <= 370): 
                        state = "SETTINGS"
                    elif (400 <= posy <= 460):
                        state = "ABOUT"
                    elif (490 <= posy <= 550): 
                        state = "QUIT_CONFIRM"

        # 2. SETTINGS
        elif state == "SETTINGS":
            screen.blit(bg_image , (0,0))
            title = menu_font.render("SETTINGS", 1, YELLOW)
            screen.blit(title, (width/2 - title.get_width()/2, 100))
            vol_text = button_font.render(f"Music Volume: {int(volume_level*100)}%", 1, RED)
            screen.blit(vol_text, (width/2 - vol_text.get_width()/2, 250))
            
            pygame.draw.rect(screen, BLUE, (width/2 - 100, 320, 60, 60), border_radius=10)
            screen.blit(menu_font.render("-", 1, BLACK), (width/2 - 80, 320))
            pygame.draw.rect(screen, BLUE, (width/2 + 40, 320, 60, 60), border_radius=10)
            screen.blit(menu_font.render("+", 1, BLACK), (width/2 + 55, 320))
            
            pygame.draw.rect(screen, RED, (width/2 - 100, 480, 200, 60), border_radius=10)
            back_text = button_font.render("BACK", 1, BLACK)
            screen.blit(back_text, (width/2 - back_text.get_width()/2, 495))
            
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                posx, posy = event.pos
                if (width/2 - 100 <= posx <= width/2 - 40) and (320 <= posy <= 380):
                    volume_level = max(0.0, volume_level - 0.1)
                    pygame.mixer.music.set_volume(volume_level)
                elif (width/2 + 40 <= posx <= width/2 + 100) and (320 <= posy <= 380):
                    volume_level = min(1.0, volume_level + 0.1)
                    pygame.mixer.music.set_volume(volume_level)
                elif (width/2 - 100 <= posx <= width/2 + 100) and (480 <= posy <= 540):
                    state = "MENU"

        # 3. ABOUT (Hakkında Ekranı)
        elif state == "ABOUT":
            screen.blit(bg_image, (0,0))
            title = menu_font.render("ABOUT GAME", 1, GREEN)
            screen.blit(title, (width/2 - title.get_width()/2, 50))
            
            about_lines = [
                "1. Connect 4 pieces in a row to win.",
                "2. Row can be vertical, horizontal or diagonal.",
                "3. AI uses Minimax with Alpha-Beta Pruning.",
                "4. Difficulty: AI evaluates 5 moves ahead.",
                "5. Developed with Python & Pygame."
            ]
            
            for i, line in enumerate(about_lines):
                info = top_button_font.render(line, 1, WHITE)
                screen.blit(info, (50, 180 + (i * 45)))

            pygame.draw.rect(screen, RED, (width/2 - 100, 500, 200, 60), border_radius=10)
            back_text = button_font.render("BACK", 1, BLACK)
            screen.blit(back_text, (width/2 - back_text.get_width()/2, 515))
            
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                posx, posy = event.pos
                if (width/2 - 100 <= posx <= width/2 + 100) and (500 <= posy <= 560):
                    state = "MENU"

        # 4. PLAYING
        elif state == "PLAYING":
            if game_over:
                pygame.draw.rect(screen, GREEN, (width - 130, 30, 110, 40), border_radius=10)
                screen.blit(top_button_font.render("REMATCH", 1, BLACK), (width - 120, 40))
                pygame.draw.rect(screen, RED, (20, 30, 120, 40), border_radius=10)
                screen.blit(top_button_font.render("MENU", 1, BLACK), (45, 40))
                
                pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    posx, posy = event.pos
                    if (width - 130 <= posx <= width - 20) and (30 <= posy <= 70):
                        board, game_over, turn = reset_game()
                    elif (20 <= posx <= 140) and (30 <= posy <= 70):
                        state = "MENU"
                continue

            if event.type == pygame.MOUSEMOTION:
                screen.blit(game_bg_image, (0,0), (0, 0, width, SQUARESIZE))
                if turn == PLAYER:
                    pygame.draw.circle(screen, RED, (event.pos[0], int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                screen.blit(game_bg_image, (0,0), (0, 0, width, SQUARESIZE))
                if turn == PLAYER:
                    col = int(math.floor(event.pos[0]/SQUARESIZE))
                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)
                        try: drop_sound.play()
                        except: pass

                        if winning_move(board, PLAYER_PIECE):
                            label = win_font.render("Player 1 wins!!", 1, RED)
                            screen.blit(label, (width/2 - label.get_width()/2, 30))
                            game_over = True

                        turn = (turn + 1) % 2
                        print_board(board)
                        draw_board(board)

        # 5. QUIT_CONFIRM
        elif state == "QUIT_CONFIRM":
            screen.blit(bg_image , (0,0))
            question = menu_font.render("QUIT THE GAME?", 1, YELLOW)
            screen.blit(question, (width/2 - question.get_width()/2, 200))
            
            pygame.draw.rect(screen, GREEN, (width/2 - 150, 350, 120, 60), border_radius=10)
            screen.blit(button_font.render("YES", 1, BLACK), (width/2 - 120, 365))
            pygame.draw.rect(screen, RED, (width/2 + 30, 350, 120, 60), border_radius=10)
            screen.blit(button_font.render("NO", 1, BLACK), (width/2 + 75, 365))
            
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                posx, posy = event.pos
                if (width/2 - 150 <= posx <= width/2 - 30) and (350 <= posy <= 410):
                    sys.exit()
                elif (width/2 + 30 <= posx <= width/2 + 150) and (350 <= posy <= 410):
                    state = "MENU"

    # AI Sırası
    if state == "PLAYING" and turn == AI and not game_over:                
        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            try: drop_sound.play()
            except: pass

            if winning_move(board, AI_PIECE):
                label = win_font.render("AI wins!!", 1, YELLOW)
                screen.blit(label, (width/2 - label.get_width()/2, 30))
                game_over = True

            print_board(board)
            draw_board(board)
            turn = (turn + 1) % 2