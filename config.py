game = {
    "tiles": [9, 9],
    "mines": 10,
    "colors": {
        "unknown": (31, 113, 248),
        "empty": (230, 230, 230),
        "flag": (255, 0, 0),
        "mine": (0, 0, 0),
    }
}

window = {
    "tile_size": 16,
    "border_width": 2,
    "title": "Minesweeper",
    "width": 0,
    "height": 0,
}

window["width"] = game["tiles"][0] * window["tile_size"] + (game["tiles"][0] - 1) * window["border_width"]
window["height"] = game["tiles"][1] * window["tile_size"] + (game["tiles"][1] - 1) * window["border_width"]