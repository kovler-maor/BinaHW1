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

        initial = {"map": self.map, "pirate_ships": self.pirate_ships, "treasures": self.treasures,
                   "marine_ships": self.marine_ships, "turns": self.turns}

        search.Problem.__init__(self, initial)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
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
        # check if the action is valid
        if action not in self.actions(state):
            raise ValueError("Invalid action")

        new_state = state.copy()
        new_state["turns"] += 1
        if action[0] == "sail":
            new_state["pirate_ships"][action[1]]["position"] = action[2]
        elif action[0] == "collect_treasure":
            new_state["treasures"][action[2]]["is_collected"] = True
            new_state["pirate_ships"][action[1]]["treasures"].append(action[2])
        elif action[0] == "deposit_treasure":
            new_state["pirate_ships"][action[1]]["treasures"] = []
        return new_state

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


def create_onepiece_problem(game):
    return OnePieceProblem(game)
