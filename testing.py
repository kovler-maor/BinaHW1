marines = {"marine_1": {"position": (2, 5), "route": [(1, 2), (2, 3)], "direction": "forwardbackwards"}}

print(marines["marine_1"]["route"].index((2, 3)))

x = []
state = {
    "map": [
        ['I', 'I', 'I', 'S'],
        ['I', 'I', 'I', 'S'],
        ['I', 'I', 'I', 'I']
    ],
    "pirate_ships": {"pirate_ship_1": (2, 0), "pirate_ship_2": (2, 0)},
    "treasures": {'treasure_1': (1, 1)},
    "marine_ships": {'marine_1': [(0, 0)], 'marine_2': [(1, 0)]}
},

x = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
y = {1, 2}
print(x - y)
