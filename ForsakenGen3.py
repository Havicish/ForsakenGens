import pyautogui as Gui
from itertools import permutations
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

Gui.PAUSE = 0.1

MainConsole = Console()
#MainConsole.clear()

GetColorX = 727 + 3
GetColorY = 312 + 3
GetIfOnGenX = 698
GetIfOnGenY = 277

EmptyColor = (12, 12, 12)

#system("clear")

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
                if Color == EmptyColor:
                    NewRow.append(EmptyColor + (False,))
                else:
                    NewRow.append(Color + (True,))
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

    def ResetConnects(self, ColorSpecific = None):
        for i in range(0, 6):
            for j in range(0, 6):
                Color = self.Grid[i][j]
                if ColorSpecific is None:
                    if Color[3] == False:
                        self.Grid[i][j] = EmptyColor + (False,)
                else:
                    if Color[3] == False and Color[0:3] == ColorSpecific[0:3]:
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

        for i, j in Path:
            self.Grid[i][j] = (StartingColor[0], StartingColor[1], StartingColor[2], False)
        # Restore node status at ends
        self.Grid[Path[0][0]][Path[0][1]] = StartingColor
        self.Grid[Path[-1][0]][Path[-1][1]] = StartingColor


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
                if 0 <= nx < 6 and 0 <= ny < 6 and (nx, ny) not in visited and (self.Grid[nx][ny] == EmptyColor + (False,) or self.Grid[nx][ny] == self.Grid[i0][j0]):
                    queue.append((nx, ny, path))

        return []
    
    def FindAllPaths(self, i0, j0, i1, j1):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        visited = set()
        queue = deque([(i0, j0, [])])
        paths = []

        while queue:
            x, y, path = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            path = path + [(x, y)]

            if (x, y) == (i1, j1):
                paths.append(path)
                continue

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 6 and 0 <= ny < 6 and (nx, ny) not in visited and (self.Grid[nx][ny] == EmptyColor + (False,) or self.Grid[nx][ny] == self.Grid[i0][j0]):
                    queue.append((nx, ny, path))

        return paths
    
    from itertools import permutations

    def Solve(self):
        Pairs = []
        Seen = set()

        for i in range(6):
            for j in range(6):
                Color = self.Grid[i][j]
                if Color[3] == True and Color not in Seen:
                    Partner = self.GetPartner(Color, i, j)
                    if Partner:
                        Pairs.append(((i, j), Partner))
                        Seen.add(Color)

        def Backtrack(PairOrder, Index):
            if Index == len(PairOrder):
                return True

            (i0, j0), (i1, j1) = PairOrder[Index]
            Paths = self.FindAllPaths(i0, j0, i1, j1)
            for Path in Paths:
                Backup = [row[:] for row in self.Grid]
                self.FollowPath(Path)
                if Backtrack(PairOrder, Index + 1):
                    return True
                self.Grid = [row[:] for row in Backup]
            return False

        for Order in permutations(Pairs):
            if Backtrack(Order, 0):
                return

    def CheckAllPathsValid(self):
        for i in range(0, 6):
            for j in range(0, 6):
                Color = self.Grid[i][j]
                if Color[3] == True:
                    Partner = self.GetPartner(Color, i, j)
                    if Partner is not None:
                        Path = self.FindPath(i, j, Partner[0], Partner[1])
                        if not Path:
                            return False
        return True
    
    def MoveMouse(self):
        ColorsDone = []
        for i in range(0, 6):
            for j in range(0, 6):
                Color = self.Grid[i][j]
                if Color[3] == True and Color not in ColorsDone:
                    ColorsDone.append(Color)
                    visited = set()
                    stack = [(i, j)]

                    Gui.mouseDown(GetColorX + 86 * j, GetColorY + 86 * i)
                    while stack:
                        x, y = stack.pop()
                        if (x, y) in visited:
                            continue
                        visited.add((x, y))

                        Gui.moveTo(GetColorX + 86 * y, GetColorY + 86 * x)

                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < 6 and 0 <= ny < 6 and (nx, ny) not in visited and self.Grid[nx][ny][0:3] == Color[0:3]:
                                stack.append((nx, ny))
                    Gui.mouseUp()

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

while True:    
    time.sleep(0.5)

    if GetIfOnGen():
        MainGrid = Grid()
        MainGrid.MakeGrid()
        MainGrid.Solve()
        MainGrid.MoveMouse()
        MainGrid.Print()
        Gui.moveTo(GetColorX + 86 * 3, GetColorY + 86 * -1)