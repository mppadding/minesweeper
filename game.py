import pygame, random
from pygame.locals import *

import config

pygame.init()
 
displaysurface = pygame.display.set_mode((config.window["width"], config.window["height"]))
pygame.display.set_caption(config.window["title"])

font = pygame.font.SysFont('Times New Roman', 16)

numbers = [font.render(str(i), False, (0, 0, 0)) for i in range(1, 9)]

def getColorFromValue(val):
    if val == -1:
        return config.game["colors"]["unknown"]
    if val == 0 or val == 1:
        return config.game["colors"]["empty"]
    if val == 2:
        return config.game["colors"]["flag"]
    if val == 3:
        return config.game["colors"]["mine"]

def getIndexFromTile(tile):
    return tile[1] * config.game["tiles"][1] + tile[0]

def getTileFromIndex(index):
    return (index % config.game["tiles"][0], index // config.game["tiles"][1])

def getXPositionFromTile(tile):
    return tile[0] * config.window["tile_size"] + (tile[0] if tile[0] > 0 else 0) * config.window["border_width"]

def getYPositionFromTile(tile):
    return tile[1] * config.window["tile_size"] + (tile[1] if tile[1] > 0 else 0) * config.window["border_width"]

def getPositionFromTile(tile):
    return (getXPositionFromTile(tile), getYPositionFromTile(tile))

def getTileFromPosition(position):
    x_tile = position[0] // 18
    y_tile = position[1] // 18

    return (x_tile, y_tile)

def drawBoard(surf, board, neighbours):
    for y in range(config.game["tiles"][1]):
        y_offset = y * config.game["tiles"][1]
        y_pos = y * config.window["tile_size"] + (y if y > 0 else 0) * config.window["border_width"]
        for x in range(config.game["tiles"][0]):
            x_pos = x * config.window["tile_size"] + (x if x > 0 else 0) * config.window["border_width"]
            pygame.draw.rect(surf, getColorFromValue(board[y_offset + x]), pygame.Rect(x_pos, y_pos, 16, 16))

            if board[y_offset + x] == 1:
                neighb = neighbours[y_offset + x]
                if neighb > 0:
                    displaysurface.blit(numbers[neighb - 1],(5+x_pos,-1 + y_pos))

def generateMines():
    positions = [x for x in range(config.game["tiles"][0] * config.game["tiles"][1])]
    random.seed(None)

    random.shuffle(positions)
    
    return positions[:config.game["mines"]]

def generateNearPositionList(x, y, index):
    checks = [
        index - config.game["tiles"][1] - 1, index - config.game["tiles"][1], index - config.game["tiles"][1] + 1,
        index - 1, index + 1,
        index + config.game["tiles"][1] - 1, index + config.game["tiles"][1], index + config.game["tiles"][1] + 1,
    ]

    # Remove all invalid positions
    if y == 0:
        checks[0] = -1
        checks[1] = -1
        checks[2] = -1

    if x == 0:
        checks[0] = -1
        checks[3] = -1
        checks[5] = -1

    if x == config.game["tiles"][0] - 1:
        checks[2] = -1
        checks[4] = -1
        checks[7] = -1

    if y == config.game["tiles"][1] - 1:
        checks[5] = -1
        checks[6] = -1
        checks[7] = -1

    return checks

def generateNeighbours(mines):
    neighbours = []
    for y in range(config.game["tiles"][1]):
        for x in range(config.game["tiles"][0]):
            index = y * config.game["tiles"][1] + x

            if index in mines:
                neighbours.append(-1)
                continue

            checks = generateNearPositionList(x, y, index)

            num_mines = 0

            for check_pos in checks:
                # Array bounds check
                if check_pos != -1:
                    if check_pos in mines:
                        num_mines += 1

            neighbours.append(num_mines)
    
    return neighbours

def openTile(board, neighbours, index):
    if neighbours[index] > 0:
        board[index] = 1
    else:
        # Neighbours is 0, so flood clear all connected tiles.
        pos = getTileFromIndex(index)
        nears = generateNearPositionList(pos[0], pos[1], index)

        for i in nears:
            if i == -1:
                continue

            if neighbours[i] > 0:
                board[i] = 1

            if neighbours[i] == 0 and board[i] == -1:
                # Recursive solve nears
                board[i] = 1
                openTile(board, neighbours, i)

def moveMine(mines, index):
    for i in range(getIndexFromTile((15, 15))):
        if i not in mines:
            print("Moved mine to " + str(getTileFromIndex(i)))
            print(index)
            print(i)
            mines[index] = i
            break

    return mines

gamestate = {
    "board": [-1 for x in range(config.game["tiles"][0] * config.game["tiles"][1])],
    "mines": generateMines(),
    "neighbours": [],
    "dead": False,
    "first_uncovered": False,
    "run": True
}
gamestate["neighbours"] = generateNeighbours(gamestate["mines"])

while gamestate["run"]:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            gamestate["run"] = False

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            tile_clicked = getTileFromPosition(mouse_pos)
            index_clicked = getIndexFromTile(tile_clicked)

            if gamestate["dead"]:
                gamestate["run"] = False

            if event.button == 1:
                # left click
                if index_clicked in gamestate["mines"]:
                    if not gamestate["first_uncovered"]:
                        # Gracefully move the mine to the 0 position or any free position right from that one.
                        # This is so the player does not die on the first move.
                        gamestate["mines"] = moveMine(gamestate["mines"], gamestate["mines"].index(index_clicked))
                        openTile(gamestate["board"], gamestate["neighbours"], index_clicked)
                    else:
                        print("Boom.")
                        gamestate["board"][index_clicked] = 3
                        gamestate["dead"] = True

                elif gamestate["board"][index_clicked] == -1:
                    openTile(gamestate["board"], gamestate["neighbours"], index_clicked)

                gamestate["first_uncovered"] = True
        
            elif event.button == 3:
                # Right click handler

                # Add flag only to unknown tiles
                if gamestate["board"][index_clicked] == -1:
                    gamestate["board"][index_clicked] = 2

                    gamestate["finished"] = True
                    for m in gamestate["mines"]:
                        if gamestate["board"][m] != 2:
                            gamestate["finished"] = False
                            break
                    
                    if gamestate["finished"]:
                        print("Congratulations!")

                # Remove flag from flag tile
                elif gamestate["board"][index_clicked] == 2:
                    gamestate["board"][index_clicked] = -1

    displaysurface.fill((0,0,0))

    drawBoard(displaysurface, gamestate["board"], gamestate["neighbours"])

    pygame.display.update()

pygame.quit()