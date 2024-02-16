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

        self.treasures = {}
        for treasure in initial["treasures"]:
            self.treasures[treasure] = {"position": initial["treasures"][treasure], "is_deposited": False,
                                        "is_collected": False}

        self.pirate_ships = {}
        for pirate_ship in initial["pirate_ships"]:
            self.pirate_ships[pirate_ship] = {"position": initial["pirate_ships"][pirate_ship], "treasures": ["", ""]}

        self.marine_ships = {}
        for marine_ship in initial["marine_ships"]:
            self.marine_ships[marine_ship] = {"position": initial["marine_ships"][marine_ship][0],
                                              "route": initial["marine_ships"][marine_ship],
                                              "direction": "forward"}

        self.turns = 0

        pirate_base_position = [(i, j) for i in range(len(self.map)) for j in range(len(self.map[0]))
                                if self.map[i][j] == "B"][0]
        initial_dict = {"map": self.map, "pirate_ships": self.pirate_ships, "treasures": self.treasures,
                        "marine_ships": self.marine_ships,
                        "pirate_base_position": pirate_base_position,
                        "lost_treasure" : False}
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
                state["marine_ships"][marine_ship]["position"] = next_position

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
                        new_state["treasures"][action[2]]["is_collected"] = True
                    elif new_state["pirate_ships"][action[1]]["treasures"][1] == "":
                        new_state["pirate_ships"][action[1]]["treasures"][1] = action[2]
                        new_state["treasures"][action[2]]["is_collected"] = True

                # Deposit treasure action
                elif action[0] == "deposit_treasure":
                    treasure_1 = new_state["pirate_ships"][action[1]]["treasures"][0]
                    treasure_2 = new_state["pirate_ships"][action[1]]["treasures"][1]
                    new_state["treasures"][treasure_1]["is_deposited"] = True
                    if treasure_2 != "":
                        new_state["treasures"][treasure_2]["is_deposited"] = True

                # Wait action
                elif action[0] == "wait":
                    pass

                else:
                    raise ValueError("Invalid action")

                # if pirate ship is in the same position as a marine ship, remove the treasures
            marine_ships_positions = [
                marine_ship["position"] for marine_ship in new_state["marine_ships"].values()
            ]
            if state["pirate_ships"][action[1]]["position"] in marine_ships_positions:
                pirate_ship_treasure_1 = new_state["pirate_ships"][action[1]]["treasures"][0]
                pirate_ship_treasure_2 = new_state["pirate_ships"][action[1]]["treasures"][1]
                new_state["pirate_ships"][action[1]]["treasures"] = ["", ""]
                flag_for_treasure_1 = False
                flag_for_treasure_2 = False
                for pirate_ship in new_state["pirate_ships"]:
                    if new_state["pirate_ships"][pirate_ship]["treasures"][0] == pirate_ship_treasure_1 or \
                            new_state["pirate_ships"][pirate_ship]["treasures"][1] == pirate_ship_treasure_1:
                        flag_for_treasure_1 = True
                    if new_state["pirate_ships"][pirate_ship]["treasures"][0] == pirate_ship_treasure_2 or \
                            new_state["pirate_ships"][pirate_ship]["treasures"][1] == pirate_ship_treasure_2:
                        flag_for_treasure_2 = True
                if not flag_for_treasure_1 or not flag_for_treasure_2:

            # for each treasure that is not collected yet, check if the there is a pirate ship that has it
            # if there is, make the treasure is_collect = True
            curr_collected_treasures = set()
            treasures_names = set(new_state["treasures"].keys())
            for treasure in new_state["treasures"]:
                for pirate_ship in new_state["pirate_ships"]:
                    treasure_1 = new_state["pirate_ships"][pirate_ship]["treasures"][0]
                    treasure_2 = new_state["pirate_ships"][pirate_ship]["treasures"][1]
                    if treasure_1 == treasure or treasure_2 == treasure:
                        curr_collected_treasures.add(treasure)

            for treasure in curr_collected_treasures:
                new_state["treasures"][treasure]["is_collected"] = True
            curr_uncollected_treasures = treasures_names - curr_collected_treasures
            for treasure in curr_uncollected_treasures:
                new_state["treasures"][treasure]["is_collected"] = False

        return dict_to_string(new_state)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        state = string_to_dict(state)
        for treasure in state["treasures"]:
            if not state["treasures"][treasure]["is_deposited"]:
                return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        state = string_to_dict(node.state)
        h_1 = self.h_1(state)
        h_2 = self.h_2(state)
        h_final = self.h_final(state)
        if h_1 == 0:
            return 0
        return max(h_1, h_2, h_final)

    def h_1(self, state):
        """
        number of un-deposit treasures divided by the number of pirate ships
        """
        return non_deposit_treasures(state) / len(state["pirate_ships"])

    def h_2(self, state):
        """
        Sum of the distances from the pirate base to the closest sea cell adjacent to a treasure -
        for each treasure, divided by the number of pirates. If there is a treasure which all the
        adjacent cells are islands – return infinity.
        """
        pirate_base_position = state["pirate_base_position"]
        treasures = state["treasures"]
        pirate_ships = state["pirate_ships"]
        closest_distances = []
        for treasure in treasures:
            treasure_adjacent_sea_cells = get_adjacent_sea_cells(state, treasures[treasure]["position"])
            if len(treasure_adjacent_sea_cells) == 0:
                return math.inf
            closest_distance = math.inf
            for cell in treasure_adjacent_sea_cells:
                distance = L1_distance(pirate_base_position, cell)
                if distance < closest_distance:
                    closest_distance = distance
            closest_distances.append(closest_distance)
        return sum(closest_distances) / len(pirate_ships)

    def h_2_upgraded(self, state):
        """
        Sum of the distances from the pirate base to the closest sea cell adjacent to a treasure -
        which is not collected yet, devided by the number of pirates. If there is a treasure which all the
        adjacent cells are islands – return infinity.
        """
        pirate_base_position = state["pirate_base_position"]
        treasures = state["treasures"]
        pirate_ships = state["pirate_ships"]
        closest_distances = []
        for treasure in treasures:
            if not treasures[treasure]["is_deposited"]:
                treasure_adjacent_sea_cells = get_adjacent_sea_cells(state, treasures[treasure]["position"])
                if len(treasure_adjacent_sea_cells) == 0:
                    return math.inf
                closest_distance = math.inf
                for cell in treasure_adjacent_sea_cells:
                    distance = L1_distance(pirate_base_position, cell)
                    if distance < closest_distance:
                        closest_distance = distance
                closest_distances.append(closest_distance)
        return sum(closest_distances) / len(pirate_ships)

    def h_2_upgraded_2(self, state):
        """
        Sum For every treasure that is not deposited yet, the minimal number of steps that it will take to deposit it
        get the closest pirate ship to the treasure, if the ship is full, calculate the distance for it to get to the
        base and than go to the treasure, collect it and go back to the base, if the ship is not full, calculate the
        distance for it to get to the treasure, collect it and go back to the base
        Finaly, get the minimal number of steps for all the treasures and return the sum of them
        """
        treasures = state["treasures"]
        pirate_ships = state["pirate_ships"]
        pirate_base_position = state["pirate_base_position"]
        total_distance = 0
        for treasure in treasures:
            if not treasures[treasure]["is_deposited"]:  # if the treasure is not deposited yet
                if treasures[treasure]["is_collected"]:  # if the treasure is collected
                    total_distance += closest_ship_with_treasure_to_base(state, treasure)
                else:  # if the treasure is not collected yet
                    total_distance += closest_pirate_ship_to_treasure_to_base(state, treasure)
        return total_distance

    def h_final(self, state):
        """
        Returns the minimal distance of a treasure to the pirate base
        """
        state = string_to_dict(state)
        D = 0  #
        T = 0  #
        counter_on_way = 0
        number_of_deposited_treasures = 0
        for treasure in state['treasures']:
            if not state['treasures'][treasure]["is_collected"] and \
                    not state['treasures'][treasure]["is_deposited"]:
                D += closest_distance_to_adjacent_sea_cell(state, state['pirate_base_position'],
                                                           state['treasures'][treasure]['position'])

            if state['treasures'][treasure]["is_collected"] and \
                    not state['treasures'][treasure]["is_deposited"]:
                T += closest_ship_with_treasure_to_base(state, treasure)
                counter_on_way += 1
            if state['treasures'][treasure]["is_deposited"]:
                number_of_deposited_treasures += 1

        number_of_treasures = len(state['treasures'])
        counter_not_on_way = (number_of_treasures - number_of_deposited_treasures) - counter_on_way

        return (D + T) + (2 * counter_not_on_way) + counter_on_way  # Plus 2 because the cost of actions

    def caught_by_marine(self, state):
        pirate_ships = state["pirate_ships"]
        marine_ships = state["marine_ships"]
        for pirate_ship in pirate_ships:
            for marine_ship in marine_ships:
                if pirate_ships[pirate_ship]["position"] == marine_ships[marine_ship]["position"]:
                    return True
        return False


def closest_ship_with_treasure_to_base(state, treasure):
    """
    Returns the minimal number of steps that it will take to deposit the treasure
    """
    pirate_ships = state["pirate_ships"]
    pirate_base_position = state["pirate_base_position"]
    closest_distance = math.inf
    for pirate_ship in pirate_ships:
        if pirate_ships[pirate_ship]["treasures"][0] == treasure or pirate_ships[pirate_ship]["treasures"][
            1] == treasure:
            distance_to_base = L1_distance(pirate_ships[pirate_ship]["position"], pirate_base_position)
            if distance_to_base < closest_distance:
                closest_distance = distance_to_base
    return closest_distance


def closest_pirate_ship_to_treasure_to_base(state, treasure):
    """
    For each pirate ship: if the ship is full, calculate the distance for it to get to the base and than go to the
    treasure, collect it and go back to the base, if the ship is not full, calculate the distance for it to get to the
    closest sea cell to the treasure, collect it and go back to the base.
    Finally, return the minimal number of steps for all the pirate ships
    """
    treasure_position = state["treasures"][treasure]["position"]
    pirate_ships = state["pirate_ships"]
    pirate_base_position = state["pirate_base_position"]
    closest_distance = math.inf
    for pirate_ship in pirate_ships:
        if is_ship_full(pirate_ships[pirate_ship]):  # if the ship is full -> go to the base and then to the treasure
            # and back to the base
            distance_to_base = L1_distance(pirate_ships[pirate_ship]["position"], pirate_base_position)
            distance_to_treasure = closest_distance_to_adjacent_sea_cell(state, pirate_ships[pirate_ship]["position"],
                                                                         treasure_position)
            distance = distance_to_base + distance_to_treasure * 2
        elif (not is_ship_full(pirate_ships[pirate_ship]) and not
        is_treasure_on_ship(pirate_ships[pirate_ship], treasure)):  # if the
            # ship is not full and the treasure is not on the ship -> go to the treasure and then to the base
            distance_to_treasure = closest_distance_to_adjacent_sea_cell(state, pirate_ships[pirate_ship]["position"],
                                                                         treasure_position)
            distance_to_base = closest_distance_to_adjacent_sea_cell(state, pirate_base_position, treasure_position)
            distance = distance_to_treasure + distance_to_base
        elif (pirate_ships[pirate_ship]["treasures"][0] == treasure or
              pirate_ships[pirate_ship]["treasures"][
                  1] == treasure):  # if the treasure is on the ship -> go to the base
            distance = L1_distance(pirate_ships[pirate_ship]["position"], pirate_base_position)

        if distance < closest_distance:
            closest_distance = distance
    return closest_distance


def closest_distance_to_adjacent_sea_cell(state, position_1, position_to_be_adjacent):
    adjacent_sea_cells = get_adjacent_sea_cells(state, position_to_be_adjacent)
    if adjacent_sea_cells == []:
        return math.inf
    closest_distance = math.inf
    for cell in adjacent_sea_cells:
        distance = L1_distance(position_1, cell)
        if distance < closest_distance:
            closest_distance = distance
    return closest_distance


def dict_to_string(d):
    return str(d)


def non_deposit_treasures(state):
    """
    Returns the number of treasures that we not deposited yet
    """
    treasures = state["treasures"]
    not_collected = 0
    for treasure in treasures:
        if not state["treasures"][treasure]["is_deposited"]:
            not_collected += 1
    return not_collected


def uncollected_treasures(state):
    """
    returns the number of treasures that are not collected yet by a pirate ship (dos't counts the deposited treasures)
    """
    treasures = state["treasures"]
    not_collected = 0
    for treasure in treasures:
        if not state["treasures"][treasure]["is_collected"] and not state["treasures"][treasure]["is_on_ship"]:
            not_collected += 1
    return not_collected


def collected_treasures(state):
    """
    returns the number of treasures that are collected by a pirate ship
    """
    treasures = state["treasures"]
    collected = 0
    for treasure in treasures:
        if state["treasures"][treasure]["is_collected"]:
            collected += 1
    return collected


def deposited_treasures(state):
    """
    returns the number of treasures that are deposited by a pirate ship
    """
    treasures = state["treasures"]
    deposited = 0
    for treasure in treasures:
        if state["treasures"][treasure]["is_collected"] and state["treasures"][treasure]["is_on_ship"]:
            deposited += 1
    return deposited


def get_capacity(pirate_ships):
    capacity = 0
    for pirate_ship in pirate_ships:
        if pirate_ships[pirate_ship]["treasures"][0] == "":
            capacity += 2
        elif pirate_ships[pirate_ship]["treasures"][0] != "" and pirate_ships[pirate_ship]["treasures"][1] == "":
            capacity += 1
        else:
            capacity += 0
    return capacity


# returns the L1 distance between two points
def L1_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


# returns the distance of the closest pirate ship to the treasure (that is not full)
def is_treasure_on_ship(pirate_ship, treasure):
    """
    Returns True if the treasure is on the pirate ship given, False otherwise
    """
    if pirate_ship["treasures"][0] == treasure or pirate_ship["treasures"][1] == treasure:
        return True
    return False


# returns True if the ship is full, False otherwise
def is_ship_full(pirate_ship):
    return pirate_ship["treasures"][0] != "" and pirate_ship["treasures"][1] != ""


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


def get_adjacent_sea_cells(state, position):
    """
    Returns a list of the adjacent sea cells to the given position
    """
    adjacent_cells = [(position[0] + 1, position[1]), (position[0] - 1, position[1]),
                      (position[0], position[1] + 1), (position[0], position[1] - 1)]
    adjacent_sea_cells = []
    for adjacent_cell in adjacent_cells:
        if 0 <= adjacent_cell[0] < len(state["map"]) and 0 <= adjacent_cell[1] < len(state["map"][0]) and \
                state["map"][adjacent_cell[0]][adjacent_cell[1]] != "I":
            adjacent_sea_cells.append(adjacent_cell)
    return adjacent_sea_cells
