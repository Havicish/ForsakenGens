#import pyautogui as Gui
import time
import mss
import threading
from rich.console import Console
from rich.text import Text
from PIL import Image
from os import system
from random import randint
from queue import Queue
from collections import deque

#Gui.PAUSE = 0.03

MainConsole = Console()
MainConsole.clear()

GetColorX = 727 + 3
GetColorY = 312 + 3
GetIfOnGenX = 698
GetIfOnGenY = 277

EmptyColor = (12, 12, 12)

system("clear")

class Grid:
    def __init__(self):
        self.Grid = []
    
    def MakeGrid(self, MakeFake = False):
        # !!! The point of the fourth item in the tuple is to check if the cell is a connector, or a node
        if MakeFake:
            self.Grid = [
                [
                    (0, 128, 255), EmptyColor, (0, 128, 255), (0, 255, 255), (128, 0, 255), (255, 128, 0)
                ], [
                    EmptyColor, EmptyColor, EmptyColor, EmptyColor, (128, 0, 255), EmptyColor
                ], [
                    EmptyColor, (255, 255, 0), (255, 255, 255), EmptyColor, EmptyColor, (255, 128, 0)
                ], [
                    EmptyColor, (255, 255, 0), (0, 255, 255), EmptyColor, EmptyColor, EmptyColor
                ], [
                    EmptyColor, (0, 255, 0), (0, 255, 0), EmptyColor, (255, 0, 255), EmptyColor
                ], [
                    EmptyColor, EmptyColor, EmptyColor, EmptyColor, (255, 0, 255), (255, 255, 255)
                ]
            ]
            for i in range(0, 6):
                for j in range(0, 6):
                    if self.Grid[i][j] != EmptyColor:
                        self.Grid[i][j] += (True,)
                    else:
                        self.Grid[i][j] += (False,)
            return self.Grid
        
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
        Colors = [EmptyColor + (False,)]
        for i in range(0, 6):
            for j in range(0, 6):
                Color = self.Grid[i][j]
                if Color not in Colors:
                    Colors.append(Color)
        for i in range(0, 6):
            for j in range(0, 6):
                Color = self.Grid[i][j]
                if Color[3] == True:
                    MainConsole.print(Text("#", style=f"s b {RgbToHex(Color)}"), end = " ")
                else:
                    MainConsole.print(Text("+", style=f"{RgbToHex(Color)}"), end = " ")
            MainConsole.print()

    def ResetConnects(self):
        for i in range(0, 6):
            for j in range(0, 6):
                Color = self.Grid[i][j]
                if Color[3] == False:
                    self.Grid[i][j] = EmptyColor + (False,)

    def GetPartner(self, Color: tuple, i: int, j: int):
        for x in range(0, 6):
            for y in range(0, 6):
                if self.Grid[x][y] == Color and (i, j) != (x, y):
                    return (x, y)
                
    """def IsOnWall(self, i: int, j: int):
        if i == 0 or j == 0 or i == 5 or j == 5:
            return True
        return False"""
    
    def FollowPath(self, Path: list):
        StartingColor = self.Grid[Path[0][0]][Path[0][1]]
        if StartingColor[3] == False:
            return
        
        for i in range(0, len(Path)):
            self.Grid[Path[i][0]][Path[i][1]] = (StartingColor[0], StartingColor[1], StartingColor[2], self.Grid[Path[i][0]][Path[i][1]][3])

    def FindPath(self, i0, j0, i1, j1):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        visited = set()
        queue = deque([(i0, j0, [])])

        while queue:
            x, y, path = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            path = path + [(x, y)]

            if (x, y) == (i1, j1):
                return path

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 6 and 0 <= ny < 6:
                    MainConsole.print(Text(f"{nx}, {ny}", style=RgbToHex(self.Grid[nx][ny])), end=" ")
                    print(self.Grid[nx][ny])
                if 0 <= nx < 6 and 0 <= ny < 6 and (nx, ny) not in visited and (self.Grid[nx][ny] == EmptyColor + (False,) or self.Grid[nx][ny] == self.Grid[i0][j0]):
                    queue.append((nx, ny, path))

        return []
    
    def Solve(self):
        PairsNeeded = []
        for i in range(6):
            for j in range(6):
                Color = self.Grid[i][j]
                if Color[3] == True:
                    Partner = self.GetPartner(Color, i, j)
                    if Partner != None:
                        if abs(i - Partner[0]) + abs(j - Partner[1]) == 1:
                            continue
                        if (Partner[0], Partner[1], i, j) not in PairsNeeded:
                            PairsNeeded.append((i, j, Partner[0], Partner[1]))

        for i0, j0, i1, j1 in PairsNeeded:
            Path = self.FindPath(i0, j0, i1, j1)
            if Path:
                self.FollowPath(Path)

def GetImg():
    with mss.mss() as sct:
        screenshot = sct.grab((0, 0, 1919, 1079))
        img = Image.frombytes("RGB", (1919, 1079), screenshot.rgb, "raw")
        return img
    
def GetIfOnGen():
    Img = GetImg()
    StillOnGen = True
    for i in range(0, 5):
        Color = Img.getpixel((GetIfOnGenX + 86 * i, GetIfOnGenY))
        if Color != (0, 0, 0):
            StillOnGen = False
            break
    if StillOnGen:
        return True
    else:
        return False

def RgbToHex(Color):
    return "#{:02X}{:02X}{:02X}".format(Color[0], Color[1], Color[2])
    
MainGrid = Grid()
MainGrid.MakeGrid(True)
MainGrid.Solve()
MainGrid.Print()