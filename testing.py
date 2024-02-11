import itertools

import ex1
import search
import time

list_1 = [("sail", "pirate_ship1", (2, 0)), ("wait", "pirate_ship1")]
list_2 = [("sail", "pirate_ship2", (2, 0)), ("wait", "pirate_ship2")]
list_3 = [("sail", "pirate_ship3", (2, 0)), ("wait", "pirate_ship3")]
list_4 = [("sail", "pirate_ship4", (2, 0)), ("wait", "pirate_ship4")]

list_of_lists = [list_1]


# a function that gives all of the cross product of all given tuples in the form of list of tuples
def cross_product(list_of_lists):
    if len(list_of_lists) == 1:
        return list_of_lists[0]
    else:
        return [(x,) + (y,) for x in list_of_lists[0] for y in cross_product(list_of_lists[1:])]


list_t = cross_product(list_of_lists)


# a function that gives all of the cross product of all given tuples in the form of list of tuples


from itertools import product

# a function that gets a list of lists and returns each list separately separated by a comma



actions = list(itertools.product(*list_of_lists))
for action in actions:
    print(action)
