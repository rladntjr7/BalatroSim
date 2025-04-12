import random
from card import Card

class Deck:
    def __init__(self):
        self.cards = []
        for suit in ['hearts', 'diamonds', 'clubs', 'spades']:
            for rank in range(1, 14):
                self.cards.append(Card(rank, suit))
                
    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        try:
            return self.cards.pop()
        except IndexError:
            print("Warning: Deck is empty.")
            return None 