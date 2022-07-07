""" This file scrapes the puzzle grid geometry, across and down clues,
    and the official solutions provided at New York Times Mini Puzzle by Joel
    Fagliano, by using Selenium for website clicks and Beautiful Soup for 
    content parsing. 
    
    After web-scraping, it displays puzzle grid, official solution and
    the clues on a window created with Tkinter library.
    
    Created by    
        Bartu Akyürek

    @date 25 October 2020
"""
from bs4 import BeautifulSoup
from tkinter import *
from datetime import date
import datetime
import time

# Import the Selenium libraries used in this program
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# Import the Chrome driver manager to install the latest version without adding it to the path (to run Selenium without additional setups on different computers)
from webdriver_manager.chrome import ChromeDriverManager # Driver manager for Chrome

ssflag = 0
mode = input("Enter 1 to run the program in singlestepping mode \n Enter 0 to run in normal mode: ")
if mode == "1":
    ssflag = 1

''' Chrome web-driver is used in Selenium for clicking buttons on the web page'''
driver = webdriver.Chrome(ChromeDriverManager().install()) # Installs latest Chrome web-driver

print("\n-----------------------------------------")
print("======= Web Driver is installed. ========") # Web driver is installed.
print("-----------------------------------------")

class Cell(object):
    ''' Cell is an object with availability, upper number and letter attributes.
    It is used for having 25 cells with having all the three information (availability,
    upper text and letter) in one structure for compactness. When displaying scraped
    data, the letter is provided by NYT official solution, when the cell object is 
    constructed by AI, the letter attribute will be the guess letter of AI.
    
    @param available: whether the cell is black or white | boolean type (0:black, 1:white)
    @param upper_text: the text at the top left corner of a cell (if exists) | string type
    @param letter: the revealed letter belongs to the official solution or (in the next demo) AI's guess
    '''
    def __init__(self, available, upper_text,letter):
        self.available = available
        self.upper_text = upper_text
        self.letter = letter

if ssflag == 1:
    print("Connecting to nytimes.com/crosswords/game/mini...")
    time.sleep(1)

URL = 'https://www.nytimes.com/crosswords/game/mini'
#URL = "https://www.nytimes.com/crosswords/game/mini/2019/11/10"

if ssflag == 1:
    print("Opening the website...")
    time.sleep(1)

# Open the website
driver.get(URL)

#----------------------------------CLICKING THE POP-UPS AND THE REVEAL BUTTON USING SELENIUM-----------------------------------

if ssflag == 1:
    print("Closing the pop up...")
    time.sleep(0.5)
# Locate the first pop-up window, wait until clickable and click okay
first_popup_xpath = '//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/div[2]/div[3]/div/article/div[2]/button'
first_popup = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, first_popup_xpath)))
first_popup.click()

if ssflag == 1:
    print("Clicking reveal...")
    time.sleep(0.5)
# Locate and click the reveal button 
reveal_button = driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/li[2]/button')
reveal_button.click()

# From reveal options, select puzzle (puzzle reveal)
reveal_option = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/li[2]/ul/li[3]/a') 
reveal_option.click()

# Click reveal at the "are you sure?" pop-up
sure_popup = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/article/div[2]/button[2]/div/span') 
sure_popup.click()

if ssflag == 1:
    print("Reveal is done.")
    time.sleep(0.5)

#------------------------------------WEB-SCRAPING USING BEAUTIFUL SOUP-------------------------------------------------------

if ssflag == 1:
    print("Downloading the web content...")
    time.sleep(1)
    
# Get the page content after revealed by Selenium web driver
soup = BeautifulSoup(driver.page_source, 'html.parser') # Pass the web content to Beautiful Soup

# Find the puzzle board by ID and role
board_id = soup.find(id='xwd-board')
cells = board_id.find(role='table') # Cells are located at role = table attribute under the board_id line
cell_list = cells.find_all('g') # Each cell has the tag <g>, there are 25 <g> tags under the variable "cells"

row = 5 # Number of rows of the mini puzzle
col = 5 # Number of columns of the mini puzzle

# entries is a 5x5 list for each individual cell
entries = [[Cell(0, 0,'-') for x in range(row)] for y in range(col)]
# r and c are for the iteration at entries list
r = 0
c = 0

if ssflag == 1:
    print("Scraping grid...")
    time.sleep(1)

# Iterate through the puzzle for scraping each individual cell content
for cell in cell_list:
    cell_texts = cell.find_all('text')
    
    if c == col: # If reached to the end of columns
            c = 0 # Go to column zero
            r += 1 # Update the row index

    if(len(cell_texts) == 0): # cell is a black square
        entries[r][c] = Cell(0,0,"-") # "-" means it is a black square

    elif(len(cell_texts) == 2): # cell is a white square without a little number
        letter = cell_texts[1].text # Revealed letter
        entries[r][c] = Cell(1,0,letter) 
        
    elif(len(cell_texts) == 4): # cell is a white square with a little number
        little_number = cell_texts[0].text # Little number
        letter = cell_texts[3].text # Revealed letter
        entries[r][c] = Cell(1,little_number,letter) 
        
    else: # If this error is given, it means the website content is changed because the if-elif statements above are working for current website structure
        print("Error: Website grid content should have changed.")
        
    c += 1 # Move to the next cell

if ssflag == 1:
    print("Scraping clues...")
    time.sleep(1)
clue_class = soup.find_all(class_="Clue-li--1JoPu") # Only the across and down clues is inside the class "Clue-li--1JoPu"

across_clue_list= []
down_clue_list= []
clue_divider_flag = False # to distinguish across and down clues

for i in clue_class:
    clue_number = i.find(class_ = "Clue-label--2IdMY").string # Gets the string attribute of the "clue label" class
    clue_text = i.find(class_ = "Clue-text--3lZl7").string # Gets the string attribute of the "clue text" class
    
    if clue_number == "1": # Across and down clues start with clue number 1
        clue_divider_flag = not clue_divider_flag # Flag is used for distinguishing which clue number = 1 belongs to across or down
    
    if clue_divider_flag: # If the flag is True, the cursor is at across clues
        across_clue_list.append( [ clue_number, clue_text] )
    else: # If the flag is false, the cursor is at down clues
        down_clue_list.append( [ clue_number, clue_text] )

# Web scraping is completed.
if ssflag == 1:
    print("Web-scraping is completed.")
    time.sleep(1)
    
# Close the driver.
driver.quit()
 
if ssflag == 1:
    print("-----------------------------------------")
    print("========= Web driver is closed. =========")
    print("-----------------------------------------")
    time.sleep(0.2)
    print("Printing the web contents...")
    time.sleep(0.5)

#---------------------------------------------CREATING GUI WINDOW---------------------------------------------------------

# Creating gui window
if ssflag == 1:
    print("Opening window...")
    time.sleep(1)
    
window = Tk()
window.attributes("-topmost", True) # Make the window appear at the front
#window.iconbitmap('nyt.ico') # NYT icon for the GUI window
# commented line above let a nyt icon appear on the top left of the figure window
# since moddle doesnt let additional uploads we commented the icon 
window.title('New York Times Mini Crossword by Joel Fagliano')
window.geometry('1000x600+400+200') # Window appears at (500,200) with 1000x600 dimensions on the screen

#Placing canvas to the window
if ssflag == 1:
    print("Opening canvas...")
    time.sleep(1)
 
mini_canvas_width = 470
mini_canvas_height = 575
mini_canvas = Canvas(window, width = mini_canvas_width, height = mini_canvas_height)
mini_canvas.pack(side = LEFT)

#------------------------------------------------CREATING THE GRID STRUCTURE----------------------------------------------------

if ssflag == 1:
    print("Placing the grid...")
    time.sleep(1)
    
# Placing the grid with the left corner (x_margin,y_margin)
x_margin = 50
y_margin = 125

# Defining square size for a cell
box_width = 75
box_height = box_width 

if ssflag == 1:
    print("Writing info...")
    time.sleep(1)

# Printing the title "Mini Crossword" and original creator
mini_canvas.create_text(x_margin,90,text = "The Mini Crossword",font=('Arial', '38', 'bold'),anchor="sw")
mini_canvas.create_text(x_margin,100,text = "by Joel Fagliano",font=('Arial', '14', 'normal'),anchor="sw")

line_margin = 1 #for internal lines
outline_margin = 4*line_margin #for the heavy outline of the puzzle grid

# Heavy outline of the mini puzzle
outline_x1 = x_margin-outline_margin
outline_y1 = y_margin-outline_margin
outline_x2 = x_margin+(col*box_width)+outline_margin
outline_y2 = y_margin+(row*box_height)+outline_margin
# Create a black quare for the heavy grid outline
mini_canvas.create_rectangle(outline_x1,outline_y1,outline_x2,outline_y2,fill="black")

# Add date, time and group nick at the right bottom of the puzzle outline
date_widget = mini_canvas.create_text(outline_x2, outline_y2+5,text = date.today().strftime("%A, %B %d, %Y"),font=('Arial', '14', 'normal'),anchor="ne")
time_widget = mini_canvas.create_text(outline_x2-45, outline_y2+22,text = datetime.datetime.now().strftime("%H:%M:%S"),font=('Arial', '12', 'normal'),anchor="nw")

# Put the group name
mini_canvas.create_text(outline_x2, outline_y2+35,text = "BADS",font=('Arial', '20', 'normal'),anchor="ne")

cell_frames= [ [[None] for c in range(col)] for r in range(row)] 
solution_letters = []

#---------------------------------------------PRINTING THE CLUES---------------------------------------------------------
clue_cancas_width = 230
clue_canvas_height = 350

across_canvas = Canvas(window, width=clue_cancas_width,height=clue_canvas_height,bg="white")
across_canvas.pack(side=LEFT)

down_canvas = Canvas(window, width=clue_cancas_width,height=clue_canvas_height, bg = "white")
down_canvas.pack(side=LEFT)

if ssflag == 1:
    print("Printing across clues...")
    time.sleep(1)

clue_padx = 20 # Text offsets of clues inside their canvas

across_canvas.create_text(clue_padx,30,width= 200,text = "Across",font=('Arial', '18', 'bold'),anchor="w")
across_text = ""

for clue in across_clue_list:
    across_text += clue[0] + " " + clue[1] + "\n\n"

across_canvas.create_text(clue_padx,65,width= 200,text = across_text,font=('Arial', '14', 'normal'),anchor="nw")

if ssflag == 1:
    print("Printing down clues...")
    time.sleep(1)

down_canvas.create_text(clue_padx,30,width= 200,text = "Down",font=('Arial', '18', 'bold'),anchor="w")
down_text = ""

for clue in down_clue_list:
        down_text += clue[0] + " " + clue[1] + "\n\n"


down_canvas.create_text(clue_padx,65,width= 200,text = down_text,font=('Arial', '14', 'normal'),anchor="nw")

#-------------------------------------METHODS FOR PRINTING THE GRID AND TIME--------------------------------------
def update_puzzle():
    '''
    This method draws the puzzle grid on the left side of the GUI window. Each cell is
    a square created by Tkinter's create_rectangle() method, with the fill color determined
    by cell's availability (block cell or answer cell) and gray border color (originated by 
    NYT mini website).
    
    After putting the square for an individual cell, the function looks for the upper number
    of the cell (if available) and the solution letter if the cell is not black.
    '''
    for r in range(row):
        for c in range(col):
                
            cell = entries[r][c]
            if cell.available == 1:
                box_color = "white"
            else:
                box_color = "black"
                
            x1 = x_margin+(box_width*c)
            x2 = x_margin + box_width * (c + 1)
            y1 = y_margin + box_height *r
            y2 = y_margin + box_height * (r + 1)
            
            cell_frames[r][c] = mini_canvas.create_rectangle(x1,y1,x2,y2, fill=box_color,outline="#575757")
            
            if cell.upper_text != 0:
                mini_canvas.create_text(x1+2,y1+3,text = str(cell.upper_text),font=('Arial', '18', 'bold'),anchor="nw")

            solution_letters.append(cell.letter)
            if cell.letter != '-':
                mini_canvas.create_text(x1+box_width/2,y2,text = str(cell.letter),font=('Arial', '45', 'bold'),anchor="s",fill="#2760d8")
def clock():
    '''
    This method calls itself in every one second, to update the time at the right bottom
    of the puzzle grid.
    
    Datetime library provides current time information with %H as hour, %M as
    minute and %S as second appended by 0 (for instance 09:32:02)
    
    It calls itself after every second (1000ms) to update the time. Note that the 
    warning printed in the console is due to after() command but it still works correctly.
    '''
    time_txt = datetime.datetime.now().strftime("%H:%M:%S")
    
    if 'normal' == window.state(): # If GUI window is open, update the time
        mini_canvas.itemconfig(time_widget, text = time_txt)
        window.after(1000,clock) # Calls itself every 1000 ms

#-------------------------------------INITIAL CALLS FOR GUI TO START--------------------------------------
#initially    
update_puzzle()
clock()
window.mainloop()

#----------AUTOMATIC STORAGE OF PUZZLE INFORMATION IN A TXT FILE (executed after the gui window is closed)-----------------------------------
"""
The code below deals with the storage of the puzzles.
puzzlebank.txt is the file where information of that day's puzzle is written to a new line.
every piece of information is separated by a tab character in order of:
date - across clues - down clues - cell information
"""
if ssflag == 1:
    print("Storing today's puzzle...")
    time.sleep(1)

puzzle_file = open("puzzlebank.txt","a")
tab = "\t"
puzzle_info=[] #list for information of puzzle
puzzle_info.append(date.today().strftime("%y-%m-%d")) #date of the puzzle
for pair in across_clue_list: #since across clues are made of lists [clue#,clue]
    puzzle_info.append(",".join(pair)) #make the pair list a string separated by comma
for pair in down_clue_list: #since down clues are made of lists [clue#,clue]
    puzzle_info.append(",".join(pair)) #make the pair list a string separated by comma
for r in range(row):
    for c in range(col):
        tmp_cell = entries[r][c] #for every cell
        puzzle_info.append(str(tmp_cell.available) + ',' + str(tmp_cell.upper_text) + ',' + tmp_cell.letter)
        #cell info is written as availability,uppertext,letter in solution

puzzle_file.write(tab.join(puzzle_info)) 
puzzle_file.write("\n") # Put a new line at the end to indicate termination (if the puzzle is today) or for the upcoming puzzle, indicate seperation
#If there is no content in the new line, it indicates termination

#since puzzle_info is a list, make it a string with elements separated by tab character
#append info at the end of the file
puzzle_file.close()

if ssflag == 1:
    print("Done.")
    time.sleep(1)
