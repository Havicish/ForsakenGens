import pyautogui as Gui
import time
import mss
from PIL import Image
from os import system
from random import randint

Gui.PAUSE = 0.5

GetColorX = 760 - 8
GetColorY = 395 - 5

def TupleDist(Tuple1, Tuple2):
    if len(Tuple1) != len(Tuple2):
        raise ValueError("Tuples must have the same length.")
    return sum(abs(a - b) for a, b in zip(Tuple1, Tuple2))

def GetImg():
    with mss.mss() as sct:
        screenshot = sct.grab((0, 0, 1919, 1079))
        img = Image.frombytes("RGB", (1919, 1079), screenshot.rgb, "raw")
        return img
    
def GetPartner(Grid: list, Color: tuple):
    for i in range(0, 6):
        for j in range(0, 6):
            if Grid[i][j] == Color:
                return (i, j)
            
def IsOnWall(i: int, j: int):
    if i == 0 or j == 0 or i == 5 or j == 5:
        return True
    return False

def ConnectNeighbors(Grid: list):
    for i in range(0, 4):
        for j in range(0, 4):
            if Grid[i][j][0] != Grid[i][j][1] and Grid[i][j][1] != Grid[i][j][2]:
                if Grid[i][j] == Grid[i + 1][j]:
                    print("Down")
                    Gui.mouseDown(GetColorX + 88 * j - randint(0, 33), GetColorY + 88 * i - 88 + randint(0, 33))
                    Gui.moveRel(0, 88 + randint(0, 33))
                    Gui.mouseUp()
                if Grid[i][j] == Grid[i][j + 1]:
                    print("Right")
                    Gui.mouseDown(GetColorX + 88 * j - randint(0, 33), GetColorY + 88 * i - 88 + randint(0, 33))
                    Gui.moveRel(88 - randint(0, 33), 0)
                    Gui.mouseUp()

def ConnectPartnersOnWalls(Grid: list):
    for i in range(0, 5):
        for j in range(0, 5):
            if Grid[i][j][0] == Grid[i][j][1] == Grid[i][j][2]:
                continue

            print("e")

            if IsOnWall(i, j):
                Partner = GetPartner(Grid, Grid[i][j])
                if IsOnWall(Partner[0], Partner[1]):
                    while j < Partner[1]:
                        print("Right")
                        Gui.mouseDown(GetColorX + 88 * j - randint(0, 33), GetColorY + 88 * i - 88 + randint(0, 33))
                        Gui.moveRel(88 - randint(0, 33), 0)
                        Gui.mouseUp()
                        j += 1
                    while j > Partner[1]:
                        print("Left")
                        Gui.mouseDown(GetColorX + 88 * j - randint(0, 33), GetColorY + 88 * i - 88 + randint(0, 33))
                        Gui.moveRel(-88 + randint(0, 33), 0)
                        Gui.mouseUp()
                        j -= 1
                    while i < Partner[0]:
                        print("Down")
                        Gui.mouseDown(GetColorX + 88 * j - randint(0, 33), GetColorY + 88 * i - 88 + randint(0, 33))
                        Gui.moveRel(0, 88 + randint(0, 33))
                        Gui.mouseUp()
                        i += 1
                    while i > Partner[0]:
                        print("Up")
                        Gui.mouseDown(GetColorX + 88 * j - randint(0, 33), GetColorY + 88 * i - 88 + randint(0, 33))
                        Gui.moveRel(0, -88 + randint(0, 33))
                        Gui.mouseUp()
                        i -= 1

time.sleep(2)
Gui.moveTo(100, 100)
while True:
    Img = GetImg()
    Pxl = Img.getpixel((611, 191))
    if TupleDist(Pxl, (255, 255, 255)) < 25 and Pxl[0] == Pxl[1] == Pxl[2] or True:
        #system(f"afplay /Users/damiencaum/Documents/GitHub/ForskenPuzzleSolver/CameraSound.mp3")

        Grid = []
        for i in range(-1, 5):
            Row = []
            for j in range(0, 6):
                Pxl = Img.getpixel((GetColorX + 88 * j, GetColorY + 88 * i))
                Row.append(Pxl)
            Grid.append(Row)

        for i in range(0, 6):
            for j in range(0, 6):
                print(Grid[i][j], end = " ")
            print()

        ConnectNeighbors(Grid)

        ConnectPartnersOnWalls(Grid)

    exit()
    time.sleep(1)