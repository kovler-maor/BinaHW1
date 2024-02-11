import itertools

import search
import random
import math

ids = ["313598674", "312239296"]


class OnePieceProblem(search.Problem):
    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        # map of the world
        self.map = initial["map"]
        # treasures in the world ->
        # treasures = {
        # "treasure_1": {"position": (x, y) , "is_collected": true/false},
        # "treasure_2": {"position": (x, y) , "is_collected": true/false}
        # }
        self.treasures = {}
        for treasure in initial["treasures"]:
            self.treasures[treasure] = {"position": initial["treasures"][treasure], "is_collected": False,
                                        "is_on_ship": False}
        # pirate ships in the world ->
        # pirate_ships = {
        # "pirate_ship_1": {"position": (x, y), "treasures": (,)},
        # "pirate_ship_2": {"position": (x, y), "treasures": (,)}
        # }
        self.pirate_ships = {}
        for pirate_ship in initial["pirate_ships"]:
            self.pirate_ships[pirate_ship] = {"position": initial["pirate_ships"][pirate_ship], "treasures": ["", ""]}
        # marine ships in the world marine_ships ={
        # "marine_1": {"position": (x, y), "route":[(x1,y1),(x2,y2)],"direction": "forward"/"backwards"},
        # "marine_2": {"position": (x, y), "route":[(x1,y1),(x2,y2)],"direction": "forward"/"backwards"}
        # }
        self.marine_ships = {}
        for marine_ship in initial["marine_ships"]:
            self.marine_ships[marine_ship] = {"position": initial["marine_ships"][marine_ship][0],
                                              "route": initial["marine_ships"][marine_ship],
                                              "direction": "forward"}

        self.turns = 0

        pirate_base_position = [(i, j) for i in range(len(self.map)) for j in range(len(self.map[0]))
                                if self.map[i][j] == "B"][0]
        initial_dict = {"map": self.map, "pirate_ships": self.pirate_ships, "treasures": self.treasures,
                        "marine_ships": self.marine_ships, "turns": self.turns,
                        "pirate_base_position": pirate_base_position}
        initial = dict_to_string(initial_dict)
        search.Problem.__init__(self, initial)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        state = string_to_dict(state)
        available_actions = []
        for pirate_ship in state["pirate_ships"]:
            current_ship = state["pirate_ships"][pirate_ship]
            ship_actions = []
            pirate_ship_position = state["pirate_ships"][pirate_ship]["position"]
            # Check if the pirate ship can SAIL to the next position
            for action in [("sail", pirate_ship, (pirate_ship_position[0] + 1, pirate_ship_position[1])),
                           ("sail", pirate_ship, (pirate_ship_position[0] - 1, pirate_ship_position[1])),
                           ("sail", pirate_ship, (pirate_ship_position[0], pirate_ship_position[1] + 1)),
                           ("sail", pirate_ship, (pirate_ship_position[0], pirate_ship_position[1] - 1))]:
                if 0 <= action[2][0] < len(state["map"]) and 0 <= action[2][1] < len(state["map"][0]):
                    if state["map"][action[2][0]][action[2][1]] != "I":
                        ship_actions.append(action)
            # End of SAIL action

            # Check if the pirate ship can COLLECT TREASURE from the current position
            for treasure in state["treasures"]:
                treasure_position = state["treasures"][treasure]["position"]
                pirate_ship_treasure1 = state["pirate_ships"][pirate_ship]["treasures"][0]
                pirate_ship_treasure2 = state["pirate_ships"][pirate_ship]["treasures"][1]
                # check if the pirate ship is adjacent to the treasure
                if abs(pirate_ship_position[0] - treasure_position[0]) + abs(
                        pirate_ship_position[1] - treasure_position[1]) == 1:
                    if pirate_ship_treasure1 != treasure and pirate_ship_treasure2 != treasure:
                        if current_ship["treasures"][0] == "" or current_ship["treasures"][1] == "":
                            ship_actions.append(("collect_treasure", pirate_ship, treasure))
            # End of COLLECT TREASURE action

            # Check if the pirate ship can Deposit TREASURE from the current position
            if state["map"][pirate_ship_position[0]][pirate_ship_position[1]] == "B":
                if state["pirate_ships"][pirate_ship]["treasures"][0] != "":
                    ship_actions.append(("deposit_treasure", pirate_ship))
            # End of DEPOSIT TREASURE action

            # Add the WAIT action
            ship_actions.append(("wait", pirate_ship))
            # End of WAIT action
            available_actions.append(ship_actions)

        cp = list(itertools.product(*available_actions))
        return cp

    def result(self, state, actions):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        state = string_to_dict(state)
        new_state = state.copy()
        new_state["turns"] += 1
        # MOVE MARINE SHIPS
        for marine_ship in state["marine_ships"]:
            marine_ship_position = state["marine_ships"][marine_ship]["position"]
            marine_ship_route = state["marine_ships"][marine_ship]["route"]
            if marine_ship_position == marine_ship_route[-1]:
                new_state["marine_ships"][marine_ship]["direction"] = "backwards"
            elif marine_ship_position == marine_ship_route[0]:
                new_state["marine_ships"][marine_ship]["direction"] = "forward"
            if state["marine_ships"][marine_ship]["direction"] == "forward":
                next_position = marine_ship_route[marine_ship_route.index(marine_ship_position) + 1]
            else:
                next_position = marine_ship_route[marine_ship_route.index(marine_ship_position) - 1]
            new_state["marine_ships"][marine_ship]["position"] = next_position

        # ACT WITH PIRATE SHIPS
        if actions not in self.actions(state):
            raise ValueError("Invalid action")
        else:
            number_of_pirate_ships = len(state["pirate_ships"])
            if number_of_pirate_ships == 1:
                actions = [actions[0]]
            for action in actions:
                # Sail action
                a = action[0]
                if action[0] == "sail":
                    new_state["pirate_ships"][action[1]]["position"] = action[2]

                # Collect treasure action
                elif action[0] == "collect_treasure":
                    if new_state["pirate_ships"][action[1]]["treasures"][0] == "":
                        new_state["pirate_ships"][action[1]]["treasures"][0] = action[2]
                    else:
                        new_state["pirate_ships"][action[1]]["treasures"][1] = action[2]
                    new_state["treasures"][action[2]]["is_on_ship"] = True
                # Deposit treasure action
                elif action[0] == "deposit_treasure":
                    treasure_1 = new_state["pirate_ships"][action[1]]["treasures"][0]
                    treasure_2 = new_state["pirate_ships"][action[1]]["treasures"][1]
                    new_state["treasures"][treasure_1]["is_collected"] = True
                    if treasure_2 != "":
                        new_state["treasures"][treasure_2]["is_collected"] = True

                # Wait action
                elif action[0] == "wait":
                    pass

                else:
                    raise ValueError("Invalid action")

                # if pirate ship is in the same position as a marine ship, remove the treasures
                marine_ships_positions = [
                    marine_ship["position"] for marine_ship in new_state["marine_ships"].values()
                ]
                if action[1] in marine_ships_positions:
                    new_state["pirate_ships"][action[1]]["treasures"] = ["", ""]
        return dict_to_string(new_state)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        state = string_to_dict(state)
        for treasure in state["treasures"]:
            if not state["treasures"][treasure]["is_collected"]:
                return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

        return self.h_1(node) + self.h_2(node)

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    # get_unique_number_of_treasures_collected --> returns the number of unique treasures collected by the pirate ships
    # and brought to base plus the number of treasures that are now on the ships
    def h_1(self, node):
        state = string_to_dict(self.initial)
        treasures_collected = []
        for pirate_ship in state["pirate_ships"]:
            for treasure in state["pirate_ships"][pirate_ship]["treasures"]:
                if treasure != "":
                    treasures_collected.append(treasure)

        for treasure in state["treasures"]:
            if state["treasures"][treasure]["is_collected"]:
                treasures_collected.append(treasure)

        number_of_total_treasures = len(set(state["treasures"]))

        return (number_of_total_treasures - len(set(treasures_collected))) / len(state["pirate_ships"])

    # h_1 --> Number of uncollected treasures divided by the number of pirates

    # h_2 --> Sum of the distances from the pirate base to the closest sea cell adjacent to a treasure -
    # for each treasure, divided by the number of pirates. If there is a treasure which all the
    # adjacent cells are islands – return infinity.

    def h_2(self, node):
        state = string_to_dict(node.state)
        treasures_positions = [treasure["position"] for treasure in state["treasures"].values()]
        pirate_base_position = state["pirate_base_position"]
        pirate_ships = state["pirate_ships"]
        ships_distances = []
        for pirate_ship in pirate_ships:
            current_ship = pirate_ships[pirate_ship]
            for treasure_position in treasures_positions:
                if (current_ship["treasures"][0] != "" and
                        current_ship["treasures"][1] != ""):
                    ships_distances.append(0)
                else:
                    distance = (min([abs(pirate_base_position[0] - treasure_position[0]) + abs(
                        pirate_base_position[1] - treasure_position[1])]))
                    ships_distances.append(distance)
        return sum(ships_distances) / len(pirate_ships)

    # h_3 --> Sum of the distances from each pirate ship to the closest treasure, divided by the number of pirates.
    # a ship with 2 treasures, the distance for it is zero
    def h_3(self, node):
        state = string_to_dict(node.state)
        ships_distances = []
        treasures_positions = [treasure["position"] for treasure in state["treasures"].values()]
        for pirate_ship in state["pirate_ships"]:
            current_ship = state["pirate_ships"][pirate_ship]
            for treasures_position in treasures_positions:
                if (current_ship["treasures"][0] != "" and
                        current_ship["treasures"][1] != ""):
                    ships_distances.append(0)
                else:
                    distance = (min([abs(current_ship["position"][0] - treasures_position[0]) + abs(
                        current_ship["position"][1] - treasures_position[1])]))
                    if current_ship["treasures"][0] != "":
                        ships_distances.append(distance / 2)
                    else:
                        ships_distances.append(distance)
        return sum(ships_distances) / len(state["pirate_ships"])


def h_4(node):
    state = string_to_dict(node.state)
    missing_treasures = state["treasures"].values().count(False)
    if missing_treasures == 0:
        return 0
    pirate_ships = state["pirate_ships"]
    treasures = state["treasures"]
    base_position = state["pirate_base_position"]
    sum_of_distances_to_base = 0
    sum_of_distances_to_treasures = 0
    for treasure in treasures:
        if not treasures[treasure]["is_collected"]:
            sum_of_distances_to_base += L1_distance(base_position, treasures[treasure]["position"])
        if not treasures[treasure]["is_on_ship"]:
            sum_of_distances_to_treasures += closest_pirate_ship_to_treasure(state, treasures[treasure]["position"])

    average_distance_to_base = sum_of_distances_to_base / missing_treasures



# a function that coverts dictionary to a string
def dict_to_string(d):
    return str(d)


def L1_distance(self, p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


# a function that coverts string to a dictionary if the input is not already a dictionary

def closest_pirate_ship_to_treasure(self, state, treasure_position):
    pirate_ships = state["pirate_ships"]
    closest_distance = math.inf
    closest_ship = ""
    for ship in pirate_ships:
        distance = self.L1_distance(pirate_ships[ship]["position"], treasure_position)
        if distance < closest_distance:
            closest_distance = distance
            closest_ship = ship
    return closest_distance


def string_to_dict(s):
    if isinstance(s, dict):
        return s
    else:
        return eval(s)


def cross_product(list_of_lists):
    if len(list_of_lists) == 1:
        return list_of_lists[0]
    else:
        return [(x,) + (y,) for x in list_of_lists[0] for y in cross_product(list_of_lists[1:])]


def create_onepiece_problem(game):
    return OnePieceProblem(game)
