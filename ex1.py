import search
import random
import math

ids = ["111111111", "111111111"]


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
            self.treasures[treasure] = {"position": initial["treasures"][treasure], "is_collected": False}
        # pirate ships in the world ->
        # pirate_ships = {
        # "pirate_ship_1": {"position": (x, y), "treasures": (,)},
        # "pirate_ship_2": {"position": (x, y), "treasures": (,)}
        # }
        self.pirate_ships = {}
        for pirate_ship in initial["pirate_ships"]:
            self.pirate_ships[pirate_ship] = {"position": initial["pirate_ships"][pirate_ship], "treasures": []}
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

        initial_dict = {"map": self.map, "pirate_ships": self.pirate_ships, "treasures": self.treasures,
                        "marine_ships": self.marine_ships, "turns": self.turns}
        initial = dict_to_string(initial_dict)
        search.Problem.__init__(self, initial)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        state = string_to_dict(state)
        available_actions = []
        for pirate_ship in state["pirate_ships"]:
            pirate_ship_position = state["pirate_ships"][pirate_ship]["position"]
            # Check if the pirate ship can SAIL to the next position
            for action in [("sail", pirate_ship, (pirate_ship_position[0] + 1, pirate_ship_position[1])),
                           ("sail", pirate_ship, (pirate_ship_position[0] - 1, pirate_ship_position[1])),
                           ("sail", pirate_ship, (pirate_ship_position[0], pirate_ship_position[1] + 1)),
                           ("sail", pirate_ship, (pirate_ship_position[0], pirate_ship_position[1] - 1)), ]:
                if 0 <= action[2][0] < len(state["map"]) and 0 <= action[2][1] < len(state["map"][0]):
                    if state["map"][action[2][0]][action[2][1]] != "I":
                        available_actions.append(action)
            # End of SAIL action

            # Check if the pirate ship can COLLECT TREASURE from the current position
            for treasure in state["treasures"]:
                treasure_position = state["treasures"][treasure]["position"]
                # check if the pirate ship is adjacent to the treasure
                if abs(pirate_ship_position[0] - treasure_position[0]) + abs(
                        pirate_ship_position[1] - treasure_position[1]) == 1:
                    available_actions.append(("collect_treasure", pirate_ship, treasure))
            # End of COLLECT TREASURE action

            # Check if the pirate ship can Deposit TREASURE from the current position
            if state["map"][pirate_ship_position[0]][pirate_ship_position[1]] == "B":
                available_actions.append(("deposit_treasure", pirate_ship))
            # End of DEPOSIT TREASURE action

            # Add the WAIT action
            available_actions.append(("wait", pirate_ship))
            # End of WAIT action

        return available_actions

    def result(self, state, action):
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
        for current_action in action:
            if current_action not in self.actions(state):
                raise ValueError("Invalid action")
            else:
                # Sail action
                if current_action[0] == "sail":
                    new_state["pirate_ships"][current_action[1]]["position"] = current_action[2]
                    marine_ships_positions = [
                        marine_ship["position"] for marine_ship in new_state["marine_ships"].values()
                    ]
                    # if pirate ship is in the same position as a marine ship, remove the treasures
                    if current_action[2] in marine_ships_positions:
                        new_state["pirate_ships"][current_action[1]]["treasures"] = ["", ""]

                # Collect treasure action
                elif current_action[0] == "collect_treasure":
                    if new_state["pirate_ships"][current_action[1]]["treasures"][0] == "":
                        new_state["pirate_ships"][current_action[1]]["treasures"][0] = current_action[2]
                    elif new_state["pirate_ships"][current_action[1]]["treasures"][1] == "":
                        new_state["pirate_ships"][current_action[1]]["treasures"][1] = current_action[2]
                    else:
                        raise ValueError("Pirate ship is full")

                # Deposit treasure action
                elif current_action[0] == "deposit_treasure":
                    pirate_ship_position = new_state["pirate_ships"][current_action[1]]["position"]
                    if new_state["map"][pirate_ship_position[0]][pirate_ship_position[1]] != "B":
                        raise ValueError("Can't deposit, pirate ship is not in the base")
                    elif new_state["pirate_ships"][current_action[1]]["treasures"][0] == "":
                        raise ValueError("Can't deposit, pirate ship has no treasures")
                    else:
                        for treasure in new_state["pirate_ships"][current_action[1]]["treasures"]:
                            new_state["treasures"][treasure]["is_collected"] = True

                # Wait action
                elif current_action[0] == "wait":
                    pass

                else:
                    raise ValueError("Invalid action")
            return dict_to_string(new_state)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for treasure in state["treasures"]:
            if not state["treasures"][treasure]["is_collected"]:
                return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

        return 0

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    # h_1 --> Number of uncollected treasures divided by the number of pirates
    def h_1(self, node):
        state = string_to_dict(node.state)
        uncollected_treasures = 0
        for treasure in state["treasures"]:
            if not state["treasures"][treasure]["is_collected"]:
                uncollected_treasures += 1
        return uncollected_treasures / len(state["pirate_ships"])

    # h_2 --> Sum of the distances from the pirate base to the closest sea cell adjacent to a treasure -
    # for each treasure, divided by the number of pirates. If there is a treasure which all the
    # adjacent cells are islands – return infinity.

    def h_2(self, node):
        state = string_to_dict(node.state)
        pirate_ships_positions = [pirate_ship["position"] for pirate_ship in state["pirate_ships"].values()]
        treasures_positions = [treasure["position"] for treasure in state["treasures"].values()]
        pirate_base_position = [(i, j) for i in range(len(state["map"])) for j in range(len(state["map"][0]))
                                if state["map"][i][j] == "B"][0]
        distances = []
        for treasure_position in treasures_positions:
            if all([state["map"][treasure_position[0] + i][treasure_position[1] + j] == "I"
                    for i in [-1, 0, 1] for j in [-1, 0, 1] if
                    0 <= treasure_position[0] + i < len(state["map"]) and 0 <= treasure_position[1] + j < len(
                        state["map"][0])]):
                return math.inf
            else:
                distances.append(
                    min([abs(pirate_base_position[0] - treasure_position[0]) + abs(
                        pirate_base_position[1] - treasure_position[1]) for pirate_base_position in
                         pirate_ships_positions]))
        return sum(distances) / len(state["pirate_ships"])


# a function that coverts dictionary to a string
def dict_to_string(d):
    return str(d)


# a function that coverts string to a dictionary
def string_to_dict(s):
    return eval(s)


def create_onepiece_problem(game):
    return OnePieceProblem(game)
