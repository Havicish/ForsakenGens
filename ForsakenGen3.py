import pyautogui as Gui
import time
import mss
import threading
from PIL import Image
from os import system
from random import randint
from queue import Queue

Gui.PAUSE = 0.03

GetColorX = 727 + 3
GetColorY = 312 + 3
GetIfOnGenX = 698
GetIfOnGenY = 277

EmptyColor = (12, 12, 12)
FilledColor = (0, 0, 0)

class Grid:
    def __init__(self):
        self.Grid = []
    
    def MakeGrid(self):
        Img = GetImg()
        self.Grid = []  

        for i in range(0, 6):
            NewRow = []
            for j in range(0, 6):
                Color = Img.getpixel((GetColorX + 86 * j, GetColorY + 86 * i))
                NewRow.append(Color)
            self.Grid.append(NewRow)
        
        return self.Grid
    
    def Print(self):
        for i in range(0, 6):
            for j in range(0, 6):
                print(self.Grid[i][j], end=" ")
            print()

def GetImg():
    with mss.mss() as sct:
        screenshot = sct.grab((0, 0, 1919, 1079))
        img = Image.frombytes("RGB", (1919, 1079), screenshot.rgb, "raw")
        return img
    
MainGrid = Grid()
MainGrid.MakeGrid()
MainGrid.Print()