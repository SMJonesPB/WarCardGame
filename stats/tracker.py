class StatsTracker:
    def __init__(self):
        self.reset_session()

    def reset_session(self):
        self.total_games = 0
        self.p1_wins = 0
        self.p2_wins = 0
        self.ties = 0
        self.total_rounds = 0
        self.total_wars = 0
        self.max_war_chain_overall = 0

    def record_game(self, engine, winner):
        self.total_games += 1

        if winner == "Player 1":
            self.p1_wins += 1
        elif winner == "Player 2":
            self.p2_wins += 1
        else:
            self.ties += 1

        self.total_rounds += engine.rounds_played
        self.total_wars += engine.wars
        self.max_war_chain_overall = max(
            self.max_war_chain_overall, engine.max_war_chain
        )

    def session_summary(self):
        if self.total_games == 0:
            avg_rounds = 0
            avg_wars = 0
        else:
            avg_rounds = self.total_rounds / self.total_games
            avg_wars = self.total_wars / self.total_games

        return {
            "total_games": self.total_games,
            "p1_wins": self.p1_wins,
            "p2_wins": self.p2_wins,
            "ties": self.ties,
            "avg_rounds": avg_rounds,
            "avg_wars": avg_wars,
            "max_war_chain_overall": self.max_war_chain_overall
        }