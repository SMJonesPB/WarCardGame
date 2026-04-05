# engine/deck.py

import random

class Deck:
    def __init__(self, cards=None):
        self.cards = cards[:] if cards else []

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            return None
        return self.cards.pop(0)

    def draw_war_cards(self):
        """
        Draw 4 cards for war:
        - 3 face-down
        - 1 face-up
        If fewer than 4 remain, return whatever is left.
        """
        drawn = []
        for _ in range(4):
            if self.cards:
                drawn.append(self.cards.pop(0))
        return drawn

    def add_cards(self, cards):
        """
        Winner takes the pile — cards go to the bottom.
        """
        self.cards.extend(cards)

    def __len__(self):
        return len(self.cards)