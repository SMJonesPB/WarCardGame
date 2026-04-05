class DeckBiasTracker:
    def __init__(self):
        # Stats per rank (2–14)
        self.rank_stats = {
            rank: {
                "wins": 0,
                "losses": 0,
                "cards_won": 0,
                "cards_lost": 0,
            }
            for rank in range(2, 15)
        }

    def record_battle(self, p1_card, p2_card, winner, cards_in_pile):
        # p1_card and p2_card are tuples: (rank_string, suit_string)
        rank_order = {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
            "jack": 11, "queen": 12, "king": 13, "ace": 14
        }

        r1 = rank_order[p1_card[0]]
        r2 = rank_order[p2_card[0]]

        if winner == "Player 1":
            self.rank_stats[r1]["wins"] += 1
            self.rank_stats[r1]["cards_won"] += cards_in_pile

            self.rank_stats[r2]["losses"] += 1
            self.rank_stats[r2]["cards_lost"] += cards_in_pile

        elif winner == "Player 2":
            self.rank_stats[r2]["wins"] += 1
            self.rank_stats[r2]["cards_won"] += cards_in_pile

            self.rank_stats[r1]["losses"] += 1
            self.rank_stats[r1]["cards_lost"] += cards_in_pile


    def merge(self, other):
        """Merge another DeckBiasTracker into this one (for multi‑game simulation)."""
        for rank in self.rank_stats:
            for key in self.rank_stats[rank]:
                self.rank_stats[rank][key] += other.rank_stats[rank][key]