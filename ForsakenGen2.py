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

def GetImg():
    with mss.mss() as sct:
        screenshot = sct.grab((0, 0, 1919, 1079))
        img = Image.frombytes("RGB", (1919, 1079), screenshot.rgb, "raw")
        return img

def MakeGrid():
    Img = GetImg()
    Grid = []

    for i in range(0, 6):
        NewRow = []
        for j in range(0, 6):
            Color = Img.getpixel((GetColorX + 86 * j, GetColorY + 86 * i))
            NewRow.append(Color)
        Grid.append(NewRow)
    
    return Grid

def PrintGrid(Grid: list):
    for i in range(0, 6):
        for j in range(0, 6):
            print(Grid[i][j], end=" ")
        print()

def GetPartner(Grid: list, Color: tuple, i: int, j: int):
    for x in range(0, 6):
        for y in range(0, 6):
            if Grid[x][y] == Color and (i, j) != (x, y):
                return (x, y)

def IsOnWall(i: int, j: int):
    if i == 0 or j == 0 or i == 5 or j == 5:
        return True
    return False

def FollowPath(Path: list, Grid: list):
    if Path:
        Grid = PseudoFollowPath(Path, Grid)
        IsDown = False
        for ni, nj in Path:
            if IsDown:
                Gui.moveTo(GetColorX + 86 * nj, GetColorY + 86 * ni)
            else:
                Gui.mouseDown(GetColorX + 86 * nj, GetColorY + 86 * ni)
                IsDown = True
        Gui.mouseUp()

    return Grid

def PseudoFollowPath(Path: list, Grid: list):
    if Path:
        for ni, nj in Path:
            if Grid[ni][nj] != EmptyColor:
                continue

            Grid[ni][nj] = FilledColor

    return Grid

def PathfindToPos(Grid: list, i0: int, j0: int, i1: int, j1: int):
    def BFS(start, goal):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        visited = set()
        queue = Queue()
        queue.put((start, []))

        while not queue.empty():
            (current, path) = queue.get()
            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                return path

            for dx, dy in directions:
                ni, nj = current[0] + dx, current[1] + dy
                if 0 <= ni < 6 and 0 <= nj < 6 and (Grid[ni][nj] == EmptyColor or (ni, nj) == goal) and Grid[ni][nj] != FilledColor:
                    queue.put(((ni, nj), path + [(ni, nj)]))

        return None

    path = BFS((i0, j0), (i1, j1))
    if path:
        Gui.mouseDown(GetColorX + 86 * j0, GetColorY + 86 * i0)
        for ni, nj in path:
            Gui.moveTo(GetColorX + 86 * nj, GetColorY + 86 * ni)
        Gui.mouseUp()

def PathfindToPosWALLBOUND(Grid: list, i0: int, j0: int, i1: int, j1: int):
    def BFS(start, goal):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        visited = set()
        queue = Queue()
        queue.put((start, []))

        while not queue.empty():
            (current, path) = queue.get()
            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                return path

            for dx, dy in directions:
                ni, nj = current[0] + dx, current[1] + dy
                if 0 <= ni < 6 and 0 <= nj < 6 and IsOnWall(ni, nj) and (Grid[ni][nj] == EmptyColor or (ni, nj) == goal) and Grid[ni][nj] != FilledColor:
                    queue.put(((ni, nj), path + [(ni, nj)]))

        return None

    path = BFS((i0, j0), (i1, j1))
    if path:
        path = [(i0, j0)] + path
    return path

HasConnected = []
def ConnectPartnersOnWalls(Grid: list):
    global HasConnected
    HasConnected.clear()
    for i in range(6):
        for j in range(6):
            Color = Grid[i][j]
            if Color == EmptyColor:
                continue

            if Color in HasConnected:
                continue

            if not IsOnWall(i, j):
                continue

            Partner = GetPartner(Grid, Color, i, j)
            if not Partner:
                continue

            if not IsOnWall(Partner[0], Partner[1]):
                continue

            print("Both on wall", "\n", j + 1, i + 1, "\n", Partner[1] + 1, Partner[0] + 1)

            Path = PathfindToPosWALLBOUND(Grid, i, j, Partner[0], Partner[1])
            if Path:
                PathIsClear = True
                for ni, nj in Path:
                    if Grid[ni][nj] != EmptyColor and Grid[ni][nj] != Color:
                        PathIsClear = False
                        print("Path is blocked", "\n", nj + 1, ni + 1)
                        break

                if not PathIsClear:
                    continue

                print("Path is clear")
                FollowPath(Path, Grid)

            if Path:
                HasConnected.append(Color)

def ConnectOtherPartners(Grid: list):
    global HasConnected
    HasConnected = HasConnected
    for i in range(6):
        for j in range(6):
            Color = Grid[i][j]
            if Color == EmptyColor:
                continue

            if Color in HasConnected:
                continue

            Partner = GetPartner(Grid, Color, i, j)
            if not Partner:
                continue

            Path = PathfindToPos(Grid, i, j, Partner[0], Partner[1])
            if Path:
                PathIsClear = True
                for ni, nj in Path:
                    if Grid[ni][nj] != EmptyColor and Grid[ni][nj] != Color:
                        PathIsClear = False
                        break

                if not PathIsClear:
                    continue

                Grid = PseudoFollowPath(Path)

                # Check if all other colors can still connect
                ColorsThatCantConnect = []
                for x in range(6):
                    for y in range(6):
                        Color = Grid[x][y]
                        if Color == EmptyColor:
                            continue

                        if Color in HasConnected:
                            continue

                        Partner = GetPartner(Grid, Color, x, y)
                        if not Partner:
                            continue

                        Path = PathfindToPos(Grid, x, y, Partner[0], Partner[1])
                        if not Path:
                            ColorsThatCantConnect.append(Color)
                            continue
                        
                        PathIsClear = True
                        for ni, nj in Path:
                            if Grid[ni][nj] != EmptyColor and Grid[ni][nj] != Color:
                                PathIsClear = False
                                break

                        if not PathIsClear:
                            ColorsThatCantConnect.append(Color)
                            continue

                        Grid = PseudoFollowPath(Path)

                for Color in ColorsThatCantConnect:
                    #if Color in HasConnected:
                    #    continue

                    Partner = GetPartner(Grid, Color, i, j)
                    if not Partner:
                        continue

                    Path = PathfindToPos(Grid, i, j, Partner[0], Partner[1])
                    if Path:
                        PathIsClear = True
                        for ni, nj in Path:
                            if Grid[ni][nj] != EmptyColor and Grid[ni][nj] != Color:
                                PathIsClear = False
                                break

                        if not PathIsClear:
                            continue

                        Grid = FollowPath(Path)

            HasConnected.append(Color)

    return Grid

def CheckIfOnGen():
    Img = GetImg()
    StillTrue = True
    for i in range(0, 5):
        Color = Img.getpixel((GetIfOnGenX + 86 * i, GetIfOnGenY))
        if Color != (0, 0, 0):
            StillTrue = False
            break

    return StillTrue

Grid = []
def Solve():
    global Grid

    ConnectPartnersOnWalls(Grid)
    ConnectOtherPartners(Grid)

    system("afplay /System/Library/Sounds/Glass.aiff")

while True:
    time.sleep(0.5)

    if not CheckIfOnGen():
        continue

    Grid = MakeGrid()
    PrintGrid(Grid)

    Thread = threading.Thread(target=Solve)
    Thread.daemon = True
    Thread.start()
    Thread.join()

    while CheckIfOnGen():
        time.sleep(0)