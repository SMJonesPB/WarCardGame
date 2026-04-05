# engine/replay_engine.py

import copy
from logging import log

class ReplayLog:
    """
    Stores the full sequence of events for a single game of War.
    Each entry is a dict describing one round.
    """
    def __init__(self):
        self.rounds = []          # list of dicts
        self.final_winner = None
        self.total_rounds = 0
        self.total_wars = 0
        self.max_chain = 0

    def add_round(self, p1_card, p2_card, winner, war_depth):
        """
        p1_card, p2_card: card tuples or objects
        winner: "Player 1", "Player 2", or "War"
        war_depth: 0 = normal round, 1+ = war chain depth
        """
        self.rounds.append({
            "p1_card": p1_card,
            "p2_card": p2_card,
            "winner": winner,
            "war_depth": war_depth
        })

    def finalize(self, engine, winner):
        """
        Called at the end of the game to store summary stats.
        """
        self.final_winner = winner
        self.total_rounds = engine.rounds_played
        self.total_wars = engine.wars
        self.max_chain = engine.max_war_chain

    def clone(self):
        return copy.deepcopy(self)

class ReplayEngine:
    """
    Tracks multiple replay logs and identifies the most interesting games:
        - shortest game
        - longest game
        - most wars
        - longest war chain
    """
    def __init__(self):
        self.replays = []  # list[ReplayLog]

        # Best-of categories
        self.shortest = None
        self.longest = None
        self.most_wars = None
        self.longest_chain = None
        self.game_counter = 0

    def start_new_log(self):
        """
        Begin logging a new game.
        Returns a ReplayLog instance that the caller will fill.
        """
        log = ReplayLog()
        log.game_number = self.game_counter
        self.replays.append(log)
        return log

    def finalize_log(self, log, engine, winner):
        """
        Called when a game ends. Updates summary stats and best-of categories.
        """
         # Increment global game counter
        self.game_counter += 1
        log.game_number = self.game_counter
        log.finalize(engine, winner)

        # Update shortest game
        if self.shortest is None or log.total_rounds < self.shortest.total_rounds:
            self.shortest = log.clone()
            self.shortest.title = "Shortest Game"

        # Update longest game
        if self.longest is None or log.total_rounds > self.longest.total_rounds:
            self.longest = log.clone()
            self.longest.title = "Longest Game"

        # Update most wars
        if self.most_wars is None or log.total_wars > self.most_wars.total_wars:
            self.most_wars = log.clone()
            self.most_wars.title = "Most Wars"

        # Update longest war chain
        if self.longest_chain is None or log.max_chain > self.longest_chain.max_chain:
            self.longest_chain = log.clone()
            self.longest_chain.title = "Longest War Chain"


    # -----------------------------
    # Accessors for GUI
    # -----------------------------

    def get_shortest(self):
        return self.shortest

    def get_longest(self):
        return self.longest

    def get_most_wars(self):
        return self.most_wars

    def get_longest_chain(self):
        return self.longest_chain
