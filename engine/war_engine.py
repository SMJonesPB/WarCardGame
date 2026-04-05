# engine/war_engine.py

from engine.bias_engine import DeckBiasTracker
from engine.deck import Deck
import random


class WarEngine:
    """
    Core game logic for War.
    Handles:
        - deck setup
        - round resolution
        - war chains
        - stats (rounds, wars, max war chain)
    """

    def __init__(self, update_callback=None):
        self.update_callback = update_callback

        # Stats
        self.rounds_played = 0
        self.wars = 0
        self.max_war_chain = 0

        # Build and shuffle deck
        self._build_decks()
        self.bias = DeckBiasTracker()


    # ---------------------------------------------------------
    # Deck setup
    # ---------------------------------------------------------

    def _build_decks(self):
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
                 "jack", "queen", "king", "ace"]
        suits = ["hearts", "diamonds", "clubs", "spades"]

        # Build full deck
        full_deck = [(rank, suit) for suit in suits for rank in ranks]
        random.shuffle(full_deck)

        # Split into two decks
        p1_cards = full_deck[:26]
        p2_cards = full_deck[26:]

        self.p1 = Deck(p1_cards)
        self.p2 = Deck(p2_cards)

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def has_winner(self):
        if len(self.p1) == 0:
            return "Player 2"
        if len(self.p2) == 0:
            return "Player 1"
        return None

    def _determine_winner(self):
        if len(self.p1) > len(self.p2):
            return "Player 1"
        elif len(self.p2) > len(self.p1):
            return "Player 2"
        else:
            return "Tie"

    # ---------------------------------------------------------
    # Main round logic
    # ---------------------------------------------------------

    def play_round(self):
        """
        Plays a single round of War, including recursive war resolution.
        Returns a dict containing:
            - p1_card
            - p2_card
            - winner
            - log_lines
            - war_depth   (0 = normal round, 1+ = war chain depth)
        """

        log_lines = []
        war_depth = 0
        MAX_WAR_DEPTH = 3   # Cap war chain to prevent infinite loops

        # If someone has already won
        winner = self.has_winner()
        if winner:
            return {
                "p1_card": None,
                "p2_card": None,
                "winner": winner,
                "log_lines": [f"{winner} already won."],
                "war_depth": 0
            }

        # -----------------------------------------------------
        # Draw initial cards
        # -----------------------------------------------------
        p1_card = self.p1.draw()
        p2_card = self.p2.draw()
        
        if p1_card is None or p2_card is None:
            winner = self._determine_winner()
            return {
                "p1_card": p1_card,
                "p2_card": p2_card,
                "winner": winner,
                "log_lines": [f"Player ran out of cards. {winner} wins."],
                "war_depth": 0
            }

        log_lines.append(f"P1 plays {p1_card}, P2 plays {p2_card}")

        # -----------------------------------------------------
        # Resolve the round (including wars)
        # -----------------------------------------------------
        pile = [p1_card, p2_card]

        while True:
            # Normal win
            if p1_card[0] != p2_card[0]:
                ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
                        "jack", "queen", "king", "ace"]
                p1_val = ranks.index(p1_card[0])
                p2_val = ranks.index(p2_card[0])
                if p1_val > p2_val:
                    winner = "Player 1"
                    self.p1.add_cards(pile)
                else:
                    winner = "Player 2"
                    self.p2.add_cards(pile)
                break

            # -------------------------------------------------
            # WAR!
            # -------------------------------------------------
            war_depth += 1
            self.wars += 1
            self.max_war_chain = max(self.max_war_chain, war_depth)

            log_lines.append(f"--- WAR! Depth {war_depth} ---")

            # SAFETY VALVE: cap war depth
            if war_depth > MAX_WAR_DEPTH:
                # Count forced war endings (simulation-level)
                if hasattr(self, "sim_forced_war_ends"):
                    self.sim_forced_war_ends += 1
                # Decide winner by deck size
                if len(self.p1) > len(self.p2):
                    winner = "Player 1"
                elif len(self.p2) > len(self.p1):
                    winner = "Player 2"
                else:
                    winner = "tie"

                log_lines.append(f"War depth exceeded {MAX_WAR_DEPTH}. Forcing result: {winner}")
                break

            war_cards_p1 = self.p1.draw_war_cards()
            war_cards_p2 = self.p2.draw_war_cards()

            pile.extend(war_cards_p1)
            pile.extend(war_cards_p2)

            # If either player cannot continue
            if len(war_cards_p1) < 4 or len(war_cards_p2) < 4:
                winner = self._determine_winner()
                log_lines.append(f"Player cannot continue war. {winner} wins.")
                break

            # New face-up cards
            p1_card = war_cards_p1[-1]
            p2_card = war_cards_p2[-1]

            log_lines.append(f"P1 war card: {p1_card}, P2 war card: {p2_card}")

        # -----------------------------------------------------
        # Update round count
        # -----------------------------------------------------
        self.rounds_played += 1
        self.bias.record_battle(
            p1_card,
            p2_card,
            winner,          # 1 or 2
            len(pile)        # number of cards awarded
        )

        if self.update_callback:
            self.update_callback()

        return {
            "p1_card": p1_card,
            "p2_card": p2_card,
            "winner": winner,
            "log_lines": log_lines,
            "war_depth": war_depth
        }

    # ---------------------------------------------------------
    # Reset decks for new game
    # ---------------------------------------------------------

    def reset_decks(self):
        self.rounds_played = 0
        self.wars = 0
        self.max_war_chain = 0
        self._build_decks()