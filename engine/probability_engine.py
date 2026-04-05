# engine/probability_engine.py

from collections import Counter
import math

class SimulationResult:
    """
    Raw data collected from many simulated games of War.
    This is a simple container; all math lives in ProbabilityEngine.
    """
    def __init__(self):
        self.total_games = 0

        self.p1_wins = 0
        self.p2_wins = 0
        self.ties = 0

        # Per-game metrics
        self.round_counts = []       # list[int]
        self.war_counts = []         # list[int]
        self.max_chain_counts = []   # list[int]

    def has_data(self) -> bool:
        return self.total_games > 0


class ProbabilityEngine:
    """
    Collects simulation results and exposes probability/statistical queries
    over many games of War.
    """
    def __init__(self):
        self.results = SimulationResult()

    # -----------------------------
    # Data collection
    # -----------------------------

    def record_game(self, engine, winner: str) -> None:
        """
        Record the outcome and stats of a single completed game.

        `engine` is your WarEngine instance after the game ends.
        It must expose:
            - engine.rounds_played
            - engine.wars
            - engine.max_war_chain

        `winner` is a string like "Player 1", "Player 2", or "Tie".
        """
        self.results.total_games += 1

        if winner == "Player 1":
            self.results.p1_wins += 1
        elif winner == "Player 2":
            self.results.p2_wins += 1
        else:
            self.results.ties += 1

        self.results.round_counts.append(engine.rounds_played)
        self.results.war_counts.append(engine.wars)
        self.results.max_chain_counts.append(engine.max_war_chain)

    # -----------------------------
    # Basic win probabilities
    # -----------------------------

    def win_rates(self) -> dict:
        """
        Returns a dict with win probabilities for P1, P2, and ties.
        Example:
            {"p1": 0.503, "p2": 0.492, "tie": 0.005}
        """
        if not self.results.has_data():
            return {"p1": 0.0, "p2": 0.0, "tie": 0.0}

        t = self.results.total_games
        return {
            "p1": self.results.p1_wins / t,
            "p2": self.results.p2_wins / t,
            "tie": self.results.ties / t,
        }

    # -----------------------------
    # Averages
    # -----------------------------

    def average_rounds(self) -> float:
        if not self.results.round_counts:
            return 0.0
        return sum(self.results.round_counts) / len(self.results.round_counts)

    def average_wars(self) -> float:
        if not self.results.war_counts:
            return 0.0
        return sum(self.results.war_counts) / len(self.results.war_counts)

    def average_max_chain(self) -> float:
        if not self.results.max_chain_counts:
            return 0.0
        return sum(self.results.max_chain_counts) / len(self.results.max_chain_counts)

    # -----------------------------
    # Distributions (histograms)
    # -----------------------------

    def _distribution(self, data_list) -> dict:
        """
        Returns a dict mapping value -> frequency.
        Example for rounds:
            {12: 103, 13: 98, 14: 112, ...}
        """
        return dict(Counter(data_list))

    def round_distribution(self) -> dict:
        return self._distribution(self.results.round_counts)

    def war_distribution(self) -> dict:
        return self._distribution(self.results.war_counts)

    def chain_distribution(self) -> dict:
        return self._distribution(self.results.max_chain_counts)

    # -----------------------------
    # Probability queries
    # -----------------------------

    def probability_game_under_rounds(self, max_rounds: int) -> float:
        """
        Probability that a game finishes in <= max_rounds.
        """
        if not self.results.has_data():
            return 0.0

        count = sum(1 for r in self.results.round_counts if r <= max_rounds)
        return count / self.results.total_games

    def probability_at_least_one_war(self) -> float:
        """
        Probability that a game has at least one war.
        """
        if not self.results.has_data():
            return 0.0

        count = sum(1 for w in self.results.war_counts if w >= 1)
        return count / self.results.total_games

    def probability_chain_at_least(self, min_chain: int) -> float:
        """
        Probability that a game has a max war chain >= min_chain.
        """
        if not self.results.has_data():
            return 0.0

        count = sum(1 for c in self.results.max_chain_counts if c >= min_chain)
        return count / self.results.total_games

    # -----------------------------
    # Confidence intervals (optional)
    # -----------------------------

    def confidence_interval(self, p: float, z: float = 1.96) -> tuple[float, float]:
        """
        Compute a z-score confidence interval for a proportion p
        over total_games trials.

        Default z=1.96 → 95% confidence interval.
        """
        t = self.results.total_games
        if t == 0:
            return (0.0, 0.0)

        se = math.sqrt(p * (1 - p) / t)
        return (p - z * se, p + z * se)