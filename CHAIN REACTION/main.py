import pygame, sys
from pygame import transform
from pygame.locals import *
import os
from time import sleep
from database import *

#Clear the terminal or console
os.system("cls")

#Set the maximum recursion depth
sys.setrecursionlimit(3000)

#Create colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
SKYBLUE = (0, 250, 230)
PINK = (245, 0, 245)
ORANGE = (255, 126, 0)
GREY = (210, 210, 210)
BROWN = (100, 0, 0)
WHITE = (255, 255, 255)

#Create a class for the players
class Player:
    def __init__(self, num):
        #No which identifies the individual player
        self.NUMBER = num

        #No of cells occupied by the player
        self.score = 0

        #Color representation of the player
        self.color = None

        #To check if the player has been eliminated
        self.is_dead = False

        self.assign_color()
    
    # To assign the colors to each player
    def assign_color(self):
        if self.NUMBER == 0:
            self.color = RED
        elif self.NUMBER == 1:
            self.color = GREEN
        elif self.NUMBER == 2:
            self.color = BLUE
        elif self.NUMBER == 3:
            self.color = YELLOW
        elif self.NUMBER == 4:
            self.color = SKYBLUE
        elif self.NUMBER == 5:
            self.color = PINK
        elif self.NUMBER == 6:
            self.color = ORANGE
        elif self.NUMBER == 7:
            self.color = GREY
        elif self.NUMBER == 8:
            self.color = BROWN


#Create a class to handle the individual cells in the game
class Cell:
    def __init__(self):
        #No of balls that a cell holds
        self.current_hold = 0 

        #Maximum no of balls a cell can hold
        self.max_hold = 0

        #The player who holds the cell
        self.holder = None

        #The pygame rect that represents the cell on the display surface 
        self.rect = None

        #To check if the cell has undergone explosion
        self.is_exploding = False
    
    def is_explode(self):
        #Condition for the explosion of a cell
        return True if self.current_hold > self.max_hold else False
    
    def append(self, current_player):
        #Increment the hold of the cell and update the holder of the cell
        self.current_hold += 1
        self.holder = current_player


#Create a class for the main layout
class Grid:
    def __init__(self, no_of_rows, no_of_cols, no_of_frames, window_width, window_height):
        #Set window height and width
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = window_width, window_height

        #Percent of the window occupied by the grid
        self.percent = 84/100

        self.setup()

        self.no_of_rows = no_of_rows
        self.no_of_cols = no_of_cols

        self.no_of_frames = no_of_frames
    
        #The player to make a move
        self.current_player = 0

        #List of player instances
        self.players = list(Player(i) for i in range(self.no_of_players))

        #List to store the players who have not been eliminated
        self.not_dead_players = list(i for i in range(self.no_of_players))

        #To check if any of the cells are in the process of explosion
        self.explosion = False

        #Variable to store which cycle in the game is going on
        self.cycle_no = 1

        #To design the game framework depending upon no of players
        self.set_layout()

        #To initialize the cells in the grid
        self.cells_init()

        #To initialize the variables related to the coordinates of the lines
        self.lines_init()

        #To initialize the pygame rectangles
        self.rects_init()

        #Start the game
        self.game()

    # To adapt the size to different window sizes
    def transform(self, value, size):
        if size == self.WINDOW_WIDTH:
            new_value = value/400 * size
        elif size == self.WINDOW_HEIGHT:
             new_value = value/500 * size
        return int(new_value)
    
    def set_layout(self):
        #Initialize variables
        
        self.col_width = int(self.WINDOW_WIDTH * self.percent / self.no_of_cols)
        self.row_height = int(self.WINDOW_HEIGHT * self.percent / self.no_of_rows)
        self.circle_radius = min(self.col_width, self.row_height)//6
        
    def cells_init(self):
        #Create a list of cell objects
        self.cells = list(list(Cell() for i in range(self.no_of_cols)) for i in range(self.no_of_rows))
        

        #Assign the maximum capacity of each cell
        for i in range(self.no_of_rows):
            for j in range(self.no_of_cols):
                if ((i==0 or i==self.no_of_rows-1) and (j==0 or j==self.no_of_cols-1)):
                    self.cells[i][j].max_hold = 1
                elif i==0 or i==self.no_of_rows-1 or j==0 or j==self.no_of_cols-1:
                    self.cells[i][j].max_hold = 2
                else:
                    self.cells[i][j].max_hold = 3
                

    def lines_init(self):
        #Create lists for storing the coordinates of the lines which seperate each cell
        self.line_x = list()
        self.line_y = list()
        
        if self.no_of_cols % 2 == 0:
            self.line_x.append(int(self.WINDOW_WIDTH/2 - (self.no_of_cols/2) * self.col_width))
        else:
            self.line_x.append(int(self.WINDOW_WIDTH/2 - (self.no_of_cols//2 + 0.5) * self.col_width))
        
        if self.no_of_rows % 2 == 0:
            self.line_y.append(int(self.WINDOW_HEIGHT/2 - (self.no_of_rows/2) * self.row_height))
        else:
            self.line_y.append(int(self.WINDOW_HEIGHT/2 - (self.no_of_rows//2 + 0.5) * self.row_height))
        
        self.line_x.extend((self.line_x[0] + (i+1)*self.col_width) for i in range(self.no_of_cols))
        self.line_y.extend((self.line_y[0] + (i+1)*self.row_height) for i in range(self.no_of_rows))
        

    def rects_init(self):
        #Create the rect objects for the cells
        for i in range(self.no_of_rows):
            for j in range(self.no_of_cols):
                self.cells[i][j].rect = pygame.Rect(self.line_x[j], self.line_y[i], self.col_width, self.row_height)
                
                

    def draw_lines(self):
        #Vertical lines
        for i in range(len(self.line_x)):
            pygame.draw.line(self.DISPLAY_SURF, self.players[self.current_player].color, (self.line_x[i], self.line_y[0]), (self.line_x[i], self.line_y[-1]))
        
        #Horizontal lines
        for i in range(len(self.line_y)):
            pygame.draw.line(self.DISPLAY_SURF, self.players[self.current_player].color, (self.line_x[0], self.line_y[i]), (self.line_x[-1], self.line_y[i]))
            #pygame.draw.line(self.DISPLAY_SURF, self.players[self.current_player].color, (self.line_x[0]-3, self.line_y[i]-9), (self.line_x[-1]-3, self.line_y[i]-9))

    def which_cell(self, coord):
        #To determine which cell has been selected from the coordinates of the click
        cell_x = (coord[0] - (1-self.percent)/2 * self.WINDOW_WIDTH)//self.col_width
        cell_y = (coord[1] - (1-self.percent)/2 * self.WINDOW_HEIGHT)//self.row_height
        return (int(cell_x), int(cell_y))
    
    def display1(self, a):
        self.display()
        for i in range(self.no_of_rows):
            for j in range(self.no_of_cols):
                if self.cells[i][j].is_exploding:
                    if i > 0:
                        pygame.draw.circle(self.DISPLAY_SURF, self.players[self.current_player].color, (self.cells[i][j].rect.center[0], self.cells[i][j].rect.center[1] - a/self.no_of_frames * self.row_height), self.circle_radius)
                        
                    if i < self.no_of_rows-1:
                        pygame.draw.circle(self.DISPLAY_SURF, self.players[self.current_player].color, (self.cells[i][j].rect.center[0], self.cells[i][j].rect.center[1] + a/self.no_of_frames * self.row_height), self.circle_radius)
                        
                    if j > 0:
                        pygame.draw.circle(self.DISPLAY_SURF, self.players[self.current_player].color, (self.cells[i][j].rect.center[0] - a/self.no_of_frames * self.col_width, self.cells[i][j].rect.center[1]), self.circle_radius)
                        
                    if j < self.no_of_cols-1:
                        pygame.draw.circle(self.DISPLAY_SURF, self.players[self.current_player].color, (self.cells[i][j].rect.center[0] + a/self.no_of_frames * self.col_width, self.cells[i][j].rect.center[1]), self.circle_radius)
        pygame.display.update()
        sleep(0.0013)        

    def explode(self, explode_list):
        
        #The list to store the cells of possible future explosion
        next_explode_list = list()

        self.explosion = False

        for y, x in explode_list:

            #Check if the cell explodes
            
            if self.cells[y][x].is_explode():
                #Decrement the cell hold count and alter its holder 
                self.cells[y][x].current_hold -= self.cells[y][x].max_hold+1
                self.cells[y][x].is_exploding = True
                self.explosion = True
                
        if self.explosion:
            self.EXPLODE_SOUND.play()
            
            for i in range(1, self.no_of_frames+1):
                self.display1(i)
                #sleep(0.01)
                    
        for y, x in explode_list:
            
            if self.cells[y][x].is_exploding:
               
                if self.cells[y][x].current_hold == 0:
                    
                    self.players[self.current_player].score -= 1
                    
                    self.cells[y][x].holder = None
                #Impact the surrounding cells
                if x > 0:

                    #Change the scores of the players
                    if self.cells[y][x-1].holder != self.current_player:
                        
                        self.players[self.current_player].score += 1
                        
                        if self.cells[y][x-1].holder != None:
                            
                            self.players[self.cells[y][x-1].holder].score -= 1
                            
                    
                    #Increment the count of the surrounding cells, alter their holder and add the impacted cells to the next explode list
                    self.cells[y][x-1].append(self.current_player)
                    
                    next_explode_list.append((y, x-1))

                if x < self.no_of_cols-1:

                    #Change the scores of the players
                    if self.cells[y][x+1].holder != self.current_player:
                        self.players[self.current_player].score += 1
                        if self.cells[y][x+1].holder != None:
                            self.players[self.cells[y][x+1].holder].score -= 1

                    #Increment the count of the surrounding cells, alter their holder and add the impacted cells to the next explode list
                    self.cells[y][x+1].append(self.current_player)
                    next_explode_list.append((y, x+1))

                if y > 0:

                    #Change the scores of the players
                    if self.cells[y-1][x].holder != self.current_player:
                        self.players[self.current_player].score += 1
                        if self.cells[y-1][x].holder != None:
                            self.players[self.cells[y-1][x].holder].score -= 1
                    
                    #Increment the count of the surrounding cells, alter their holder and add the impacted cells to the next explode list
                    self.cells[y-1][x].append(self.current_player)
                    next_explode_list.append((y-1, x))

                if y < self.no_of_rows-1:

                    #Change the scores of the players
                    if self.cells[y+1][x].holder != self.current_player:
                        self.players[self.current_player].score += 1
                        if self.cells[y+1][x].holder != None:
                            self.players[self.cells[y+1][x].holder].score -= 1

                    #Increment the count of the surrounding cells, alter their holder and add the impacted cells to the next explode list
                    self.cells[y+1][x].append(self.current_player)
                    next_explode_list.append((y+1, x))
                
                self.cells[y][x].is_exploding = False
        
        #Kill the players with 0 score
        for i in self.not_dead_players:
            if self.players[i].score == 0 and self.cycle_no > 1:
                self.players[i].is_dead = True
                self.not_dead_players.remove(i)
        #Condition for winning
        if len(self.not_dead_players) == 1:
            print("player", self.not_dead_players[0], "wins")
            self.display()
            pygame.display.update()
            sleep(1)
            self.winner_display(self.not_dead_players[0])
            grid = Grid(*grid_allotment)

        #Recursion to continue the explosion
        if len(next_explode_list) > 0:

            self.explode(next_explode_list)
        else:
            return

    # Function to display the winner when the game ends         
    def winner_display(self, winner):
        winner_text = self.HEADING_FONT.render("Player {} WINS!!!".format(winner+1), True, self.players[winner].color)
        winner_text_rect = winner_text.get_rect()
        winner_text_rect.center = self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//2 - self.transform(25, self.WINDOW_HEIGHT)

        continue_text = self.SMALL_SIZE_FONT.render("Press any key to continue...", True, self.players[winner].color)
        continue_text_rect = continue_text.get_rect()
        continue_text_rect.center = self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//1.2
        i = 0
        while True:
        
            self.DISPLAY_SURF.fill(BLACK)
            self.DISPLAY_SURF.blit(winner_text, winner_text_rect)
            if (i//no_of_frames) % 2 == 1: 
                self.DISPLAY_SURF.blit(continue_text, continue_text_rect)
            pygame.draw.rect(self.DISPLAY_SURF, self.players[winner].color, (winner_text_rect.left - self.transform(10, self.WINDOW_WIDTH), winner_text_rect.top - self.transform(2, self.WINDOW_HEIGHT), winner_text_rect.width + self.transform(20, self.WINDOW_WIDTH), winner_text_rect.height + self.transform(8, self.WINDOW_HEIGHT)), self.transform(3, self.WINDOW_WIDTH), self.transform(10, self.WINDOW_WIDTH) )
            pygame.draw.rect(self.DISPLAY_SURF, self.players[winner].color, (winner_text_rect.left - self.transform(14, self.WINDOW_WIDTH), winner_text_rect.top - self.transform(6, self.WINDOW_HEIGHT), winner_text_rect.width + self.transform(28, self.WINDOW_WIDTH), winner_text_rect.height + self.transform(16, self.WINDOW_HEIGHT)), self.transform(3, self.WINDOW_WIDTH), self.transform(12, self.WINDOW_WIDTH) )
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN or event.type == FINGERDOWN or event.type == KEYDOWN:
                    return
                
                elif event.type == VIDEORESIZE:
                    self.WINDOW_WIDTH, self.WINDOW_HEIGHT = event.w, event.h
                    
            i += 1


    def display(self):
        self.DISPLAY_SURF.fill(BLACK)
        #To draw the lines
        self.draw_lines()

        #To draw the balls
        for i in range(self.no_of_rows):
            for j in range(self.no_of_cols):
                if self.cells[i][j].current_hold == 1:
                    pygame.draw.circle(self.DISPLAY_SURF, self.players[self.cells[i][j].holder].color, (self.cells[i][j].rect.center), self.circle_radius)
                elif self.cells[i][j].current_hold == 2:
                    pygame.draw.circle(self.DISPLAY_SURF, self.players[self.cells[i][j].holder].color, (self.cells[i][j].rect.center[0] - self.circle_radius, self.cells[i][j].rect.center[1]), self.circle_radius)
                    pygame.draw.circle(self.DISPLAY_SURF, self.players[self.cells[i][j].holder].color, (self.cells[i][j].rect.center[0] + self.circle_radius, self.cells[i][j].rect.center[1]), self.circle_radius)
                elif self.cells[i][j].current_hold >= 3:
                    pygame.draw.circle(self.DISPLAY_SURF, self.players[self.cells[i][j].holder].color, (self.cells[i][j].rect.center[0] - self.circle_radius, self.cells[i][j].rect.center[1] - self.circle_radius/1.19), self.circle_radius)
                    pygame.draw.circle(self.DISPLAY_SURF, self.players[self.cells[i][j].holder].color, (self.cells[i][j].rect.center[0] + self.circle_radius, self.cells[i][j].rect.center[1] - self.circle_radius/1.19), self.circle_radius)
                    pygame.draw.circle(self.DISPLAY_SURF, self.players[self.cells[i][j].holder].color, (self.cells[i][j].rect.center[0], self.cells[i][j].rect.center[1] + self.circle_radius/1.19), self.circle_radius)
        
    def logic(self, coord, event_player):
        if event_player != self.current_player:
            return
        #Get the cell which is clicked from the coordinates of the click
        cell_x, cell_y = self.which_cell(coord)
        
        #To check if the chosen cell is in fact a cell and to verify the holder of the cell
        if cell_x >= 0 and cell_x <self.no_of_cols and cell_y >= 0 and cell_y < self.no_of_rows and (self.cells[cell_y][cell_x].holder == self.current_player or self.cells[cell_y][cell_x].holder == None):
            #Increment the hold of the cell
            if self.cells[cell_y][cell_x].holder == None:
                self.players[self.current_player].score += 1
            
            self.cells[cell_y][cell_x].append(self.current_player)
            

            #Condition for the explosion
            if self.cells[cell_y][cell_x].is_explode():
                self.explode([(cell_y, cell_x)])

            #Change the current player
            (self.current_player, self.cycle_no) = (self.current_player+1, self.cycle_no) if self.current_player < self.no_of_players-1 else (0, self.cycle_no+1)
           
    def main_menu_display_setup(self, textbox_fill):
        
        self.DISPLAY_SURF.blit(self.MAIN_MENU_IMAGE, self.MAIN_MENU_IMAGE_rect)
        self.DISPLAY_SURF.blit(self.HEADING_text, self.HEADING_text_rect)
        self.DISPLAY_SURF.blit(self.NO_OF_PLAYERS_text, self.NO_OF_PLAYERS_text_rect)
        if textbox_fill:
            pygame.draw.rect(self.DISPLAY_SURF, BLACK, self.NO_OF_PLAYERS_textbox_rect, 0)
        self.DISPLAY_SURF.blit(self.START_text, self.START_text_rect)
        self.DISPLAY_SURF.blit(self.NO_OF_PLAYERS_pygame_text, (self.NO_OF_PLAYERS_textbox_rect.centerx - self.options_font_size//2, self.NO_OF_PLAYERS_textbox_rect.centery - self.options_font_size//1.1, self.options_font_size, self.options_font_size))
        pygame.draw.line(self.DISPLAY_SURF, YELLOW, (self.HEADING_text_rect.left, self.HEADING_text_rect.bottom + self.transform(3, self.WINDOW_HEIGHT)), (self.HEADING_text_rect.right, self.HEADING_text_rect.bottom + self.transform(3, self.WINDOW_HEIGHT)), self.transform(2, self.WINDOW_HEIGHT))
        pygame.draw.line(self.DISPLAY_SURF, YELLOW, (self.HEADING_text_rect.left, self.HEADING_text_rect.bottom + self.transform(7, self.WINDOW_HEIGHT)), (self.HEADING_text_rect.right, self.HEADING_text_rect.bottom + self.transform(7, self.WINDOW_HEIGHT)), self.transform(2, self.WINDOW_HEIGHT))
        
        pygame.draw.rect(self.DISPLAY_SURF, YELLOW, (self.START_text_rect.left - self.transform(5, self.WINDOW_WIDTH), self.START_text_rect.top - self.transform(0, self.WINDOW_HEIGHT), self.START_text_rect.width + self.transform(10, self.WINDOW_WIDTH), self.START_text_rect.height + self.transform(2, self.WINDOW_HEIGHT)), self.transform(2, self.WINDOW_HEIGHT), self.transform(5, self.WINDOW_WIDTH))
        pygame.draw.rect(self.DISPLAY_SURF, YELLOW, (self.START_text_rect.left - self.transform(9, self.WINDOW_WIDTH), self.START_text_rect.top - self.transform(4, self.WINDOW_HEIGHT), self.START_text_rect.width + self.transform(18, self.WINDOW_WIDTH), self.START_text_rect.height + self.transform(10, self.WINDOW_HEIGHT)), self.transform(2, self.WINDOW_HEIGHT), self.transform(8, self.WINDOW_WIDTH))
        pygame.draw.rect(self.DISPLAY_SURF, YELLOW, self.NO_OF_PLAYERS_textbox_rect, self.transform(2, self.WINDOW_HEIGHT), self.transform(6, self.WINDOW_WIDTH))
        pygame.draw.rect(self.DISPLAY_SURF, YELLOW, (self.NO_OF_PLAYERS_textbox_rect.left + self.transform(4, self.WINDOW_WIDTH), self.NO_OF_PLAYERS_textbox_rect.top + self.transform(4, self.WINDOW_HEIGHT), self.NO_OF_PLAYERS_textbox_rect.width - self.transform(8, self.WINDOW_WIDTH), self.NO_OF_PLAYERS_textbox_rect.height - self.transform(8, self.WINDOW_HEIGHT)), self.transform(2, self.WINDOW_WIDTH), self.transform(5, self.WINDOW_WIDTH))
        pygame.display.update()
          
    def setup(self):
        #Initialize pygame
        pygame.init()
        pygame.display.set_caption("Chain Reaction")

        #Create the display window
        self.DISPLAY_SURF = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)

        self.textbox_active = False
        
        #Load all the sounds
        self.EXPLODE_SOUND = pygame.mixer.Sound("sounds/Burst.mp3")

        #Load all the images
        self.neon_tunnel_image = pygame.image.load("images/main_menu_img.jpg")

        
        #Main menu bg image
        self.MAIN_MENU_IMAGE = pygame.transform.scale(self.neon_tunnel_image, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.MAIN_MENU_IMAGE_rect = self.MAIN_MENU_IMAGE.get_rect()
        self.MAIN_MENU_IMAGE_rect.center = self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//2

        #Heading font size
        self.heading_font_size = self.WINDOW_WIDTH//10
        self.options_font_size = self.WINDOW_WIDTH//12
        self.small_font_size = self.WINDOW_WIDTH//20

        #Create all the fonts and store in a list
        self.HEADING_FONT = pygame.font.Font("fonts/sportrop/Sportrop.ttf", self.heading_font_size)
        self.OPTIONS_FONT = pygame.font.Font("fonts/sportrop/Sportrop.ttf", self.options_font_size)
        self.SMALL_SIZE_FONT = pygame.font.Font("fonts/sportrop/Sportrop.ttf", self.small_font_size)
  
        #Create heading text
        self.HEADING_text = self.HEADING_FONT.render("CHAIN REACTION", True, YELLOW)
        self.HEADING_text_rect = self.HEADING_text.get_rect()
        self.HEADING_text_rect.center = self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//12

        #Create the number of players choice option
        self.NO_OF_PLAYERS_text = self.OPTIONS_FONT.render("No of Players:", True, YELLOW)
        self.NO_OF_PLAYERS_text_rect = self.NO_OF_PLAYERS_text.get_rect()
        self.NO_OF_PLAYERS_text_rect.center = self.WINDOW_WIDTH//2.8, self.WINDOW_HEIGHT//3.5

        self.NO_OF_PLAYERS_textbox_rect = pygame.rect.Rect(self.NO_OF_PLAYERS_text_rect.right + self.transform(10, self.WINDOW_WIDTH), self.NO_OF_PLAYERS_text_rect.top, self.WINDOW_WIDTH//4.5, self.NO_OF_PLAYERS_text_rect.height)
        global no_of_players
        self.NO_OF_PLAYERS_textbox_text = str(no_of_players)
        self.NO_OF_PLAYERS_pygame_text = self.OPTIONS_FONT.render(self.NO_OF_PLAYERS_textbox_text, True, YELLOW)

        #Create no of players text input
        self.NO_OF_FRAMES_text = self.OPTIONS_FONT.render("No of Frames:", True, YELLOW)
        self.NO_OF_FRAMES_text_rect = self.NO_OF_FRAMES_text.get_rect()
        self.NO_OF_FRAMES_text_rect.center = self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//2

        self.NO_OF_FRAMES_textbox_rect = pygame.rect.Rect(self.NO_OF_FRAMES_text_rect.right + self.transform(10, self.WINDOW_WIDTH), self.NO_OF_FRAMES_text_rect.top, self.WINDOW_WIDTH//4.5, self.NO_OF_FRAMES_text_rect.height)
        global no_of_frames
        self.NO_OF_FRAMES_textbox_text = str(no_of_frames)
        self.NO_OF_FRAMES_pygame_text = self.OPTIONS_FONT.render(self.NO_OF_PLAYERS_textbox_text, True, YELLOW)

        #Create start game button
        self.START_text = self.HEADING_FONT.render("Start Game", True, YELLOW)
        self.START_text_rect = self.START_text.get_rect()
        self.START_text_rect.center = self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//1.5
        

        #To blit the elements of the main menu
        self.main_menu_display_setup(False)

        #Main menu display loop
        while True:
            for event in pygame.event.get():
                #Quit event
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == MOUSEBUTTONDOWN or event.type == FINGERDOWN:
                    #Game start
                    if self.START_text_rect.collidepoint(event.pos):
                        self.no_of_players = int(self.NO_OF_PLAYERS_textbox_text)
                        return
                    
                    #No of players textbox
                    elif self.NO_OF_PLAYERS_textbox_rect.collidepoint(event.pos):
                        self.no_of_players = self.text_input(self.NO_OF_PLAYERS_textbox_rect, "int")
                        
                        #Change the global no_of_players variable imported from database
                        no_of_players = self.no_of_players
                        readfile = open("database.py", 'r')
                        lines = readfile.readlines()
                        for i in range(len(lines)):
                            if "no_of_players" in lines[i]:
                                lines[i] = f"no_of_players = {self.no_of_players}\n"
                            
                        readfile.close()
                        
                        with open("database.py", 'w') as writefile:
                            writefile.writelines(lines)
                elif event.type == VIDEORESIZE:

                    self.WINDOW_WIDTH, self.WINDOW_HEIGHT = event.w, event.h
                    self.setup()

    def text_input(self, rect, data_type):
        #Variable to check if textbox is active
        self.textbox_active = True
        i = 0
        #Textbox input loop
        while True:
            for event in pygame.event.get():
                #Quit event
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == VIDEORESIZE:
                    self.WINDOW_WIDTH, self.WINDOW_HEIGHT = event.w, event.h
                    self.setup()

                elif event.type == MOUSEBUTTONDOWN or event.type == FINGERDOWN:
                    #Exiting the textbox
                    if not rect.collidepoint(event.pos):
                        if self.NO_OF_PLAYERS_textbox_text == "" or self.NO_OF_PLAYERS_textbox_text == "0":
                            self.NO_OF_PLAYERS_textbox_text = "4"
                        self.NO_OF_PLAYERS_pygame_text = self.OPTIONS_FONT.render(self.NO_OF_PLAYERS_textbox_text, True, YELLOW)
                        self.textbox_active = False
                        self.main_menu_display_setup(False)
                        return int(self.NO_OF_PLAYERS_textbox_text)
                
                #Taking key input and updating textbox
                elif event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        self.NO_OF_PLAYERS_textbox_text = self.NO_OF_PLAYERS_textbox_text[:-1]
                        print(self.NO_OF_PLAYERS_textbox_text)
                    
                    #To exit the textbox
                    elif event.key == pygame.K_RETURN or event.key == K_KP_ENTER:
                        if self.NO_OF_PLAYERS_textbox_text == "" or self.NO_OF_PLAYERS_textbox_text == "0":
                            self.NO_OF_PLAYERS_textbox_text = "4"
                        self.NO_OF_PLAYERS_pygame_text = self.OPTIONS_FONT.render(self.NO_OF_PLAYERS_textbox_text, True, YELLOW)
                        self.textbox_active = False
                        self.main_menu_display_setup(False)
                        return int(self.NO_OF_PLAYERS_textbox_text)

                    #To validate the input text
                    try:
                        if chr(event.key).isnumeric():
                            self.NO_OF_PLAYERS_textbox_text = chr(event.key)
                        
                    except:
                        pass

            self.NO_OF_PLAYERS_pygame_text = self.OPTIONS_FONT.render(self.NO_OF_PLAYERS_textbox_text, True, YELLOW)
            self.main_menu_display_setup(True if (i//no_of_frames)%2 == 1 else False)
            i += 1

    def game(self):
        
        #Game loop!
        while True:
            #Check if the current player is dead
            if self.players[self.current_player].is_dead:
                self.current_player = self.current_player + 1 if self.current_player < self.no_of_players-1 else 0
                continue

            for event in pygame.event.get():

                #Quit event
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
        
                #Touch event
                elif event.type == MOUSEBUTTONDOWN or event.type == FINGERDOWN:
                    #Logic of the game
                    event.player = self.current_player
                    self.logic(event.pos, event.player)
                
                elif event.type == VIDEORESIZE:
                    self.WINDOW_WIDTH, self.WINDOW_HEIGHT = event.w, event.h
                    self.set_layout()
                    self.lines_init()
                    self.rects_init()
            
            #Update the background                    
            
            self.display()

            #Update the window screen
            pygame.display.update()

if __name__ == "__main__":
    grid_allotment = (8, 6, 100, 600, 700)
    grid = Grid(*grid_allotment)
